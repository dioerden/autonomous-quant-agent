from mexc_client import MEXCClient
client = MEXCClient()
for s in ["SOLUSDT", "BTCUSDT", "ETHUSDT"]:
    ticker = client.get_ticker_24h(s)
    print(f"{s}: {ticker.get('lastPrice')}")
