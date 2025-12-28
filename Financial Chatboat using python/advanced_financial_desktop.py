"""
Advanced Financial Assistance Chatbot - Desktop Application
==========================================================
A comprehensive financial chatbot with multiple ML models for professional financial analysis
Uses: scikit-learn, pandas, numpy, yfinance for local data processing
No external APIs required for ML predictions
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import os
import pickle
from typing import Dict, List, Tuple, Any

# ML and Data Analysis Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

class AdvancedFinancialMLEngine:
    """
    Advanced ML Engine for Financial Analysis
    Contains multiple models for different financial tasks
    """
    
    def __init__(self):
        self.sentiment_model = None
        self.price_prediction_model = None
        self.risk_assessment_model = None
        self.portfolio_optimization_model = None
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Financial knowledge base
        self.financial_keywords = {
            'positive': ['profit', 'growth', 'increase', 'bull', 'rising', 'gain', 'upturn', 'surge', 
                        'boom', 'rally', 'outperform', 'beat', 'exceed', 'strong', 'robust'],
            'negative': ['loss', 'decline', 'bear', 'crash', 'fall', 'drop', 'recession', 'downturn',
                        'plunge', 'slump', 'underperform', 'miss', 'weak', 'volatile', 'risk'],
            'neutral': ['stable', 'maintain', 'hold', 'steady', 'flat', 'unchanged', 'sideways',
                       'consolidate', 'range', 'neutral', 'moderate', 'balanced']
        }
        
        # Market data cache
        self.market_data_cache = {}
        self.last_update = None
        
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize all ML models with sample data"""
        try:
            # Create sample training data for sentiment analysis
            self._train_sentiment_model()
            
            # Create sample training data for price prediction
            self._train_price_prediction_model()
            
            # Create sample training data for risk assessment
            self._train_risk_assessment_model()
            
            print("✅ All ML models initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing models: {e}")
    
    def _train_sentiment_model(self):
        """Train sentiment analysis model with financial text data"""
        # Sample financial text data
        texts = [
            "Company reports record quarterly profits exceeding expectations",
            "Stock price surges after positive earnings announcement", 
            "Market shows strong bullish sentiment with rising volumes",
            "Analysts upgrade rating following robust financial performance",
            "New product launch drives significant revenue growth",
            "Stock plummets on disappointing earnings report",
            "Company faces major losses due to market volatility",
            "Bearish sentiment dominates as recession fears grow",
            "Shares tumble following weak guidance from management",
            "Market crash wipes billions from company valuations",
            "Stock remains stable despite market uncertainties",
            "Company maintains steady performance in volatile market",
            "Neutral outlook as analysts await quarterly results",
            "Share price holds steady in sideways trading pattern",
            "Balanced portfolio shows moderate risk-adjusted returns"
        ]
        
        labels = ['positive'] * 5 + ['negative'] * 5 + ['neutral'] * 5
        
        # Vectorize text data
        X = self.vectorizer.fit_transform(texts)
        y = self.label_encoder.fit_transform(labels)
        
        # Train sentiment model
        self.sentiment_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.sentiment_model.fit(X, y)
        
        print("✅ Sentiment analysis model trained")
    
    def _train_price_prediction_model(self):
        """Train stock price prediction model"""
        # Generate sample stock data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: Open, High, Low, Volume, MA_5, MA_20, RSI, etc.
        features = np.random.randn(n_samples, 8)
        
        # Target: Next day price change (%)
        target = np.random.randn(n_samples) * 2  # ±2% typical daily change
        
        # Train price prediction model
        self.price_prediction_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.price_prediction_model.fit(features, target)
        
        print("✅ Price prediction model trained")
    
    def _train_risk_assessment_model(self):
        """Train risk assessment model"""
        # Generate sample risk data
        np.random.seed(42)
        n_samples = 500
        
        # Features: Volatility, Beta, Debt Ratio, Current Ratio, etc.
        features = np.random.randn(n_samples, 6)
        
        # Target: Risk level (Low, Medium, High)
        risk_levels = np.random.choice(['Low', 'Medium', 'High'], n_samples)
        target = self.label_encoder.fit_transform(risk_levels)
        
        # Train risk assessment model
        self.risk_assessment_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.risk_assessment_model.fit(features, target)
        
        print("✅ Risk assessment model trained")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of financial text"""
        try:
            # Preprocess text
            text_vector = self.vectorizer.transform([text])
            
            # Predict sentiment
            prediction = self.sentiment_model.predict(text_vector)[0]
            probabilities = self.sentiment_model.predict_proba(text_vector)[0]
            
            # Get sentiment label
            sentiment_labels = self.label_encoder.classes_
            sentiment = sentiment_labels[prediction]
            
            # Calculate confidence scores
            sentiment_scores = {
                sentiment_labels[i]: float(prob) 
                for i, prob in enumerate(probabilities)
            }
            
            return {
                'sentiment': sentiment,
                'confidence': float(max(probabilities)),
                'scores': sentiment_scores,
                'analysis': f"The text shows {sentiment} sentiment with {max(probabilities)*100:.1f}% confidence"
            }
            
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': {'positive': 0.33, 'negative': 0.33, 'neutral': 0.34},
                'analysis': f"Error in sentiment analysis: {str(e)}"
            }
    
    def predict_price_movement(self, stock_symbol: str) -> Dict[str, Any]:
        """Predict stock price movement using ML model"""
        try:
            # Get stock data
            stock_data = self.get_stock_data(stock_symbol)
            
            if stock_data is None:
                return {
                    'prediction': 0.0,
                    'confidence': 0.0,
                    'direction': 'neutral',
                    'analysis': 'Unable to fetch stock data'
                }
            
            # Calculate technical indicators
            features = self._calculate_technical_indicators(stock_data)
            
            # Make prediction
            prediction = self.price_prediction_model.predict([features])[0]
            
            # Determine direction
            direction = 'bullish' if prediction > 0.5 else 'bearish' if prediction < -0.5 else 'neutral'
            confidence = min(abs(prediction) / 2.0, 1.0)  # Normalize confidence
            
            return {
                'prediction': float(prediction),
                'confidence': float(confidence),
                'direction': direction,
                'analysis': f"ML model predicts {direction} movement with {confidence*100:.1f}% confidence"
            }
            
        except Exception as e:
            return {
                'prediction': 0.0,
                'confidence': 0.0,
                'direction': 'neutral',
                'analysis': f"Error in price prediction: {str(e)}"
            }
    
    def assess_investment_risk(self, stock_symbol: str) -> Dict[str, Any]:
        """Assess investment risk using ML model"""
        try:
            # Get stock data
            stock_data = self.get_stock_data(stock_symbol)
            
            if stock_data is None:
                return {
                    'risk_level': 'Medium',
                    'risk_score': 0.5,
                    'factors': ['Insufficient data'],
                    'analysis': 'Unable to assess risk due to data limitations'
                }
            
            # Calculate risk factors
            risk_features = self._calculate_risk_factors(stock_data)
            
            # Make risk prediction
            risk_prediction = self.risk_assessment_model.predict([risk_features])[0]
            risk_probabilities = self.risk_assessment_model.predict_proba([risk_features])[0]
            
            # Get risk level
            risk_labels = ['High', 'Low', 'Medium']  # Based on label encoding
            risk_level = risk_labels[risk_prediction]
            risk_score = float(max(risk_probabilities))
            
            # Identify key risk factors
            risk_factors = self._identify_risk_factors(risk_features)
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'factors': risk_factors,
                'analysis': f"Investment shows {risk_level} risk with {risk_score*100:.1f}% confidence"
            }
            
        except Exception as e:
            return {
                'risk_level': 'Medium',
                'risk_score': 0.5,
                'factors': ['Analysis error'],
                'analysis': f"Error in risk assessment: {str(e)}"
            }
    
    def get_stock_data(self, symbol: str, period: str = "1mo") -> pd.DataFrame:
        """Get stock data with caching"""
        try:
            cache_key = f"{symbol}_{period}"
            current_time = datetime.now()
            
            # Check cache (refresh every 15 minutes)
            if (cache_key in self.market_data_cache and 
                self.last_update and 
                (current_time - self.last_update).seconds < 900):
                return self.market_data_cache[cache_key]
            
            # Fetch new data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if not data.empty:
                self.market_data_cache[cache_key] = data
                self.last_update = current_time
                return data
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> List[float]:
        """Calculate technical indicators for price prediction"""
        try:
            if len(data) < 20:
                return [0.0] * 8  # Return zeros if insufficient data
            
            # Calculate indicators
            latest = data.iloc[-1]
            
            # Price-based indicators
            ma_5 = data['Close'].tail(5).mean()
            ma_20 = data['Close'].tail(20).mean()
            
            # Volatility
            volatility = data['Close'].pct_change().std() * 100
            
            # Volume
            avg_volume = data['Volume'].tail(20).mean()
            volume_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1.0
            
            # Price position
            price_change = (latest['Close'] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100
            
            return [
                float(latest['Open']),
                float(latest['High']),
                float(latest['Low']),
                float(volume_ratio),
                float(ma_5),
                float(ma_20),
                float(volatility),
                float(price_change)
            ]
            
        except Exception:
            return [0.0] * 8
    
    def _calculate_risk_factors(self, data: pd.DataFrame) -> List[float]:
        """Calculate risk factors for risk assessment"""
        try:
            if len(data) < 20:
                return [0.5] * 6  # Return neutral values if insufficient data
            
            # Volatility (higher = more risky)
            volatility = data['Close'].pct_change().std() * 100
            normalized_volatility = min(volatility / 5.0, 1.0)  # Normalize to 0-1
            
            # Price trend (declining = more risky)
            ma_5 = data['Close'].tail(5).mean()
            ma_20 = data['Close'].tail(20).mean()
            trend_factor = 0.5 + (ma_5 - ma_20) / ma_20 * 2  # Normalized trend
            trend_factor = max(0, min(1, trend_factor))
            
            # Volume consistency (inconsistent = more risky)
            volume_cv = data['Volume'].std() / data['Volume'].mean()
            volume_factor = min(volume_cv / 2.0, 1.0)
            
            # Price range factor
            price_range = (data['High'].max() - data['Low'].min()) / data['Close'].mean()
            range_factor = min(price_range / 0.5, 1.0)
            
            return [
                float(normalized_volatility),
                float(1 - trend_factor),  # Inverse for risk
                float(volume_factor),
                float(range_factor),
                float(np.random.random()),  # Placeholder for beta
                float(np.random.random())   # Placeholder for debt ratio
            ]
            
        except Exception:
            return [0.5] * 6
    
    def _identify_risk_factors(self, risk_features: List[float]) -> List[str]:
        """Identify key risk factors based on feature values"""
        factors = []
        
        if risk_features[0] > 0.7:  # High volatility
            factors.append("High price volatility")
        
        if risk_features[1] > 0.6:  # Negative trend
            factors.append("Declining price trend")
        
        if risk_features[2] > 0.6:  # Volume inconsistency
            factors.append("Inconsistent trading volume")
        
        if risk_features[3] > 0.7:  # Wide price range
            factors.append("Wide price range")
        
        if not factors:
            factors.append("Standard market risks")
        
        return factors

class FinancialDatabase:
    """SQLite database for storing conversations and analysis history"""
    
    def __init__(self, db_path: str = "financial_assistant.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                analysis_type TEXT,
                confidence REAL,
                metadata TEXT
            )
        ''')
        
        # Stock analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                result TEXT NOT NULL,
                confidence REAL,
                features TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_message: str, bot_response: str, 
                         analysis_type: str = None, confidence: float = None, 
                         metadata: Dict = None):
        """Save conversation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (user_message, bot_response, analysis_type, confidence, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_message, bot_response, analysis_type, confidence, 
              json.dumps(metadata) if metadata else None))
        
        conn.commit()
        conn.close()
    
    def save_stock_analysis(self, symbol: str, analysis_type: str, result: Dict, 
                           confidence: float = None, features: List = None):
        """Save stock analysis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO stock_analysis (symbol, analysis_type, result, confidence, features)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, analysis_type, json.dumps(result), confidence,
              json.dumps(features) if features else None))
        
        conn.commit()
        conn.close()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Tuple]:
        """Get recent conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, user_message, bot_response, analysis_type, confidence
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results

class AdvancedFinancialChatbot:
    """
    Advanced Financial Assistance Chatbot
    Combines multiple ML models for comprehensive financial analysis
    """
    
    def __init__(self):
        self.ml_engine = AdvancedFinancialMLEngine()
        self.database = FinancialDatabase()
        
        # Conversation context
        self.conversation_history = []
        self.user_portfolio = {}
        
        # Financial knowledge
        self.financial_terms = {
            'bull market': 'A market characterized by rising prices and optimistic investor sentiment',
            'bear market': 'A market characterized by falling prices and pessimistic investor sentiment',
            'volatility': 'A measure of price fluctuations in a security or market',
            'diversification': 'Spreading investments across various assets to reduce risk',
            'dividend': 'A payment made by companies to shareholders from profits',
            'pe ratio': 'Price-to-earnings ratio, a valuation metric comparing price to earnings',
            'market cap': 'Total value of a company\'s shares in the stock market',
            'rsi': 'Relative Strength Index, a momentum oscillator measuring speed and change of price movements'
        }
    
    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process user message and generate comprehensive response"""
        try:
            # Clean and normalize input
            user_input = user_input.strip().lower()
            
            # Determine message type and intent
            intent = self._classify_intent(user_input)
            
            # Generate response based on intent
            if intent == 'sentiment_analysis':
                response = self._handle_sentiment_analysis(user_input)
            elif intent == 'stock_analysis':
                response = self._handle_stock_analysis(user_input)
            elif intent == 'risk_assessment':
                response = self._handle_risk_assessment(user_input)
            elif intent == 'portfolio_advice':
                response = self._handle_portfolio_advice(user_input)
            elif intent == 'market_education':
                response = self._handle_market_education(user_input)
            elif intent == 'general_financial':
                response = self._handle_general_financial(user_input)
            else:
                response = self._handle_general_conversation(user_input)
            
            # Add conversation to history
            self.conversation_history.append({
                'user': user_input,
                'bot': response['message'],
                'timestamp': datetime.now(),
                'intent': intent
            })
            
            # Save to database
            self.database.save_conversation(
                user_input, response['message'], 
                intent, response.get('confidence'),
                response.get('analysis_data')
            )
            
            return response
            
        except Exception as e:
            return {
                'message': f"I apologize, but I encountered an error processing your request: {str(e)}",
                'type': 'error',
                'confidence': 0.0
            }
    
    def _classify_intent(self, user_input: str) -> str:
        """Classify user intent based on input"""
        input_lower = user_input.lower()
        
        # Sentiment analysis keywords
        if any(word in input_lower for word in ['sentiment', 'feel', 'opinion', 'mood', 'analyze text']):
            return 'sentiment_analysis'
        
        # Stock analysis keywords
        if any(word in input_lower for word in ['stock', 'share', 'ticker', 'price', 'predict', 'forecast']):
            return 'stock_analysis'
        
        # Risk assessment keywords
        if any(word in input_lower for word in ['risk', 'safe', 'dangerous', 'volatility', 'assess']):
            return 'risk_assessment'
        
        # Portfolio advice keywords
        if any(word in input_lower for word in ['portfolio', 'invest', 'allocation', 'diversify', 'recommend']):
            return 'portfolio_advice'
        
        # Education keywords
        if any(word in input_lower for word in ['what is', 'explain', 'define', 'how does', 'meaning']):
            return 'market_education'
        
        # General financial keywords
        if any(word in input_lower for word in ['market', 'economy', 'financial', 'money', 'trading']):
            return 'general_financial'
        
        return 'general_conversation'
    
    def _handle_sentiment_analysis(self, user_input: str) -> Dict[str, Any]:
        """Handle sentiment analysis requests"""
        # Extract text to analyze (simple approach)
        text_to_analyze = user_input
        if 'analyze' in user_input:
            parts = user_input.split('analyze', 1)
            if len(parts) > 1:
                text_to_analyze = parts[1].strip(' "\':')
        
        # Perform sentiment analysis
        sentiment_result = self.ml_engine.analyze_sentiment(text_to_analyze)
        
        response = f"""📊 **Sentiment Analysis Results:**

**Text Analyzed:** "{text_to_analyze}"

**Primary Sentiment:** {sentiment_result['sentiment'].upper()}
**Confidence:** {sentiment_result['confidence']*100:.1f}%

**Detailed Scores:**
• Positive: {sentiment_result['scores'].get('positive', 0)*100:.1f}%
• Negative: {sentiment_result['scores'].get('negative', 0)*100:.1f}%
• Neutral: {sentiment_result['scores'].get('neutral', 0)*100:.1f}%

**Analysis:** {sentiment_result['analysis']}

💡 **Professional Interpretation:**
{self._interpret_sentiment(sentiment_result)}"""

        return {
            'message': response,
            'type': 'sentiment_analysis',
            'confidence': sentiment_result['confidence'],
            'analysis_data': sentiment_result
        }
    
    def _handle_stock_analysis(self, user_input: str) -> Dict[str, Any]:
        """Handle stock analysis requests"""
        # Extract stock symbol
        stock_symbol = self._extract_stock_symbol(user_input)
        
        if not stock_symbol:
            return {
                'message': "Please specify a stock symbol (e.g., AAPL, MSFT, TSLA) for analysis.",
                'type': 'stock_analysis',
                'confidence': 0.0
            }
        
        # Perform comprehensive stock analysis
        price_prediction = self.ml_engine.predict_price_movement(stock_symbol)
        risk_assessment = self.ml_engine.assess_investment_risk(stock_symbol)
        
        # Get additional stock data
        stock_data = self.ml_engine.get_stock_data(stock_symbol)
        current_price = stock_data['Close'].iloc[-1] if stock_data is not None and not stock_data.empty else "N/A"
        
        # Format price safely
        if current_price == "N/A":
            price_display = "N/A"
        else:
            try:
                price_display = f"${float(current_price):.2f}"
            except (ValueError, TypeError):
                price_display = "N/A"
        
        response = f"""📈 **Comprehensive Stock Analysis for {stock_symbol.upper()}**

**Current Price:** {price_display}

**💹 Price Prediction (ML Model):**
• Direction: {price_prediction['direction'].upper()}
• Confidence: {price_prediction['confidence']*100:.1f}%
• Analysis: {price_prediction['analysis']}

**⚠️ Risk Assessment (ML Model):**
• Risk Level: {risk_assessment['risk_level']}
• Risk Score: {risk_assessment['risk_score']*100:.1f}%
• Key Factors: {', '.join(risk_assessment['factors'])}

**🎯 Professional Recommendation:**
{self._generate_stock_recommendation(price_prediction, risk_assessment)}

**📊 Technical Analysis:**
{self._generate_technical_analysis(stock_data) if stock_data is not None else 'Data unavailable for technical analysis'}

⚠️ **Disclaimer:** This analysis is based on ML models and historical data. Always consult with a financial advisor before making investment decisions."""

        # Save analysis
        self.database.save_stock_analysis(
            stock_symbol, 'comprehensive_analysis',
            {'price_prediction': price_prediction, 'risk_assessment': risk_assessment},
            (price_prediction['confidence'] + risk_assessment['risk_score']) / 2
        )

        return {
            'message': response,
            'type': 'stock_analysis',
            'confidence': price_prediction['confidence'],
            'analysis_data': {
                'symbol': stock_symbol,
                'price_prediction': price_prediction,
                'risk_assessment': risk_assessment
            }
        }
    
    def _handle_risk_assessment(self, user_input: str) -> Dict[str, Any]:
        """Handle risk assessment requests"""
        stock_symbol = self._extract_stock_symbol(user_input)
        
        if stock_symbol:
            # Specific stock risk assessment
            risk_result = self.ml_engine.assess_investment_risk(stock_symbol)
            
            response = f"""⚠️ **Risk Assessment for {stock_symbol.upper()}**

**Risk Level:** {risk_result['risk_level']}
**Confidence:** {risk_result['risk_score']*100:.1f}%

**Risk Factors Identified:**
{chr(10).join(f'• {factor}' for factor in risk_result['factors'])}

**Detailed Analysis:** {risk_result['analysis']}

**Risk Management Recommendations:**
{self._generate_risk_management_advice(risk_result)}"""
            
        else:
            # General risk assessment advice
            response = """⚠️ **General Investment Risk Assessment Guide**

**Risk Categories:**
• **Low Risk:** Government bonds, savings accounts, CDs
• **Medium Risk:** Blue-chip stocks, diversified index funds
• **High Risk:** Individual stocks, cryptocurrencies, options

**Key Risk Factors to Consider:**
• Market volatility and price fluctuations
• Company-specific risks (earnings, management, competition)
• Economic factors (interest rates, inflation, recession)
• Sector-specific risks (technology, healthcare, energy)

**Risk Management Strategies:**
• Diversification across asset classes and sectors
• Dollar-cost averaging for long-term investments
• Setting stop-loss orders to limit downside
• Regular portfolio rebalancing
• Maintaining emergency fund before investing

💡 **Professional Advice:** Never invest more than you can afford to lose, and always consider your risk tolerance and investment timeline."""

        return {
            'message': response,
            'type': 'risk_assessment',
            'confidence': 0.8,
            'analysis_data': risk_result if stock_symbol else None
        }
    
    def _handle_portfolio_advice(self, user_input: str) -> Dict[str, Any]:
        """Handle portfolio advice requests"""
        response = """💼 **Professional Portfolio Management Advice**

**📊 Asset Allocation Strategy:**
• **Conservative (Low Risk):** 60% Bonds, 30% Large-cap stocks, 10% Cash
• **Moderate (Medium Risk):** 40% Bonds, 50% Stocks (mix of large/mid-cap), 10% Alternatives
• **Aggressive (High Risk):** 20% Bonds, 70% Stocks (including small-cap), 10% Growth investments

**🎯 Diversification Principles:**
• **Geographic:** Domestic and international markets
• **Sector:** Technology, healthcare, finance, consumer goods, etc.
• **Asset Class:** Stocks, bonds, REITs, commodities
• **Market Cap:** Large, mid, and small-cap companies

**⏰ Investment Timeline Considerations:**
• **Short-term (< 3 years):** Focus on capital preservation, low-risk investments
• **Medium-term (3-10 years):** Balanced approach with moderate risk
• **Long-term (> 10 years):** Growth-oriented with higher risk tolerance

**🔄 Rebalancing Strategy:**
• Review portfolio quarterly
• Rebalance when allocations drift >5% from target
• Consider tax implications when rebalancing
• Use new contributions to rebalance when possible

**💡 Professional Tips:**
• Start with index funds for broad market exposure
• Keep expense ratios low (< 0.5% annually)
• Maximize tax-advantaged accounts (401k, IRA)
• Don't try to time the market
• Stay disciplined during market volatility

**🚨 Risk Management:**
• Never put all eggs in one basket
• Maintain 3-6 months emergency fund
• Consider your age in bond allocation (age = % in bonds)
• Regular portfolio review and adjustment"""

        return {
            'message': response,
            'type': 'portfolio_advice',
            'confidence': 0.9
        }
    
    def _handle_market_education(self, user_input: str) -> Dict[str, Any]:
        """Handle market education requests with detailed Q&A format"""
        
        # Determine which educational topic to address
        if any(word in user_input for word in ['project', 'investment choice', 'risk averse', 'compare projects']):
            response = self._get_investment_comparison_lesson()
        elif any(word in user_input for word in ['compound', 'simple', 'interest', 'ci', 'si']):
            response = self._get_interest_calculation_lesson()
        elif any(word in user_input for word in ['primary market', 'secondary market', 'ipo']):
            response = self._get_market_types_lesson()
        elif any(word in user_input for word in ['expected return', 'dividend', 'stock return']):
            response = self._get_stock_return_lesson()
        elif any(word in user_input for word in ['mutual fund', 'future value', 'compounding']):
            response = self._get_mutual_fund_lesson()
        else:
            # Look for specific terms to explain
            for term, definition in self.financial_terms.items():
                if term in user_input.lower():
                    response = f"""📚 **Financial Education: {term.title()}**

**Definition:** {definition}

**Key Points:**
{self._get_detailed_explanation(term)}

**Practical Application:**
{self._get_practical_example(term)}

**Related Concepts:**
{self._get_related_concepts(term)}"""
                    
                    return {
                        'message': response,
                        'type': 'market_education',
                        'confidence': 0.95
                    }
            
            # Default comprehensive education
            response = self._get_comprehensive_finance_lessons()

        return {
            'message': response,
            'type': 'market_education',
            'confidence': 0.95
        }
    
    def _handle_general_financial(self, user_input: str) -> Dict[str, Any]:
        """Handle general financial questions"""
        
        # Check for specific funding/financing questions
        if any(word in user_input.lower() for word in ['funding', 'loan', 'equity', 'debt', 'financing', 'bank loan']):
            funding_response = self._get_funding_options_lesson()
            return {
                'message': funding_response,
                'type': 'general_financial',
                'confidence': 0.95
            }
        elif any(word in user_input.lower() for word in ['retain control', 'ownership', 'dilution']):
            funding_response = self._get_funding_options_lesson()
            return {
                'message': funding_response,
                'type': 'general_financial', 
                'confidence': 0.95
            }
        
        response = """💰 **General Financial Guidance**

**Investment Fundamentals:**
• Start investing early to benefit from compound growth
• Understand your risk tolerance and investment goals
• Create a diversified portfolio across asset classes
• Regular investing (dollar-cost averaging) reduces timing risk

**Financial Planning Basics:**
• Emergency fund: 3-6 months of expenses
• Debt management: Pay off high-interest debt first
• Tax-advantaged investing: 401(k), IRA contributions
• Insurance: Protect against catastrophic losses

**Market Timing Reality:**
• Time in market > Timing the market
• Markets are efficient, making consistent outperformance difficult
• Focus on long-term trends rather than daily fluctuations
• Emotional decisions often lead to poor investment outcomes

**Professional Development:**
• Continuously educate yourself about markets and economics
• Stay informed about global economic trends
• Understand the businesses you invest in
• Develop a consistent investment methodology

**Current Market Considerations:**
• Interest rate environment affects bond and stock valuations
• Inflation impacts real returns on investments
• Geopolitical events can create market volatility
• Technology disruption changes industry dynamics

**Action Steps:**
1. Define your investment objectives and timeline
2. Assess your current financial situation
3. Create an appropriate asset allocation strategy
4. Choose low-cost, diversified investment vehicles
5. Implement systematic investing approach
6. Monitor and rebalance periodically"""

        return {
            'message': response,
            'type': 'general_financial',
            'confidence': 0.85
        }
    
    def _handle_general_conversation(self, user_input: str) -> Dict[str, Any]:
        """Handle general conversation"""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        
        if any(greeting in user_input.lower() for greeting in greetings):
            response = """👋 **Welcome to Advanced Financial Assistant!**

I'm your AI-powered financial advisor with advanced ML capabilities. I can help you with:

🔍 **Analysis Services:**
• Sentiment analysis of financial news and texts
• Stock price prediction using ML models
• Investment risk assessment
• Portfolio optimization advice

📊 **Market Intelligence:**
• Technical analysis and chart patterns
• Fundamental analysis guidance
• Economic indicator interpretation
• Market trend analysis

🎓 **Financial Education:**
• Investment concepts and terminology
• Market dynamics explanation
• Trading strategies and techniques
• Personal finance management

💼 **Professional Advice:**
• Asset allocation strategies
• Risk management techniques
• Long-term investment planning
• Retirement planning guidance

**How can I assist you today?** You can ask me about specific stocks, request market analysis, or get general financial advice!"""
        else:
            response = """🤖 **Advanced Financial Assistant**

I'm here to provide professional financial analysis and advice using advanced ML models. 

**You can ask me about:**
• Stock analysis and price predictions
• Investment risk assessment
• Portfolio management strategies
• Financial market education
• Economic trends and indicators

**Example questions:**
• "Analyze the sentiment of this financial news..."
• "What's your prediction for AAPL stock?"
• "Assess the risk of investing in TSLA"
• "What's a good portfolio allocation strategy?"
• "Explain what P/E ratio means"

Please let me know how I can help with your financial questions!"""

        return {
            'message': response,
            'type': 'general_conversation',
            'confidence': 0.8
        }
    
    def _extract_stock_symbol(self, text: str) -> str:
        """Extract stock symbol from text"""
        # Look for common stock symbol patterns
        import re
        
        # Pattern for stock symbols (2-5 uppercase letters)
        pattern = r'\b[A-Z]{2,5}\b'
        matches = re.findall(pattern, text.upper())
        
        if matches:
            return matches[0]
        
        # Common stock names to symbols mapping
        name_to_symbol = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'tesla': 'TSLA',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'facebook': 'META',
            'nvidia': 'NVDA',
            'netflix': 'NFLX'
        }
        
        for name, symbol in name_to_symbol.items():
            if name in text.lower():
                return symbol
        
        return None
    
    def _interpret_sentiment(self, sentiment_result: Dict) -> str:
        """Provide professional interpretation of sentiment analysis"""
        sentiment = sentiment_result['sentiment']
        confidence = sentiment_result['confidence']
        
        if sentiment == 'positive' and confidence > 0.8:
            return "Strong positive sentiment indicates bullish market outlook. Consider this favorable for investment decisions."
        elif sentiment == 'positive':
            return "Moderately positive sentiment suggests cautious optimism. Good for balanced investment approach."
        elif sentiment == 'negative' and confidence > 0.8:
            return "Strong negative sentiment indicates bearish market outlook. Consider defensive strategies or wait for better opportunities."
        elif sentiment == 'negative':
            return "Moderately negative sentiment suggests caution. Monitor closely before making investment decisions."
        else:
            return "Neutral sentiment indicates balanced market view. Good time for fundamental analysis-based decisions."
    
    def _generate_stock_recommendation(self, price_prediction: Dict, risk_assessment: Dict) -> str:
        """Generate professional stock recommendation"""
        direction = price_prediction['direction']
        risk_level = risk_assessment['risk_level']
        
        if direction == 'bullish' and risk_level == 'Low':
            return "🟢 **BUY RECOMMENDATION** - Positive outlook with manageable risk profile"
        elif direction == 'bullish' and risk_level == 'Medium':
            return "🟡 **MODERATE BUY** - Positive outlook but monitor risk factors closely"
        elif direction == 'bullish' and risk_level == 'High':
            return "🟠 **SPECULATIVE BUY** - Positive outlook but high risk - suitable only for risk-tolerant investors"
        elif direction == 'neutral':
            return "⚪ **HOLD/NEUTRAL** - No strong directional bias - good for long-term holders"
        elif direction == 'bearish' and risk_level == 'Low':
            return "🟡 **HOLD/CAUTIOUS** - Negative outlook but low risk - monitor closely"
        else:
            return "🔴 **AVOID/SELL** - Negative outlook with elevated risk factors"
    
    def _generate_technical_analysis(self, stock_data: pd.DataFrame) -> str:
        """Generate technical analysis summary"""
        if stock_data is None or stock_data.empty:
            return "Technical analysis unavailable - insufficient data"
        
        try:
            latest_price = stock_data['Close'].iloc[-1]
            ma_5 = stock_data['Close'].tail(5).mean()
            ma_20 = stock_data['Close'].tail(20).mean()
            
            analysis = []
            
            # Price vs moving averages
            if latest_price > ma_5 > ma_20:
                analysis.append("• Price above both 5-day and 20-day MA (Bullish)")
            elif latest_price < ma_5 < ma_20:
                analysis.append("• Price below both moving averages (Bearish)")
            else:
                analysis.append("• Mixed signals from moving averages (Neutral)")
            
            # Volatility analysis
            volatility = stock_data['Close'].pct_change().std() * 100
            if volatility > 3:
                analysis.append(f"• High volatility ({volatility:.1f}%) - Increased risk")
            elif volatility < 1:
                analysis.append(f"• Low volatility ({volatility:.1f}%) - Stable trading")
            else:
                analysis.append(f"• Moderate volatility ({volatility:.1f}%) - Normal trading")
            
            # Volume analysis
            avg_volume = stock_data['Volume'].tail(10).mean()
            latest_volume = stock_data['Volume'].iloc[-1]
            volume_ratio = latest_volume / avg_volume
            
            if volume_ratio > 1.5:
                analysis.append("• Above-average volume - Strong interest")
            elif volume_ratio < 0.5:
                analysis.append("• Below-average volume - Low interest")
            else:
                analysis.append("• Normal trading volume")
            
            return "\n".join(analysis)
            
        except Exception:
            return "Technical analysis calculation error"
    
    def _generate_risk_management_advice(self, risk_result: Dict) -> str:
        """Generate risk management advice"""
        risk_level = risk_result['risk_level']
        
        if risk_level == 'High':
            return """• Use stop-loss orders to limit downside (5-10% below purchase price)
• Consider position sizing - limit to 2-5% of total portfolio
• Monitor daily for any fundamental changes
• Have exit strategy planned before entering position"""
        elif risk_level == 'Medium':
            return """• Standard position sizing appropriate (5-10% of portfolio)
• Set stop-loss at 10-15% below purchase price
• Review weekly for any significant changes
• Suitable for moderate risk tolerance investors"""
        else:
            return """• Can be core holding (10-20% of portfolio)
• Wide stop-loss acceptable (15-20% below purchase)
• Monthly review sufficient for monitoring
• Appropriate for conservative investors"""
    
    def _get_detailed_explanation(self, term: str) -> str:
        """Get detailed explanation for financial terms"""
        explanations = {
            'bull market': """• Characterized by 20%+ rise from recent lows
• Typically lasts 2-5 years on average
• Driven by economic growth, low unemployment, rising corporate profits
• Investor psychology: Optimism, confidence, risk-taking""",
            
            'bear market': """• Defined as 20%+ decline from recent highs
• Can last 6 months to 2 years
• Caused by recession, high unemployment, geopolitical tensions
• Investor psychology: Fear, pessimism, risk aversion""",
            
            'volatility': """• Measured by standard deviation of price returns
• VIX index tracks S&P 500 volatility expectations
• Higher volatility = higher risk and potential returns
• Can be caused by earnings announcements, economic data, geopolitical events""",
            
            'pe ratio': """• Calculated as Price per Share ÷ Earnings per Share
• Forward P/E uses estimated future earnings
• Industry comparison is crucial for context
• High P/E may indicate growth expectations or overvaluation"""
        }
        
        return explanations.get(term, "• Key characteristics and factors that influence this concept")
    
    def _get_practical_example(self, term: str) -> str:
        """Get practical examples for financial terms"""
        examples = {
            'bull market': "The 2009-2020 bull market saw S&P 500 rise from 666 to 3,393 (409% gain)",
            'bear market': "2007-2009 financial crisis saw S&P 500 fall 57% from peak to trough",
            'volatility': "Tesla (TSLA) has high volatility with daily moves often exceeding 5%",
            'pe ratio': "If a stock trades at $100 with $5 EPS, the P/E ratio is 20x"
        }
        
        return examples.get(term, "Practical applications in real market scenarios")
    
    def _get_related_concepts(self, term: str) -> str:
        """Get related concepts for financial terms"""
        related = {
            'bull market': "Market cycles, Economic indicators, Sector rotation, Growth investing",
            'bear market': "Market correction, Recession, Defensive stocks, Value investing",
            'volatility': "Beta, Standard deviation, VIX index, Risk management",
            'pe ratio': "P/B ratio, EV/EBITDA, PEG ratio, Valuation metrics"
        }
        
        return related.get(term, "Related financial concepts and metrics")
    
    def _get_investment_comparison_lesson(self) -> str:
        """Corporate Finance Q&A with detailed explanation"""
        return """📊 **Question 1 (Corporate Finance):**

**Scenario:** A company has two investment options:
• **Project A:** Expected return = 12%, Risk (standard deviation) = 8%
• **Project B:** Expected return = 9%, Risk (standard deviation) = 4%

**Question:** If the company is risk-averse, which project should it choose and why?

**Answer:**

Since the company is risk-averse, it will prioritize lower risk over higher return.

**Project A** offers a higher return (12%) but comes with higher risk (8%).
**Project B** offers a slightly lower return (9%) but with much lower risk (4%).

➡️ **Therefore, the company should choose Project B** because the lower risk aligns better with a risk-averse strategy, even if it means accepting a slightly lower return.

**Conclusion:** A risk-averse company should select **Project B (9% return, 4% risk)** as it provides safer and more stable returns.

**🎯 Key Learning Points:**
• Risk-averse investors prefer certainty over potentially higher but uncertain returns
• Risk-return trade-off is fundamental in finance
• Standard deviation measures investment volatility/uncertainty
• Conservative strategies focus on capital preservation

**📚 Additional Context:**
Risk-adjusted returns can be measured using Sharpe ratio: (Return - Risk-free rate) / Standard deviation"""
    
    def _get_interest_calculation_lesson(self) -> str:
        """Interest calculation Q&A with examples"""
        return """💰 **Question 4 (Banking & Investment):**

**Question:** What is the difference between Simple Interest (SI) and Compound Interest (CI)?

**Answer:**

**Simple Interest (SI)** is calculated only on the original principal:
📐 **Formula:** SI = (P × R × T) / 100

**Compound Interest (CI)** is calculated on the principal plus accumulated interest:
📐 **Formula:** CI = P(1 + r/n)^(nt) - P

➡️ **CI always gives higher returns than SI** (for more than one compounding period).

**💡 Example:** For ₹10,000 at 10% for 2 years →
• **SI = ₹2,000**
• **CI = ₹2,100**

**Detailed Calculation:**
**Simple Interest:**
SI = (10,000 × 10 × 2) / 100 = ₹2,000

**Compound Interest:**
Year 1: ₹10,000 + ₹1,000 = ₹11,000
Year 2: ₹11,000 + ₹1,100 = ₹12,100
CI = ₹12,100 - ₹10,000 = ₹2,100

**🎯 Key Learning Points:**
• Compound interest creates "interest on interest"
• The longer the time period, the greater the difference
• Frequent compounding (daily vs annually) increases returns
• Einstein called compound interest "the 8th wonder of the world" """
    
    def _get_stock_return_lesson(self) -> str:
        """Stock return calculation Q&A"""
        return """📈 **Question 5 (Stock Market):**

**Scenario:** A stock is priced at ₹1,000 today. The expected dividend next year is ₹50, and the stock price is expected to rise to ₹1,080.

**Question:** What is the expected return?

**Answer:**

**Expected Return Formula:**
Expected Return = (Dividend + Price Gain) / Current Price

**Calculation:**
= [50 + (1080 - 1000)] / 1000
= [50 + 80] / 1000
= 130 / 1000 = 0.13

➡️ **The stock's expected return is 13%**

**💡 Breakdown:**
• **Dividend Yield:** ₹50/₹1,000 = 5%
• **Capital Gain:** ₹80/₹1,000 = 8%
• **Total Return:** 5% + 8% = 13%

**🎯 Key Learning Points:**
• Total return = Dividend yield + Capital appreciation
• Both income and growth contribute to investment returns
• Expected returns are forward-looking estimates
• Actual returns may differ from expectations due to market volatility

**📊 Professional Analysis:**
A 13% expected return is attractive, but consider:
• Is this return realistic given market conditions?
• What's the risk associated with this stock?
• How does it compare to market averages?"""
    
    def _get_mutual_fund_lesson(self) -> str:
        """Mutual fund calculation Q&A"""
        return """📊 **Question 2 (Personal Finance):**

**Scenario:** You invest ₹50,000 in a mutual fund that grows at an average annual rate of 10%.

**Question:** How much will your investment be worth after 5 years (assuming annual compounding)?

**Answer:**

**Future Value Formula:**
FV = P(1 + r)^n

**Where:**
• P = Principal = ₹50,000
• r = Rate = 10% = 0.10
• n = Time = 5 years

**Calculation:**
= 50,000 × (1 + 0.10)^5
= 50,000 × (1.10)^5
= 50,000 × 1.61051
= ₹80,525.5

➡️ **The investment will grow to approximately ₹80,526 in 5 years.**

**📊 Year-by-Year Breakdown:**
• Year 1: ₹50,000 × 1.10 = ₹55,000
• Year 2: ₹55,000 × 1.10 = ₹60,500
• Year 3: ₹60,500 × 1.10 = ₹66,550
• Year 4: ₹66,550 × 1.10 = ₹73,205
• Year 5: ₹73,205 × 1.10 = ₹80,526

**🎯 Key Learning Points:**
• Compound growth accelerates over time
• Small rate differences compound significantly
• Time is the most powerful factor in wealth building
• Consistent investing amplifies compound effects"""

    def _get_market_types_lesson(self) -> str:
        """Market types Q&A"""
        return """🏪 **Question 3 (Financial Markets):**

**Question:** Explain the difference between Primary Market and Secondary Market with examples.

**Answer:**

**Primary Market:**
• Where companies issue **NEW securities** (shares/bonds) for the first time
• Companies raise capital directly from investors
• **Example:** IPO (Initial Public Offering) of Zomato in India

**Secondary Market:**
• Where **EXISTING securities** are traded among investors
• No new capital goes to the company
• **Example:** Buying/selling Zomato shares on NSE/BSE after IPO

➡️ **Key Difference:** Primary = Fund raising for company; Secondary = Trading between investors

**🔍 Detailed Comparison:**

**Primary Market Features:**
• Company receives proceeds from sale
• Investment banks help with underwriting
• Fixed price determined by company/underwriters
• Examples: IPOs, Rights issues, Private placements

**Secondary Market Features:**
• Investors trade with each other
• Stock exchanges facilitate trading
• Market-determined prices (supply & demand)
• Examples: NSE, BSE, NASDAQ, NYSE

**🎯 Key Learning Points:**
• Primary markets create securities, secondary markets trade them
• Both markets are essential for capital formation
• Secondary market liquidity encourages primary market participation
• Price discovery happens in secondary markets"""
    
    def _get_comprehensive_finance_lessons(self) -> str:
        """Comprehensive finance education"""
        return """📚 **Complete Financial Education - 5 Essential Questions & Answers**

**Q1. Corporate Finance - Risk vs Return:**
A company choosing between Project A (12% return, 8% risk) vs Project B (9% return, 4% risk).
➡️ **Answer:** Risk-averse companies choose Project B for stability.

**Q2. Personal Finance - Compound Growth:**
₹50,000 invested at 10% for 5 years = ₹80,526
➡️ **Answer:** Time and compounding create wealth exponentially.

**Q3. Financial Markets - Primary vs Secondary:**
Primary = IPOs (new securities), Secondary = Stock exchanges (existing securities)
➡️ **Answer:** Primary raises capital, Secondary provides liquidity.

**Q4. Banking - Simple vs Compound Interest:**
₹10,000 at 10% for 2 years: SI = ₹2,000, CI = ₹2,100
➡️ **Answer:** Compound interest beats simple interest over time.

**Q5. Stock Markets - Expected Returns:**
Stock at ₹1,000, dividend ₹50, target ₹1,080 = 13% expected return
➡️ **Answer:** Total return = Dividend yield + Capital appreciation.

**🎯 Universal Financial Principles:**
• Risk and return are positively correlated
• Time is the most powerful wealth-building tool
• Diversification reduces portfolio risk
• Markets are generally efficient over long periods
• Education and discipline beat market timing

**💡 Next Steps:**
Ready for more advanced topics? Ask about portfolio theory, options, derivatives, or specific investment strategies!

**🔍 Try These Sample Questions:**
• "Compare two investment projects"
• "Calculate compound interest"
• "Explain primary vs secondary market"
• "Calculate stock returns"
• "Show mutual fund growth"

**👉 Do you want me to create more questions with detailed answers? I can cover advanced topics like portfolio optimization, risk management, and derivatives!**"""
    
    def _get_funding_options_lesson(self) -> str:
        """Corporate funding options Q&A"""
        return """🏦 **Question 6 (Corporate Finance - Funding Options):**

**Scenario:** A company is considering two funding options:
• **Bank Loan at 8% interest rate**
• **Issuing new Equity shares**

**Question:** Which option should the company choose if it wants to retain control, and why?

**Answer:**

When a company wants to **retain control**, it should prioritize maintaining ownership and decision-making power.

**Bank Loan Analysis:**
• ✅ **Retains 100% ownership** - No dilution of equity
• ✅ **Maintains full control** - No new shareholders with voting rights
• ❌ **Fixed interest obligation** - Must pay 8% regardless of profits
• ❌ **Credit risk** - Requires collateral and creditworthiness

**Equity Shares Analysis:**
• ❌ **Dilutes ownership** - Reduces current shareholders' percentage
• ❌ **Shares control** - New shareholders get voting rights
• ✅ **No fixed payments** - Dividends paid only when profitable
• ✅ **Risk sharing** - Investors share business risks

➡️ **Therefore, the company should choose the Bank Loan** if retaining control is the primary objective.

**Conclusion:** For control retention, **Bank Loan (8% interest)** is the better choice as it preserves 100% ownership and decision-making authority.

**🎯 Key Learning Points:**
• Debt financing preserves ownership control
• Equity financing dilutes ownership but shares risk
• Cost of capital vs. control is a critical trade-off
• Different financing needs require different optimal structures

**📊 Professional Analysis:**
• **Control Priority:** Choose debt financing
• **Growth Priority:** Consider equity for expansion capital
• **Risk Management:** Balance debt capacity with growth needs
• **Long-term Strategy:** Plan optimal capital structure for sustainable growth

**🔍 Additional Factors to Consider:**
• Company's debt capacity and credit rating
• Market conditions for both debt and equity
• Tax implications (interest is tax-deductible)
• Future financing flexibility and growth plans"""


class FinancialDesktopApp:
    """
    Main Desktop Application Class
    Creates GUI interface for the Advanced Financial Chatbot
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏦 Advanced Financial Assistant - AI-Powered Desktop App")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize chatbot
        self.chatbot = AdvancedFinancialChatbot()
        
        # Initialize GUI components
        self.setup_gui()
        
        # Welcome message
        self.add_system_message("🚀 Welcome to Advanced Financial Assistant!")
        self.add_system_message("AI-powered financial analysis with multiple ML models at your service.")
        self.add_system_message("Ask me about stocks, risk assessment, portfolio advice, or financial education!")
    
    def setup_gui(self):
        """Setup the GUI components"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(title_frame, 
                               text="🏦 Advanced Financial Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="AI-Powered Financial Analysis & Advisory", 
                                  font=('Arial', 10))
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Left panel - Controls
        left_panel = ttk.LabelFrame(main_frame, text="🎛️ Controls & Features", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Analysis buttons
        ttk.Label(left_panel, text="📊 Quick Analysis:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.stock_entry = ttk.Entry(left_panel, width=15, font=('Arial', 10))
        self.stock_entry.pack(fill=tk.X, pady=(0, 5))
        self.stock_entry.insert(0, "Enter stock symbol...")
        self.stock_entry.bind('<FocusIn>', self.clear_placeholder)
        
        ttk.Button(left_panel, text="📈 Analyze Stock", 
                  command=self.analyze_stock).pack(fill=tk.X, pady=2)
        
        ttk.Button(left_panel, text="⚠️ Risk Assessment", 
                  command=self.assess_risk).pack(fill=tk.X, pady=2)
        
        ttk.Button(left_panel, text="💼 Portfolio Advice", 
                  command=self.get_portfolio_advice).pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Education section
        ttk.Label(left_panel, text="📚 Financial Education:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        education_topics = [
            ("📊 Market Basics", "explain market basics"),
            ("💹 Investment Types", "explain investment types"),
            ("⚖️ Risk Management", "explain risk management"),
            ("📈 Technical Analysis", "explain technical analysis")
        ]
        
        for topic_name, topic_query in education_topics:
            ttk.Button(left_panel, text=topic_name, 
                      command=lambda q=topic_query: self.send_message(q)).pack(fill=tk.X, pady=1)
        
        # Separator
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Utilities
        ttk.Label(left_panel, text="🔧 Utilities:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Button(left_panel, text="💾 Export Chat", 
                  command=self.export_chat).pack(fill=tk.X, pady=2)
        
        ttk.Button(left_panel, text="🗑️ Clear Chat", 
                  command=self.clear_chat).pack(fill=tk.X, pady=2)
        
        ttk.Button(left_panel, text="📊 View Analytics", 
                  command=self.show_analytics).pack(fill=tk.X, pady=2)
        
        # Right panel - Chat area
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            right_panel, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            font=('Consolas', 10),
            bg='#ffffff',
            fg='#333333'
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(right_panel)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        # Message input
        self.message_entry = ttk.Entry(input_frame, font=('Arial', 11))
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_user_message())
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="💬 Send", 
                                     command=self.send_user_message)
        self.send_button.grid(row=0, column=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Ready - Advanced Financial Assistant loaded with ML models")
        status_bar = ttk.Label(right_panel, textvariable=self.status_var, 
                              font=('Arial', 9), foreground='green')
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E))
    
    def clear_placeholder(self, event):
        """Clear placeholder text"""
        if self.stock_entry.get() == "Enter stock symbol...":
            self.stock_entry.delete(0, tk.END)
    
    def add_message(self, sender: str, message: str, message_type: str = "normal"):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Choose colors based on sender and type
        if sender == "System":
            color = "#0066cc"
            prefix = "🤖 SYSTEM"
        elif sender == "You":
            color = "#006600"
            prefix = "👤 YOU"
        else:
            color = "#cc6600"
            prefix = "🏦 ASSISTANT"
        
        # Insert message
        self.chat_display.insert(tk.END, f"\n[{timestamp}] {prefix}:\n", f"{sender.lower()}_time")
        self.chat_display.insert(tk.END, f"{message}\n", f"{sender.lower()}_msg")
        
        # Configure tags for styling
        self.chat_display.tag_config(f"{sender.lower()}_time", foreground="gray", font=('Arial', 8))
        self.chat_display.tag_config(f"{sender.lower()}_msg", foreground=color, font=('Consolas', 10))
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
    
    def add_system_message(self, message: str):
        """Add system message"""
        self.add_message("System", message)
    
    def send_user_message(self):
        """Send user message to chatbot"""
        user_input = self.message_entry.get().strip()
        if not user_input:
            return
        
        # Clear input
        self.message_entry.delete(0, tk.END)
        
        # Add user message to display
        self.add_message("You", user_input)
        
        # Process in background thread
        self.status_var.set("🔄 Processing with ML models...")
        self.send_button.config(state='disabled')
        
        def process_message():
            try:
                response = self.chatbot.process_message(user_input)
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.handle_response(response))
                
            except Exception as e:
                error_msg = f"Error processing message: {str(e)}"
                self.root.after(0, lambda: self.handle_error(error_msg))
        
        # Start background thread
        threading.Thread(target=process_message, daemon=True).start()
    
    def send_message(self, message: str):
        """Send predefined message"""
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, message)
        self.send_user_message()
    
    def handle_response(self, response: Dict[str, Any]):
        """Handle chatbot response"""
        self.add_message("Assistant", response['message'])
        
        # Update status
        confidence = response.get('confidence', 0.0)
        analysis_type = response.get('type', 'general')
        
        self.status_var.set(f"✅ {analysis_type.replace('_', ' ').title()} - Confidence: {confidence*100:.1f}%")
        self.send_button.config(state='normal')
        
        # Focus back to input
        self.message_entry.focus()
    
    def handle_error(self, error_message: str):
        """Handle error"""
        self.add_message("System", f"❌ {error_message}")
        self.status_var.set("❌ Error occurred")
        self.send_button.config(state='normal')
        self.message_entry.focus()
    
    def analyze_stock(self):
        """Analyze stock from entry field"""
        symbol = self.stock_entry.get().strip()
        if symbol and symbol != "Enter stock symbol...":
            self.send_message(f"analyze stock {symbol}")
        else:
            messagebox.showwarning("Input Required", "Please enter a stock symbol first.")
    
    def assess_risk(self):
        """Assess risk for stock"""
        symbol = self.stock_entry.get().strip()
        if symbol and symbol != "Enter stock symbol...":
            self.send_message(f"assess risk for {symbol}")
        else:
            self.send_message("general investment risk assessment")
    
    def get_portfolio_advice(self):
        """Get portfolio advice"""
        self.send_message("portfolio allocation advice")
    
    def export_chat(self):
        """Export chat history"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Chat History"
            )
            
            if file_path:
                chat_content = self.chat_display.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Advanced Financial Assistant - Chat History\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(chat_content)
                
                messagebox.showinfo("Export Successful", f"Chat history exported to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export chat history:\n{str(e)}")
    
    def clear_chat(self):
        """Clear chat display"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_display.delete(1.0, tk.END)
            self.add_system_message("Chat cleared. How can I assist you today?")
    
    def show_analytics(self):
        """Show analytics window"""
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("📊 Analytics Dashboard")
        analytics_window.geometry("600x400")
        
        # Get recent conversations
        recent_conversations = self.chatbot.database.get_recent_conversations(20)
        
        # Create text widget for analytics
        analytics_text = scrolledtext.ScrolledText(analytics_window, wrap=tk.WORD, font=('Consolas', 10))
        analytics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display analytics
        analytics_content = "📊 ANALYTICS DASHBOARD\n"
        analytics_content += "=" * 50 + "\n\n"
        
        analytics_content += f"📈 Total Conversations: {len(recent_conversations)}\n\n"
        
        if recent_conversations:
            analytics_content += "🕒 Recent Activity:\n"
            analytics_content += "-" * 30 + "\n"
            
            for conv in recent_conversations[:10]:
                timestamp, user_msg, bot_response, analysis_type, confidence = conv
                analytics_content += f"[{timestamp}] {analysis_type or 'general'}\n"
                analytics_content += f"Q: {user_msg[:100]}{'...' if len(user_msg) > 100 else ''}\n"
                if confidence:
                    analytics_content += f"Confidence: {confidence*100:.1f}%\n"
                analytics_content += "\n"
        
        analytics_text.insert(1.0, analytics_content)
        analytics_text.config(state='disabled')

def main():
    """Main function to run the application"""
    try:
        # Create root window
        root = tk.Tk()
        
        # Set window icon (if available)
        try:
            root.iconbitmap(default='icon.ico')  # Add icon file if available
        except:
            pass
        
        # Create and run application
        app = FinancialDesktopApp(root)
        
        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Run main loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()
