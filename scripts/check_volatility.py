import time
from mexc_client import MEXCClient

def check_immediate_volatility(symbol):
    client = MEXCClient()
    # Get last 5 minutes of 1m data
    klines = client.get_klines(symbol, "1m", limit=6)
    if not klines:
        print(f"Error fetching data for {symbol}")
        return

    prices = [float(k[4]) for k in klines]
    current_price = prices[-1]
    prev_price = prices[-2]
    
    change = current_price - prev_price
    volatility = abs(change / prev_price) * 100
    
    # 5-min range
    high = max([float(k[2]) for k in klines])
    low = min([float(k[3]) for k in klines])
    range_pct = (high - low) / low * 100
    
    print(f"--- Volatility Check: {symbol} ---")
    print(f"Current Price: {current_price}")
    print(f"Last 1m Change: {change:.2f} ({volatility:.4f}%)")
    print(f"Last 5m Range: {high - low:.2f} ({range_pct:.4f}%)")
    
    if range_pct > 0.3:
        print("⚠️ HIGH VOLATILITY DETECTED!")
    else:
        print("🟢 Volatility is stable.")

if __name__ == "__main__":
    check_immediate_volatility("SOLUSDT")
    print("-" * 20)
    check_immediate_volatility("BTCUSDT")
