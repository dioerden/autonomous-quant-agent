from strategy import HybridStrategy
import time

def check_solid_assets():
    print("🏰 FORTRESS SCAN: Analyzing Solid Fundamentals (BTC & SOL)...")
    
    majors = ["BTCUSDT", "SOLUSDT"]
    
    for symbol in majors:
        print("-" * 50)
        print(f"🔎 Analyzing {symbol}...")
        
        try:
            strategy = HybridStrategy(symbol)
            
            # Fetch Signals (Technicals + AI + Sentiment)
            # Pass empty headlines as we know macro is quiet
            result = strategy.get_signals(news_headlines=[])
            
            if "error" in result:
                # Fallback: Provide Strategy Plan even if data fails
                print(f"⚠️ Live Data Unavailable (API Block). Switching to STRATEGY MODE.")
                if symbol == "BTCUSDT":
                    print("🗺️ BTC PLAN (New York Open):")
                    print("   - BUY ZONE: $95,200 - $95,500")
                    print("   - SELL ZONE: $97,000+")
                    print("   - PIVOT: If price > $96,000 => BULLISH")
                elif symbol == "SOLUSDT":
                    print("🗺️ SOL PLAN (New York Open):")
                    print("   - BUY ZONE: $125.50 - $126.00 (Our Previous Entry)")
                    print("   - TARGET: $128.00 (Scalp) / $130.00 (Swing)")
                    print("   - LOGIC: 'RSI Reset'. If price stable > $126, Re-Enter.")
                continue
                
            # Extract Key Metrics
            price = result['price']
            rsi = result['indicators']['rsi']
            signal = result['signal']
            ai_verdict = result.get('ai_opinion', 'N/A')
            funding = result.get('funding_rate', 0)
            
            print(f"💵 Price: ${price:,.2f}")
            print(f"📈 RSI (15m): {rsi:.2f}")
            print(f"🤖 AI Verdict: {ai_verdict}")
            print(f"📡 System Signal: {signal}")
            
            # Fundamental Insight
            if symbol == "BTCUSDT":
                print("🧠 FUNDAMENTAL NOTE: 'The Market Mover'")
                print("   -> ETF Inflows are positive.")
                print("   -> If BTC holds, Alts (SOL) are safe.")
            elif symbol == "SOLUSDT":
                print("🧠 FUNDAMENTAL NOTE: 'High Beta Play'")
                print("   -> Strong Ecosystem but follows BTC.")
                print("   -> If BTC is Green, SOL is usually Greener.")
                
            # Recommendation
            if rsi < 40 and "BUY" in ai_verdict:
                print("🎯 CONCLUSION: STRONG BUY (Discounted Quality)")
            elif "BUY" in signal:
                print("✅ CONCLUSION: BUY (Trend Following)")
            elif rsi > 70:
                print("⚠️ CONCLUSION: WAIT (Overheated)")
            else:
                print("⚖️ CONCLUSION: HOLD/NEUTRAL")
                
        except Exception as e:
            print(f"❌ Analysis Failed: {e}")
            
        print("   (Cooling down API for 16s...)")
        time.sleep(16) # Heavy delay for Rate Limits

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    check_solid_assets()
