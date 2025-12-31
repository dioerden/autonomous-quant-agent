import time
import datetime
from core.logic.strategy import HybridStrategy
from execute_trade import execute_at_market

def wait_for_london_open():
    """Waits until 07:00 UTC (14:00 WIB)"""
    target_hour_utc = 7
    
    while True:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        if now_utc.hour >= target_hour_utc:
            print(f"🚀 LONDON OPEN REACHED | Time: {now_utc.strftime('%H:%M:%S')} UTC")
            break
        
        remaining = (target_hour_utc - now_utc.hour - 1) * 3600 + (60 - now_utc.minute - 1) * 60 + (60 - now_utc.second)
        print(f"⏳ Waiting for London Open... (~{remaining//60} mins left) | Current UTC: {now_utc.strftime('%H:%M:%S')}", end="\r")
        time.sleep(30)

def execute_london_strategy(symbol="SOLUSDT"):
    strategy = HybridStrategy(symbol)
    print(f"\nEvaluating {symbol} for London Open...")
    
    result = strategy.get_signals()
    signal = result.get("signal")
    price = result.get("price")
    
    print(f"📊 Signal: {signal} | Price: {price}")
    
    if "BUY" in signal:
        print(f"✅ Executing LONG for {symbol}...")
        execute_at_market(symbol, "BUY", amount_usdt=50) # Activated automatic execution
    elif "SHORT" in signal:
        print(f"✅ Executing SHORT for {symbol}...")
        execute_at_market(symbol, "SELL", amount_usdt=50) # Activated automatic execution
    else:
        print("❌ No clear signal at London Open. Standing by.")

if __name__ == "__main__":
    # Script akan standby menunggu jam 14:00 WIB (07:00 UTC)
    wait_for_london_open()
    
    execute_london_strategy("SOLUSDT")
    execute_london_strategy("BTCUSDT")
