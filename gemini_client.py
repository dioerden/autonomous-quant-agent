import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    """
    Client for Institutional-Grade Sentiment Analysis using Gemini AI.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️ GEMINI_API_KEY not found in .env file.")
            self.model = None
            return
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze_sentiment(self, headlines):
        """
        Analyzes a list of news headlines and returns a sentiment score.
        Score range: -1.0 (Bearish) to 1.0 (Bullish)
        """
        if not self.model or not headlines:
            return 0.0
            
        prompt = f"Analyze the following crypto news headlines and provide a single sentiment score from -1.0 (extremely bearish) to 1.0 (extremely bullish). Only return the numeric score:\n\n"
        prompt += "\n".join(headlines)
        
        try:
            response = self.model.generate_content(prompt)
            score_str = response.text.strip()
            # Basic cleaning to handle potential text around the number
            import re
            match = re.search(r"[-+]?\d*\.\d+|\d+", score_str)
            if match:
                score = float(match.group())
                return max(-1.0, min(1.0, score))
            return 0.0
        except Exception as e:
            print(f"⚠️ Error with Gemini AI: {e}")
            return 0.0

if __name__ == "__main__":
    client = GeminiClient()
    test_headlines = [
        "Bitcoin breaks $100k as institutional demand surges",
        "SEC approves more spot crypto ETFs",
        "Major hack results in massive drain from exchange"
    ]
    print(f"Test Sentiment Score: {client.analyze_sentiment(test_headlines)}")
