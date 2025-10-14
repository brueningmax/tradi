#!/usr/bin/env python3
"""
OpenAI API Connectivity Test
Quick health check for OpenAI API connectivity and authentication
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

try:
    from traderagent.ai_decision import get_ai_decision
    import openai
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure the traderagent package is properly installed")
    sys.exit(1)


def test_api_key_exists():
    """Check if API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No OpenAI API key found")
        print("   Please set OPENAI_API_KEY environment variable")
        return False
    
    if api_key == 'test_api_key':
        print("⚠ Test API key detected")
        print("   Please set a real OpenAI API key for connectivity testing")
        return False
    
    if len(api_key) < 20:
        print("❌ API key appears too short")
        print("   Please check your OPENAI_API_KEY environment variable")
        return False
    
    print(f"✅ API key found (length: {len(api_key)})")
    return True


def test_openai_client():
    """Test OpenAI client initialization"""
    try:
        from traderagent.ai_decision import client
        print("✅ OpenAI client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ OpenAI client initialization failed: {e}")
        return False


def test_simple_api_call():
    """Test a minimal API call to verify connectivity"""
    try:
        # Use minimal data to conserve tokens
        test_data = {
            "BTC": [("2024-01-01 12:00", 50000.0)],
            "SOL": [("2024-01-01 12:00", 100.0)]
        }
        
        test_balance = {
            "USD": 1000.0,
            "realized_pnl": 0.0,
            "positions": {
                "BTC": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}},
                "SOL": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}}
            }
        }
        
        print("🔗 Testing OpenAI API call...")
        
        # Make the API call
        decisions = get_ai_decision(test_data, test_balance)
        
        # Validate response
        if isinstance(decisions, dict) and 'BTC' in decisions and 'SOL' in decisions:
            print("✅ API call successful!")
            print(f"   Response: {decisions}")
            return True
        else:
            print(f"❌ Invalid response format: {decisions}")
            return False
            
    except openai.AuthenticationError:
        print("❌ Authentication failed - Invalid API key")
        return False
    except openai.RateLimitError:
        print("⚠ Rate limit exceeded - API is working but you're being throttled")
        return True  # API is reachable, just rate limited
    except openai.APIConnectionError:
        print("❌ Connection failed - Check your internet connection")
        return False
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False


def main():
    """Run all connectivity tests"""
    print("=" * 50)
    print("OpenAI API Connectivity Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: API Key
    print("\n1. Checking API Key Configuration...")
    if test_api_key_exists():
        tests_passed += 1
    
    # Test 2: Client Initialization
    print("\n2. Testing OpenAI Client Initialization...")
    if test_openai_client():
        tests_passed += 1
    
    # Test 3: API Call
    print("\n3. Testing API Connectivity...")
    if test_simple_api_call():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! OpenAI API is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)