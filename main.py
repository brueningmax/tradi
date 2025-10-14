#!/usr/bin/env python3
"""
TraderAgent Main Entry Point
"""

import sys
import argparse
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from traderagent.data_fetcher import get_all_price_histories, get_all_price_and_volume_histories
from traderagent.advanced_trader import AdvancedTrader
from traderagent.ai_decision import get_ai_decision, get_ai_decision_with_volume
from traderagent.config import TradingConfig

def run_backtest(paper_trading=False, use_volume=True):
    """Run backtesting mode"""
    mode_text = "paper trading" if paper_trading else "live"
    volume_text = "with volume analysis" if use_volume else "price-only"
    print(f"=== Starting {mode_text} backtest ({volume_text}) ===")
    
    # Create configuration
    config = TradingConfig(paper_trading=paper_trading)
    trader = AdvancedTrader(paper_trading=paper_trading)
    
    # Update trader to use correct paths
    trader.balance_file = config.get_balance_file_path()
    
    balance = trader.load_balance()
    
    # Get market data with or without volume
    if use_volume:
        market_data = get_all_price_and_volume_histories()
        print("Fetching price and volume data...")
    else:
        price_data = get_all_price_histories()
        print("Fetching price data only...")
    
    # Advanced backtest
    if use_volume:
        length = len(next(iter(market_data.values())))
    else:
        length = len(next(iter(price_data.values())))
    total_runs = length - 30

    for i in range(30, length):
        if use_volume:
            # Slice the market history up to this point
            sliced_history = {coin: data[:i] for coin, data in market_data.items()}
            current_prices = {coin: data[i][1] for coin, data in market_data.items()}
            
            # Get AI decision with volume analysis
            decisions = get_ai_decision_with_volume(sliced_history, balance)
        else:
            # Slice the price history up to this point
            sliced_history = {coin: data[:i] for coin, data in price_data.items()}
            current_prices = {coin: data[i][1] for coin, data in price_data.items()}
            
            # Get AI decision with price only
            decisions = get_ai_decision(sliced_history, balance)

        # Check stop losses and take profits
        trader.check_stop_losses_and_take_profits(balance, current_prices)

        for coin, decision_data in decisions.items():
            if coin in current_prices:
                current_price = current_prices[coin]
                
                if len(decision_data) == 5:  # Advanced position
                    action, percent, leverage, stop_loss, take_profit = decision_data
                    trader.execute_trade(balance, action, coin, current_price, percent, leverage, stop_loss, take_profit)
                
                elif len(decision_data) == 2:  # Simple action
                    action, percent = decision_data
                    trader.execute_trade(balance, action, coin, current_price, percent)

        # Progress bar
        completed = i - 30 + 1
        bar_length = 30
        filled = int((completed / total_runs) * bar_length)
        bar = "#" * filled + "_" * (bar_length - filled)
        print(f"\r[{bar}] {completed}/{total_runs}", end="")

    print()  # New line after progress bar
    
    trader.save_balance(balance)
    current_prices = {coin: data[-1][1] for coin, data in price_data.items()}
    
    print(f"Final Available Margin: ${balance['margin']['available']:.2f}")
    print(f"Realized P&L: ${balance['realized_pnl']:.2f}")
    total_pnl = trader.calculate_total_pnl(balance, current_prices)
    print(f"Total Unrealized P&L: ${total_pnl:.2f}")
    print(f"=== {mode_text.title()} backtest complete ===")

def run_live(paper_trading=False, use_volume=True):
    """Run live trading mode"""
    import os
    import datetime
    
    mode_text = "paper trading" if paper_trading else "live"
    volume_text = "with volume analysis" if use_volume else "price-only"
    
    # Enhanced logging for CI/CD
    print(f"🤖 === TraderAgent Execution ===")
    print(f"📅 Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Mode: {mode_text} ({volume_text})")
    print(f"🌍 Environment: {'CI/CD' if os.getenv('GITHUB_ACTIONS') else 'Local'}")
    print("=" * 50)
    
    # Create configuration
    config = TradingConfig(paper_trading=paper_trading)
    trader = AdvancedTrader(paper_trading=paper_trading)
    
    # Update trader to use correct paths
    trader.balance_file = config.get_balance_file_path()
    
    # Get market data with or without volume
    print("📊 Fetching market data...")
    if use_volume:
        market_data = get_all_price_and_volume_histories()
        current_prices = {coin: history[-1][1] for coin, history in market_data.items()}
        print("✅ Using price and volume data for AI decisions")
    else:
        price_histories = get_all_price_histories()
        current_prices = {coin: history[-1][1] for coin, history in price_histories.items()}
        print("✅ Using price data only for AI decisions")
    
    # Display current market prices
    print("\n💰 Current Market Prices:")
    for coin, price in current_prices.items():
        print(f"  {coin}: ${price:,.2f}")
    print()
    
    balance = trader.load_balance()
    
    # Display current balance
    print("💳 Current Balance:")
    print(f"  USD: ${balance['USD']:,.2f}")
    print(f"  Available Margin: ${balance['margin']['available']:,.2f}")
    print(f"  Used Margin: ${balance['margin']['used']:,.2f}")
    print(f"  Realized P&L: ${balance['realized_pnl']:,.2f}")
    
    # Show current positions
    has_positions = False
    for coin in current_prices.keys():
        long_pos = balance["positions"][coin]["long"]
        short_pos = balance["positions"][coin]["short"]
        if long_pos["amount"] > 0 or short_pos["amount"] > 0:
            if not has_positions:
                print("\n📈 Current Positions:")
                has_positions = True
            if long_pos["amount"] > 0:
                print(f"  {coin} LONG: {long_pos['amount']:.6f} @ ${long_pos['avg_price']:,.2f}")
            if short_pos["amount"] > 0:
                print(f"  {coin} SHORT: {short_pos['amount']:.6f} @ ${short_pos['avg_price']:,.2f}")
    
    if not has_positions:
        print("\n📈 No open positions")
    print()

    # Check for stop losses and take profits first
    print("🔍 Checking stop losses and take profits...")
    initial_pnl = balance['realized_pnl']
    trader.check_stop_losses_and_take_profits(balance, current_prices)
    
    if balance['realized_pnl'] != initial_pnl:
        pnl_change = balance['realized_pnl'] - initial_pnl
        print(f"💫 Stop loss/take profit triggered! P&L change: ${pnl_change:,.2f}")
    else:
        print("✅ No stop losses or take profits triggered")

    # Get AI decision with or without volume
    print("\n🧠 Getting AI trading decision...")
    if use_volume:
        decisions = get_ai_decision_with_volume(market_data, balance)
    else:
        decisions = get_ai_decision(price_histories, balance)

    print(f"\n🎯 AI Decisions:")
    trades_executed = False
    for coin, decision_data in decisions.items():
        if coin in current_prices:
            current_price = current_prices[coin]
            
            if len(decision_data) == 5:  # Advanced position
                action, percent, leverage, stop_loss, take_profit = decision_data
                print(f"  {coin}: {action} {int(percent * 100)}%", end="")
                if stop_loss:
                    print(f" [SL: ${stop_loss:,.2f}]", end="")
                if take_profit:
                    print(f" [TP: ${take_profit:,.2f}]", end="")
                print()
                
                success = trader.execute_trade(balance, action, coin, current_price, percent, leverage, stop_loss, take_profit)
                if success:
                    trades_executed = True
            
            elif len(decision_data) == 2:  # Simple action
                action, percent = decision_data
                print(f"  {coin}: {action} {int(percent * 100)}%")
                success = trader.execute_trade(balance, action, coin, current_price, percent)
                if success:
                    trades_executed = True

    if not trades_executed:
        print("  No trades executed this round")
    
    print()
    trader.save_balance(balance)
    # Final summary
    final_balance = trader.load_balance()  # Reload to get latest state
    total_pnl = trader.calculate_total_pnl(final_balance, current_prices)
    
    print("=" * 50)
    print("📊 EXECUTION SUMMARY")
    print("=" * 50)
    print(f"💰 Final USD Balance: ${final_balance['USD']:,.2f}")
    print(f"📈 Realized P&L: ${final_balance['realized_pnl']:,.2f}")
    print(f"📊 Unrealized P&L: ${total_pnl:,.2f}")
    print(f"🎯 Total P&L: ${final_balance['realized_pnl'] + total_pnl:,.2f}")
    print(f"📅 Completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Show recent trades
    recent_trades = final_balance.get('history', [])[-3:]  # Last 3 trades
    if recent_trades:
        print(f"\n🔄 Recent Trades:")
        for trade in recent_trades:
            print(f"  • {trade}")
    
    print("=" * 50)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='TraderAgent - AI-powered cryptocurrency trading bot')
    
    parser.add_argument("--backtest", action="store_true", help="Run in backtest mode")
    parser.add_argument("--paper", action="store_true", help="Use paper trading (simulation mode)")
    parser.add_argument("--live", action="store_true", help="Use live trading - BE CAREFUL!")
    parser.add_argument("--no-volume", action="store_true", help="Disable volume analysis (price-only trading)")
    
    args = parser.parse_args()
    
    # Determine trading mode - default to paper trading for safety
    if args.live and args.paper:
        print("Error: Cannot specify both --live and --paper")
        sys.exit(1)
    
    paper_trading = not args.live  # Default to paper trading unless --live specified
    use_volume = not args.no_volume  # Default to using volume unless --no-volume specified
    
    if args.live:
        print("⚠️  WARNING: LIVE TRADING MODE ENABLED")
        print("  This will use real money. Are you sure?")
        
        # Check if running in CI/CD environment
        import os
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            print("  Running in CI/CD environment - proceeding automatically")
        else:
            response = input("Type 'YES' to continue with live trading: ")
            if response != "YES":
                print("Exiting for safety. Use --paper for simulation.")
                sys.exit(0)
    else:
        print("📊 Paper trading mode enabled (safe simulation)")
    
    # Run the appropriate mode
    try:
        if args.backtest:
            run_backtest(paper_trading, use_volume)
        else:
            run_live(paper_trading, use_volume)
    except KeyboardInterrupt:
        print("\n  Trading stopped by user")
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
