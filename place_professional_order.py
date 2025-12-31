import os
import sys
import time
import requests
from mexc_futures_client import MEXCFuturesClient

def place_sol_futures_limit_order(notional_usdt=40):
    symbol = "SOL_USDT" # Futures format
    entry_price = 124.50 # Matching user screenshot
    leverage = 10
    sl_pct = 0.015  # 1.5%
    tp_pct = 0.07   # 7.0%
    
    # Calculations
    sl_price = entry_price * (1 - sl_pct)
    tp_price = entry_price * (1 + tp_pct)
    
    # Format for SOL
    sl_price = round(sl_price, 2)
    tp_price = round(tp_price, 2)
    
    # Volume in SOL (Notional / Price)
    vol = round(notional_usdt / entry_price, 2)
    
    print(f"🎯 PROFESSIONAL FUTURES LIMIT ORDER: {symbol}")
    print(f"--- Settings ---")
    print(f"LEVERAGE: {leverage}X (Isolated)")
    print(f"ENTRY LIMIT: {entry_price}")
    print(f"STOP LOSS (1.5%): {sl_price}")
    print(f"TAKE PROFIT (7%): {tp_price}")
    print(f"NOTIONAL: {notional_usdt} USDT (~{vol} SOL)")
    print(f"----------------")
    
    client = MEXCFuturesClient()
    
    # 1. First, ensure leverage is set to 10x
    print(f"⚙️ Setting leverage to {leverage}x...")
    for i in range(3):
        try:
            client.change_leverage(symbol, leverage)
            print("✅ Leverage set.")
            break
        except Exception as e:
            print(f"⚠️ Leverage attempt {i+1} failed: {e}")
            time.sleep(2)
    
    # 2. Place Limit Open Long order
    print(f"🚀 Placing LIMIT OPEN LONG for {vol} SOL...")
    for i in range(5):
        try:
            result = client.create_order(
                symbol=symbol,
                side=1,
                order_type=1,
                vol=vol,
                leverage=leverage,
                price=entry_price
            )
            if result.get('success'):
                print("✅ Futures Limit Order Successful!")
                print(f"Order Data: {result.get('data')}")
                print(f"\n📢 ACTION REQUIRED: Please set your TP/SL in the MEXC UI:")
                print(f"👉 SL: Close Long at {sl_price}")
                print(f"👉 TP: Close Long at {tp_price}")
                return
            else:
                print(f"❌ Order attempt {i+1} failed: {result}")
        except Exception as e:
            print(f"⚠️ Connection attempt {i+1} failed: {e}")
            time.sleep(2)
    
    print("\n❌ All attempts failed. Please try running the script manually from your terminal.")

if __name__ == "__main__":
    place_sol_futures_limit_order(40)
