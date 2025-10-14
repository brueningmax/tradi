#!/usr/bin/env python3
"""
Test Runner for TraderAgent
"""

import sys
import unittest
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
tests_dir = project_root / "tests"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(tests_dir))

def run_all_tests():
    """Discover and run all tests (excluding expensive real API tests)"""
    print("Running TraderAgent Test Suite...")
    print(f"Test directory: {tests_dir}")
    print(f"Source directory: {src_dir}")
    print("=" * 50)
    print("Note: Real OpenAI API tests are excluded to avoid costs.")
    print("   To run real API tests: python tests/test_ai_decision_real_api.py")
    print("   To include conditional real API tests: set RUN_REAL_API_TESTS=true")
    print("=" * 50)
    
    # Discover tests, excluding real API tests
    loader = unittest.TestLoader()
    start_dir = str(tests_dir)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Remove the real API test file from the suite
    filtered_suite = unittest.TestSuite()
    for test_group in suite:
        for test_case in test_group:
            # Skip the real API test file
            if not test_case.__class__.__module__.endswith('test_ai_decision_real_api'):
                filtered_suite.addTest(test_case)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(filtered_suite)
    
    # Print summary
    print("=" * 50)
    if result.wasSuccessful():
        print("All tests passed!")
    else:
        print(f"{len(result.failures)} failures, {len(result.errors)} errors")
        
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)