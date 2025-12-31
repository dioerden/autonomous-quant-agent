import re
from core.clients.sentiment_api import FearGreedClient
from core.clients.gemini_client import GeminiClient

class SentimentEngine:
    """
    A simple sentiment engine that analyzes news text for market signals.
    """
    def __init__(self):
        self.bullish_keywords = [
            'bullish', 'surge', 'pump', 'breakout', 'growth', 'partnership', 
            'adoption', 'listing', 'buy', 'positive', 'green', 'moon'
        ]
        self.bearish_keywords = [
            'bearish', 'drop', 'dump', 'crash', 'negative', 'sell', 'red', 
            'scam', 'hack', 'regulation', 'ban', 'fud'
        ]
        self.fng_client = FearGreedClient()
        self.gemini_client = GeminiClient()

    def analyze_text(self, text):
        """
        Analyzes the sentiment of a given text.
        Returns a score between -1 (highly bearish) and 1 (highly bullish).
        """
        text = text.lower()
        bull_count = sum(len(re.findall(f'\\b{word}\\b', text)) for word in self.bullish_keywords)
        bear_count = sum(len(re.findall(f'\\b{word}\\b', text)) for word in self.bearish_keywords)
        
        total = bull_count + bear_count
        if total == 0:
            return 0
        
        return (bull_count - bear_count) / total

    def get_market_sentiment(self, symbol, news_headlines):
        """
        Aggregates sentiment from multiple headlines using AI and Keywords.
        """
        if not news_headlines:
            return "NEUTRAL"
            
        # 1. Headline Sentiment (Gemini AI)
        gemini_score = self.gemini_client.analyze_sentiment(news_headlines)
        
        # 2. Headline Sentiment (Keyword Fallback)
        keyword_scores = [self.analyze_text(h) for h in news_headlines]
        avg_keyword_score = sum(keyword_scores) / len(keyword_scores)
        
        # Hybrid Score (60% AI, 40% Keyword)
        avg_score = (gemini_score * 0.6) + (avg_keyword_score * 0.4)
        
        if avg_score > 0.1:
            return "BULLISH"
        elif avg_score < -0.1:
            return "BEARISH"
        else:
            return "NEUTRAL"

    def get_fear_greed_score(self):
        """
        Returns a consolidated market sentiment score using external API.
        """
        fng = self.fng_client.get_fng_index()
        if fng:
            return fng # Returns dict with value and classification
        return {"value": 50, "classification": "Neutral (Default)"}

if __name__ == "__main__":
    engine = SentimentEngine()
    test_headlines = [
        "Bitcoin surges past 100k as institutional adoption grows",
        "New partnership announced for crypto payment system",
        "Market sentiment turns negative amid regulatory concerns"
    ]
    print(f"Aggregated Sentiment: {engine.get_market_sentiment('BTC', test_headlines)}")
