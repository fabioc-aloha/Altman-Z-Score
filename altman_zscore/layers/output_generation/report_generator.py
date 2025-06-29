"""
Report Generator - Create comprehensive analysis reports

This module generates detailed HTML and text reports combining
financial data analysis with AI-powered insights and recommendations.

Key Features:
- HTML reports with professional styling
- AI-generated financial insights integration
- Risk assessment summaries
- Actionable recommendations and warnings
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Template
import markdown

from ...common.logging_config import get_logger
from ...common.exceptions import OutputGenerationError
from ...common.markdown_utils import format_ai_insights_for_html
from ...common.constants import ZSCORE_MODELS
from ..zscore_calculation import ZScoreCalculationResult

logger = get_logger(__name__)


class ReportGenerator:
    """Generator for comprehensive analysis reports."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize report generator.
        
        Args:
            output_base_path: Base directory for output files        
        """
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(
        self, 
        zscore_result: ZScoreCalculationResult,
        ai_insights: Optional[str] = None,
        market_analysis = None,
        ai_analysis = None
    ) -> str:
        """
        Generate comprehensive HTML report enhanced with market analysis and AI analysis.
        
        Args:
            zscore_result: Z-Score calculation result
            ai_insights: Optional AI-generated insights
            market_analysis: Optional market analysis results for enhanced insights
            ai_analysis: Optional comprehensive AI analysis results
            
        Returns:
            str: Path to generated HTML report
        """
        try:
            ticker_dir = self.output_base_path / zscore_result.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            report_path = ticker_dir / f"{zscore_result.ticker}_comprehensive_report.html"
            # Generate report content
            html_content = self._generate_html_report(zscore_result, ai_insights, market_analysis, ticker_dir, ai_analysis)
            
            # Write HTML file
            with open(report_path, 'w', encoding='utf-8') as report_file:
                report_file.write(html_content)
            
            logger.info(f"Comprehensive report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            error_msg = f"Failed to generate report for {zscore_result.ticker}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def generate_summary_report(self, zscore_result: ZScoreCalculationResult, market_analysis=None, ai_analysis=None) -> str:
        """
        Generate concise text summary report enhanced with market analysis and AI analysis.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results for enhanced insights
            ai_analysis: Optional comprehensive AI analysis results
            
        Returns:
            str: Path to generated text report
        """
        try:
            ticker_dir = self.output_base_path / zscore_result.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            summary_path = ticker_dir / f"{zscore_result.ticker}_summary.txt"
            # Generate summary content
            summary_content = self._generate_summary_content(zscore_result, market_analysis, ai_analysis)
            
            # Write text file
            with open(summary_path, 'w', encoding='utf-8') as summary_file:
                summary_file.write(summary_content)
            
            logger.info(f"Summary report generated: {summary_path}")
            return str(summary_path)
            
        except Exception as e:
            error_msg = f"Failed to generate summary for {zscore_result.ticker}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def _generate_html_report(
        self, 
        zscore_result: ZScoreCalculationResult,
        ai_insights: Optional[str] = None,
        market_analysis = None,
        output_dir: Path = None,
        ai_analysis = None
    ) -> str:
        """Generate HTML report content enhanced with market analysis and AI analysis."""
        
        # Load template from external file
        template_path = Path(__file__).parent / "templates" / "report_template.html"
        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()
        
        template = Template(template_str)
        
        # Determine risk class for styling
        risk_class = self._get_risk_class(zscore_result.z_score)
        
        # Get model-specific thresholds and description for display
        model_thresholds = self._get_model_thresholds(zscore_result.model_used)
        model_description = self._get_model_description(zscore_result.model_used)
        
        # Prepare base template data
        template_data = {
            'ticker': zscore_result.ticker,
            'company_name': self._get_company_name(zscore_result),
            'logo_url': self._get_logo_path(zscore_result, output_dir),
            'z_score': f"{zscore_result.z_score:.2f}",
            'risk_category': zscore_result.risk_category,
            'model_used': zscore_result.model_used,
            'model_description': model_description,
            'model_thresholds': model_thresholds,
            'data_quality_score': f"{zscore_result.data_quality_score * 100:.1f}",
            'calculation_date': self._format_calculation_date(zscore_result.calculation_timestamp),
            'component_values': self._format_component_values(zscore_result.component_values),
            'warnings': zscore_result.warnings,
            'ai_insights': format_ai_insights_for_html(ai_insights),  # Convert markdown to HTML (legacy)
            'ai_analysis': ai_analysis,  # Comprehensive AI analysis from orchestrator
            'ai_analysis_html': format_ai_insights_for_html(ai_analysis.llm_final_commentary if ai_analysis and hasattr(ai_analysis, 'llm_final_commentary') else None),  # HTML-formatted comprehensive analysis
            'risk_class': risk_class,
            'generation_date': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            'market_analysis': market_analysis
        }
        
        # Add comprehensive AI analysis data if available
        if ai_analysis:
            # Data Quality Analysis - Extract comprehensive details
            if hasattr(ai_analysis, 'data_quality') and ai_analysis.data_quality:
                dq = ai_analysis.data_quality
                template_data.update({
                    'ai_data_quality_score': getattr(dq, 'overall_quality_score', 0),
                    'ai_data_reliability': getattr(dq, 'reliability_rating', 'unknown'),
                    'ai_data_anomalies': len(getattr(dq, 'anomalies_detected', [])),
                    'ai_data_recommendation': getattr(dq, 'recommendation', 'No specific recommendation available.'),
                    'ai_anomalies_list': getattr(dq, 'anomalies_detected', []),
                    'ai_quality_issues': getattr(dq, 'quality_issues', [])
                })
            else:
                template_data.update({
                    'ai_data_quality_score': None,
                    'ai_data_reliability': 'unknown',
                    'ai_data_anomalies': 0,
                    'ai_data_recommendation': None
                })
            
            # Peer Analysis - Extract with industry context
            if hasattr(ai_analysis, 'peer_analysis') and ai_analysis.peer_analysis:
                peer = ai_analysis.peer_analysis
                template_data.update({
                    'ai_company_zscore': getattr(peer, 'company_zscore', None),
                    'ai_industry_avg_zscore': getattr(peer, 'industry_average_zscore', None),
                    'ai_peer_rank': getattr(peer, 'industry_rank_percentile', None),
                    'ai_peer_reasoning': getattr(peer, 'reasoning', 'Peer analysis completed using AI-powered company similarity matching.'),
                    'ai_identified_peers': getattr(peer, 'identified_peers', [])
                })
            else:
                template_data.update({
                    'ai_company_zscore': None,
                    'ai_industry_avg_zscore': None,
                    'ai_peer_rank': None,
                    'ai_peer_reasoning': None
                })
            
            # Sentiment Analysis - Extract with detailed insights
            if hasattr(ai_analysis, 'sentiment_analysis') and ai_analysis.sentiment_analysis:
                sentiment = ai_analysis.sentiment_analysis
                template_data.update({
                    'ai_sentiment_score': getattr(sentiment, 'overall_sentiment_score', 0),
                    'ai_sentiment_trend': getattr(sentiment, 'sentiment_trend', 'stable'),
                    'ai_sentiment_confidence': getattr(sentiment, 'confidence', 0.5),
                    'ai_sentiment_summary': getattr(sentiment, 'summary', 'Market sentiment analysis completed.'),
                    'ai_sentiment_divergence': getattr(sentiment, 'fundamental_sentiment_divergence', None)
                })
            else:
                template_data.update({
                    'ai_sentiment_score': None,
                    'ai_sentiment_trend': 'stable',
                    'ai_sentiment_confidence': None,
                    'ai_sentiment_summary': None
                })
            
            # Risk Analysis - Extract with comprehensive risk factors
            if hasattr(ai_analysis, 'risk_analysis') and ai_analysis.risk_analysis:
                risk = ai_analysis.risk_analysis
                template_data.update({
                    'ai_risk_score': getattr(risk, 'overall_risk_score', 0.5),
                    'ai_risk_level': getattr(risk, 'risk_level', 'moderate'),
                    'ai_risk_factors': getattr(risk, 'key_risk_factors', []),
                    'ai_risk_trajectory': getattr(risk, 'risk_trajectory', 'stable'),
                    'ai_risk_mitigation': getattr(risk, 'risk_mitigation_suggestions', [])
                })
            else:
                template_data.update({
                    'ai_risk_score': 0.5,
                    'ai_risk_level': 'moderate',
                    'ai_risk_factors': [],
                    'ai_risk_trajectory': 'stable'
                })
            
            # Overall AI Metrics and Enhanced Insights
            template_data.update({
                'ai_overall_confidence': getattr(ai_analysis, 'overall_ai_confidence', 0),
                'ai_recommendations': getattr(ai_analysis, 'ai_recommendations', []),
                'ai_recommendations_count': len(getattr(ai_analysis, 'ai_recommendations', [])),
                'ai_analysis_timestamp': getattr(ai_analysis, 'analysis_timestamp', None),
                'ai_executive_summary': self._extract_executive_summary(ai_analysis),
                'ai_key_insights': self._extract_key_insights(ai_analysis),
                'ai_investment_thesis': self._extract_investment_thesis(ai_analysis)
            })
        
        # Add market analysis data if available
        if market_analysis:
            rec = market_analysis.risk_return_profile
            tech = market_analysis.technical_analysis
            val = market_analysis.valuation_metrics  
            perf = market_analysis.market_performance
            risk = market_analysis.risk_return_profile
            
            template_data.update({
                'recommendation_action': self._format_investment_rating(rec.investment_rating if rec else "HOLD"),
                'recommendation_confidence': f"{rec.confidence_level * 100:.1f}" if rec else "N/A",
                'recommendation_class': self._get_recommendation_class(rec.investment_rating if rec else "hold"),
                'key_risks': rec.key_risks if rec and rec.key_risks else [],
                'key_opportunities': rec.key_opportunities if rec and rec.key_opportunities else [],
                'current_price': self._format_currency(tech.current_price) if tech and tech.current_price else "N/A",
                'market_cap': self._format_currency(val.market_cap / 1e9, "B") if val and hasattr(val, 'market_cap') and val.market_cap else "N/A",
                'pe_ratio': f"{val.pe_ratio:.1f}" if val and hasattr(val, 'pe_ratio') and val.pe_ratio else "N/A",
                'return_1y': f"{perf.return_1y * 100:.1f}" if perf and hasattr(perf, 'return_1y') and perf.return_1y else "N/A",                
                'volatility': f"{risk.volatility_risk * 100:.1f}" if risk and hasattr(risk, 'volatility_risk') and risk.volatility_risk else "N/A",
                'rsi': f"{tech.indicators.rsi:.1f}" if tech and tech.indicators and hasattr(tech.indicators, 'rsi') and tech.indicators.rsi else "N/A",
                'macd_signal': tech.overall_signal or "N/A" if tech else "N/A",
                'bollinger_signal': "N/A",  # Simplified for now
                'momentum_score': f"{tech.momentum_score * 10:.1f}" if tech and tech.momentum_score else "N/A",
                'technical_trend': tech.price_trend or "N/A" if tech else "N/A",
                'return_1d': f"{perf.return_1d * 100:.2f}" if perf.return_1d else "N/A",
                'return_5d': f"{perf.return_1w * 100:.2f}" if perf.return_1w else "N/A",
                'return_1m': f"{perf.return_1m * 100:.1f}" if perf.return_1m else "N/A",
                'return_3m': f"{perf.return_3m * 100:.1f}" if perf.return_3m else "N/A",
                'return_6m': f"{perf.return_6m * 100:.1f}" if perf.return_6m else "N/A",
                'beta': f"{perf.beta:.2f}" if perf.beta else "N/A",
                'sharpe_ratio': f"{perf.sharpe_ratio:.2f}" if perf.sharpe_ratio else "N/A",
                'max_drawdown': f"{perf.max_drawdown * 100:.1f}" if perf.max_drawdown else "N/A",
                'risk_score': f"{risk.overall_risk_score * 10:.1f}" if risk and risk.overall_risk_score else "N/A"
            })
        
        # Render template
        return template.render(template_data)
    
    def _generate_summary_content(self, zscore_result: ZScoreCalculationResult, market_analysis=None, ai_analysis=None) -> str:
        """Generate text summary content."""
        content = []
        content.append(f"=== ALTMAN Z-SCORE ANALYSIS SUMMARY ===")
        content.append(f"Ticker: {zscore_result.ticker}")
        content.append(f"Analysis Date: {zscore_result.calculation_timestamp}")
        content.append("")
        
        # Z-Score Summary
        content.append(f"Z-SCORE: {zscore_result.z_score:.2f}")
        content.append(f"Risk Category: {zscore_result.risk_category}")
        content.append(f"Model Used: {zscore_result.model_used}")
        content.append(f"Data Quality: {zscore_result.data_quality_score * 100:.1f}%")
        content.append("")
        
        # Model-specific thresholds
        model_thresholds = self._get_model_thresholds(zscore_result.model_used)
        content.append("MODEL THRESHOLDS:")
        content.append(f"  Safe Zone: > {model_thresholds['safe']}")
        content.append(f"  Gray Zone: {model_thresholds['gray_zone_lower']} - {model_thresholds['gray_zone_upper']}")
        content.append(f"  Distress Zone: < {model_thresholds['distress']}")
        content.append("")
        
        # Component Analysis
        content.append("COMPONENT ANALYSIS:")
        for component, value in zscore_result.component_values.items():
            # Skip non-numeric values (like metadata)
            if not isinstance(value, (int, float)) or component.startswith('_'):
                continue
            formatted_name = self._format_component_name(component)
            formatted_value = self._format_number(value)
            content.append(f"  {formatted_name}: {formatted_value}")
        content.append("")
        
        # Market Analysis Summary (if available)
        if market_analysis:
            rec = market_analysis.risk_return_profile
            if rec:
                content.append("INVESTMENT RECOMMENDATION:")
                content.append(f"  Action: {self._format_investment_rating(rec.investment_rating)}")
                content.append(f"  Confidence: {rec.confidence_level * 100:.1f}%")
                content.append("")
        
        # AI Analysis Summary (if available)
        if ai_analysis and hasattr(ai_analysis, 'llm_final_commentary') and ai_analysis.llm_final_commentary:
            content.append("AI-POWERED ANALYSIS SUMMARY:")
            # Extract first few lines of AI analysis for summary
            ai_lines = ai_analysis.llm_final_commentary.split('\n')[:10]
            for line in ai_lines:
                if line.strip():
                    content.append(f"  {line.strip()}")
            if len(ai_analysis.llm_final_commentary.split('\n')) > 10:
                content.append("  [Full analysis available in comprehensive report]")
            content.append("")
        
        # Warnings
        if zscore_result.warnings:
            content.append("WARNINGS:")
            for warning in zscore_result.warnings:
                content.append(f"  • {warning}")
            content.append("")
        
        content.append("=== END OF SUMMARY ===")
        return "\n".join(content)
    
    def _format_component_values(self, component_values: Dict[str, float]) -> Dict[str, str]:
        """Format component values for display with proper number formatting."""
        formatted = {}
        for component, value in component_values.items():
            # Skip non-numeric values (like metadata)
            if not isinstance(value, (int, float)) or component.startswith('_'):
                continue
            formatted_name = self._format_component_name(component)
            formatted_value = self._format_number(value)
            formatted[formatted_name] = formatted_value
        return formatted
    
    def _format_component_name(self, component_name: str) -> str:
        """Format component names to be more user-friendly."""
        # Component name mapping for better readability
        name_mapping = {
            'working_capital_to_total_assets': 'Working Capital / Total Assets',
            'retained_earnings_to_total_assets': 'Retained Earnings / Total Assets', 
            'ebit_to_total_assets': 'EBIT / Total Assets',
            'market_value_equity_to_total_liabilities': 'Market Value Equity / Total Liabilities',
            'sales_to_total_assets': 'Sales / Total Assets',
            'book_value_equity_to_total_liabilities': 'Book Value Equity / Total Liabilities'
        }
        
        return name_mapping.get(component_name, component_name.replace('_', ' ').title())
    
    def _format_number(self, value: float) -> str:
        """Format numbers for better readability."""
        if value is None:
            return "N/A"
        
        # Handle very small numbers (close to zero)
        if abs(value) < 0.0001:
            return "0.0000"
        
        # Handle large numbers
        if abs(value) >= 1000:
            return f"{value:,.1f}"
        
        # Handle regular numbers with appropriate decimal places
        if abs(value) >= 10:
            return f"{value:.2f}"
        elif abs(value) >= 1:
            return f"{value:.3f}"
        else:
            return f"{value:.4f}"
    
    def _format_currency(self, value: float, suffix: str = "") -> str:
        """Format currency values with proper comma separators."""
        if value is None:
            return "N/A"
        
        # Handle very large numbers (billions)
        if suffix and value >= 1:
            return f"{value:,.1f}{suffix}"
        elif value >= 1000:
            return f"{value:,.2f}"
        else:
            return f"{value:.2f}"
    
    def _format_percentage(self, value: float) -> str:
        """Format percentage values consistently."""
        if value is None:
            return "N/A"
        return f"{value:.1f}"
    
    def _get_risk_class(self, z_score: float) -> str:
        """Get CSS risk class based on Z-Score."""
        if z_score > 2.99:
            return "risk-low"
        elif z_score > 1.8:
            return "risk-medium"
        else:
            return "risk-high"
    
    def _format_investment_rating(self, rating: str) -> str:
        """Format investment rating for display."""
        rating_map = {
            'STRONG_BUY': 'Strong Buy',
            'BUY': 'Buy',
            'HOLD': 'Hold',
            'SELL': 'Sell',
            'STRONG_SELL': 'Strong Sell'
        }
        return rating_map.get(rating.upper(), rating.title())
    
    def _get_recommendation_class(self, rating: str) -> str:
        """Get CSS class for recommendation styling."""
        rating = rating.upper()
        if rating in ['STRONG_BUY', 'BUY']:
            return "buy"
        elif rating in ['STRONG_SELL', 'SELL']:
            return "sell"
        else:
            return "hold"
    
    def _get_model_thresholds(self, model_used: str) -> Dict[str, str]:
        """Get model-specific thresholds for display."""
        try:
            model_key = model_used.lower().replace(" ", "_").replace("-", "_").replace("'", "").replace('"', "")
            if model_key in ZSCORE_MODELS:
                thresholds = ZSCORE_MODELS[model_key]["thresholds"]
                return {
                    'safe': f"{thresholds['safe']:.2f}",
                    'gray_zone_upper': f"{thresholds['grey_upper']:.2f}",
                    'gray_zone_lower': f"{thresholds['grey_lower']:.2f}",
                    'distress': f"{thresholds['distress']:.2f}"
                }
            else:
                # Fallback for unknown models
                return {
                    'safe': "2.99",
                    'gray_zone_upper': "2.99", 
                    'gray_zone_lower': "1.81",
                    'distress': "1.81"
                }
        except Exception as e:
            logger.warning(f"Could not retrieve thresholds for model {model_used}: {e}")
            return {
                'safe': "N/A",
                'gray_zone_upper': "N/A",
                'gray_zone_lower': "N/A", 
                'distress': "N/A"
            }
    
    def _get_model_description(self, model_used: str) -> str:
        """Get model description for display."""
        try:
            model_key = model_used.lower().replace(" ", "_").replace("-", "_").replace("'", "").replace('"', "")
            if model_key in ZSCORE_MODELS:
                return ZSCORE_MODELS[model_key]["description"]
            else:
                return f"Z-Score model: {model_used}"
        except Exception as e:
            logger.warning(f"Could not retrieve description for model {model_used}: {e}")
            return f"Z-Score model: {model_used}"
    
    def _get_company_name(self, zscore_result: ZScoreCalculationResult) -> str:
        """Extract company name from Z-Score result metadata or provide fallback."""
        try:
            # Try to get company name from metadata
            if hasattr(zscore_result, 'metadata') and zscore_result.metadata:
                company_name = zscore_result.metadata.get('company_name')
                if company_name:
                    return company_name
            
            # If no company name in metadata, use ticker as fallback
            return zscore_result.ticker
            
        except Exception as e:
            logger.warning(f"Could not extract company name for {zscore_result.ticker}: {e}")
            return zscore_result.ticker
    
    def _get_logo_path(self, zscore_result: ZScoreCalculationResult, output_dir: Path) -> Optional[str]:
        """Copy company logo to output directory and return local path."""
        try:
            if not hasattr(zscore_result, 'metadata') or not zscore_result.metadata:
                return None
            
            # First try to use cached logo file if available
            logo_file_path = zscore_result.metadata.get('logo_file_path')
            if logo_file_path and Path(logo_file_path).exists():
                # Copy from cache to output directory
                try:
                    import shutil
                    logo_filename = f"{zscore_result.ticker}_logo.png"
                    output_logo_path = output_dir / logo_filename
                    
                    shutil.copy2(logo_file_path, output_logo_path)
                    logger.info(f"Copied cached logo for {zscore_result.ticker} to {output_logo_path}")
                    return logo_filename  # Return relative path for HTML
                    
                except Exception as e:
                    logger.warning(f"Failed to copy cached logo for {zscore_result.ticker}: {e}")
            
            # Fallback to logo URL (for backward compatibility)
            logo_url = zscore_result.metadata.get('logo_url')
            if logo_url:
                logger.debug(f"Using logo URL for {zscore_result.ticker}: {logo_url}")
                return logo_url
        
        except Exception as e:
            logger.debug(f"Could not get logo for {zscore_result.ticker}: {e}")
        
        # Return None if no logo available (template will handle gracefully)
        return None
    
    def _format_calculation_date(self, calculation_timestamp: str) -> str:
        """Format calculation timestamp for better display."""
        try:
            # Parse ISO format timestamp
            if 'T' in calculation_timestamp:
                dt = datetime.fromisoformat(calculation_timestamp.replace('Z', '+00:00'))
            else:
                # Try parsing as simple date
                dt = datetime.strptime(calculation_timestamp, "%Y-%m-%d")
            
            # Format as readable date
            return dt.strftime("%B %d, %Y at %I:%M %p")
            
        except Exception as e:
            logger.warning(f"Could not parse calculation date {calculation_timestamp}: {e}")
            return calculation_timestamp
        
    def _extract_executive_summary(self, ai_analysis) -> Optional[str]:
        """Extract executive summary from AI analysis commentary."""
        try:
            if not ai_analysis or not hasattr(ai_analysis, 'llm_final_commentary'):
                return None
            
            commentary = ai_analysis.llm_final_commentary
            if not commentary:
                return None
            
            # Look for executive summary section
            lines = commentary.split('\n')
            summary_lines = []
            capture = False
            
            for line in lines:
                line = line.strip()
                if 'executive summary' in line.lower():
                    capture = True
                    continue
                elif line.startswith('#') and capture:
                    break
                elif capture and line and not line.startswith('---'):
                    summary_lines.append(line)
                    if len(summary_lines) >= 5:  # Limit to first 5 paragraphs
                        break
            
            if summary_lines:
                return ' '.join(summary_lines)
            
            # Fallback: extract first meaningful paragraph
            for line in lines:
                line = line.strip()
                if len(line) > 100 and not line.startswith('#') and not line.startswith('---'):
                    return line[:500] + "..." if len(line) > 500 else line
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract executive summary: {e}")
            return None
    
    def _extract_key_insights(self, ai_analysis) -> List[str]:
        """Extract key insights from AI analysis."""
        try:
            if not ai_analysis or not hasattr(ai_analysis, 'llm_final_commentary'):
                return []
            
            commentary = ai_analysis.llm_final_commentary
            if not commentary:
                return []
            
            insights = []
            
            # Extract from AI recommendations
            if hasattr(ai_analysis, 'ai_recommendations'):
                recommendations = getattr(ai_analysis, 'ai_recommendations', [])
                insights.extend(recommendations[:3])  # Top 3 recommendations
            
            # Extract key points from commentary
            lines = commentary.split('\n')
            for line in lines:
                line = line.strip()
                # Look for bullet points or numbered insights
                if (line.startswith('- ') or line.startswith('• ') or 
                    line.startswith('*') or line.startswith('Key')):
                    clean_line = line.lstrip('- •*').strip()
                    if len(clean_line) > 20 and len(clean_line) < 200:
                        insights.append(clean_line)
                        if len(insights) >= 5:
                            break
            
            return insights[:5]  # Limit to top 5 insights
            
        except Exception as e:
            logger.warning(f"Failed to extract key insights: {e}")
            return []
    
    def _extract_investment_thesis(self, ai_analysis) -> Optional[str]:
        """Extract investment thesis from AI analysis."""
        try:
            if not ai_analysis or not hasattr(ai_analysis, 'llm_final_commentary'):
                return None
            
            commentary = ai_analysis.llm_final_commentary
            if not commentary:
                return None
            
            # Look for investment thesis section
            lines = commentary.split('\n')
            thesis_lines = []
            capture = False
            
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['investment thesis', 'recommendation', 'investment stance']):
                    capture = True
                    if ':' in line:
                        thesis_lines.append(line.split(':', 1)[1].strip())
                    continue
                elif line.startswith('#') and capture:
                    break
                elif capture and line and not line.startswith('---'):
                    thesis_lines.append(line)
                    if len(thesis_lines) >= 3:  # Limit to 3 sentences
                        break
            
            if thesis_lines:
                return ' '.join(thesis_lines)
            
            # Fallback: look for conclusion or summary
            for i, line in enumerate(lines):
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['conclusion', 'overall', 'based on']):
                    # Take this line and next few lines
                    thesis_lines = [line]
                    for j in range(i+1, min(i+3, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('#'):
                            thesis_lines.append(next_line)
                        else:
                            break
                    return ' '.join(thesis_lines)
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract investment thesis: {e}")
            return None
