import time
import os
import sys
from mexc_client import MEXCClient

def create_progress_bar(current, start, end, width=40):
    progress = (current - start) / (end - start)
    progress = max(0, min(1, progress)) # Clamp between 0 and 1
    filled = int(width * progress)
    bar = "█" * filled + "░" * (width - filled)
    percent = progress * 100
    return f"[{bar}] {percent:.2f}%"

def run_dashboard():
    # Phase 1 Config
    START_BAL = 20.0
    TARGET_BAL = 200.0
    
    # Active Trade Data
    SYMBOL = "SOLUSDT"
    ENTRY_PRICE = 123.93
    MARGIN = 19.82
    SIZE_USDT = 99.13
    
    client = MEXCClient()
    
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            
            ticker = client.get_ticker_24h(SYMBOL)
            current_price = float(ticker.get('lastPrice', 0))
            
            if current_price == 0:
                print("⚠️ Waiting for market data...")
                time.sleep(5)
                continue
                
            # Calculate PNL & Current Bal
            pnl_usdt = (current_price - ENTRY_PRICE) * (SIZE_USDT / ENTRY_PRICE)
            current_bal = START_BAL + pnl_usdt
            
            # Formatting
            color = "\033[92m" if pnl_usdt >= 0 else "\033[91m"
            reset = "\033[0m"
            
            print("=" * 60)
            print(f"🚀 QUANT TRADE AI - MISSION: PHASE 1 ($20 ➔ $200)")
            print("=" * 60)
            
            # Progress Section
            print(f"\n📈 GLOBAL PROGRESS TO $200")
            print(create_progress_bar(current_bal, START_BAL, TARGET_BAL))
            print(f"Current Balance: ${current_bal:.2f} | Remaining: ${TARGET_BAL - current_bal:.2f}")
            
            # Active Position Section
            print(f"\n🔥 ACTIVE POSITION: {SYMBOL} 5X LONG")
            print(f"Entry: ${ENTRY_PRICE:<8} | Price: ${current_price:<8}")
            print(f"Live PNL: {color}{pnl_usdt:>+6.2f} USDT ({ (pnl_usdt/MARGIN)*100 :>+6.2f}%){reset}")
            
            # Recommendation
            print(f"\n💡 STRATEGY STATUS:")
            if pnl_usdt > 0:
                print(">>> Position in PROFIT. Holding towards TP $127.10.")
            else:
                print(">>> Price accumulating. Structure remains Bullish.")
            
            print("\n" + "=" * 60)
            print(f"Last Update: {time.strftime('%H:%M:%S')} WIB | Ctrl+C to Exit")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard closed.")

if __name__ == "__main__":
    run_dashboard()
