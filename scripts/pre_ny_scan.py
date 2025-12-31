import requests
import pandas as pd
from indicators import calculate_rsi

TOKENS = {
    "bitcoin": "BTC",
    "solana": "SOL",
    "myro": "MYRO"
}

def scan_pulse():
    print("🏥 MARKET PULSE CHECK (Pre-NY Open)...")
    print("-" * 50)
    print(f"{'ASSET':<8} | {'PRICE':<12} | {'RSI':<6} | {'VERDICT':<20}")
    print("-" * 50)
    
    for coin_id, symbol in TOKENS.items():
        try:
            print(f"   Scanning {symbol}...", end="\r")
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1"
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, verify=False, timeout=10)
            
            if resp.status_code != 200:
                print(f"{symbol:<8} | {'ERROR':<12} | {'-':<6} | Rate Limit ⚠️ (Hit API Wall)")
                continue
                
            data = resp.json()
            prices = [p[1] for p in data['prices']]
            
            if not prices: continue
            
            # Calc RSI
            rsi_series = calculate_rsi(pd.Series(prices), 14)
            rsi = rsi_series.iloc[-1]
            price = prices[-1]
            
            # Logic
            verdict = "WAIT"
            if rsi < 30: verdict = "💎 BUY (SNIPER)"
            elif rsi < 45: verdict = "✅ BUY (SAFE)"
            elif rsi > 70: verdict = "🛑 SELL/SHORT"
            else: verdict = "⚖️ NEUTRAL"
            
            # Color
            rsi_str = f"{rsi:.1f}"
            if rsi < 35: rsi_str = f"\033[92m{rsi:.1f}\033[0m"
            elif rsi > 70: rsi_str = f"\033[91m{rsi:.1f}\033[0m"
            
            print(f"{symbol:<8} | ${price:<11.5f} | {rsi_str:<6} | {verdict}")
            
            # Respect Rate Limits
            import time
            time.sleep(12)
            
        except Exception as e:
            print(f"{symbol}: Error {e}")
            
    print("-" * 50)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    scan_pulse()
