#!/usr/bin/env python3
"""
Test the GitHub Actions trading workflow locally
"""

import os
import subprocess
import sys
from pathlib import Path

def test_local_execution():
    """Test the trading bot execution locally to simulate GitHub Actions"""
    
    print("🧪 Testing TraderAgent GitHub Actions Workflow Locally")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set it before running this test:")
        print("   export OPENAI_API_KEY='your_api_key_here'")
        return False
    
    print("✅ OpenAI API key found")
    
    # Set CI environment variables to simulate GitHub Actions
    os.environ['CI'] = 'true'
    os.environ['GITHUB_ACTIONS'] = 'true'
    
    print("🔧 Environment variables set to simulate CI/CD")
    
    # Test paper trading with volume analysis
    print("\n📊 Testing: Paper trading with volume analysis")
    try:
        result = subprocess.run([
            sys.executable, 'main.py', '--live', '--paper'
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Paper trading test PASSED")
        else:
            print(f"❌ Paper trading test FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    # Test without volume analysis
    print("\n📈 Testing: Paper trading without volume analysis")
    try:
        result = subprocess.run([
            sys.executable, 'main.py', '--live', '--paper', '--no-volume'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ No-volume trading test PASSED")
        else:
            print(f"❌ No-volume trading test FAILED (exit code: {result.returncode})")
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ No-volume test failed: {e}")
        return False
    
    # Check if balance file exists and is valid
    balance_file = Path("data/paper_balance.json")
    if balance_file.exists():
        print("✅ Paper balance file exists")
        try:
            import json
            with open(balance_file) as f:
                balance = json.load(f)
            print(f"📊 Current balance: ${balance['USD']:.2f}")
            print(f"📈 Realized P&L: ${balance['realized_pnl']:.2f}")
            print("✅ Balance file is valid JSON")
        except Exception as e:
            print(f"❌ Balance file is invalid: {e}")
            return False
    else:
        print("❌ Paper balance file not found")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ TraderAgent is ready for GitHub Actions deployment")
    return True

if __name__ == "__main__":
    success = test_local_execution()
    sys.exit(0 if success else 1)