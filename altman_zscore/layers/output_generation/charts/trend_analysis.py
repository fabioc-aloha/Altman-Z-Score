"""
Trend Analysis Chart Components

Chart components for time series analysis, trend visualization, and price correlation.
Includes price data fetching and trend chart generation.
"""

import plotly.graph_objects as go
from datetime import datetime
from typing import List, Optional, Tuple, Any
import pandas as pd

from .base import ChartBase
from ....common.logging_config import get_logger

logger = get_logger(__name__)


class PriceDataFetcher:
    """Utility class for fetching historical price data."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def fetch_historical_prices(self, ticker: str, results: List[Any], dates: List[datetime]) -> Tuple[List[datetime], List[float]]:
        """Fetch historical price data from FMP."""
        price_dates = []
        prices = []
        
        try:
            from ....layers.data_fetch.fmp_fetcher import FMPDataFetcher
            fmp_fetcher = FMPDataFetcher()
            
            # Calculate date range for price data
            from_date, to_date = self._calculate_date_range(results, dates)
            
            self.logger.info(f"Fetching FMP price data for {ticker} from {from_date}")
            
            # Get daily price data from FMP
            price_data = fmp_fetcher.get_historical_prices_daily(ticker, from_date, to_date)
            
            if price_data and len(price_data) > 0:
                price_dates, prices = self._process_price_data(price_data)
                self.logger.info(f"Successfully fetched {len(price_dates)} price records from FMP for {ticker}")
                self.logger.info(f"FMP price range: ${min(prices):.2f} - ${max(prices):.2f}")
            else:
                self.logger.warning(f"No price data available from FMP for {ticker}")
                        
        except Exception as e:
            self.logger.error(f"Error fetching price data from FMP: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return price_dates, prices
    
    def _calculate_date_range(self, results: List[Any], dates: List[datetime]) -> Tuple[str, Optional[str]]:
        """Calculate the appropriate date range for price data."""
        if len(results) > 1 and dates:
            # For multi-quarter analysis, get data from 30 days before first quarter
            earliest_zscore_date = min(dates).replace(tzinfo=None)
            buffer_start_date = earliest_zscore_date - pd.Timedelta(days=30)
            from_date = buffer_start_date.strftime('%Y-%m-%d')
            to_date = None
        else:
            # For single Z-Score point, get last 2 years of data
            from_date = (pd.Timestamp.now() - pd.Timedelta(days=730)).strftime('%Y-%m-%d')
            to_date = None
        
        return from_date, to_date
    
    def _process_price_data(self, price_data: List[dict]) -> Tuple[List[datetime], List[float]]:
        """Process FMP price data format."""
        # FMP returns data in descending order (newest first), so reverse it
        price_data.reverse()
        
        # Extract dates and prices
        price_dates = [pd.to_datetime(item['date']) for item in price_data]
        prices = [float(item['close']) for item in price_data]
        
        return price_dates, prices


class TrendChart(ChartBase):
    """Chart component for trend analysis with Z-Score and price correlation."""
    
    def __init__(self):
        super().__init__()
        self.price_fetcher = PriceDataFetcher()
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, 
                     results: List[Any], market_analysis: Any = None, 
                     start_date: Optional[str] = None, **kwargs) -> None:
        """Add trend chart to figure."""
        try:
            # Build Z-Score time series
            dates, scores = self._build_zscore_timeseries(results, start_date)
            latest = results[0]
            
            # Fetch historical prices
            price_dates, prices = self.price_fetcher.fetch_historical_prices(latest.ticker, results, dates)
            
            self.logger.info(f"Z-Score data: {len(dates)} points, scores: {scores}")
            self.logger.info(f"Price data: {len(price_dates)} points for dual y-axis chart")
            
            # Add Z-Score trace on primary y-axis
            self._add_zscore_trace(fig, dates, scores, row, col)
            
            # Add price trace on secondary y-axis
            self._add_price_trace(fig, price_dates, prices, latest.ticker, row, col)
            
            # Add Z-Score risk zones
            self.add_risk_zone_lines(fig, row, col)
            
            # Update y-axis labels
            fig.update_yaxes(title_text="Z-Score", row=row, col=col, secondary_y=False)
            fig.update_yaxes(title_text="Price ($)", row=row, col=col, secondary_y=True)
                         
        except Exception as e:
            self.logger.warning(f"Could not generate trend chart: {str(e)}")
            import traceback
            self.logger.warning(f"Traceback: {traceback.format_exc()}")
    
    def _build_zscore_timeseries(self, results: List[Any], start_date: Optional[str]) -> Tuple[List[datetime], List[float]]:
        """Build time series data from Z-Score results."""
        dates = [datetime.fromisoformat(r.calculation_timestamp) for r in results]
        scores = [r.z_score for r in results]
        
        # Filter by start_date if provided
        if start_date:
            sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            filtered = [(d, s) for d, s in zip(dates, scores) if d.date() >= sd]
            if filtered:
                dates, scores = zip(*filtered)
        
        return list(dates), list(scores)
    
    def _add_zscore_trace(self, fig: go.Figure, dates: List[datetime], scores: List[float], row: int, col: int) -> None:
        """Add Z-Score trace to the chart."""
        marker_colors = self.get_marker_colors(scores)
        fig.add_trace(
            go.Scatter(
                x=dates, y=scores, 
                mode='lines+markers', 
                name='Z-Score',
                line=dict(color='blue', width=3),
                marker=dict(size=10, color=marker_colors)
            ), 
            row=row, col=col,
            secondary_y=False  # Primary y-axis for Z-Score
        )
    
    def _add_price_trace(self, fig: go.Figure, price_dates: List[datetime], prices: List[float], 
                        ticker: str, row: int, col: int) -> None:
        """Add price trace to the chart on secondary y-axis."""
        if price_dates and prices:
            min_price, max_price = min(prices), max(prices)
            if max_price > min_price:
                # Add price trace to secondary y-axis with original values
                fig.add_trace(
                    go.Scatter(
                        x=price_dates, 
                        y=prices,  # Use actual prices
                        mode='lines',
                        name=f'Price ($)',
                        line=dict(color='green', width=2, dash='dot'),
                        opacity=0.8
                    ),
                    row=row, col=col,
                    secondary_y=True  # Secondary y-axis for price
                )
                
                self.logger.info("Price trace added successfully on secondary y-axis")
            else:
                self.logger.warning(f"Price data has no variance for {ticker}")
        else:
            self.logger.warning(f"No price data available for trend chart - price_dates: {len(price_dates) if price_dates else 0}, prices: {len(prices) if prices else 0}")


class AICommentaryAnnotation:
    """Utility class for adding AI commentary annotations to charts."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def add_to_figure(self, fig: go.Figure, ai_analysis: Any) -> None:
        """Add AI commentary summary as a text annotation on the chart."""
        try:
            if not ai_analysis or not hasattr(ai_analysis, 'llm_final_commentary') or not ai_analysis.llm_final_commentary:
                return
            
            summary_text = self._extract_commentary_summary(ai_analysis.llm_final_commentary)
            confidence_text = self._get_confidence_text(ai_analysis)
            
            # Add as title annotation
            fig.add_annotation(
                text=f"<b>AI Analysis Summary:</b> {summary_text}{confidence_text}",
                xref="paper", yref="paper",
                x=0.5, y=1.02,
                showarrow=False,
                font=dict(size=11, color='darkblue'),
                align="center",
                bgcolor="rgba(240,248,255,0.8)",
                bordercolor="lightblue",
                borderwidth=1,
                width=900
            )
            
            self.logger.debug("AI commentary annotation added to chart")
            
        except Exception as e:
            self.logger.warning(f"Failed to add AI commentary annotation: {str(e)}")
    
    def _extract_commentary_summary(self, commentary: str) -> str:
        """Extract a summary from AI commentary."""
        lines = [line.strip() for line in commentary.split('\n') if line.strip()]
        summary_text = ""
        
        # Look for executive summary section
        for i, line in enumerate(lines):
            if 'executive' in line.lower() and 'summary' in line.lower():
                # Take next few lines after executive summary header
                summary_lines = []
                for j in range(i+1, min(i+4, len(lines))):
                    if not lines[j].startswith('#') and len(lines[j]) > 20:
                        summary_lines.append(lines[j])
                if summary_lines:
                    summary_text = ' '.join(summary_lines)[:300] + "..."
                break
        
        # Fallback to first substantial paragraph if no executive summary found
        if not summary_text:
            for line in lines:
                if not line.startswith('#') and len(line) > 50:
                    summary_text = line[:300] + "..."
                    break
        
        # Final fallback to first 300 characters
        if not summary_text:
            summary_text = commentary[:300] + "..."
        
        return summary_text
    
    def _get_confidence_text(self, ai_analysis: Any) -> str:
        """Get confidence text for annotation."""
        if hasattr(ai_analysis, 'overall_ai_confidence') and ai_analysis.overall_ai_confidence:
            return f" (AI Confidence: {ai_analysis.overall_ai_confidence:.1%})"
        return ""
