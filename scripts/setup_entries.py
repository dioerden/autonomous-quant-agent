def setup_entries():
    print("🛠️ SETUP ENTRIES: SOLUSDT (NY Session)")
    print("-" * 50)
    
    # Strategy Parameters
    limit_price = 125.55
    sl_price = 124.90
    tp_price = 128.00
    
    # Position Sizing Logic (Approximate)
    capital_usdt = 22.0
    leverage = 10
    total_position_size = capital_usdt * leverage # $220
    quantity_sol = total_position_size / limit_price
    
    print("📋 COPIED TO CLIPBOARD (Manual Entry):")
    print(f"1. PAIR:        SOL USDT (Perpetual)")
    print(f"2. LEVERAGE:    {leverage}x (Isolated)")
    print(f"3. ORDER 1:     LIMIT BUY @ {limit_price}")
    print(f"   - Size:      {quantity_sol:.2f} SOL (~50% of Balance)")
    print(f"   - SL:        {sl_price}")
    print(f"   - TP:        {tp_price}")
    print("-" * 50)
    print("4. ORDER 2:     MARKET BUY (Ready)")
    print("   - Logic:     If price stays > 126.00 for 5 mins")
    print("   - Size:      Remaining 50% Balance")
    print("-" * 50)
    print("⚠️ EXECUTION NOTE:")
    print("   Set the LIMIT order now.")
    print("   Keep 'Market Buy' button ready if it pumps early.")

if __name__ == "__main__":
    setup_entries()
