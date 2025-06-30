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
        
        # Calculate smaller domain position for this subplot to make gauge more compact
        domain = self.calculate_indicator_domain(row, col)
        # Make the gauge smaller by reducing the domain size
        x_center = (domain['x'][0] + domain['x'][1]) / 2
        y_center = (domain['y'][0] + domain['y'][1]) / 2
        width = (domain['x'][1] - domain['x'][0]) * 0.7  # Reduce width by 30%
        height = (domain['y'][1] - domain['y'][0]) * 0.7  # Reduce height by 30%
        
        compact_domain = {
            'x': [x_center - width/2, x_center + width/2],
            'y': [y_center - height/2, y_center + height/2]
        }
        
        # Color based on quality score
        color = self._get_quality_color(quality_score)
        
        # Use horizontal bar chart instead of gauge for cleaner look
        fig.add_trace(
            go.Bar(
                x=[quality_score],
                y=[f"Data Quality<br>{reliability.title()}<br>{anomalies} anomalies"],
                orientation='h',
                marker_color=color,
                text=[f"{quality_score:.1f}/100"],
                textposition='auto',
                textfont={'size': 12, 'color': 'white'},
                name='Data Quality Score',
                showlegend=False,
                hovertemplate=f"<b>Data Quality Score</b><br>" +
                            f"Score: {quality_score:.1f}/100<br>" +
                            f"Reliability: {reliability.title()}<br>" +
                            f"Anomalies: {anomalies}<br>" +
                            "<extra></extra>"
            ),
            row=row, col=col
        )
        
        # Add reference line for excellent threshold (90)
        fig.add_vline(x=90, line_dash="dash", line_color="darkgreen", 
                     opacity=0.7, row=row, col=col)
        
        # Update x-axis for this subplot
        fig.update_xaxes(range=[0, 100], title_text="Score", row=row, col=col)
    
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
        
        # Calculate smaller domain position for this subplot to make gauge more compact
        domain = self.calculate_indicator_domain(row, col)
        # Make the gauge smaller by reducing the domain size
        x_center = (domain['x'][0] + domain['x'][1]) / 2
        y_center = (domain['y'][0] + domain['y'][1]) / 2
        width = (domain['x'][1] - domain['x'][0]) * 0.7  # Reduce width by 30%
        height = (domain['y'][1] - domain['y'][0]) * 0.7  # Reduce height by 30%
        
        compact_domain = {
            'x': [x_center - width/2, x_center + width/2],
            'y': [y_center - height/2, y_center + height/2]
        }
        
        # Convert sentiment score from -1 to 1 range to 0-100 for display
        display_value = (sentiment_score + 1) * 50  # Convert -1,1 to 0,100
        
        # Use horizontal bar with sentiment zones
        fig.add_trace(
            go.Bar(
                x=[display_value],
                y=[f"Market Sentiment<br>{sentiment_trend.title()} {trend_symbol}<br>{confidence:.0%} confidence"],
                orientation='h',
                marker_color=color,
                text=[f"{sentiment_score:+.2f}"],
                textposition='auto',
                textfont={'size': 12, 'color': 'white'},
                name='Market Sentiment',
                showlegend=False,
                hovertemplate=f"<b>Market Sentiment</b><br>" +
                            f"Score: {sentiment_score:+.2f}<br>" +
                            f"Trend: {sentiment_trend.title()}<br>" +
                            f"Confidence: {confidence:.1%}<br>" +
                            "<extra></extra>"
            ),
            row=row, col=col
        )
        
        # Add sentiment zone markers
        fig.add_vline(x=25, line_dash="dash", line_color="red", opacity=0.5, row=row, col=col)  # -0.5 threshold
        fig.add_vline(x=50, line_dash="solid", line_color="gray", opacity=0.7, row=row, col=col)  # Neutral
        fig.add_vline(x=75, line_dash="dash", line_color="green", opacity=0.5, row=row, col=col)  # +0.5 threshold
        
        # Update x-axis
        fig.update_xaxes(
            range=[0, 100], 
            title_text="Negative ← Sentiment → Positive",
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['-1.0', '-0.5', '0.0', '+0.5', '+1.0'],
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
        # Use same horizontal bar style for consistency
        fig.add_trace(
            go.Bar(
                x=[50],  # Neutral position (center)
                y=[f"Market Sentiment<br>{subtitle}"],
                orientation='h',
                marker_color="gray",
                text=["0.00"],
                textposition='auto',
                textfont={'size': 12, 'color': 'white'},
                name='Market Sentiment',
                showlegend=False,
                hovertemplate=f"<b>Market Sentiment</b><br>" +
                            f"Status: {subtitle}<br>" +
                            "<extra></extra>"
            ),
            row=row, col=col
        )
        
        # Add neutral line
        fig.add_vline(x=50, line_dash="solid", line_color="gray", opacity=0.7, row=row, col=col)
        
        # Update x-axis
        fig.update_xaxes(
            range=[0, 100], 
            title_text="Negative ← Sentiment → Positive",
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['-1.0', '-0.5', '0.0', '+0.5', '+1.0'],
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
        
        # Calculate smaller domain position for this subplot to make gauge more compact
        domain = self.calculate_indicator_domain(row, col)
        # Make the gauge smaller by reducing the domain size
        x_center = (domain['x'][0] + domain['x'][1]) / 2
        y_center = (domain['y'][0] + domain['y'][1]) / 2
        width = (domain['x'][1] - domain['x'][0]) * 0.7  # Reduce width by 30%
        height = (domain['y'][1] - domain['y'][0]) * 0.7  # Reduce height by 30%
        
        compact_domain = {
            'x': [x_center - width/2, x_center + width/2],
            'y': [y_center - height/2, y_center + height/2]
        }
        
        # Use horizontal bar with risk level zones
        display_value = risk_score * 100  # Convert 0-1 to 0-100
        
        fig.add_trace(
            go.Bar(
                x=[display_value],
                y=[f"Risk Assessment<br>{risk_level.title()}<br>{factor_count} factors"],
                orientation='h',
                marker_color=color,
                text=[f"{risk_score:.2f}"],
                textposition='auto',
                textfont={'size': 12, 'color': 'white'},
                name='Risk Score',
                showlegend=False,
                hovertemplate=f"<b>Risk Assessment</b><br>" +
                            f"Risk Score: {risk_score:.2f}/1.0<br>" +
                            f"Risk Level: {risk_level.title()}<br>" +
                            f"Key Factors: {factor_count}<br>" +
                            "<extra></extra>"
            ),
            row=row, col=col
        )
        
        # Add risk zone markers
        fig.add_vline(x=30, line_dash="dash", line_color="green", opacity=0.7, row=row, col=col)  # Low risk
        fig.add_vline(x=70, line_dash="dash", line_color="orange", opacity=0.7, row=row, col=col)  # High risk
        fig.add_vline(x=80, line_dash="dash", line_color="red", opacity=0.7, row=row, col=col)    # Critical
        
        # Update x-axis
        fig.update_xaxes(
            range=[0, 100], 
            title_text="Low ← Risk Level → High",
            tickvals=[0, 30, 70, 100],
            ticktext=['0%', '30%', '70%', '100%'],
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
        # Use same horizontal bar style for consistency
        fig.add_trace(
            go.Bar(
                x=[50],  # Moderate risk (center)
                y=[f"Risk Assessment<br>{subtitle}"],
                orientation='h',
                marker_color="yellow",
                text=["0.50"],
                textposition='auto',
                textfont={'size': 12, 'color': 'black'},
                name='Risk Score',
                showlegend=False,
                hovertemplate=f"<b>Risk Assessment</b><br>" +
                            f"Status: {subtitle}<br>" +
                            "<extra></extra>"
            ),
            row=row, col=col
        )
        
        # Add risk zone markers
        fig.add_vline(x=30, line_dash="dash", line_color="green", opacity=0.7, row=row, col=col)
        fig.add_vline(x=70, line_dash="dash", line_color="orange", opacity=0.7, row=row, col=col)
        
        # Update x-axis
        fig.update_xaxes(
            range=[0, 100], 
            title_text="Low ← Risk Level → High",
            tickvals=[0, 30, 70, 100],
            ticktext=['0%', '30%', '70%', '100%'],
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
        
        # Calculate smaller domain position for this subplot to make gauge more compact
        domain = self.calculate_indicator_domain(row, col)
        # Make the gauge smaller by reducing the domain size
        x_center = (domain['x'][0] + domain['x'][1]) / 2
        y_center = (domain['y'][0] + domain['y'][1]) / 2
        width = (domain['x'][1] - domain['x'][0]) * 0.7  # Reduce width by 30%
        height = (domain['y'][1] - domain['y'][0]) * 0.7  # Reduce height by 30%
        
        compact_domain = {
            'x': [x_center - width/2, x_center + width/2],
            'y': [y_center - height/2, y_center + height/2]
        }
        
        # Use metric card style with scatter plot for clean presentation
        fig.add_trace(
            go.Scatter(
                x=[0.5],
                y=[0.5], 
                mode='text',
                text=[f"<b>{confidence:.0%}</b><br>AI Confidence<br><span style='font-size:10px'>{recommendations_count} insights</span>"],
                textfont={'size': 16, 'color': 'white'},
                marker=dict(
                    size=120,
                    color=color,
                    symbol='square',
                    line=dict(width=2, color='white')
                ),
                showlegend=False,
                hovertemplate=f"<b>AI Confidence</b><br>" +
                            f"Confidence Level: {confidence:.1%}<br>" +
                            f"Generated Insights: {recommendations_count}<br>" +
                            "<extra></extra>"
            ),
            row=row, col=col
        )
        
        # Clean up axes for card look
        fig.update_xaxes(visible=False, row=row, col=col)
        fig.update_yaxes(visible=False, row=row, col=col)
    
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
        # Use metric card style for consistency
        fig.add_trace(
            go.Scatter(
                x=[0.5],
                y=[0.5], 
                mode='text',
                text=["<b>N/A</b><br>AI Confidence<br><span style='font-size:10px'>No Analysis</span>"],
                textfont={'size': 16, 'color': 'white'},
                marker=dict(
                    size=120,
                    color="gray",
                    symbol='square',
                    line=dict(width=2, color='white')
                ),
                showlegend=False,
                hovertemplate="<b>AI Confidence</b><br>Status: No Analysis Available<br><extra></extra>"
            ),
            row=row, col=col
        )
        
        # Clean up axes for card look
        fig.update_xaxes(visible=False, row=row, col=col)
        fig.update_yaxes(visible=False, row=row, col=col)
