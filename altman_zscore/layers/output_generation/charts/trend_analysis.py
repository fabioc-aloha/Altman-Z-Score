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
        # Cache for fiscal year end dates to avoid repeated API calls
        self._fiscal_year_cache = {}
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, 
                     results: List[Any], market_analysis: Any = None, 
                     start_date: Optional[str] = None, forecasts: Optional[List[Any]] = None, **kwargs) -> None:
        """Add trend chart to figure with optional forecast data shown as dashed lines."""
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
            
            # Add historical Z-Score line on primary y-axis
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=scores,
                    mode='lines+markers',
                    line=dict(color='blue', width=3),
                    marker=dict(size=8),
                    name='Historical Z-Score',
                    hovertemplate='Z-Score: %{y:.2f}<br>Date: %{x|%Y-%m-%d}<extra></extra>'
                ),
                row=row, col=col,
                secondary_y=False  # Primary y-axis for Z-Score
            )
            
            # Add forecast Z-Score line if forecasts are provided
            if forecasts and len(forecasts) > 0:
                self.logger.info(f"Adding forecast visualization with {len(forecasts)} forecast scenarios")
                forecast_dates, forecast_scores = self._build_forecast_timeseries(forecasts, latest.ticker)
                
                if forecast_dates and forecast_scores:
                    self.logger.info(f"Forecast data: {len(forecast_dates)} dates, scores: {forecast_scores}")
                    
                    # Connect last historical point to first forecast point for continuity
                    if dates and scores:
                        # Ensure dates are sorted and get the last point
                        last_historical_date = max(dates)
                        last_historical_score = scores[dates.index(last_historical_date)]
                        
                        self.logger.info(f"Connecting forecast from last historical point: {last_historical_date}, Z-Score: {last_historical_score}")
                        
                        # Create connecting line from last historical to first forecast point
                        # But only use the last historical point for the line connection, not as a marker
                        if forecast_dates and forecast_scores:
                            # Add a connecting line segment without markers
                            fig.add_trace(
                                go.Scatter(
                                    x=[last_historical_date, forecast_dates[0]],
                                    y=[last_historical_score, forecast_scores[0]],
                                    mode='lines',
                                    line=dict(color='blue', width=3, dash='dash'),
                                    name='Forecast Connection',
                                    showlegend=False,  # Don't show in legend
                                    hoverinfo='skip'   # Skip hover for connection line
                                ),
                                row=row, col=col,
                                secondary_y=False
                            )
                        
                        # Use only the forecast points for the main forecast trace (no duplication)
                        connected_dates = forecast_dates
                        connected_scores = forecast_scores
                        
                        self.logger.info(f"Forecast series: {len(connected_dates)} points from {connected_dates[0]} to {connected_dates[-1]}")
                    else:
                        connected_dates = forecast_dates
                        connected_scores = forecast_scores
                        self.logger.info("No historical data available, showing forecast only")
                    
                    fig.add_trace(
                        go.Scatter(
                            x=connected_dates,
                            y=connected_scores,
                            mode='lines+markers',
                            line=dict(color='blue', width=3, dash='dash'),  # Dashed line for forecast
                            marker=dict(size=8, symbol='diamond'),  # Different marker for forecast
                            name='Forecast Z-Score',
                            hovertemplate='Forecast Z-Score: %{y:.2f}<br>Date: %{x|%Y-%m-%d}<extra></extra>'
                        ),
                        row=row, col=col,
                        secondary_y=False  # Primary y-axis for Z-Score
                    )
                    
                    # Add confidence intervals for forecasts if available
                    self._add_forecast_confidence_bands(fig, row, col, forecasts, forecast_dates)
                    
                    self.logger.info("Forecast visualization added successfully")
                else:
                    self.logger.warning("No forecast dates/scores available for visualization")
            else:
                self.logger.info("No forecast data provided for trend chart")
            
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
                
                # Calculate y-axis range for zones
                if scores:
                    z_score_min = min(scores)
                    z_score_max = max(scores)
                    z_range = z_score_max - z_score_min
                    padding = max(z_range * 0.1, 0.5)
                    
                    # Start at 0 if all scores are positive, otherwise allow negative values
                    if z_score_min >= 0:
                        y_min = 0.0  # Start at 0 for positive Z-Scores
                    else:
                        y_min = z_score_min - padding  # Allow negative range when needed
                    y_max = max(z_score_max + padding, 5.0)
                else:
                    y_min = 0.0  # Default to starting at 0
                    y_max = 5.0
                
                # Add distress zone (red background) - from bottom to danger threshold
                fig.add_trace(
                    go.Scatter(
                        x=date_range + date_range[::-1],
                        y=[y_min, y_min, danger_threshold, danger_threshold],
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
                        y=[safe_threshold, safe_threshold, y_max, y_max],
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
            if scores:
                z_score_min = min(scores)
                z_score_max = max(scores)
                
                # Add padding to min/max for better visualization
                z_range = z_score_max - z_score_min
                padding = max(z_range * 0.1, 0.5)  # At least 0.5 padding for context
                
                # Start at 0 if all scores are positive, otherwise allow negative values
                if z_score_min >= 0:
                    y_min = 0.0  # Start at 0 for positive Z-Scores
                else:
                    y_min = z_score_min - padding  # Allow negative range when needed
                y_max = max(z_score_max + padding, 5.0)  # At least 5.0 for context with thresholds
                
                self.logger.info(f"Z-Score y-axis range: {y_min:.2f} to {y_max:.2f} (data range: {z_score_min:.2f} to {z_score_max:.2f})")
            else:
                # Default range when no data
                y_min = 0.0  # Start at 0 by default
                y_max = 5.0
            
            fig.update_yaxes(
                title_text="Z-Score", 
                title_font_color="blue",
                tickfont_color="blue",
                range=[y_min, y_max],
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
                if scores:
                    z_score_min = min(scores)
                    z_score_max = max(scores)
                    
                    # Add padding to min/max for better visualization
                    z_range = z_score_max - z_score_min
                    padding = max(z_range * 0.1, 0.5)  # At least 0.5 padding for context
                    
                    # Start at 0 if all scores are positive, otherwise allow negative values
                    if z_score_min >= 0:
                        y_min = 0.0  # Start at 0 for positive Z-Scores
                    else:
                        y_min = z_score_min - padding  # Allow negative range when needed
                    y_max = max(z_score_max + padding, 5.0)  # At least 5.0 for context with thresholds
                else:
                    # Default range when no data
                    y_min = 0.0  # Start at 0 by default
                    y_max = 5.0
                
                fig.update_yaxes(
                    title_text="Z-Score", 
                    title_font_color="blue",
                    tickfont_color="blue",
                    range=[y_min, y_max],
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
            
            # Set x-axis title and configure range slider
            fig.update_xaxes(
                title_text="Date", 
                row=row, col=col,
                rangeslider=dict(
                    visible=True,
                    thickness=0.08  # Reduce height from default 0.15 to 0.08 (about half)
                )
            )
            
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
        date_score_pairs = []
        
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
                    
                    date_score_pairs.append((date, r.z_score))
                else:
                    self.logger.warning(f"No valid timestamp found for result: {r.ticker}")
            except Exception as e:
                self.logger.warning(f"Failed to parse timestamp for {r.ticker}: {e}")
                # Skip this result
                continue
        
        # Sort by date to ensure proper chronological order
        date_score_pairs.sort(key=lambda x: x[0])
        
        # Filter by start_date if provided
        if start_date and date_score_pairs:
            try:
                sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                date_score_pairs = [(d, s) for d, s in date_score_pairs if d.date() >= sd]
            except Exception as e:
                self.logger.warning(f"Failed to filter by start_date {start_date}: {e}")
        
        # Extract dates and scores
        if date_score_pairs:
            dates, scores = zip(*date_score_pairs)
            return list(dates), list(scores)
        else:
            return [], []
    
    def _build_forecast_timeseries(self, forecasts: List[Any], ticker: str = None) -> Tuple[List[datetime], List[float]]:
        """Build time series data from forecast results."""
        dates = []
        scores = []
        
        try:
            self.logger.info(f"Building forecast timeseries from {len(forecasts)} forecast items")
            
            # Sort forecasts by period/date
            forecast_list = []
            for i, forecast in enumerate(forecasts):
                self.logger.info(f"Processing forecast {i}: type={type(forecast)}")
                
                # Handle ForecastScenario objects directly
                if hasattr(forecast, 'scenario_name') and hasattr(forecast, 'z_score'):
                    scenario_name = forecast.scenario_name.lower()
                    self.logger.info(f"Forecast scenario {i}: name='{scenario_name}', z_score={forecast.z_score}")
                    
                    # Only use base case scenarios for the main trend line
                    if scenario_name in ['base case', 'base', 'base case scenario', 'consensus']:
                        # Parse forecast period to create date
                        period = getattr(forecast, 'forecast_period', 'Unknown')
                        self.logger.info(f"Forecast period: {period}")
                        
                        if period.startswith('FY'):
                            # Handle fiscal year format like "FY2025", "FY2026"
                            year = int(period[2:])  # Remove "FY" prefix
                            
                            # Get company-specific fiscal year end date
                            fiscal_year_end = self._get_fiscal_year_end_date(ticker, year)
                            forecast_date = fiscal_year_end
                        elif 'Annual' in period:
                            # Extract year from period string like "2026 Annual"
                            year = int(period.split()[0])
                            # Use end of year as forecast date
                            forecast_date = datetime(year, 12, 31)
                        elif 'Q' in period:
                            # Handle quarterly periods like "2025 Q4"
                            parts = period.split()
                            if len(parts) >= 2:
                                year = int(parts[0])
                                quarter = parts[1]
                                if quarter == 'Q1':
                                    forecast_date = datetime(year, 3, 31)
                                elif quarter == 'Q2':
                                    forecast_date = datetime(year, 6, 30)
                                elif quarter == 'Q3':
                                    forecast_date = datetime(year, 9, 30)
                                elif quarter == 'Q4':
                                    forecast_date = datetime(year, 12, 31)
                                else:
                                    forecast_date = datetime(year, 12, 31)  # Default to end of year
                            else:
                                forecast_date = datetime.now().replace(year=datetime.now().year + 1, month=12, day=31)
                        else:
                            # Fallback to current year + 1
                            forecast_date = datetime.now().replace(year=datetime.now().year + 1, month=12, day=31)
                        
                        self.logger.info(f"Forecast date: {forecast_date}, Z-Score: {forecast.z_score}")
                        forecast_list.append((forecast_date, forecast.z_score))
                else:
                    self.logger.warning(f"Forecast {i} does not have expected ForecastScenario structure")
            
            # Sort by date
            forecast_list.sort(key=lambda x: x[0])
            
            # Extract dates and scores
            for date, score in forecast_list:
                dates.append(date)
                scores.append(score)
                
            self.logger.info(f"Final forecast timeseries: {len(dates)} points")
                
        except Exception as e:
            self.logger.error(f"Error building forecast timeseries: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return dates, scores
    
    def _add_forecast_confidence_bands(self, fig: go.Figure, row: int, col: int, 
                                     forecasts: List[Any], forecast_dates: List[datetime]) -> None:
        """Add confidence bands around forecast line."""
        try:
            if not forecasts or not forecast_dates:
                return
            
            # Build confidence bands from forecast scenarios
            upper_bounds = []
            lower_bounds = []
            
            for forecast in forecasts:
                if hasattr(forecast, 'scenarios') and forecast.scenarios:
                    scenario_scores = [s.z_score for s in forecast.scenarios]
                    if scenario_scores:
                        upper_bounds.append(max(scenario_scores))
                        lower_bounds.append(min(scenario_scores))
            
            if len(upper_bounds) == len(forecast_dates) and len(lower_bounds) == len(forecast_dates):
                # Create confidence band using fill_between equivalent
                combined_x = forecast_dates + forecast_dates[::-1]
                combined_y = upper_bounds + lower_bounds[::-1]
                
                fig.add_trace(
                    go.Scatter(
                        x=combined_x,
                        y=combined_y,
                        fill='toself',
                        fillcolor='rgba(0, 0, 255, 0.1)',  # Light blue fill
                        line=dict(color='rgba(0, 0, 255, 0)'),  # No line
                        name='Forecast Confidence Band',
                        showlegend=True,
                        hoverinfo='skip'
                    ),
                    row=row, col=col,
                    secondary_y=False
                )
                
        except Exception as e:
            self.logger.error(f"Error adding forecast confidence bands: {e}")
    
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
    
    def _get_fiscal_year_end_date(self, ticker: str, fiscal_year: int) -> datetime:
        """
        Get the specific fiscal year end date for a company by dynamically fetching 
        from FMP API financial statements.
        
        Args:
            ticker: Company ticker symbol
            fiscal_year: Fiscal year (e.g., 2025)
            
        Returns:
            datetime: The fiscal year end date for the company
        """
        try:
            # Check cache first
            if ticker in self._fiscal_year_cache:
                month, day = self._fiscal_year_cache[ticker]
                calendar_year = fiscal_year
                fiscal_date = datetime(calendar_year, month, day)
                self.logger.debug(f"Using cached fiscal year end for {ticker}: {fiscal_date.strftime('%Y-%m-%d')} (FY{fiscal_year})")
                return fiscal_date
            
            # Try to get fiscal year end from recent financial statements
            fiscal_year_end = self._fetch_fiscal_year_end_from_api(ticker)
            
            if fiscal_year_end:
                month, day = fiscal_year_end
                
                # Cache the result
                self._fiscal_year_cache[ticker] = (month, day)
                
                # Calculate the correct calendar year for the fiscal year end
                # For fiscal years ending Jan-June, they typically end in the fiscal year
                # For fiscal years ending July-December, they typically end in the fiscal year
                calendar_year = fiscal_year
                
                fiscal_date = datetime(calendar_year, month, day)
                
                self.logger.info(f"Using API-derived fiscal year end for {ticker}: {fiscal_date.strftime('%Y-%m-%d')} (FY{fiscal_year})")
                return fiscal_date
            else:
                # Fallback to December 31 for unknown companies
                default_date = datetime(fiscal_year, 12, 31)
                self.logger.info(f"Using default fiscal year end for {ticker}: {default_date.strftime('%Y-%m-%d')} (FY{fiscal_year}) - API lookup failed")
                return default_date
                
        except Exception as e:
            self.logger.warning(f"Error calculating fiscal year end for {ticker} FY{fiscal_year}: {e}")
            # Fallback to December 31 of the fiscal year
            return datetime(fiscal_year, 12, 31)
    
    def _fetch_fiscal_year_end_from_api(self, ticker: str) -> Optional[Tuple[int, int]]:
        """
        Fetch fiscal year end date from FMP API by examining recent financial statements.
        
        Args:
            ticker: Company ticker symbol
            
        Returns:
            Tuple of (month, day) if found, None otherwise
        """
        try:
            from ....layers.data_fetch.fmp_fetcher import FMPDataFetcher
            fmp_fetcher = FMPDataFetcher()
            
            # Get recent income statements to determine fiscal year end pattern
            self.logger.debug(f"Fetching fiscal year end pattern for {ticker} from API")
            
            # Try to get annual financial statements for the last 2 years
            income_data = fmp_fetcher.get_income_statement(ticker, period='annual', limit=3)
            
            if income_data and len(income_data) >= 2:
                # Look at the dates of the most recent annual reports
                fiscal_year_ends = []
                
                for statement in income_data[:2]:  # Look at last 2 years
                    if 'date' in statement:
                        try:
                            date_str = statement['date']
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                            fiscal_year_ends.append((date_obj.month, date_obj.day))
                            self.logger.debug(f"Found fiscal year end: {date_obj.month}/{date_obj.day} from {date_str}")
                        except ValueError as e:
                            self.logger.debug(f"Could not parse date {statement.get('date')}: {e}")
                            continue
                
                # Check if we have consistent fiscal year end dates
                if len(fiscal_year_ends) >= 2:
                    # Check if the fiscal year ends are consistent (same month/day)
                    if fiscal_year_ends[0] == fiscal_year_ends[1]:
                        month, day = fiscal_year_ends[0]
                        self.logger.info(f"Determined fiscal year end for {ticker}: {month}/{day} (consistent pattern)")
                        return (month, day)
                    else:
                        # Use the most recent one if they differ
                        month, day = fiscal_year_ends[0]
                        self.logger.info(f"Using most recent fiscal year end for {ticker}: {month}/{day} (inconsistent pattern)")
                        return (month, day)
                elif len(fiscal_year_ends) == 1:
                    # Only one data point, but better than nothing
                    month, day = fiscal_year_ends[0]
                    self.logger.info(f"Using single fiscal year end data point for {ticker}: {month}/{day}")
                    return (month, day)
            
            # If income statement doesn't work, try balance sheet
            balance_data = fmp_fetcher.get_balance_sheet(ticker, period='annual', limit=2)
            
            if balance_data and len(balance_data) >= 1:
                statement = balance_data[0]
                if 'date' in statement:
                    try:
                        date_str = statement['date']
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        month, day = date_obj.month, date_obj.day
                        self.logger.info(f"Determined fiscal year end for {ticker} from balance sheet: {month}/{day}")
                        return (month, day)
                    except ValueError as e:
                        self.logger.debug(f"Could not parse balance sheet date {statement.get('date')}: {e}")
            
            self.logger.warning(f"Could not determine fiscal year end for {ticker} from API data")
            return None
            
        except Exception as e:
            self.logger.warning(f"Error fetching fiscal year end from API for {ticker}: {e}")
            return None
