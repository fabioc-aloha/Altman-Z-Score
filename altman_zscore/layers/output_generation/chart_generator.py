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
    
    def generate_zscore_dashboard(self, zscore_results, start_date: Optional[str] = None) -> str:
        """
        Generate comprehensive Z-Score dashboard chart using multiple periods for trend.
        
        Args:
            zscore_results: Z-Score calculation result or list of results
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
            
            # Create subplot figure with additional trend chart row
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    'Z-Score Overview',
                    'Component Breakdown',
                    'Risk Zone Analysis',
                    'Data Quality Metrics',
                    'Z-Score & Price Trend',
                    ''
                ),
                specs=[
                    [{"type": "indicator"}, {"type": "bar"}],
                    [{"type": "scatter"}, {"type": "pie"}],
                    [{"type": "xy", "colspan": 2}, None]
                ],
                row_heights=[0.3, 0.3, 0.4],
                vertical_spacing=0.05
            )
            
            # Add Z-Score gauge
            self._add_zscore_gauge(fig, latest, row=1, col=1)
            
            # Add component breakdown
            self._add_component_breakdown(fig, latest, row=1, col=2)
            
            # Add risk zone analysis
            self._add_risk_zone_chart(fig, latest, row=2, col=1)
            
            # Add data quality pie chart
            self._add_data_quality_chart(fig, latest, row=2, col=2)
            
            # Add Z-Score vs Price trend chart
            try:
                # Build Z-Score time series from result list if available
                # zscore_result may be a list for multiple periods
                dates = [datetime.fromisoformat(r.calculation_timestamp) for r in results]
                scores = [r.z_score for r in results]
                # Filter series by CLI start_date
                if start_date:
                    sd = datetime.strptime(start_date, "%Y-%m-%d").date()
                    filtered = [(d, s) for d, s in zip(dates, scores) if d.date() >= sd]
                    if filtered:
                        dates, scores = zip(*filtered)
                # Fetch historical prices
                from ...layers.data_fetch.yahoo_fetcher import YahooDataFetcher
                yf_fetcher = YahooDataFetcher()
                history = yf_fetcher.get_historical_prices(latest.ticker, period="max")
                price_dates = []
                prices = []
                if history is not None and hasattr(history, 'reset_index'):
                    hist = history.reset_index()
                    # Filter by start_date if provided
                    if start_date and 'Date' in hist.columns:
                        hist = hist[hist['Date'].dt.date >= sd]
                    # Use Close prices
                    price_dates = hist['Date'].tolist()
                    prices = hist['Close'].tolist()
                # Add traces
                fig.add_trace(
                    go.Scatter(
                        x=dates, y=scores, mode='lines+markers', name='Z-Score', yaxis='y3'
                    ), row=3, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=price_dates, y=prices, mode='lines', name='Price', yaxis='y4'
                    ), row=3, col=1
                )
                # Configure axes for trend
                fig.update_layout(
                    yaxis3=dict(title='Z-Score'),
                    yaxis4=dict(title='Price', overlaying='y3', side='right')
                )
            except Exception:
                logger.warning(f"Could not generate price trend for {latest.ticker}")
             
            # Update layout
            fig.update_layout(
                title=f"Altman Z-Score Analysis Dashboard - {latest.ticker}",
                height=900,
                showlegend=True
            )
            
            # Save to HTML
            fig.write_html(str(chart_path))
            
            logger.info(f"Z-Score dashboard generated: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            error_msg = f"Failed to generate dashboard for {zscore_results.ticker}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def _add_zscore_gauge(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add Z-Score gauge indicator."""
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=zscore_result.z_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Z-Score"},
                delta={'reference': 2.99},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': self._get_risk_color(zscore_result.z_score)},
                    'steps': [
                        {'range': [0, 1.8], 'color': "red"},
                        {'range': [1.8, 2.99], 'color': "yellow"},
                        {'range': [2.99, 10], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 2.99
                    }
                }
            ),
            row=row, col=col
        )
    
    def _add_component_breakdown(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add component breakdown bar chart."""
        components = list(zscore_result.component_values.keys())
        values = list(zscore_result.component_values.values())
        
        fig.add_trace(
            go.Bar(
                x=components,
                y=values,
                name="Z-Score Components",
                marker_color='lightblue'
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
                marker=dict(size=15, color=self._get_risk_color(zscore_result.z_score)),
                name=f"Current Z-Score ({zscore_result.z_score:.2f})"
            ),
            row=row, col=col
        )
    
    def _add_data_quality_chart(self, fig, zscore_result: ZScoreCalculationResult, row: int, col: int):
        """Add data quality pie chart."""
        quality_score = zscore_result.data_quality_score
        missing_score = 100 - quality_score
        
        fig.add_trace(
            go.Pie(
                labels=['Data Available', 'Data Missing'],
                values=[quality_score, missing_score],
                marker_colors=['green', 'red']
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
