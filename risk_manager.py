import math

def calculate_risk(capital=20.0, risk_pct=2.5, entry_price=123.0, sl_price=121.77):
    """
    Calculate position size and leverage for Futures.
    
    capital: Total USDT in Futures wallet.
    risk_pct: % of capital to lose if SL is hit.
    entry_price: Planned entry price.
    sl_price: Technical Stop Loss price.
    """
    
    # 1. Amount to risk in USDT
    amount_to_risk = capital * (risk_pct / 100)
    
    # 2. Price difference to SL
    price_diff_pct = abs(entry_price - sl_price) / entry_price
    
    # 3. Required Position Size (National Value) to lose exactly amount_to_risk
    # Position Size * Price_Diff_Pct = Amount_to_Risk
    position_size_usdt = amount_to_risk / price_diff_pct
    
    # 4. Appropriate Leverage
    # Leverage = Position Size / Margin (Capital)
    # However, since we only use $20, we can use higher leverage to control a larger 'notional' size
    leverage = position_size_usdt / capital
    
    # 5. Contract Quantity (Assuming SOL_USDT contract size is 1 SOL or 0.1 SOL)
    # Check MEXC SOLUSDT contract size (usually 1 unit = 0.1 SOL)
    contract_size = 0.1 # Example for SOL
    qty_contracts = position_size_usdt / (entry_price * contract_size)
    
    return {
        "capital": capital,
        "risk_to_lose_usdt": amount_to_risk,
        "price_to_sl_pct": price_diff_pct * 100,
        "notional_position_usdt": position_size_usdt,
        "recommended_leverage": math.ceil(leverage),
        "qty_to_order_contracts": math.floor(qty_contracts * 10) / 10,
        "reward_1_2_tp": entry_price + (entry_price - sl_price) * 2
    }

if __name__ == "__main__":
    # Example for SOL at 123.50 with SL at 122.0
    res = calculate_risk(capital=20.0, risk_pct=3.0, entry_price=123.5, sl_price=122.0)
    print("--- Risk Management Report ($20 Capital) ---")
    print(f"Capital: ${res['capital']}")
    print(f"Risk per Trade (3%): ${res['risk_to_lose_usdt']:.2f}")
    print(f"Distance to SL: {res['price_to_sl_pct']:.2f}%")
    print(f"Notional Position Size: ${res['notional_position_usdt']:.2f}")
    print(f"Recommended Leverage: {res['recommended_leverage']}x")
    print(f"TP Target (1:2): ${res['reward_1_2_tp']:.2f}")
