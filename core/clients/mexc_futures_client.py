import os
import time
import hmac
import hashlib
import requests
import urllib.parse
from dotenv import load_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class MEXCFuturesClient:
    """
    Client for MEXC Futures (Contract) API.
    Base URL: https://contract.mexc.com
    """
    def __init__(self):
        self.access_key = os.getenv('MEXC_ACCESS_KEY')
        self.secret_key = os.getenv('MEXC_SECRET_KEY')
        self.base_url = "https://contract.mexc.com"

    def _get_server_time(self):
        url = f"{self.base_url}/api/v1/contract/ping"
        response = requests.get(url, verify=False)
        return response.json().get('data', int(time.time() * 1000))

    def _sign(self, timestamp, body_str=""):
        # MEXC Contract V1 signature: apiKey + reqTime + body
        # For POST, body_str is the JSON payload. For GET, it's the query string.
        message = f"{self.access_key}{timestamp}{body_str}"
        return hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def get_account_assets(self):
        """Get futures account assets (private)."""
        endpoint = "/api/v1/private/account/assets"
        timestamp = int(time.time() * 1000)
        
        signature = self._sign(timestamp)
        
        headers = {
            'ApiKey': self.access_key,
            'Request-Time': str(timestamp),
            'Signature': signature
        }
        
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=headers, verify=False)
        return response.json()

    def get_positions(self, symbol=None):
        """Get open positions (private)."""
        endpoint = "/api/v1/private/position/open_positions"
        timestamp = int(time.time() * 1000)
        params = {}
        if symbol:
            params["symbol"] = symbol
            
        params_str = urllib.parse.urlencode(sorted(params.items()))
        signature = self._sign(timestamp, params_str)
        
        headers = {
            'ApiKey': self.access_key,
            'Request-Time': str(timestamp),
            'Signature': signature
        }
        
        url = f"{self.base_url}{endpoint}"
        if params_str:
            url += f"?{params_str}"
            
        print(f"DEBUG GET: {url}")
        response = requests.get(url, headers=headers, verify=False)
        return response.json()

    def change_leverage(self, symbol, leverage, side=None):
        """Change leverage for a symbol (private)."""
        endpoint = "/api/v1/private/position/change_leverage"
        timestamp = int(time.time() * 1000)
        
        params = {
            "symbol": symbol,
            "leverage": int(leverage)
        }
        if side:
            params["positionType"] = int(side)
            
        import json
        body_str = json.dumps(params, separators=(',', ':'))
        signature = self._sign(timestamp, body_str)
        
        headers = {
            'ApiKey': self.access_key,
            'Request-Time': str(timestamp),
            'Signature': signature,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        print(f"DEBUG POST: {url} | Body: {body_str}")
        response = requests.post(url, data=body_str, headers=headers, verify=False)
        return response.json()

    def create_order(self, symbol, side, order_type, vol, leverage, price=None, open_type=1):
        """
        Place a futures order.
        side: 1=Open Long, 2=Close Short, 3=Open Short, 4=Close Long
        order_type: 1=Limit, 5=Market
        open_type: 1=Isolated, 2=Cross
        """
        endpoint = "/api/v1/private/order/create"
        timestamp = int(time.time() * 1000)
        
        params = {
            "symbol": symbol,
            "price": float(price) if price else 0,
            "vol": float(vol),
            "side": int(side),
            "type": int(order_type),
            "openType": int(open_type),
            "leverage": int(leverage)
        }
        
        import json
        body_str = json.dumps(params, separators=(',', ':'))
        signature = self._sign(timestamp, body_str)
        
        headers = {
            'ApiKey': self.access_key,
            'Request-Time': str(timestamp),
            'Signature': signature,
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        print(f"DEBUG POST: {url} | Body: {body_str}")
        response = requests.post(url, data=body_str, headers=headers, verify=False)
        return response.json()

    def get_funding_rate(self, symbol):
        """Get public funding rate for a symbol."""
        # Symbol format for this endpoint: BTC_USDT
        endpoint = f"/api/v1/contract/funding_rate/{symbol}"
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, verify=False, timeout=10)
            data = response.json()
            if data.get('success'):
                return data['data'].get('fundingRate', 0)
            return 0
        except Exception as e:
            print(f"⚠️ Error fetching funding rate: {e}")
            return 0

if __name__ == "__main__":
    client = MEXCFuturesClient()
    print("Testing Futures Account Assets:")
    print(client.get_account_assets())
    
    print("\nTesting Leverage Change (SOL_USDT to 5x):")
    # Using SOL_USDT as symbol format for Futures
    print(client.change_leverage("SOL_USDT", 5))
