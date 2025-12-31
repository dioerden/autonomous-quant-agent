import time
from strategy import HybridStrategy
from mtf_verify import analyze_timeframe

def run_resilient_analysis(symbol):
    print(f"\n--- Resilient Analysis for {symbol} ---")
    
    # 1. MTF Analysis
    print(f"🔍 Analyzing Multi-Timeframe Trends...")
    for _ in range(3):
        try:
            m15 = analyze_timeframe(symbol, "15m")
            m60 = analyze_timeframe(symbol, "60m")
            h4 = analyze_timeframe(symbol, "4h")
            print(f"[15m] Trend: {m15['trend']} | RSI: {m15['rsi']:.2f}")
            print(f"[60m] Trend: {m60['trend']} | RSI: {m60['rsi']:.2f}")
            print(f"[4h] Trend: {h4['trend']} | RSI: {h4['rsi']:.2f}")
            break
        except Exception as e:
            print(f"⚠️ Retry MTF due to error: {e}")
            time.sleep(2)

    # 2. Strategy & AI
    print(f"🤖 Fetching Hybrid Strategy & AI Signal...")
    for _ in range(3):
        try:
            strategy = HybridStrategy(symbol)
            result = strategy.get_signals()
            print(f"SIGNAL: {result.get('signal', 'N/A')}")
            print(f"PRICE: {result.get('price', 'N/A')}")
            print(f"AI OPINION: {result.get('ai_opinion', 'N/A')}")
            print(f"SCORE: {result.get('score', 'N/A')}")
            break
        except Exception as e:
            print(f"⚠️ Retry Strategy due to error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    run_resilient_analysis("SOLUSDT")
    run_resilient_analysis("BTCUSDT")
