from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from app.models.chat_models import ChatRequest, ChatResponse
from app.models.finbert_model import FinBERTModel

logger = logging.getLogger(__name__)
router = APIRouter()

def get_finbert_model(request: Request) -> FinBERTModel:
    """Dependency to get FinBERT model from app state"""
    return request.app.state.finbert_model

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    finbert_model: FinBERTModel = Depends(get_finbert_model)
):
    """
    Process chat message and return analysis with sentiment and entities
    """
    try:
        if not finbert_model.is_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Analyze the message
        result = await finbert_model.analyze_text(
            text=chat_request.message,
            include_entities=chat_request.include_entities
        )
        
        # Create response
        response = ChatResponse(
            message=result["message"],
            sentiment=result["sentiment"] if chat_request.include_sentiment else None,
            entities=result["entities"] if chat_request.include_entities else None,
            response_time=result["response_time"],
            timestamp=datetime.fromisoformat(result["timestamp"]),
            conversation_id=str(uuid.uuid4())
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history")
async def get_chat_history(
    conversation_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get chat history for a conversation
    """
    # This would typically query a database
    # For now, return a placeholder response
    return {
        "conversation_id": conversation_id,
        "messages": [],
        "total_count": 0,
        "limit": limit
    }

@router.post("/chat/batch")
async def batch_analyze(
    messages: List[str],
    finbert_model: FinBERTModel = Depends(get_finbert_model)
):
    """
    Analyze multiple messages in batch
    """
    try:
        if not finbert_model.is_loaded:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        results = []
        for message in messages:
            result = await finbert_model.analyze_text(message)
            results.append(result)
        
        return {
            "batch_size": len(messages),
            "results": results,
            "total_processing_time": sum(r["response_time"] for r in results)
        }
        
    except Exception as e:
        logger.error(f"Error in batch analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/info")
async def get_model_info(
    finbert_model: FinBERTModel = Depends(get_finbert_model)
):
    """
    Get information about the current model
    """
    try:
        return finbert_model.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
