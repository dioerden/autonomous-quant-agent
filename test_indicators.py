import unittest
from indicators import calculate_ema, calculate_rsi

class TestIndicators(unittest.TestCase):
    def test_ema(self):
        prices = [10, 10, 10, 10, 10]
        ema5 = calculate_ema(prices, 5)
        self.assertEqual(ema5[-1], 10)
        
    def test_rsi_flat(self):
        # All same prices = RSI Neutral/Undefined but handled by pandas
        prices = [10] * 20
        rsi = calculate_rsi(prices, 14)
        # RSI should be 50 (Neutral) for flat prices
        self.assertEqual(rsi[-1], 50)

    def test_rsi_uptrend(self):
        prices = list(range(20))
        rsi = calculate_rsi(prices, 14)
        self.assertGreater(rsi[-1], 50)

if __name__ == "__main__":
    unittest.main()
