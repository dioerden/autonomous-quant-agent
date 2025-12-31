import time
import os
from mexc_client import MEXCClient
from core.logic.strategy import HybridStrategy
from core.clients.sentiment_engine import SentimentEngine

def main():
    symbol = "SOLUSDT"
    amount_usdt = 20.0 # Initial trade size
    
    print(f"🤖 Starting Quant Bot for {symbol}...")
    print(f"Goal: Grow {amount_usdt} USDT to 100 USDT")
    
    client = MEXCClient()
    strategy = HybridStrategy(symbol)
    
    # Check if API keys are set
    acc_info = client.get_account_info()
    if 'error' in acc_info:
        print(f"❌ API Error: {acc_info['error']}")
        print("Please ensure MEXC_ACCESS_KEY and MEXC_SECRET_KEY are set in .env")
        return

    print("✅ API Connection Successful.")
    
    # Initial balance check to see if we're already in a trade
    try:
        balances = client.get_account_info().get('balances', [])
        asset_symbol = symbol.replace("USDT", "")
        initial_asset_balance = float(next((b['free'] for b in balances if b['asset'] == asset_symbol), 0))
        if initial_asset_balance > 0.1: # Threshold for a trade
            print(f"⚠️ Detected existing {asset_symbol} balance ({initial_asset_balance}). Monitoring for exit...")
            # We don't know the entry price if the bot just started, so we use current price as fallback
            strategy.entry_price = float(client.get_ticker(symbol)['price'])
    except:
        pass

    while True:
        try:
            result = strategy.get_signals()
            signal = result['signal']
            price = result['price']
            inds = result.get('indicators', {})
            ai_opinion = result.get('ai_opinion', 'N/A')
            
            # Calculate PNL if in trade
            pnl_str = ""
            if strategy.entry_price:
                pnl = (price - strategy.entry_price) / strategy.entry_price * 100
                pnl_str = f" | PNL: {pnl:+.2f}%"
            
            log_msg = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Price: {price:,.2f} | EMA9: {inds.get('ema9', 0):,.2f} | AI: {ai_opinion} | Signal: {signal}{pnl_str}"
            print(log_msg)
            
            if "BUY" in signal:
                print(f"🚀 BUY Signal Triggered! Ordering {amount_usdt} USDT worth of {symbol}...")
                order_result = client.create_order(
                    symbol=symbol,
                    side="BUY",
                    order_type="MARKET",
                    quoteOrderQty=amount_usdt
                )
                if 'orderId' in order_result:
                    print(f"✅ BUY Order Success: {order_result['orderId']}")
                    strategy.entry_price = price # Set entry price on success
                else:
                    print(f"❌ BUY Order Failed: {order_result}")
                    
            elif "SELL" in signal:
                print(f"🔻 {signal} Triggered! Selling all {symbol}...")
                balances = client.get_account_info().get('balances', [])
                asset_balance = next((b['free'] for b in balances if b['asset'] == asset_symbol), 0)
                
                if float(asset_balance) > 0:
                    order_result = client.create_order(
                        symbol=symbol,
                        side="SELL",
                        order_type="MARKET",
                        quantity=asset_balance
                    )
                    if 'orderId' in order_result:
                        print(f"✅ SELL Order Success: {order_result['orderId']}")
                        strategy.entry_price = None # Reset on success
                    else:
                        print(f"❌ SELL Order Failed: {order_result}")
                else:
                    print("⚠️ No balance to sell.")
                    strategy.entry_price = None # Reset if no balance anyway

            time.sleep(30) 
            
        except Exception as e:
            print(f"⚠️ Error in loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
