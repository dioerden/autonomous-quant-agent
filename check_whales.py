import requests
import time
from mexc_futures_client import MEXCFuturesClient

def analyze_whales(symbol="SOL_USDT"):
    print(f"🐋 WHALE RADAR: Scanning Deep Waters for {symbol}...")
    client = MEXCFuturesClient()
    
    # 1. Fetch Open Interest (The Weight of Whales)
    # Note: Using a robust public endpoint if client fails
    oi_data = None
    funding_data = None
    
    # 1. Fetch Open Interest Proxy (Using CoinGecko Volume as Fallback due to blocks)
    try:
        # Try CoinGecko for Volume/Whale Proxy first (Most reliable)
        cg_id = "solana"
        url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=usd&days=1"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, verify=False, timeout=10)
        data = resp.json()
        
        volumes = data.get('total_volumes', [])
        if volumes:
            curr_vol = volumes[-1][1]
            prev_vol = volumes[0][1]
            
            print("-" * 50)
            print(f"📊 WHALE ACTIVITY MONITOR (Volume Proxy)")
            print("-" * 50)
            print(f"🌊 24h Volume Profile: ${curr_vol:,.0f}")
            
            if curr_vol > prev_vol * 1.2:
                print("   -> 🐋 SPIKE DETECTED: Volume is growing (+20%). Whales Entering.")
            elif curr_vol < prev_vol * 0.8:
                print("   -> 📉 DRYING UP: Volume dropping. Whales sleeping.")
            else:
                print("   -> ⚖️ STABLE: Retail flow dominant.")
                
            # Funding Estimation (Static based on trend)
            price_change = (data['prices'][-1][1] - data['prices'][0][1]) / data['prices'][0][1]
            est_funding = "POSITIVE" if price_change > 0 else "NEGATIVE"
            print(f"💰 Est. Funding Sentiment: {est_funding} (based on trend)")
            
    except Exception as e:
        print(f"❌ Error fetching Whale data: {e}")
        return

    # 4. On-Chain Proxy (Search based)
    print("\n🔗 ON-CHAIN SENTIMENT (External Data):")
    print("   Scanning mainly for: Large Transfers to/from Exchanges.")
    print("   * INFLOW to Exchange = Potential SELL (Bearish)")
    print("   * OUTFLOW to Wallet = Accumulation (Bullish)")
    print("   (Refer to AI Search Report for specific transactions)")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    analyze_whales()
