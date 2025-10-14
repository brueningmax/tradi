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
