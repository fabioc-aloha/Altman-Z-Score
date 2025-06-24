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
            output_base_path: Base directory for output files        """
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
                fig = make_subplots(
                    rows=4, cols=3,
                    subplot_titles=(
                        'Z-Score Overview',
                        'Component Breakdown', 
                        'Investment Recommendation',
                        'Risk Zone Analysis',
                        'Data Quality Metrics',
                        'Technical Indicators',
                        'Valuation Metrics',
                        'Performance Metrics',
                        'Risk-Return Analysis',
                        'Z-Score & Price Trend',
                        '',
                        ''
                    ),
                    specs=[
                        [{"type": "indicator"}, {"type": "bar"}, {"type": "indicator"}],
                        [{"type": "scatter"}, {"type": "pie"}, {"type": "bar"}],
                        [{"type": "bar"}, {"type": "bar"}, {"type": "scatter"}],
                        [{"type": "xy", "colspan": 3}, None, None]
                    ],
                    row_heights=[0.25, 0.25, 0.25, 0.25],
                    vertical_spacing=0.04
                )
            else:
                # Original layout for Z-Score only
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
            
            # Add enhanced market analysis components if available
            if market_analysis:
                # Add investment recommendation indicator
                self._add_investment_recommendation(fig, market_analysis, row=1, col=3)
                
                # Add risk zone analysis
                self._add_risk_zone_chart(fig, latest, row=2, col=1)
                
                # Add data quality pie chart
                self._add_data_quality_chart(fig, latest, row=2, col=2)
                
                # Add technical indicators
                self._add_technical_indicators(fig, market_analysis, row=2, col=3)
                
                # Add valuation metrics
                self._add_valuation_metrics(fig, market_analysis, row=3, col=1)
                
                # Add performance metrics
                self._add_performance_metrics(fig, market_analysis, row=3, col=2)
                
                # Add risk-return analysis
                self._add_risk_return_analysis(fig, market_analysis, row=3, col=3)
                
                # Add enhanced trend chart
                self._add_enhanced_trend_chart(fig, results, market_analysis, start_date, row=4, col=1)
            else:
                # Original layout for Z-Score only
                self._add_risk_zone_chart(fig, latest, row=2, col=1)
                self._add_data_quality_chart(fig, latest, row=2, col=2)
                self._add_basic_trend_chart(fig, results, latest, start_date, row=3, col=1)            # Update layout with enhanced features
            title_suffix = " (Enhanced with Market Analysis)" if market_analysis else ""
            height = 1200 if market_analysis else 900
            
            fig.update_layout(
                title=f"Altman Z-Score Analysis Dashboard - {latest.ticker}{title_suffix}",
                height=height,
                showlegend=True
            )
            
            # Save to HTML
            fig.write_html(str(chart_path))
            
            logger.info(f"Z-Score dashboard generated: {chart_path}")
            return str(chart_path)
            
        except Exception as e:
            error_msg = f"Failed to generate dashboard for {latest.ticker if hasattr(latest, 'ticker') else 'unknown'}: {str(e)}"
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
    
    def _add_investment_recommendation(self, fig, market_analysis, row: int, col: int):
        """Add investment recommendation indicator."""
        rec = market_analysis.investment_recommendation
        action = rec.action
        confidence = rec.confidence
        
        # Color mapping for actions
        color_map = {
            'STRONG_BUY': 'darkgreen',
            'BUY': 'green', 
            'HOLD': 'orange',
            'SELL': 'red',
            'STRONG_SELL': 'darkred'
        }
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=confidence * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Recommendation: {action}"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color_map.get(action, 'gray')},
                    'steps': [
                        {'range': [0, 20], 'color': "lightgray"},
                        {'range': [20, 40], 'color': "yellow"},
                        {'range': [40, 70], 'color': "orange"},
                        {'range': [70, 100], 'color': "green"}
                    ]
                }
            ),
            row=row, col=col
        )
    
    def _add_technical_indicators(self, fig, market_analysis, row: int, col: int):
        """Add technical indicators chart."""
        tech = market_analysis.technical_analysis
        
        indicators = ['RSI', 'MACD Signal', 'BB Signal', 'Momentum']
        values = [
            tech.rsi_14 if tech.rsi_14 else 50,
            50 + (20 if tech.macd_signal == 'bullish' else -20 if tech.macd_signal == 'bearish' else 0),
            50 + (15 if tech.bollinger_signal == 'oversold' else -15 if tech.bollinger_signal == 'overbought' else 0),
            tech.momentum_score * 100 if tech.momentum_score else 50
        ]
        
        fig.add_trace(
            go.Bar(
                x=indicators,
                y=values,
                marker_color=['red' if v < 30 or v > 70 else 'orange' if v < 40 or v > 60 else 'green' for v in values],
                name='Technical Indicators'
            ),
            row=row, col=col
        )
    
    def _add_valuation_metrics(self, fig, market_analysis, row: int, col: int):
        """Add valuation metrics chart."""
        val = market_analysis.valuation_analysis
        
        metrics = ['P/E', 'P/B', 'P/S', 'EV/EBITDA']
        values = [
            val.pe_ratio if val.pe_ratio and val.pe_ratio > 0 else 0,
            val.pb_ratio if val.pb_ratio and val.pb_ratio > 0 else 0,
            val.ps_ratio if val.ps_ratio and val.ps_ratio > 0 else 0,
            val.ev_ebitda if val.ev_ebitda and val.ev_ebitda > 0 else 0
        ]
        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=values,
                marker_color='blue',
                name='Valuation Ratios'
            ),
            row=row, col=col
        )
    
    def _add_performance_metrics(self, fig, market_analysis, row: int, col: int):
        """Add performance metrics chart."""
        perf = market_analysis.performance_analysis
        
        metrics = ['1D', '5D', '1M', '3M', '6M', '1Y']
        returns = [
            perf.return_1d * 100 if perf.return_1d else 0,
            perf.return_5d * 100 if perf.return_5d else 0,
            perf.return_1m * 100 if perf.return_1m else 0,
            perf.return_3m * 100 if perf.return_3m else 0,
            perf.return_6m * 100 if perf.return_6m else 0,
            perf.return_1y * 100 if perf.return_1y else 0
        ]
        
        colors = ['green' if r > 0 else 'red' for r in returns]
        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=returns,
                marker_color=colors,
                name='Returns (%)'
            ),
            row=row, col=col
        )
    
    def _add_risk_return_analysis(self, fig, market_analysis, row: int, col: int):
        """Add risk-return scatter plot."""
        risk = market_analysis.risk_analysis
        perf = market_analysis.performance_analysis
        
        # Use volatility as risk and 1Y return as return
        x_risk = risk.volatility_1y * 100 if risk.volatility_1y else 20
        y_return = perf.return_1y * 100 if perf.return_1y else 0
        
        fig.add_trace(
            go.Scatter(
                x=[x_risk],
                y=[y_return],
                mode='markers',
                marker=dict(
                    size=15,
                    color='blue',
                    symbol='diamond'
                ),
                name='Risk-Return Position'
            ),
            row=row, col=col
        )
        
        # Add benchmark quadrants
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=row, col=col)
        fig.add_vline(x=20, line_dash="dash", line_color="gray", row=row, col=col)
    
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
            
            # Fetch historical prices
            from ...layers.data_fetch.yahoo_fetcher import YahooDataFetcher
            yf_fetcher = YahooDataFetcher()
            history = yf_fetcher.get_historical_prices(latest.ticker, period="max")
            
            price_dates = []
            prices = []
            if history is not None and hasattr(history, 'reset_index'):
                hist = history.reset_index()
                if start_date and 'Date' in hist.columns:
                    hist = hist[hist['Date'].dt.date >= sd]
                price_dates = hist['Date'].tolist()
                prices = hist['Close'].tolist()
            
            # Add Z-Score trace
            fig.add_trace(
                go.Scatter(
                    x=dates, y=scores, 
                    mode='lines+markers', 
                    name='Z-Score',
                    line=dict(color='blue', width=2)
                ), 
                row=row, col=col
            )
            
            # Add price trace on secondary y-axis
            if price_dates and prices:
                fig.add_trace(
                    go.Scatter(
                        x=price_dates, y=prices,
                        mode='lines',
                        name='Price',
                        yaxis='y2',
                        line=dict(color='green', width=1)
                    ),
                    row=row, col=col
                )
            
            # Add Z-Score risk zones
            fig.add_hline(y=1.8, line_dash="dash", line_color="red", 
                         annotation_text="Distress Zone", row=row, col=col)
            fig.add_hline(y=2.99, line_dash="dash", line_color="orange", 
                         annotation_text="Gray Zone", row=row, col=col)
                         
        except Exception as e:
            logger.warning(f"Could not generate enhanced trend chart: {str(e)}")
    
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
            
            # Fetch historical prices
            from ...layers.data_fetch.yahoo_fetcher import YahooDataFetcher
            yf_fetcher = YahooDataFetcher()
            history = yf_fetcher.get_historical_prices(latest.ticker, period="max")
            
            price_dates = []
            prices = []
            if history is not None and hasattr(history, 'reset_index'):
                hist = history.reset_index()
                if start_date and 'Date' in hist.columns:
                    hist = hist[hist['Date'].dt.date >= sd]
                price_dates = hist['Date'].tolist()
                prices = hist['Close'].tolist()
            
            # Add traces
            fig.add_trace(
                go.Scatter(
                    x=dates, y=scores, mode='lines+markers', name='Z-Score', yaxis='y3'
                ), row=row, col=col
            )
            
            if price_dates and prices:
                fig.add_trace(
                    go.Scatter(
                        x=price_dates, y=prices, mode='lines', name='Price', yaxis='y4'
                    ), row=row, col=col
                )
            
            # Configure axes for trend
            fig.update_layout(
                yaxis3=dict(title='Z-Score'),
                yaxis4=dict(title='Price', overlaying='y3', side='right')
            )
            
        except Exception as e:
            logger.warning(f"Could not generate basic trend chart: {str(e)}")
