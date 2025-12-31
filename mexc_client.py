import os
import time
import hmac
import hashlib
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

class MEXCClient:
    def __init__(self):
        self.access_key = os.getenv('MEXC_ACCESS_KEY')
        self.secret_key = os.getenv('MEXC_SECRET_KEY')
        self.base_url = os.getenv('BASE_URL', 'https://api.mexc.com')
        # Robust Endpoint List
        self.endpoints = [
            "https://api.mexc.com",
            "https://api.mexc.so", 
            "https://api.coingecko.com/api/v3" # Fallback for public data only
        ]

    def _safe_request(self, method, endpoint, params=None, headers=None):
        """
        Robust request wrapper with rotation logic.
        """
        for i, base_url in enumerate(self.endpoints):
            try:
                # Adjust for CoinGecko fallback on specific public endpoints
                if "coingecko" in base_url:
                    if "ticker/price" in endpoint or "klines" in endpoint:
                        # Map to CoinGecko equivalent (Simplified)
                        # Only supports simple price check for now
                        symbol = params.get("symbol", "").replace("USDT", "").lower() if params else ""
                        if not symbol: continue
                        cg_url = f"{base_url}/simple/price?ids={symbol}&vs_currencies=usd"
                        resp = requests.get(cg_url, verify=False, timeout=5)
                        data = resp.json()
                        if "ticker" in endpoint:
                            # Mimic MEXC response structure
                            return {"symbol": params.get("symbol"), "price": str(data.get(symbol, {}).get("usd", 0))}
                        continue # Skip others for CG
                    else:
                        continue # Skip private/complex endpoints for CG

                url = f"{base_url}{endpoint}"
                if method == "GET":
                    response = requests.get(url, params=params, headers=headers, verify=False, timeout=5)
                else:
                    response = requests.post(url, headers=headers, verify=False, timeout=5)
                
                return response.json()
                
            except Exception as e:
                # print(f"\r⚠️ API Error ({base_url}): {str(e)}. Switching...", end="")
                time.sleep(1)
                continue
        
        # If all fail
        return {"error": "All endpoints failed"}

    def _get_server_time(self):
        # Time is critical, only trust MEXC
        for base in self.endpoints[:2]:
            try:
                url = f"{base}/api/v3/time"
                response = requests.get(url, verify=False, timeout=5)
                return response.json()['serverTime']
            except: continue
        return int(time.time() * 1000)

    def _sign(self, query_string):
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def create_order(self, symbol, side, order_type, quantity=None, quoteOrderQty=None, price=None):
        if not self.access_key or not self.secret_key:
            return {"error": "API Keys not configured in .env"}

        endpoint = "/api/v3/order"
        timestamp = self._get_server_time()
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "timestamp": timestamp,
            "recvWindow": 5000
        }
        
        if quantity:
            params['quantity'] = quantity
        if quoteOrderQty:
            params['quoteOrderQty'] = quoteOrderQty
        if price:
            params['price'] = price
        if order_type == "LIMIT" and not price:
            return {"error": "Price is required for LIMIT orders"}

        import urllib.parse
        query_string = urllib.parse.urlencode(sorted(params.items()))
        signature = self._sign(query_string)
        
        headers = {
            'X-MEXC-APIKEY': self.access_key
        }
        
        # Order placement MUST try reliable endpoints first
        for base in self.endpoints[:2]:
            try: 
                url = f"{base}{endpoint}?{query_string}&signature={signature}"
                response = requests.post(url, headers=headers, verify=False, timeout=5)
                return response.json()
            except: continue
            
        return {"error": "Failed to place order (Network Limit)"}

    def get_account_info(self):
        if not self.access_key or not self.secret_key:
            return {"error": "API Keys not configured in .env"}

        endpoint = "/api/v3/account"
        timestamp = self._get_server_time()
        params = {
            "timestamp": timestamp,
            "recvWindow": 5000
        }
        import urllib.parse
        query_string = urllib.parse.urlencode(sorted(params.items()))
        signature = self._sign(query_string)
        
        headers = {
            'X-MEXC-APIKEY': self.access_key
        }
        
        for base in self.endpoints[:2]:
            try:
                url = f"{base}{endpoint}?{query_string}&signature={signature}"
                response = requests.get(url, headers=headers, verify=False, timeout=5)
                return response.json()
            except: continue
        return {"error": "Failed to fetch account"}

    def get_ticker(self, symbol="BTCUSDT"):
        endpoint = "/api/v3/ticker/price"
        params = {"symbol": symbol}
        return self._safe_request("GET", endpoint, params)

    def get_klines(self, symbol, interval, limit=500):
        """
        Get K-line data (candlesticks).
        Intervals: 1m, 5m, 15m, 30m, 60m, 4h, 1d, 1W, 1M
        """
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        # KLines is strict on format, avoid CoinGecko for now as it's complex to map
        for base in self.endpoints[:2]:
            try:
                url = f"{base}{endpoint}"
                # print(f"DEBUG: Fetching KLines from {url}") 
                response = requests.get(url, params=params, verify=False, timeout=10)
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception as e:
                # print(f"DEBUG: KLines error {base}: {e}")
                continue
        return []

    def get_ticker_24h(self, symbol):
        """
        Get 24-hour ticker price change statistics.
        """
        endpoint = "/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        # Ticker 24h also strict
        for base in self.endpoints[:2]:
            try:
                url = f"{base}{endpoint}"
                response = requests.get(url, params=params, verify=False, timeout=5)
                return response.json()
            except: continue
        return {}

if __name__ == "__main__":
    client = MEXCClient()
    # Test Public Ticker
    print("Testing Public Ticker (BTCUSDT):")
    print(client.get_ticker("BTCUSDT"))
