#!/usr/bin/env python3
"""
Test Enhanced Financial Chatbot with Detailed Q&A
Demo script to show the improved educational responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from advanced_financial_desktop import AdvancedFinancialChatbot

def test_chatbot_responses():
    """Test the enhanced chatbot with sample questions"""
    
    print("🤖 Testing Enhanced Financial Chatbot with Detailed Q&A\n")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = AdvancedFinancialChatbot()
    
    # Test questions similar to your examples
    test_questions = [
        "Compare two investment projects with different risk levels",
        "What is compound interest vs simple interest?",
        "Explain primary market and secondary market",
        "Calculate expected return for a stock",
        "Show mutual fund future value calculation",
        "Give me comprehensive finance lessons"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🎓 TEST {i}: {question}")
        print("-" * 50)
        
        try:
            response = chatbot.process_message(question)
            print(response['message'])
            print(f"\n📊 Confidence: {response.get('confidence', 0)*100:.1f}%")
            print(f"📝 Type: {response.get('type', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_chatbot_responses()
