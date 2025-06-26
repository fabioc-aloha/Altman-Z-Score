"""
Chart Generator - Create visualizations for Z-Score analysis

This module generates interactive charts and visualizations from Z-Score results,
providing visual insights into financial health and risk assessment.

Key Features:
- Z-Score trend charts with risk zone indicators
- Component breakdown visualizations
- Comparative analysis charts
- Interactive HTML charts with Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly.graph_objs import Figure
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.exceptions import OutputGenerationError
from ..zscore_calculation import ZScoreCalculationResult

logger = get_logger(__name__)


class ChartGenerator:
    """Generator for Z-Score visualization charts."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize chart generator.
        
        Args:
            output_base_path: Base directory for output files        
        """

        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
    
    def generate_zscore_dashboard(self, zscore_results, market_analysis=None, start_date: Optional[str] = None) -> str:
        """
        Generate comprehensive Z-Score dashboard chart using multiple periods for trend,
        enhanced with market analysis insights.
        
        Args:
            zscore_results: Z-Score calculation result or list of results
            market_analysis: Optional market analysis results for enhanced insights
            start_date (Optional[str]): Optional start date for filtering results (format: YYYY-MM-DD)
            
        Returns:
            str: Path to generated HTML chart file
        """

        try:
            # Normalize input to list of results
            results = zscore_results if isinstance(zscore_results, list) else [zscore_results]
            latest = results[0]
            ticker_dir = self.output_base_path / latest.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            chart_path = ticker_dir / f"{latest.ticker}_zscore_dashboard.html"
              # Enhanced layout based on whether market analysis is available
            if market_analysis:
                # Create enhanced subplot figure with market analysis
                # Note: Using "xy" instead of "indicator" to avoid xaxis property conflicts
                fig = make_subplots(
                    rows=4, cols=3,
                    subplot_titles=(
                        'Z-Score Analysis',
                        'Component Breakdown', 
                        'Investment Recommendation',
                        'Data Quality Metrics',
                        'Technical Indicators',
                        'Valuation Metrics',
                        'Performance Metrics',
                        'Risk-Return Analysis',
                        '',
                        'Z-Score & Price Trend',
                        '',
                        ''
                    ),                    
                    specs=[
                        [{"type": "xy"}, {"type": "bar"}, {"type": "xy"}],
                        [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                        [{"type": "bar"}, {"type": "bar"}, {"type": "xy"}],
                        [{"type": "xy", "secondary_y": True, "colspan": 3}, None, None]  # Enable secondary y-axis for trend chart
                    ],                    
                    row_heights=[0.25, 0.25, 0.25, 0.25],
                    vertical_spacing=0.08
                )
            else:                
                fig = make_subplots(
                    rows=3, cols=2,
                    subplot_titles=(
                        'Z-Score Analysis',
                        'Component Breakdown',
                        'Data Quality Metrics',
                        'Z-Score & Price Trend'
                    ),                    
                    specs=[
                        [{"type": "xy"}, {"type": "bar"}],
                        [{"type": "bar"}, {"type": "bar"}],
                        [{"type": "xy", "secondary_y": True, "colspan": 2}, None]  # Enable secondary y-axis for trend chart
                    ],                    
                    row_heights=[0.3, 0.3, 0.4],
                    vertical_spacing=0.08
                )
            # Add Z-Score analysis (risk zones)
            self._add_risk_zone_chart(fig, latest, row=1, col=1)
            
            # Add component breakdown
            self._add_component_breakdown(fig, latest, row=1, col=2)
            
            # Add enhanced market analysis components if available
            if market_analysis:
                # Add investment recommendation indicator
                self._add_investment_recommendation(fig, market_analysis, row=1, col=3)
                
                # Add data quality pie chart
                self._add_data_quality_chart(fig, latest, row=2, col=1)
                
                # Add technical indicators
                self._add_technical_indicators(fig, market_analysis, row=2, col=2)
                
                # Add valuation metrics
                self._add_valuation_metrics(fig, market_analysis, row=2, col=3)
                
                # Add performance metrics
                self._add_performance_metrics(fig, market_analysis, row=3, col=1)
                
                # Add risk-return analysis
                self._add_risk_return_analysis(fig, market_analysis, row=3, col=2)
                  # Add enhanced trend chart
                self._add_enhanced_trend_chart(fig, results, market_analysis, start_date, row=4, col=1)
            else:
                # Original layout for Z-Score only
                self._add_data_quality_chart(fig, latest, row=2, col=1)
                self._add_basic_trend_chart(fig, results, latest, start_date, row=3, col=1)
            
            # Update layout with enhanced features
            title_suffix = " (Enhanced with Market Analysis)" if market_analysis else ""
            height = 1400 if market_analysis else 1000
            
            fig.update_layout(
                title=f"Altman Z-Score Analysis Dashboard - {latest.ticker}{title_suffix}",
                height=height,
                showlegend=True
            )
            
            # Configure secondary y-axis for price data in the trend chart
            if market_analysis:
                # For enhanced layout, the trend chart is in row 4
                fig.update_yaxes(title_text="Z-Score", row=4, col=1, secondary_y=False)
                fig.update_yaxes(
                    title_text="Price ($)",
                    row=4, col=1, secondary_y=True,
                    showgrid=False,
                    tickformat="$.0f"
                )
            else:
                # For basic layout, the trend chart is in row 3
                fig.update_yaxes(title_text="Z-Score", row=3, col=1, secondary_y=False)
                fig.update_yaxes(
                    title_text="Price ($)",
                    row=3, col=1, secondary_y=True,
                    showgrid=False,
                    tickformat="$.0f"
                )
            
            # Configure x-axis font sizes to prevent label overlap
            fig.update_xaxes(tickfont=dict(size=10))  # Make all x-axis labels smaller
            
            # Make component breakdown x-axis labels even smaller due to long names
            if market_analysis:
                fig.update_xaxes(tickfont=dict(size=10), row=1, col=2)  # Component breakdown chart
            else:
                fig.update_xaxes(tickfont=dict(size=10), row=1, col=2)  # Component breakdown chart
            
            # Save to HTML
            fig.write_html(str(chart_path))
            
            logger.info(f"Z-Score dashboard generated: {chart_path}")
            return str(chart_path)            
        except Exception as e:
            import traceback
            logger.error(f"Chart generation error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            error_msg = f"Failed to generate dashboard for {latest.ticker if hasattr(latest, 'ticker') else 'unknown'}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def _add_zscore_gauge(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add Z-Score gauge indicator as a standalone figure."""

        # Create a simple bar chart representation instead of gauge for subplot compatibility
        risk_colors = {'Safe': 'green', 'Grey Zone': 'yellow', 'Distress': 'red'}
        color = risk_colors.get(zscore_result.risk_category, 'blue')
        
        fig.add_trace(
            go.Bar(
                x=['Z-Score'],
                y=[zscore_result.z_score],
                marker_color=color,
                name=f'Z-Score: {zscore_result.z_score:.2f}',
                text=[f'{zscore_result.z_score:.2f}<br>{zscore_result.risk_category}'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Add risk zone reference lines
        fig.add_hline(y=1.8, line_dash="dash", line_color="red", 
                     annotation_text="Distress Zone", row=row, col=col)
        fig.add_hline(y=2.99, line_dash="dash", line_color="orange", 
                     annotation_text="Safe Zone", row=row, col=col)
      
    def _add_component_breakdown(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add component breakdown bar chart."""

        # Filter to only numeric values to avoid formatting errors
        numeric_components = {}
        for key, value in zscore_result.component_values.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_components[key] = value
        
        components = list(numeric_components.keys())
        values = list(numeric_components.values())
        
        # Shorten component names for better display
        short_names = []
        for comp in components:
            if 'working_capital' in comp:
                short_names.append('Working<br>Capital')
            elif 'retained_earnings' in comp:
                short_names.append('Retained<br>Earnings')
            elif 'ebit' in comp:
                short_names.append('EBIT<br>Ratio')
            elif 'market_equity' in comp:
                short_names.append('Market<br>Equity')
            elif 'asset_turnover' in comp:
                short_names.append('Asset<br>Turnover')
            else:
                short_names.append(comp.replace('_', '<br>'))
        
        fig.add_trace(
            go.Bar(
                x=short_names,
                y=values,
                name="Z-Score Components",
                marker_color='lightblue',
                text=[f'{v:.2f}' if isinstance(v, (int, float)) else 'N/A' for v in values],
                textposition='auto'
            ),
            row=row, col=col
        )
    
    def _add_risk_zone_chart(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add risk zone scatter plot."""

        # Risk zones
        risk_zones = [
            {'name': 'Distress Zone', 'min': 0, 'max': 1.8, 'color': 'red'},
            {'name': 'Grey Zone', 'min': 1.8, 'max': 2.99, 'color': 'orange'},
            {'name': 'Safe Zone', 'min': 2.99, 'max': 10, 'color': 'green'}
        ]
        
        # Add risk zone backgrounds
        for zone in risk_zones:
            fig.add_shape(
                type="rect",
                x0=0, y0=zone['min'], x1=1, y1=zone['max'],
                fillcolor=zone['color'], opacity=0.2,
                row=row, col=col
            )
        
        # Add current Z-Score point
        fig.add_trace(
            go.Scatter(
                x=[0.5],
                y=[zscore_result.z_score],
                mode='markers',
                marker=dict(size=24, color=self._get_risk_color(zscore_result.z_score)),
                name=f"Current Z-Score ({zscore_result.z_score:.2f})"            ),
            row=row, col=col
        )
    
    def _add_data_quality_chart(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add data quality bar chart (replacing pie chart to avoid subplot conflicts)."""

        # Convert decimal to percentage (1.0 -> 100%)
        quality_score = zscore_result.data_quality_score * 100
        missing_score = 100 - quality_score
        
        fig.add_trace(
            go.Bar(
                x=['Data Available', 'Data Missing'],
                y=[quality_score, missing_score],
                marker_color=['green', 'red'],
                name='Data Quality',
                text=[f'{quality_score:.1f}%', f'{missing_score:.1f}%'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
    
    def _get_risk_color(self, z_score: float) -> str:
        """Get color based on Z-Score risk level."""
        if z_score < 1.8:
            return "red"
        elif z_score < 2.99:            
            return "orange"
        else:
            return "green"
    
    def _get_marker_colors(self, z_scores: list) -> list:
        """Get marker colors for multiple Z-Score values based on risk zones."""
        return [self._get_risk_color(score) for score in z_scores]
    
    def _add_investment_recommendation(self, fig, market_analysis, row: int, col: int):
        """Add investment recommendation indicator."""
        if not market_analysis.risk_return_profile:
            return
            
        rec = market_analysis.risk_return_profile
        action = rec.investment_rating.upper()
        
        # Safely handle confidence level - ensure it's numeric
        confidence = rec.confidence_level
        if not isinstance(confidence, (int, float)) or confidence is None:
            confidence = 0.5  # Default to 50%
            
        # Color mapping for actions
        color_map = {
            'STRONG_BUY': 'darkgreen',
            'BUY': 'green', 
            'HOLD': 'orange',
            'SELL': 'red',
            'STRONG_SELL': 'darkred'
        }
        
        # Use bar chart instead of gauge for subplot compatibility
        fig.add_trace(
            go.Bar(
                x=['Confidence'],
                y=[confidence * 100],
                marker_color=color_map.get(action, 'gray'),
                name=f'{action}: {confidence*100:.1f}',
                text=[f'{action}<br>{confidence*100:.1f}%'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Add confidence level reference lines
        fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                     annotation_text="Moderate Confidence", row=row, col=col)
        fig.add_hline(y=75, line_dash="dash", line_color="green", 
                     annotation_text="High Confidence", row=row, col=col)
      
    def _add_technical_indicators(self, fig, market_analysis, row: int, col: int):
        """Add technical indicators chart."""
        tech = market_analysis.technical_analysis
        
        indicators = ['RSI', 'MACD<br>Signal', 'BB<br>Signal', 'Momentum']
        
        # Safely extract momentum score
        momentum_value = 50  # Default
        if tech and hasattr(tech, 'momentum_score') and tech.momentum_score is not None:
            if isinstance(tech.momentum_score, (int, float)):
                momentum_value = tech.momentum_score * 100
        
        values = [
            tech.indicators.rsi if tech and tech.indicators and isinstance(tech.indicators.rsi, (int, float)) else 50,
            50 + (20 if tech and tech.overall_signal == 'buy' else -20 if tech and tech.overall_signal == 'sell' else 0),
            50,  # Simplified - no bollinger signal available
            momentum_value
        ]
        
        fig.add_trace(
            go.Bar(
                x=indicators,
                y=values,
                marker_color=['red' if v < 30 or v > 70 else 'orange' if v < 40 or v > 60 else 'green' for v in values],
                name='Technical Indicators',
                text=[f'{v:.1f}' if isinstance(v, (int, float)) else 'N/A' for v in values],
                textposition='auto'
            ),
            row=row, col=col
        )
    
    def _add_valuation_metrics(self, fig, market_analysis, row: int, col: int):
        """Add valuation metrics chart."""
        val = market_analysis.valuation_metrics
        
        metrics = ['P/E', 'P/B', 'P/S', 'EV/EBITDA']
        values = [
            val.pe_ratio if val.pe_ratio and isinstance(val.pe_ratio, (int, float)) and val.pe_ratio > 0 else 0,
            val.pb_ratio if val.pb_ratio and isinstance(val.pb_ratio, (int, float)) and val.pb_ratio > 0 else 0,
            val.ps_ratio if val.ps_ratio and isinstance(val.ps_ratio, (int, float)) and val.ps_ratio > 0 else 0,
            val.ev_ebitda if val.ev_ebitda and isinstance(val.ev_ebitda, (int, float)) and val.ev_ebitda > 0 else 0
        ]        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=values,
                marker_color='blue',
                name='Valuation Ratios',
                text=[f'{v:.1f}' if isinstance(v, (int, float)) and v > 0 else 'N/A' for v in values],
                textposition='auto'
            ),
            row=row, col=col
        )
      
    def _add_performance_metrics(self, fig, market_analysis, row: int, col: int):
        """Add performance metrics chart."""
        perf = market_analysis.market_performance
        
        metrics = ['1D', '1W', '1M', '3M', '6M', '1Y']
        returns = [
            perf.return_1d * 100 if perf.return_1d and isinstance(perf.return_1d, (int, float)) else 0,
            perf.return_1w * 100 if perf.return_1w and isinstance(perf.return_1w, (int, float)) else 0,
            perf.return_1m * 100 if perf.return_1m and isinstance(perf.return_1m, (int, float)) else 0,
            perf.return_3m * 100 if perf.return_3m and isinstance(perf.return_3m, (int, float)) else 0,
            perf.return_6m * 100 if perf.return_6m and isinstance(perf.return_6m, (int, float)) else 0,
            perf.return_1y * 100 if perf.return_1y and isinstance(perf.return_1y, (int, float)) else 0
        ]
        
        colors = ['green' if r > 0 else 'red' for r in returns]
        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=returns,
                marker_color=colors,
                name='Returns (%)',
                text=[f'{r:.1f}%' if isinstance(r, (int, float)) else 'N/A' for r in returns],
                textposition='auto'
            ),
            row=row, col=col
        )
    
    def _add_risk_return_analysis(self, fig, market_analysis, row: int, col: int):
        """Add risk-return scatter plot."""
        risk = market_analysis.risk_return_profile
        perf = market_analysis.market_performance
        
        # Extract actual data - check for None specifically, not falsy values
        volatility_risk = risk.volatility_risk if risk and risk.volatility_risk is not None else None
        
        # Use the longest available return period (preferring 1Y, falling back to shorter periods)
        return_value = None
        return_period = ""
        
        if perf:
            if perf.return_1y is not None:
                return_value = perf.return_1y
                return_period = "1Y"
            elif perf.return_6m is not None:
                return_value = perf.return_6m
                return_period = "6M"
            elif perf.return_3m is not None:
                return_value = perf.return_3m
                return_period = "3M"
            elif perf.return_1m is not None:
                return_value = perf.return_1m
                return_period = "1M"
            elif perf.return_1w is not None:
                return_value = perf.return_1w
                return_period = "1W"
            elif perf.return_1d is not None:
                return_value = perf.return_1d
                return_period = "1D"
        
        # Debug logging to understand data availability
        logger.info(f"Risk-Return Analysis - Volatility: {volatility_risk}, Return {return_period}: {return_value}")
        logger.info(f"Risk object exists: {risk is not None}, Perf object exists: {perf is not None}")
        
        # Additional debugging for performance object
        if perf:
            logger.info(f"Performance data available: return_1d={perf.return_1d}, return_1w={perf.return_1w}, return_1m={perf.return_1m}, return_3m={perf.return_3m}, return_6m={perf.return_6m}, return_1y={perf.return_1y}")
        else:
            logger.info("Performance object is None")
        
        if volatility_risk is not None and return_value is not None:
            # Use actual data
            x_risk = volatility_risk * 100  # Convert 0-1 scale to 0-100%
            y_return = return_value * 100      # Convert decimal to percentage
            
            # Color based on risk-return profile
            if y_return > 10 and x_risk < 25:
                color = 'green'  # High return, low risk
            elif y_return > 0 and x_risk < 30:
                color = 'blue'   # Positive return, moderate risk
            elif y_return < -10:
                color = 'red'    # Negative return
            else:
                color = 'orange' # Neutral
                
            marker_text = f'Risk: {x_risk:.1f}%<br>Return ({return_period}): {y_return:.1f}%'
            logger.info(f"Using actual data: Risk={x_risk:.1f}%, Return ({return_period})={y_return:.1f}%")
        else:
            # If data is missing, show "No Data" placeholder  
            x_risk = 50
            y_return = 0
            color = 'gray'
            marker_text = 'Insufficient Data<br>for Risk-Return Analysis'
            logger.info(f"Using fallback data due to missing values")
        
        fig.add_trace(
            go.Scatter(
                x=[x_risk],
                y=[y_return],
                mode='markers',
                marker=dict(
                    size=15,
                    color=color,
                    symbol='diamond'
                ),
                name='Risk-Return Position',
                text=[marker_text],
                textposition='top center'
            ),
            row=row, col=col
        )
        
        # Add benchmark quadrants with labels
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=col)
        fig.add_vline(x=25, line_dash="dash", line_color="gray", row=row, col=col)
        
        # Add quadrant labels
        fig.add_annotation(
            x=10, y=15, text="Low Risk<br>High Return", 
            showarrow=False, font=dict(size=10, color="green"),
            row=row, col=col
        )
        fig.add_annotation(
            x=40, y=-15, text="High Risk<br>Low Return", 
            showarrow=False, font=dict(size=10, color="red"),
            row=row, col=col
        )
    
    def _add_enhanced_trend_chart(self, fig, results, market_analysis, start_date, row: int, col: int):
        """Add enhanced trend chart with market data."""
        try:
            # Build Z-Score time series
            dates = [datetime.fromisoformat(r.calculation_timestamp) for r in results]
            scores = [r.z_score for r in results]
            latest = results[0]
            
            # Filter by start_date if provided
            if start_date:
                sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                filtered = [(d, s) for d, s in zip(dates, scores) if d.date() >= sd]
                if filtered:
                    dates, scores = zip(*filtered)
            
            # Try to get price data from market analysis first, then fallback to direct fetch
            price_dates = []
            prices = []
            history = None
            
            # Fetch ALL available historical prices - always use "max" period to get full history
            try:
                from ...layers.data_fetch.yahoo_fetcher import YahooDataFetcher
                yf_fetcher = YahooDataFetcher()
                
                logger.info(f"Fetching all available price data for {latest.ticker} using 'max' period")
                
                # Always fetch maximum available data first
                history = yf_fetcher.get_historical_prices(latest.ticker, period="max")
                
                if history is None or not hasattr(history, 'empty') or history.empty:
                    # If "max" fails, try other long periods
                    logger.warning(f"'max' period failed for {latest.ticker}, trying fallback periods")
                    for period in ["10y", "5y", "2y", "1y"]:
                        try:
                            history = yf_fetcher.get_historical_prices(latest.ticker, period=period)
                            if history is not None and hasattr(history, 'empty') and not history.empty:
                                logger.info(f"Successfully fetched {period} price data: {len(history)} records for {latest.ticker}")
                                break
                        except Exception as period_error:
                            logger.warning(f"Failed to fetch {period} price data for {latest.ticker}: {str(period_error)}")
                            continue
                else:
                    logger.info(f"Successfully fetched max price data: {len(history)} records for {latest.ticker}")
                        
            except Exception as e:
                logger.error(f"Error fetching price data: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Process price data and filter to required date range
            if history is not None and hasattr(history, 'reset_index'):
                hist = history.reset_index()
                logger.info(f"Retrieved {len(hist)} price records for {latest.ticker}")
                logger.info(f"Full date range: {hist['Date'].min()} to {hist['Date'].max()}")
                
                # For multi-quarter analysis, filter price data to show from 30 days before first quarter to today
                if len(results) > 1 and dates:
                    # Get the Z-Score date range
                    earliest_zscore_date = min(dates).replace(tzinfo=None)
                    
                    # Add buffer: 30 days before earliest quarter, extend to today
                    import pandas as pd
                    buffer_start_date = earliest_zscore_date - pd.Timedelta(days=30)
                    buffer_end_date = pd.Timestamp.now().tz_localize(None)  # Today
                    
                    logger.info(f"Filtering price data from {buffer_start_date.strftime('%Y-%m-%d')} to {buffer_end_date.strftime('%Y-%m-%d')}")
                    
                    # Remove timezone info from price data for comparison
                    hist_dates = hist['Date'].dt.tz_localize(None) if hist['Date'].dt.tz is not None else hist['Date']
                    
                    # Filter price data to required date range
                    before_filter = len(hist)
                    hist = hist[(hist_dates >= buffer_start_date) & (hist_dates <= buffer_end_date)]
                    after_filter = len(hist)
                    
                    logger.info(f"Filtered price data from {before_filter} to {after_filter} records")
                elif start_date and 'Date' in hist.columns:
                    # Apply start_date filter if provided
                    sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                    before_filter = len(hist)
                    hist = hist[hist['Date'].dt.date >= sd]
                    logger.info(f"Filtered by start_date {start_date}: {before_filter} -> {len(hist)} records")
                elif len(results) == 1:
                    # For single Z-Score point, show recent price history (last year)
                    import pandas as pd
                    recent_date = pd.Timestamp.now().tz_localize(None) - pd.Timedelta(days=365)
                    hist_dates = hist['Date'].dt.tz_localize(None) if hist['Date'].dt.tz is not None else hist['Date']
                    before_filter = len(hist)
                    hist = hist[hist_dates >= recent_date]
                    logger.info(f"Filtered to last 365 days: {before_filter} -> {len(hist)} records")
                
                # Extract price dates and values
                if not hist.empty:
                    price_dates = hist['Date'].tolist()
                    prices = hist['Close'].tolist()
                    logger.info(f"Final price data: {len(price_dates)} dates from {min(price_dates)} to {max(price_dates)}, price range ${min(prices):.2f} - ${max(prices):.2f}")
                else:
                    logger.warning(f"No price data after filtering for {latest.ticker}")
            else:
                logger.warning(f"No price data available for {latest.ticker}")
            
            logger.info(f"Z-Score data: {len(dates)} points, scores: {scores}")
            logger.info(f"Price data: {len(price_dates)} points, will normalize to 0-10 scale")
            
            # Add Z-Score trace with risk-zone colored markers
            marker_colors = self._get_marker_colors(scores)
            fig.add_trace(
                go.Scatter(
                    x=dates, y=scores, 
                    mode='lines+markers', 
                    name='Z-Score',
                    line=dict(color='blue', width=3),
                    marker=dict(size=10, color=marker_colors)
                ), 
                row=row, col=col
            )
            
            # Add price trace - normalize to Z-Score scale for better visualization
            if price_dates and prices:
                logger.info(f"Adding price trace with {len(price_dates)} data points")
                # Scale prices to be visible alongside Z-Score (normalize to 0-10 range)
                min_price, max_price = min(prices), max(prices)
                logger.info(f"Price range: ${min_price:.2f} - ${max_price:.2f}")
                
                if max_price > min_price:
                    # Scale prices to Z-Score range for better visualization but keep original for hover
                    z_min, z_max = min(scores), max(scores)
                    z_range = max(z_max - z_min, 10)  # Ensure minimum range
                    
                    # Scale prices to fit within Z-Score range
                    price_range = max_price - min_price
                    scaled_prices = []
                    for p in prices:
                        # Scale price to Z-Score range
                        normalized = (p - min_price) / price_range  # 0-1
                        scaled = z_min + (normalized * z_range)  # Scale to Z-Score range
                        scaled_prices.append(scaled)
                    
                    logger.info(f"Scaled price range: {min(scaled_prices):.2f} - {max(scaled_prices):.2f} (Z-range: {z_min:.2f} - {z_max:.2f})")
                    
                    fig.add_trace(
                        go.Scatter(
                            x=price_dates, y=prices,  # Use actual prices instead of scaled
                            mode='lines',
                            name=f'Price (${min_price:.0f} - ${max_price:.0f})',
                            line=dict(color='green', width=2, dash='dot'),
                            opacity=0.8
                        ),
                        row=row, col=col, secondary_y=True  # Use secondary y-axis parameter
                    )
                    
                    # Remove the annotation since we'll have a proper price axis
                    logger.info(f"Price trace added successfully with secondary y-axis")
                else:
                    logger.warning(f"Price data has no variance for {latest.ticker}")
            else:
                logger.warning(f"No price data available for trend chart - price_dates: {len(price_dates) if price_dates else 0}, prices: {len(prices) if prices else 0}")
            
            # Add Z-Score risk zones
            fig.add_hline(y=1.8, line_dash="dash", line_color="red", 
                         annotation_text="Distress Zone", row=row, col=col)
            fig.add_hline(y=2.99, line_dash="dash", line_color="orange", 
                         annotation_text="Gray Zone", row=row, col=col)
                         
        except Exception as e:
            logger.warning(f"Could not generate enhanced trend chart: {str(e)}")
            import traceback
            logger.warning(f"Traceback: {traceback.format_exc()}")
    
    def _add_basic_trend_chart(self, fig, results, latest, start_date, row: int, col: int):
        """Add basic trend chart for Z-Score only mode."""

        try:
            # Build Z-Score time series
            dates = [datetime.fromisoformat(r.calculation_timestamp) for r in results]
            scores = [r.z_score for r in results]
            
            # Filter by start_date if provided
            if start_date:
                sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                filtered = [(d, s) for d, s in zip(dates, scores) if d.date() >= sd]
                if filtered:
                    dates, scores = zip(*filtered)
            
            # Fetch ALL available historical prices - always use "max" period to get full history
            from ...layers.data_fetch.yahoo_fetcher import YahooDataFetcher
            yf_fetcher = YahooDataFetcher()
            
            logger.info(f"Basic chart: Fetching all available price data for {latest.ticker} using 'max' period")
            
            try:
                # Always fetch maximum available data first
                history = yf_fetcher.get_historical_prices(latest.ticker, period="max")
                
                if history is None or not hasattr(history, 'empty') or history.empty:
                    # If "max" fails, try other long periods
                    logger.warning(f"Basic chart: 'max' period failed for {latest.ticker}, trying fallback periods")
                    for period in ["10y", "5y", "2y", "1y"]:
                        try:
                            history = yf_fetcher.get_historical_prices(latest.ticker, period=period)
                            if history is not None and hasattr(history, 'empty') and not history.empty:
                                logger.info(f"Basic chart: Successfully fetched {period} price data: {len(history)} records for {latest.ticker}")
                                break
                        except Exception as period_error:
                            logger.warning(f"Basic chart: Failed to fetch {period} price data for {latest.ticker}: {str(period_error)}")
                            continue
                else:
                    logger.info(f"Basic chart: Successfully fetched max price data: {len(history)} records for {latest.ticker}")
                        
            except Exception as e:
                logger.error(f"Basic chart: Error fetching price data: {str(e)}")
                import traceback
                logger.error(f"Basic chart: Traceback: {traceback.format_exc()}")
            
            # Process price data and filter to required date range
            price_dates = []
            prices = []
            if history is not None and hasattr(history, 'reset_index'):
                hist = history.reset_index()
                logger.info(f"Basic chart: Retrieved {len(hist)} price records for {latest.ticker}")
                logger.info(f"Basic chart: Full date range: {hist['Date'].min()} to {hist['Date'].max()}")
                
                # For multi-quarter analysis, filter price data to show from 30 days before first quarter to today
                if len(results) > 1 and dates:
                    # Get the Z-Score date range
                    earliest_zscore_date = min(dates).replace(tzinfo=None)
                    
                    # Add buffer: 30 days before earliest quarter, extend to today
                    import pandas as pd
                    buffer_start_date = earliest_zscore_date - pd.Timedelta(days=30)
                    buffer_end_date = pd.Timestamp.now().tz_localize(None)  # Today
                    
                    logger.info(f"Basic chart: Filtering price data from {buffer_start_date.strftime('%Y-%m-%d')} to {buffer_end_date.strftime('%Y-%m-%d')}")
                    
                    # Remove timezone info from price data for comparison
                    hist_dates = hist['Date'].dt.tz_localize(None) if hist['Date'].dt.tz is not None else hist['Date']
                    
                    # Filter price data to required date range
                    before_filter = len(hist)
                    hist = hist[(hist_dates >= buffer_start_date) & (hist_dates <= buffer_end_date)]
                    after_filter = len(hist)
                    
                    logger.info(f"Basic chart: Filtered price data from {before_filter} to {after_filter} records")
                
                # Extract price dates and values
                if not hist.empty:
                    price_dates = hist['Date'].tolist()
                    prices = hist['Close'].tolist()
                    logger.info(f"Basic chart: Using {len(price_dates)} price points from {min(price_dates)} to {max(price_dates)}")
                else:
                    logger.warning(f"Basic chart: No price data after filtering for {latest.ticker}")
            else:
                logger.warning(f"Basic chart: No price data available for {latest.ticker}")
            
            # Add Z-Score trace with risk-zone colored markers
            marker_colors = self._get_marker_colors(scores)
            fig.add_trace(
                go.Scatter(
                    x=dates, y=scores, 
                    mode='lines+markers', 
                    name='Z-Score',
                    line=dict(color='blue', width=3),
                    marker=dict(size=10, color=marker_colors)
                ), 
                row=row, col=col
            )
            
            # Add price trace - scale to Z-Score range for better visualization
            if price_dates and prices:
                # Scale prices to be visible alongside Z-Score but keep original for hover
                min_price, max_price = min(prices), max(prices)
                if max_price > min_price:
                    # Scale prices to Z-Score range for better visualization
                    z_min, z_max = min(scores), max(scores)
                    z_range = max(z_max - z_min, 10)  # Ensure minimum range
                    
                    # Scale prices to fit within Z-Score range
                    price_range = max_price - min_price
                    scaled_prices = []
                    for p in prices:
                        normalized = (p - min_price) / price_range  # 0-1
                        scaled = z_min + (normalized * z_range)  # Scale to Z-Score range
                        scaled_prices.append(scaled)
                    
                    fig.add_trace(
                        go.Scatter(
                            x=price_dates, y=prices,  # Use actual prices instead of scaled
                            mode='lines',
                            name=f'Price (${min_price:.0f} - ${max_price:.0f})',
                            line=dict(color='green', width=2, dash='dot'),
                            opacity=0.8
                        ),
                        row=row, col=col, secondary_y=True  # Use secondary y-axis parameter
                    )
                    
                    logger.info(f"Price trace added successfully with secondary y-axis")
                else:
                    logger.warning(f"Price data has no variance for {latest.ticker}")
            
            # Add Z-Score risk zones
            fig.add_hline(y=1.8, line_dash="dash", line_color="red", 
                         annotation_text="Distress Zone", row=row, col=col)
            fig.add_hline(y=2.99, line_dash="dash", line_color="orange", 
                         annotation_text="Gray Zone", row=row, col=col)
                         
        except Exception as e:
            logger.warning(f"Could not generate basic trend chart: {str(e)}")
