import time
import requests
from mexc_client import MEXCClient

def emergency_market_buy(symbol="SOLUSDT", amount_usdt=50):
    print(f"🚨 EMERGENCY MARKET BUY: {symbol} | Amount: {amount_usdt} USDT")
    client = MEXCClient()
    
    # Session handling to prevent connection resets
    session = requests.Session()
    
    for i in range(10): # 10 attempts
        try:
            print(f"🔄 Attempt {i+1}/10...")
            result = client.create_order(
                symbol=symbol,
                side="BUY",
                order_type="MARKET",
                quoteOrderQty=amount_usdt
            )
            
            if 'orderId' in result:
                print("✅ SUCCESS! Order placed successfully.")
                print(f"Order ID: {result['orderId']}")
                return True
            else:
                print(f"⚠️ API Error: {result}")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
        
        time.sleep(1) # Wait 1 second before retry
        
    print("💀 All attempts failed. Please enter manually on MEXC UI!")
    return False

if __name__ == "__main__":
    emergency_market_buy("SOLUSDT", 50)
