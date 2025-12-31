from strategy import HybridStrategy
import json

def analyze_btc():
    symbol = "BTCUSDT"
    print(f"--- Deep Hybrid AI Analysis: {symbol} ---")
    strategy = HybridStrategy(symbol)
    
    # Get signals with fake news headlines for comprehensive sentiment check
    headlines = [
        "Institutional interest in Bitcoin remains high despite consolidation",
        "Analysts predict major breakout if BTC holds 87k"
    ]
    result = strategy.get_signals(news_headlines=headlines)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    analyze_btc()
