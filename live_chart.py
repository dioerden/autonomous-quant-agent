import time
import os
import sys
import requests
import datetime
import pandas as pd
from indicators import calculate_rsi

# Configuration
SYMBOL = "SOLUSDT"
CG_ID = "solana" # Mapping for CoinGecko
REFRESH_RATE = 60 # Seconds

def get_market_chart():
    """Fetch 24h data from CoinGecko (Granularity ~5 min usually)"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{CG_ID}/market_chart?vs_currency=usd&days=1"
        # Add User-Agent to avoid 403 Forbidden
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if resp.status_code != 200:
            print(f"⚠️ API Status: {resp.status_code}")
            return None
            
        data = resp.json()
        
        prices = data.get('prices', [])
        if not prices: return None
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calculate RSI
        df['rsi'] = calculate_rsi(df['price'], 14)
        
        return df.tail(15) # Last 15 data points
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None

def draw_chart(df):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"🕯️ LIVE CANDLE MONITOR: {SYMBOL} (Last 24h Trend)")
    print(f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print("-" * 65)
    print(f"{'TIME':<10} | {'PRICE':<10} | {'RSI':<6} | {'CHANGE':<10}")
    print("-" * 65)
    
    prev_price = df.iloc[0]['price']
    
    for index, row in df.iterrows():
        price = row['price']
        rsi = row['rsi']
        time_str = row['datetime'].strftime('%H:%M')
        
        change = price - prev_price
        pct = (change / prev_price) * 100
        
        # Visuals
        color = "\033[92m" if change >= 0 else "\033[91m"
        reset = "\033[0m"
        icon = "🟢" if change >= 0 else "🔴"
        bar = "█" * int(abs(pct) * 20) # Dynamic bar length
        if len(bar) == 0: bar = " "
        
        # RSI Warning
        rsi_str = f"{rsi:.1f}"
        if rsi > 70: rsi_str = f"\033[91m{rsi:.1f}\033[0m" # Red if Overbought
        elif rsi < 30: rsi_str = f"\033[92m{rsi:.1f}\033[0m" # Green if Oversold
        
        entry_marker = ""
        if 125.70 <= price <= 125.90:
            entry_marker = "👈 YOUR ENTRY"
            
        print(f"{time_str:<10} | ${price:<9.2f} | {rsi_str:<15} | {color}{icon} {pct:+.2f}% {bar}{reset} {entry_marker}")
        
        prev_price = price

    print("-" * 65)
    print("Press Ctrl+C to stop.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    
    while True:
        df = get_market_chart()
        if df is not None:
            draw_chart(df)
        else:
            print("⚠️ Reconnecting to data feed...")
            
        time.sleep(REFRESH_RATE)
