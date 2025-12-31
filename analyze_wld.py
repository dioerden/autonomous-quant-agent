import sys
from mexc_client import MEXCClient
from indicators import calculate_ema, calculate_rsi, calculate_volume_profile, calculate_atr, calculate_bollinger_bands

def analyze_symbol(symbol="WLDUSDT"):
    client = MEXCClient()
    print(f"🔬 Deep Quantitative Analysis for: {symbol}")
    print("-" * 50)
    
    # 1. Fetch Data (Via CoinGecko for Resilience)
    # 1. Fetch Data (Via CoinGecko for Resilience)
    print("Fetch K-Lines (CoinGecko)...")
    try:
        # Simple Mapping
        cg_id = "worldcoin-wld"
        if "BTC" in symbol: cg_id = "bitcoin"
        elif "SOL" in symbol: cg_id = "solana"
        elif "ETH" in symbol: cg_id = "ethereum"
        
        # Get 5 days of data (auto-hourly interval)
        url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=usd&days=5"
        import requests
        resp = requests.get(url, verify=False, timeout=10)
        data = resp.json()
        
        prices = data.get('prices', [])
        total_volumes = data.get('total_volumes', [])
        
        if not prices:
            raise Exception("No price data")
            
        # Convert to OHLC-like format (approximate since CG only gives Price/Vol snapshots)
        # We will use the snapshot price as Close, and simulate Open from prev Close
        # This is sufficient for EMA/RSI trends.
        
        closes = [p[1] for p in prices]
        volumes = [v[1] for v in total_volumes]
        
        # Approximate High/Low for ATR (using simple variance if real H/L not available)
        # For better ATR, we ideally need real candle data.
        # But valid trend analysis (EMA/RSI) is possible with just Closes.
        highs = closes # Placeholder
        lows = closes  # Placeholder
        
        # Construct synthetic klines for Volume Profile
        # [time, open, high, low, close, volume]
        klines = []
        for i in range(len(prices)):
            p_time = prices[i][0]
            p_close = prices[i][1]
            p_vol = total_volumes[i][1]
            # Synth structure
            klines.append([p_time, p_close, p_close, p_close, p_close, p_vol])
            
        current_price = closes[-1]

    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return
    
    if not current_price: 
        print("❌ Analytical data missing")
        return
    
    # 2. Volatility Analysis (ATR & Bands)
    atr = calculate_atr(highs, lows, closes, 14)[-1]
    ma, upper, lower = calculate_bollinger_bands(closes, 20, 2)
    upper_band = upper[-1]
    lower_band = lower[-1]
    
    atr_pct = (atr / current_price) * 100
    
    # 3. Momentum & Trend
    ema21 = calculate_ema(closes, 21)[-1]
    ema50 = calculate_ema(closes, 50)[-1]
    rsi = calculate_rsi(closes, 14)[-1]
    
    # 4. Volume Profile
    poc = calculate_volume_profile(klines)
    
    # OUTPUT REPORT
    print(f"\n📊 MARKET STRUCTURE REPORT")
    print(f"Price: ${current_price:.4f}")
    
    print(f"\n1. VOLATILITY METRICS")
    print(f"   - ATR (14): {atr:.4f} ({atr_pct:.2f}%)")
    print(f"   - Band Width: {((upper_band - lower_band)/current_price)*100:.2f}%")
    print(f"   - Status: {'🔥 HIGH VOLATILITY' if atr_pct > 2.0 else '❄️ STABLE/COMPRESSED'}")
    
    print(f"\n2. TREND & MOMENTUM")
    print(f"   - RSI (14): {rsi:.2f} ({'OVERBOUGHT' if rsi>70 else 'OVERSOLD' if rsi<30 else 'NEUTRAL'})")
    print(f"   - Trend (EMA21): {'BULLISH' if current_price > ema21 else 'BEARISH'}")
    print(f"   - Dist from EMA21: {((current_price - ema21)/ema21)*100:.2f}%")
    
    print(f"\n3. VOLUME & LIQUIDITY")
    print(f"   - POC (Point of Control): ${poc:.4f}")
    print(f"   - Price vs POC: {'ABOVE (Demand)' if current_price > poc else 'BELOW (Supply)'}")
    
    print(f"\n🎯 QUANTITATIVE VERDICT")
    
    score = 0
    reasons = []
    
    if current_price > ema21: score += 1
    else: reasons.append("Price below EMA21 Trend")
    
    if current_price > poc: score += 1
    else: reasons.append("Price below Volume POC")
    
    if 40 < rsi < 65: score += 1
    else: reasons.append(f"RSI not optimal ({rsi:.1f})")
    
    if atr_pct > 1.0: score += 1 # We want volatility for WLD
    else: reasons.append("Volatility too low for scalp")
    
    print(f"   - Quant Score: {score}/4")
    if score >= 3:
        print("   - Action: ✅ POTENTIAL ENTRY (Wait for Trigger)")
    else:
        print("   - Action: ⚠️ CAUTION / WAIT")
        for r in reasons:
            print(f"     * {r}")
            
    # Calculate stop loss based on ATR
    sl_dist = atr * 1.5
    print(f"\n🛑 Risk Management (ATR Based)")
    print(f"   - Suggested Stop Loss Distance: ${sl_dist:.4f}")
    if current_price > ema21:
        print(f"   - Long SL: ${current_price - sl_dist:.4f}")
    else:
        print(f"   - Short SL: ${current_price + sl_dist:.4f}")

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "WLDUSDT"
    analyze_symbol(symbol)
