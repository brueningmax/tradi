# trader.py
import json

BALANCE_FILE = "balance.json"
PAPER_BALANCE_FILE = "paper_balance.json"

def load_balance(paper_trading=False):
    filename = PAPER_BALANCE_FILE if paper_trading else BALANCE_FILE
    with open(filename, "r") as f:
        return json.load(f)

def save_balance(balance, paper_trading=False):
    filename = PAPER_BALANCE_FILE if paper_trading else BALANCE_FILE
    with open(filename, "w") as f:
        json.dump(balance, f, indent=2)

def apply_trade(balance, decision, coin, current_price, percent, paper_trading=False):
    mode_text = "[PAPER]" if paper_trading else "[LIVE]"
    print(f"{mode_text} {decision}")
    
    if decision == "BUY" and balance["USD"] > 0 and percent > 0:
        usd_to_spend = balance["USD"] * percent
        amount = round(usd_to_spend / current_price, 6)
        balance["coins"][coin]["amount"] += amount
        balance["coins"][coin]["avg_price"] = current_price
        balance["USD"] -= usd_to_spend
        trade_msg = f"{mode_text} BOUGHT {amount} {coin} at {current_price} using {percent*100:.0f}% of USD"
        balance["history"].append(trade_msg)
        print(trade_msg)

    elif decision == "SELL" and balance["coins"][coin]["amount"] > 0 and percent > 0:
        amount_to_sell = balance["coins"][coin]["amount"] * percent
        avg_price = balance["coins"][coin]["avg_price"]
        pnl = (current_price - avg_price) * amount_to_sell

        balance["USD"] += round(amount_to_sell * current_price, 2)
        balance["coins"][coin]["amount"] -= amount_to_sell

        if balance["coins"][coin]["amount"] == 0:
            balance["coins"][coin]["avg_price"] = 0

        balance["realized_pnl"] += round(pnl, 2)
        trade_msg = f"{mode_text} SOLD {amount_to_sell} {coin} at {current_price} (P&L: {round(pnl, 2)})"
        balance["history"].append(trade_msg)
        print(trade_msg)

    else:
        trade_msg = f"{mode_text} HELD {coin} at {current_price}"
        balance["history"].append(trade_msg)
        print(trade_msg)

    save_balance(balance, paper_trading)

def calc_unrealized_pnl(balance, current_prices):
    total_unrealized = 0.0
    for coin, data in balance["coins"].items():
        amount = data["amount"]
        avg_price = data["avg_price"]
        if amount > 0:
            current_price = current_prices.get(coin)
            if current_price:
                unrealized = (current_price - avg_price) * amount
                total_unrealized += unrealized
    return round(total_unrealized, 2)

def backtest(price_data, balance, ai_function, paper_trading=False):
    # price_data = {"BTC": [(timestamp, price), ...], "SOL": [...], ...}
    length = len(next(iter(price_data.values())))
    total_runs = length - 30

    for i in range(30, length):
        # Slice the price history up to this point
        sliced_history = {coin: data[:i] for coin, data in price_data.items()}
        current_prices = {coin: data[i][1] for coin, data in price_data.items()}

        decisions = ai_function(sliced_history, balance)

        for coin, (decision, percent) in decisions.items():
            apply_trade(balance, decision, coin, current_prices[coin], percent, paper_trading)

        # Progress bar
        completed = i - 30 + 1
        bar_length = 30
        filled = int((completed / total_runs) * bar_length)
        bar = "#" * filled + "_" * (bar_length - filled)
        print(f"\r[{bar}] {completed}/{total_runs}", end="")

    print()  # New line after progress bar
    return balance

