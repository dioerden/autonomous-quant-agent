import time
import pandas as pd
from mexc_client import MEXCClient

def collect_historical_data(symbol="SOLUSDT", interval="15m", total_batches=5):
    """
    Collects multiple batches of historical K-lines for AI training.
    """
    client = MEXCClient()
    print(f"📥 Starting data collection for {symbol} ({interval})...")
    
    all_klines = []
    
    # We fetch batches of 1000 (max)
    # The API returns oldest to newest. To go back in time, we fetch current, then use its oldest timestamp as endTime for the next call.
    
    end_time = None
    for b in range(total_batches):
        print(f"Fetching batch {b+1}/{total_batches}...")
        
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": 1000
        }
        if end_time:
            params["endTime"] = end_time - 1 # Subtract 1ms to avoid overlap
            
        import requests
        response = requests.get(f"{client.base_url}{endpoint}", params=params)
        klines = response.json()
        
        if not klines or 'error' in klines:
            print("❌ No more data or error.")
            break
            
        all_klines = klines + all_klines # Prepend older data
        end_time = klines[0][0] # Update end_time to the oldest timestamp in this batch
        
        time.sleep(1) # Rate limit protection
    
    if all_klines:
        # Sort by time just in case
        all_klines.sort(key=lambda x: x[0])
    
    if all_klines:
        df = pd.DataFrame(all_klines, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume'
        ])
        
        # Save to CSV for AI4Finance tools to ingest
        filename = f"{symbol}_{interval}_historical.csv"
        df.to_csv(filename, index=False)
        print(f"💾 Data saved to {filename}")
        return filename
    else:
        print("❌ Failed to collect data.")
        return None

if __name__ == "__main__":
    collect_historical_data()
