#!/usr/bin/env python3
"""
Real OpenAI API Test Runner for TraderAgent

⚠️  WARNING: These tests make actual API calls and cost money!

Usage:
    python scripts/run_real_api_tests.py
    
Or run individual test files:
    python tests/test_ai_decision_real_api.py
    python scripts/test_openai_api.py
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
tests_dir = project_root / "tests"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(tests_dir))

def check_api_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'test_api_key':
        print("❌ No real OpenAI API key found!")
        print("   Please set the OPENAI_API_KEY environment variable")
        print("   Example: set OPENAI_API_KEY=sk-your-actual-key-here")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    return True

def run_real_api_tests():
    """Run real OpenAI API tests"""
    print("=" * 60)
    print("🚨 REAL OPENAI API TESTS - THESE COST MONEY! 🚨")
    print("=" * 60)
    
    if not check_api_key():
        return False
    
    print("These tests make actual API calls to OpenAI.")
    print("Make sure you have:")
    print("1. A valid OPENAI_API_KEY environment variable set")
    print("2. Sufficient API credits")
    print("3. Internet connection")
    print("=" * 60)
    
    # Ask for confirmation
    try:
        confirm = input("Continue with real API tests? (y/N): ").lower().strip()
        if confirm != 'y':
            print("Tests cancelled.")
            return False
    except (EOFError, KeyboardInterrupt):
        print("\nTests cancelled.")
        return False
    
    print("\n🧪 Running Real API Tests...")
    
    # Run the connectivity test script first
    try:
        print("\n1️⃣ Running basic connectivity test...")
        import subprocess
        result = subprocess.run([
            sys.executable, 
            str(project_root / "scripts" / "test_openai_api.py")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Basic connectivity test passed")
            print(result.stdout)
        else:
            print("❌ Basic connectivity test failed")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running basic connectivity test: {e}")
        return False
    
    # Run the comprehensive API tests
    try:
        print("\n2️⃣ Running comprehensive API tests...")
        result = subprocess.run([
            sys.executable, 
            str(project_root / "tests" / "test_ai_decision_real_api.py")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Comprehensive API tests passed")
            print(result.stdout)
        else:
            print("❌ Comprehensive API tests failed")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running comprehensive API tests: {e}")
        return False
    
    print("\n✅ All real API tests completed successfully!")
    return True

if __name__ == "__main__":
    success = run_real_api_tests()
    sys.exit(0 if success else 1)