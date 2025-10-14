import unittest
import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path

# Add src directory to Python path for testing
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

class TestConfig:
    """Test configuration and utilities"""
    
    @staticmethod
    def create_test_balance():
        """Create a test balance for paper trading"""
        return {
            "USD": 10000.0,
            "coins": {
                "BTC": {"amount": 0.0, "avg_price": 0.0},
                "SOL": {"amount": 0.0, "avg_price": 0.0}
            },
            "positions": {
                "BTC": {
                    "long": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None},
                    "short": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None}
                },
                "SOL": {
                    "long": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None},
                    "short": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None}
                }
            },
            "margin": {"available": 10000.0, "used": 0.0},
            "history": [],
            "realized_pnl": 0.0,
            "paper_trading": True
        }
    
    @staticmethod
    def create_test_price_data():
        """Create mock price data for testing"""
        timestamps = [f"2025-10-{i:02d} 12:00" for i in range(1, 8)]
        btc_prices = [60000, 61000, 59500, 62000, 61500, 63000, 62500]
        sol_prices = [150, 152, 148, 155, 153, 157, 156]
        
        return {
            "BTC": list(zip(timestamps, btc_prices)),
            "SOL": list(zip(timestamps, sol_prices))
        }
    
    @staticmethod
    def create_temp_balance_file(balance_data):
        """Create a temporary balance file for testing"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(balance_data, temp_file, indent=2)
        temp_file.close()
        return temp_file.name
    
    @staticmethod
    def cleanup_temp_file(filepath):
        """Clean up temporary files"""
        if os.path.exists(filepath):
            os.unlink(filepath)

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_balance = TestConfig.create_test_balance()
        self.test_prices = TestConfig.create_test_price_data()
        self.temp_files = []
    
    def tearDown(self):
        """Clean up after tests"""
        for temp_file in self.temp_files:
            TestConfig.cleanup_temp_file(temp_file)
    
    def create_temp_balance(self, balance_data=None):
        """Helper to create temporary balance file"""
        if balance_data is None:
            balance_data = self.test_balance
        temp_file = TestConfig.create_temp_balance_file(balance_data)
        self.temp_files.append(temp_file)
        return temp_file

if __name__ == '__main__':
    # Run basic infrastructure tests
    print("Testing infrastructure setup...")
    
    # Test balance creation
    balance = TestConfig.create_test_balance()
    assert balance["USD"] == 10000.0
    assert balance["paper_trading"] == True
    print("✓ Test balance creation works")
    
    # Test price data creation
    prices = TestConfig.create_test_price_data()
    assert "BTC" in prices
    assert "SOL" in prices
    assert len(prices["BTC"]) == 7
    print("✓ Test price data creation works")
    
    # Test temp file creation
    temp_file = TestConfig.create_temp_balance_file(balance)
    assert os.path.exists(temp_file)
    with open(temp_file, 'r') as f:
        loaded_balance = json.load(f)
    assert loaded_balance["USD"] == 10000.0
    TestConfig.cleanup_temp_file(temp_file)
    assert not os.path.exists(temp_file)
    print("✓ Temp file creation and cleanup works")
    
    print("Test infrastructure setup complete!")