from strategy import HybridStrategy
from sentiment_engine import SentimentEngine
import json

def scalp_check():
    symbol = "BTCUSDT"
    print(f"--- ⚡ Scalp Intelligence Scan: {symbol} ---")
    strategy = HybridStrategy(symbol)
    sentiment_engine = SentimentEngine()
    
    # 1. Technical Check (15m base but we'll infer 1m volatility)
    result = strategy.get_signals()
    
    # 2. Latest News Sentiment (Gemini Powered)
    # Simulate fresh headines check
    headlines = [
        "BTC liquidations increasing as price tests 89k",
        "Ethereum whale activity spikes in late NY session"
    ]
    ai_sentiment = sentiment_engine.get_market_sentiment(symbol, headlines)
    
    # 3. Decision Logic for Scalping
    price = result['price']
    rsi = result['indicators']['rsi']
    fng = result['fng']
    
    is_scalpable = False
    reasons = []
    
    if rsi < 30 or rsi > 70:
        reasons.append(f"High Volatility detected (RSI: {rsi:.2f})")
        is_scalpable = True
    
    if ai_sentiment != "NEUTRAL":
        reasons.append(f"AI Sentiment Shift: {ai_sentiment}")
        is_scalpable = True

    print(json.dumps({
        "is_scalpable": is_scalpable,
        "price": price,
        "sentiment": ai_sentiment,
        "fng": fng,
        "reasons": reasons
    }, indent=2))

if __name__ == "__main__":
    scalp_check()
