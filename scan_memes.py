import requests
import pandas as pd
import time
from indicators import calculate_rsi

# Top Memecoins to Scan (CoinGecko IDs)
MEMES = [
    "dogecoin", "shiba-inu", "pepe", "dogwifhat", "bonk", 
    "floki", "memecoin", "book-of-meme", "popcat", "myro",
    "brett", "mog-coin"
]

def get_token_data(coin_id):
    try:
        # Fetch 30 days of hourly data for decent RSI calculation
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=14"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if resp.status_code == 429:
            print(f"⚠️ Rate Limit on {coin_id}. Waiting...")
            time.sleep(5)
            return None
            
        data = resp.json()
        prices = [p[1] for p in data.get('prices', [])]
        
        if len(prices) < 50: return None
        
        return pd.Series(prices)
    except Exception as e:
        print(f"❌ Error {coin_id}: {e}")
        return None

def scan_memes():
    print("🔎 SCANNING MEMECOINS FOR BOTTOM PATTERNS...")
    print("Criteria: RSI < 40 (Oversold) | Accumulation Zone")
    print("-" * 65)
    print(f"{'COIN':<15} | {'PRICE':<12} | {'RSI (14)':<10} | {'STATUS':<20}")
    print("-" * 65)
    
    candidates = []
    
    for coin in MEMES:
        prices = get_token_data(coin)
        if prices is None: continue
        
        # Calculate Indicators
        rsi_series = calculate_rsi(prices, 14)
        if isinstance(rsi_series, pd.Series):
             curr_rsi = rsi_series.iloc[-1]
        else:
             curr_rsi = rsi_series[-1]
             
        curr_price = prices.iloc[-1]
        
        # Determine Status
        status = "NEUTRAL"
        if curr_rsi < 30: status = "💎 ULTRA OVERSOLD"
        elif curr_rsi < 40: status = "✅ BUY ZONE"
        elif curr_rsi > 70: status = "⚠️ OVERBOUGHT (Exit)"
        
        # Color coding for terminal
        rsi_str = f"{curr_rsi:.1f}"
        if curr_rsi < 40: rsi_str = f"\033[92m{curr_rsi:.1f}\033[0m" # Green
        elif curr_rsi > 70: rsi_str = f"\033[91m{curr_rsi:.1f}\033[0m" # Red
        
        print(f"{coin:<15} | ${curr_price:<11.6f} | {rsi_str:<10} | {status}")
        
        candidates.append({
            "coin": coin,
            "rsi": curr_rsi,
            "price": curr_price
        })
        
        # Respect API Rate Limits (HEAVY DELAY for Free Tier)
        print(f"   (Cooling down for 12s...)")
        time.sleep(12) 
        
    print("-" * 65)
    
    # Sort by RSI (Lowest First)
    candidates.sort(key=lambda x: x['rsi'])
    
    best_pick = candidates[0] if candidates else None
    if best_pick and best_pick['rsi'] < 45:
        print(f"\n🏆 TOP PICK: {best_pick['coin'].upper()} (RSI: {best_pick['rsi']:.1f})")
        print("   -> Closest to Bottom. Recommended for 'Buy Low' Strategy.")
    else:
        print("\n⚠️ No 'Screaming Buy' found. Market might be generally pumpy.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    scan_memes()
