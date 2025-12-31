import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MacroClient:
    """
    Client to fetch Macro Economic data like DXY (US Dollar Index).
    """
    def __init__(self):
        # We use a public finance API endpoint to get DXY
        self.dxy_url = "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y=F"

    def get_dxy_trend(self):
        """
        Fetches the current DXY price and trend (24h change).
        Returns:
            dict: {
                "price": float,
                "change_pct": float,
                "sentiment": str (BEARISH/BULLISH)
            }
        """
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        try:
            response = requests.get(self.dxy_url, headers=headers, verify=False, timeout=10)
            data = response.json()
            
            meta = data['chart']['result'][0]['meta']
            current_price = meta['regularMarketPrice']
            prev_close = meta['previousClose']
            
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # For Crypto, DXY UP = BAD (Bearish), DXY DOWN = GOOD (Bullish)
            sentiment = "BULLISH" if change_pct < 0 else "BEARISH"
            
            return {
                "price": current_price,
                "change_pct": change_pct,
                "sentiment": sentiment
            }
        except Exception as e:
            # Fallback: Treat as Neutral to avoid breaking strategy
            return {
                "price": 0,
                "change_pct": 0,
                "sentiment": "NEUTRAL"
            }

if __name__ == "__main__":
    client = MacroClient()
    print(f"Current Macro (DXY) Status: {client.get_dxy_trend()}")
