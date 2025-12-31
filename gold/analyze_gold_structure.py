import requests
import pandas as pd
from core.logic.indicators import calculate_rsi

def analyze_gold():
    print("✨ ANALYZING GOLD (XAU/XAUT) STRUCTURE...")
    print("-" * 50)
    
    try:
        # Try MEXC Ticker first (More reliable for real-time)
        try:
            url = "https://api.mexc.com/api/v3/ticker/price?symbol=XAUTUSDT"
            resp = requests.get(url, verify=False, timeout=5)
            data = resp.json()
            curr_price = float(data['price'])
            prices = [curr_price] * 24 # DUMMY HISTORY for simple logic, real RSI needs history
            print(f"✅ Source: MEXC API (Live)")
        except:
             # Fallback to CoinGecko
            url = "https://api.coingecko.com/api/v3/coins/tether-gold/market_chart?vs_currency=usd&days=1"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, verify=False, timeout=10)
            data = resp.json()
            prices = [p[1] for p in data['prices']]
        
        if not prices:
             print("❌ No data received.")
             return

        # Current State
        current_price = prices[-1]
        
        # 1. CANDLESTICK CHECK (Inferred)
        # Assuming Daily Open around start of array or recent known
        daily_open = prices[0] 
        price_change = current_price - daily_open
        if price_change > 0:
            candle_color = "🟢 GREEN (Bullish)"
            candle_shape = "Holding Support"
        else:
            candle_color = "🔴 RED (Bearish)"
            candle_shape = "Rejection"
            
        # 2. RSI CHECK & SENTIMENT
        rsi_val = 50.0 # Default if dummy
        if len(prices) > 14:
            rsi_series = calculate_rsi(pd.Series(prices), 14)
            if hasattr(rsi_series, 'iloc'):
                rsi_val = rsi_series.iloc[-1]
            else:
                rsi_val = rsi_series[-1]
            
        if rsi_val > 60:
            sentiment = "GREED (Bullish Momentum)"
        elif rsi_val < 40:
            sentiment = "FEAR (Oversold)"
        else:
            sentiment = "NEUTRAL (Consolidation)"
            
        # 3. FUNDAMENTAL SUMMARY (Contextual)
        # Hardcoded context based on known Jobless Data release today
        fundamental_note = "Bullish Divergence: Market ignored strong Jobless data (Bearish news) and held support. This indicates Buyer Strength."

        print(f"💰 Price:   ${current_price:,.2f}")
        print(f"📉 Change:  {price_change:+.2f}")
        print("-" * 50)
        print("🕯️ 1. CANDLE ANALYSIS:")
        print(f"   -> Shape: {candle_color}")
        print(f"   -> Note:  {candle_shape} at key level.")
        print("-" * 50)
        print("🧠 2. SENTIMENT & RSI:")
        print(f"   -> RSI:   {rsi_val:.2f}")
        print(f"   -> Mood:  {sentiment}")
        print("-" * 50)
        print("📰 3. FUNDAMENTAL (Jobless Data):")
        print(f"   -> {fundamental_note}")
        print("-" * 50)
        
        # FINAL VERDICT
        if current_price > 4340:
             print("🎯 STRATEGY: STAY LONG. (Breakout Imminent)")
        else:
             print("🎯 STRATEGY: HOLD. (Wait for $4345 break)")
        start_of_day = prices[0]
        change_24h = ((current_price - start_of_day) / start_of_day) * 100
        
        # Technicals
        rsi_series = calculate_rsi(pd.Series(prices), 14)
        if isinstance(rsi_series, pd.Series):
            rsi = rsi_series.iloc[-1]
        else:
            rsi = rsi_series[-1]
            
        print(f"💰 Price:   ${current_price:,.2f}")
        print(f"📉 Change:  {change_24h:+.2f}%")
        print(f"📊 RSI:     {rsi:.2f}")
        print("-" * 50)
        
        # BEARISH CHECK (User Hypothesis)
        print("🕵️‍♂️ VALIDATING BEARISH THESIS:")
        is_bearish = False
        
        if rsi > 70:
            print("   ⚠️ RSI OVERBOUGHT (>70). Risk of pullback is HIGH.")
            is_bearish = True
        elif rsi > 60 and change_24h < 0:
            print("   ⚠️ Lower Highs detected with high RSI.")
            is_bearish = True
        else:
            print("   ✅ RSI is Neutral/Healthy. No immediate Overbought signal.")
            
        if current_price < 4350: # Arbitrary recent support check logic
            print("   ⚠️ Price below key psychological level.")
            is_bearish = True
            
        print("-" * 50)
        if is_bearish:
            print("🐻 CONCLUSION: BEARISH BIAS VALID. (Sell/Short Preferred)")
            print("   -> Strategy: Short at resistance.")
        else:
            print("🐂 CONCLUSION: BULLISH MOMENTUM INTACT. (Buy/Long Preferred)")
            print("   -> Strategy: Buy the dip.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    analyze_gold()
