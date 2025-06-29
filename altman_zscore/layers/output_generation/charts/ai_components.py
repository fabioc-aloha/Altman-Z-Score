"""
AI Analysis Chart Components

Chart components for AI-enhanced analysis including data quality, peer analysis,
sentiment analysis, risk assessment, and confidence metrics.
"""

import plotly.graph_objects as go
from typing import Any

from .base import ChartBase


class AIDataQuality(ChartBase):
    """Chart component for AI data quality metrics."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, comprehensive_ai_analysis: Any, **kwargs) -> None:
        """Add AI data quality chart to figure."""
        if not comprehensive_ai_analysis or not hasattr(comprehensive_ai_analysis, 'data_quality'):
            self.add_no_data_annotation(fig, "No AI Data Quality Analysis", row, col)
            return

        dq = comprehensive_ai_analysis.data_quality
        quality_score = self.safe_get_numeric(dq, 'overall_quality_score', 0)
        reliability = getattr(dq, 'reliability_rating', 'unknown')
        anomalies = len(getattr(dq, 'anomalies_detected', []))
        
        # Calculate domain position for this subplot
        domain = self.calculate_indicator_domain(row, col)
        
        # Color based on quality score
        color = self._get_quality_color(quality_score)
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=quality_score,
                title={"text": f"Data Quality Score<br><span style='font-size:0.8em;color:gray'>{reliability.title()} • {anomalies} anomalies</span>"},
                domain=domain,
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75, 
                        'value': 90
                    }
                }
            )
        )
    
    def _get_quality_color(self, quality_score: float) -> str:
        """Get color based on quality score."""
        if quality_score >= 80:
            return "green"
        elif quality_score >= 60:
            return "orange"
        else:
            return "red"


class AIPeerAnalysis(ChartBase):
    """Chart component for AI peer comparison analysis."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, comprehensive_ai_analysis: Any, **kwargs) -> None:
        """Add AI peer analysis chart to figure."""
        if not comprehensive_ai_analysis or not hasattr(comprehensive_ai_analysis, 'peer_analysis'):
            fig.add_trace(self.create_no_data_bar("Peer Analysis"), row=row, col=col)
            return

        peer_analysis = comprehensive_ai_analysis.peer_analysis
        if not peer_analysis:
            fig.add_trace(self.create_no_data_bar("Peer Analysis"), row=row, col=col)
            return

        # Extract peer comparison data
        company_zscore = self.safe_get_numeric(peer_analysis, 'company_zscore', 2.0)
        industry_avg = self.safe_get_numeric(peer_analysis, 'industry_average_zscore', 1.9)
        peer_rank = self.safe_get_numeric(peer_analysis, 'industry_rank_percentile', 0.5)
        
        categories = ['Company Z-Score', 'Industry Average', 'Peer Rank %']
        values = [company_zscore, industry_avg, peer_rank * 100]
        colors = ['blue', 'gray', 'green' if peer_rank > 0.5 else 'orange']
        
        fig.add_trace(
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                name='Peer Comparison',
                text=[self.format_value(v) for v in values],
                textposition='auto'
            ),
            row=row, col=col
        )


class AISentiment(ChartBase):
    """Chart component for AI sentiment analysis."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, comprehensive_ai_analysis: Any, **kwargs) -> None:
        """Add AI sentiment analysis chart to figure."""
        if not comprehensive_ai_analysis or not hasattr(comprehensive_ai_analysis, 'sentiment_analysis'):
            self._add_neutral_sentiment_indicator(fig, "No AI Analysis", row, col)
            return

        sentiment = comprehensive_ai_analysis.sentiment_analysis
        if not sentiment:
            self._add_neutral_sentiment_indicator(fig, "Neutral", row, col)
            return

        sentiment_score = self.safe_get_numeric(sentiment, 'overall_sentiment_score', 0)
        sentiment_trend = getattr(sentiment, 'sentiment_trend', 'stable')
        confidence = self.safe_get_numeric(sentiment, 'confidence', 0.5)
        
        # Color based on sentiment
        color = self._get_sentiment_color(sentiment_score)
        
        # Trend indicator
        trend_symbol = self._get_trend_symbol(sentiment_trend)
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=sentiment_score,
                title={"text": f"Market Sentiment<br><span style='font-size:0.8em;color:gray'>{sentiment_trend.title()} {trend_symbol} • {confidence:.0%} confidence</span>"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [-1, -0.3], 'color': "lightcoral"},
                        {'range': [-0.3, 0.3], 'color': "lightyellow"},
                        {'range': [0.3, 1], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75, 
                        'value': 0
                    }
                }
            ),
            row=row, col=col
        )
    
    def _get_sentiment_color(self, sentiment_score: float) -> str:
        """Get color based on sentiment score."""
        if sentiment_score > 0.3:
            return "green"
        elif sentiment_score < -0.3:
            return "red"
        else:
            return "yellow"
    
    def _get_trend_symbol(self, sentiment_trend: str) -> str:
        """Get trend symbol based on sentiment trend."""
        if sentiment_trend == 'improving':
            return "↗"
        elif sentiment_trend == 'declining':
            return "↘"
        else:
            return "→"
    
    def _add_neutral_sentiment_indicator(self, fig: go.Figure, subtitle: str, row: int, col: int) -> None:
        """Add neutral sentiment indicator."""
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=0,
                title={"text": f"Market Sentiment<br><span style='font-size:0.8em;color:gray'>{subtitle}</span>"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': "gray"},
                    'steps': [{'range': [-1, 1], 'color': "lightgray"}]
                }
            ),
            row=row, col=col
        )


class AIRisk(ChartBase):
    """Chart component for AI risk assessment."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, comprehensive_ai_analysis: Any, **kwargs) -> None:
        """Add AI risk assessment chart to figure."""
        if not comprehensive_ai_analysis or not hasattr(comprehensive_ai_analysis, 'risk_analysis'):
            self._add_default_risk_indicator(fig, "No AI Analysis", row, col)
            return

        risk_analysis = comprehensive_ai_analysis.risk_analysis
        if not risk_analysis:
            self._add_default_risk_indicator(fig, "Moderate Risk", row, col)
            return

        risk_score = self.safe_get_numeric(risk_analysis, 'overall_risk_score', 0.5)
        risk_level = getattr(risk_analysis, 'risk_level', 'moderate')
        key_factors = getattr(risk_analysis, 'key_risk_factors', [])
        
        # Color based on risk level
        color = self._get_risk_color(risk_score)
        factor_count = len(key_factors) if key_factors else 0
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={"text": f"Risk Assessment<br><span style='font-size:0.8em;color:gray'>{risk_level.title()} • {factor_count} factors</span>"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 1]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 0.3], 'color': "lightgreen"},
                        {'range': [0.3, 0.7], 'color': "lightyellow"},
                        {'range': [0.7, 1], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75, 
                        'value': 0.8
                    }
                }
            ),
            row=row, col=col
        )
    
    def _get_risk_color(self, risk_score: float) -> str:
        """Get color based on risk level."""
        if risk_score < 0.3:
            return "green"
        elif risk_score < 0.7:
            return "yellow"
        else:
            return "red"
    
    def _add_default_risk_indicator(self, fig: go.Figure, subtitle: str, row: int, col: int) -> None:
        """Add default risk indicator."""
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=0.5,
                title={"text": f"Risk Assessment<br><span style='font-size:0.8em;color:gray'>{subtitle}</span>"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 1]},
                    'bar': {'color': "yellow"},
                    'steps': [{'range': [0, 1], 'color': "lightgray"}]
                }
            ),
            row=row, col=col
        )


class AIConfidence(ChartBase):
    """Chart component for AI confidence metrics."""
    
    def add_to_figure(self, fig: go.Figure, row: int, col: int, comprehensive_ai_analysis: Any, **kwargs) -> None:
        """Add AI confidence chart to figure."""
        if not comprehensive_ai_analysis:
            self._add_no_confidence_indicator(fig, row, col)
            return

        confidence = self.safe_get_numeric(comprehensive_ai_analysis, 'overall_ai_confidence', 0)
        recommendations_count = len(getattr(comprehensive_ai_analysis, 'ai_recommendations', []))
        
        # Color based on confidence level
        color = self._get_confidence_color(confidence)
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=confidence,
                title={"text": f"AI Confidence<br><span style='font-size:0.8em;color:gray'>{recommendations_count} insights</span>"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 1]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 0.5], 'color': "lightgray"},
                        {'range': [0.5, 0.8], 'color': "lightyellow"},
                        {'range': [0.8, 1], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75, 
                        'value': 0.9
                    }
                }
            ),
            row=row, col=col
        )
    
    def _get_confidence_color(self, confidence: float) -> str:
        """Get color based on confidence level."""
        if confidence >= 0.8:
            return "green"
        elif confidence >= 0.6:
            return "yellow"
        else:
            return "orange"
    
    def _add_no_confidence_indicator(self, fig: go.Figure, row: int, col: int) -> None:
        """Add no confidence indicator."""
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=0,
                title={"text": "AI Confidence<br><span style='font-size:0.8em;color:gray'>No Analysis</span>"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 1]},
                    'bar': {'color': "gray"},
                    'steps': [{'range': [0, 1], 'color': "lightgray"}]
                }
            ),
            row=row, col=col
        )
