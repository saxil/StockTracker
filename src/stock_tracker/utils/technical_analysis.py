"""Technical analysis indicators and functions."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class TechnicalAnalysis:
    """Technical analysis indicators for stock data."""
    
    @staticmethod
    def moving_average(data: pd.Series, window: int) -> pd.Series:
        """Calculate Simple Moving Average (SMA)."""
        return data.rolling(window=window).mean()
    
    @staticmethod
    def exponential_moving_average(data: pd.Series, window: int) -> pd.Series:
        """Calculate Exponential Moving Average (EMA)."""
        return data.ewm(span=window).mean()
    
    @staticmethod
    def rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index (RSI)."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'middle': sma,
            'upper': upper_band,
            'lower': lower_band
        }
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, 
                            k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator."""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return {
            'k_percent': k_percent,
            'd_percent': d_percent
        }
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, 
                   window: int = 14) -> pd.Series:
        """Calculate Williams %R."""
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()
        
        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
        return williams_r
    
    @staticmethod
    def average_true_range(high: pd.Series, low: pd.Series, close: pd.Series,
                          window: int = 14) -> pd.Series:
        """Calculate Average True Range (ATR)."""
        high_low = high - low
        high_close_prev = np.abs(high - close.shift())
        low_close_prev = np.abs(low - close.shift())
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = true_range.rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def commodity_channel_index(high: pd.Series, low: pd.Series, close: pd.Series,
                               window: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index (CCI)."""
        typical_price = (high + low + close) / 3
        sma = typical_price.rolling(window=window).mean()
        mad = typical_price.rolling(window=window).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (typical_price - sma) / (0.015 * mad)
        return cci
    
    @staticmethod
    def volume_weighted_average_price(high: pd.Series, low: pd.Series, 
                                    close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate Volume Weighted Average Price (VWAP)."""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    @staticmethod
    def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume (OBV)."""
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    @staticmethod
    def fibonacci_retracement(high_price: float, low_price: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels."""
        diff = high_price - low_price
        
        levels = {
            '0%': high_price,
            '23.6%': high_price - (0.236 * diff),
            '38.2%': high_price - (0.382 * diff),
            '50%': high_price - (0.5 * diff),
            '61.8%': high_price - (0.618 * diff),
            '100%': low_price
        }
        
        return levels
    
    @classmethod
    def analyze_stock(cls, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Perform comprehensive technical analysis on stock data."""
        if df.empty:
            return {}
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
        
        high = df['High']
        low = df['Low']
        close = df['Close']
        volume = df['Volume']
        
        analysis = {}
        
        # Moving Averages
        analysis['SMA_20'] = cls.moving_average(close, 20)
        analysis['SMA_50'] = cls.moving_average(close, 50)
        analysis['SMA_200'] = cls.moving_average(close, 200)
        analysis['EMA_12'] = cls.exponential_moving_average(close, 12)
        analysis['EMA_26'] = cls.exponential_moving_average(close, 26)
        
        # Momentum Indicators
        analysis['RSI'] = cls.rsi(close)
        analysis['Williams_R'] = cls.williams_r(high, low, close)
        
        # Volatility Indicators
        bollinger = cls.bollinger_bands(close)
        analysis['BB_Upper'] = bollinger['upper']
        analysis['BB_Middle'] = bollinger['middle']
        analysis['BB_Lower'] = bollinger['lower']
        analysis['ATR'] = cls.average_true_range(high, low, close)
        
        # Trend Indicators
        macd_data = cls.macd(close)
        analysis['MACD'] = macd_data['macd']
        analysis['MACD_Signal'] = macd_data['signal']
        analysis['MACD_Histogram'] = macd_data['histogram']
        
        # Oscillators
        stoch = cls.stochastic_oscillator(high, low, close)
        analysis['Stoch_K'] = stoch['k_percent']
        analysis['Stoch_D'] = stoch['d_percent']
        analysis['CCI'] = cls.commodity_channel_index(high, low, close)
        
        # Volume Indicators
        analysis['VWAP'] = cls.volume_weighted_average_price(high, low, close, volume)
        analysis['OBV'] = cls.on_balance_volume(close, volume)
        
        return analysis
    
    @staticmethod
    def generate_signals(analysis: Dict[str, pd.Series]) -> Dict[str, str]:
        """Generate trading signals based on technical indicators."""
        signals = {}
        
        if 'RSI' in analysis and not analysis['RSI'].empty:
            latest_rsi = analysis['RSI'].iloc[-1]
            if pd.notna(latest_rsi):
                if latest_rsi > 70:
                    signals['RSI'] = 'SELL - Overbought'
                elif latest_rsi < 30:
                    signals['RSI'] = 'BUY - Oversold'
                else:
                    signals['RSI'] = 'NEUTRAL'
        
        if 'MACD' in analysis and 'MACD_Signal' in analysis:
            macd = analysis['MACD']
            signal = analysis['MACD_Signal']
            if len(macd) > 1 and len(signal) > 1:
                if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
                    signals['MACD'] = 'BUY - Bullish Crossover'
                elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
                    signals['MACD'] = 'SELL - Bearish Crossover'
                else:
                    signals['MACD'] = 'NEUTRAL'
        
        if 'SMA_20' in analysis and 'SMA_50' in analysis:
            sma20 = analysis['SMA_20']
            sma50 = analysis['SMA_50']
            if len(sma20) > 1 and len(sma50) > 1:
                if sma20.iloc[-1] > sma50.iloc[-1] and sma20.iloc[-2] <= sma50.iloc[-2]:
                    signals['Moving_Average'] = 'BUY - Golden Cross'
                elif sma20.iloc[-1] < sma50.iloc[-1] and sma20.iloc[-2] >= sma50.iloc[-2]:
                    signals['Moving_Average'] = 'SELL - Death Cross'
                else:
                    signals['Moving_Average'] = 'NEUTRAL'
        
        # Bollinger Bands
        if all(key in analysis for key in ['BB_Upper', 'BB_Lower']) and 'Close' in analysis:
            close = analysis.get('Close')
            bb_upper = analysis['BB_Upper']
            bb_lower = analysis['BB_Lower']
            
            if close is not None and not close.empty:
                if close.iloc[-1] > bb_upper.iloc[-1]:
                    signals['Bollinger_Bands'] = 'SELL - Above Upper Band'
                elif close.iloc[-1] < bb_lower.iloc[-1]:
                    signals['Bollinger_Bands'] = 'BUY - Below Lower Band'
                else:
                    signals['Bollinger_Bands'] = 'NEUTRAL'
        
        return signals
    
    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict[str, List[float]]:
        """Calculate support and resistance levels."""
        high = df['High']
        low = df['Low']
        
        # Find local maxima (resistance) and minima (support)
        resistance_levels = []
        support_levels = []
        
        for i in range(window, len(high) - window):
            # Check for resistance (local maxima)
            if high.iloc[i] == high.iloc[i-window:i+window+1].max():
                resistance_levels.append(high.iloc[i])
            
            # Check for support (local minima)
            if low.iloc[i] == low.iloc[i-window:i+window+1].min():
                support_levels.append(low.iloc[i])
        
        # Remove duplicates and sort
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        support_levels = sorted(list(set(support_levels)))
        
        return {
            'resistance': resistance_levels[:5],  # Top 5 resistance levels
            'support': support_levels[-5:]      # Top 5 support levels
        }
