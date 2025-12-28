import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass
import pandas as pd
import torch
import torch.nn.functional as F
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinBERTModel:
    """Professional FinBERT Model for financial sentiment analysis"""
    
    def __init__(self):
        self.model_name = "yiyanghkust/finbert-tone"
        self.tokenizer = None
        self.model = None
        self.finbert_pipeline = None
        self.is_model_loaded = False
        
        # Fallback keyword-based analysis
        self.sentiment_keywords = {
            'positive': ['profit', 'profits', 'growth', 'increase', 'gain', 'rise', 'strong', 'optimistic', 
                        'record', 'success', 'outperform', 'bullish', 'buy', 'upgrade', 'beat', 'exceed',
                        'robust', 'solid', 'impressive', 'surge', 'rally', 'boom', 'expansion'],
            'negative': ['loss', 'losses', 'decline', 'fall', 'drop', 'weak', 'poor', 'challenge', 'risk', 
                        'concern', 'underperform', 'bearish', 'sell', 'downgrade', 'miss', 'disappoint',
                        'plunge', 'crash', 'recession', 'crisis', 'bankruptcy', 'deficit'],
            'neutral': ['stable', 'maintain', 'steady', 'expect', 'anticipate', 'guidance', 'analyst', 
                       'forecast', 'outlook', 'target', 'estimate', 'unchanged', 'hold', 'neutral']
        }
        
        self._try_load_finbert()
        
    def _try_load_finbert(self):
        """Try to load the actual FinBERT model"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
            
            logger.info("Loading FinBERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.finbert_pipeline = pipeline("sentiment-analysis", model=self.model, tokenizer=self.tokenizer)
            self.is_model_loaded = True
            logger.info("FinBERT model loaded successfully!")
            
        except Exception as e:
            logger.warning(f"Could not load FinBERT model: {e}")
            logger.info("Using fallback keyword-based sentiment analysis")
            self.is_model_loaded = False
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze financial sentiment using FinBERT or fallback method"""
        if self.is_model_loaded:
            return self._analyze_with_finbert(text)
        else:
            return self._analyze_with_keywords(text)
    
    def _analyze_with_finbert(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using the actual FinBERT model"""
        try:
            # Tokenize and run raw model output for detailed probabilities
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = self.model(**inputs)
            
            # Convert logits to probabilities
            probs = F.softmax(outputs.logits, dim=-1).detach().numpy()[0]
            
            # Map labels (FinBERT uses: 0=negative, 1=neutral, 2=positive)
            labels = self.model.config.id2label if hasattr(self.model.config, 'id2label') else {0: 'negative', 1: 'neutral', 2: 'positive'}
            
            # Extract probabilities
            negative_prob = float(probs[0]) if 0 in labels and labels[0].lower() in ['negative', 'bearish'] else float(probs[0])
            neutral_prob = float(probs[1]) if 1 in labels and labels[1].lower() in ['neutral', 'hold'] else float(probs[1])
            positive_prob = float(probs[2]) if 2 in labels and labels[2].lower() in ['positive', 'bullish'] else float(probs[2])
            
            # Determine predicted sentiment
            predicted_idx = probs.argmax()
            predicted_sentiment = labels.get(predicted_idx, 'neutral').lower()
            confidence = float(probs[predicted_idx])
            
            return {
                "Text": text,
                "Negative": round(negative_prob, 4),
                "Neutral": round(neutral_prob, 4),
                "Positive": round(positive_prob, 4),
                "Predicted Sentiment": predicted_sentiment,
                "confidence": round(confidence, 4),
                "model_used": "FinBERT"
            }
            
        except Exception as e:
            logger.error(f"Error in FinBERT analysis: {e}")
            return self._analyze_with_keywords(text)
    
    def _analyze_with_keywords(self, text: str) -> Dict[str, Any]:
        """Fallback keyword-based sentiment analysis"""
        text_lower = text.lower()
        
        # Count keywords with weighted scoring
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        for word in self.sentiment_keywords['positive']:
            if word in text_lower:
                positive_score += text_lower.count(word) * 2
                
        for word in self.sentiment_keywords['negative']:
            if word in text_lower:
                negative_score += text_lower.count(word) * 2
                
        for word in self.sentiment_keywords['neutral']:
            if word in text_lower:
                neutral_score += text_lower.count(word)
        
        total_score = positive_score + negative_score + neutral_score
        
        if total_score == 0:
            # No financial keywords found, analyze general sentiment
            positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
            negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor']
            
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                return {
                    "Text": text,
                    "Negative": 0.2,
                    "Neutral": 0.3,
                    "Positive": 0.5,
                    "Predicted Sentiment": "positive",
                    "confidence": 0.5,
                    "model_used": "Keyword-based"
                }
            elif neg_count > pos_count:
                return {
                    "Text": text,
                    "Negative": 0.5,
                    "Neutral": 0.3,
                    "Positive": 0.2,
                    "Predicted Sentiment": "negative",
                    "confidence": 0.5,
                    "model_used": "Keyword-based"
                }
            else:
                return {
                    "Text": text,
                    "Negative": 0.25,
                    "Neutral": 0.5,
                    "Positive": 0.25,
                    "Predicted Sentiment": "neutral",
                    "confidence": 0.5,
                    "model_used": "Keyword-based"
                }
        
        # Calculate probabilities based on financial keywords
        base_score = 1.0
        positive_prob = (positive_score + base_score) / (total_score + 3 * base_score)
        negative_prob = (negative_score + base_score) / (total_score + 3 * base_score)
        neutral_prob = (neutral_score + base_score) / (total_score + 3 * base_score)
        
        # Normalize probabilities
        total_prob = positive_prob + negative_prob + neutral_prob
        positive_prob /= total_prob
        negative_prob /= total_prob
        neutral_prob /= total_prob
        
        # Determine prediction
        if positive_prob > negative_prob and positive_prob > neutral_prob:
            predicted = "positive"
            confidence = positive_prob
        elif negative_prob > positive_prob and negative_prob > neutral_prob:
            predicted = "negative"
            confidence = negative_prob
        else:
            predicted = "neutral"
            confidence = neutral_prob
        
        return {
            "Text": text,
            "Negative": round(negative_prob, 4),
            "Neutral": round(neutral_prob, 4),
            "Positive": round(positive_prob, 4),
            "Predicted Sentiment": predicted,
            "confidence": round(confidence, 4),
            "model_used": "Keyword-based"
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts and return results as list"""
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
        return results
    
    def analyze_to_dataframe(self, texts: List[str]) -> pd.DataFrame:
        """Analyze multiple texts and return results as pandas DataFrame"""
        results = self.analyze_batch(texts)
        return pd.DataFrame(results)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "is_model_loaded": self.is_model_loaded,
            "model_type": "FinBERT" if self.is_model_loaded else "Keyword-based",
            "capabilities": [
                "Financial Sentiment Analysis",
                "Batch Processing",
                "Confidence Scoring",
                "Multi-class Classification (Positive/Negative/Neutral)"
            ]
        }

# Pydantic models for API
class AnalysisRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")

class BatchAnalysisRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze")

class AnalysisResponse(BaseModel):
    Text: str
    Negative: float
    Neutral: float
    Positive: float
    Predicted_Sentiment: str = Field(alias="Predicted Sentiment")
    confidence: float
    model_used: str

# Create FastAPI app
app = FastAPI(
    title="FinBERT Financial Sentiment Analysis API",
    description="Professional FinBERT API for financial sentiment analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize FinBERT model
finbert_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize the FinBERT model on startup"""
    global finbert_model
    try:
        logger.info("Initializing FinBERT Model...")
        finbert_model = FinBERTModel()
        logger.info("FinBERT Model initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing FinBERT model: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FinBERT Financial Sentiment Analysis API",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": finbert_model.is_model_loaded if finbert_model else False
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global finbert_model
    return {
        "status": "healthy",
        "finbert_model_status": "loaded" if finbert_model and finbert_model.is_model_loaded else "fallback",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/analyze")
async def analyze_sentiment(request: AnalysisRequest):
    """Analyze sentiment of a single text"""
    global finbert_model
    
    if not finbert_model:
        raise HTTPException(status_code=503, detail="FinBERT model not initialized")
    
    try:
        result = finbert_model.analyze_sentiment(request.text)
        return result
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze_batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """Analyze sentiment of multiple texts"""
    global finbert_model
    
    if not finbert_model:
        raise HTTPException(status_code=503, detail="FinBERT model not initialized")
    
    try:
        results = finbert_model.analyze_batch(request.texts)
        return {
            "results": results,
            "total_analyzed": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/model/info")
async def get_model_info():
    """Get detailed model information"""
    global finbert_model
    
    if not finbert_model:
        return {
            "status": "FinBERT model not initialized",
            "loaded": False
        }
    
    return finbert_model.get_model_info()

@app.post("/api/v1/demo")
async def demo_analysis():
    """Demo endpoint with sample financial texts"""
    global finbert_model
    
    if not finbert_model:
        raise HTTPException(status_code=503, detail="FinBERT model not initialized")
    
    # Sample financial texts
    sample_texts = [
        "The company reported record profits this quarter.",
        "Stock prices fell sharply due to weak earnings guidance.", 
        "Analysts expect steady growth in the upcoming fiscal year.",
        "The merger deal faced regulatory challenges.",
        "Investors are optimistic about the new product launch."
    ]
    
    try:
        results = finbert_model.analyze_batch(sample_texts)
        return {
            "demo_results": results,
            "model_info": finbert_model.get_model_info(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in demo analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("finbert_main:app", host="0.0.0.0", port=8001, reload=True)
