import unittest
import os
from unittest.mock import patch, MagicMock
from test_config import BaseTestCase
from traderagent.advanced_trader import AdvancedTrader
from traderagent.ai_decision import get_ai_decision
from traderagent.data_fetcher import get_all_price_histories

class TestIntegrationWorkflows(BaseTestCase):
    """Integration tests for complete trading workflows - PAPER TRADING ONLY"""
    
    def setUp(self):
        super().setUp()
        self.trader = AdvancedTrader(paper_trading=True)
        self.test_balance_file = self.create_temp_balance()
        self.trader.balance_file = self.test_balance_file
        
        # Mock price data
        self.mock_price_histories = {
            "BTC": [
                ("2025-10-01 12:00", 60000.0),
                ("2025-10-01 13:00", 61000.0),
                ("2025-10-01 14:00", 62000.0),
                ("2025-10-01 15:00", 61500.0)
            ],
            "SOL": [
                ("2025-10-01 12:00", 150.0),
                ("2025-10-01 13:00", 152.0),
                ("2025-10-01 14:00", 155.0),
                ("2025-10-01 15:00", 153.0)
            ]
        }
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_complete_trading_cycle_paper_only(self, mock_openai):
        """Test complete trading cycle - PAPER TRADING ONLY"""
        
        # Ensure we're in paper trading mode
        self.assertTrue(self.trader.paper_trading)
        
        # Mock AI decision
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: BUY_LONG 50% 58000 65000\nSOL: SELL_SHORT 30% 160 140"
        mock_openai.return_value = mock_response
        
        # Load balance
        balance = self.trader.load_balance()
        initial_available = balance["margin"]["available"]
        
        # Step 1: Get AI decisions
        decisions = get_ai_decision(self.mock_price_histories, balance)
        
        # Step 2: Execute AI decisions
        current_prices = {"BTC": 62000.0, "SOL": 153.0}
        
        for coin, decision_data in decisions.items():
            if coin in current_prices:
                current_price = current_prices[coin]
                
                if len(decision_data) == 5:  # Advanced position
                    action, percent, leverage, stop_loss, take_profit = decision_data
                    self.trader.execute_trade(balance, action, coin, current_price, percent, leverage, stop_loss, take_profit)
                elif len(decision_data) == 2:  # Simple action
                    action, percent = decision_data
                    self.trader.execute_trade(balance, action, coin, current_price, percent)
        
        # Step 3: Verify positions were opened
        self.assertGreater(balance["positions"]["BTC"]["long"]["amount"], 0)
        self.assertGreater(balance["positions"]["SOL"]["short"]["amount"], 0)
        self.assertLess(balance["margin"]["available"], initial_available)
        
        # Step 4: Check stop losses and take profits
        # Simulate price movement that triggers BTC take profit
        profit_prices = {"BTC": 66000.0, "SOL": 153.0}
        self.trader.check_stop_losses_and_take_profits(balance, profit_prices)
        
        # BTC position should be closed due to take profit
        self.assertEqual(balance["positions"]["BTC"]["long"]["amount"], 0)
        self.assertGreater(balance["realized_pnl"], 0)
        
        # Step 5: Verify all trades were marked as [PAPER] or automated triggers
        for trade in balance["history"]:
            # Trade should be either [PAPER] or automated trigger like [TAKE PROFIT]/[STOP LOSS]
            self.assertTrue(
                "[PAPER]" in trade or "[TAKE PROFIT]" in trade or "[STOP LOSS]" in trade,
                f"Trade '{trade}' not properly marked"
            )
        
        print("✓ Complete trading cycle (PAPER ONLY) test passed")
    
    @patch('traderagent.data_fetcher.requests.get')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_full_workflow_with_mocked_apis(self, mock_openai, mock_requests):
        """Test full workflow with mocked external APIs - PAPER TRADING ONLY"""
        
        # Mock Binance API response
        mock_binance_data = [
            [1728864000000, "60000.0", "60500.0", "59500.0", "60200.0", "100.0", 1728867599999, "6020000.0", 1000, "50.0", "3010000.0", "0"],
            [1728867600000, "60200.0", "61000.0", "60000.0", "60800.0", "120.0", 1728871199999, "7296000.0", 1200, "60.0", "3648000.0", "0"]
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_binance_data
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        # Mock OpenAI response
        mock_ai_response = MagicMock()
        mock_ai_response.choices[0].message.content = "BTC: BUY_LONG 40% NULL 62000\nSOL: HOLD"
        mock_openai.return_value = mock_ai_response
        
        # Test complete workflow
        balance = self.trader.load_balance()
        
        # Get price histories (mocked)
        price_histories = get_all_price_histories()
        
        # Get AI decision (mocked)
        decisions = get_ai_decision(price_histories, balance)
        
        # Execute decisions
        current_prices = {coin: history[-1][1] for coin, history in price_histories.items()}
        
        for coin, decision_data in decisions.items():
            if coin in current_prices and len(decision_data) > 2:
                action, percent, leverage, stop_loss, take_profit = decision_data
                self.trader.execute_trade(balance, action, coin, current_prices[coin], percent, leverage, stop_loss, take_profit)
        
        # Verify integration worked
        self.assertGreater(balance["positions"]["BTC"]["long"]["amount"], 0)
        self.assertIn("[PAPER]", balance["history"][-1])
        
        print("✓ Full workflow with mocked APIs (PAPER ONLY) test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_multi_round_trading_simulation(self, mock_openai):
        """Test multi-round trading simulation - PAPER TRADING ONLY"""
        
        # Mock different AI responses for each round
        ai_responses = [
            "BTC: BUY_LONG 30% 58000 64000\nSOL: HOLD",
            "BTC: HOLD\nSOL: SELL_SHORT 25% 160 145",
            "BTC: CLOSE_LONG 50%\nSOL: HOLD",
            "BTC: CLOSE_LONG 100%\nSOL: CLOSE_SHORT 100%"
        ]
        
        balance = self.trader.load_balance()
        
        # Simulate price movements
        price_scenarios = [
            {"BTC": 61000.0, "SOL": 152.0},
            {"BTC": 62000.0, "SOL": 155.0},
            {"BTC": 63000.0, "SOL": 150.0},
            {"BTC": 64500.0, "SOL": 148.0}
        ]
        
        for round_num, (ai_response, prices) in enumerate(zip(ai_responses, price_scenarios)):
            print(f"  Round {round_num + 1}: Testing with prices BTC:{prices['BTC']}, SOL:{prices['SOL']}")
            
            # Mock AI response for this round
            mock_response = MagicMock()
            mock_response.choices[0].message.content = ai_response
            mock_openai.return_value = mock_response
            
            # Get AI decision
            decisions = get_ai_decision(self.mock_price_histories, balance)
            
            # Execute decisions
            for coin, decision_data in decisions.items():
                if coin in prices:
                    current_price = prices[coin]
                    
                    if len(decision_data) == 5:  # Advanced position
                        action, percent, leverage, stop_loss, take_profit = decision_data
                        self.trader.execute_trade(balance, action, coin, current_price, percent, leverage, stop_loss, take_profit)
                    elif len(decision_data) == 2:  # Simple action
                        action, percent = decision_data
                        self.trader.execute_trade(balance, action, coin, current_price, percent)
            
            # Check stop losses and take profits
            self.trader.check_stop_losses_and_take_profits(balance, prices)
        
        # Final verification
        # All positions should be closed by round 4
        self.assertEqual(balance["positions"]["BTC"]["long"]["amount"], 0)
        self.assertEqual(balance["positions"]["SOL"]["short"]["amount"], 0)
        
        # Should have trading history
        self.assertGreater(len(balance["history"]), 4)
        
        # All trades should be paper trades
        for trade in balance["history"]:
            self.assertIn("[PAPER]", trade)
        
        print("✓ Multi-round trading simulation (PAPER ONLY) test passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_risk_management_workflow(self, mock_openai):
        """Test risk management features in workflow - PAPER TRADING ONLY"""
        
        # Mock aggressive AI decision with stop losses
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BTC: BUY_LONG 80% 59000 66000\nSOL: SELL_SHORT 70% 158 145"
        mock_openai.return_value = mock_response
        
        balance = self.trader.load_balance()
        
        # Execute aggressive positions
        decisions = get_ai_decision(self.mock_price_histories, balance)
        current_prices = {"BTC": 60000.0, "SOL": 155.0}
        
        for coin, decision_data in decisions.items():
            if coin in current_prices and len(decision_data) == 5:
                action, percent, leverage, stop_loss, take_profit = decision_data
                self.trader.execute_trade(balance, action, coin, current_prices[coin], percent, leverage, stop_loss, take_profit)
        
        # Verify large positions were opened
        self.assertGreater(balance["margin"]["used"], 7000.0)  # 80% + 70% of funds used
        
        # Simulate adverse price movement triggering stop losses
        adverse_prices = {"BTC": 58000.0, "SOL": 160.0}  # Both hit stop losses
        
        initial_realized_pnl = balance["realized_pnl"]
        self.trader.check_stop_losses_and_take_profits(balance, adverse_prices)
        
        # Both positions should be closed due to stop losses
        self.assertEqual(balance["positions"]["BTC"]["long"]["amount"], 0)
        self.assertEqual(balance["positions"]["SOL"]["short"]["amount"], 0)
        
        # Should have realized losses
        self.assertLess(balance["realized_pnl"], initial_realized_pnl)
        
        # Margin should be released (allow for floating point precision)
        self.assertAlmostEqual(balance["margin"]["used"], 0, places=10)
        
        print("✓ Risk management workflow (PAPER ONLY) test passed")
    
    def test_paper_trading_safety_checks(self):
        """Test that paper trading safety checks work"""
        
        # Ensure trader is in paper mode
        self.assertTrue(self.trader.paper_trading)
        
        # Verify trader is configured for paper trading
        self.assertTrue(hasattr(self.trader, 'paper_trading'))
        self.assertTrue(self.trader.paper_trading)
        
        # Load balance and verify paper trading flag
        balance = self.trader.load_balance()
        self.assertTrue(balance.get("paper_trading", False))
        
        # Execute a trade and verify it's marked as paper
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.1, 1.0, None, None)
        
        # Check trade is marked as paper
        self.assertIn("[PAPER]", balance["history"][-1])
        
        print("✓ Paper trading safety checks passed")
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_api_key'})
    @patch('traderagent.ai_decision.client.chat.completions.create')
    def test_error_recovery_workflow(self, mock_openai):
        """Test error recovery in trading workflow - PAPER TRADING ONLY"""
        
        balance = self.trader.load_balance()
        
        # Test 1: Invalid AI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "INVALID FORMAT"
        mock_openai.return_value = mock_response
        
        decisions = get_ai_decision(self.mock_price_histories, balance)
        
        # Should handle gracefully (empty decisions)
        self.assertEqual(len(decisions), 0)
        
        # Test 2: Valid decision but insufficient margin
        balance["margin"]["available"] = 10.0  # Very low margin
        
        mock_response.choices[0].message.content = "BTC: BUY_LONG 90% NULL NULL"
        decisions = get_ai_decision(self.mock_price_histories, balance)
        
        # Should try to execute but fail gracefully
        for coin, decision_data in decisions.items():
            if len(decision_data) == 5:
                action, percent, leverage, stop_loss, take_profit = decision_data
                success = self.trader.execute_trade(balance, action, coin, 60000.0, percent, leverage, stop_loss, take_profit)
                # Should succeed but with very small position due to low margin
                self.assertTrue(success)
        
        print("✓ Error recovery workflow (PAPER ONLY) test passed")
    
    def test_performance_tracking_workflow(self):
        """Test performance tracking through workflow - PAPER TRADING ONLY"""
        
        balance = self.trader.load_balance()
        
        # Track initial state
        initial_available = balance["margin"]["available"]
        trade_count = 0
        
        # Execute series of trades
        trades = [
            ("BUY_LONG", "BTC", 60000.0, 0.3, 1.0, None, 65000.0),
            ("SELL_SHORT", "SOL", 150.0, 0.2, 1.0, 155.0, None),
            ("BUY", "BTC", 61000.0, 0.1),  # Legacy
        ]
        
        for trade_data in trades:
            if len(trade_data) == 7:  # Advanced trade
                action, coin, price, percent, leverage, stop_loss, take_profit = trade_data
                success = self.trader.execute_trade(balance, action, coin, price, percent, leverage, stop_loss, take_profit)
            else:  # Legacy trade
                action, coin, price, percent = trade_data
                success = self.trader.execute_trade(balance, action, coin, price, percent)
            
            if success:
                trade_count += 1
        
        # Check performance metrics
        self.assertEqual(len(balance["history"]), trade_count)
        
        # Calculate unrealized P&L
        current_prices = {"BTC": 63000.0, "SOL": 145.0}
        unrealized_pnl = self.trader.calculate_total_pnl(balance, current_prices)
        
        # Get position summary
        position_summary = self.trader.get_position_summary(balance, current_prices)
        
        # Verify tracking
        self.assertGreater(len(position_summary), 10)  # Should have position info
        self.assertNotEqual(unrealized_pnl, 0)  # Should have some P&L
        
        # Close all positions and check final performance
        self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 63000.0, 1.0)
        self.trader.execute_trade(balance, "CLOSE_SHORT", "SOL", 145.0, 1.0)
        self.trader.execute_trade(balance, "SELL", "BTC", 63000.0, 1.0)  # Legacy
        
        # Final performance check - include legacy USD changes
        final_available = balance["margin"]["available"] + (balance["USD"] - 10000.0)
        total_return = final_available - initial_available
        
        # Should equal realized P&L
        self.assertAlmostEqual(total_return, balance["realized_pnl"], places=2)
        
        print("✓ Performance tracking workflow (PAPER ONLY) test passed")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)