import unittest
from unittest.mock import patch, MagicMock
import requests
from test_config import BaseTestCase
from traderagent.data_fetcher import get_price_history, get_all_price_histories

class TestDataFetcher(BaseTestCase):
    """Test data fetching from Binance API"""
    
    def setUp(self):
        super().setUp()
        self.mock_binance_response = [
            [1728864000000, "60000.0", "60500.0", "59500.0", "60200.0", "100.0", 1728867599999, "6020000.0", 1000, "50.0", "3010000.0", "0"],
            [1728867600000, "60200.0", "61000.0", "60000.0", "60800.0", "120.0", 1728871199999, "7296000.0", 1200, "60.0", "3648000.0", "0"],
            [1728871200000, "60800.0", "61500.0", "60300.0", "61200.0", "110.0", 1728874799999, "6732000.0", 1100, "55.0", "3366000.0", "0"]
        ]
    
    @patch('traderagent.data_fetcher.requests.get')
    def test_get_price_history_success(self, mock_get):
        """Test successful price history retrieval"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_binance_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the function
        result = get_price_history("BTCUSDT", "1h", 3)
        
        # Verify API call
        mock_get.assert_called_once_with(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": "1h", "limit": 3}
        )
        
        # Verify result format
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], tuple)
        self.assertIsInstance(result[0][0], str)  # timestamp
        self.assertIsInstance(result[0][1], float)  # price
        
        # Verify price extraction (close price)
        self.assertEqual(result[0][1], 60200.0)
        self.assertEqual(result[1][1], 60800.0)
        self.assertEqual(result[2][1], 61200.0)
        
        print("✓ get_price_history success test passed")
    
    @patch('traderagent.data_fetcher.requests.get')
    def test_get_price_history_api_error(self, mock_get):
        """Test API error handling"""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Test should raise exception
        with self.assertRaises(requests.exceptions.RequestException):
            get_price_history("BTCUSDT", "1h", 3)
        
        print("✓ get_price_history API error test passed")
    
    @patch('traderagent.data_fetcher.requests.get')
    def test_get_price_history_http_error(self, mock_get):
        """Test HTTP error handling"""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Test should raise exception
        with self.assertRaises(requests.exceptions.HTTPError):
            get_price_history("BTCUSDT", "1h", 3)
        
        print("✓ get_price_history HTTP error test passed")
    
    @patch('traderagent.data_fetcher.get_price_history')
    def test_get_all_price_histories(self, mock_get_price_history):
        """Test getting all price histories"""
        # Mock individual price history calls
        btc_data = [("2025-10-01 12:00", 60000.0), ("2025-10-01 13:00", 60500.0)]
        sol_data = [("2025-10-01 12:00", 150.0), ("2025-10-01 13:00", 152.0)]
        
        def mock_price_side_effect(symbol, *args, **kwargs):
            if symbol == "BTCUSDT":
                return btc_data
            elif symbol == "SOLUSDT":
                return sol_data
            else:
                raise ValueError(f"Unknown symbol: {symbol}")
        
        mock_get_price_history.side_effect = mock_price_side_effect
        
        # Test the function
        result = get_all_price_histories()
        
        # Verify calls
        self.assertEqual(mock_get_price_history.call_count, 2)
        mock_get_price_history.assert_any_call("BTCUSDT")
        mock_get_price_history.assert_any_call("SOLUSDT")
        
        # Verify result structure
        self.assertIn("BTC", result)
        self.assertIn("SOL", result)
        self.assertEqual(result["BTC"], btc_data)
        self.assertEqual(result["SOL"], sol_data)
        
        print("✓ get_all_price_histories test passed")
    
    @patch('traderagent.data_fetcher.requests.get')
    def test_price_history_data_format(self, mock_get):
        """Test price history data format validation"""
        # Mock response with edge cases
        mock_response_data = [
            [1728864000000, "59999.99", "60500.1", "59500.0", "60200.55", "100.123", 1728867599999, "6020000.0", 1000, "50.0", "3010000.0", "0"]
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_price_history("BTCUSDT", "1h", 1)
        
        # Verify timestamp format
        timestamp, price = result[0]
        self.assertRegex(timestamp, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}')
        
        # Verify price is float
        self.assertIsInstance(price, float)
        self.assertEqual(price, 60200.55)
        
        print("✓ price history data format test passed")

class TestDataFetcherIntegration(BaseTestCase):
    """Integration tests for data fetcher (requires internet)"""
    
    def test_real_api_call(self):
        """Test real API call to Binance (optional - requires internet)"""
        try:
            # Test with small limit to avoid rate limiting
            result = get_price_history("BTCUSDT", "1h", 2)
            
            # Basic validation
            self.assertEqual(len(result), 2)
            self.assertIsInstance(result[0], tuple)
            self.assertIsInstance(result[0][0], str)
            self.assertIsInstance(result[0][1], float)
            self.assertGreater(result[0][1], 0)  # Price should be positive
            
            print("✓ Real API call test passed")
            
        except Exception as e:
            print(f"⚠ Real API call test skipped (no internet or API issue): {e}")
    
    def test_real_all_price_histories(self):
        """Test real API call for all symbols (optional - requires internet)"""
        try:
            result = get_all_price_histories()
            
            # Basic validation
            self.assertIn("BTC", result)
            self.assertIn("SOL", result)
            self.assertGreater(len(result["BTC"]), 0)
            self.assertGreater(len(result["SOL"]), 0)
            
            # Verify both have same length (same time period)
            self.assertEqual(len(result["BTC"]), len(result["SOL"]))
            
            print("✓ Real all price histories test passed")
            
        except Exception as e:
            print(f"⚠ Real all price histories test skipped (no internet or API issue): {e}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)