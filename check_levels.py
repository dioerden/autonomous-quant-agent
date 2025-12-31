from strategy import HybridStrategy

def get_levels(symbol):
    strat = HybridStrategy(symbol)
    res = strat.get_signals()
    print(f"SYMBOL: {symbol}")
    print(f"CURRENT PRICE: {res['price']}")
    print(f"POC (Point of Control): {res['poc']}")
    print(f"FIB LEVELS: {res['fib_levels']}")
    print(f"REASONS: {res['reasons']}")
    print(f"AI OPINION: {res['ai_opinion']}")

if __name__ == "__main__":
    get_levels("SOLUSDT")
