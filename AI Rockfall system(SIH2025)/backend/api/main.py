"""
AI Rockfall Prediction System - FastAPI Backend
===============================================

Main application entry point for the AI Rockfall Prediction System.
Provides REST APIs for data upload, analysis orchestration, and real-time monitoring.

Features:
- File upload and validation
- Analysis pipeline orchestration
- Real-time WebSocket updates
- Comprehensive reporting
- Database integration
- Authentication and authorization

Author: AI Rockfall Prediction Team
Date: October 26, 2025
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# FastAPI and related imports
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect

# Database and caching
from sqlalchemy.orm import Session
import redis.asyncio as redis

# Local imports
from .database import get_db, init_db
from .models import Site, Analysis, Device, Alert
from .auth import get_current_user, create_access_token
from .analysis_orchestrator import AnalysisOrchestrator
from .websocket_manager import WebSocketManager
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
analysis_orchestrator = AnalysisOrchestrator()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AI Rockfall Prediction System...")

    # Initialize database
    init_db()

    # Initialize Redis connection
    app.state.redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )

    # Start background tasks
    asyncio.create_task(analysis_orchestrator.start_monitoring())

    logger.info("System startup complete")

    yield

    # Shutdown
    logger.info("Shutting down AI Rockfall Prediction System...")
    await app.state.redis.close()
    logger.info("Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="AI Rockfall Prediction System API",
    description="Comprehensive rockfall prediction and monitoring system for open-pit mining",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
from .routers import auth, sites, devices, analysis, reports, dashboard

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sites.router, prefix="/api/sites", tags=["Sites"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "AI Rockfall Prediction System API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "redis": "connected",
            "analysis_orchestrator": "running"
        }
    }

@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            # Process client messages if needed
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )