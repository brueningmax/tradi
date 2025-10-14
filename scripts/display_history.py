#!/usr/bin/env python3
"""
Script to display recent trading history for GitHub Actions summary
"""
import json
import os

def main():
    balance_file = "data/paper_balance.json"
    
    if not os.path.exists(balance_file):
        print("No balance file found")
        return
    
    try:
        with open(balance_file, 'r') as f:
            balance = json.load(f)
        
        # Get last 5 trades from history
        history = balance.get('history', [])
        recent_trades = history[-5:] if len(history) > 5 else history
        
        if not recent_trades:
            print("No recent trading history")
            return
        
        for trade in recent_trades:
            print(trade)
            
    except Exception as e:
        print(f"Error reading history: {e}")

if __name__ == "__main__":
    main()