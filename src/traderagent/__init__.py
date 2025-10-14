"""
TraderAgent Package
A sophisticated cryptocurrency trading bot with AI decision making
"""

__version__ = "1.0.0"
__author__ = "TraderAgent"

from .ai_decision import get_ai_decision, get_ai_decision_with_volume
from .advanced_trader import AdvancedTrader
from .data_fetcher import (
    get_all_price_histories, 
    get_price_history,
    get_all_price_and_volume_histories,
    get_price_and_volume_history,
    get_volume_analysis
)
from .trader import load_balance, save_balance, calc_unrealized_pnl

__all__ = [
    'get_ai_decision',
    'get_ai_decision_with_volume',
    'AdvancedTrader', 
    'get_all_price_histories',
    'get_price_history',
    'get_all_price_and_volume_histories',
    'get_price_and_volume_history',
    'get_volume_analysis',
    'load_balance',
    'save_balance',
    'calc_unrealized_pnl'
]