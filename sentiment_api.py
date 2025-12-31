import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FearGreedClient:
    """
    Client to fetch market sentiment data from Alternative.me API.
    """
    def __init__(self):
        self.base_url = "https://api.alternative.me/fng/"

    def get_fng_index(self):
        """
        Fetches the current Fear & Greed Index.
        Returns:
            dict: {
                "value": str,
                "value_classification": str,
                "timestamp": str,
                "time_until_update": str
            }
        """
        try:
            response = requests.get(self.base_url, verify=False, timeout=10)
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                result = data["data"][0]
                return {
                    "value": int(result["value"]),
                    "classification": result["value_classification"],
                    "timestamp": result["timestamp"]
                }
        except Exception as e:
            print(f"⚠️ Error fetching Fear & Greed Index: {e}")
        return None

if __name__ == "__main__":
    client = FearGreedClient()
    print(f"Current Market Sentiment: {client.get_fng_index()}")
