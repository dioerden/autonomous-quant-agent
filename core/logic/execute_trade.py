import sys
from mexc_client import MEXCClient

def execute_at_market(symbol, side, amount_usdt):
    """Executes a market order with a specified USDT amount."""
    print(f"🚀 Preparing to {side} {amount_usdt} USDT on {symbol}...")
    client = MEXCClient()
    
    # Execute Market Order
    result = client.create_order(
        symbol=symbol,
        side=side,
        order_type="MARKET",
        quoteOrderQty=amount_usdt
    )
    
    if 'orderId' in result:
        print(f"✅ {side} Order Successful!")
        print(f"Order ID: {result['orderId']}")
        return result
    else:
        print(f"❌ {side} Order Failed.")
        print("Response:", result)
        return None

def main():
    # User request: Entry 20 USDT
    # Assuming BTCUSDT as discussed
    execute_at_market("BTCUSDT", "BUY", 20.0)

if __name__ == "__main__":
    main()
