import numpy as np
import pandas as pd

class TradingEnvironment:
    """
    A simplified trading environment for Reinforcement Learning, 
    inspired by OpenAI Gym and FinRL.
    """
    def __init__(self, data_path, initial_balance=100.0):
        self.df = pd.read_csv(data_path)
        self.initial_balance = initial_balance
        self._add_indicators()
        self.reset()

    def _add_indicators(self):
        """Adds technical indicators to the dataframe for state enrichment."""
        # Clean numeric data
        self.df['close'] = pd.to_numeric(self.df['close'])
        
        # EMA
        self.df['ema9'] = self.df['close'].ewm(span=9, adjust=False).mean()
        self.df['ema21'] = self.df['close'].ewm(span=21, adjust=False).mean()
        
        # RSI
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.df['rsi'] = 100 - (100 / (1 + rs))
        
        # Fill NaNs
        self.df.fillna(method='bfill', inplace=True)

    def reset(self):
        """Resets the environment to initial state."""
        self.balance = self.initial_balance
        self.inventory = 0
        self.current_step = 21 # Start where indicators are valid
        self.total_trades = 0
        self.done = False
        return self._get_observation()

    def _get_observation(self):
        """Returns the current market state/observation."""
        row = self.df.iloc[self.current_step]
        obs = np.array([
            row['close'],
            row['ema9'],
            row['ema21'],
            row['rsi'],
            self.balance,
            self.inventory,
            self.current_step / len(self.df)
        ], dtype=np.float32)
        return obs

    def step(self, action):
        """
        Executes an action in the environment.
        Actions: 0 = HOLD, 1 = BUY ALL, 2 = SELL ALL
        """
        current_price = self.df.iloc[self.current_step]['close']
        reward = 0
        
        # BUY
        if action == 1 and self.balance > 10:
            self.inventory = self.balance / current_price
            self.balance = 0
            self.total_trades += 1
        
        # SELL
        elif action == 2 and self.inventory > 0:
            self.balance = self.inventory * current_price
            # Reward is change in total account value
            reward = (self.balance - self.initial_balance) # Simplified reward
            self.inventory = 0
            self.total_trades += 1

        self.current_step += 1
        if self.current_step >= len(self.df) - 1:
            self.done = True
        
        obs = self._get_observation()
        
        # Calculate net worth for reward monitoring
        net_worth = self.balance + (self.inventory * current_price)
        reward = net_worth - self.initial_balance # Ongoing reward
        
        return obs, reward, self.done, {"net_worth": net_worth}

if __name__ == "__main__":
    # Quick Test
    env = TradingEnvironment("SOLUSDT_15m_historical.csv")
    obs = env.reset()
    print(f"Initial Observation: {obs}")
    
    # Simulate a few steps
    for _ in range(5):
        obs, reward, done, info = env.step(1) # Try to Buy
        print(f"Step Reward: {reward} | Net Worth: {info['net_worth']}")
