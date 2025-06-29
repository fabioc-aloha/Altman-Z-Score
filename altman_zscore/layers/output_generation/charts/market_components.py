"""
Market Analysis Chart Components

Chart components for market analysis including investment recommendations,
technical indicators, and valuation metrics.
"""

import plotly.graph_objects as go
from typing import Any

from .base import ChartBase


class InvestmentRecommendation(ChartBase):
    """Chart component for investment recommendation display."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, market_analysis: Any, **kwargs) -> None:
        """Add investment recommendation chart to figure."""
        if not market_analysis or not hasattr(market_analysis, 'risk_return_profile') or not market_analysis.risk_return_profile:
            fig.add_trace(self.create_no_data_bar("Investment Rec"), row=row, col=col)
            return
            
        rec = market_analysis.risk_return_profile
        action = rec.investment_rating.upper()
        
        # Safely handle confidence level - ensure it's numeric
        confidence = self.safe_get_numeric(rec, 'confidence_level', 0.5)
            
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


class TechnicalIndicators(ChartBase):
    """Chart component for technical indicators display."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, market_analysis: Any, **kwargs) -> None:
        """Add technical indicators chart to figure."""
        if not market_analysis or not hasattr(market_analysis, 'technical_analysis'):
            fig.add_trace(self.create_no_data_bar("Technical Indicators"), row=row, col=col)
            return
            
        tech = market_analysis.technical_analysis
        
        indicators = ['RSI', 'MACD<br>Signal', 'BB<br>Signal', 'Momentum']
        
        # Safely extract momentum score
        momentum_value = 50  # Default
        if tech and hasattr(tech, 'momentum_score'):
            momentum_value = self.safe_get_numeric(tech, 'momentum_score', 0.5) * 100
        
        values = [
            self._get_rsi_value(tech),
            self._get_macd_signal_value(tech),
            50,  # Simplified - no bollinger signal available
            momentum_value
        ]
        
        colors = [self._get_indicator_color(v) for v in values]
        
        fig.add_trace(
            go.Bar(
                x=indicators,
                y=values,
                marker_color=colors,
                name='Technical Indicators',
                text=[self.format_value(v) for v in values],
                textposition='auto'
            ),
            row=row, col=col
        )
    
    def _get_rsi_value(self, tech: Any) -> float:
        """Get RSI value safely."""
        if tech and hasattr(tech, 'indicators') and tech.indicators:
            return self.safe_get_numeric(tech.indicators, 'rsi', 50)
        return 50
    
    def _get_macd_signal_value(self, tech: Any) -> float:
        """Get MACD signal value safely."""
        if tech and hasattr(tech, 'overall_signal'):
            if tech.overall_signal == 'buy':
                return 70
            elif tech.overall_signal == 'sell':
                return 30
        return 50
    
    def _get_indicator_color(self, value: float) -> str:
        """Get color based on indicator value."""
        if value < 30 or value > 70:
            return 'red'
        elif value < 40 or value > 60:
            return 'orange'
        else:
            return 'green'


class ValuationMetrics(ChartBase):
    """Chart component for valuation metrics display."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, market_analysis: Any, **kwargs) -> None:
        """Add valuation metrics chart to figure."""
        if not market_analysis or not hasattr(market_analysis, 'valuation_metrics'):
            fig.add_trace(self.create_no_data_bar("Valuation Metrics"), row=row, col=col)
            return
            
        val = market_analysis.valuation_metrics
        
        metrics = ['P/E', 'P/B', 'P/S', 'EV/EBITDA']
        values = [
            self._get_positive_ratio(val, 'pe_ratio'),
            self._get_positive_ratio(val, 'pb_ratio'),
            self._get_positive_ratio(val, 'ps_ratio'),
            self._get_positive_ratio(val, 'ev_ebitda')
        ]
        
        fig.add_trace(
            go.Bar(
                x=metrics,
                y=values,
                marker_color='blue',
                name='Valuation Ratios',
                text=[self.format_value(v) if v > 0 else 'N/A' for v in values],
                textposition='auto'
            ),
            row=row, col=col
        )
    
    def _get_positive_ratio(self, val_obj: Any, attr: str) -> float:
        """Get a valuation ratio, ensuring it's positive."""
        value = self.safe_get_numeric(val_obj, attr, 0)
        return value if value > 0 else 0
