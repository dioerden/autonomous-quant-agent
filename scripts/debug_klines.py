
import requests
import time

def debug_klines():
    symbol = "WLDUSDT"
    endpoints = [
        f"https://api.mexc.com/api/v3/klines?symbol={symbol}&interval=1h&limit=5",
        f"https://api.mexc.so/api/v3/klines?symbol={symbol}&interval=1h&limit=5"
    ]
    
    import urllib3
    urllib3.disable_warnings()
    
    print("🔍 Testing KLines Direct Connection...")
    
    for url in endpoints:
        print(f"\nTarget: {url}")
        try:
            start = time.time()
            resp = requests.get(url, verify=False, timeout=10)
            elapsed = time.time() - start
            print(f"✅ Status: {resp.status_code}")
            print(f"⏱️ Latency: {elapsed:.2f}s")
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"📦 Data Received: {len(data)} candles")
                print(f"   Sample: {data[0][:5]}")
            else:
                print(f"⚠️ Empty/Invalid Data: {data}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    debug_klines()
