"""
Technical Analyzer - Price trends, volatility, and momentum analysis

Provides comprehensive technical analysis including:
- Price trend analysis with moving averages
- Momentum indicators (RSI, MACD)
- Volatility analysis and Bollinger Bands
- Volume analysis and trading signals
- Support/resistance levels
"""

import numpy as np
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict

from ...common.logging_config import get_logger
from ...common.exceptions import DataFetchError
from ...common.api_rate_limiter import rate_limiter
from ...models.market_models import TechnicalAnalysis, TechnicalIndicators, AnalysisParameters

logger = get_logger(__name__)


class TechnicalAnalyzer:
    """Technical analysis for stock price data."""
    
    def __init__(self, parameters: Optional[AnalysisParameters] = None):
        """
        Initialize technical analyzer.
        
        Args:
            parameters: Analysis parameters, uses defaults if None
        """
        self.params = parameters or AnalysisParameters()
    
    @rate_limiter.rate_limited("technical_analysis")
    def analyze_ticker(self, ticker: str, period: str = "1y") -> TechnicalAnalysis:
        """
        Perform comprehensive technical analysis for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1y, 6mo, 3mo, etc.)
            
        Returns:
            TechnicalAnalysis with complete technical metrics
        """
        try:
            logger.info(f"Starting technical analysis for {ticker}")
            
            # Fetch price data
            price_data = self._fetch_price_data(ticker, period)
            if price_data is None or len(price_data) < 50:
                raise DataFetchError(f"Insufficient price data for {ticker}")
            
            # Calculate technical indicators
            indicators = self._calculate_indicators(price_data)
            
            # Analyze trends
            trend_info = self._analyze_trends(price_data, indicators)
            
            # Analyze volatility
            volatility_info = self._analyze_volatility(price_data)
            
            # Analyze momentum
            momentum_info = self._analyze_momentum(indicators)
            
            # Generate trading signals
            signals = self._generate_signals(price_data, indicators)
            
            # Get current price
            current_price = float(price_data['Close'].iloc[-1])
            
            return TechnicalAnalysis(
                ticker=ticker,
                current_price=current_price,
                analysis_date=datetime.now(),
                indicators=indicators,
                price_trend=trend_info['trend'],
                trend_strength=trend_info['strength'],
                support_level=trend_info.get('support'),
                resistance_level=trend_info.get('resistance'),
                volatility_30d=volatility_info['volatility_30d'],
                volatility_rank=volatility_info['volatility_rank'],
                momentum_score=momentum_info['score'],
                momentum_direction=momentum_info['direction'],
                buy_signals=signals['buy_signals'],
                sell_signals=signals['sell_signals'],
                overall_signal=signals['overall_signal']
            )
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {ticker}: {e}")
            raise DataFetchError(f"Technical analysis failed for {ticker}: {str(e)}")
    
    def _fetch_price_data(self, ticker: str, period: str) -> Optional[pd.DataFrame]:
        """Fetch historical price data."""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                return None
                
            # Reset index to get Date as column
            data.reset_index(inplace=True)
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch price data for {ticker}: {e}")
            return None
    
    def _calculate_indicators(self, data: pd.DataFrame) -> TechnicalIndicators:
        """Calculate all technical indicators."""
        close_prices = data['Close']
        high_prices = data['High']
        low_prices = data['Low']
        volume = data['Volume']
        
        # Moving averages
        sma_20 = close_prices.rolling(window=self.params.short_ma_period).mean().iloc[-1]
        sma_50 = close_prices.rolling(window=self.params.medium_ma_period).mean().iloc[-1]
        sma_200 = close_prices.rolling(window=self.params.long_ma_period).mean().iloc[-1]
        
        # Exponential moving averages
        ema_12 = close_prices.ewm(span=12).mean().iloc[-1]
        ema_26 = close_prices.ewm(span=26).mean().iloc[-1]
        
        # RSI
        rsi = self._calculate_rsi(close_prices, self.params.rsi_period)
        
        # MACD
        macd_line = ema_12 - ema_26
        macd_signal = pd.Series([macd_line]).ewm(span=9).mean().iloc[-1]
        macd_histogram = macd_line - macd_signal
        
        # Bollinger Bands
        bb_middle = close_prices.rolling(window=self.params.bollinger_period).mean()
        bb_std = close_prices.rolling(window=self.params.bollinger_period).std()
        bollinger_upper = (bb_middle + (bb_std * self.params.bollinger_std)).iloc[-1]
        bollinger_lower = (bb_middle - (bb_std * self.params.bollinger_std)).iloc[-1]
        
        # Average True Range
        atr = self._calculate_atr(high_prices, low_prices, close_prices)
        
        # Volume indicators
        volume_sma = volume.rolling(window=20).mean().iloc[-1]
        volume_ratio = volume.iloc[-1] / volume_sma if volume_sma > 0 else 1.0
        
        return TechnicalIndicators(
            sma_20=float(sma_20) if not pd.isna(sma_20) else None,
            sma_50=float(sma_50) if not pd.isna(sma_50) else None,
            sma_200=float(sma_200) if not pd.isna(sma_200) else None,
            ema_12=float(ema_12) if not pd.isna(ema_12) else None,
            ema_26=float(ema_26) if not pd.isna(ema_26) else None,
            rsi=float(rsi) if not pd.isna(rsi) else None,
            macd=float(macd_line) if not pd.isna(macd_line) else None,
            macd_signal=float(macd_signal) if not pd.isna(macd_signal) else None,
            macd_histogram=float(macd_histogram) if not pd.isna(macd_histogram) else None,
            bollinger_upper=float(bollinger_upper) if not pd.isna(bollinger_upper) else None,
            bollinger_lower=float(bollinger_lower) if not pd.isna(bollinger_lower) else None,
            atr=float(atr) if not pd.isna(atr) else None,
            volume_sma=float(volume_sma) if not pd.isna(volume_sma) else None,
            volume_ratio=float(volume_ratio) if not pd.isna(volume_ratio) else None
        )
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Calculate Average True Range."""
        high_low = high - low
        high_close = np.abs(high - close.shift(1))
        low_close = np.abs(low - close.shift(1))
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr.iloc[-1]
    
    def _analyze_trends(self, data: pd.DataFrame, indicators: TechnicalIndicators) -> Dict:
        """Analyze price trends and support/resistance."""
        close_prices = data['Close']
        current_price = close_prices.iloc[-1]
        
        # Trend determination based on moving averages
        trend_signals = []
        
        if indicators.sma_20 and indicators.sma_50:
            if indicators.sma_20 > indicators.sma_50:
                trend_signals.append("short_term_up")
            else:
                trend_signals.append("short_term_down")
        
        if indicators.sma_50 and indicators.sma_200:
            if indicators.sma_50 > indicators.sma_200:
                trend_signals.append("medium_term_up")
            else:
                trend_signals.append("medium_term_down")
        
        # Overall trend
        up_signals = len([s for s in trend_signals if "up" in s])
        down_signals = len([s for s in trend_signals if "down" in s])
        
        if up_signals > down_signals:
            trend = "uptrend"
            strength = up_signals / len(trend_signals) if trend_signals else 0.5
        elif down_signals > up_signals:
            trend = "downtrend"
            strength = down_signals / len(trend_signals) if trend_signals else 0.5
        else:
            trend = "sideways"
            strength = 0.5
        
        # Basic support/resistance (recent highs/lows)
        recent_data = data.tail(20)
        support = recent_data['Low'].min()
        resistance = recent_data['High'].max()
        
        return {
            'trend': trend,
            'strength': strength,
            'support': float(support),
            'resistance': float(resistance)
        }
    
    def _analyze_volatility(self, data: pd.DataFrame) -> Dict:
        """Analyze price volatility."""
        close_prices = data['Close']
        
        # 30-day historical volatility
        returns = close_prices.pct_change().dropna()
        volatility_30d = returns.tail(30).std() * np.sqrt(252)  # Annualized
        
        # Volatility ranking
        volatility_hist = returns.rolling(window=30).std() * np.sqrt(252)
        current_vol = volatility_30d
        vol_percentile = (volatility_hist <= current_vol).mean()
        
        if vol_percentile <= 0.33:
            volatility_rank = "low"
        elif vol_percentile <= 0.66:
            volatility_rank = "medium"
        else:
            volatility_rank = "high"
        
        return {
            'volatility_30d': float(volatility_30d),
            'volatility_rank': volatility_rank
        }
    
    def _analyze_momentum(self, indicators: TechnicalIndicators) -> Dict:
        """Analyze momentum indicators."""
        momentum_score = 0.0
        signals = []
        
        # RSI momentum
        if indicators.rsi:
            if indicators.rsi > 70:
                signals.append("overbought")
                momentum_score -= 0.3
            elif indicators.rsi > 50:
                signals.append("bullish_momentum")
                momentum_score += 0.2
            elif indicators.rsi < 30:
                signals.append("oversold")
                momentum_score += 0.3
            elif indicators.rsi < 50:
                signals.append("bearish_momentum")
                momentum_score -= 0.2
        
        # MACD momentum
        if indicators.macd and indicators.macd_signal:
            if indicators.macd > indicators.macd_signal:
                signals.append("macd_bullish")
                momentum_score += 0.2
            else:
                signals.append("macd_bearish")
                momentum_score -= 0.2
        
        # Overall momentum direction
        if momentum_score > 0.1:
            direction = "bullish"
        elif momentum_score < -0.1:
            direction = "bearish"
        else:
            direction = "neutral"
        
        return {
            'score': max(-1.0, min(1.0, momentum_score)),
            'direction': direction
        }
    
    def _generate_signals(self, data: pd.DataFrame, indicators: TechnicalIndicators) -> Dict:
        """Generate trading signals."""
        buy_signals = []
        sell_signals = []
        
        current_price = data['Close'].iloc[-1]
        
        # Moving average signals
        if indicators.sma_20 and indicators.sma_50:
            if indicators.sma_20 > indicators.sma_50:
                buy_signals.append("SMA 20 > SMA 50 (Golden Cross)")
            else:
                sell_signals.append("SMA 20 < SMA 50 (Death Cross)")
        
        # RSI signals
        if indicators.rsi:
            if indicators.rsi < 30:
                buy_signals.append("RSI Oversold")
            elif indicators.rsi > 70:
                sell_signals.append("RSI Overbought")
        
        # MACD signals
        if indicators.macd and indicators.macd_signal:
            if indicators.macd > indicators.macd_signal and indicators.macd > 0:
                buy_signals.append("MACD Bullish Crossover")
            elif indicators.macd < indicators.macd_signal and indicators.macd < 0:
                sell_signals.append("MACD Bearish Crossover")
        
        # Bollinger Band signals
        if indicators.bollinger_upper and indicators.bollinger_lower:
            if current_price <= indicators.bollinger_lower:
                buy_signals.append("Price at Lower Bollinger Band")
            elif current_price >= indicators.bollinger_upper:
                sell_signals.append("Price at Upper Bollinger Band")
        
        # Overall signal
        buy_score = len(buy_signals)
        sell_score = len(sell_signals)
        
        if buy_score > sell_score and buy_score >= 2:
            overall_signal = "buy"
        elif sell_score > buy_score and sell_score >= 2:
            overall_signal = "sell"
        else:
            overall_signal = "hold"
        
        return {
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'overall_signal': overall_signal
        }
