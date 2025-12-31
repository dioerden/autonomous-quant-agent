import requests
import pandas as pd
from indicators import calculate_rsi

def analyze_gold_deep():
    print("🎇 NEW YEAR DEEP DIVE: GOLD (XAU/XAUT) WEEKLY STRUCTURE...")
    print("-" * 60)
    
    try:
        # Fetch 7 Days Data (Weekly Context)
        url = "https://api.coingecko.com/api/v3/coins/tether-gold/market_chart?vs_currency=usd&days=7"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        data = resp.json()
        
        if 'prices' not in data:
            print(f"❌ API Error: {data}")
            return

        prices = [p[1] for p in data['prices']]
        
        # 1. Weekly Trend Check
        curr_price = prices[-1]
        week_high = max(prices)
        week_low = min(prices)
        avg_price = sum(prices) / len(prices)
        
        # Position relative to Weekly Range
        range_percent = (curr_price - week_low) / (week_high - week_low) * 100
        
        # 2. RSI Check (Longer Term reliability)
        rsi_series = calculate_rsi(pd.Series(prices), 14)
        if isinstance(rsi_series, pd.Series):
            rsi = rsi_series.iloc[-1]
        else:
            rsi = rsi_series[-1]
            
        print(f"💰 Price:       ${curr_price:,.2f}")
        print(f"📅 Weekly Low:  ${week_low:,.2f}")
        print(f"📅 Weekly High: ${week_high:,.2f}")
        print(f"📊 Rel Position: {range_percent:.1f}% (0=Low, 100=High)")
        print(f"📉 RSI (1H/4H):  {rsi:.2f}")
        print("-" * 60)
        
        # 3. HOLIDAY CONTEXT ANALYSIS
        print("🧠 NEW YEAR 'HOLIDAY' PSYCHOLOGY:")
        
        sentiment = "NEUTRAL"
        strategy = "WAIT"
        
        # Scenario A: Top of Range + High RSI = Sell/Take Profit before holiday
        if range_percent > 80 and rsi > 60:
            sentiment = "BEARISH (Profit Taking)"
            print("   -> Traders are cashing out for the holiday.")
            print("   -> Price is high in weekly range. Resistance expected.")
            strategy = "SHORT SCALP"
            
        # Scenario B: Bottom of Range + Low RSI = Buy for January Effect
        elif range_percent < 20:
            sentiment = "BULLISH (Discount Accumulation)"
            print("   -> Smart money buys the dip for 'January Rally'.")
            strategy = "LONG SWING"
            
        # Scenario C: Middle (Choppy)
        else:
            sentiment = "NEUTRAL (Choppy)"
            print("   -> Price is in 'No Man's Land'.")
            print("   -> Liquidity is thin. Expect fakeouts.")
            strategy = "WAIT / RANGE TRADE"

        print(f"\n🎯 FINAL VERDICT: {sentiment}")
        print(f"🛠️ SUGGESTED SETUP: {strategy}")
        
        if strategy == "SHORT SCALP":
            print("   Entry: Market (Top of Range)")
            print(f"   SL:    ${week_high * 1.005:.2f} (Above Week High)")
            print(f"   TP:    ${avg_price:.2f} (Mean Reversion)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    analyze_gold_deep()
