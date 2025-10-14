"""
Balance persistence utilities for TraderAgent
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, Optional

class BalancePersistence:
    """Handle balance persistence across different environments"""
    
    def __init__(self, paper_trading: bool = True):
        self.paper_trading = paper_trading
        self.is_github_actions = bool(os.getenv('GITHUB_ACTIONS'))
        
        # File paths
        self.local_balance_file = Path("data/paper_balance.json" if paper_trading else "data/balance.json")
        
    def load_balance(self) -> Dict:
        """Load balance with fallback strategies"""
        
        # First try local file
        if self.local_balance_file.exists():
            print(f"📁 Loading balance from {self.local_balance_file}")
            with open(self.local_balance_file, 'r') as f:
                return json.load(f)
        
        # Fallback to default balance
        print("⚠️ Balance file not found, using default balance")
        return self._get_default_balance()
    
    def save_balance(self, balance: Dict) -> bool:
        """Save balance with persistence strategy"""
        
        # Always save locally first
        self.local_balance_file.parent.mkdir(exist_ok=True)
        with open(self.local_balance_file, 'w') as f:
            json.dump(balance, f, indent=2)
        
        print(f"💾 Balance saved to {self.local_balance_file}")
        
        # In GitHub Actions, the git commit will handle persistence
        if self.is_github_actions:
            print("🤖 Running in GitHub Actions - balance will be committed automatically")
        
        return True
    
    def _get_default_balance(self) -> Dict:
        """Get default starting balance"""
        return {
            "USD": 10000.0 if self.paper_trading else 1000.0,
            "coins": {
                "BTC": {"amount": 0.0, "avg_price": 0.0},
                "SOL": {"amount": 0.0, "avg_price": 0.0}
            },
            "positions": {
                "BTC": {
                    "long": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None},
                    "short": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None}
                },
                "SOL": {
                    "long": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None},
                    "short": {"amount": 0.0, "avg_price": 0.0, "stop_loss": None, "take_profit": None}
                }
            },
            "margin": {
                "available": 10000.0 if self.paper_trading else 1000.0,
                "used": 0.0
            },
            "history": [],
            "realized_pnl": 0.0,
            "paper_trading": self.paper_trading
        }
    
    def get_balance_summary(self, balance: Dict) -> str:
        """Get formatted balance summary for logging"""
        return f"""
💰 Balance Summary:
  USD: ${balance['USD']:,.2f}
  Available Margin: ${balance['margin']['available']:,.2f} 
  Used Margin: ${balance['margin']['used']:,.2f}
  Realized P&L: ${balance['realized_pnl']:,.2f}
  Total Trades: {len(balance.get('history', []))}
        """.strip()