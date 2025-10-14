import json
from typing import Dict, Optional, Tuple

class AdvancedTrader:
    """Advanced trading system supporting various position types and risk management"""
    
    def __init__(self, paper_trading=False):
        self.paper_trading = paper_trading
        self.balance_file = "paper_balance.json" if paper_trading else "balance.json"
    
    def load_balance(self) -> Dict:
        """Load balance from file"""
        with open(self.balance_file, "r") as f:
            return json.load(f)
    
    def save_balance(self, balance: Dict):
        """Save balance to file"""
        with open(self.balance_file, "w") as f:
            json.dump(balance, f, indent=2)
    
    def execute_trade(self, balance: Dict, action: str, coin: str, current_price: float, 
                     percent: float, leverage: float = 1.0, stop_loss: Optional[float] = None,
                     take_profit: Optional[float] = None) -> bool:
        """Execute trading positions - NO LEVERAGE ALLOWED"""
        
        # Force leverage to 1.0 - no leverage allowed
        if leverage != 1.0:
            print(f"WARNING: Leverage {leverage} not allowed. Setting to 1.0 (no leverage)")
            leverage = 1.0
        
        mode_text = "[PAPER]" if self.paper_trading else "[LIVE]"
        
        if action == "BUY_LONG":
            return self._open_long_position(balance, coin, current_price, percent, leverage, 
                                          stop_loss, take_profit, mode_text)
        
        elif action == "SELL_SHORT":
            return self._open_short_position(balance, coin, current_price, percent, leverage,
                                           stop_loss, take_profit, mode_text)
        
        elif action == "CLOSE_LONG":
            return self._close_long_position(balance, coin, current_price, percent, mode_text)
        
        elif action == "CLOSE_SHORT":
            return self._close_short_position(balance, coin, current_price, percent, mode_text)
        
        elif action == "BUY":  # Legacy support
            return self._simple_buy(balance, coin, current_price, percent, mode_text)
        
        elif action == "SELL":  # Legacy support
            return self._simple_sell(balance, coin, current_price, percent, mode_text)
        
        elif action == "HOLD":
            balance["history"].append(f"{mode_text} HELD {coin} at {current_price}")
            print(f"{mode_text} HELD {coin} at {current_price}")
            return True
        
        return False
    
    def _open_long_position(self, balance: Dict, coin: str, price: float, percent: float,
                           leverage: float, stop_loss: Optional[float], take_profit: Optional[float],
                           mode_text: str) -> bool:
        """Open a long position (NO LEVERAGE - 1:1 only)"""
        
        # Ensure no leverage
        leverage = 1.0
        
        available_margin = balance["margin"]["available"]
        if available_margin <= 0:
            print(f"{mode_text} No available funds for long position")
            return False
        
        # Calculate position size (no leverage amplification)
        margin_to_use = available_margin * percent
        position_value = margin_to_use  # No leverage multiplication
        amount = position_value / price
        
        # Update position
        position = balance["positions"][coin]["long"]
        if position["amount"] > 0:
            # Add to existing position (average price)
            total_value = position["amount"] * position["avg_price"] + position_value
            total_amount = position["amount"] + amount
            position["avg_price"] = total_value / total_amount
            position["amount"] = total_amount
        else:
            position["amount"] = amount
            position["avg_price"] = price
        
        position["stop_loss"] = stop_loss
        position["take_profit"] = take_profit
        
        # Update margin
        balance["margin"]["used"] += margin_to_use
        balance["margin"]["available"] -= margin_to_use
        
        trade_msg = f"{mode_text} OPENED LONG {amount:.6f} {coin} at {price} (Margin: ${margin_to_use:.2f})"
        if stop_loss:
            trade_msg += f" [SL: {stop_loss}]"
        if take_profit:
            trade_msg += f" [TP: {take_profit}]"
        
        balance["history"].append(trade_msg)
        print(trade_msg)
        return True
    
    def _open_short_position(self, balance: Dict, coin: str, price: float, percent: float,
                            leverage: float, stop_loss: Optional[float], take_profit: Optional[float],
                            mode_text: str) -> bool:
        """Open a short position (NO LEVERAGE - 1:1 only)"""
        
        # Ensure no leverage
        leverage = 1.0
        
        available_margin = balance["margin"]["available"]
        if available_margin <= 0:
            print(f"{mode_text} No available funds for short position")
            return False
        
        # Calculate position size (no leverage amplification)
        margin_to_use = available_margin * percent
        position_value = margin_to_use  # No leverage multiplication
        amount = position_value / price
        
        # Update position
        position = balance["positions"][coin]["short"]
        if position["amount"] > 0:
            # Add to existing position (average price)
            total_value = position["amount"] * position["avg_price"] + position_value
            total_amount = position["amount"] + amount
            position["avg_price"] = total_value / total_amount
            position["amount"] = total_amount
        else:
            position["amount"] = amount
            position["avg_price"] = price
        
        position["stop_loss"] = stop_loss
        position["take_profit"] = take_profit
        
        # Update margin
        balance["margin"]["used"] += margin_to_use
        balance["margin"]["available"] -= margin_to_use
        
        trade_msg = f"{mode_text} OPENED SHORT {amount:.6f} {coin} at {price} (Margin: ${margin_to_use:.2f})"
        if stop_loss:
            trade_msg += f" [SL: {stop_loss}]"
        if take_profit:
            trade_msg += f" [TP: {take_profit}]"
        
        balance["history"].append(trade_msg)
        print(trade_msg)
        return True
    
    def _close_long_position(self, balance: Dict, coin: str, price: float, percent: float, mode_text: str) -> bool:
        """Close long position (full or partial)"""
        
        position = balance["positions"][coin]["long"]
        if position["amount"] <= 0:
            print(f"{mode_text} No long position to close for {coin}")
            return False
        
        amount_to_close = position["amount"] * percent
        avg_price = position["avg_price"]
        
        # Calculate P&L (no leverage amplification)
        price_diff = price - avg_price
        pnl = price_diff * amount_to_close  # No leverage multiplication
        
        # Calculate margin to release
        position_value = amount_to_close * avg_price
        margin_to_release = position_value  # No leverage division
        
        # Update position
        position["amount"] -= amount_to_close
        if position["amount"] <= 0:
            position["amount"] = 0
            position["avg_price"] = 0
            position["stop_loss"] = None
            position["take_profit"] = None
        
        # Update margin and balance
        balance["margin"]["used"] -= margin_to_release
        balance["margin"]["available"] += margin_to_release + pnl
        balance["realized_pnl"] += pnl
        
        trade_msg = f"{mode_text} CLOSED LONG {amount_to_close:.6f} {coin} at {price} (P&L: ${pnl:.2f})"
        balance["history"].append(trade_msg)
        print(trade_msg)
        return True
    
    def _close_short_position(self, balance: Dict, coin: str, price: float, percent: float, mode_text: str) -> bool:
        """Close short position (full or partial)"""
        
        position = balance["positions"][coin]["short"]
        if position["amount"] <= 0:
            print(f"{mode_text} No short position to close for {coin}")
            return False
        
        amount_to_close = position["amount"] * percent
        avg_price = position["avg_price"]
        
        # Calculate P&L (no leverage amplification - inverse for short)
        price_diff = avg_price - price
        pnl = price_diff * amount_to_close  # No leverage multiplication
        
        # Calculate margin to release
        position_value = amount_to_close * avg_price
        margin_to_release = position_value  # No leverage division
        
        # Update position
        position["amount"] -= amount_to_close
        if position["amount"] <= 0:
            position["amount"] = 0
            position["avg_price"] = 0
            position["stop_loss"] = None
            position["take_profit"] = None
        
        # Update margin and balance
        balance["margin"]["used"] -= margin_to_release
        balance["margin"]["available"] += margin_to_release + pnl
        balance["realized_pnl"] += pnl
        
        trade_msg = f"{mode_text} CLOSED SHORT {amount_to_close:.6f} {coin} at {price} (P&L: ${pnl:.2f})"
        balance["history"].append(trade_msg)
        print(trade_msg)
        return True
    
    def _simple_buy(self, balance: Dict, coin: str, price: float, percent: float, mode_text: str) -> bool:
        """Legacy simple buy (spot trading)"""
        if balance["USD"] <= 0 or percent <= 0:
            return False
        
        usd_to_spend = balance["USD"] * percent
        amount = usd_to_spend / price
        
        balance["coins"][coin]["amount"] += amount
        balance["coins"][coin]["avg_price"] = price
        balance["USD"] -= usd_to_spend
        
        trade_msg = f"{mode_text} BOUGHT {amount:.6f} {coin} at {price} using {percent*100:.0f}% of USD"
        balance["history"].append(trade_msg)
        print(trade_msg)
        return True
    
    def _simple_sell(self, balance: Dict, coin: str, price: float, percent: float, mode_text: str) -> bool:
        """Legacy simple sell (spot trading)"""
        if balance["coins"][coin]["amount"] <= 0 or percent <= 0:
            return False
        
        amount_to_sell = balance["coins"][coin]["amount"] * percent
        avg_price = balance["coins"][coin]["avg_price"]
        pnl = (price - avg_price) * amount_to_sell
        
        balance["USD"] += amount_to_sell * price
        balance["coins"][coin]["amount"] -= amount_to_sell
        
        if balance["coins"][coin]["amount"] <= 0:
            balance["coins"][coin]["avg_price"] = 0
        
        balance["realized_pnl"] += pnl
        
        trade_msg = f"{mode_text} SOLD {amount_to_sell:.6f} {coin} at {price} (P&L: ${pnl:.2f})"
        balance["history"].append(trade_msg)
        print(trade_msg)
        return True
    
    def check_stop_losses_and_take_profits(self, balance: Dict, current_prices: Dict[str, float]):
        """Check and execute stop losses and take profits"""
        
        for coin, price in current_prices.items():
            # Check long positions
            long_pos = balance["positions"][coin]["long"]
            if long_pos["amount"] > 0:
                if long_pos["stop_loss"] and price <= long_pos["stop_loss"]:
                    print(f"Stop loss triggered for {coin} long position at {price}")
                    self._close_long_position(balance, coin, price, 1.0, "[STOP LOSS]")
                elif long_pos["take_profit"] and price >= long_pos["take_profit"]:
                    print(f"Take profit triggered for {coin} long position at {price}")
                    self._close_long_position(balance, coin, price, 1.0, "[TAKE PROFIT]")
            
            # Check short positions
            short_pos = balance["positions"][coin]["short"]
            if short_pos["amount"] > 0:
                if short_pos["stop_loss"] and price >= short_pos["stop_loss"]:
                    print(f"Stop loss triggered for {coin} short position at {price}")
                    self._close_short_position(balance, coin, price, 1.0, "[STOP LOSS]")
                elif short_pos["take_profit"] and price <= short_pos["take_profit"]:
                    print(f"Take profit triggered for {coin} short position at {price}")
                    self._close_short_position(balance, coin, price, 1.0, "[TAKE PROFIT]")
    
    def calculate_total_pnl(self, balance: Dict, current_prices: Dict[str, float]) -> float:
        """Calculate total unrealized P&L from all positions"""
        total_unrealized = 0.0
        
        for coin, price in current_prices.items():
            # Long positions (no leverage)
            long_pos = balance["positions"][coin]["long"]
            if long_pos["amount"] > 0:
                pnl = (price - long_pos["avg_price"]) * long_pos["amount"]  # No leverage
                total_unrealized += pnl
            
            # Short positions (no leverage)
            short_pos = balance["positions"][coin]["short"]
            if short_pos["amount"] > 0:
                pnl = (short_pos["avg_price"] - price) * short_pos["amount"]  # No leverage
                total_unrealized += pnl
            
            # Spot holdings (legacy)
            if balance["coins"][coin]["amount"] > 0:
                pnl = (price - balance["coins"][coin]["avg_price"]) * balance["coins"][coin]["amount"]
                total_unrealized += pnl
        
        return round(total_unrealized, 2)
    
    def get_position_summary(self, balance: Dict, current_prices: Dict[str, float]) -> str:
        """Get a formatted summary of all positions"""
        summary = []
        
        for coin in balance["positions"].keys():
            price = current_prices.get(coin, 0)
            
            # Long position
            long_pos = balance["positions"][coin]["long"]
            if long_pos["amount"] > 0:
                pnl = (price - long_pos["avg_price"]) * long_pos["amount"]  # No leverage
                summary.append(f"{coin} LONG: {long_pos['amount']:.6f} @ {long_pos['avg_price']:.2f} "
                             f"(P&L: ${pnl:.2f})")
            
            # Short position
            short_pos = balance["positions"][coin]["short"]
            if short_pos["amount"] > 0:
                pnl = (short_pos["avg_price"] - price) * short_pos["amount"]  # No leverage
                summary.append(f"{coin} SHORT: {short_pos['amount']:.6f} @ {short_pos['avg_price']:.2f} "
                             f"(P&L: ${pnl:.2f})")
        
        return "\n".join(summary) if summary else "No open positions"