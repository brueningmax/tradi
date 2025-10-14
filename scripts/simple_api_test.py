#!/usr/bin/env python3
"""
Simple OpenAI API Connectivity Test

A lightweight test to verify OpenAI API connectivity without 
running the full test suite.

Usage: python scripts/simple_api_test.py
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def test_openai_connectivity():
    """Simple test of OpenAI API connectivity"""
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'test_api_key':
        print("❌ No real OpenAI API key found!")
        print("   Set OPENAI_API_KEY environment variable")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        from traderagent.ai_decision import get_ai_decision
        
        # Minimal test data
        test_histories = {
            "BTC": [("2024-01-01 12:00", 50000.0), ("2024-01-01 13:00", 50500.0)],
            "SOL": [("2024-01-01 12:00", 100.0), ("2024-01-01 13:00", 105.0)]
        }
        
        test_balance = {
            "USD": 1000.0,
            "realized_pnl": 0.0,
            "positions": {
                "BTC": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}},
                "SOL": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}}
            }
        }
        
        print("🔗 Testing OpenAI API connectivity...")
        print("💰 This makes a real API call and costs money!")
        
        # Make API call
        result = get_ai_decision(test_histories, test_balance)
        
        print("✅ API call successful!")
        print(f"Response type: {type(result)}")
        print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Simple OpenAI API Connectivity Test")
    print("=" * 50)
    
    success = test_openai_connectivity()
    
    if success:
        print("\n✅ OpenAI API connectivity verified!")
    else:
        print("\n❌ OpenAI API connectivity test failed")
    
    sys.exit(0 if success else 1)