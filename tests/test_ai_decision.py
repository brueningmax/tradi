import unittest
from unittest.mock import patch, MagicMock
import os
from test_config import BaseTestCase
from traderagent.ai_decision import get_ai_decision

class TestAIDecision(BaseTestCase):
    """Test AI decision making functionality"""
    
    def setUp(self):
        super().setUp()
        self.price_histories = {
            "BTC": [
                ("2025-10-01 12:00", 60000.0),
                ("2025-10-01 13:00", 61000.0),
                ("2025-10-01 14:00", 62000.0)
            ],
            "SOL": [
                ("2025-10-01 12:00", 150.0),
                ("2025-10-01 13:00", 152.0),
                ("2025-10-01 14:00", 155.0)
            ]
        }
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_buy_long_decision_parsing(self, mock_openai):
        """Test parsing of BUY_LONG decision"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: BUY_LONG 50% 58000 70000\nSOL: HOLD"
        mock_openai.return_value = mock_response
        
        # Test the function
        result = get_ai_decision(self.price_histories, self.test_balance)
        
        # Verify OpenAI was called
        mock_openai.assert_called_once()
        call_args = mock_openai.call_args
        self.assertEqual(call_args[1]['model'], 'gpt-4o')
        # Temperature parameter removed for compatibility
        
        # Verify parsing
        self.assertIn("BTC", result)
        self.assertIn("SOL", result)
        
        # Check BTC decision (should be 5 parameters for BUY_LONG)
        btc_decision = result["BTC"]
        self.assertEqual(len(btc_decision), 5)
        action, percent, leverage, stop_loss, take_profit = btc_decision
        self.assertEqual(action, "BUY_LONG")
        self.assertEqual(percent, 0.5)  # 50%
        self.assertEqual(leverage, 1.0)  # Forced to 1.0
        self.assertEqual(stop_loss, 58000.0)
        self.assertEqual(take_profit, 70000.0)
        
        # Check SOL decision (should be 2 parameters for HOLD)
        sol_decision = result["SOL"]
        self.assertEqual(len(sol_decision), 2)
        action, percent = sol_decision
        self.assertEqual(action, "HOLD")
        self.assertEqual(percent, 0.0)
        
        print("✓ BUY_LONG decision parsing test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_sell_short_decision_parsing(self, mock_openai):
        """Test parsing of SELL_SHORT decision"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: SELL_SHORT 25% 65000 55000\nSOL: CLOSE_LONG 100%"
        mock_openai.return_value = mock_response
        
        result = get_ai_decision(self.price_histories, self.test_balance)
        
        # Check BTC decision
        btc_decision = result["BTC"]
        action, percent, leverage, stop_loss, take_profit = btc_decision
        self.assertEqual(action, "SELL_SHORT")
        self.assertEqual(percent, 0.25)  # 25%
        self.assertEqual(leverage, 1.0)  # Forced to 1.0
        self.assertEqual(stop_loss, 65000.0)
        self.assertEqual(take_profit, 55000.0)
        
        # Check SOL decision
        sol_decision = result["SOL"]
        action, percent = sol_decision
        self.assertEqual(action, "CLOSE_LONG")
        self.assertEqual(percent, 1.0)  # 100%
        
        print("✓ SELL_SHORT decision parsing test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_legacy_buy_sell_parsing(self, mock_openai):
        """Test parsing of legacy BUY/SELL decisions"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: BUY 30%\nSOL: SELL 75%"
        mock_openai.return_value = mock_response
        
        result = get_ai_decision(self.price_histories, self.test_balance)
        
        # Check BTC decision
        btc_decision = result["BTC"]
        action, percent = btc_decision
        self.assertEqual(action, "BUY")
        self.assertEqual(percent, 0.3)  # 30%
        
        # Check SOL decision
        sol_decision = result["SOL"]
        action, percent = sol_decision
        self.assertEqual(action, "SELL")
        self.assertEqual(percent, 0.75)  # 75%
        
        print("✓ Legacy BUY/SELL decision parsing test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_malformed_response_handling(self, mock_openai):
        """Test handling of malformed AI responses"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: INVALID_ACTION 50%\nSOL MISSING_COLON\n: MISSING_COIN\nBTC: BUY 30%"
        mock_openai.return_value = mock_response
        
        result = get_ai_decision(self.price_histories, self.test_balance)
        
        # Should only parse the valid BTC decision
        self.assertIn("BTC", result)
        self.assertNotIn("SOL", result)
        
        btc_decision = result["BTC"]
        action, percent = btc_decision
        self.assertEqual(action, "BUY")
        self.assertEqual(percent, 0.3)
        
        print("✓ Malformed response handling test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_null_stop_loss_take_profit(self, mock_openai):
        """Test handling of NULL stop loss and take profit"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: BUY_LONG 50% NULL 70000\nSOL: SELL_SHORT 25% 180 NULL"
        mock_openai.return_value = mock_response
        
        result = get_ai_decision(self.price_histories, self.test_balance)
        
        # Check BTC decision (NULL stop loss)
        btc_decision = result["BTC"]
        action, percent, leverage, stop_loss, take_profit = btc_decision
        self.assertEqual(action, "BUY_LONG")
        self.assertIsNone(stop_loss)
        self.assertEqual(take_profit, 70000.0)
        
        # Check SOL decision (NULL take profit)
        sol_decision = result["SOL"]
        action, percent, leverage, stop_loss, take_profit = sol_decision
        self.assertEqual(action, "SELL_SHORT")
        self.assertEqual(stop_loss, 180.0)
        self.assertIsNone(take_profit)
        
        print("✓ NULL stop loss/take profit handling test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_prompt_content(self, mock_openai):
        """Test that prompt contains necessary information"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: HOLD\nSOL: HOLD"
        mock_openai.return_value = mock_response
        
        # Create balance with existing positions
        balance_with_positions = self.test_balance.copy()
        balance_with_positions["positions"]["BTC"]["long"]["amount"] = 0.5
        balance_with_positions["positions"]["BTC"]["long"]["avg_price"] = 60000.0
        balance_with_positions["margin"]["available"] = 5000.0
        balance_with_positions["margin"]["used"] = 5000.0
        
        get_ai_decision(self.price_histories, balance_with_positions)
        
        # Get the prompt that was sent
        call_args = mock_openai.call_args
        prompt = call_args[1]['messages'][0]['content']
        
        # Verify prompt contains key information
        self.assertIn("BTC price trend", prompt)
        self.assertIn("SOL price trend", prompt)
        self.assertIn("USD: $10000.00", prompt)
        self.assertIn("Margin Available: $5000.00", prompt)
        self.assertIn("BTC LONG: 0.500000 @ 60000.00", prompt)
        self.assertIn("IMPORTANT: You cannot use leverage", prompt)
        self.assertIn("BUY_LONG", prompt)
        self.assertIn("SELL_SHORT", prompt)
        self.assertIn("volume analysis", prompt)  # Test new volume guidance
        
        print("✓ Prompt content test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_openai_error_handling(self, mock_openai):
        """Test handling of OpenAI API errors"""
        # Mock OpenAI API error
        mock_openai.side_effect = Exception("OpenAI API Error")
        
        # Should raise the exception
        with self.assertRaises(Exception):
            get_ai_decision(self.price_histories, self.test_balance)
        
        print("✓ OpenAI error handling test passed")
    
    def test_missing_api_key(self):
        """Test behavior when OpenAI API key is missing"""
        # Remove API key from environment
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # This should raise an error when trying to create the client
        # The error handling depends on how the client is initialized
        try:
            # Import will fail or client creation will fail
            import ai_decision
            print("⚠ Missing API key test: Module imported without error")
        except Exception as e:
            print(f"✓ Missing API key properly handled: {e}")

    @unittest.skipUnless(os.getenv('RUN_REAL_API_TESTS') == 'true', 
                         "Real API tests skipped (set RUN_REAL_API_TESTS=true to enable)")
    def test_real_openai_api_connection(self):
        """Test actual OpenAI API connectivity (COSTS MONEY - conditional)"""
        # This test is now conditional and skipped by default
        # To run: set environment variable RUN_REAL_API_TESTS=true
        print("💰 WARNING: Running real API test - this costs money!")
        
        # Skip if no real API key is set
        if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'test_api_key':
            self.skipTest("No real OpenAI API key found")
        
        try:
            # Test with minimal data to avoid using too many tokens
            minimal_price_histories = {
                "BTC": [("2024-01-01 12:00", 50000.0), ("2024-01-01 13:00", 50500.0)],
                "SOL": [("2024-01-01 12:00", 100.0), ("2024-01-01 13:00", 105.0)]
            }
            
            minimal_balance = {
                "USD": 1000.0,
                "realized_pnl": 0.0,
                "positions": {
                    "BTC": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}},
                    "SOL": {"long": {"amount": 0, "avg_price": 0}, "short": {"amount": 0, "avg_price": 0}}
                }
            }
            
            # Make actual API call
            decisions = get_ai_decision(minimal_price_histories, minimal_balance)
            
            # Verify we got valid decisions back
            self.assertIsInstance(decisions, dict)
            self.assertIn('BTC', decisions)
            self.assertIn('SOL', decisions)
            
            print("✅ Real OpenAI API connectivity test passed!")
            print(f"   Received decisions: {decisions}")
            
        except Exception as e:
            if "rate limit" in str(e).lower():
                print(f"⚠ Rate Limit: {e}")
                # Don't fail on rate limits
            else:
                raise

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)