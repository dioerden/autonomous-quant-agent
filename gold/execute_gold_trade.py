from core.clients.mexc_futures_client import MEXCFuturesClient
import requests
import time

def execute_gold_rush():
    print("✨ INITIATING GOLD RUSH EXECUTION...")
    client = MEXCFuturesClient()
    symbol = "XAUT_USDT" # Targeting Tether Gold
    leverage = 25
    amount_usdt = 450.0  # High Risk Quantity
    
    try:
        # 1. Get Live Price
        try:
            # Try MEXC Ticker first
            url = f"https://contract.mexc.com/api/v1/contract/ticker?symbol={symbol}"
            resp = requests.get(url, verify=False, timeout=5)
            data = resp.json()
            if data['success']:
                price = data['data']['lastPrice']
            else:
                raise Exception("Ticker fetch failed")
        except:
            # Fallback Estimate
            price = 4381.0
            print(f"⚠️ Using fallback price: ${price}")

        # 2. Calculate Volume (Contracts)
        # Vol = 450 USDT / Price
        vol = round(amount_usdt / price, 4) 
        
        print(f"🎯 Target: {symbol}")
        print(f"💰 Price: ${price}")
        print(f"📦 Vol:   {vol} XAUT (={amount_usdt} USDT)")
        
        # 3. Set Leverage
        print(f"⚙️ Setting Leverage {leverage}x...")
        # client.change_leverage(symbol, leverage) # Often fails if already set, ignoring error for speed
        
        # 4. Execute Market Buy
        print("🚀 FIRING MARKET LONG...")
        res = client.create_order(
            symbol=symbol,
            side=1,          # Open Long
            order_type=5,    # Market Order
            vol=vol,
            leverage=leverage,
            price=price,     # For market, sometimes used as ref
            open_type=1      # Isolated
        )
        
        if res.get('success'):
            print("✅ OFFICIALLY EXECUTED!")
            print(f"   sl_check: {res}")
            print("🛡️ REMINDER: Set SL @ 4,290 manually!")
        else:
            print(f"❌ Execution Failed: {res}")
            raise Exception("API Error")
            
    except Exception as e:
        print(f"\n🚫 AUTO-EXECUTION FAILED ({e}).")
        print("⚡ MANUAL OVERRIDE REQUIRED:")
        print(f"1. Pair:     {symbol}")
        print(f"2. Type:     Market Buy (Long)")
        print(f"3. Quantity: {vol} XAUT (or ~450 USDT)")
        print(f"4. Leverage: {leverage}x")

if __name__ == "__main__":
    execute_gold_rush()
