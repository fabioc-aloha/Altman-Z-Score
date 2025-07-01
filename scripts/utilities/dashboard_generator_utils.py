#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard Generation Utilities

This module provides common functionality for generating standardized
dashboard HTML files across all dashboard types.
"""

import os
from datetime import datetime
from pathlib import Path

def get_common_paths():
    """Get common paths used across all dashboard generators."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    web_dir = project_root / "web"
    assets_dir = web_dir / "assets"
    template_path = assets_dir / "dashboard_template.html"
    
    return {
        "project_root": project_root,
        "web_dir": web_dir,
        "assets_dir": assets_dir,
        "template_path": template_path
    }

def load_dashboard_template():
    """Load the common dashboard HTML template."""
    paths = get_common_paths()
    
    try:
        with open(paths["template_path"], 'r', encoding='utf-8') as f:
            template = f.read()
        return template
    except Exception as e:
        print(f"Error loading template: {str(e)}")
        # Return a minimal template as fallback
        return """<!DOCTYPE html>
<html>
<head>
    <title>{{DASHBOARD_TITLE}}</title>
    <link rel="stylesheet" href="assets/dashboard_common.css">
</head>
<body>
    <h1>{{DASHBOARD_TITLE}}</h1>
    <div class="date">Generated: {{GENERATION_DATE}}</div>
    <div>{{COMPANY_GRID}}</div>
</body>
</html>"""

def generate_company_card_html(company):
    """
    Generate standardized HTML for a company card.
    
    Args:
        company: Dictionary containing company data with at least:
                - name: Company name
                - ticker: Stock ticker symbol
                - z_score: Altman Z-Score value
                - metrics: Dictionary of metrics to display
                - logo_path: Path to company logo (relative to web dir)
    
    Returns:
        String containing HTML for the company card
    """
    # Determine Z-Score zone class
    if company.get('z_score', 0) > 2.99:
        zone_class = "safe"
        zone_text = "Safe Zone"
    elif company.get('z_score', 0) < 1.81:
        zone_class = "distress"
        zone_text = "Distress Zone"
    else:
        zone_class = "gray"
        zone_text = "Gray Zone"
    
    # Use default logo if not provided
    logo_path = company.get('logo_path', 'assets/default_logo.png')
    
    # Generate metrics HTML
    metrics_html = ""
    for metric_name, metric_value in company.get('metrics', {}).items():
        metrics_html += f"""
        <div class="metric">
            <span class="metric-name">{metric_name}</span>
            <span class="metric-value">{metric_value}</span>
        </div>"""
    
    # Generate the company card HTML
    return f"""
    <div class="company-card" data-ticker="{company.get('ticker', '')}">
        <div class="company-header">
            <img src="{logo_path}" alt="{company.get('name', 'Company')} logo" class="company-logo">
            <div class="company-name">
                <h3>{company.get('name', 'Company')}</h3>
                <span class="company-ticker">{company.get('ticker', '')}</span>
            </div>
        </div>
        <div class="company-metrics">
            {metrics_html}
            <div class="z-score {zone_class}">
                Z-Score: {company.get('z_score', 'N/A')} ({zone_text})
            </div>
        </div>
    </div>
    """

def generate_stats_grid_html(stats):
    """
    Generate HTML for the statistics grid.
    
    Args:
        stats: Dictionary of stat_name -> stat_value
    
    Returns:
        String containing HTML for the stats grid
    """
    stats_html = ""
    for stat_name, stat_value in stats.items():
        stats_html += f"""
            <div class="stat-card">
                <div class="stat-number">{stat_value}</div>
                <div class="stat-label">{stat_name}</div>
            </div>"""
    
    return stats_html

def generate_dashboard_html(template_data):
    """
    Generate a complete dashboard HTML using the common template.
    
    Args:
        template_data: Dictionary containing template replacement values:
                      - dashboard_title: Title of the dashboard
                      - subtitle: Optional subtitle (can be empty)
                      - generation_date: Date string
                      - stats: Dictionary of statistics
                      - summary_text: Summary text HTML
                      - model_info: Optional model info HTML (can be empty)
                      - companies: List of company dictionaries
                      - additional_css: Optional additional CSS (can be empty)
                      - additional_scripts: Optional additional scripts (can be empty)
    
    Returns:
        String containing the complete dashboard HTML
    """
    template = load_dashboard_template()
    
    # Generate stats grid HTML
    stats_grid_html = generate_stats_grid_html(template_data.get('stats', {}))
    
    # Generate company grid HTML
    company_grid_html = ""
    for company in template_data.get('companies', []):
        company_grid_html += generate_company_card_html(company)
    
    # Generate subtitle HTML
    subtitle_html = ""
    if template_data.get('subtitle'):
        subtitle_html = f'<p class="subtitle">{template_data["subtitle"]}</p>'
    
    # Generate model info HTML
    model_info_html = ""
    if template_data.get('model_info'):
        model_info_html = f"""
        <div class="model-info">
            {template_data['model_info']}
        </div>"""
    
    # Replace placeholders in template
    html = template.replace('{{DASHBOARD_TITLE}}', template_data.get('dashboard_title', 'Dashboard'))
    html = html.replace('{{SUBTITLE_PLACEHOLDER}}', subtitle_html)
    html = html.replace('{{GENERATION_DATE}}', template_data.get('generation_date', datetime.now().strftime('%B %d, %Y')))
    html = html.replace('{{STATS_GRID}}', stats_grid_html)
    html = html.replace('{{SUMMARY_TEXT}}', template_data.get('summary_text', ''))
    html = html.replace('{{MODEL_INFO_PLACEHOLDER}}', model_info_html)
    html = html.replace('{{COMPANY_GRID}}', company_grid_html)
    html = html.replace('{{ADDITIONAL_CSS}}', template_data.get('additional_css', ''))
    html = html.replace('{{ADDITIONAL_SCRIPTS}}', template_data.get('additional_scripts', ''))
    
    return html
