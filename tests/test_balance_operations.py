import unittest
import json
from test_config import BaseTestCase
from traderagent.utils import calc_unrealized_pnl
from traderagent.advanced_trader import AdvancedTrader

class TestBalanceOperations(BaseTestCase):
    """Test balance management and P&L calculations"""
    
    def setUp(self):
        super().setUp()
        self.trader = AdvancedTrader(paper_trading=True)
        self.current_prices = {"BTC": 62000.0, "SOL": 155.0}
    
    def test_unrealized_pnl_calculation_legacy(self):
        """Test legacy unrealized P&L calculation from utils.py"""
        # Create balance with legacy spot positions
        balance = {
            "coins": {
                "BTC": {"amount": 0.1, "avg_price": 60000.0},
                "SOL": {"amount": 10.0, "avg_price": 150.0}
            }
        }
        
        current_prices = {"BTC": 65000.0, "SOL": 145.0}
        
        # Calculate unrealized P&L
        unrealized = calc_unrealized_pnl(balance, current_prices)
        
        # BTC: (65000 - 60000) * 0.1 = 500
        # SOL: (145 - 150) * 10 = -50
        # Total: 500 - 50 = 450
        expected = 450.0
        self.assertEqual(unrealized, expected)
        
        print("✓ Legacy unrealized P&L calculation test passed")
    
    def test_advanced_pnl_calculation(self):
        """Test advanced P&L calculation with positions"""
        balance = self.test_balance.copy()
        
        # Add long position in BTC
        balance["positions"]["BTC"]["long"]["amount"] = 0.08  # ~5000 USD at 62500
        balance["positions"]["BTC"]["long"]["avg_price"] = 60000.0
        
        # Add short position in SOL
        balance["positions"]["SOL"]["short"]["amount"] = 20.0  # ~3000 USD at 150
        balance["positions"]["SOL"]["short"]["avg_price"] = 150.0
        
        # Add legacy spot position
        balance["coins"]["BTC"]["amount"] = 0.02
        balance["coins"]["BTC"]["avg_price"] = 61000.0
        
        current_prices = {"BTC": 65000.0, "SOL": 145.0}
        
        total_pnl = self.trader.calculate_total_pnl(balance, current_prices)
        
        # Long BTC: (65000 - 60000) * 0.08 = 400
        # Short SOL: (150 - 145) * 20 = 100  
        # Spot BTC: (65000 - 61000) * 0.02 = 80
        # Total: 400 + 100 + 80 = 580
        expected = 580.0
        self.assertEqual(total_pnl, expected)
        
        print("✓ Advanced P&L calculation test passed")
    
    def test_pnl_with_zero_positions(self):
        """Test P&L calculation with no positions"""
        balance = self.test_balance.copy()  # Empty positions
        
        total_pnl = self.trader.calculate_total_pnl(balance, self.current_prices)
        self.assertEqual(total_pnl, 0.0)
        
        print("✓ P&L with zero positions test passed")
    
    def test_pnl_with_negative_unrealized(self):
        """Test P&L calculation with losses"""
        balance = self.test_balance.copy()
        
        # Add losing long position
        balance["positions"]["BTC"]["long"]["amount"] = 0.1
        balance["positions"]["BTC"]["long"]["avg_price"] = 70000.0  # Bought high
        
        # Add losing short position  
        balance["positions"]["SOL"]["short"]["amount"] = 10.0
        balance["positions"]["SOL"]["short"]["avg_price"] = 140.0  # Shorted low
        
        current_prices = {"BTC": 60000.0, "SOL": 160.0}  # Bad prices
        
        total_pnl = self.trader.calculate_total_pnl(balance, current_prices)
        
        # Long BTC: (60000 - 70000) * 0.1 = -1000
        # Short SOL: (140 - 160) * 10 = -200
        # Total: -1000 - 200 = -1200
        expected = -1200.0
        self.assertEqual(total_pnl, expected)
        
        print("✓ P&L with negative unrealized test passed")
    
    def test_balance_state_transitions(self):
        """Test balance state changes through trading sequence"""
        balance = self.test_balance.copy()
        
        # Track initial state
        initial_available = balance["margin"]["available"]
        initial_realized = balance["realized_pnl"]
        
        # Step 1: Open long position
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.5, 1.0, None, None)
        
        # Check state after opening
        self.assertEqual(balance["margin"]["used"], 5000.0)
        self.assertEqual(balance["margin"]["available"], 5000.0)
        self.assertGreater(balance["positions"]["BTC"]["long"]["amount"], 0)
        
        # Step 2: Close position with profit
        self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 66000.0, 1.0)
        
        # Check final state
        self.assertEqual(balance["margin"]["used"], 0.0)
        self.assertGreater(balance["margin"]["available"], initial_available)
        self.assertGreater(balance["realized_pnl"], initial_realized)
        self.assertEqual(balance["positions"]["BTC"]["long"]["amount"], 0)
        
        # Calculate expected profit
        amount = 5000.0 / 60000.0  # Amount bought
        expected_profit = (66000.0 - 60000.0) * amount
        expected_final_available = initial_available + expected_profit
        
        self.assertAlmostEqual(balance["margin"]["available"], expected_final_available, places=2)
        
        print("✓ Balance state transitions test passed")
    
    def test_margin_accounting(self):
        """Test margin accounting accuracy"""
        balance = self.test_balance.copy()
        
        # Open multiple positions
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.3, 1.0, None, None)
        self.trader.execute_trade(balance, "SELL_SHORT", "SOL", 150.0, 0.4, 1.0, None, None)
        
        # Check margin accounting
        # BTC uses 30% of initial margin: 3000
        # SOL uses 40% of remaining margin: 40% of 7000 = 2800  
        expected_used = 3000.0 + 2800.0  # 5800
        expected_available = 10000.0 - expected_used  # 4200
        
        self.assertAlmostEqual(balance["margin"]["used"], expected_used, places=2)
        self.assertAlmostEqual(balance["margin"]["available"], expected_available, places=2)
        
        # Close one position partially
        self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 65000.0, 0.5)
        
        # Half of BTC margin should be released
        btc_margin_released = 3000.0 * 0.5  # 1500
        expected_used_after = expected_used - btc_margin_released  # 5500
        
        self.assertAlmostEqual(balance["margin"]["used"], expected_used_after, places=2)
        
        print("✓ Margin accounting test passed")
    
    def test_position_averaging(self):
        """Test position averaging when adding to existing positions"""
        balance = self.test_balance.copy()
        
        # Open initial position
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.4, 1.0, None, None)
        initial_amount = balance["positions"]["BTC"]["long"]["amount"]
        
        # Add to position at different price
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 64000.0, 0.3, 1.0, None, None)
        
        # Check position averaging
        final_position = balance["positions"]["BTC"]["long"]
        
        # Calculate expected average price
        initial_value = initial_amount * 60000.0
        # Second trade uses 30% of available margin (6000), so 1800 USD worth
        additional_value = 1800.0  # $1800 worth at $64000
        total_value = initial_value + additional_value
        total_amount = final_position["amount"]
        expected_avg_price = total_value / total_amount
        
        self.assertAlmostEqual(final_position["avg_price"], expected_avg_price, places=2)
        self.assertGreater(final_position["amount"], initial_amount)
        
        print("✓ Position averaging test passed")
    
    def test_realized_vs_unrealized_pnl(self):
        """Test distinction between realized and unrealized P&L"""
        balance = self.test_balance.copy()
        
        # Open position
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.5, 1.0, None, None)
        
        # Check unrealized P&L at higher price
        current_prices = {"BTC": 65000.0, "SOL": 150.0}
        unrealized = self.trader.calculate_total_pnl(balance, current_prices)
        self.assertGreater(unrealized, 0)
        self.assertEqual(balance["realized_pnl"], 0)  # Nothing realized yet
        
        # Close position to realize profit
        initial_realized = balance["realized_pnl"]
        self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 65000.0, 1.0)
        
        # Check that profit was realized
        self.assertGreater(balance["realized_pnl"], initial_realized)
        
        # Check unrealized is now zero (no open positions)
        unrealized_after = self.trader.calculate_total_pnl(balance, current_prices)
        self.assertEqual(unrealized_after, 0)
        
        print("✓ Realized vs unrealized P&L test passed")
    
    def test_balance_consistency(self):
        """Test balance consistency through complex trading sequence"""
        balance = self.test_balance.copy()
        initial_total = balance["margin"]["available"] + balance["margin"]["used"]
        
        # Complex sequence of trades
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.3, 1.0, None, None)
        self.trader.execute_trade(balance, "SELL_SHORT", "SOL", 150.0, 0.2, 1.0, None, None)
        self.trader.execute_trade(balance, "BUY", "BTC", 61000.0, 0.1)  # Legacy
        self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 62000.0, 0.5)
        self.trader.execute_trade(balance, "SELL", "BTC", 63000.0, 1.0)  # Legacy
        
        # Check that total value is conserved (plus/minus P&L)
        # For mixed margin/legacy trades, account for USD changes from legacy trades
        current_total = balance["margin"]["available"] + balance["margin"]["used"] + (balance["USD"] - 10000.0)
        total_change = current_total - initial_total
        
        # Total change should equal realized P&L
        self.assertAlmostEqual(total_change, balance["realized_pnl"], places=2)
        
        print("✓ Balance consistency test passed")
    
    def test_edge_case_tiny_amounts(self):
        """Test handling of very small amounts"""
        balance = self.test_balance.copy()
        
        # Trade tiny amount
        self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.001, 1.0, None, None)
        
        # Check position was created
        btc_position = balance["positions"]["BTC"]["long"]
        self.assertGreater(btc_position["amount"], 0)
        self.assertLess(btc_position["amount"], 0.001)  # Should be very small
        
        # Close tiny position
        self.trader.execute_trade(balance, "CLOSE_LONG", "BTC", 65000.0, 1.0)
        
        # Should handle tiny P&L correctly
        self.assertGreaterEqual(balance["realized_pnl"], 0)
        
        print("✓ Edge case tiny amounts test passed")
    
    def test_zero_percent_trades(self):
        """Test handling of zero percent trades"""
        balance = self.test_balance.copy()
        
        # Try 0% trade
        success = self.trader.execute_trade(balance, "BUY_LONG", "BTC", 60000.0, 0.0, 1.0, None, None)
        
        # Should succeed but do nothing
        self.assertTrue(success)
        self.assertEqual(balance["positions"]["BTC"]["long"]["amount"], 0)
        self.assertEqual(balance["margin"]["used"], 0)
        
        print("✓ Zero percent trades test passed")

class TestLegacyTraderCompatibility(BaseTestCase):
    """Test compatibility with legacy trader functions"""
    
    def test_legacy_calc_unrealized_pnl(self):
        """Test legacy calc_unrealized_pnl function"""
        balance = {
            "coins": {
                "BTC": {"amount": 0.5, "avg_price": 58000.0},
                "SOL": {"amount": 20.0, "avg_price": 160.0}
            }
        }
        
        current_prices = {"BTC": 62000.0, "SOL": 155.0}
        
        # Test the legacy function
        unrealized = calc_unrealized_pnl(balance, current_prices)
        
        # BTC: (62000 - 58000) * 0.5 = 2000
        # SOL: (155 - 160) * 20 = -100
        # Total: 1900
        expected = 1900.0
        self.assertEqual(unrealized, expected)
        
        print("✓ Legacy calc_unrealized_pnl test passed")
    
    def test_legacy_with_missing_coins(self):
        """Test legacy function with missing price data"""
        balance = {
            "coins": {
                "BTC": {"amount": 0.1, "avg_price": 60000.0},
                "ETH": {"amount": 2.0, "avg_price": 3000.0}  # Not in current_prices
            }
        }
        
        current_prices = {"BTC": 65000.0}  # Missing ETH
        
        unrealized = calc_unrealized_pnl(balance, current_prices)
        
        # Only BTC should be calculated: (65000 - 60000) * 0.1 = 500
        expected = 500.0
        self.assertEqual(unrealized, expected)
        
        print("✓ Legacy with missing coins test passed")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)