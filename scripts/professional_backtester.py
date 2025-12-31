import pandas as pd
import numpy as np
from strategy import HybridStrategy

class ProfessionalBacktester:
    def __init__(self, csv_path="/Users/radenyudi/.gemini/antigravity/scratch/quant_trade_ai/SOLUSDT_15m_historical.csv", initial_balance=20.0, leverage=3):
        self.csv_path = csv_path
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.leverage = leverage
        self.position = None # "LONG", "SHORT", None
        self.entry_price = 0
        self.trades = []
        
    def run(self):
        print(f"📊 Loading historical data from {self.csv_path}...")
        df = pd.read_csv(self.csv_path)
        
        # Ensure correct column format (time, open, high, low, close, volume, ...)
        # If it's the MEXC format, we might need to adjust column names
        if 'close' not in df.columns:
            # Fallback for raw MEXC list-style CSV
            df.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_vol']
            
        strategy = HybridStrategy("SOLUSDT")
        
        print(f"🚀 Starting Professional Backtest | Initial: ${self.balance} | Leverage: {self.leverage}x")
        
        # We need to simulate the strategy.get_signals() call but with historical data slice
        klines = df.values.tolist()
        
        # Start from 100 to have enough data for indicators
        for i in range(100, len(klines)):
            current_klines = klines[max(0, i-100):i+1]
            current_price = float(klines[i][4])
            
            # Mock the strategy's internal data
            # get_signals normally pulls from the exchange, so we override it for backtesting
            result = strategy.get_signals_backtest(current_klines)
            signal = result['signal']
            
            # Position Management
            if not self.position:
                if "BUY" in signal:
                    self.position = "LONG"
                    self.entry_price = current_price
                    # print(f"Entry LONG at ${current_price:.2f}")
                elif "SHORT" in signal:
                    self.position = "SHORT"
                    self.entry_price = current_price
                    # print(f"Entry SHORT at ${current_price:.2f}")
            
            else:
                # Check for Exit (Strategy logic handled crossover)
                exit_signal = False
                pnl_pct = 0
                
                if self.position == "LONG":
                    pnl_pct = (current_price - self.entry_price) / self.entry_price
                    if "SELL" in signal or pnl_pct <= -0.015 or pnl_pct >= 0.04:
                        exit_signal = True
                elif self.position == "SHORT":
                    pnl_pct = (self.entry_price - current_price) / self.entry_price
                    if "COVER" in signal or pnl_pct <= -0.015 or pnl_pct >= 0.04:
                        exit_signal = True
                
                if exit_signal:
                    # Calculate PNL with leverage
                    trade_profit = self.initial_balance * pnl_pct * self.leverage
                    self.balance += trade_profit
                    self.trades.append({
                        'type': self.position,
                        'entry': self.entry_price,
                        'exit': current_price,
                        'profit': trade_profit,
                        'pnl_pct': pnl_pct * self.leverage * 100
                    })
                    self.position = None
                    self.entry_price = 0

        self.print_summary()

    def print_summary(self):
        print("\n" + "="*40)
        print("📈 PROFESSIONAL BACKTEST SUMMARY")
        print("="*40)
        print(f"Initial Balance: ${self.initial_balance:.2f}")
        print(f"Final Balance:   ${self.balance:.2f}")
        print(f"Total Profit:    ${self.balance - self.initial_balance:.2f} ({((self.balance/self.initial_balance)-1)*100:+.2f}%)")
        print(f"Total Trades:    {len(self.trades)}")
        
        if self.trades:
            wins = [t for t in self.trades if t['profit'] > 0]
            print(f"Win Rate:        {(len(wins)/len(self.trades))*100:.2f}%")
            print(f"Best Trade:      {max([t['pnl_pct'] for t in self.trades]):+.2f}%")
            print(f"Worst Trade:     {min([t['pnl_pct'] for t in self.trades]):+.2f}%")
        print("="*40)

if __name__ == "__main__":
    tester = ProfessionalBacktester()
    tester.run()
