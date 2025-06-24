"""
Report Generator - Create comprehensive analysis reports

This module generates detailed HTML and text reports combining Z-Score analysis
with AI-powered insights and recommendations.

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

from ...common.logging_config import get_logger
from ...common.exceptions import OutputGenerationError
from ..zscore_calculation import ZScoreCalculationResult

logger = get_logger(__name__)


class ReportGenerator:
    """Generator for comprehensive analysis reports."""
    
    def __init__(self, output_base_path: str = "output"):
        """
        Initialize report generator.
        
        Args:
            output_base_path: Base directory for output files        """
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(
        self, 
        zscore_result: ZScoreCalculationResult,
        ai_insights: Optional[str] = None,
        market_analysis = None
    ) -> str:
        """
        Generate comprehensive HTML report enhanced with market analysis.
        
        Args:
            zscore_result: Z-Score calculation result
            ai_insights: Optional AI-generated insights
            market_analysis: Optional market analysis results for enhanced insights
            
        Returns:
            str: Path to generated HTML report
        """
        try:
            ticker_dir = self.output_base_path / zscore_result.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            report_path = ticker_dir / f"{zscore_result.ticker}_comprehensive_report.html"
              # Generate report content
            html_content = self._generate_html_report(zscore_result, ai_insights, market_analysis)
            
            # Write HTML file
            with open(report_path, 'w', encoding='utf-8') as report_file:
                report_file.write(html_content)
            
            logger.info(f"Comprehensive report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            error_msg = f"Failed to generate report for {zscore_result.ticker}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def generate_summary_report(self, zscore_result: ZScoreCalculationResult, market_analysis=None) -> str:
        """
        Generate concise text summary report enhanced with market analysis.
        
        Args:
            zscore_result: Z-Score calculation result
            market_analysis: Optional market analysis results for enhanced insights
            
        Returns:
            str: Path to generated text report
        """
        try:
            ticker_dir = self.output_base_path / zscore_result.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            summary_path = ticker_dir / f"{zscore_result.ticker}_summary.txt"
              # Generate summary content
            summary_content = self._generate_summary_content(zscore_result, market_analysis)
            
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
        market_analysis = None    ) -> str:
        """Generate HTML report content enhanced with market analysis."""
        
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Altman Z-Score Analysis - {{ ticker }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .risk-high { background-color: #ffebee; border-left: 4px solid #f44336; }
        .risk-medium { background-color: #fff3e0; border-left: 4px solid #ff9800; }
        .risk-low { background-color: #e8f5e8; border-left: 4px solid #4caf50; }
        .market-section { background-color: #f8f9fa; border-left: 4px solid #007bff; }
        .recommendation { background-color: #e7f3ff; border: 2px solid #007bff; padding: 15px; border-radius: 8px; text-align: center; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .metric { background: #f5f5f5; padding: 10px; border-radius: 4px; text-align: center; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; }
        .buy { color: #28a745; font-weight: bold; }
        .sell { color: #dc3545; font-weight: bold; }
        .hold { color: #ffc107; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Enhanced Investment Analysis Report</h1>
        <h2>{{ ticker }} - {{ calculation_date }}</h2>
        {% if market_analysis %}
        <p>Complete analysis with Z-Score + Market Intelligence</p>
        {% else %}
        <p>Z-Score Financial Health Analysis</p>
        {% endif %}
    </div>
    
    {% if market_analysis %}
    <div class="section recommendation">
        <h2>Investment Recommendation</h2>
        <div style="font-size: 1.5em; margin: 10px 0;">
            <span class="{{ recommendation_class }}">{{ recommendation_action }}</span>
        </div>
        <p>Confidence: {{ recommendation_confidence }}%</p>
        <p><em>{{ recommendation_rationale }}</em></p>
    </div>
    {% endif %}
    
    <div class="section {{ risk_class }}">
        <h2>Z-Score Summary</h2>
        <div class="metrics">
            <div class="metric">
                <h3>Z-Score</h3>
                <p style="font-size: 2em; font-weight: bold;">{{ z_score }}</p>
            </div>
            <div class="metric">
                <h3>Risk Category</h3>
                <p style="font-size: 1.5em;">{{ risk_category }}</p>
            </div>
            <div class="metric">
                <h3>Model Used</h3>
                <p>{{ model_used }}</p>
            </div>
            <div class="metric">
                <h3>Data Quality</h3>
                <p>{{ data_quality_score }}%</p>
            </div>
        </div>
    </div>
    
    {% if market_analysis %}
    <div class="section market-section">
        <h2>Market Analysis Summary</h2>
        <div class="metrics">
            <div class="metric">
                <h4>Current Price</h4>
                <p>${{ current_price }}</p>
            </div>
            <div class="metric">
                <h4>Market Cap</h4>
                <p>${{ market_cap }}</p>
            </div>
            <div class="metric">
                <h4>P/E Ratio</h4>
                <p>{{ pe_ratio }}</p>
            </div>
            <div class="metric">
                <h4>1Y Return</h4>
                <p>{{ return_1y }}%</p>
            </div>
            <div class="metric">
                <h4>Volatility</h4>
                <p>{{ volatility }}%</p>
            </div>
            <div class="metric">
                <h4>RSI</h4>
                <p>{{ rsi }}</p>
            </div>
        </div>
    </div>
    
    <div class="section market-section">
        <h2>Technical Analysis</h2>
        <div class="metrics">
            <div class="metric">
                <h4>MACD Signal</h4>
                <p>{{ macd_signal }}</p>
            </div>
            <div class="metric">
                <h4>Bollinger Signal</h4>
                <p>{{ bollinger_signal }}</p>
            </div>
            <div class="metric">
                <h4>Momentum Score</h4>
                <p>{{ momentum_score }}/10</p>
            </div>
            <div class="metric">
                <h4>Technical Trend</h4>
                <p>{{ technical_trend }}</p>
            </div>
        </div>
    </div>
    
    <div class="section market-section">
        <h2>Performance Analysis</h2>
        <div class="metrics">
            <div class="metric">
                <h4>1 Day</h4>
                <p>{{ return_1d }}%</p>
            </div>
            <div class="metric">
                <h4>1 Week</h4>
                <p>{{ return_5d }}%</p>
            </div>
            <div class="metric">
                <h4>1 Month</h4>
                <p>{{ return_1m }}%</p>
            </div>
            <div class="metric">
                <h4>3 Months</h4>
                <p>{{ return_3m }}%</p>
            </div>
            <div class="metric">
                <h4>6 Months</h4>
                <p>{{ return_6m }}%</p>
            </div>
            <div class="metric">
                <h4>1 Year</h4>
                <p>{{ return_1y }}%</p>
            </div>
        </div>
    </div>
    
    <div class="section market-section">
        <h2>Risk Assessment</h2>
        <div class="metrics">
            <div class="metric">
                <h4>Beta</h4>
                <p>{{ beta }}</p>
            </div>
            <div class="metric">
                <h4>Sharpe Ratio</h4>
                <p>{{ sharpe_ratio }}</p>
            </div>
            <div class="metric">
                <h4>Max Drawdown</h4>
                <p>{{ max_drawdown }}%</p>
            </div>
            <div class="metric">
                <h4>Risk Score</h4>
                <p>{{ risk_score }}/10</p>
            </div>
        </div>
    </div>
    {% endif %}
    
    <div class="section">
        <h2>Component Analysis</h2>
        <div class="metrics">
            {% for component, value in component_values.items() %}
            <div class="metric">
                <h4>{{ component }}</h4>
                <p>{{ value }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
    
    {% if warnings %}
    <div class="section warning">
        <h2>Warnings & Notes</h2>
        <ul>
            {% for warning in warnings %}
            <li>{{ warning }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
    
    {% if ai_insights %}
    <div class="section">
        <h2>AI-Powered Analysis</h2>
        <div style="white-space: pre-wrap;">{{ ai_insights }}</div>
    </div>
    {% endif %}
    
    <div class="section">
        <h2>Analysis Guide</h2>
        <h3>Z-Score Risk Assessment:</h3>
        <ul>
            <li><strong>Z-Score > 2.99:</strong> Safe Zone - Low bankruptcy risk</li>
            <li><strong>1.8 < Z-Score < 2.99:</strong> Grey Zone - Moderate risk, requires monitoring</li>
            <li><strong>Z-Score < 1.8:</strong> Distress Zone - High bankruptcy risk</li>
        </ul>
        {% if market_analysis %}
        <h3>Investment Actions:</h3>
        <ul>
            <li><strong>STRONG_BUY:</strong> High conviction buy opportunity</li>
            <li><strong>BUY:</strong> Favorable risk/reward profile</li>
            <li><strong>HOLD:</strong> Maintain current position</li>
            <li><strong>SELL:</strong> Unfavorable outlook, consider reducing</li>
            <li><strong>STRONG_SELL:</strong> High conviction sell signal</li>
        </ul>
        {% endif %}
    </div>
    
    <footer style="margin-top: 40px; text-align: center; color: #666;">
        <p>Generated on {{ generation_date }} by Enhanced Altman Z-Score Analysis v3.11.0</p>
        {% if market_analysis %}
        <p><em>This report combines fundamental Z-Score analysis with comprehensive market intelligence</em></p>
        {% endif %}
    </footer>
</body>
</html>        """
        
        template = Template(template_str)
          # Determine risk class for styling
        risk_class = self._get_risk_class(zscore_result.z_score)
        
        # Prepare base template data
        template_data = {
            'ticker': zscore_result.ticker,
            'z_score': f"{zscore_result.z_score:.2f}",
            'risk_category': zscore_result.risk_category,
            'model_used': zscore_result.model_used,
            'data_quality_score': f"{zscore_result.data_quality_score:.1f}",
            'calculation_date': zscore_result.calculation_timestamp,
            'component_values': zscore_result.component_values,
            'warnings': zscore_result.warnings,
            'ai_insights': ai_insights,
            'risk_class': risk_class,
            'generation_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'market_analysis': market_analysis
        }
        
        # Add market analysis data if available
        if market_analysis:
            rec = market_analysis.investment_recommendation
            tech = market_analysis.technical_analysis
            val = market_analysis.valuation_analysis  
            perf = market_analysis.performance_analysis
            risk = market_analysis.risk_analysis
            
            template_data.update({
                'recommendation_action': rec.action,
                'recommendation_confidence': f"{rec.confidence * 100:.1f}",
                'recommendation_rationale': rec.rationale,
                'recommendation_class': self._get_recommendation_class(rec.action),
                'current_price': f"{val.current_price:.2f}" if val.current_price else "N/A",
                'market_cap': f"{val.market_cap / 1e9:.1f}B" if val.market_cap else "N/A",
                'pe_ratio': f"{val.pe_ratio:.1f}" if val.pe_ratio else "N/A",
                'return_1y': f"{perf.return_1y * 100:.1f}" if perf.return_1y else "N/A",
                'volatility': f"{risk.volatility_1y * 100:.1f}" if risk.volatility_1y else "N/A",
                'rsi': f"{tech.rsi_14:.1f}" if tech.rsi_14 else "N/A",
                'macd_signal': tech.macd_signal or "N/A",
                'bollinger_signal': tech.bollinger_signal or "N/A",
                'momentum_score': f"{tech.momentum_score * 10:.1f}" if tech.momentum_score else "N/A",
                'technical_trend': tech.trend_direction or "N/A",
                'return_1d': f"{perf.return_1d * 100:.2f}" if perf.return_1d else "N/A",
                'return_5d': f"{perf.return_5d * 100:.2f}" if perf.return_5d else "N/A",
                'return_1m': f"{perf.return_1m * 100:.1f}" if perf.return_1m else "N/A",
                'return_3m': f"{perf.return_3m * 100:.1f}" if perf.return_3m else "N/A",
                'return_6m': f"{perf.return_6m * 100:.1f}" if perf.return_6m else "N/A",
                'beta': f"{risk.beta:.2f}" if risk.beta else "N/A",
                'sharpe_ratio': f"{risk.sharpe_ratio:.2f}" if risk.sharpe_ratio else "N/A",
                'max_drawdown': f"{risk.max_drawdown * 100:.1f}" if risk.max_drawdown else "N/A",
                'risk_score': f"{risk.risk_score * 10:.1f}" if risk.risk_score else "N/A"            })
        
        return template.render(**template_data)
    
    def _generate_summary_content(self, zscore_result: ZScoreCalculationResult, market_analysis=None) -> str:
        """Generate text summary content enhanced with market analysis."""
        content = []
        content.append(f"ENHANCED INVESTMENT ANALYSIS SUMMARY")
        content.append(f"=" * 45)
        content.append(f"Ticker: {zscore_result.ticker}")
        content.append(f"Analysis Date: {zscore_result.calculation_timestamp}")
        content.append("")
        
        # Investment Recommendation (if available)
        if market_analysis:
            rec = market_analysis.investment_recommendation
            content.append("INVESTMENT RECOMMENDATION:")
            content.append("-" * 25)
            content.append(f"Action: {rec.action}")
            content.append(f"Confidence: {rec.confidence * 100:.1f}%")
            content.append(f"Rationale: {rec.rationale}")
            content.append("")
        
        # Z-Score Analysis
        content.append("Z-SCORE ANALYSIS:")
        content.append("-" * 18)
        content.append(f"Z-Score: {zscore_result.z_score:.2f}")
        content.append(f"Risk Category: {zscore_result.risk_category}")
        content.append(f"Model Used: {zscore_result.model_used}")
        content.append(f"Data Quality: {zscore_result.data_quality_score:.1f}%")
        content.append("")
        
        # Market Analysis Summary (if available)
        if market_analysis:
            val = market_analysis.valuation_analysis
            perf = market_analysis.performance_analysis
            risk = market_analysis.risk_analysis
            tech = market_analysis.technical_analysis
            
            content.append("MARKET ANALYSIS SUMMARY:")
            content.append("-" * 24)
            content.append(f"Current Price: ${val.current_price:.2f}" if val.current_price else "Current Price: N/A")
            content.append(f"Market Cap: ${val.market_cap / 1e9:.1f}B" if val.market_cap else "Market Cap: N/A")
            content.append(f"P/E Ratio: {val.pe_ratio:.1f}" if val.pe_ratio else "P/E Ratio: N/A")
            content.append(f"1Y Return: {perf.return_1y * 100:.1f}%" if perf.return_1y else "1Y Return: N/A")
            content.append(f"Volatility: {risk.volatility_1y * 100:.1f}%" if risk.volatility_1y else "Volatility: N/A")
            content.append(f"RSI: {tech.rsi_14:.1f}" if tech.rsi_14 else "RSI: N/A")
            content.append(f"Beta: {risk.beta:.2f}" if risk.beta else "Beta: N/A")
            content.append("")
        
        content.append("COMPONENT BREAKDOWN:")
        content.append("-" * 20)
        for component, value in zscore_result.component_values.items():
            content.append(f"{component}: {value}")
        
        if zscore_result.warnings:
            content.append("")
            content.append("WARNINGS:")
            content.append("-" * 10)
            for warning in zscore_result.warnings:
                content.append(f"• {warning}")
        
        content.append("")
        content.append(f"Generated: {datetime.now()}")
        
        return "\n".join(content)
    
    def _get_risk_class(self, z_score: float) -> str:
        """Get CSS class based on risk level."""
        if z_score < 1.8:
            return "risk-high"
        elif z_score < 2.99:
            return "risk-medium"
        else:
            return "risk-low"
    
    def _get_recommendation_class(self, action: str) -> str:
        """Get CSS class based on recommendation action."""
        if action in ['STRONG_BUY', 'BUY']:
            return "buy"
        elif action in ['STRONG_SELL', 'SELL']:
            return "sell"
        else:
            return "hold"
