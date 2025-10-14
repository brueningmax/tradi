import requests
from datetime import datetime

def get_price_history(symbol="BTCUSDT", interval="1h", limit=72):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    prices = [float(entry[4]) for entry in data]
    timestamps = [datetime.fromtimestamp(entry[0] / 1000).strftime('%Y-%m-%d %H:%M') for entry in data]
    return list(zip(timestamps, prices))

def get_price_and_volume_history(symbol="BTCUSDT", interval="1h", limit=72):
    """Get price and volume history for a symbol"""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Extract prices (close price) and volumes
    prices = [float(entry[4]) for entry in data]  # Close price
    volumes = [float(entry[5]) for entry in data]  # Volume
    timestamps = [datetime.fromtimestamp(entry[0] / 1000).strftime('%Y-%m-%d %H:%M') for entry in data]
    
    return list(zip(timestamps, prices, volumes))

def get_all_price_histories():
    return {
        "BTC": get_price_history("BTCUSDT"),
        "SOL": get_price_history("SOLUSDT")
    }

def get_all_price_and_volume_histories():
    """Get price and volume histories for all supported coins"""
    return {
        "BTC": get_price_and_volume_history("BTCUSDT"),
        "SOL": get_price_and_volume_history("SOLUSDT")
    }

def get_volume_analysis(volumes):
    """Analyze volume data to provide trading insights"""
    if len(volumes) < 2:
        return "Insufficient volume data"
    
    # Calculate recent volume metrics
    recent_vol = volumes[-5:]  # Last 5 periods
    older_vol = volumes[-20:-5] if len(volumes) >= 20 else volumes[:-5]  # Previous periods
    
    avg_recent = sum(recent_vol) / len(recent_vol)
    avg_older = sum(older_vol) / len(older_vol) if older_vol else avg_recent
    
    # Volume trend analysis
    if avg_recent > avg_older * 1.5:
        return "HIGH (significantly above average)"
    elif avg_recent > avg_older * 1.2:
        return "ELEVATED (above average)"
    elif avg_recent < avg_older * 0.7:
        return "LOW (below average)"
    else:
        return "NORMAL (average levels)"
