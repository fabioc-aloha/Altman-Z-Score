    def _add_ai_data_quality_chart(self, fig, comprehensive_ai_analysis, row: int, col: int):
        """Display AI data quality metrics and anomalies."""
        if not comprehensive_ai_analysis or not hasattr(comprehensive_ai_analysis, 'data_quality'):
            # Show "No Data" placeholder
            fig.add_trace(
                go.Bar(
                    x=['No Data'],
                    y=[0],
                    marker_color='gray',
                    name='AI Data Quality',
                    text=['No AI Analysis'],
                    textposition='auto',
                    showlegend=False
                ),
                row=row, col=col
            )
            return

        dq = comprehensive_ai_analysis.data_quality
        quality_score = getattr(dq, 'overall_quality_score', 0)
        reliability = getattr(dq, 'reliability_rating', 'unknown')
        anomalies = len(getattr(dq, 'anomalies_detected', []))
        
        # Color based on quality score
        if quality_score >= 80:
            color = "green"
        elif quality_score >= 60:
            color = "orange"
        else:
            color = "red"
        
        fig.add_trace(
            go.Bar(
                x=['Data Quality'],
                y=[quality_score],
                marker_color=color,
                name=f'Quality: {quality_score:.1f}%',
                text=[f'{quality_score:.1f}%<br>{reliability}<br>{anomalies} anomalies'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Add quality reference lines
        fig.add_hline(y=60, line_dash="dash", line_color="red", 
                     annotation_text="Min Quality", row=row, col=col)
        fig.add_hline(y=80, line_dash="dash", line_color="green", 
                     annotation_text="Good Quality", row=row, col=col)

    def _add_ai_sentiment_chart(self, fig, comprehensive_ai_analysis, row: int, col: int):
        """Display sentiment analysis and trend indicators."""
        if not comprehensive_ai_analysis or not hasattr(comprehensive_ai_analysis, 'sentiment_analysis'):
            # Show "No Data" placeholder
            fig.add_trace(
                go.Bar(
                    x=['No Data'],
                    y=[0],
                    marker_color='gray',
                    name='AI Sentiment',
                    text=['No AI Analysis'],
                    textposition='auto',
                    showlegend=False
                ),
                row=row, col=col
            )
            return

        sentiment = comprehensive_ai_analysis.sentiment_analysis
        if not sentiment:
            fig.add_trace(
                go.Bar(
                    x=['Sentiment'],
                    y=[0],
                    marker_color='gray',
                    name='Neutral Sentiment',
                    text=['Neutral'],
                    textposition='auto',
                    showlegend=False
                ),
                row=row, col=col
            )
            return

        sentiment_score = getattr(sentiment, 'overall_sentiment_score', 0)
        sentiment_trend = getattr(sentiment, 'sentiment_trend', 'stable')
        confidence = getattr(sentiment, 'confidence', 0.5)
        
        # Color based on sentiment
        if sentiment_score > 0.3:
            color = "green"
        elif sentiment_score < -0.3:
            color = "red"
        else:
            color = "yellow"
        
        # Trend indicator
        if sentiment_trend == 'improving':
            trend_symbol = "↗"
        elif sentiment_trend == 'declining':
            trend_symbol = "↘"
        else:
            trend_symbol = "→"
        
        # Convert to 0-100 scale for display
        display_score = (sentiment_score + 1) * 50  # -1 to 1 becomes 0 to 100
        
        fig.add_trace(
            go.Bar(
                x=['Sentiment'],
                y=[display_score],
                marker_color=color,
                name=f'Sentiment: {sentiment_score:.2f}',
                text=[f'{sentiment_score:.2f}<br>{sentiment_trend} {trend_symbol}<br>{confidence:.0%} conf'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Add sentiment reference lines
        fig.add_hline(y=30, line_dash="dash", line_color="red", 
                     annotation_text="Negative", row=row, col=col)
        fig.add_hline(y=70, line_dash="dash", line_color="green", 
                     annotation_text="Positive", row=row, col=col)

    def _add_ai_risk_chart(self, fig, comprehensive_ai_analysis, row: int, col: int):
        """Display risk factor analysis and trajectory."""
        if not comprehensive_ai_analysis or not hasattr(comprehensive_ai_analysis, 'risk_analysis'):
            # Show "No Data" placeholder
            fig.add_trace(
                go.Bar(
                    x=['No Data'],
                    y=[50],
                    marker_color='gray',
                    name='AI Risk',
                    text=['No AI Analysis'],
                    textposition='auto',
                    showlegend=False
                ),
                row=row, col=col
            )
            return

        risk_analysis = comprehensive_ai_analysis.risk_analysis
        if not risk_analysis:
            fig.add_trace(
                go.Bar(
                    x=['Risk Level'],
                    y=[50],
                    marker_color='yellow',
                    name='Moderate Risk',
                    text=['Moderate Risk'],
                    textposition='auto',
                    showlegend=False
                ),
                row=row, col=col
            )
            return

        risk_score = getattr(risk_analysis, 'overall_risk_score', 0.5)
        risk_level = getattr(risk_analysis, 'risk_level', 'moderate')
        key_factors = getattr(risk_analysis, 'key_risk_factors', [])
        
        # Color based on risk level
        if risk_score < 0.3:
            color = "green"
        elif risk_score < 0.7:
            color = "yellow"
        else:
            color = "red"
        
        factor_count = len(key_factors) if key_factors else 0
        
        # Convert to 0-100 scale for display
        display_score = risk_score * 100
        
        fig.add_trace(
            go.Bar(
                x=['Risk Level'],
                y=[display_score],
                marker_color=color,
                name=f'Risk: {risk_score:.2f}',
                text=[f'{risk_level}<br>{risk_score:.2f}<br>{factor_count} factors'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Add risk reference lines
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="Low Risk", row=row, col=col)
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="High Risk", row=row, col=col)

    def _add_ai_confidence_chart(self, fig, comprehensive_ai_analysis, row: int, col: int):
        """Display overall AI analysis confidence metrics."""
        if not comprehensive_ai_analysis:
            # Show "No Data" placeholder
            fig.add_trace(
                go.Bar(
                    x=['No Data'],
                    y=[0],
                    marker_color='gray',
                    name='AI Confidence',
                    text=['No Analysis'],
                    textposition='auto',
                    showlegend=False
                ),
                row=row, col=col
            )
            return

        confidence = getattr(comprehensive_ai_analysis, 'overall_ai_confidence', 0)
        recommendations_count = len(getattr(comprehensive_ai_analysis, 'ai_recommendations', []))
        
        # Color based on confidence level
        if confidence >= 0.8:
            color = "green"
        elif confidence >= 0.6:
            color = "yellow"
        else:
            color = "orange"
        
        # Convert to 0-100 scale for display
        display_confidence = confidence * 100
        
        fig.add_trace(
            go.Bar(
                x=['AI Confidence'],
                y=[display_confidence],
                marker_color=color,
                name=f'Confidence: {confidence:.1%}',
                text=[f'{confidence:.1%}<br>{recommendations_count} insights'],
                textposition='auto',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Add confidence reference lines
        fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                     annotation_text="Moderate", row=row, col=col)
        fig.add_hline(y=80, line_dash="dash", line_color="green", 
                     annotation_text="High Confidence", row=row, col=col)
