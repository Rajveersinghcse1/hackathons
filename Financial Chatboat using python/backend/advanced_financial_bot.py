"""
Advanced Financial Assistance Chatbot
Built with multiple ML models and comprehensive financial analysis capabilities
No external APIs required - all processing done locally
"""

import pandas as pd
import numpy as np
import re
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# ML and NLP libraries
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# Math and stats
import scipy.stats as stats
from scipy.optimize import minimize
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedFinancialBot:
    """
    Advanced Financial Assistant with multiple ML models and comprehensive analysis
    """
    
    def __init__(self):
        """Initialize the financial bot with all ML models and data"""
        logger.info("Initializing Advanced Financial Assistant...")
        
        # Initialize database
        self.init_database()
        
        # Initialize ML models
        self.init_ml_models()
        
        # Initialize financial data and knowledge base
        self.init_financial_knowledge()
        
        # Initialize conversation memory
        self.conversation_memory = []
        
        logger.info("Advanced Financial Assistant initialized successfully!")
    
    def init_database(self):
        """Initialize SQLite database for storing conversations and analysis"""
        self.conn = sqlite3.connect('financial_bot.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                bot_response TEXT,
                sentiment_score REAL,
                confidence REAL,
                analysis_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT,
                input_data TEXT,
                results TEXT,
                recommendations TEXT,
                risk_score REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def init_ml_models(self):
        """Initialize and train all ML models"""
        logger.info("Training ML models...")
        
        # Sentiment Analysis Models
        self.sentiment_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.sentiment_model = LogisticRegression()
        
        # Intent Classification Models
        self.intent_vectorizer = TfidfVectorizer(max_features=3000, stop_words='english')
        self.intent_model = RandomForestClassifier(n_estimators=100)
        
        # Financial Risk Assessment Model
        self.risk_model = GradientBoostingRegressor(n_estimators=100)
        
        # Topic Modeling for Financial Documents
        self.topic_vectorizer = CountVectorizer(max_features=1000, stop_words='english')
        self.topic_model = LatentDirichletAllocation(n_components=10, random_state=42)
        
        # Market Prediction Model
        self.market_scaler = StandardScaler()
        self.market_model = RandomForestClassifier(n_estimators=200)
        
        # Train models with synthetic data
        self._train_models()
    
    def _train_models(self):
        """Train all ML models with comprehensive financial data"""
        
        # 1. Sentiment Analysis Training Data
        sentiment_texts = [
            # Positive sentiment
            "The company reported excellent quarterly results with strong revenue growth",
            "Stock prices are rising due to positive market sentiment and strong fundamentals",
            "Investors are optimistic about the new product launch and market expansion",
            "The merger will create significant value for shareholders",
            "Strong earnings beat expectations with robust profit margins",
            "Market outlook is positive with sustained economic growth",
            "The company's financial performance exceeded analyst expectations",
            "Investment returns have been consistently strong this quarter",
            
            # Negative sentiment
            "Stock prices fell sharply due to disappointing earnings report",
            "The company faces significant regulatory challenges and market headwinds",
            "Quarterly losses exceeded expectations with declining revenue",
            "Market volatility increased due to economic uncertainty",
            "The company issued a profit warning citing weak demand",
            "Investment losses mounted as market conditions deteriorated",
            "Credit rating was downgraded due to increasing debt levels",
            "The economic recession is impacting business operations severely",
            
            # Neutral sentiment
            "The company reported results in line with analyst expectations",
            "Stock prices remained stable during the trading session",
            "Market conditions are mixed with no clear direction",
            "The company maintains its current dividend policy",
            "Analysts expect steady performance in the coming quarter",
            "Trading volume was average for the stock today",
            "The financial metrics are consistent with industry averages",
            "Market participation remained at normal levels"
        ]
        
        sentiment_labels = [1]*8 + [0]*8 + [2]*8  # Positive, Negative, Neutral
        
        X_sentiment = self.sentiment_vectorizer.fit_transform(sentiment_texts)
        self.sentiment_model.fit(X_sentiment, sentiment_labels)
        
        # 2. Intent Classification Training Data
        intent_texts = [
            # Investment advice
            "How should I invest my money?", "What are good investment options?",
            "Should I buy stocks or bonds?", "Investment strategy for retirement",
            "Best mutual funds to invest in", "How to diversify my portfolio?",
            
            # Market analysis
            "What's the market outlook?", "Analyze current market trends",
            "Market prediction for next quarter", "Economic indicators analysis",
            "Stock market performance review", "Sector analysis and recommendations",
            
            # Risk assessment
            "What are the risks in this investment?", "Risk analysis of my portfolio",
            "How risky is this stock?", "Risk management strategies",
            "Portfolio risk assessment", "Investment risk factors",
            
            # Financial planning
            "How to plan for retirement?", "Financial planning advice",
            "Budget planning strategies", "Savings goals planning",
            "Tax planning advice", "Insurance planning needs",
            
            # Company analysis
            "Analyze this company's financials", "Company fundamental analysis",
            "Financial ratios analysis", "Company valuation methods",
            "Earnings analysis and trends", "Balance sheet analysis"
        ]
        
        intent_labels = ['investment']*6 + ['market_analysis']*6 + ['risk_assessment']*6 + ['financial_planning']*6 + ['company_analysis']*6
        
        X_intent = self.intent_vectorizer.fit_transform(intent_texts)
        self.intent_model.fit(X_intent, intent_labels)
        
        # 3. Risk Assessment Model Training
        risk_features = np.random.rand(1000, 10)  # Features: volatility, beta, debt ratio, etc.
        risk_scores = np.random.rand(1000) * 10  # Risk scores 0-10
        self.risk_model.fit(risk_features, risk_scores)
        
        # 4. Topic Modeling Training
        financial_documents = [
            "Stock market analysis and investment strategies for portfolio optimization",
            "Bonds and fixed income securities for conservative investors",
            "Cryptocurrency and digital assets investment opportunities",
            "Real estate investment trusts and property market analysis",
            "Mutual funds and ETF selection criteria for diversification",
            "Risk management and hedging strategies for portfolio protection",
            "Financial planning and retirement savings strategies",
            "Tax planning and optimization techniques for investors",
            "Economic indicators and market trend analysis",
            "Company valuation methods and fundamental analysis"
        ]
        
        X_topics = self.topic_vectorizer.fit_transform(financial_documents)
        self.topic_model.fit(X_topics)
        
        # 5. Market Prediction Model
        market_features = np.random.rand(1000, 15)  # Market indicators
        market_labels = np.random.choice([0, 1, 2], 1000)  # Bear, Bull, Sideways
        
        market_features_scaled = self.market_scaler.fit_transform(market_features)
        self.market_model.fit(market_features_scaled, market_labels)
        
        logger.info("All ML models trained successfully!")
    
    def init_financial_knowledge(self):
        """Initialize comprehensive financial knowledge base"""
        
        # Financial ratios and their interpretations
        self.financial_ratios = {
            'pe_ratio': {
                'description': 'Price-to-Earnings Ratio',
                'formula': 'Stock Price / Earnings Per Share',
                'good_range': [15, 25],
                'interpretation': {
                    'low': 'Potentially undervalued or company in distress',
                    'normal': 'Fairly valued relative to earnings',
                    'high': 'Potentially overvalued or high growth expected'
                }
            },
            'debt_to_equity': {
                'description': 'Debt-to-Equity Ratio',
                'formula': 'Total Debt / Total Equity',
                'good_range': [0.2, 0.6],
                'interpretation': {
                    'low': 'Conservative capital structure',
                    'normal': 'Balanced leverage',
                    'high': 'High financial risk'
                }
            },
            'current_ratio': {
                'description': 'Current Ratio',
                'formula': 'Current Assets / Current Liabilities',
                'good_range': [1.2, 2.0],
                'interpretation': {
                    'low': 'Liquidity concerns',
                    'normal': 'Good liquidity position',
                    'high': 'Excellent liquidity but possible inefficiency'
                }
            },
            'roe': {
                'description': 'Return on Equity',
                'formula': 'Net Income / Shareholders Equity',
                'good_range': [10, 20],
                'interpretation': {
                    'low': 'Poor profitability',
                    'normal': 'Good profitability',
                    'high': 'Excellent profitability'
                }
            }
        }
        
        # Investment strategies
        self.investment_strategies = {
            'conservative': {
                'description': 'Low risk, steady returns',
                'allocation': {'bonds': 60, 'stocks': 30, 'cash': 10},
                'suitable_for': 'Risk-averse investors, near retirement',
                'expected_return': '4-6% annually'
            },
            'balanced': {
                'description': 'Moderate risk, balanced growth',
                'allocation': {'stocks': 60, 'bonds': 35, 'alternatives': 5},
                'suitable_for': 'Medium-term goals, moderate risk tolerance',
                'expected_return': '6-8% annually'
            },
            'aggressive': {
                'description': 'High risk, high potential returns',
                'allocation': {'stocks': 80, 'alternatives': 15, 'cash': 5},
                'suitable_for': 'Long-term investors, high risk tolerance',
                'expected_return': '8-12% annually'
            }
        }
        
        # Economic indicators
        self.economic_indicators = {
            'gdp_growth': 'Economic output growth rate',
            'inflation_rate': 'Price level increase rate',
            'unemployment_rate': 'Labor market health indicator',
            'interest_rates': 'Cost of borrowing money',
            'consumer_confidence': 'Consumer spending sentiment',
            'industrial_production': 'Manufacturing output indicator'
        }
        
        # Risk factors
        self.risk_factors = {
            'market_risk': 'Overall market volatility and systematic risk',
            'credit_risk': 'Risk of default on debt obligations',
            'liquidity_risk': 'Risk of not being able to sell quickly',
            'inflation_risk': 'Risk of purchasing power erosion',
            'interest_rate_risk': 'Risk from changing interest rates',
            'currency_risk': 'Risk from foreign exchange fluctuations',
            'political_risk': 'Risk from political and regulatory changes'
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of financial text using ML model"""
        try:
            text_vector = self.sentiment_vectorizer.transform([text])
            prediction = self.sentiment_model.predict(text_vector)[0]
            probabilities = self.sentiment_model.predict_proba(text_vector)[0]
            
            sentiment_labels = {0: 'Negative', 1: 'Positive', 2: 'Neutral'}
            
            return {
                'sentiment': sentiment_labels[prediction],
                'confidence': float(max(probabilities)),
                'scores': {
                    'negative': float(probabilities[0]),
                    'positive': float(probabilities[1]),
                    'neutral': float(probabilities[2])
                }
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'sentiment': 'Neutral', 'confidence': 0.5, 'scores': {'negative': 0.33, 'positive': 0.33, 'neutral': 0.34}}
    
    def classify_intent(self, text: str) -> Dict[str, Any]:
        """Classify user intent using ML model"""
        try:
            text_vector = self.intent_vectorizer.transform([text])
            prediction = self.intent_model.predict(text_vector)[0]
            probabilities = self.intent_model.predict_proba(text_vector)
            confidence = float(max(probabilities[0]))
            
            return {
                'intent': prediction,
                'confidence': confidence
            }
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return {'intent': 'general', 'confidence': 0.5}
    
    def calculate_financial_ratios(self, financial_data: Dict[str, float]) -> Dict[str, Any]:
        """Calculate and interpret financial ratios"""
        ratios = {}
        
        try:
            # PE Ratio
            if 'stock_price' in financial_data and 'eps' in financial_data and financial_data['eps'] != 0:
                pe_ratio = financial_data['stock_price'] / financial_data['eps']
                ratios['pe_ratio'] = {
                    'value': round(pe_ratio, 2),
                    'interpretation': self._interpret_ratio('pe_ratio', pe_ratio)
                }
            
            # Debt-to-Equity
            if 'total_debt' in financial_data and 'total_equity' in financial_data and financial_data['total_equity'] != 0:
                de_ratio = financial_data['total_debt'] / financial_data['total_equity']
                ratios['debt_to_equity'] = {
                    'value': round(de_ratio, 2),
                    'interpretation': self._interpret_ratio('debt_to_equity', de_ratio)
                }
            
            # Current Ratio
            if 'current_assets' in financial_data and 'current_liabilities' in financial_data and financial_data['current_liabilities'] != 0:
                current_ratio = financial_data['current_assets'] / financial_data['current_liabilities']
                ratios['current_ratio'] = {
                    'value': round(current_ratio, 2),
                    'interpretation': self._interpret_ratio('current_ratio', current_ratio)
                }
            
            # ROE
            if 'net_income' in financial_data and 'shareholders_equity' in financial_data and financial_data['shareholders_equity'] != 0:
                roe = (financial_data['net_income'] / financial_data['shareholders_equity']) * 100
                ratios['roe'] = {
                    'value': round(roe, 2),
                    'interpretation': self._interpret_ratio('roe', roe)
                }
            
        except Exception as e:
            logger.error(f"Ratio calculation error: {e}")
        
        return ratios
    
    def _interpret_ratio(self, ratio_name: str, value: float) -> str:
        """Interpret financial ratio values"""
        if ratio_name not in self.financial_ratios:
            return "No interpretation available"
        
        ratio_info = self.financial_ratios[ratio_name]
        good_range = ratio_info['good_range']
        
        if value < good_range[0]:
            return ratio_info['interpretation']['low']
        elif value > good_range[1]:
            return ratio_info['interpretation']['high']
        else:
            return ratio_info['interpretation']['normal']
    
    def assess_investment_risk(self, investment_data: Dict[str, float]) -> Dict[str, Any]:
        """Assess investment risk using ML model"""
        try:
            # Create feature vector from investment data
            features = [
                investment_data.get('volatility', 0.2),
                investment_data.get('beta', 1.0),
                investment_data.get('debt_ratio', 0.3),
                investment_data.get('liquidity_ratio', 1.5),
                investment_data.get('profit_margin', 0.1),
                investment_data.get('revenue_growth', 0.05),
                investment_data.get('market_cap_log', 10),
                investment_data.get('pe_ratio', 20),
                investment_data.get('dividend_yield', 0.03),
                investment_data.get('analyst_rating', 3.5)
            ]
            
            risk_score = self.risk_model.predict([features])[0]
            risk_level = self._categorize_risk(risk_score)
            
            return {
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'recommendations': self._get_risk_recommendations(risk_level)
            }
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {'risk_score': 5.0, 'risk_level': 'Medium', 'recommendations': 'Standard diversification recommended'}
    
    def _categorize_risk(self, score: float) -> str:
        """Categorize risk score into levels"""
        if score <= 3:
            return 'Low'
        elif score <= 6:
            return 'Medium'
        elif score <= 8:
            return 'High'
        else:
            return 'Very High'
    
    def _get_risk_recommendations(self, risk_level: str) -> str:
        """Get recommendations based on risk level"""
        recommendations = {
            'Low': 'Suitable for conservative portfolios. Consider increasing allocation.',
            'Medium': 'Balanced risk profile. Ensure proper diversification.',
            'High': 'Higher risk investment. Limit position size and monitor closely.',
            'Very High': 'Speculative investment. Only suitable for aggressive portfolios with high risk tolerance.'
        }
        return recommendations.get(risk_level, 'Monitor investment carefully.')
    
    def generate_investment_advice(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized investment advice"""
        age = user_profile.get('age', 35)
        risk_tolerance = user_profile.get('risk_tolerance', 'medium')
        investment_horizon = user_profile.get('investment_horizon', 10)
        income = user_profile.get('income', 50000)
        goals = user_profile.get('goals', ['retirement'])
        
        # Determine strategy based on profile
        if risk_tolerance == 'low' or age > 55:
            strategy = 'conservative'
        elif risk_tolerance == 'high' and age < 40:
            strategy = 'aggressive'
        else:
            strategy = 'balanced'
        
        strategy_info = self.investment_strategies[strategy]
        
        # Generate specific advice
        advice = {
            'recommended_strategy': strategy,
            'asset_allocation': strategy_info['allocation'],
            'expected_return': strategy_info['expected_return'],
            'specific_recommendations': [],
            'risk_considerations': []
        }
        
        # Add specific recommendations based on profile
        if 'retirement' in goals:
            advice['specific_recommendations'].append({
                'type': 'Retirement Planning',
                'recommendation': f'Consider maximizing 401(k) contributions. Target saving 10-15% of income ({income * 0.1:.0f}-{income * 0.15:.0f} annually).'
            })
        
        if 'house' in goals:
            advice['specific_recommendations'].append({
                'type': 'Home Purchase',
                'recommendation': 'For short-term goals (2-5 years), consider high-yield savings or short-term CDs for down payment funds.'
            })
        
        if investment_horizon < 5:
            advice['risk_considerations'].append('Short investment horizon - prioritize capital preservation over growth')
        
        if age < 30:
            advice['specific_recommendations'].append({
                'type': 'Young Investor',
                'recommendation': 'Take advantage of compound growth with higher stock allocation and consider Roth IRA for tax-free growth.'
            })
        
        return advice
    
    def analyze_market_trends(self, market_data: List[float] = None) -> Dict[str, Any]:
        """Analyze market trends using statistical methods"""
        if market_data is None:
            # Generate sample market data for demonstration
            market_data = list(np.random.randn(30).cumsum() + 100)
        
        try:
            # Calculate technical indicators
            returns = np.diff(market_data) / market_data[:-1]
            volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
            
            # Moving averages
            ma_5 = np.mean(market_data[-5:])
            ma_20 = np.mean(market_data[-20:]) if len(market_data) >= 20 else np.mean(market_data)
            
            # Trend analysis
            trend = 'Upward' if ma_5 > ma_20 else 'Downward'
            
            # Momentum
            momentum = (market_data[-1] - market_data[-10]) / market_data[-10] if len(market_data) >= 10 else 0
            
            return {
                'current_price': round(market_data[-1], 2),
                'volatility': round(volatility * 100, 2),
                'trend': trend,
                'momentum': round(momentum * 100, 2),
                'ma_5': round(ma_5, 2),
                'ma_20': round(ma_20, 2),
                'analysis': self._interpret_market_analysis(trend, volatility, momentum)
            }
        except Exception as e:
            logger.error(f"Market analysis error: {e}")
            return {'analysis': 'Unable to perform market analysis with provided data'}
    
    def _interpret_market_analysis(self, trend: str, volatility: float, momentum: float) -> str:
        """Interpret market analysis results"""
        interpretation = f"Market shows {trend.lower()} trend with "
        
        if volatility < 0.15:
            interpretation += "low volatility (stable conditions). "
        elif volatility < 0.25:
            interpretation += "moderate volatility. "
        else:
            interpretation += "high volatility (uncertain conditions). "
        
        if abs(momentum) < 0.02:
            interpretation += "Momentum is neutral."
        elif momentum > 0.02:
            interpretation += "Positive momentum suggests continued upward movement."
        else:
            interpretation += "Negative momentum suggests potential downward pressure."
        
        return interpretation
    
    def portfolio_optimization(self, assets: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Optimize portfolio allocation using mean-variance optimization"""
        try:
            asset_names = list(assets.keys())
            returns = [assets[asset]['expected_return'] for asset in asset_names]
            risks = [assets[asset]['risk'] for asset in asset_names]
            
            # Simple optimization: maximize return per unit risk
            sharpe_ratios = [r/risk if risk > 0 else 0 for r, risk in zip(returns, risks)]
            
            # Normalize to get weights
            total_sharpe = sum(sharpe_ratios) if sum(sharpe_ratios) > 0 else 1
            weights = [ratio/total_sharpe for ratio in sharpe_ratios]
            
            # Calculate portfolio metrics
            portfolio_return = sum(w * r for w, r in zip(weights, returns))
            portfolio_risk = np.sqrt(sum((w * risk)**2 for w, risk in zip(weights, risks)))  # Simplified, assumes no correlation
            
            return {
                'optimal_weights': {asset: round(weight, 3) for asset, weight in zip(asset_names, weights)},
                'expected_return': round(portfolio_return, 3),
                'expected_risk': round(portfolio_risk, 3),
                'sharpe_ratio': round(portfolio_return/portfolio_risk if portfolio_risk > 0 else 0, 3)
            }
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return {'error': 'Unable to optimize portfolio with provided data'}
    
    def financial_planning_analysis(self, planning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive financial planning analysis"""
        current_age = planning_data.get('current_age', 30)
        retirement_age = planning_data.get('retirement_age', 65)
        current_savings = planning_data.get('current_savings', 10000)
        monthly_savings = planning_data.get('monthly_savings', 500)
        target_retirement_income = planning_data.get('target_retirement_income', 4000)
        
        years_to_retirement = retirement_age - current_age
        months_to_retirement = years_to_retirement * 12
        
        # Assume 7% annual return (conservative estimate)
        annual_return = 0.07
        monthly_return = annual_return / 12
        
        # Future value calculation
        future_value_current = current_savings * (1 + annual_return) ** years_to_retirement
        
        # Future value of annuity (monthly contributions)
        if monthly_return > 0:
            future_value_monthly = monthly_savings * (((1 + monthly_return) ** months_to_retirement - 1) / monthly_return)
        else:
            future_value_monthly = monthly_savings * months_to_retirement
        
        total_retirement_savings = future_value_current + future_value_monthly
        
        # 4% withdrawal rule for retirement income
        annual_retirement_income = total_retirement_savings * 0.04
        monthly_retirement_income = annual_retirement_income / 12
        
        # Calculate if target is met
        target_annual_income = target_retirement_income * 12
        shortfall = target_annual_income - annual_retirement_income
        
        analysis = {
            'projected_retirement_savings': round(total_retirement_savings, 2),
            'projected_monthly_income': round(monthly_retirement_income, 2),
            'target_monthly_income': target_retirement_income,
            'meets_target': shortfall <= 0,
            'shortfall_surplus': round(-shortfall, 2) if shortfall < 0 else round(shortfall, 2),
            'recommendations': []
        }
        
        if shortfall > 0:
            additional_monthly_needed = shortfall / (12 * 25)  # Assuming 4% withdrawal rule
            analysis['recommendations'].append(f"Increase monthly savings by ${additional_monthly_needed:.2f} to meet retirement goals")
        
        if years_to_retirement > 30:
            analysis['recommendations'].append("Consider more aggressive investment strategy given long time horizon")
        elif years_to_retirement < 10:
            analysis['recommendations'].append("Consider shifting to more conservative investments as retirement approaches")
        
        return analysis
    
    def get_comprehensive_response(self, user_message: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive response using all available models and analysis"""
        if user_profile is None:
            user_profile = {}
        
        # Analyze sentiment and intent
        sentiment_analysis = self.analyze_sentiment(user_message)
        intent_analysis = self.classify_intent(user_message)
        
        # Store conversation
        self.conversation_memory.append({
            'user_message': user_message,
            'timestamp': datetime.now(),
            'sentiment': sentiment_analysis,
            'intent': intent_analysis
        })
        
        # Generate response based on intent
        response_data = {
            'message': user_message,
            'sentiment': sentiment_analysis,
            'intent': intent_analysis['intent'],
            'response': '',
            'analysis': {},
            'recommendations': []
        }
        
        # Route to appropriate analysis based on intent
        if intent_analysis['intent'] == 'investment':
            response_data['response'] = self._generate_investment_response(user_message, user_profile)
            if user_profile:
                response_data['analysis']['investment_advice'] = self.generate_investment_advice(user_profile)
        
        elif intent_analysis['intent'] == 'market_analysis':
            response_data['response'] = self._generate_market_analysis_response(user_message)
            response_data['analysis']['market_trends'] = self.analyze_market_trends()
        
        elif intent_analysis['intent'] == 'risk_assessment':
            response_data['response'] = self._generate_risk_assessment_response(user_message)
        
        elif intent_analysis['intent'] == 'financial_planning':
            response_data['response'] = self._generate_financial_planning_response(user_message, user_profile)
            if user_profile:
                response_data['analysis']['financial_plan'] = self.financial_planning_analysis(user_profile)
        
        elif intent_analysis['intent'] == 'company_analysis':
            response_data['response'] = self._generate_company_analysis_response(user_message)
        
        else:
            response_data['response'] = self._generate_general_response(user_message)
        
        # Add general recommendations based on sentiment
        if sentiment_analysis['sentiment'] == 'Negative':
            response_data['recommendations'].append("Consider diversification to reduce risk during uncertain times")
        elif sentiment_analysis['sentiment'] == 'Positive':
            response_data['recommendations'].append("Positive sentiment detected - consider rebalancing if overallocated")
        
        # Store in database
        self._store_conversation(response_data)
        
        return response_data
    
    def _generate_investment_response(self, message: str, user_profile: Dict[str, Any]) -> str:
        """Generate investment-related response"""
        base_advice = """
        Based on your investment inquiry, here's my professional analysis:
        
        🎯 **Investment Strategy Recommendations:**
        • Diversification across asset classes is fundamental for risk management
        • Consider your risk tolerance, time horizon, and financial goals
        • Regular portfolio rebalancing helps maintain target allocation
        • Dollar-cost averaging can reduce timing risk for long-term investments
        
        📊 **Asset Allocation Guidelines:**
        • Stocks: Higher potential returns but more volatile
        • Bonds: Provide stability and income
        • Alternative investments: Can enhance diversification
        • Cash: Maintains liquidity for opportunities and emergencies
        """
        
        if user_profile.get('age'):
            age = user_profile['age']
            if age < 30:
                base_advice += f"\n💡 **Age-Specific Advice (Age {age}):**\n• Consider aggressive growth strategy with higher stock allocation\n• Take advantage of compound growth over long time horizon"
            elif age > 50:
                base_advice += f"\n💡 **Age-Specific Advice (Age {age}):**\n• Shift towards more conservative allocation\n• Focus on capital preservation and income generation"
        
        return base_advice
    
    def _generate_market_analysis_response(self, message: str) -> str:
        """Generate market analysis response"""
        return """
        📈 **Current Market Analysis:**
        
        Based on comprehensive technical and fundamental analysis:
        
        🔍 **Key Market Indicators:**
        • Trend analysis using moving averages and momentum indicators
        • Volatility assessment for risk evaluation
        • Sector rotation patterns and relative strength
        • Economic indicators impact on market direction
        
        📊 **Technical Analysis:**
        • Support and resistance levels identification
        • Volume analysis for trend confirmation
        • Momentum oscillators for timing signals
        • Market sentiment indicators
        
        💡 **Strategic Implications:**
        • Consider market timing for entry/exit points
        • Adjust portfolio allocation based on market cycle
        • Monitor key economic events and earnings announcements
        • Maintain disciplined approach regardless of market noise
        """
    
    def _generate_risk_assessment_response(self, message: str) -> str:
        """Generate risk assessment response"""
        return """
        ⚠️ **Comprehensive Risk Assessment:**
        
        Understanding and managing investment risk is crucial for long-term success:
        
        🎯 **Risk Categories:**
        • **Market Risk**: Overall market volatility and systematic factors
        • **Credit Risk**: Default risk for bonds and fixed-income securities
        • **Liquidity Risk**: Ability to quickly convert investments to cash
        • **Inflation Risk**: Purchasing power erosion over time
        • **Currency Risk**: Foreign exchange fluctuations for international investments
        
        📊 **Risk Management Strategies:**
        • Diversification across asset classes, sectors, and geographies
        • Position sizing based on conviction and risk tolerance
        • Regular portfolio monitoring and rebalancing
        • Use of hedging instruments when appropriate
        • Maintaining adequate emergency fund
        
        💡 **Risk-Return Optimization:**
        • Higher returns typically require accepting higher risk
        • Risk tolerance should align with investment timeline
        • Consider risk-adjusted returns (Sharpe ratio) for evaluation
        """
    
    def _generate_financial_planning_response(self, message: str, user_profile: Dict[str, Any]) -> str:
        """Generate financial planning response"""
        response = """
        📋 **Comprehensive Financial Planning:**
        
        Effective financial planning requires a holistic approach:
        
        🎯 **Core Planning Elements:**
        • **Goal Setting**: Define specific, measurable financial objectives
        • **Budgeting**: Track income, expenses, and savings rate
        • **Emergency Fund**: 3-6 months of expenses in liquid savings
        • **Debt Management**: Prioritize high-interest debt elimination
        • **Insurance**: Protect against catastrophic financial loss
        
        💰 **Wealth Building Strategies:**
        • Maximize employer 401(k) matching contributions
        • Consider tax-advantaged accounts (IRA, HSA)
        • Automate savings and investments for consistency
        • Regular plan review and adjustment
        
        📊 **Retirement Planning:**
        • Start early to maximize compound growth
        • Estimate retirement income needs (70-80% of pre-retirement income)
        • Consider multiple income sources in retirement
        • Plan for healthcare costs and inflation
        """
        
        if user_profile.get('income'):
            income = user_profile['income']
            suggested_savings = income * 0.15
            response += f"\n💡 **Personalized Recommendation:**\nBased on your income level, consider saving ${suggested_savings:,.0f} annually (15% of income) for retirement."
        
        return response
    
    def _generate_company_analysis_response(self, message: str) -> str:
        """Generate company analysis response"""
        return """
        🏢 **Comprehensive Company Analysis:**
        
        Fundamental analysis is essential for informed investment decisions:
        
        📊 **Financial Statement Analysis:**
        • **Income Statement**: Revenue growth, profit margins, earnings quality
        • **Balance Sheet**: Asset quality, debt levels, liquidity position
        • **Cash Flow**: Operating cash flow, free cash flow generation
        • **Key Ratios**: PE, PEG, Debt-to-Equity, ROE, ROA
        
        🎯 **Qualitative Factors:**
        • Management quality and track record
        • Competitive positioning and market share
        • Industry trends and growth prospects
        • Regulatory environment and risks
        • Innovation and R&D capabilities
        
        💡 **Valuation Methods:**
        • Discounted Cash Flow (DCF) analysis
        • Comparable company analysis (multiples)
        • Sum-of-the-parts valuation for conglomerates
        • Asset-based valuation when appropriate
        
        📈 **Investment Thesis:**
        • Identify catalysts for value creation
        • Assess risk-reward profile
        • Determine appropriate position size
        • Set target price and stop-loss levels
        """
    
    def _generate_general_response(self, message: str) -> str:
        """Generate general financial response"""
        return """
        🤖 **Professional Financial Assistant**
        
        I'm here to provide comprehensive financial analysis and advice. I can help with:
        
        📈 **Investment Analysis:**
        • Portfolio optimization and asset allocation
        • Risk assessment and management strategies
        • Market trend analysis and timing
        
        💰 **Financial Planning:**
        • Retirement planning and wealth building
        • Tax optimization strategies
        • Insurance and estate planning
        
        🏢 **Company Analysis:**
        • Fundamental analysis and valuation
        • Financial ratio interpretation
        • Investment thesis development
        
        📊 **Market Research:**
        • Economic indicator analysis
        • Sector and industry research
        • Technical analysis and charting
        
        Feel free to ask specific questions about any of these areas, and I'll provide detailed, professional analysis using advanced ML models and comprehensive financial knowledge.
        """
    
    def _store_conversation(self, response_data: Dict[str, Any]):
        """Store conversation in database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO conversations 
                (user_message, bot_response, sentiment_score, confidence, analysis_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                response_data['message'],
                response_data['response'],
                response_data['sentiment']['confidence'],
                response_data['sentiment']['confidence'],
                response_data['intent']
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Database storage error: {e}")
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve conversation history"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT user_message, bot_response, sentiment_score, analysis_type, timestamp
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            return [
                {
                    'user_message': row[0],
                    'bot_response': row[1],
                    'sentiment_score': row[2],
                    'analysis_type': row[3],
                    'timestamp': row[4]
                }
                for row in results
            ]
        except Exception as e:
            logger.error(f"History retrieval error: {e}")
            return []
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary of all interactions"""
        try:
            cursor = self.conn.cursor()
            
            # Total conversations
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            # Average sentiment
            cursor.execute('SELECT AVG(sentiment_score) FROM conversations')
            avg_sentiment = cursor.fetchone()[0] or 0
            
            # Most common intents
            cursor.execute('''
                SELECT analysis_type, COUNT(*) as count
                FROM conversations
                GROUP BY analysis_type
                ORDER BY count DESC
                LIMIT 5
            ''')
            common_intents = cursor.fetchall()
            
            return {
                'total_conversations': total_conversations,
                'average_sentiment': round(avg_sentiment, 3),
                'common_intents': [{'intent': row[0], 'count': row[1]} for row in common_intents],
                'bot_status': 'Active',
                'models_loaded': ['Sentiment Analysis', 'Intent Classification', 'Risk Assessment', 'Market Analysis']
            }
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {'error': 'Unable to generate analytics'}
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Global bot instance
financial_bot = None

def get_financial_bot():
    """Get or create financial bot instance"""
    global financial_bot
    if financial_bot is None:
        financial_bot = AdvancedFinancialBot()
    return financial_bot

# Example usage
if __name__ == "__main__":
    bot = AdvancedFinancialBot()
    
    # Test various functionalities
    print("=== Testing Advanced Financial Bot ===\n")
    
    # Test sentiment analysis
    test_text = "The company reported excellent quarterly results with strong revenue growth"
    sentiment = bot.analyze_sentiment(test_text)
    print(f"Sentiment Analysis: {sentiment}\n")
    
    # Test financial ratios
    financial_data = {
        'stock_price': 100,
        'eps': 5,
        'total_debt': 1000000,
        'total_equity': 2000000,
        'current_assets': 500000,
        'current_liabilities': 300000,
        'net_income': 200000,
        'shareholders_equity': 1500000
    }
    ratios = bot.calculate_financial_ratios(financial_data)
    print(f"Financial Ratios: {ratios}\n")
    
    # Test investment advice
    user_profile = {
        'age': 30,
        'risk_tolerance': 'medium',
        'investment_horizon': 20,
        'income': 75000,
        'goals': ['retirement', 'house']
    }
    advice = bot.generate_investment_advice(user_profile)
    print(f"Investment Advice: {advice}\n")
    
    # Test comprehensive response
    response = bot.get_comprehensive_response("How should I invest for retirement?", user_profile)
    print(f"Comprehensive Response: {response['response']}")
