import pandas as pd
import requests
from indicators import calculate_atr

def get_price_history(symbol_id):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{symbol_id}/market_chart?vs_currency=usd&days=1"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if resp.status_code != 200:
            print(f"⚠️ API Error {symbol_id}: {resp.status_code}")
            return None
            
        data = resp.json()
        prices = [p[1] for p in data['prices']]
        return pd.Series(prices)
    except Exception as e:
        print(f"⚠️ Fetch Error {symbol_id}: {e}")
        return None
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if resp.status_code != 200:
            print(f"⚠️ API Error {symbol_id}: {resp.status_code}")
            return None
            
        data = resp.json()
        prices = [p[1] for p in data['prices']]
        return pd.Series(prices)
    except Exception as e:
        print(f"⚠️ Fetch Error {symbol_id}: {e}")
        return None

def check_correlation():
    print("🔄 Calculating Market Correlation (SOL vs BTC)...")
    
    sol_prices = get_price_history("solana")
    btc_prices = get_price_history("bitcoin")
    
    if sol_prices is None or btc_prices is None:
        print("❌ Failed to fetch data.")
        return

    # Trim to matching length
    min_len = min(len(sol_prices), len(btc_prices))
    sol = sol_prices.iloc[-min_len:]
    btc = btc_prices.iloc[-min_len:]
    
    # Calculate Returns
    sol_ret = sol.pct_change().dropna()
    btc_ret = btc.pct_change().dropna()
    
    # Correlation & Beta
    correlation = sol_ret.corr(btc_ret)
    covariance = sol_ret.cov(btc_ret)
    variance = btc_ret.var()
    beta = covariance / variance
    
    # Recent Performance (Last 3h approx - last 36 points of 5min candles)
    sol_perf = (sol.iloc[-1] - sol.iloc[-36]) / sol.iloc[-36] * 100
    btc_perf = (btc.iloc[-1] - btc.iloc[-36]) / btc.iloc[-36] * 100
    
    print("-" * 50)
    print(f"📊 CORRELATION REPORT")
    print("-" * 50)
    print(f"🔗 Correlation: {correlation:.4f}")
    if correlation > 0.8: print("   -> SOL is mirroring BTC closely (Sync Trade).")
    elif correlation < 0.5: print("   -> SOL is moving independently (Decoupled).")
    
    print(f"⚡ Beta (Volatility Multiplier): {beta:.2f}x")
    print(f"   -> Example: If BTC moves 1%, SOL tends to move {beta:.2f}%.")
    
    print(f"📈 Relative Strength (Last 3h):")
    print(f"   BTC: {btc_perf:+.2f}%")
    print(f"   SOL: {sol_perf:+.2f}%")
    
    if sol_perf > btc_perf: print("   -> ✅ SOL is LEADNG/OUTPERFORMING Market.")
    else: print("   -> ⚠️ SOL is LAGGING/WEAKER than Market.")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    check_correlation()
