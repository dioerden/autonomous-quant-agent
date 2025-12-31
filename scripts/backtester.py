import pandas as pd
from mexc_client import MEXCClient
from indicators import calculate_ema, calculate_rsi

class Backtester:
    def __init__(self, symbol="BTCUSDT", initial_balance=20.0):
        self.symbol = symbol
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.client = MEXCClient()
        self.position = None # {price, amount}
        self.trades = []
        
    def run(self, days=30):
        """
        Runs backtest on historical K-lines.
        """
        # Fetch data (max limit is 1000 candles per call in MEXC API v3)
        # Using 15m candles for more granularity
        print(f"Fetching historical data for {self.symbol}...")
        klines = self.client.get_klines(self.symbol, "15m", limit=1000)
        
        if not klines or len(klines) < 100:
            print(f"Error: Not enough data for backtesting. Received: {len(klines) if klines else 0} candles.")
            return
            
        df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume'])
        df['close'] = df['close'].astype(float)
        
        closes = df['close'].tolist()
        ema9 = calculate_ema(closes, 9)
        ema21 = calculate_ema(closes, 21)
        rsi = calculate_rsi(closes, 14)
        
        sl_pct = 0.015 # Tighter Stop Loss for volatility
        tp_pct = 0.04  # Faster Take Profit
        
        print(f"Starting balance: {self.balance} USDT")
        
        for i in range(21, len(closes)):
            curr_price = closes[i]
            
            # Indicators for this candle
            c_ema9 = ema9[i]
            c_ema21 = ema21[i]
            c_rsi = rsi[i]
            
            p_ema9 = ema9[i-1]
            p_ema21 = ema21[i-1]
            
            # Logic
            bullish_cross = p_ema9 <= p_ema21 and c_ema9 > c_ema21
            bearish_cross = p_ema9 >= p_ema21 and c_ema9 < c_ema21
            
            # If not in position, check for BUY
            if not self.position:
                if bullish_cross and c_rsi < 65:
                    amount = self.balance / curr_price
                    self.position = {'price': curr_price, 'amount': amount}
                    self.balance = 0
            
            # If in position, check for EXIT
            else:
                entry_price = self.position['price']
                price_diff = (curr_price - entry_price) / entry_price
                
                exit_reason = None
                if bearish_cross:
                    exit_reason = "CROSSOVER"
                elif price_diff <= -sl_pct:
                    exit_reason = "STOP LOSS"
                elif price_diff >= tp_pct:
                    exit_reason = "TAKE PROFIT"
                
                if exit_reason:
                    self.balance = self.position['amount'] * curr_price
                    profit = self.balance - (self.position['amount'] * entry_price)
                    self.trades.append({
                        'entry': entry_price,
                        'exit': curr_price,
                        'profit': profit,
                        'reason': exit_reason
                    })
                    # print(f"SELL ({exit_reason}) at {curr_price} | Profit: {profit:.2f} | Balance: {self.balance:.2f}")
                    self.position = None

        self.summary()

    def summary(self):
        print("\n--- Backtest Summary ---")
        print(f"Initial Balance: {self.initial_balance} USDT")
        final_balance = self.balance if not self.position else self.position['amount'] * self.trades[-1]['exit']
        print(f"Final Balance: {final_balance:.2f} USDT")
        print(f"Total Trades: {len(self.trades)}")
        
        if self.trades:
            wins = len([t for t in self.trades if t['profit'] > 0])
            losses = len([t for t in self.trades if t['profit'] <= 0])
            print(f"Win Rate: {(wins/len(self.trades))*100:.2f}%")
            print(f"Total Profit: {final_balance - self.initial_balance:.2f} USDT")
        else:
            print("No trades executed.")

if __name__ == "__main__":
    tester = Backtester("SOLUSDT", initial_balance=20.0)
    tester.run()
