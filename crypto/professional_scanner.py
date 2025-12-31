import time
import os
from mexc_client import MEXCClient
from strategy import HybridStrategy

def scan_markets():
    # Symbols to watch (Top MEXC Volume & Movers)
    symbols = ["SOLUSDT", "BTCUSDT", "ETHUSDT", "XRPUSDT", "DOGEUSDT", "ARBUSDT", "PEPEUSDT"]
    
    print(f"🔍 Starting Professional Market Scan | Time: {time.strftime('%H:%M:%S')} WIB")
    
    # Check Killzone first
    dummy_strat = HybridStrategy("SOLUSDT")
    killzone = dummy_strat.check_killzone()
    
    if killzone:
        print(f"🔥 {killzone} SESSION ACTIVE | Expect high volatility.")
    else:
        # Check if it's generally the Asian Session (Tokyo Open to Close)
        import datetime
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        if 0 <= now_utc.hour < 9:
            print(f"🇯🇵 ASIAN SESSION (Tokyo) | Current Time: {now_utc.strftime('%H:%M')} UTC")
        else:
            print(f"💤 Outside Killzones (Quiet Hours). Looking for structural setups.")

    opportunities = []

    for symbol in symbols:
        try:
            # Handle MEXC symbol formatting (Spot vs Futures)
            clean_symbol = symbol.replace("_", "")
            strategy = HybridStrategy(clean_symbol)
            
            result = strategy.get_signals()
            
            if result.get('error'):
                continue

            price = result['price']
            signal = result['signal']
            gaps = result['recent_gaps']
            fib = result['fib_levels']
            poc = result['poc']
            fng = f"{result['fng']} ({result['fng_class']})"
            macro = result['macro']['dxy_sentiment']
            sentiment = result['fundamental']['sentiment']
            change = result['fundamental']['priceChange24h']

            # Professional Scoring
            score = 0
            if "BUY" in signal: score += 3
            if sentiment == "BULLISH": score += 2
            if killzone: score += 2
            if gaps: score += 1
            
            # Bonus for POC alignment
            if price >= poc: score += 1
            
            # Bonus for Golden Pocket (0.618) - If price is near it
            golden_pocket = fib["0.618"]
            is_near_fib = abs(price - golden_pocket) / price < 0.005 # 0.5% proximity
            if is_near_fib: score += 2

            opp = {
                "symbol": symbol,
                "score": score,
                "price": price,
                "signal": signal,
                "sentiment": sentiment,
                "fng": fng,
                "macro": macro,
                "fib618": golden_pocket,
                "poc": poc,
                "gaps": len(gaps),
                "change": change
            }
            opportunities.append(opp)
            
        except Exception as e:
            print(f"⚠️ Error scanning {symbol}: {e}")

    # Sort opportunities by score
    opportunities = sorted(opportunities, key=lambda x: x['score'], reverse=True)

    print("\n--- Market Opportunity Report ---")
    print(f"{'SYMBOL':<12} | {'SCORE':<5} | {'SIGNAL':<15} | {'F&G INDEX':<12} | {'MACRO (DXY)':<12} | {'SENTIMENT':<10} | {'24H %'}")
    print("-" * 130)
    for opp in opportunities:
        print(f"{opp['symbol']:<12} | {opp['score']:<5} | {opp['signal']:<15} | {opp['fng']:<12} | {opp['macro']:<12} | {opp['sentiment']:<10} | {opp['change']:+.2f}%")

if __name__ == "__main__":
    scan_markets()
