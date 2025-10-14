import unittest
import json
import os
from unittest.mock import patch
from test_config import BaseTestCase
from traderagent.advanced_trader import AdvancedTrader

class TestAdvancedTraderPaperOnly(BaseTestCase):
    """Test advanced trader functionality - PAPER TRADING ONLY"""
    
    def setUp(self):
        super().setUp()
        # ONLY use paper trading for tests
        self.trader = AdvancedTrader(paper_trading=True)
        self.test_balance_file = self.create_temp_balance()
        
        # Patch the balance file path to use our temp file
        self.trader.balance_file = self.test_balance_file
    
    def test_paper_trading_initialization(self):
        """Test that trader is properly initialized for paper trading"""
        self.assertTrue(self.trader.paper_trading)
        # Test that we're using paper trading mode (not the filename)
        self.assertTrue(hasattr(self.trader, 'paper_trading'))
        self.assertTrue(self.trader.paper_trading)
        print("✓ Paper trading initialization test passed")
    
    def test_load_save_balance(self):
        """Test balance loading and saving"""
        # Test loading
        balance = self.trader.load_balance()
        self.assertEqual(balance["USD"], 10000.0)
        self.assertTrue(balance["paper_trading"])
        
        # Modify and save
        balance["USD"] = 9500.0
        balance["realized_pnl"] = 100.0
        self.trader.save_balance(balance)
        
        # Load again and verify
        reloaded_balance = self.trader.load_balance()
        self.assertEqual(reloaded_balance["USD"], 9500.0)
        self.assertEqual(reloaded_balance["realized_pnl"], 100.0)
        
        print("✓ Load/save balance test passed")
    
    def test_buy_long_position(self):
        """Test opening a long position"""
        balance = self.trader.load_balance()
        initial_available = balance["margin"]["available"]
        
        # Execute BUY_LONG
        success = self.trader.execute_trade(
            balance, "BUY_LONG", "BTC", 60000.0, 0.5, 1.0, 58000.0, 65000.0
        )
        
        self.assertTrue(success)
        
        # Check position was created
        btc_long = balance["positions"]["BTC"]["long"]
        self.assertGreater(btc_long["amount"], 0)
        self.assertEqual(btc_long["avg_price"], 60000.0)
        self.assertEqual(btc_long["stop_loss"], 58000.0)
        self.assertEqual(btc_long["take_profit"], 65000.0)
        
        # Check margin was used
        expected_margin_used = initial_available * 0.5
        self.assertAlmostEqual(balance["margin"]["used"], expected_margin_used, places=2)
        self.assertAlmostEqual(balance["margin"]["available"], initial_available - expected_margin_used, places=2)
        
        # Check history
        self.assertGreater(len(balance["history"]), 0)
        self.assertIn("[PAPER]", balance["history"][-1])
        self.assertIn("OPENED LONG", balance["history"][-1])
        
        print("✓ Buy long position test passed")
    
    def test_sell_short_position(self):
        """Test opening a short position"""
        balance = self.trader.load_balance()
        initial_available = balance["margin"]["available"]
        
        # Execute SELL_SHORT
        success = self.trader.execute_trade(
            balance, "SELL_SHORT", "SOL", 150.0, 0.3, 1.0, 160.0, 140.0
        )
        
        self.assertTrue(success)
        
        # Check position was created
        sol_short = balance["positions"]["SOL"]["short"]
        self.assertGreater(sol_short["amount"], 0)
        self.assertEqual(sol_short["avg_price"], 150.0)
        self.assertEqual(sol_short["stop_loss"], 160.0)
        self.assertEqual(sol_short["take_profit"], 140.0)
        
        # Check margin was used
        expected_margin_used = initial_available * 0.3
        self.assertAlmostEqual(balance["margin"]["used"], expected_margin_used, places=2)
        
        # Check history
        self.assertIn("[PAPER]", balance["history"][-1])
        self.assertIn("OPENED SHORT", balance["history"][-1])
        
        print("✓ Sell short position test passed")
    
    def test_close_long_position_profit(self):
        """Test closing a long position with profit"""
        balance = self.trader.load_balance()
        
        # First open a long position
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.5, 1.0, None, None)
        initial_realized_pnl = balance["realized_pnl"]
        
        # Close at higher price (profit)
        success = self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 65000.0, 1.0)
        
        self.assertTrue(success)
        
        # Check position was closed
        btc_long = balance["positions"]["BTC"]["long"]
        self.assertEqual(btc_long["amount"], 0)
        self.assertEqual(btc_long["avg_price"], 0)
        
        # Check profit was realized
        expected_profit = (65000.0 - 60000.0) * (5000.0 / 60000.0)  # price_diff * amount
        self.assertGreater(balance["realized_pnl"], initial_realized_pnl)
        
        # Check margin was released
        self.assertEqual(balance["margin"]["used"], 0)
        self.assertGreater(balance["margin"]["available"], 10000.0)  # Should have original + profit
        
        print("✓ Close long position with profit test passed")
    
    def test_close_short_position_profit(self):
        """Test closing a short position with profit"""
        balance = self.trader.load_balance()
        
        # First open a short position
        self.trader.execute_trade(balance, "SELL_SHORT", "SOL", 150.0, 0.4, 1.0, None, None)
        initial_realized_pnl = balance["realized_pnl"]
        
        # Close at lower price (profit for short)
        success = self.trader.execute_trade(balance, "CLOSE_SHORT", "SOL", 140.0, 1.0)
        
        self.assertTrue(success)
        
        # Check position was closed
        sol_short = balance["positions"]["SOL"]["short"]
        self.assertEqual(sol_short["amount"], 0)
        
        # Check profit was realized (price went down = profit for short)
        self.assertGreater(balance["realized_pnl"], initial_realized_pnl)
        
        print("✓ Close short position with profit test passed")
    
    def test_partial_position_close(self):
        """Test partial position closing"""
        balance = self.trader.load_balance()
        
        # Open a position
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.8, 1.0, None, None)
        initial_amount = balance["positions"]["BTC"]["long"]["amount"]
        
        # Close 50% of position
        success = self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 62000.0, 0.5)
        
        self.assertTrue(success)
        
        # Check partial close
        remaining_amount = balance["positions"]["BTC"]["long"]["amount"]
        self.assertAlmostEqual(remaining_amount, initial_amount * 0.5, places=6)
        self.assertGreater(remaining_amount, 0)
        
        # Check some margin was released but not all
        self.assertGreater(balance["margin"]["used"], 0)
        self.assertLess(balance["margin"]["used"], 8000.0)  # Less than initial 80%
        
        print("✓ Partial position close test passed")
    
    def test_leverage_forced_to_one(self):
        """Test that leverage is forced to 1.0"""
        balance = self.trader.load_balance()
        
        # Try to use 5x leverage - should be forced to 1x
        success = self.trader.execute_trade(
            balance, "BUY_LONG", "BTC", 60000.0, 0.5, 5.0, None, None
        )
        
        self.assertTrue(success)
        
        # Check that position uses 1:1 ratio (no leverage)
        margin_used = balance["margin"]["used"]
        position_value = balance["positions"]["BTC"]["long"]["amount"] * 60000.0
        self.assertAlmostEqual(margin_used, position_value, places=2)
        
        print("✓ Leverage forced to 1.0 test passed")
    
    def test_insufficient_margin(self):
        """Test behavior with insufficient margin"""
        balance = self.trader.load_balance()
        
        # Use all available margin
        balance["margin"]["available"] = 0
        balance["margin"]["used"] = 10000.0
        
        # Try to open position - should fail
        success = self.trader.execute_trade(
            balance, "BUY_LONG", "BTC", 60000.0, 0.5, 1.0, None, None
        )
        
        self.assertFalse(success)
        
        # Position should not be created
        self.assertEqual(balance["positions"]["BTC"]["long"]["amount"], 0)
        
        print("✓ Insufficient margin test passed")
    
    def test_close_nonexistent_position(self):
        """Test closing a position that doesn't exist"""
        balance = self.trader.load_balance()
        
        # Try to close long position that doesn't exist
        success = self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 60000.0, 1.0)
        
        self.assertFalse(success)
        
        # Try to close short position that doesn't exist
        success = self.trader.execute_trade(balance, "CLOSE_SHORT", "SOL", 150.0, 1.0)
        
        self.assertFalse(success)
        
        print("✓ Close nonexistent position test passed")
    
    def test_stop_loss_trigger(self):
        """Test stop loss triggering"""
        balance = self.trader.load_balance()
        
        # Open long position with stop loss
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.5, 1.0, 58000.0, None)
        
        # Create current prices that trigger stop loss
        current_prices = {"BTC": 57000.0, "SOL": 150.0}
        
        # Check stop loss
        self.trader.check_stop_losses_and_take_profits(balance, current_prices)
        
        # Position should be closed
        self.assertEqual(balance["positions"]["BTC"]["long"]["amount"], 0)
        
        # Should have realized a loss
        self.assertLess(balance["realized_pnl"], 0)
        
        print("✓ Stop loss trigger test passed")
    
    def test_take_profit_trigger(self):
        """Test take profit triggering"""
        balance = self.trader.load_balance()
        
        # Open short position with take profit
        self.trader.execute_trade(balance, "SELL_SHORT", "SOL", 150.0, 0.4, 1.0, None, 140.0)
        
        # Create current prices that trigger take profit
        current_prices = {"BTC": 60000.0, "SOL": 139.0}
        
        # Check take profit
        self.trader.check_stop_losses_and_take_profits(balance, current_prices)
        
        # Position should be closed
        self.assertEqual(balance["positions"]["SOL"]["short"]["amount"], 0)
        
        # Should have realized a profit
        self.assertGreater(balance["realized_pnl"], 0)
        
        print("✓ Take profit trigger test passed")
    
    def test_legacy_buy_sell(self):
        """Test legacy BUY/SELL actions"""
        balance = self.trader.load_balance()
        initial_usd = balance["USD"]
        
        # Test legacy BUY
        success = self.trader.execute_trade(balance, "BUY", "BTC", 60000.0, 0.3)
        self.assertTrue(success)
        self.assertLess(balance["USD"], initial_usd)
        self.assertGreater(balance["coins"]["BTC"]["amount"], 0)
        
        # Test legacy SELL
        success = self.trader.execute_trade(balance, "SELL", "BTC", 65000.0, 1.0)
        self.assertTrue(success)
        self.assertEqual(balance["coins"]["BTC"]["amount"], 0)
        self.assertGreater(balance["USD"], initial_usd * 0.7)  # Should have made profit
        
        print("✓ Legacy buy/sell test passed")
    
    def test_position_summary(self):
        """Test position summary generation"""
        balance = self.trader.load_balance()
        
        # Open multiple positions
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.3, 1.0, None, None)
        self.trader.execute_trade(balance, "SELL_SHORT", "SOL", 150.0, 0.2, 1.0, None, None)
        
        current_prices = {"BTC": 62000.0, "SOL": 145.0}
        
        # Test summary
        summary = self.trader.get_position_summary(balance, current_prices)
        
        self.assertIn("BTC LONG", summary)
        self.assertIn("SOL SHORT", summary)
        self.assertIn("P&L:", summary)
        
        # Test empty summary
        empty_balance = self.trader.load_balance()
        empty_summary = self.trader.get_position_summary(empty_balance, current_prices)
        self.assertEqual(empty_summary, "No open positions")
        
        print("✓ Position summary test passed")
    
    def test_total_pnl_calculation(self):
        """Test total P&L calculation across all positions"""
        balance = self.trader.load_balance()
        
        # Open mixed positions
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.4, 1.0, None, None)
        self.trader.execute_trade(balance, "SELL_SHORT", "SOL", 150.0, 0.3, 1.0, None, None)
        self.trader.execute_trade(balance, "BUY", "BTC", 61000.0, 0.1)  # Legacy position
        
        # Calculate P&L with different prices
        current_prices = {"BTC": 65000.0, "SOL": 140.0}
        total_pnl = self.trader.calculate_total_pnl(balance, current_prices)
        
        # Should have positive P&L (BTC up, SOL down)
        self.assertGreater(total_pnl, 0)
        
        # Test with losing prices
        losing_prices = {"BTC": 55000.0, "SOL": 160.0}
        losing_pnl = self.trader.calculate_total_pnl(balance, losing_prices)
        
        # Should have negative P&L
        self.assertLess(losing_pnl, 0)
        
        print("✓ Total P&L calculation test passed")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)