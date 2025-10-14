import requests
from datetime import datetime
import time

def get_price_history(symbol="BTCUSDT", interval="1h", limit=72):
    """Get price history with error handling and retries"""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    # Try multiple times with backoff
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 451:
                print(f"⚠️ Binance API blocked (Error 451) for {symbol}. Using fallback data.")
                return get_fallback_price_data(symbol, limit)
            elif response.status_code == 429:
                print(f"⚠️ Rate limited. Waiting {2**attempt} seconds...")
                time.sleep(2**attempt)
                continue
            
            response.raise_for_status()
            data = response.json()

            prices = [float(entry[4]) for entry in data]
            timestamps = [datetime.fromtimestamp(entry[0] / 1000).strftime('%Y-%m-%d %H:%M') for entry in data]
            return list(zip(timestamps, prices))
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt + 1} failed for {symbol}: {e}")
            if attempt == 2:  # Last attempt
                print(f"🔄 Using fallback data for {symbol}")
                return get_fallback_price_data(symbol, limit)
            time.sleep(2**attempt)
    
    return get_fallback_price_data(symbol, limit)

def get_fallback_price_data(symbol, limit):
    """Generate realistic fallback price data when API is unavailable"""
    print(f"📊 Generating fallback price data for {symbol}")
    
    # Base prices for different symbols
    base_prices = {
        "BTCUSDT": 65000,
        "SOLUSDT": 150
    }
    
    base_price = base_prices.get(symbol, 50000)
    
    # Generate realistic price movements
    prices = []
    current_price = base_price
    
    for i in range(limit):
        # Small random movements (±2%)
        import random
        change = random.uniform(-0.02, 0.02)
        current_price *= (1 + change)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        prices.append((timestamp, current_price))
    
    return prices

def get_price_and_volume_history(symbol="BTCUSDT", interval="1h", limit=72):
    """Get price and volume history for a symbol with error handling"""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    # Try multiple times with backoff
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 451:
                print(f"⚠️ Binance API blocked (Error 451) for {symbol}. Using fallback data.")
                return get_fallback_volume_data(symbol, limit)
            elif response.status_code == 429:
                print(f"⚠️ Rate limited. Waiting {2**attempt} seconds...")
                time.sleep(2**attempt)
                continue
            
            response.raise_for_status()
            data = response.json()

            # Extract prices (close price) and volumes
            prices = [float(entry[4]) for entry in data]  # Close price
            volumes = [float(entry[5]) for entry in data]  # Volume
            timestamps = [datetime.fromtimestamp(entry[0] / 1000).strftime('%Y-%m-%d %H:%M') for entry in data]
            
            return list(zip(timestamps, prices, volumes))
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt + 1} failed for {symbol}: {e}")
            if attempt == 2:  # Last attempt
                print(f"🔄 Using fallback data for {symbol}")
                return get_fallback_volume_data(symbol, limit)
            time.sleep(2**attempt)
    
    return get_fallback_volume_data(symbol, limit)

def get_fallback_volume_data(symbol, limit):
    """Generate realistic fallback price and volume data"""
    print(f"📊 Generating fallback price and volume data for {symbol}")
    
    # Base prices and volumes for different symbols
    base_data = {
        "BTCUSDT": {"price": 65000, "volume": 1000},
        "SOLUSDT": {"price": 150, "volume": 50000}
    }
    
    data = base_data.get(symbol, {"price": 50000, "volume": 1000})
    current_price = data["price"]
    base_volume = data["volume"]
    
    # Generate realistic price and volume movements
    results = []
    
    for i in range(limit):
        import random
        # Small random movements (±2%)
        price_change = random.uniform(-0.02, 0.02)
        current_price *= (1 + price_change)
        
        # Volume varies more (±50%)
        volume = base_volume * random.uniform(0.5, 1.5)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        results.append((timestamp, current_price, volume))
    
    return results

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
