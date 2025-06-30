"""
Performance Analyzer - Returns, benchmarks, and comparative analysis

Provides comprehensive performance analysis including:
- Multi-timeframe return analysis (1D to 1Y)
- Benchmark comparison vs S&P 500 and sector ETFs
- Risk-adjusted metrics (Beta, Sharpe ratio, max drawdown)
- Sector ranking and correlation analysis
- Relative performance assessment
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

from ...common.logging_config import get_logger
from ...common.exceptions import DataFetchError
from ...common.api_rate_limiter import rate_limiter
from ...models.market_models import MarketPerformance, AnalysisParameters
from ..data_fetch.yahoo_fetcher import YahooDataFetcher

logger = get_logger(__name__)


class PerformanceAnalyzer:
    """Performance analysis for stock returns and risk metrics."""
    
    def __init__(self, parameters: Optional[AnalysisParameters] = None):
        """
        Initialize performance analyzer.
        
        Args:
            parameters: Analysis parameters, uses defaults if None
        """
        self.params = parameters or AnalysisParameters()
        self.yahoo_fetcher = YahooDataFetcher()
    
    @rate_limiter.rate_limited("performance_analysis")
    def analyze_ticker(self, ticker: str, period: str = "1y") -> MarketPerformance:
        """
        Perform comprehensive performance analysis for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: Analysis period for historical data
            
        Returns:
            MarketPerformance with complete performance metrics
        """
        try:
            logger.info(f"Starting performance analysis for {ticker}")
            
            # Fetch price data
            stock_data = self._fetch_price_data(ticker, period)
            if stock_data is None or len(stock_data) < 30:
                raise DataFetchError(f"Insufficient price data for {ticker}")
            
            # Get stock market data summary for sector info
            market_summary = self.yahoo_fetcher.get_market_data_summary(ticker)
            sector = market_summary.get('sector', 'Unknown')
            
            # Calculate returns
            returns_analysis = self._calculate_returns(stock_data)
              # Get benchmark data and compare
            benchmark_analysis = self._analyze_vs_benchmark(stock_data, ticker)
            benchmark_data = benchmark_analysis.pop('benchmark_data', None)  # Remove from dict
              # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(stock_data, benchmark_data)
            
            # Analyze sector performance
            sector_analysis = self._analyze_sector_performance(stock_data, sector, ticker)
            
            return MarketPerformance(
                ticker=ticker,
                analysis_date=datetime.now(),
                sector=sector,
                **returns_analysis,
                **benchmark_analysis,
                **risk_metrics,
                **sector_analysis
            )
            
        except Exception as e:
            logger.error(f"Performance analysis failed for {ticker}: {e}")
            raise DataFetchError(f"Performance analysis failed for {ticker}: {str(e)}")
    
    def _fetch_price_data(self, ticker: str, period: str) -> Optional[pd.DataFrame]:
        """Fetch historical price data using cached Yahoo fetcher."""
        try:
            data = self.yahoo_fetcher.get_historical_prices(ticker, period)
            
            if data is None or data.empty:
                logger.warning(f"No price data returned for {ticker}")
                return None
                
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch price data for {ticker}: {e}")
            return None
    
    def _calculate_returns(self, data: pd.DataFrame) -> Dict[str, Optional[float]]:
        """Calculate returns over various timeframes."""
        close_prices = data['Close']
        returns = {}
        
        # Current price
        current_price = close_prices.iloc[-1]
        
        # Calculate returns for different periods
        periods = {
            'return_1d': 1,
            'return_1w': 5,
            'return_1m': 21,
            'return_3m': 63,
            'return_6m': 126,
            'return_1y': 252
        }
        
        for return_name, days_back in periods.items():
            if len(close_prices) > days_back:
                past_price = close_prices.iloc[-(days_back + 1)]
                if past_price > 0:
                    return_value = (current_price - past_price) / past_price
                    returns[return_name] = float(return_value)
                else:
                    returns[return_name] = None
            else:
                returns[return_name] = None
        
        return returns
    
    def _analyze_vs_benchmark(self, stock_data: pd.DataFrame, ticker: str) -> Dict[str, Optional[float]]:
        """Analyze performance vs benchmark (S&P 500)."""
        try:
            # Fetch benchmark data (SPY) using cached fetcher
            benchmark_data = self.yahoo_fetcher.get_historical_prices(self.params.benchmark_symbol, "1y")
            
            if benchmark_data is None or benchmark_data.empty:
                logger.warning("Could not fetch benchmark data")
                return {
                    'benchmark_1m': None,
                    'benchmark_3m': None,
                    'benchmark_1y': None,
                    'benchmark_data': None
                }
            
            # Align data by dates
            aligned_data = self._align_price_data(stock_data, benchmark_data)
            if aligned_data is None:
                return {
                    'benchmark_1m': None,
                    'benchmark_3m': None,
                    'benchmark_1y': None,
                    'benchmark_data': None
                }
            
            stock_aligned, benchmark_aligned = aligned_data
            
            # Calculate relative performance
            stock_returns = stock_aligned['Close'].pct_change().fillna(0)
            benchmark_returns = benchmark_aligned['Close'].pct_change().fillna(0)
            
            relative_performance = {}
            
            # 1-month relative performance
            if len(stock_returns) >= 21:
                stock_1m = (1 + stock_returns.tail(21)).prod() - 1
                benchmark_1m = (1 + benchmark_returns.tail(21)).prod() - 1
                relative_performance['benchmark_1m'] = float(stock_1m - benchmark_1m)
            else:
                relative_performance['benchmark_1m'] = None
            
            # 3-month relative performance
            if len(stock_returns) >= 63:
                stock_3m = (1 + stock_returns.tail(63)).prod() - 1
                benchmark_3m = (1 + benchmark_returns.tail(63)).prod() - 1
                relative_performance['benchmark_3m'] = float(stock_3m - benchmark_3m)
            else:
                relative_performance['benchmark_3m'] = None
            
            # 1-year relative performance
            if len(stock_returns) >= 252:
                stock_1y = (1 + stock_returns.tail(252)).prod() - 1
                benchmark_1y = (1 + benchmark_returns.tail(252)).prod() - 1
                relative_performance['benchmark_1y'] = float(stock_1y - benchmark_1y)
            else:
                relative_performance['benchmark_1y'] = None
            
            relative_performance['benchmark_data'] = benchmark_aligned
            
            return relative_performance
            
        except Exception as e:
            logger.warning(f"Benchmark analysis failed: {e}")
            return {
                'benchmark_1m': None,
                'benchmark_3m': None,
                'benchmark_1y': None,
                'benchmark_data': None
            }
    
    def _align_price_data(self, stock_data: pd.DataFrame, benchmark_data: pd.DataFrame) -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]:
        """Align stock and benchmark data by common dates."""
        try:
            # Reset index to make Date a column if needed
            if 'Date' not in stock_data.columns:
                stock_data = stock_data.reset_index()
            if 'Date' not in benchmark_data.columns:
                benchmark_data = benchmark_data.reset_index()
            
            # Merge on Date
            merged = pd.merge(stock_data[['Date', 'Close']], 
                            benchmark_data[['Date', 'Close']], 
                            on='Date', 
                            suffixes=('_stock', '_benchmark'))
            
            if len(merged) < 30:  # Need at least 30 days of data
                return None
            
            # Recreate separate DataFrames
            stock_aligned = pd.DataFrame({
                'Date': merged['Date'],
                'Close': merged['Close_stock']
            }).set_index('Date')
            
            benchmark_aligned = pd.DataFrame({
                'Date': merged['Date'],
                'Close': merged['Close_benchmark']
            }).set_index('Date')
            
            return stock_aligned, benchmark_aligned
            
        except Exception as e:
            logger.error(f"Data alignment failed: {e}")
            return None
    
    def _calculate_risk_metrics(self, stock_data: pd.DataFrame, benchmark_data: Optional[pd.DataFrame]) -> Dict[str, Optional[float]]:
        """Calculate risk-adjusted performance metrics."""
        close_prices = stock_data['Close']
        returns = close_prices.pct_change().fillna(0)
        
        risk_metrics = {}
        
        # Beta calculation
        if benchmark_data is not None:
            try:
                benchmark_returns = benchmark_data['Close'].pct_change().fillna(0)
                
                # Ensure both return series have the same length by aligning on common dates
                common_dates = returns.index.intersection(benchmark_returns.index)
                if len(common_dates) < 30:  # Need sufficient data
                    risk_metrics['beta'] = None
                    risk_metrics['market_correlation'] = None
                else:
                    # Align the return series on common dates
                    aligned_returns = returns.reindex(common_dates).fillna(0)
                    aligned_benchmark_returns = benchmark_returns.reindex(common_dates).fillna(0)
                    
                    # Verify both series have the same length
                    if len(aligned_returns) != len(aligned_benchmark_returns):
                        logger.warning(f"Return series length mismatch after alignment: {len(aligned_returns)} vs {len(aligned_benchmark_returns)}")
                        risk_metrics['beta'] = None
                        risk_metrics['market_correlation'] = None
                    else:
                        # Calculate beta using covariance
                        covariance = np.cov(aligned_returns, aligned_benchmark_returns)[0, 1]
                        benchmark_variance = np.var(aligned_benchmark_returns)
                        
                        if benchmark_variance > 0:
                            beta = covariance / benchmark_variance
                            risk_metrics['beta'] = float(beta)
                        else:
                            risk_metrics['beta'] = None
                            
                        # Market correlation
                        correlation = np.corrcoef(aligned_returns, aligned_benchmark_returns)[0, 1]
                        risk_metrics['market_correlation'] = float(correlation) if not np.isnan(correlation) else None
                
            except Exception as e:
                logger.warning(f"Beta calculation failed: {e}")
                risk_metrics['beta'] = None
                risk_metrics['market_correlation'] = None
        else:
            risk_metrics['beta'] = None
            risk_metrics['market_correlation'] = None
        
        # Sharpe ratio
        try:
            excess_returns = returns - (self.params.risk_free_rate / 252)  # Daily risk-free rate
            if len(excess_returns) > 0 and excess_returns.std() > 0:
                sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)  # Annualized
                risk_metrics['sharpe_ratio'] = float(sharpe_ratio)
            else:
                risk_metrics['sharpe_ratio'] = None
        except Exception as e:
            logger.warning(f"Sharpe ratio calculation failed: {e}")
            risk_metrics['sharpe_ratio'] = None
        
        # Maximum drawdown
        try:
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns / running_max) - 1
            max_drawdown = drawdown.min()
            risk_metrics['max_drawdown'] = float(max_drawdown)
        except Exception as e:
            logger.warning(f"Max drawdown calculation failed: {e}")
            risk_metrics['max_drawdown'] = None
        
        return risk_metrics
    
    def _analyze_sector_performance(self, stock_data: pd.DataFrame, sector: str, ticker: str) -> Dict[str, Optional[Any]]:
        """Analyze performance relative to sector."""
        sector_analysis = {}
        
        # Get sector ETF symbol
        sector_etf = self.params.sector_etf_map.get(sector)
        
        if sector_etf:
            try:
                # Fetch sector ETF data using cached fetcher
                sector_data = self.yahoo_fetcher.get_historical_prices(sector_etf, "1y")
                
                if not sector_data.empty:
                    # Align data
                    aligned_data = self._align_price_data(stock_data, sector_data)
                    
                    if aligned_data is not None:
                        stock_aligned, sector_aligned = aligned_data
                        
                        # Calculate sector relative performance
                        stock_returns = stock_aligned['Close'].pct_change().fillna(0)
                        sector_returns = sector_aligned['Close'].pct_change().fillna(0)
                        
                        # 1-month sector performance
                        if len(stock_returns) >= 21:
                            stock_1m = (1 + stock_returns.tail(21)).prod() - 1
                            sector_1m = (1 + sector_returns.tail(21)).prod() - 1
                            sector_analysis['sector_performance_1m'] = float(stock_1m - sector_1m)
                        
                        # 3-month sector performance
                        if len(stock_returns) >= 63:
                            stock_3m = (1 + stock_returns.tail(63)).prod() - 1
                            sector_3m = (1 + sector_returns.tail(63)).prod() - 1
                            sector_analysis['sector_performance_3m'] = float(stock_3m - sector_3m)
                        
                        # Sector rank (simplified - would need more sector constituents for real ranking)
                        if sector_analysis.get('sector_performance_1m'):
                            if sector_analysis['sector_performance_1m'] > 0.05:  # 5% outperformance
                                sector_analysis['sector_rank'] = 1  # Top quartile
                            elif sector_analysis['sector_performance_1m'] > 0:
                                sector_analysis['sector_rank'] = 2  # Second quartile
                            elif sector_analysis['sector_performance_1m'] > -0.05:
                                sector_analysis['sector_rank'] = 3  # Third quartile
                            else:
                                sector_analysis['sector_rank'] = 4  # Bottom quartile
                
            except Exception as e:
                logger.warning(f"Sector analysis failed for {sector}: {e}")
        
        # Set defaults if analysis failed
        for key in ['sector_performance_1m', 'sector_performance_3m', 'sector_rank']:
            if key not in sector_analysis:
                sector_analysis[key] = None
        
        return sector_analysis
    
    def get_performance_summary(self, performance: MarketPerformance) -> Dict[str, Any]:
        """
        Generate a summary of performance analysis.
        
        Args:
            performance: Completed performance analysis
            
        Returns:
            Dictionary with performance summary and key insights
        """
        summary = {
            'ticker': performance.ticker,
            'analysis_date': performance.analysis_date,
            'returns_summary': {},
            'risk_summary': {},
            'relative_performance': {},
            'performance_rating': 'neutral'
        }
        
        # Returns summary
        returns = {}
        if performance.return_1d is not None:
            returns['1-Day'] = f"{performance.return_1d:.2%}"
        if performance.return_1w is not None:
            returns['1-Week'] = f"{performance.return_1w:.2%}"
        if performance.return_1m is not None:
            returns['1-Month'] = f"{performance.return_1m:.2%}"
        if performance.return_3m is not None:
            returns['3-Month'] = f"{performance.return_3m:.2%}"
        if performance.return_1y is not None:
            returns['1-Year'] = f"{performance.return_1y:.2%}"
        
        summary['returns_summary'] = returns
        
        # Risk summary
        risk = {}
        if performance.beta is not None:
            risk['Beta'] = f"{performance.beta:.2f}"
        if performance.sharpe_ratio is not None:
            risk['Sharpe Ratio'] = f"{performance.sharpe_ratio:.2f}"
        if performance.max_drawdown is not None:
            risk['Max Drawdown'] = f"{performance.max_drawdown:.2%}"
        
        summary['risk_summary'] = risk
        
        # Relative performance
        relative = {}
        if performance.benchmark_1m is not None:
            relative['vs S&P 500 (1M)'] = f"{performance.benchmark_1m:+.2%}"
        if performance.benchmark_3m is not None:
            relative['vs S&P 500 (3M)'] = f"{performance.benchmark_3m:+.2%}"
        if performance.sector_performance_1m is not None:
            relative['vs Sector (1M)'] = f"{performance.sector_performance_1m:+.2%}"
        
        summary['relative_performance'] = relative
        
        # Performance rating
        positive_indicators = 0
        total_indicators = 0
        
        # Check returns
        if performance.return_3m is not None:
            total_indicators += 1
            if performance.return_3m > 0.05:  # 5% positive return
                positive_indicators += 1
        
        # Check vs benchmark
        if performance.benchmark_3m is not None:
            total_indicators += 1
            if performance.benchmark_3m > 0:  # Outperforming benchmark
                positive_indicators += 1
        
        # Check Sharpe ratio
        if performance.sharpe_ratio is not None:
            total_indicators += 1
            if performance.sharpe_ratio > 1.0:  # Good risk-adjusted returns
                positive_indicators += 1
        
        # Check sector performance
        if performance.sector_performance_1m is not None:
            total_indicators += 1
            if performance.sector_performance_1m > 0:  # Outperforming sector
                positive_indicators += 1
        
        if total_indicators > 0:
            performance_score = positive_indicators / total_indicators
            if performance_score >= 0.75:
                summary['performance_rating'] = 'strong'
            elif performance_score >= 0.5:
                summary['performance_rating'] = 'good'
            elif performance_score >= 0.25:
                summary['performance_rating'] = 'neutral'
            else:
                summary['performance_rating'] = 'weak'
        
        return summary
