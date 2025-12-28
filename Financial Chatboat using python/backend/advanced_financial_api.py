"""
Advanced Financial Assistance Chatbot API
FastAPI backend serving the comprehensive financial ML models
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import asyncio
import json

from advanced_financial_bot import get_financial_bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="User profile data")
    session_id: str = Field("default", description="Session identifier")

class ChatResponse(BaseModel):
    message: str
    response: str
    sentiment: Dict[str, Any]
    intent: str
    analysis: Dict[str, Any]
    recommendations: List[str]
    timestamp: str

class FinancialAnalysisRequest(BaseModel):
    analysis_type: str = Field(..., description="Type of analysis: ratios, risk, portfolio, planning")
    data: Dict[str, Any] = Field(..., description="Financial data for analysis")

class UserProfile(BaseModel):
    age: Optional[int] = Field(None, ge=18, le=100, description="User age")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance: low, medium, high")
    investment_horizon: Optional[int] = Field(None, ge=1, le=50, description="Investment horizon in years")
    income: Optional[float] = Field(None, ge=0, description="Annual income")
    current_savings: Optional[float] = Field(None, ge=0, description="Current savings")
    monthly_savings: Optional[float] = Field(None, ge=0, description="Monthly savings amount")
    goals: Optional[List[str]] = Field(None, description="Financial goals")
    retirement_age: Optional[int] = Field(None, ge=50, le=80, description="Target retirement age")

class MarketAnalysisRequest(BaseModel):
    market_data: Optional[List[float]] = Field(None, description="Historical market data")
    timeframe: Optional[str] = Field("1month", description="Analysis timeframe")

# Create FastAPI app
app = FastAPI(
    title="Advanced Financial Assistant API",
    description="Comprehensive Financial Analysis and Advisory Chatbot with ML Models",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize bot
bot = None

@app.on_event("startup")
async def startup_event():
    """Initialize the financial bot on startup"""
    global bot
    try:
        logger.info("Initializing Advanced Financial Assistant...")
        bot = get_financial_bot()
        logger.info("Advanced Financial Assistant initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing financial bot: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Advanced Financial Assistant API",
        "version": "3.0.0",
        "status": "running",
        "capabilities": [
            "Multi-Model ML Analysis",
            "Sentiment Analysis",
            "Intent Classification", 
            "Risk Assessment",
            "Portfolio Optimization",
            "Financial Planning",
            "Market Analysis",
            "Company Valuation",
            "Investment Advisory"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global bot
    return {
        "status": "healthy",
        "bot_status": "loaded" if bot else "not_loaded",
        "models_active": ["Sentiment", "Intent", "Risk", "Market", "Portfolio"] if bot else [],
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Advanced chat endpoint with comprehensive financial analysis"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        result = bot.get_comprehensive_response(
            user_message=chat_request.message,
            user_profile=chat_request.user_profile or {}
        )
        
        return ChatResponse(
            message=result['message'],
            response=result['response'],
            sentiment=result['sentiment'],
            intent=result['intent'],
            analysis=result['analysis'],
            recommendations=result['recommendations'],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analysis/financial")
async def financial_analysis(analysis_request: FinancialAnalysisRequest):
    """Perform specific financial analysis"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        analysis_type = analysis_request.analysis_type.lower()
        data = analysis_request.data
        
        if analysis_type == "ratios":
            result = bot.calculate_financial_ratios(data)
        elif analysis_type == "risk":
            result = bot.assess_investment_risk(data)
        elif analysis_type == "portfolio":
            result = bot.portfolio_optimization(data)
        elif analysis_type == "planning":
            result = bot.financial_planning_analysis(data)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        return {
            "analysis_type": analysis_type,
            "results": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in financial analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/investment/advice")
async def get_investment_advice(user_profile: UserProfile):
    """Get personalized investment advice"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        profile_dict = user_profile.dict(exclude_none=True)
        advice = bot.generate_investment_advice(profile_dict)
        
        return {
            "user_profile": profile_dict,
            "investment_advice": advice,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating investment advice: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/market/analysis")
async def market_analysis(market_request: MarketAnalysisRequest):
    """Analyze market trends and conditions"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        analysis = bot.analyze_market_trends(market_request.market_data)
        
        return {
            "market_analysis": analysis,
            "timeframe": market_request.timeframe,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sentiment/analyze")
async def analyze_sentiment(text: str):
    """Analyze sentiment of financial text"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        sentiment = bot.analyze_sentiment(text)
        
        return {
            "text": text,
            "sentiment_analysis": sentiment,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/conversation/history")
async def get_conversation_history(limit: int = 10):
    """Get conversation history"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        history = bot.get_conversation_history(limit)
        
        return {
            "conversation_history": history,
            "total_retrieved": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """Get comprehensive analytics summary"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        analytics = bot.get_analytics_summary()
        
        return {
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/knowledge/financial-ratios")
async def get_financial_ratios_info():
    """Get information about financial ratios"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    return {
        "financial_ratios": bot.financial_ratios,
        "description": "Comprehensive guide to financial ratio analysis and interpretation"
    }

@app.get("/api/v1/knowledge/investment-strategies")
async def get_investment_strategies():
    """Get information about investment strategies"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    return {
        "investment_strategies": bot.investment_strategies,
        "description": "Overview of different investment strategies and their characteristics"
    }

@app.get("/api/v1/knowledge/risk-factors")
async def get_risk_factors():
    """Get information about investment risk factors"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    return {
        "risk_factors": bot.risk_factors,
        "description": "Comprehensive overview of investment risk factors and their implications"
    }

@app.post("/api/v1/portfolio/optimize")
async def optimize_portfolio(assets: Dict[str, Dict[str, float]]):
    """Optimize portfolio allocation"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        optimization = bot.portfolio_optimization(assets)
        
        return {
            "input_assets": assets,
            "optimization_results": optimization,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in portfolio optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/demo/sample-analysis")
async def demo_analysis():
    """Demonstrate various analysis capabilities"""
    global bot
    
    if not bot:
        raise HTTPException(status_code=503, detail="Financial bot not initialized")
    
    try:
        # Sample financial data
        sample_financial_data = {
            'stock_price': 150.50,
            'eps': 8.25,
            'total_debt': 5000000,
            'total_equity': 15000000,
            'current_assets': 8000000,
            'current_liabilities': 4000000,
            'net_income': 2500000,
            'shareholders_equity': 12000000
        }
        
        # Sample user profile
        sample_profile = {
            'age': 35,
            'risk_tolerance': 'medium',
            'investment_horizon': 15,
            'income': 85000,
            'current_savings': 50000,
            'monthly_savings': 1000,
            'goals': ['retirement', 'house'],
            'retirement_age': 65
        }
        
        # Perform various analyses
        ratios = bot.calculate_financial_ratios(sample_financial_data)
        investment_advice = bot.generate_investment_advice(sample_profile)
        market_analysis = bot.analyze_market_trends()
        financial_plan = bot.financial_planning_analysis(sample_profile)
        
        return {
            "demo_analysis": {
                "financial_ratios": ratios,
                "investment_advice": investment_advice,
                "market_analysis": market_analysis,
                "financial_planning": financial_plan
            },
            "sample_data": {
                "financial_data": sample_financial_data,
                "user_profile": sample_profile
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in demo analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("advanced_financial_api:app", host="0.0.0.0", port=8002, reload=True)
