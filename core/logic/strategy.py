import torch
import torch.nn as nn
import os
from core.clients.mexc_client import MEXCClient
from core.clients.mexc_futures_client import MEXCFuturesClient # Add futures client
from core.logic.indicators import calculate_ema, calculate_rsi, calculate_fibonacci_levels, calculate_volume_profile
from core.clients.sentiment_engine import SentimentEngine
from core.clients.macro_api import MacroClient

# DQN Architecture (must match train_agent.py)
class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
    
    def forward(self, x):
        return self.fc(x)

class HybridStrategy:
    def __init__(self, symbol="SOLUSDT"):
        self.symbol = symbol
        self.client = MEXCClient()
        self.futures_client = MEXCFuturesClient() # Initialize futures client
        self.sentiment_engine = SentimentEngine()
        self.macro_client = MacroClient()
        self.entry_price = None
        self.stop_loss_pct = 0.015 # 1.5% Stop Loss
        self.take_profit_pct = 0.07  # 7% Take Profit (Aggressive Growth)
        self.position_type = None    # "LONG" or "SHORT"
        
        # Load AI Model
        self.model = None
        if os.path.exists("trading_agent.pth"):
            try:
                state_dim = torch.load("trading_agent_metadata.pth")
                self.model = DQN(state_dim, 3) # 3 actions: HOLD, BUY, SELL
                self.model.load_state_dict(torch.load("trading_agent.pth"))
                self.model.eval()
            except Exception as e:
                print(f"⚠️ Failed to load AI model: {e}")
        
    def check_killzone(self):
        """
        Check if current UTC time is within London, NY, or Tokyo Killzones.
        Tokyo: 00:00 - 03:00 UTC
        London: 07:00 - 10:00 UTC
        NY: 12:00 - 15:00 UTC (AM)
        """
        import datetime
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        hour = now_utc.hour
        
        if 0 <= hour < 3:
            return "TOKYO"
        elif 7 <= hour < 10:
            return "LONDON"
        elif 12 <= hour < 15:
            return "NEW YORK AM"
        elif 18 <= hour < 20:
            return "NEW YORK PM MACRO"
        return None

    def calculate_fvg(self, klines):
        """
        Calculate Fair Value Gaps (FVG).
        FVG exists if:
        Bullish: Low[i] > High[i-2]
        Bearish: High[i] < Low[i-2]
        """
        gaps = []
        if len(klines) < 3:
            return gaps
            
        # klines format: [time, open, high, low, close, ...]
        for i in range(2, len(klines)):
            curr_low = float(klines[i][3])
            curr_high = float(klines[i][2])
            prev2_high = float(klines[i-2][2])
            prev2_low = float(klines[i-2][3])
            
            # Bullish FVG
            if curr_low > prev2_high:
                gaps.append({
                    "type": "BULLISH_FVG",
                    "top": curr_low,
                    "bottom": prev2_high,
                    "index": i
                })
            # Bearish FVG
            elif curr_high < prev2_low:
                gaps.append({
                    "type": "BEARISH_FVG",
                    "top": prev2_low,
                    "bottom": curr_high,
                    "index": i
                })
        return gaps

    def get_signals(self, news_headlines=None):
        """
        FETCHES data from API and returns signals.
        """
        # 1. Fetch Market Data (CoinGecko Fallback for Reliability)
        klines = []
        try:
            # Map symbol for CoinGecko
            cg_id = "solana" if "SOL" in self.symbol else "bitcoin" if "BTC" in self.symbol else "worldcoin-wld"
            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart?vs_currency=usd&days=1"
            import requests
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, verify=False, timeout=10)
            data = resp.json()
            
            prices = data.get('prices', [])
            total_volumes = data.get('total_volumes', [])
            
            if prices:
                # Convert to MEXC-like structure [time, open, high, low, close, volume]
                # Approximation: we use price for all OHLC since we only have line data
                for i in range(len(prices)):
                    p_time = prices[i][0]
                    p_val = prices[i][1]
                    p_vol = total_volumes[i][1]
                    klines.append([p_time, p_val, p_val, p_val, p_val, p_vol])
                    
        except Exception as e:
            print(f"Fallback Fetch Error: {e}")

        # If fallback failed, try original client (likely blocked but worth a try)
        if not klines:
             klines = self.client.get_klines(self.symbol, "15m", limit=100)
             
        if not klines or len(klines) < 60:
            print(f"DEBUG: Klines Fetched: {len(klines)}")
            return {"error": "Insufficient data"}
            
        ticker_24h = {'priceChangePercent': 0} # simplified
        
        return self._calculate_signals(klines, ticker_24h, news_headlines)

    def get_signals_backtest(self, klines, news_headlines=None):
        """
        Uses PROVIDED klines (historical) and returns signals.
        """
        # Mock 24h ticker for backtest (using last 96 candles as a day)
        mock_ticker = {'priceChangePercent': 0}
        if len(klines) >= 96:
            start_p = float(klines[-96][4])
            end_p = float(klines[-1][4])
            mock_ticker['priceChangePercent'] = (end_p - start_p) / start_p * 100
            
        return self._calculate_signals(klines, mock_ticker, news_headlines)

    def _calculate_signals(self, klines, ticker_24h, news_headlines=None):
        """
        Core logic shared between Live and Backtest.
        """
        # MEXC Klines format: [time, open, high, low, close, volume, ...]
        closes = [float(k[4]) for k in klines]
        
        # 1. Technical Indicators
        ema9 = calculate_ema(closes, 9)
        ema21 = calculate_ema(closes, 21)
        rsi = calculate_rsi(closes, 14)
        
        curr_ema9 = ema9[-1]
        curr_ema21 = ema21[-1]
        curr_rsi = rsi[-1]
        
        prev_ema9 = ema9[-2]
        prev_ema21 = ema21[-2]
        
        # 2. Fundamental/Sentiment Data
        price_change_percent = float(ticker_24h.get('priceChangePercent', 0)) if ticker_24h else 0
        
        sentiment = "NEUTRAL"
        if news_headlines:
            sentiment = self.sentiment_engine.get_market_sentiment(self.symbol, news_headlines)
        
        # 3. Fear & Greed Data
        fng_data = self.sentiment_engine.get_fear_greed_score()
        fng_value = fng_data["value"]
        fng_class = fng_data["classification"]
        
        # 4. Macro Data (DXY)
        macro_data = self.macro_client.get_dxy_trend()
        dxy_sentiment = macro_data["sentiment"] if macro_data else "NEUTRAL"
        dxy_price = macro_data["price"] if macro_data else 0
        
        # 6. Order Flow / Funding Rate (Institutional Protection)
        # Convert SOLUSDT to SOL_USDT for futures API
        futures_symbol = self.symbol.replace("USDT", "_USDT")
        funding_rate = self.futures_client.get_funding_rate(futures_symbol)
        
        # 7. Logic Implementation
        signal = "WAIT"
        reason = []
        
        # Bullish Crossover (EMA9 crosses above EMA21)
        bullish_cross = prev_ema9 <= prev_ema21 and curr_ema9 > curr_ema21
        bearish_cross = prev_ema9 >= prev_ema21 and curr_ema9 < curr_ema21
        
        # 4. POC (Point of Control) from Volume Profile
        poc = calculate_volume_profile(klines)
        
        # 5. Market Correlation (Confirmation from BTC)
        is_market_aligned = True
        if self.symbol != "BTCUSDT":
            btc_ticker = self.client.get_ticker_24h("BTCUSDT")
            btc_change = float(btc_ticker.get('priceChangePercent', 0))
            # If we want to LONG, BTC shouldn't be crashing (-2% or more)
            if btc_change < -2.0:
                is_market_aligned = False
                reason.append("BTC is crashing; market correlation rejected LONG")

        # BUY/SHORT Logic: Skip if already in a position
        if not self.position_type:
            if bullish_cross:
                if curr_rsi < 65 and is_market_aligned:
                    # Professional Confirmation: Entry near POC or above
                    # Macro Confirmation: DXY should not be pumping (Strongly Bullish Dollar = Weak Crypto)
                    is_macro_favorable = dxy_sentiment == "BULLISH" # DXY Down
                    
                    # Institutional Safety: Skip BUY if Funding Rate is dangerously high (> 0.03%)
                    # This avoids "Long Squeezes" where longs are too crowded.
                    is_funding_safe = funding_rate < 0.0003
                    
                    if (closes[-1] >= poc or fng_value < 25 or is_macro_favorable) and is_funding_safe:
                        if sentiment == "BULLISH" or (not news_headlines and price_change_percent > 0) or fng_value < 20:
                            signal = "BUY"
                            self.position_type = "LONG"
                            if is_macro_favorable: reason.append(f"Macro Tailwinds (DXY Down @ {dxy_price})")
                            if fng_value < 20: reason.append(f"Extreme Fear Contrarian BUY ({fng_value})")
                        else:
                            reason.append(f"Sentiment/Macro filter rejected BUY ({sentiment}, 24h:{price_change_percent}%)")
                    else:
                        reason.append(f"Price below POC ({poc:.2f}); waiting for value confirmation")
                else:
                    if not is_market_aligned: pass # already added reason
                    else: reason.append(f"RSI too high for entry: {curr_rsi:.2f}")
            
            elif bearish_cross:
                if curr_rsi > 35:
                    if sentiment == "BEARISH" or (not news_headlines and price_change_percent < 0):
                        signal = "SHORT"
                        self.position_type = "SHORT"
                    else:
                        reason.append(f"Sentiment filter rejected SHORT ({sentiment})")
                else:
                    reason.append(f"RSI too low for SHORT: {curr_rsi:.2f}")
        
        # EXIT/SELL/COVER Logic
        if self.position_type:
            current_price = closes[-1]
            
            # If we are in a LONG position
            if self.position_type == "LONG":
                if bearish_cross:
                    signal = "SELL"
                    # We don't reset self.position_type yet, 
                    # the bot will do it after order success.
                elif self.entry_price:
                    price_diff = (current_price - self.entry_price) / self.entry_price
                    if price_diff <= -self.stop_loss_pct:
                        signal = "SELL (STOP LOSS)"
                        self.entry_price = None
                    elif price_diff >= self.take_profit_pct:
                        signal = "SELL (TAKE PROFIT)"
                        self.entry_price = None
            
            # If we are in a SHORT position
            elif self.position_type == "SHORT":
                if bullish_cross:
                    signal = "COVER"
                elif self.entry_price:
                    # In SHORT, profit is when price goes DOWN
                    price_diff = (self.entry_price - current_price) / self.entry_price
                    if price_diff <= -self.stop_loss_pct:
                        signal = "COVER (STOP LOSS)"
                        self.entry_price = None
                    elif price_diff >= self.take_profit_pct:
                        signal = "COVER (TAKE PROFIT)"
                        self.entry_price = None
            
            if self.entry_price is None:
                self.position_type = None

        # AI Prediction
        ai_opinion = "DISABLED"
        if self.model:
            try:
                # State matches TradingEnvironment: [price, ema9, ema21, rsi, balance, inventory, progress]
                mock_balance = 100.0 if not self.entry_price else 0.0
                mock_inv = 0.0 if not self.entry_price else 1.0
                
                state = torch.FloatTensor([
                    closes[-1], 
                    curr_ema9, 
                    curr_ema21, 
                    curr_rsi, 
                    mock_balance, 
                    mock_inv, 
                    1.0
                ]).unsqueeze(0)
                
                with torch.no_grad():
                    q_values = self.model(state)
                action = torch.argmax(q_values).item()
                ai_opinion = ["HOLD", "BUY", "SELL"][action]
            except Exception as e:
                ai_opinion = f"AI ERROR: {str(e)}"

        if not self.entry_price and ai_opinion == "BUY" and signal == "WAIT":
            signal = "BUY (AI DRIVEN)"
            reason.append("AI detected a pattern before technical crossover")

        # 4. Gap & Killzone Analysis (For professional view)
        killzone = self.check_killzone()
        gaps = self.calculate_fvg(klines)
        recent_gaps = gaps[-5:] if gaps else [] # Last 5 gaps
        
        # Fibonacci Analysis (Recent High/Low of klines)
        highs = [float(k[2]) for k in klines]
        lows = [float(k[3]) for k in klines]
        fib_levels = calculate_fibonacci_levels(max(highs), min(lows))
        
        return {
            "symbol": self.symbol,
            "price": closes[-1],
            "signal": signal,
            "funding_rate": funding_rate,
            "ai_opinion": ai_opinion,
            "fng": fng_value,
            "fng_class": fng_class,
            "macro": {
                "dxy_price": dxy_price,
                "dxy_sentiment": dxy_sentiment
            },
            "killzone": killzone,
            "recent_gaps": recent_gaps,
            "fib_levels": fib_levels,
            "poc": poc,
            "indicators": {
                "ema9": curr_ema9,
                "ema21": curr_ema21,
                "rsi": curr_rsi
            },
            "fundamental": {
                "sentiment": sentiment,
                "priceChange24h": price_change_percent
            },
            "reasons": reason
        }

if __name__ == "__main__":
    strategy = HybridStrategy("SOLUSDT")
    # Mock news for testing
    headlines = [
        "Major adoption of BTC by tech giants",
        "Market outlook improves as inflation cools"
    ]
    result = strategy.get_signals(headlines)
    print("--- Strategy Results ---")
    for k, v in result.items():
        print(f"{k}: {v}")
