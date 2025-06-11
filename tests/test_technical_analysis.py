"""Unit tests for technical analysis module."""

import unittest
import pandas as pd
import numpy as np
from src.stock_tracker.utils.technical_analysis import TechnicalAnalysis


class TestTechnicalAnalysis(unittest.TestCase):
    """Test cases for TechnicalAnalysis class."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample stock data
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)  # For reproducible results
        
        # Generate realistic stock price data
        price = 100
        prices = []
        volumes = []
        
        for _ in range(100):
            change = np.random.normal(0, 0.02)  # 2% daily volatility
            price = price * (1 + change)
            prices.append(price)
            volumes.append(np.random.randint(1000000, 5000000))
        
        self.df = pd.DataFrame({
            'Date': dates,
            'Open': [p * np.random.uniform(0.995, 1.005) for p in prices],
            'High': [p * np.random.uniform(1.005, 1.02) for p in prices],
            'Low': [p * np.random.uniform(0.98, 0.995) for p in prices],
            'Close': prices,
            'Volume': volumes
        })
        self.df.set_index('Date', inplace=True)
        
        self.ta = TechnicalAnalysis()
    
    def test_moving_average(self):
        """Test Simple Moving Average calculation."""
        sma = self.ta.moving_average(self.df['Close'], 20)
        
        # Check that SMA has correct length
        self.assertEqual(len(sma), len(self.df))
        
        # Check that first 19 values are NaN
        self.assertTrue(pd.isna(sma.iloc[:19]).all())
        
        # Check that 20th value is average of first 20 close prices
        expected_sma_20 = self.df['Close'].iloc[:20].mean()
        self.assertAlmostEqual(sma.iloc[19], expected_sma_20, places=2)
    
    def test_exponential_moving_average(self):
        """Test Exponential Moving Average calculation."""
        ema = self.ta.exponential_moving_average(self.df['Close'], 12)
        
        # Check that EMA has correct length
        self.assertEqual(len(ema), len(self.df))
        
        # EMA should not have NaN values after first value
        self.assertFalse(pd.isna(ema.iloc[1:]).any())
    
    def test_rsi(self):
        """Test RSI calculation."""
        rsi = self.ta.rsi(self.df['Close'], 14)
        
        # Check that RSI has correct length
        self.assertEqual(len(rsi), len(self.df))
        
        # RSI values should be between 0 and 100
        valid_rsi = rsi.dropna()
        self.assertTrue((valid_rsi >= 0).all())
        self.assertTrue((valid_rsi <= 100).all())
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        bb = self.ta.bollinger_bands(self.df['Close'], 20, 2)
        
        # Check that all bands are returned
        self.assertIn('middle', bb)
        self.assertIn('upper', bb)
        self.assertIn('lower', bb)
        
        # Check that upper band is above middle, middle above lower
        valid_indices = ~pd.isna(bb['middle'])
        upper_valid = bb['upper'][valid_indices]
        middle_valid = bb['middle'][valid_indices]
        lower_valid = bb['lower'][valid_indices]
        
        self.assertTrue((upper_valid >= middle_valid).all())
        self.assertTrue((middle_valid >= lower_valid).all())
    
    def test_macd(self):
        """Test MACD calculation."""
        macd = self.ta.macd(self.df['Close'])
        
        # Check that all MACD components are returned
        self.assertIn('macd', macd)
        self.assertIn('signal', macd)
        self.assertIn('histogram', macd)
        
        # Check that histogram equals MACD - Signal
        valid_indices = ~pd.isna(macd['signal'])
        macd_valid = macd['macd'][valid_indices]
        signal_valid = macd['signal'][valid_indices]
        histogram_valid = macd['histogram'][valid_indices]
        
        expected_histogram = macd_valid - signal_valid
        pd.testing.assert_series_equal(histogram_valid, expected_histogram, check_names=False)
    
    def test_stochastic_oscillator(self):
        """Test Stochastic Oscillator calculation."""
        stoch = self.ta.stochastic_oscillator(
            self.df['High'], self.df['Low'], self.df['Close']
        )
        
        # Check that both K and D are returned
        self.assertIn('k_percent', stoch)
        self.assertIn('d_percent', stoch)
        
        # Values should be between 0 and 100
        k_valid = stoch['k_percent'].dropna()
        d_valid = stoch['d_percent'].dropna()
        
        self.assertTrue((k_valid >= 0).all())
        self.assertTrue((k_valid <= 100).all())
        self.assertTrue((d_valid >= 0).all())
        self.assertTrue((d_valid <= 100).all())
    
    def test_analyze_stock(self):
        """Test comprehensive stock analysis."""
        analysis = self.ta.analyze_stock(self.df)
        
        # Check that all expected indicators are calculated
        expected_indicators = [
            'SMA_20', 'SMA_50', 'SMA_200', 'EMA_12', 'EMA_26',
            'RSI', 'Williams_R', 'BB_Upper', 'BB_Middle', 'BB_Lower',
            'ATR', 'MACD', 'MACD_Signal', 'MACD_Histogram',
            'Stoch_K', 'Stoch_D', 'CCI', 'VWAP', 'OBV'
        ]
        
        for indicator in expected_indicators:
            self.assertIn(indicator, analysis)
            self.assertIsInstance(analysis[indicator], pd.Series)
    
    def test_generate_signals(self):
        """Test signal generation."""
        analysis = self.ta.analyze_stock(self.df)
        signals = self.ta.generate_signals(analysis)
        
        # Signals should be a dictionary
        self.assertIsInstance(signals, dict)
        
        # Check for expected signal types
        expected_signals = ['RSI', 'MACD', 'Moving_Average']
        for signal_type in expected_signals:
            if signal_type in signals:
                signal_value = signals[signal_type]
                self.assertIn(signal_value.split(' - ')[0], ['BUY', 'SELL', 'NEUTRAL'])
    
    def test_fibonacci_retracement(self):
        """Test Fibonacci retracement calculation."""
        high_price = 150.0
        low_price = 100.0
        
        fib_levels = self.ta.fibonacci_retracement(high_price, low_price)
        
        # Check that all levels are returned
        expected_levels = ['0%', '23.6%', '38.2%', '50%', '61.8%', '100%']
        for level in expected_levels:
            self.assertIn(level, fib_levels)
        
        # Check that levels are in correct order
        self.assertEqual(fib_levels['0%'], high_price)
        self.assertEqual(fib_levels['100%'], low_price)
        self.assertGreater(fib_levels['23.6%'], fib_levels['38.2%'])
    
    def test_support_resistance(self):
        """Test support and resistance calculation."""
        support_resistance = self.ta.calculate_support_resistance(self.df)
        
        # Check that both support and resistance are returned
        self.assertIn('support', support_resistance)
        self.assertIn('resistance', support_resistance)
        
        # Check that they are lists
        self.assertIsInstance(support_resistance['support'], list)
        self.assertIsInstance(support_resistance['resistance'], list)
    
    def test_empty_dataframe(self):
        """Test behavior with empty DataFrame."""
        empty_df = pd.DataFrame()
        analysis = self.ta.analyze_stock(empty_df)
        
        # Should return empty dictionary
        self.assertEqual(analysis, {})
    
    def test_insufficient_data(self):
        """Test behavior with insufficient data."""
        small_df = self.df.head(10)  # Only 10 days of data
        
        # Should not raise exception
        analysis = self.ta.analyze_stock(small_df)
        
        # Some indicators might have all NaN values, but structure should be intact
        self.assertIsInstance(analysis, dict)


if __name__ == '__main__':
    unittest.main()
