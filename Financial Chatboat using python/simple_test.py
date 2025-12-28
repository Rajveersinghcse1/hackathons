#!/usr/bin/env python3
"""
Simple test of the enhanced financial chatbot Q&A system
"""

# Import necessary modules without GUI
import sqlite3
import pickle
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler

class SimpleFinancialBot:
    """Simplified version for testing Q&A responses"""
    
    def __init__(self):
        self.financial_terms = {
            'diversification': 'Spreading investments across various assets to reduce risk',
            'compound interest': 'Interest calculated on initial principal and accumulated interest',
            'bull market': 'Period of rising stock prices and investor optimism',
            'bear market': 'Period of declining stock prices and investor pessimism'
        }
    
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
    
    def process_question(self, question: str) -> str:
        """Process questions and return detailed answers"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['project', 'investment choice', 'risk averse', 'compare']):
            return self._get_investment_comparison_lesson()
        elif any(word in question_lower for word in ['compound', 'simple', 'interest']):
            return self._get_interest_calculation_lesson()
        else:
            return """📚 **Welcome to Enhanced Financial Education!**

Ask me about:
• Investment project comparisons
• Interest calculations (simple vs compound)
• Primary vs secondary markets
• Stock return calculations
• Mutual fund growth projections

Try questions like:
- "Compare investment projects"
- "What is compound interest?"
- "Calculate expected return"
"""

def main():
    """Test the enhanced Q&A system"""
    print("🤖 Enhanced Financial Chatbot - Q&A Test")
    print("=" * 50)
    
    bot = SimpleFinancialBot()
    
    test_questions = [
        "Compare two investment projects with different risk levels",
        "What is compound interest vs simple interest?",
        "Help with investment decisions"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🎓 TEST {i}: {question}")
        print("-" * 40)
        response = bot.process_question(question)
        print(response)
        print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
