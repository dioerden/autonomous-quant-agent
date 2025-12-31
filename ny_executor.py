import time
import datetime
from strategy import HybridStrategy
from execute_trade import execute_at_market

def wait_for_ny_open():
    """Waits until 13:00 UTC (20:00 WIB) - New York Pre-Market / Set 8"""
    target_hour_utc = 13
    
    while True:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        if now_utc.hour >= target_hour_utc:
            print(f"🚀 NEW YORK SESSION OPEN (Set 8) | Time: {now_utc.strftime('%H:%M:%S')} UTC")
            break
        
        remaining_seconds = (target_hour_utc - now_utc.hour - 1) * 3600 + (60 - now_utc.minute - 1) * 60 + (60 - now_utc.second)
        remaining_mins = remaining_seconds // 60
        print(f"⏳ Waiting for NY Set 8 (20:00 WIB)... (~{remaining_mins} mins left) | Current UTC: {now_utc.strftime('%H:%M:%S')}", end="\r")
        time.sleep(30)

def execute_ny_strategy(symbol="SOLUSDT"):
    strategy = HybridStrategy(symbol)
    print(f"\nEvaluating {symbol} for New York Set 8...")
    
    result = strategy.get_signals()
    signal = result.get("signal")
    price = result.get("price")
    
    print(f"📊 Signal: {signal} | Price: {price}")
    
    if not signal:
        print(f"⚠️ Analysis Failed or No Signal. Result: {result}")
        return

    if "BUY" in signal:
        print(f"✅ Executing LONG for {symbol}...")
        execute_at_market(symbol, "BUY", amount_usdt=50)
    elif "SHORT" in signal:
        print(f"✅ Executing SHORT for {symbol}...")
        execute_at_market(symbol, "SELL", amount_usdt=50)
    else:
        print("❌ No clear signal at NY Open. Standing by.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="SOLUSDT", help="Symbol to trade (e.g., WLDUSDT)")
    args = parser.parse_args()
    
    symbol = args.symbol
    print(f"🎯 Target Locked: {symbol}")
    
    # Script standby menuju jam 20:00 WIB (13:00 UTC)
    wait_for_ny_open()
    
    execute_ny_strategy(symbol)
