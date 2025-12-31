import pandas as pd
import numpy as np

def calculate_ema(prices, period):
    """
    Calculate Exponential Moving Average (EMA).
    """
    return pd.Series(prices).ewm(span=period, adjust=False).mean().tolist()

def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI).
    """
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    # Handle NaN values (e.g. flat prices) by filling with 50 (Neutral)
    return rsi.fillna(50).tolist()

def calculate_fibonacci_levels(high, low):
    """
    Calculate Fibonacci Retracement levels for a given price range.
    """
    diff = high - low
    levels = {
        "0.0": high,
        "0.236": high - 0.236 * diff,
        "0.382": high - 0.382 * diff,
        "0.5": high - 0.5 * diff,
        "0.618": high - 0.618 * diff,
        "0.786": high - 0.786 * diff,
        "1.0": low
    }
    return levels

def calculate_volume_profile(klines, bins=20):
    """
    Calculate Volume Profile and return Point of Control (POC).
    klines format: [time, open, high, low, close, volume, ...]
    """
    if not klines:
        return None
        
    prices = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    
    min_p = min(prices)
    max_p = max(prices)
    
    if min_p == max_p:
        return min_p
        
    bin_size = (max_p - min_p) / bins
    profile = {}
    
    for p, v in zip(prices, volumes):
        bin_idx = int((p - min_p) / bin_size) if p < max_p else bins - 1
        bin_price = min_p + (bin_idx * bin_size)
        profile[bin_price] = profile.get(bin_price, 0) + v
        
    # POC is the price bin with the highest volume
    poc = max(profile, key=profile.get)
    return poc

def calculate_atr(high, low, close, period=14):
    """
    Calculate Average True Range (ATR).
    """
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    return atr.tolist()

def calculate_bollinger_bands(close, period=20, std_dev=2):
    """
    Calculate Bollinger Bands.
    """
    close = pd.Series(close)
    ma = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    
    upper = ma + (std * std_dev)
    lower = ma - (std * std_dev)
    
    return ma.tolist(), upper.tolist(), lower.tolist()

if __name__ == "__main__":
    # Test Data
    test_prices = [10, 11, 12, 11, 10, 9, 8, 9, 10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 11]
    print("EMA 5:", calculate_ema(test_prices, 5))
    print("RSI 14:", calculate_rsi(test_prices, 14))
