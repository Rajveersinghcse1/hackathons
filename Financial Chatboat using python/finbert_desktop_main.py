"""
FinBERT Desktop Backend - Simplified Version
Provides financial sentiment analysis and chatbot capabilities for desktop app
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
import sqlite3
import json
import random
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinBERTSimulated:
    """Simulated FinBERT model for financial sentiment analysis"""
    
    def __init__(self):
        # Financial keywords for sentiment analysis
        self.positive_financial_terms = [
            'profit', 'growth', 'revenue', 'increase', 'bullish', 'gain', 'rise',
            'positive', 'strong', 'up', 'boost', 'surge', 'rally', 'bull market',
            'dividend', 'earnings beat', 'outperform', 'upgrade', 'buy', 'invest'
        ]
        
        self.negative_financial_terms = [
            'loss', 'decline', 'decrease', 'bearish', 'fall', 'drop', 'negative',
            'weak', 'down', 'crash', 'plunge', 'bear market', 'recession',
            'bankruptcy', 'debt', 'downgrade', 'sell', 'avoid', 'risk'
        ]
        
        self.neutral_terms = [
            'stable', 'flat', 'unchanged', 'hold', 'maintain', 'steady',
            'sideways', 'consolidate', 'range', 'neutral'
        ]
        
        logger.info("FinBERT Simulated model initialized")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze financial sentiment of text"""
        text_lower = text.lower()
        
        positive_score = sum(1 for term in self.positive_financial_terms if term in text_lower)
        negative_score = sum(1 for term in self.negative_financial_terms if term in text_lower)
        neutral_score = sum(1 for term in self.neutral_terms if term in text_lower)
        
        total_score = positive_score + negative_score + neutral_score
        
        if total_score == 0:
            # No financial terms detected, general sentiment
            if any(word in text_lower for word in ['good', 'great', 'excellent', 'amazing']):
                return {"label": "positive", "confidence": 0.65, "scores": {"positive": 0.65, "negative": 0.2, "neutral": 0.15}}
            elif any(word in text_lower for word in ['bad', 'terrible', 'awful', 'horrible']):
                return {"label": "negative", "confidence": 0.65, "scores": {"positive": 0.15, "negative": 0.65, "neutral": 0.2}}
            else:
                return {"label": "neutral", "confidence": 0.6, "scores": {"positive": 0.2, "negative": 0.2, "neutral": 0.6}}
        
        # Calculate weighted scores
        if positive_score > negative_score and positive_score > neutral_score:
            confidence = min(0.85, 0.6 + (positive_score * 0.1))
            return {"label": "positive", "confidence": confidence, 
                   "scores": {"positive": confidence, "negative": (1-confidence)*0.6, "neutral": (1-confidence)*0.4}}
        elif negative_score > positive_score and negative_score > neutral_score:
            confidence = min(0.85, 0.6 + (negative_score * 0.1))
            return {"label": "negative", "confidence": confidence,
                   "scores": {"positive": (1-confidence)*0.4, "negative": confidence, "neutral": (1-confidence)*0.6}}
        else:
            confidence = min(0.8, 0.5 + (neutral_score * 0.1))
            return {"label": "neutral", "confidence": confidence,
                   "scores": {"positive": (1-confidence)*0.3, "negative": (1-confidence)*0.3, "neutral": confidence}}

class FinancialChatbot:
    """Financial chatbot with FinBERT capabilities"""
    
    def __init__(self):
        self.finbert = FinBERTSimulated()
        self.memory_db = "finbert_desktop.db"
        self.init_database()
        self.conversation_history = []
        
        # Financial knowledge base
        self.financial_knowledge = {
            'stock market': "The stock market is a collection of exchanges where stocks are traded. It reflects the overall health of the economy and individual companies.",
            'bull market': "A bull market is characterized by rising stock prices and investor optimism, typically lasting for extended periods.",
            'bear market': "A bear market involves declining stock prices, usually defined as a 20% drop from recent highs, often accompanied by pessimism.",
            'dividend': "Dividends are payments made by companies to shareholders, typically from profits, as a way to return value to investors.",
            'p/e ratio': "Price-to-Earnings ratio compares a company's stock price to its earnings per share, helping evaluate if a stock is over or undervalued.",
            'volatility': "Market volatility measures how much stock prices fluctuate over time, indicating the level of risk and uncertainty.",
            'portfolio': "An investment portfolio is a collection of financial investments like stocks, bonds, and other assets owned by an individual or institution."
        }
        
        logger.info("Financial Chatbot initialized")
    
    def init_database(self):
        """Initialize SQLite database for conversation storage"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                sentiment_label TEXT,
                sentiment_confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Process user message and generate response"""
        try:
            start_time = datetime.now()
            
            # Analyze sentiment using FinBERT
            sentiment_result = self.finbert.analyze_sentiment(message)
            
            # Determine response type
            response_type = self.classify_message_type(message)
            
            # Generate response based on type
            response = await self.generate_response(message, response_type, sentiment_result)
            
            # Store conversation
            self.store_conversation(message, response, sentiment_result, session_id)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "response": response,
                "sentiment": sentiment_result,
                "response_type": response_type,
                "processing_time": processing_time,
                "confidence": self.calculate_response_confidence(response, sentiment_result),
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your message. Please try again.",
                "sentiment": {"label": "neutral", "confidence": 0.5},
                "response_type": "error",
                "processing_time": 0,
                "confidence": 0.3,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def classify_message_type(self, message: str) -> str:
        """Classify the type of user message"""
        message_lower = message.lower()
        
        # Financial question indicators
        if any(word in message_lower for word in ['what is', 'explain', 'define', 'meaning']):
            return 'definition'
        
        # Analysis request indicators  
        if any(word in message_lower for word in ['analyze', 'sentiment', 'opinion', 'think']):
            return 'analysis'
        
        # Market inquiry indicators
        if any(word in message_lower for word in ['market', 'stock', 'price', 'trend']):
            return 'market_inquiry'
        
        # Advice request indicators
        if any(word in message_lower for word in ['should i', 'recommend', 'advice', 'invest']):
            return 'advice_request'
        
        # Greeting indicators
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return 'greeting'
        
        return 'general'
    
    async def generate_response(self, message: str, response_type: str, sentiment: Dict) -> str:
        """Generate appropriate response based on message type"""
        
        if response_type == 'greeting':
            return self.generate_greeting_response()
        
        elif response_type == 'definition':
            return self.generate_definition_response(message)
        
        elif response_type == 'analysis':
            return self.generate_analysis_response(message, sentiment)
        
        elif response_type == 'market_inquiry':
            return self.generate_market_response(message, sentiment)
        
        elif response_type == 'advice_request':
            return self.generate_advice_response(message, sentiment)
        
        else:
            return self.generate_general_response(message, sentiment)
    
    def generate_greeting_response(self) -> str:
        """Generate greeting response"""
        greetings = [
            "Hello! I'm your FinBERT financial assistant. I can help you with financial analysis, market insights, and investment guidance. What would you like to know?",
            "Hi there! I'm here to assist you with financial questions and analysis using advanced FinBERT technology. How can I help you today?",
            "Welcome! I'm your AI financial advisor powered by FinBERT. I can analyze sentiment, explain financial concepts, and provide market insights. What's on your mind?"
        ]
        return random.choice(greetings)
    
    def generate_definition_response(self, message: str) -> str:
        """Generate definition response"""
        message_lower = message.lower()
        
        # Check if we have knowledge about the topic
        for term, definition in self.financial_knowledge.items():
            if term in message_lower:
                return f"📚 {term.title()}: {definition}\n\nWould you like me to explain any related concepts or analyze the sentiment around this topic?"
        
        # General definition response
        if 'finbert' in message_lower:
            return "FinBERT is a financial domain-specific language model based on BERT, designed to understand and analyze financial text with high accuracy. It's particularly effective for sentiment analysis in financial contexts, helping investors and analysts understand market sentiment from news, reports, and social media."
        
        return "I'd be happy to explain financial concepts! Could you please specify which financial term or concept you'd like me to define? I have extensive knowledge about markets, investments, trading, and financial analysis."
    
    def generate_analysis_response(self, message: str, sentiment: Dict) -> str:
        """Generate analysis response"""
        sentiment_label = sentiment['label']
        confidence = sentiment['confidence']
        
        analysis = f"📊 **FinBERT Sentiment Analysis Results:**\n\n"
        analysis += f"**Sentiment:** {sentiment_label.upper()} ({confidence:.2%} confidence)\n"
        analysis += f"**Scores:** Positive: {sentiment['scores']['positive']:.2%}, "
        analysis += f"Negative: {sentiment['scores']['negative']:.2%}, "
        analysis += f"Neutral: {sentiment['scores']['neutral']:.2%}\n\n"
        
        if sentiment_label == 'positive':
            analysis += "💹 The text shows **positive financial sentiment**, indicating optimism, growth potential, or favorable market conditions. This suggests bullish market indicators or positive investor sentiment."
        elif sentiment_label == 'negative':
            analysis += "📉 The text shows **negative financial sentiment**, indicating concerns, risks, or unfavorable market conditions. This suggests bearish market indicators or cautious investor sentiment."
        else:
            analysis += "⚖️ The text shows **neutral financial sentiment**, indicating balanced or uncertain market conditions. This suggests a wait-and-see approach or mixed market signals."
        
        return analysis
    
    def generate_market_response(self, message: str, sentiment: Dict) -> str:
        """Generate market-related response"""
        sentiment_label = sentiment['label']
        
        base_response = "🏦 **Market Analysis:** Based on the sentiment analysis of your message, "
        
        if sentiment_label == 'positive':
            base_response += "the market indicators appear favorable. Positive sentiment often correlates with:\n"
            base_response += "• Increased investor confidence\n• Potential price appreciation\n• Growing market optimism\n• Higher trading volumes\n\n"
            base_response += "However, always conduct thorough research and consider multiple factors before making investment decisions."
        
        elif sentiment_label == 'negative':
            base_response += "the market indicators suggest caution. Negative sentiment often correlates with:\n"
            base_response += "• Decreased investor confidence\n• Potential price volatility\n• Market uncertainty\n• Risk-off behavior\n\n"
            base_response += "Consider diversification and risk management strategies during such periods."
        
        else:
            base_response += "the market sentiment appears neutral or mixed. This often indicates:\n"
            base_response += "• Consolidation periods\n• Awaiting key economic data\n• Balanced investor sentiment\n• Range-bound trading\n\n"
            base_response += "Such periods can be good for strategy planning and position evaluation."
        
        return base_response
    
    def generate_advice_response(self, message: str, sentiment: Dict) -> str:
        """Generate advice response with disclaimer"""
        disclaimer = "⚠️ **Disclaimer:** The following is educational information only and not financial advice. Always consult with qualified financial advisors.\n\n"
        
        advice = "💡 **General Financial Guidance:**\n"
        advice += "• Diversify your portfolio across different asset classes\n"
        advice += "• Invest only what you can afford to lose\n"
        advice += "• Consider your risk tolerance and investment timeline\n"
        advice += "• Stay informed about market trends and economic indicators\n"
        advice += "• Regular portfolio review and rebalancing is important\n\n"
        
        sentiment_label = sentiment['label']
        if sentiment_label == 'positive':
            advice += "📈 Current sentiment analysis suggests optimism, but remember that markets can be unpredictable."
        elif sentiment_label == 'negative':
            advice += "📉 Current sentiment analysis suggests caution, which might be a good time for defensive strategies."
        else:
            advice += "⚖️ Current sentiment analysis is neutral, suggesting a balanced approach might be appropriate."
        
        return disclaimer + advice
    
    def generate_general_response(self, message: str, sentiment: Dict) -> str:
        """Generate general response"""
        responses = [
            "I understand your message and have analyzed its financial sentiment. Is there a specific financial topic you'd like me to help you with?",
            "Thank you for your message. As your FinBERT assistant, I can provide financial analysis, explain market concepts, or analyze sentiment. What would you like to explore?",
            "I've processed your message using FinBERT analysis. Would you like me to provide more detailed financial insights or explain any specific concepts?"
        ]
        
        base_response = random.choice(responses)
        sentiment_note = f"\n\n📊 Sentiment detected: {sentiment['label']} ({sentiment['confidence']:.1%} confidence)"
        
        return base_response + sentiment_note
    
    def calculate_response_confidence(self, response: str, sentiment: Dict) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.75
        
        # Adjust based on sentiment confidence
        sentiment_conf = sentiment.get('confidence', 0.5)
        base_confidence += (sentiment_conf - 0.5) * 0.3
        
        # Adjust based on response length and detail
        if len(response) > 200:
            base_confidence += 0.1
        
        # Adjust based on specific financial terms
        financial_indicators = ['analysis', 'market', 'sentiment', 'investment', 'financial']
        if any(indicator in response.lower() for indicator in financial_indicators):
            base_confidence += 0.05
        
        return min(base_confidence, 0.95)
    
    def store_conversation(self, user_message: str, bot_response: str, 
                         sentiment: Dict, session_id: str):
        """Store conversation in database"""
        try:
            conn = sqlite3.connect(self.memory_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (user_message, bot_response, sentiment_label, sentiment_confidence, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_message, bot_response, sentiment['label'], 
                  sentiment['confidence'], session_id, json.dumps(sentiment)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing conversation: {e}")

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: str = Field("default", description="Session identifier")

class ChatResponse(BaseModel):
    response: str
    sentiment: Dict[str, Any]
    response_type: str
    processing_time: float
    confidence: float
    timestamp: str
    session_id: str

# FastAPI app
app = FastAPI(
    title="FinBERT Desktop Chatbot API",
    description="Financial sentiment analysis and chatbot API for desktop application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot
chatbot = None

@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup"""
    global chatbot
    try:
        logger.info("Initializing FinBERT Desktop Chatbot...")
        chatbot = FinancialChatbot()
        logger.info("FinBERT Desktop Chatbot initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing chatbot: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FinBERT Desktop Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Financial Sentiment Analysis",
            "FinBERT-powered responses",
            "Market insights",
            "Investment guidance",
            "Conversation memory"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global chatbot
    return {
        "status": "healthy",
        "chatbot_status": "loaded" if chatbot else "not_loaded",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Chat endpoint for desktop app"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        result = await chatbot.process_message(
            message=chat_request.message,
            session_id=chat_request.session_id
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats")
async def get_stats():
    """Get chatbot statistics"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(status_code=503, detail="Chatbot not initialized")
    
    try:
        conn = sqlite3.connect(chatbot.memory_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        cursor.execute('SELECT sentiment_label, COUNT(*) FROM conversations GROUP BY sentiment_label')
        sentiment_breakdown = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_conversations": total_conversations,
            "sentiment_breakdown": sentiment_breakdown,
            "features": [
                "FinBERT Sentiment Analysis",
                "Financial Knowledge Base",
                "Conversation Memory",
                "Market Insights"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("finbert_desktop_main:app", host="0.0.0.0", port=8001, reload=True)
