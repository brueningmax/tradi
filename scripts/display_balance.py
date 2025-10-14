#!/usr/bin/env python3
"""
Script to display trading balance for GitHub Actions summary
"""
import json
import sys
import os

def main():
    balance_file = "data/paper_balance.json"
    
    if not os.path.exists(balance_file):
        print("No balance file found")
        return
    
    try:
        with open(balance_file, 'r') as f:
            balance = json.load(f)
        
        def r2(x):
            """Round to 2 decimal places safely"""
            try:
                return round(float(x), 2)
            except (ValueError, TypeError):
                return x
        
        def r6(x):
            """Round to 6 decimal places safely"""
            try:
                return round(float(x), 6)
            except (ValueError, TypeError):
                return x
        
        output = []
        output.append(f"USD: ${r2(balance.get('USD', 0))}")
        output.append(f"Realized P&L: ${r2(balance.get('realized_pnl', 0))}")
        
        # Margin info
        margin = balance.get('margin', {})
        output.append(f"Available Margin: ${r2(margin.get('available', 0))}")
        output.append(f"Used Margin: ${r2(margin.get('used', 0))}")
        
        # Position info
        positions = balance.get('positions', {})
        for coin in ['BTC', 'SOL']:
            coin_positions = positions.get(coin, {})
            long_pos = coin_positions.get('long', {})
            short_pos = coin_positions.get('short', {})
            
            if long_pos.get('amount', 0) > 0:
                amount = r6(long_pos.get('amount', 0))
                price = r2(long_pos.get('avg_price', 0))
                output.append(f"{coin} LONG: {amount} @ ${price}")
                
            if short_pos.get('amount', 0) > 0:
                amount = r6(short_pos.get('amount', 0))
                price = r2(short_pos.get('avg_price', 0))
                output.append(f"{coin} SHORT: {amount} @ ${price}")
        
        # Print all output
        for line in output:
            print(line)
            
    except Exception as e:
        print(f"Error reading balance: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()