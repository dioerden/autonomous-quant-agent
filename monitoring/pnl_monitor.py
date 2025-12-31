import time
import requests
import urllib3

urllib3.disable_warnings()

def monitor_portfolio():
    print("🚀 QUANTUM PORTFOLIO MONITOR (NY SESSION)")
    print("-" * 60)
    
    # Active Trades Configuration
    trades = [
        {
            "name": "SOL_USDT (Scalp)",
            "symbol": "SOLUSDT",
            "coingecko_id": "solana",
            "entry": 126.18,
            "size_usdt": 100.0, # Approx
            "leverage": 10
        },
        {
            "name": "XAUT_USDT (Gold)",
            "symbol": "XAUT_USDT",
            "coingecko_id": "tether-gold",
            "entry": 4340.1,
            "size_usdt": 450.0, # High Risk
            "leverage": 25
        }
    ]
    
    # Endpoints
    sources = [
        "https://api.coingecko.com/api/v3/simple/price?ids=solana,tether-gold&vs_currencies=usd",
        "https://api.mexc.com/api/v3/ticker/price" # Backup
    ]
    
    total_pnl = 0.0
    
    try:
        while True:
            current_prices = {}
            
            # Fetch Data
            try:
                # Primary: CoinGecko (Batch fetch)
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.get(sources[0], headers=headers, verify=False, timeout=5)
                data = resp.json()
                
                if 'solana' in data:
                    current_prices['SOLUSDT'] = data['solana']['usd']
                if 'tether-gold' in data:
                    current_prices['XAUT_USDT'] = data['tether-gold']['usd']
                    
            except Exception as e:
                pass # Silent fail, try next loop or backup
                
            # Calc and Display
            output_lines = []
            session_pnl = 0.0
            
            for trade in trades:
                sym = trade['symbol']
                entry = trade['entry']
                size = trade['size_usdt']
                
                # Get price or fallback to entry (0 PNL) if data missing
                price = current_prices.get(sym, entry)
                
                # Calc PNL logic
                # PNL = (Price - Entry) * (Size / Entry)
                if price > 0:
                    qty = size / entry
                    pnl = (price - entry) * qty
                else:
                    pnl = 0
                
                session_pnl += pnl
                
                # Color code
                if pnl >= 0:
                    pnl_str = f"\033[92m+${pnl:.2f}\033[0m"
                else:
                    pnl_str = f"\033[91m-${abs(pnl):.2f}\033[0m"
                    
                output_lines.append(f"{trade['name']:<20} | Price: ${price:<8.2f} | PNL: {pnl_str}")
                
            # Total PNL Color
            if session_pnl >= 0:
                total_str = f"\033[92m+${session_pnl:.2f}\033[0m"
            else:
                total_str = f"\033[91m-${abs(session_pnl):.2f}\033[0m"

            # Print Block (Clear screen part simulation with \r)
            print(f"\r💰 TOTAL EST. PNL: {total_str}   ", end="")
            # We can't easily print multi-line with \r rewrites in simple terms, 
            # so we just print the one-liner Summary + Trade Details if changed significantly
            # For now, let's just cycle display or print status every few seconds
            
            # Simplified One-Liner for Terminal stability
            pnl_1 = output_lines[0].split('|')[-1].strip()
            pnl_2 = output_lines[1].split('|')[-1].strip()
            
            print(f"\r💎 SOL: {pnl_1} | 🥇 GOLD: {pnl_2} | 💰 NET: {total_str}    ", end="", flush=True)
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")

if __name__ == "__main__":
    monitor_portfolio()
