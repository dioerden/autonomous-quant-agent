from mexc_client import MEXCClient
from indicators import calculate_ema, calculate_rsi

def analyze_timeframe(symbol, interval):
    client = MEXCClient()
    klines = client.get_klines(symbol, interval, limit=100)
    if not klines:
        return "ERROR"
    
    closes = [float(k[4]) for k in klines]
    ema9 = calculate_ema(closes, 9)[-1]
    ema21 = calculate_ema(closes, 21)[-1]
    rsi = calculate_rsi(closes, 14)[-1]
    price = closes[-1]
    
    trend = "BULLISH" if ema9 > ema21 else "BEARISH"
    return {
        "price": price,
        "trend": trend,
        "rsi": rsi,
        "ema9": ema9,
        "ema21": ema21
    }

def run_mtfa(symbol="BTCUSDT"):
    timeframes = ["15m", "60m", "4h"]
    results = {}
    
    print(f"🔍 Performing Multi-Timeframe Analysis for {symbol}...\n")
    
    for tf in timeframes:
        results[tf] = analyze_timeframe(symbol, tf)
        res = results[tf]
        print(f"[{tf}] Price: {res['price']} | Trend: {res['trend']} | RSI: {res['rsi']:.2f}")

    # Final Verification
    trends = [results[tf]['trend'] for tf in timeframes]
    if all(t == "BULLISH" for t in trends):
        print("\n✅ CONSENSUS: STRONG BULLISH (All timeframes aligned!)")
    elif trends[1] == "BULLISH" and trends[2] == "BULLISH":
        print("\n✅ CONSENSUS: BULLISH TREND (HTF confirms LTF movement)")
    else:
        print("\n⚠️ CONSENSUS: MIXED (Market is consolidating/neutral)")

if __name__ == "__main__":
    run_mtfa()
