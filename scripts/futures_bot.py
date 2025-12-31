import time
import os
from mexc_futures_client import MEXCFuturesClient
from strategy import HybridStrategy

def main():
    symbol = "SOL_USDT" # Futures symbol format
    amount_vol = 10 # 10 units (Check contract size, SOL_USDT is usually 0.1 SOL per unit)
    leverage = 10 # 10x leverage
    
    print(f"🚀 Starting HIGH-RISK Futures Bot for {symbol}...")
    print(f"Leverage: {leverage}x | Target: Aggressive Capital Growth")
    
    client = MEXCFuturesClient()
    strategy = HybridStrategy(symbol.replace("_", "")) # Strategy uses SOLUSDT
    
    # Check if API keys and permissions are ready
    try:
        acc_info = client.get_account_assets()
        if 'code' in acc_info and acc_info['code'] != 0:
            print(f"❌ API Error: {acc_info.get('message')}")
            return
        print("✅ Futures API Connection Successful.")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # Sync initial position if any
    try:
        positions = client.get_positions(symbol).get('data', [])
        if positions:
            for pos in positions:
                if float(pos['vol']) > 0:
                    print(f"⚠️ Existing Position Detected: {pos['positionType']} | Vol: {pos['vol']}")
                    strategy.entry_price = float(pos['avgEntryPrice'])
                    strategy.position_type = "LONG" if pos['positionType'] == 1 else "SHORT"
    except:
        pass

    while True:
        try:
            result = strategy.get_signals()
            signal = result['signal']
            price = result['price']
            inds = result.get('indicators', {})
            ai_opinion = result.get('ai_opinion', 'N/A')
            
            pnl_str = ""
            if strategy.entry_price:
                if strategy.position_type == "LONG":
                    pnl = (price - strategy.entry_price) / strategy.entry_price * 100 * leverage
                else: # SHORT
                    pnl = (strategy.entry_price - price) / strategy.entry_price * 100 * leverage
                pnl_str = f" | PNL: {pnl:+.2f}%"
            
            log_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Price: {price:,.2f} | AI: {ai_opinion} | Signal: {signal}{pnl_str}"
            print(log_msg)
            
            if signal == "BUY" or signal == "BUY (AI DRIVEN)":
                print(f"🔥 OPEN LONG Triggered! Leverage: {leverage}x")
                res = client.create_order(symbol, 1, 5, amount_vol, leverage) # 1=Open Long, 5=Market
                if res.get('success'):
                    print(f"✅ LONG Order Success!")
                    strategy.entry_price = price
                    strategy.position_type = "LONG"
                else:
                    print(f"❌ Error: {res}")
                    
            elif signal == "SHORT":
                print(f"📉 OPEN SHORT Triggered! Leverage: {leverage}x")
                res = client.create_order(symbol, 3, 5, amount_vol, leverage) # 3=Open Short, 5=Market
                if res.get('success'):
                    print(f"✅ SHORT Order Success!")
                    strategy.entry_price = price
                    strategy.position_type = "SHORT"
                else:
                    print(f"❌ Error: {res}")

            elif "SELL" in signal or "COVER" in signal:
                print(f"⚡ EXIT Triggered: {signal}")
                # side: 2=Close Short, 4=Close Long
                side = 4 if strategy.position_type == "LONG" else 2
                res = client.create_order(symbol, side, 5, amount_vol, leverage)
                if res.get('success'):
                    print(f"✅ Exit Success!")
                    strategy.entry_price = None
                    strategy.position_type = None
                else:
                    print(f"❌ Exit Failed: {res}")

            time.sleep(30)
            
        except Exception as e:
            print(f"⚠️ Loop Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
