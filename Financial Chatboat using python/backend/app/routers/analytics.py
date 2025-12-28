from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# Mock analytics data storage (in production, use proper database)
analytics_data = {
    "chat_sessions": [],
    "sentiment_trends": [],
    "popular_topics": [],
    "model_performance": []
}

def get_finbert_model(request: Request):
    """Dependency to get FinBERT model from app state"""
    return request.app.state.finbert_model

@router.get("/analytics/overview")
async def get_analytics_overview():
    """
    Get general analytics overview
    """
    try:
        # Mock data for demonstration
        total_chats = len(analytics_data["chat_sessions"])
        
        # Calculate sentiment distribution
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for session in analytics_data["chat_sessions"]:
            if "sentiment" in session:
                sentiment_counts[session["sentiment"]] += 1
        
        # Calculate average response time
        response_times = [session.get("response_time", 0) for session in analytics_data["chat_sessions"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_chat_sessions": total_chats,
            "sentiment_distribution": sentiment_counts,
            "average_response_time": round(avg_response_time, 3),
            "active_models": 1,
            "fine_tuned_models": 0,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/sentiment-trends")
async def get_sentiment_trends(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze")
):
    """
    Get sentiment trends over time
    """
    try:
        # Mock sentiment trend data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        trends = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            trends.append({
                "date": date.date().isoformat(),
                "positive": 30 + (i * 2),
                "negative": 20 - (i * 1),
                "neutral": 50 + (i * 0.5),
                "total_messages": 100 + (i * 5)
            })
        
        return {
            "trends": trends,
            "period": f"{days} days",
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/popular-topics")
async def get_popular_topics(limit: int = Query(default=10, ge=1, le=50)):
    """
    Get most popular financial topics discussed
    """
    try:
        # Mock popular topics data
        topics = [
            {"topic": "stock market", "mentions": 150, "sentiment": "positive"},
            {"topic": "cryptocurrency", "mentions": 120, "sentiment": "neutral"},
            {"topic": "inflation", "mentions": 100, "sentiment": "negative"},
            {"topic": "earnings reports", "mentions": 90, "sentiment": "positive"},
            {"topic": "federal reserve", "mentions": 85, "sentiment": "neutral"},
            {"topic": "market volatility", "mentions": 75, "sentiment": "negative"},
            {"topic": "investment portfolio", "mentions": 70, "sentiment": "positive"},
            {"topic": "economic growth", "mentions": 65, "sentiment": "positive"},
            {"topic": "recession", "mentions": 60, "sentiment": "negative"},
            {"topic": "dividend yields", "mentions": 55, "sentiment": "positive"}
        ]
        
        return {
            "topics": topics[:limit],
            "total_topics": len(topics),
            "limit": limit,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting popular topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/model-performance")
async def get_model_performance():
    """
    Get model performance metrics
    """
    try:
        # Mock performance data
        performance_data = {
            "accuracy": 0.89,
            "precision": {
                "positive": 0.91,
                "negative": 0.87,
                "neutral": 0.89
            },
            "recall": {
                "positive": 0.88,
                "negative": 0.90,
                "neutral": 0.89
            },
            "f1_score": {
                "positive": 0.895,
                "negative": 0.885,
                "neutral": 0.890
            },
            "average_confidence": 0.85,
            "total_predictions": 5000,
            "model_version": "1.0.0",
            "last_evaluation": datetime.now().isoformat()
        }
        
        return performance_data
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/usage-stats")
async def get_usage_statistics(
    period: str = Query(default="7d", regex="^(1d|7d|30d|90d)$", description="Time period for stats")
):
    """
    Get usage statistics for different time periods
    """
    try:
        period_map = {
            "1d": 1,
            "7d": 7,
            "30d": 30,
            "90d": 90
        }
        
        days = period_map[period]
        
        # Mock usage statistics
        stats = {
            "period": period,
            "days": days,
            "total_requests": 1000 * days,
            "unique_users": 50 * days,
            "average_requests_per_day": 1000,
            "peak_hour": "14:00",
            "peak_day": "Tuesday",
            "api_endpoints": {
                "/api/v1/chat": 800 * days,
                "/api/v1/finetune/start": 10 * days,
                "/api/v1/analytics/overview": 50 * days
            },
            "response_time_percentiles": {
                "p50": 0.125,
                "p90": 0.250,
                "p95": 0.400,
                "p99": 0.800
            },
            "error_rate": 0.02,
            "uptime": 99.9
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting usage statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/record-session")
async def record_chat_session(session_data: Dict[str, Any]):
    """
    Record a chat session for analytics
    """
    try:
        # Add timestamp
        session_data["timestamp"] = datetime.now().isoformat()
        
        # Store session data
        analytics_data["chat_sessions"].append(session_data)
        
        # Keep only last 10,000 sessions to prevent memory issues
        if len(analytics_data["chat_sessions"]) > 10000:
            analytics_data["chat_sessions"] = analytics_data["chat_sessions"][-10000:]
        
        return {"message": "Session recorded successfully"}
        
    except Exception as e:
        logger.error(f"Error recording chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/export")
async def export_analytics_data(
    format: str = Query(default="json", regex="^(json|csv)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Export analytics data in different formats
    """
    try:
        # Filter data by date range if provided
        filtered_data = analytics_data["chat_sessions"]
        
        if start_date:
            start = datetime.fromisoformat(start_date)
            filtered_data = [
                session for session in filtered_data 
                if datetime.fromisoformat(session.get("timestamp", "1970-01-01")) >= start
            ]
        
        if end_date:
            end = datetime.fromisoformat(end_date)
            filtered_data = [
                session for session in filtered_data 
                if datetime.fromisoformat(session.get("timestamp", "1970-01-01")) <= end
            ]
        
        if format == "json":
            return {
                "data": filtered_data,
                "format": "json",
                "count": len(filtered_data),
                "exported_at": datetime.now().isoformat()
            }
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_data = "timestamp,sentiment,confidence,response_time\n"
            for session in filtered_data:
                csv_data += f"{session.get('timestamp', '')},{session.get('sentiment', '')},{session.get('confidence', '')},{session.get('response_time', '')}\n"
            
            return {
                "data": csv_data,
                "format": "csv",
                "count": len(filtered_data),
                "exported_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error exporting analytics data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
