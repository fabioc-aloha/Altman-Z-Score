"""
Trend Analysis Chart Components

Chart components for time series analysis, trend visualization, and price correlation.
Includes price data fetching and trend chart generation.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import List, Optional, Tuple, Any, Dict
import pandas as pd

from .base import ChartBase
from ....common.logging_config import get_logger

logger = get_logger(__name__)


class PriceDataFetcher:
    """Utility class for fetching historical price data with candlestick support."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def fetch_historical_prices(self, ticker: str, results: List[Any], dates: List[datetime]) -> Tuple[List[datetime], List[float]]:
        """Fetch historical price data from FMP - legacy method for backward compatibility."""
        ohlc_data = self.fetch_ohlc_data(ticker, results, dates)
        if ohlc_data:
            dates = [item['date'] for item in ohlc_data]
            prices = [item['close'] for item in ohlc_data]
            return dates, prices
        return [], []
    
    def fetch_ohlc_data(self, ticker: str, results: List[Any], dates: List[datetime]) -> List[Dict[str, Any]]:
        """
        Fetch OHLC (Open, High, Low, Close) data optimized for candlestick charts.
        Uses improved FMP endpoints for better OHLC data availability.
        
        Returns:
            List of dictionaries with keys: date, open, high, low, close, volume
        """
        try:
            from ....layers.data_fetch.fmp_fetcher import FMPDataFetcher
            fmp_fetcher = FMPDataFetcher()
            
            # Calculate date range and determine granularity
            from_date, to_date, use_weekly = self._calculate_optimal_granularity(results, dates)
            
            self.logger.info(f"Fetching {'weekly' if use_weekly else 'daily'} OHLC data for {ticker} from {from_date}")
            
            # Get price data with appropriate granularity using improved endpoints
            price_data = None
            
            if use_weekly:
                # Try weekly OHLC data first
                try:
                    price_data = fmp_fetcher.get_historical_prices_weekly(ticker, from_date, to_date)
                    if price_data and len(price_data) > 0:
                        self.logger.info(f"Successfully fetched {len(price_data)} weekly OHLC records")
                except Exception as e:
                    self.logger.warning(f"Failed to fetch weekly OHLC data: {e}")
                    
                # Fallback to daily OHLC if weekly fails
                if not price_data or len(price_data) == 0:
                    try:
                        price_data = fmp_fetcher.get_historical_prices_daily_ohlc(ticker, from_date, to_date)
                        if price_data and len(price_data) > 0:
                            self.logger.info(f"Using daily OHLC data as fallback: {len(price_data)} records")
                    except Exception as e:
                        self.logger.warning(f"Failed to fetch daily OHLC data: {e}")
            else:
                # Try daily OHLC data first
                try:
                    price_data = fmp_fetcher.get_historical_prices_daily_ohlc(ticker, from_date, to_date)
                    if price_data and len(price_data) > 0:
                        self.logger.info(f"Successfully fetched {len(price_data)} daily OHLC records")
                except Exception as e:
                    self.logger.warning(f"Failed to fetch daily OHLC data: {e}")
                    
                # Fallback to original daily endpoint if OHLC fails
                if not price_data or len(price_data) == 0:
                    try:
                        price_data = fmp_fetcher.get_historical_prices_daily(ticker, from_date, to_date)
                        if price_data and len(price_data) > 0:
                            self.logger.info(f"Using original daily data as fallback: {len(price_data)} records")
                    except Exception as e:
                        self.logger.warning(f"Failed to fetch original daily data: {e}")
            
            if price_data and len(price_data) > 0:
                ohlc_data = self._process_ohlc_data(price_data, use_weekly)
                self.logger.info(f"Successfully processed {len(ohlc_data)} {'weekly' if use_weekly else 'daily'} OHLC records for {ticker}")
                
                # Log price range if we have valid OHLC data
                if ohlc_data and len(ohlc_data) > 0:
                    try:
                        high_prices = [item['high'] for item in ohlc_data if 'high' in item]
                        low_prices = [item['low'] for item in ohlc_data if 'low' in item]
                        if high_prices and low_prices:
                            self.logger.info(f"Price range: ${min(low_prices):.2f} - ${max(high_prices):.2f}")
                        else:
                            close_prices = [item['close'] for item in ohlc_data if 'close' in item]
                            if close_prices:
                                self.logger.info(f"Close price range: ${min(close_prices):.2f} - ${max(close_prices):.2f}")
                    except Exception as e:
                        self.logger.debug(f"Could not calculate price range: {e}")
                
                return ohlc_data
            else:
                self.logger.warning(f"No price data available from FMP for {ticker}")
                        
        except Exception as e:
            self.logger.error(f"Error fetching OHLC data from FMP: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return []
    
    def _calculate_optimal_granularity(self, results: List[Any], dates: List[datetime]) -> Tuple[str, Optional[str], bool]:
        """
        Calculate optimal date range and granularity for price data.
        
        Returns:
            Tuple of (from_date, to_date, use_weekly)
        """
        if len(results) > 1 and dates:
            # For multi-quarter analysis
            earliest_zscore_date = min(dates).replace(tzinfo=None)
            latest_zscore_date = max(dates).replace(tzinfo=None)
            
            # Calculate time span
            time_span = latest_zscore_date - earliest_zscore_date
            
            # Add buffer around the data
            buffer_start_date = earliest_zscore_date - pd.Timedelta(days=60)  # 2 months before
            buffer_end_date = latest_zscore_date + pd.Timedelta(days=30)     # 1 month after
            
            from_date = buffer_start_date.strftime('%Y-%m-%d')
            to_date = buffer_end_date.strftime('%Y-%m-%d')
            
            # Use weekly for spans > 6 months, daily for shorter periods
            use_weekly = time_span.days > 180
            
        else:
            # For single Z-Score point, get last 18 months of data
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.Timedelta(days=540)  # 18 months
            
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Use weekly for longer historical periods
            use_weekly = True
        
        return from_date, to_date, use_weekly
    
    def _process_ohlc_data(self, price_data: List[dict], is_weekly: bool = False) -> List[Dict[str, Any]]:
        """Process FMP OHLC data format for candlestick charts."""
        # FMP returns data in descending order (newest first), so reverse it
        price_data.reverse()
        
        # Process OHLC data
        ohlc_data = []
        for item in price_data:
            try:
                # Check if we have full OHLC data
                has_full_ohlc = all(key in item and item[key] is not None for key in ['open', 'high', 'low', 'close'])
                
                if has_full_ohlc:
                    # Full OHLC data available
                    ohlc_record = {
                        'date': pd.to_datetime(item['date']),
                        'open': float(item['open']),
                        'high': float(item['high']),
                        'low': float(item['low']),
                        'close': float(item['close']),
                        'volume': int(item.get('volume', 0)),
                        'has_full_ohlc': True
                    }
                else:
                    # Only close price available - create a synthetic OHLC record
                    close_price = float(item['close'])
                    ohlc_record = {
                        'date': pd.to_datetime(item['date']),
                        'open': close_price,
                        'high': close_price,
                        'low': close_price,
                        'close': close_price,
                        'volume': int(item.get('volume', 0)),
                        'has_full_ohlc': False
                    }
                    
                ohlc_data.append(ohlc_record)
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Skipping invalid OHLC record: {item} - {e}")
                continue
        
        return ohlc_data


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
            
            # Fetch OHLC data for candlestick chart
            ohlc_data = self.price_fetcher.fetch_ohlc_data(latest.ticker, results, dates)
            
            # Keep backward compatibility for existing price references
            if ohlc_data:
                price_dates = [item['date'] for item in ohlc_data]
                prices = [item['close'] for item in ohlc_data]
            else:
                price_dates, prices = [], []
            
            # Check for bankruptcy analysis
            is_bankruptcy_analysis = False
            bankruptcy_date = None
            
            if hasattr(latest, 'metadata') and latest.metadata and 'bankruptcy_date' in latest.metadata:
                is_bankruptcy_analysis = True
                bankruptcy_date = latest.metadata['bankruptcy_date']
                self.logger.info(f"Adding bankruptcy date marker to trend chart: {bankruptcy_date}")
            
            # Add Z-Score line on primary y-axis
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=scores,
                    mode='lines+markers',
                    line=dict(color='blue', width=3),
                    marker=dict(size=8),
                    name='Z-Score',
                    hovertemplate='Z-Score: %{y:.2f}<br>Date: %{x|%Y-%m-%d}<extra></extra>'
                ),
                row=row, col=col,
                secondary_y=False  # Primary y-axis for Z-Score
            )
            
            # Determine model-specific thresholds
            if latest.model_used == 'original':
                danger_threshold = 1.81
                safe_threshold = 3.0
                model_name = "Original Altman"
            elif latest.model_used == 'revised':
                danger_threshold = 1.1
                safe_threshold = 2.6
                model_name = "Revised Altman"
            else:
                danger_threshold = 1.81
                safe_threshold = 3.0
                model_name = "Original Altman"
            
            # Add Z-Score zone background colors
            if dates:
                date_range = [min(dates), max(dates)]
                z_score_max = max(scores) if scores else 5.0
                z_score_upper_limit = max(z_score_max * 1.1, 5.0)
                
                # Add distress zone (red background)
                fig.add_trace(
                    go.Scatter(
                        x=date_range + date_range[::-1],
                        y=[0, 0, danger_threshold, danger_threshold],
                        fill='toself',
                        fillcolor='rgba(255, 0, 0, 0.1)',
                        line=dict(color='rgba(255, 0, 0, 0)'),
                        name='Distress Zone',
                        showlegend=True,
                        hoverinfo='skip'
                    ),
                    row=row, col=col,
                    secondary_y=False
                )
                
                # Add gray zone (yellow background)
                fig.add_trace(
                    go.Scatter(
                        x=date_range + date_range[::-1],
                        y=[danger_threshold, danger_threshold, safe_threshold, safe_threshold],
                        fill='toself',
                        fillcolor='rgba(255, 255, 0, 0.1)',
                        line=dict(color='rgba(255, 255, 0, 0)'),
                        name='Gray Zone',
                        showlegend=True,
                        hoverinfo='skip'
                    ),
                    row=row, col=col,
                    secondary_y=False
                )
                
                # Add safe zone (green background)
                fig.add_trace(
                    go.Scatter(
                        x=date_range + date_range[::-1],
                        y=[safe_threshold, safe_threshold, z_score_upper_limit, z_score_upper_limit],
                        fill='toself',
                        fillcolor='rgba(0, 255, 0, 0.1)',
                        line=dict(color='rgba(0, 255, 0, 0)'),
                        name='Safe Zone',
                        showlegend=True,
                        hoverinfo='skip'
                    ),
                    row=row, col=col,
                    secondary_y=False
                )
            
            # Add threshold lines
            fig.add_trace(
                go.Scatter(
                    x=[min(dates), max(dates)] if dates else [0, 1],
                    y=[danger_threshold, danger_threshold],
                    mode='lines',
                    line=dict(color='red', width=2, dash='dash'),
                    name=f'{model_name} Distress Threshold ({danger_threshold})',
                    showlegend=True,
                    hovertemplate=f'Distress Threshold: {danger_threshold}<extra></extra>'
                ),
                row=row, col=col,
                secondary_y=False  # Primary y-axis for threshold
            )
            
            # Add safe zone threshold line
            fig.add_trace(
                go.Scatter(
                    x=[min(dates), max(dates)] if dates else [0, 1],
                    y=[safe_threshold, safe_threshold],
                    mode='lines',
                    line=dict(color='green', width=2, dash='dot'),
                    name=f'{model_name} Safe Threshold ({safe_threshold})',
                    showlegend=True,
                    hovertemplate=f'Safe Threshold: {safe_threshold}<extra></extra>'
                ),
                row=row, col=col,
                secondary_y=False  # Primary y-axis for threshold
            )
            
            # Configure primary y-axis for Z-Score with proper scale
            z_score_max = max(scores) if scores else 5.0
            z_score_upper_limit = max(z_score_max * 1.1, 5.0)  # At least 5.0 for context
            
            fig.update_yaxes(
                title_text="Z-Score", 
                title_font_color="blue",
                tickfont_color="blue",
                range=[0, z_score_upper_limit],  # Always start at 0 for consistent scaling
                zeroline=True,  # Show zero line for visual reference
                zerolinecolor='rgba(0,0,0,0.3)',
                zerolinewidth=1,
                row=row, col=col, 
                secondary_y=False
            )
            
            # Add price data on secondary y-axis if available
            if ohlc_data and len(ohlc_data) > 0:
                # Add candlestick chart on secondary y-axis
                fig.add_trace(
                    go.Candlestick(
                        x=[item['date'] for item in ohlc_data],
                        open=[item['open'] for item in ohlc_data],
                        high=[item['high'] for item in ohlc_data],
                        low=[item['low'] for item in ohlc_data],
                        close=[item['close'] for item in ohlc_data],
                        name='Stock Price',
                        increasing_line_color='#2E8B57',  # Sea green for up candles
                        decreasing_line_color='#DC143C',  # Crimson for down candles
                        increasing_fillcolor='#90EE90',   # Light green fill
                        decreasing_fillcolor='#FFB6C1',   # Light pink fill
                        line=dict(width=1),
                        # Note: Candlestick charts don't support hovertemplate
                        # They use built-in hover formatting
                    ),
                    row=row, col=col,
                    secondary_y=True  # Secondary y-axis for price
                )
                
                # Configure secondary y-axis for price
                fig.update_yaxes(
                    title_text="Price ($)", 
                    title_font_color="darkgreen",
                    tickfont_color="darkgreen",
                    row=row, col=col, 
                    secondary_y=True
                )
                
                # Optional: Add volume bars as a subtle overlay (commented out for cleaner look)
                # if any(item['volume'] > 0 for item in ohlc_data):
                #     self._add_volume_overlay(fig, ohlc_data, row, col)
                
                # Add bankruptcy date marker if available
                if is_bankruptcy_analysis and bankruptcy_date:
                    try:
                        # Convert to timestamp
                        bankruptcy_timestamp = pd.to_datetime(bankruptcy_date)
                        
                        # Add vertical line at bankruptcy date (spans both y-axes)
                        fig.add_vline(
                            x=bankruptcy_timestamp,
                            line=dict(color='red', width=3, dash='dot'),
                            annotation_text="Bankruptcy Date",
                            annotation_position="top",
                            annotation=dict(
                                bgcolor='rgba(255, 0, 0, 0.7)',
                                font=dict(color='white', size=10)
                            ),
                            row=row, col=col
                        )
                    except Exception as e:
                        self.logger.warning(f"Failed to add bankruptcy marker: {e}")
            else:
                # No price data - configure only primary y-axis for Z-Score with proper scale
                z_score_max = max(scores) if scores else 5.0
                z_score_upper_limit = max(z_score_max * 1.1, 5.0)  # At least 5.0 for context
                
                fig.update_yaxes(
                    title_text="Z-Score", 
                    title_font_color="blue",
                    tickfont_color="blue",
                    range=[0, z_score_upper_limit],  # Always start at 0 for consistent scaling
                    zeroline=True,  # Show zero line for visual reference
                    zerolinecolor='rgba(0,0,0,0.3)',
                    zerolinewidth=1,
                    row=row, col=col
                )
            
            # Debug logging
            self.logger.info(f"Building trend chart for {latest.ticker} with {len(results)} Z-Score points")
            if dates and scores:
                self.logger.info(f"Z-Score range: {min(scores):.2f} to {max(scores):.2f}")
                self.logger.info(f"Date range: {min(dates)} to {max(dates)}")
            
            if ohlc_data:
                high_prices = [item['high'] for item in ohlc_data]
                low_prices = [item['low'] for item in ohlc_data]
                self.logger.info(f"OHLC data available: {len(ohlc_data)} candlesticks, price range: ${min(low_prices):.2f} - ${max(high_prices):.2f}")
            elif prices:
                self.logger.info(f"Price data available: {len(prices)} points, range: ${min(prices):.2f} to ${max(prices):.2f}")
            else:
                self.logger.info("No price data available for trend chart")
            
            # Set x-axis title
            fig.update_xaxes(title_text="Date", row=row, col=col)
            
        except Exception as e:
            self.logger.error(f"Error adding trend chart to figure: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't re-raise - allow dashboard generation to continue
                
            # Set chart title
            chart_title = "Z-Score Progression"
            if is_bankruptcy_analysis:
                chart_title = "Pre-Bankruptcy Z-Score Progression"
                
            fig.update_layout(
                title={
                    'text': chart_title,
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error rendering trend chart: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Add error message to chart
            fig.add_annotation(
                text=f"Error rendering trend chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(color="red", size=14),
                row=row, col=col
            )
    
    def _build_zscore_timeseries(self, results: List[Any], start_date: Optional[str]) -> Tuple[List[datetime], List[float]]:
        """Build time series data from Z-Score results."""
        dates = []
        scores = []
        
        for r in results:
            try:
                # Try to parse the timestamp - handle different formats
                timestamp = getattr(r, 'period_date', None) or getattr(r, 'calculation_timestamp', None)
                if timestamp:
                    # Handle different date formats
                    if isinstance(timestamp, str):
                        if 'T' in timestamp:
                            # ISO format
                            date = datetime.fromisoformat(timestamp.replace('Z', ''))
                        else:
                            # Simple date format
                            date = datetime.strptime(timestamp, '%Y-%m-%d')
                    else:
                        # Assume it's already a datetime
                        date = timestamp
                    
                    dates.append(date)
                    scores.append(r.z_score)
                else:
                    self.logger.warning(f"No valid timestamp found for result: {r.ticker}")
            except Exception as e:
                self.logger.warning(f"Failed to parse timestamp for {r.ticker}: {e}")
                # Skip this result
                continue
        
        # Filter by start_date if provided
        if start_date and dates:
            try:
                sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                filtered = [(d, s) for d, s in zip(dates, scores) if d.date() >= sd]
                if filtered:
                    dates, scores = zip(*filtered)
                    dates, scores = list(dates), list(scores)
            except Exception as e:
                self.logger.warning(f"Failed to filter by start_date {start_date}: {e}")
        
        return dates, scores
    
    def _add_volume_overlay(self, fig: go.Figure, ohlc_data: List[Dict[str, Any]], row: int, col: int) -> None:
        """
        Add volume bars as a subtle overlay on the price chart.
        
        Args:
            fig: Plotly figure to add volume to
            ohlc_data: OHLC data including volume
            row: Subplot row
            col: Subplot column
        """
        try:
            volume_data = [item['volume'] for item in ohlc_data if item['volume'] > 0]
            if not volume_data:
                return
            
            # Normalize volume to a reasonable scale (0-20% of price range)
            max_volume = max(volume_data)
            min_volume = min(volume_data)
            volume_range = max_volume - min_volume if max_volume > min_volume else max_volume
            
            if volume_range > 0:
                # Get price range for scaling
                high_prices = [item['high'] for item in ohlc_data]
                low_prices = [item['low'] for item in ohlc_data]
                price_range = max(high_prices) - min(low_prices)
                
                # Scale volume to 15% of price range
                volume_scale = (price_range * 0.15) / volume_range
                volume_baseline = min(low_prices) - (price_range * 0.05)
                
                # Add volume bars
                fig.add_trace(
                    go.Bar(
                        x=[item['date'] for item in ohlc_data],
                        y=[item['volume'] * volume_scale + volume_baseline for item in ohlc_data],
                        name='Volume',
                        marker_color='rgba(128, 128, 128, 0.3)',  # Semi-transparent gray
                        opacity=0.3,
                        showlegend=False,
                        hovertemplate='Volume: %{customdata:,.0f}<extra></extra>',
                        customdata=[item['volume'] for item in ohlc_data]
                    ),
                    row=row, col=col,
                    secondary_y=True  # Same axis as price
                )
                
                self.logger.debug(f"Added volume overlay with {len(volume_data)} volume bars")
                
        except Exception as e:
            self.logger.warning(f"Failed to add volume overlay: {e}")


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
