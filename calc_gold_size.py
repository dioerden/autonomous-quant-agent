import requests

def calc_gold_size():
    print("✨ CALCULATING GOLD (XAU) POSITION SIZE...")
    
    # User Context
    capital_usdt = 10.0  # Remaining balance approx
    leverage = 50        # Gold allows high leverage
    buying_power = capital_usdt * leverage # $500
    
    try:
        # Fetch Live Price (CoinGecko fallback)
        url = "https://api.coingecko.com/api/v3/simple/price?ids=tether-gold&vs_currencies=usd"
        resp = requests.get(url, verify=False, timeout=10)
        data = resp.json()
        price = data['tether-gold']['usd'] # XAUT ~ XAU
        
        # Calculate Quantity (Oz)
        # MEXC usually trades in 0.01 increments for Gold
        quantity_oz = buying_power / price
        
        # Safety Buffer (90% of max)
        safe_quantity = quantity_oz * 0.9
        
        print("-" * 50)
        print(f"💰 Gold Price:   ${price:,.2f}")
        print(f"💳 Margin:       ${capital_usdt:.2f} (Lev {leverage}x)")
        print(f"🔫 Buying Power: ${buying_power:.2f}")
        print("-" * 50)
        print(f"👉 MAX QUANTITY: {quantity_oz:.4f} Oz")
        print(f"✅ SAFE INPUT:   {int(safe_quantity * 100) / 100} (Human Readable)")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Manual Fallback Estimate (Price ~2650)
        est_price = 2650
        est_qty = (500 / est_price) * 0.9
        print(f"⚠️ Using Est. Price ${est_price}")
        print(f"👉 SAFE INPUT:   {int(est_qty * 100) / 100}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    calc_gold_size()
