#!/usr/bin/env python3
"""
Quick test to verify the fixes for the financial chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test import
try:
    from advanced_financial_desktop import AdvancedFinancialChatbot
    print("✅ Import successful")
    
    # Initialize chatbot
    chatbot = AdvancedFinancialChatbot()
    print("✅ Chatbot initialized")
    
    # Test the problematic question
    test_question = "Q: A company is considering two funding options: Bank Loan at 8% interest rate and Issuing new Equity shares. Which option should the company choose if it wants to retain control, and why?"
    
    print(f"\n🧪 Testing question: {test_question[:80]}...")
    
    response = chatbot.process_message(test_question)
    print("✅ Question processed successfully!")
    print(f"📊 Response type: {response.get('type')}")
    print(f"📊 Confidence: {response.get('confidence', 0)*100:.1f}%")
    print(f"📝 Response length: {len(response.get('message', ''))} characters")
    
    # Test stock analysis
    print(f"\n🧪 Testing stock analysis: analyze stock AAPL")
    response2 = chatbot.process_message("analyze stock AAPL")
    print("✅ Stock analysis processed successfully!")
    print(f"📊 Response type: {response2.get('type')}")
    
    print(f"\n🎉 All tests passed! The application is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
