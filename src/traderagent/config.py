"""
Configuration settings for TraderAgent
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_DIR = PROJECT_ROOT / "config"
TESTS_DIR = PROJECT_ROOT / "tests"

# Data file paths
BALANCE_FILE = DATA_DIR / "balance.json"
PAPER_BALANCE_FILE = DATA_DIR / "paper_balance.json"

# Trading configuration
DEFAULT_COINS = ["BTC", "SOL"]
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

# AI configuration
DEFAULT_AI_MODEL = "gpt-5"
DEFAULT_AI_TEMPERATURE = 0

# Trading limits
MAX_LEVERAGE = 1.0  # No leverage allowed
DEFAULT_INTERVAL = "1h"
DEFAULT_PRICE_LIMIT = 72  # Hours of price history

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class TradingConfig:
    """Trading configuration class"""
    
    def __init__(self, paper_trading=True):
        self.paper_trading = paper_trading
        self.balance_file = PAPER_BALANCE_FILE if paper_trading else BALANCE_FILE
        self.coins = DEFAULT_COINS.copy()
        self.max_leverage = MAX_LEVERAGE
        self.ai_model = DEFAULT_AI_MODEL
        self.ai_temperature = DEFAULT_AI_TEMPERATURE
        
    def get_balance_file_path(self):
        """Get the appropriate balance file path"""
        return str(self.balance_file)
    
    def is_paper_trading(self):
        """Check if in paper trading mode"""
        return self.paper_trading
    
    def get_supported_coins(self):
        """Get list of supported coins"""
        return self.coins.copy()
    
    def validate_config(self):
        """Validate configuration"""
        errors = []
        
        if not OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY environment variable not set")
        
        if not DATA_DIR.exists():
            errors.append(f"Data directory does not exist: {DATA_DIR}")
        
        return errors

# Default configuration instances
PAPER_CONFIG = TradingConfig(paper_trading=True)
LIVE_CONFIG = TradingConfig(paper_trading=False)