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
            output_base_path: Base directory for output files
        """
        self.output_base_path = Path(output_base_path)
        self.output_base_path.mkdir(exist_ok=True)
    
    def generate_comprehensive_report(
        self, 
        zscore_result: ZScoreCalculationResult,
        ai_insights: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive HTML report.
        
        Args:
            zscore_result: Z-Score calculation result
            ai_insights: Optional AI-generated insights
            
        Returns:
            str: Path to generated HTML report
        """
        try:
            ticker_dir = self.output_base_path / zscore_result.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            report_path = ticker_dir / f"{zscore_result.ticker}_comprehensive_report.html"
            
            # Generate report content
            html_content = self._generate_html_report(zscore_result, ai_insights)
            
            # Write HTML file
            with open(report_path, 'w', encoding='utf-8') as report_file:
                report_file.write(html_content)
            
            logger.info(f"Comprehensive report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            error_msg = f"Failed to generate report for {zscore_result.ticker}: {str(e)}"
            logger.error(error_msg)
            raise OutputGenerationError(error_msg) from e
    
    def generate_summary_report(self, zscore_result: ZScoreCalculationResult) -> str:
        """
        Generate concise text summary report.
        
        Args:
            zscore_result: Z-Score calculation result
            
        Returns:
            str: Path to generated text report
        """
        try:
            ticker_dir = self.output_base_path / zscore_result.ticker
            ticker_dir.mkdir(exist_ok=True)
            
            summary_path = ticker_dir / f"{zscore_result.ticker}_summary.txt"
            
            # Generate summary content
            summary_content = self._generate_summary_content(zscore_result)
            
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
        ai_insights: Optional[str] = None
    ) -> str:
        """Generate HTML report content."""
        
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
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .metric { background: #f5f5f5; padding: 10px; border-radius: 4px; text-align: center; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Altman Z-Score Analysis Report</h1>
        <h2>{{ ticker }} - {{ calculation_date }}</h2>
    </div>
    
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
        <h2>Risk Assessment Guide</h2>
        <ul>
            <li><strong>Z-Score > 2.99:</strong> Safe Zone - Low bankruptcy risk</li>
            <li><strong>1.8 < Z-Score < 2.99:</strong> Grey Zone - Moderate risk, requires monitoring</li>
            <li><strong>Z-Score < 1.8:</strong> Distress Zone - High bankruptcy risk</li>
        </ul>
    </div>
    
    <footer style="margin-top: 40px; text-align: center; color: #666;">
        <p>Generated on {{ generation_date }} by Altman Z-Score Analysis v3.8.0-dev</p>
    </footer>
</body>
</html>
        """
        
        template = Template(template_str)
        
        # Determine risk class for styling
        risk_class = self._get_risk_class(zscore_result.z_score)
        
        return template.render(
            ticker=zscore_result.ticker,
            z_score=f"{zscore_result.z_score:.2f}",
            risk_category=zscore_result.risk_category,
            model_used=zscore_result.model_used,
            data_quality_score=f"{zscore_result.data_quality_score:.1f}",
            calculation_date=zscore_result.calculation_date.strftime("%Y-%m-%d %H:%M"),
            component_values=zscore_result.component_values,
            warnings=zscore_result.warnings,
            ai_insights=ai_insights,
            risk_class=risk_class,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    
    def _generate_summary_content(self, zscore_result: ZScoreCalculationResult) -> str:
        """Generate text summary content."""
        content = []
        content.append(f"ALTMAN Z-SCORE ANALYSIS SUMMARY")
        content.append(f"=" * 40)
        content.append(f"Ticker: {zscore_result.ticker}")
        content.append(f"Analysis Date: {zscore_result.calculation_date}")
        content.append("")
        content.append(f"Z-Score: {zscore_result.z_score:.2f}")
        content.append(f"Risk Category: {zscore_result.risk_category}")
        content.append(f"Model Used: {zscore_result.model_used}")
        content.append(f"Data Quality: {zscore_result.data_quality_score:.1f}%")
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
