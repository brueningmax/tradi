import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from traderagent.data_fetcher import get_volume_analysis, get_price_and_volume_history, get_all_price_and_volume_histories
from traderagent.ai_decision import get_ai_decision_with_volume


class TestVolumeAnalysis(unittest.TestCase):
    
    def test_volume_analysis_high(self):
        """Test volume analysis with high volume scenario"""
        # High recent volume compared to older volume
        volumes = [100, 120, 110, 90, 105, 180, 200, 220, 190, 210]
        result = get_volume_analysis(volumes)
        self.assertEqual(result, "HIGH (significantly above average)")
    
    def test_volume_analysis_elevated(self):
        """Test volume analysis with elevated volume scenario"""
        # Moderately high recent volume
        volumes = [100, 120, 110, 90, 105, 130, 140, 135, 125, 130]
        result = get_volume_analysis(volumes)
        self.assertEqual(result, "ELEVATED (above average)")
    
    def test_volume_analysis_low(self):
        """Test volume analysis with low volume scenario"""
        # Low recent volume compared to older volume
        volumes = [100, 120, 110, 90, 105, 60, 50, 55, 45, 40]
        result = get_volume_analysis(volumes)
        self.assertEqual(result, "LOW (below average)")
    
    def test_volume_analysis_normal(self):
        """Test volume analysis with normal volume scenario"""
        # Similar recent and older volume
        volumes = [100, 120, 110, 90, 105, 95, 110, 100, 105, 95]
        result = get_volume_analysis(volumes)
        self.assertEqual(result, "NORMAL (average levels)")
    
    def test_volume_analysis_insufficient_data(self):
        """Test volume analysis with insufficient data"""
        volumes = [100]
        result = get_volume_analysis(volumes)
        self.assertEqual(result, "Insufficient volume data")
    
    @patch('traderagent.data_fetcher.requests.get')
    def test_get_price_and_volume_history(self, mock_get):
        """Test fetching price and volume history"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            [1609459200000, "29000", "29500", "28500", "29200", "1234.56", "35000000", 100, "600.12", "17500000", "0"],
            [1609462800000, "29200", "29800", "29100", "29600", "2345.67", "42000000", 150, "800.23", "23600000", "0"],
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_price_and_volume_history("BTCUSDT", "1h", 2)
        
        # Check that we get the expected format: (timestamp, price, volume)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 3)  # timestamp, price, volume
        self.assertEqual(result[0][1], 29200.0)  # Close price
        self.assertEqual(result[0][2], 1234.56)  # Volume
        self.assertEqual(result[1][1], 29600.0)  # Close price
        self.assertEqual(result[1][2], 2345.67)  # Volume
    
    @patch('traderagent.data_fetcher.requests.get')
    def test_get_all_price_and_volume_histories(self, mock_get):
        """Test fetching all price and volume histories"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            [1609459200000, "100", "105", "95", "102", "1000.0", "102000", 50, "500.0", "51000", "0"],
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_all_price_and_volume_histories()
        
        # Check that we get data for both BTC and SOL
        self.assertIn("BTC", result)
        self.assertIn("SOL", result)
        
        # Check that each entry has 3 elements (timestamp, price, volume)
        for coin in result:
            for entry in result[coin]:
                self.assertEqual(len(entry), 3)
    
    @patch('traderagent.ai_decision.client')
    def test_get_ai_decision_with_volume(self, mock_client):
        """Test AI decision making with volume data"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: HOLD\nSOL: BUY_LONG 25% 150 200"
        mock_client.chat.completions.create.return_value = mock_response
        
        # Sample price and volume data
        price_volume_histories = {
            "BTC": [
                ("2024-01-01 10:00", 50000.0, 1000.0),
                ("2024-01-01 11:00", 50500.0, 1200.0),
                ("2024-01-01 12:00", 51000.0, 800.0),
            ],
            "SOL": [
                ("2024-01-01 10:00", 100.0, 5000.0),
                ("2024-01-01 11:00", 105.0, 6000.0),
                ("2024-01-01 12:00", 110.0, 4000.0),
            ]
        }
        
        balance = {
            "USD": 10000.0,
            "realized_pnl": 0.0,
            "positions": {
                "BTC": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}},
                "SOL": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}}
            }
        }
        
        decisions = get_ai_decision_with_volume(price_volume_histories, balance)
        
        # Check that decisions were made
        self.assertIn("BTC", decisions)
        self.assertIn("SOL", decisions)
        self.assertEqual(decisions["BTC"], ("HOLD", 0.0))
        self.assertEqual(decisions["SOL"], ("BUY_LONG", 0.25, 1.0, 150.0, 200.0))
        
        # Verify that the prompt included volume information
        call_args = mock_client.chat.completions.create.call_args[1]
        prompt_content = call_args["messages"][0]["content"]
        self.assertIn("volume analysis", prompt_content)
        self.assertIn("Recent volumes", prompt_content)


if __name__ == '__main__':
    unittest.main()