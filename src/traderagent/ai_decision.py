import openai
from dotenv import load_dotenv
import os
from .data_fetcher import get_volume_analysis

# Load .env file
load_dotenv()

# Load the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

def get_ai_decision(price_histories, balance):
    """Legacy function for backward compatibility - calls new function with volume data"""
    # Convert price histories to price+volume format with empty volume data
    price_volume_histories = {}
    for coin, history in price_histories.items():
        # Convert (timestamp, price) to (timestamp, price, volume=0)
        price_volume_histories[coin] = [(t, p, 0) for t, p in history]
    
    return get_ai_decision_with_volume(price_volume_histories, balance)

def get_ai_decision_with_volume(price_volume_histories, balance):
    """Enhanced AI decision making with volume analysis"""
    # Format price and volume data for AI
    market_analysis = []
    for coin, history in price_volume_histories.items():
        # Extract price and volume data
        prices = [p for _, p, _ in history]
        volumes = [v for _, _, v in history if v > 0]  # Filter out zero volumes
        
        # Price trend
        price_text = f"{coin} price trend (1h intervals, past 3 days):\n{[(t, round(p, 2)) for t, p, _ in history]}"
        
        # Volume analysis (only if we have real volume data)
        volume_text = ""
        if volumes and sum(volumes) > 0:  # Check if we have meaningful volume data
            volume_analysis = get_volume_analysis(volumes)
            recent_volumes = volumes[-5:] if len(volumes) >= 5 else volumes
            volume_text = f"\n{coin} volume analysis: {volume_analysis}\nRecent volumes: {[round(v, 2) for v in recent_volumes]}"
        
        market_analysis.append(price_text + volume_text)
    
    market_text = "\n\n".join(market_analysis)

    # Format current positions for AI context
    positions_text = ""
    if "positions" in balance:
        for coin in balance["positions"]:
            long_pos = balance["positions"][coin]["long"]
            short_pos = balance["positions"][coin]["short"]
            if long_pos["amount"] > 0:
                positions_text += f"\n{coin} LONG: {long_pos['amount']:.6f} @ {long_pos['avg_price']:.2f}"
            if short_pos["amount"] > 0:
                positions_text += f"\n{coin} SHORT: {short_pos['amount']:.6f} @ {short_pos['avg_price']:.2f}"

    margin_info = ""
    if "margin" in balance:
        margin_info = f"\nMargin Available: ${balance['margin']['available']:.2f}, Used: ${balance['margin']['used']:.2f}"

    prompt = f"""
You are an advanced crypto trading AI with access to short selling and risk management tools. 
IMPORTANT: You cannot use leverage - all positions are 1:1 (no amplification).

Here are the market analysis data for each coin:
{market_text}

Your current balance and holdings:
USD: ${balance.get('USD', 0):.2f}
Realized P&L: ${balance.get('realized_pnl', 0):.2f}{margin_info}

Current Positions:{positions_text if positions_text else " None"}

For each coin (BTC and SOL), what is your recommended action?

TRADING GUIDELINES:
- Consider volume analysis when making decisions:
  * HIGH volume = Strong conviction moves, good for trend following
  * ELEVATED volume = Moderate conviction, suitable for smaller positions
  * NORMAL volume = Standard market activity, use regular position sizing
  * LOW volume = Weak conviction, consider smaller positions or waiting
- Volume spikes often precede significant price movements
- Low volume in trending markets may indicate weakening momentum

Available Actions:
- BUY_LONG [percent] [stop_loss] [take_profit] - Open long position (no leverage)
- SELL_SHORT [percent] [stop_loss] [take_profit] - Open short position (no leverage)
- CLOSE_LONG [percent] - Close long position (partial or full)
- CLOSE_SHORT [percent] - Close short position (partial or full)
- BUY [percent] - Simple spot buy (legacy)
- SELL [percent] - Simple spot sell (legacy)
- HOLD - Do nothing

Examples:
BTC: BUY_LONG 50% 58000 70000
SOL: SELL_SHORT 25% 180 120
BTC: CLOSE_LONG 100%

The reply should adhere strictly to the following format:
BTC: [ACTION] [parameters]
SOL: [ACTION] [parameters]

Set stop losses and take profits to manage risk. No leverage is available.
"""

    print("=== PROMPT SENT TO GPT ===")
    print(prompt)
    print("==========================")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o which supports more parameters
            messages=[
                {"role": "user", "content": prompt}
            ]
            # Remove temperature parameter - use model default
        )
    except Exception as e:
        # Fallback to GPT-4 if GPT-4o is not available
        if "model" in str(e).lower():
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        else:
            raise e

    raw = response.choices[0].message.content.strip().upper()
    print("=== RAW GPT RESPONSE ===")
    print(raw)
    print("========================")

    decisions = {}
    for line in raw.splitlines():
        if ":" not in line or not line.strip():
            continue  # Skip bad or empty lines

        try:
            coin, action_info = line.strip().split(":", 1)
            parts = action_info.strip().split()
            if not parts:
                continue
            
            action = parts[0]
            
            # Parse parameters based on action type
            if action in ["BUY_LONG", "SELL_SHORT"]:
                percent = float(parts[1].replace('%', '')) / 100 if len(parts) > 1 else 0.0
                leverage = 1.0  # Force leverage to 1x (no leverage allowed)
                stop_loss = float(parts[2]) if len(parts) > 2 and parts[2] != 'NULL' else None
                take_profit = float(parts[3]) if len(parts) > 3 and parts[3] != 'NULL' else None
                decisions[coin.strip()] = (action, percent, leverage, stop_loss, take_profit)
            
            elif action in ["CLOSE_LONG", "CLOSE_SHORT", "BUY", "SELL"]:
                percent = float(parts[1].replace('%', '')) / 100 if len(parts) > 1 else 0.0
                decisions[coin.strip()] = (action, percent)
            
            elif action == "HOLD":
                decisions[coin.strip()] = (action, 0.0)
            
        except Exception as e:
            print(f"Skipping malformed line: '{line}' — {e}")
            continue

    return decisions