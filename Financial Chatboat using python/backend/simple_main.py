from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import time
import random
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple Pydantic models
class ChatRequest(BaseModel):
    message: str
    include_sentiment: bool = True
    include_entities: bool = True

class SentimentResult(BaseModel):
    label: str
    confidence: float
    raw_scores: Dict[str, float]

class EntityResult(BaseModel):
    text: str
    label: str
    confidence: float
    start: int
    end: int

class ChatResponse(BaseModel):
    message: str
    sentiment: Optional[SentimentResult] = None
    entities: Optional[List[EntityResult]] = None
    response_time: float
    timestamp: datetime

# Simple FinBERT mock class
class SimpleFinBERT:
    def __init__(self):
        self.is_loaded = True
        logger.info("Simple FinBERT model initialized")
    
    async def analyze_text(self, text: str, include_entities: bool = True) -> Dict[str, Any]:
        start_time = time.time()
        
        # Simple sentiment analysis simulation
        positive_words = ['good', 'great', 'excellent', 'profit', 'growth', 'surge', 'rise', 'up', 'gain', 'bullish']
        negative_words = ['bad', 'terrible', 'loss', 'decline', 'fall', 'down', 'crash', 'bearish', 'drop', 'poor']
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        # Determine sentiment
        if positive_score > negative_score:
            sentiment_label = "positive"
            confidence = 0.7 + (positive_score * 0.1)
        elif negative_score > positive_score:
            sentiment_label = "negative"
            confidence = 0.7 + (negative_score * 0.1)
        else:
            sentiment_label = "neutral"
            confidence = 0.6 + random.uniform(0, 0.2)
        
        confidence = min(confidence, 0.95)
        
        # Create sentiment result
        sentiment = {
            "label": sentiment_label,
            "confidence": confidence,
            "raw_scores": {
                "positive": confidence if sentiment_label == "positive" else 1 - confidence,
                "negative": confidence if sentiment_label == "negative" else (1 - confidence) / 2,
                "neutral": confidence if sentiment_label == "neutral" else (1 - confidence) / 2
            }
        }
        
        # Simple entity extraction
        entities = []
        if include_entities:
            financial_entities = {
                "STOCK": ["stock", "shares", "equity", "NYSE", "NASDAQ"],
                "COMPANY": ["Apple", "Microsoft", "Google", "Tesla", "Amazon"],
                "CURRENCY": ["USD", "EUR", "GBP", "dollar", "euro"],
                "METRIC": ["revenue", "profit", "earnings", "ROI", "P/E"]
            }
            
            for entity_type, keywords in financial_entities.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        start_idx = text_lower.find(keyword.lower())
                        entities.append({
                            "text": keyword,
                            "label": entity_type,
                            "confidence": 0.8,
                            "start": start_idx,
                            "end": start_idx + len(keyword)
                        })
        
        # Generate response
        response_message = self._generate_response(text, sentiment)
        
        response_time = time.time() - start_time
        
        return {
            "message": response_message,
            "sentiment": sentiment,
            "entities": entities,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_response(self, text: str, sentiment: Dict[str, Any]) -> str:
        sentiment_label = sentiment["label"]
        confidence = sentiment["confidence"]
        
        if sentiment_label == "positive":
            return f"Great! I detected positive financial sentiment in your message (confidence: {confidence:.2f}). This suggests optimistic market outlook or favorable financial conditions."
        elif sentiment_label == "negative":
            return f"I detected negative financial sentiment in your message (confidence: {confidence:.2f}). This indicates concerns or pessimistic outlook regarding financial matters."
        else:
            return f"Your message shows neutral financial sentiment (confidence: {confidence:.2f}), indicating a balanced perspective without strong positive or negative bias."

# Create FastAPI app
app = FastAPI(
    title="Financial Chatbot API",
    description="Simple Financial Chatbot using mock FinBERT",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model
finbert_model = SimpleFinBERT()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_status": "loaded",
        "version": "1.0.0"
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Process chat message and return analysis"""
    try:
        result = await finbert_model.analyze_text(
            text=chat_request.message,
            include_entities=chat_request.include_entities
        )
        
        response = ChatResponse(
            message=result["message"],
            sentiment=result["sentiment"] if chat_request.include_sentiment else None,
            entities=result["entities"] if chat_request.include_entities else None,
            response_time=result["response_time"],
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/model/info")
async def get_model_info():
    """Get model information"""
    return {
        "model_name": "Simple FinBERT Mock",
        "is_loaded": True,
        "model_type": "FinBERT",
        "version": "1.0.0"
    }

@app.get("/api/v1/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    return {
        "total_chat_sessions": 42,
        "sentiment_distribution": {
            "positive": 25,
            "negative": 10,
            "neutral": 7
        },
        "average_response_time": 0.125,
        "active_models": 1,
        "fine_tuned_models": 0
    }

@app.get("/api/v1/analytics/sentiment-trends")
async def get_sentiment_trends(days: int = 7):
    """Get sentiment trends"""
    trends = []
    for i in range(days):
        trends.append({
            "date": f"2025-09-{2-i:02d}",
            "positive": 30 + (i * 2),
            "negative": 20 - i,
            "neutral": 50 + i,
            "total_messages": 100 + (i * 5)
        })
    
    return {"trends": trends}

@app.get("/api/v1/analytics/popular-topics")
async def get_popular_topics(limit: int = 10):
    """Get popular topics"""
    topics = [
        {"topic": "stock market", "mentions": 150, "sentiment": "positive"},
        {"topic": "cryptocurrency", "mentions": 120, "sentiment": "neutral"},
        {"topic": "inflation", "mentions": 100, "sentiment": "negative"},
        {"topic": "earnings reports", "mentions": 90, "sentiment": "positive"},
    ]
    
    return {"topics": topics[:limit]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)
