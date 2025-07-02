#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
import logging

# Import the assets manager to ensure the assets folder is populated
from assets_manager import ensure_assets_folder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Path handling - script now in utilities folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
WEB_DIR = os.path.join(PROJECT_ROOT, "web")
WEB_ASSETS_DIR = os.path.join(WEB_DIR, "assets")
HTML_OUTPUT = os.path.join(WEB_DIR, "index.html")
CSS_FILE = os.path.join(WEB_ASSETS_DIR, "dashboard_styles.css")
TEMPLATE_FILE = os.path.join(WEB_ASSETS_DIR, "index_template.html")

# Ensure web directory exists
os.makedirs(WEB_DIR, exist_ok=True)
logger.info(f"Using web directory: {WEB_DIR}")

def load_and_embed_css():
    """Load CSS content for embedding."""
    try:
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            css_content = f.read()
        return css_content
    except Exception as e:
        logger.warning(f"Could not load CSS file {CSS_FILE}: {str(e)}")
        # Return minimal CSS as fallback
        return """
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a5276; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .dashboard-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: white; }
        """

def get_dashboard_stats():
    """
    Check which dashboard files exist and get basic stats from each.
    """
    dashboards = {
        # Investor Profile Dashboards
        "strong_buys.html": {
            "title": "Strong Buy Recommendations",
            "description": "Companies with the highest confidence buy recommendations",
            "icon": "🚀",
            "color": "#27ae60",
            "category": "buy"
        },
        "conservative_picks.html": {
            "title": "Conservative Investor Picks",
            "description": "Safe, stable companies for risk-averse investors",
            "icon": "🛡️",
            "color": "#3498db",
            "category": "profile"
        },
        "dividend_picks.html": {
            "title": "Dividend Investor Picks",
            "description": "Income-focused stocks with reliable dividend yields",
            "icon": "💰",
            "color": "#f39c12",
            "category": "profile"
        },
        "value_picks.html": {
            "title": "Value Investor Picks",
            "description": "Undervalued companies with strong fundamentals",
            "icon": "💎",
            "color": "#9b59b6",
            "category": "profile"
        },
        "growth_picks.html": {
            "title": "Growth Investor Picks",
            "description": "High-growth potential companies for capital appreciation",
            "icon": "📈",
            "color": "#e67e22",
            "category": "profile"
        },
        "aggressive_picks.html": {
            "title": "Aggressive Investor Picks",
            "description": "High-risk, high-reward investment opportunities",
            "icon": "🔥",
            "color": "#e74c3c",
            "category": "profile"
        },
        "sell_picks.html": {
            "title": "Sell Recommendations",
            "description": "Companies with concerning financial indicators",
            "icon": "⚠️",
            "color": "#c0392b",
            "category": "sell"
        },
        "strong_sell_picks.html": {
            "title": "Strong Sell Recommendations",
            "description": "Companies in severe financial distress - avoid these",
            "icon": "🚨",
            "color": "#7f0000",
            "category": "sell"
        },
        
        # Industry-Specific Model Portfolios - support both naming conventions
        "manufacturing_&_industrial.html": {
            "title": "Manufacturing & Industrial",
            "description": "Traditional manufacturing firms using original Altman Z-Score",
            "icon": "🏭",
            "color": "#34495e",
            "category": "industry"
        },
        "manufacturing__and__industrial.html": {  # Alternative naming
            "title": "Manufacturing & Industrial",
            "description": "Traditional manufacturing firms using original Altman Z-Score",
            "icon": "🏭",
            "color": "#34495e",
            "category": "industry"
        },
        "private_&_service_companies.html": {
            "title": "Private & Service Companies",
            "description": "Service companies using Z'-Score adaptation",
            "icon": "🏢",
            "color": "#2980b9",
            "category": "industry"
        },
        "private__and__service_companies.html": {  # Alternative naming
            "title": "Private & Service Companies",
            "description": "Service companies using Z'-Score adaptation",
            "icon": "🏢",
            "color": "#2980b9",
            "category": "industry"
        },
        "emerging_markets.html": {
            "title": "Emerging Markets",
            "description": "Non-US and emerging market companies with Z\"-Score",
            "icon": "🌏",
            "color": "#16a085",
            "category": "industry"
        },
        "financial_institutions.html": {
            "title": "Financial Institutions",
            "description": "Banks and financial institutions using CAMELS framework",
            "icon": "🏦",
            "color": "#8e44ad",
            "category": "industry"
        },
        "regulated_utilities.html": {
            "title": "Regulated Utilities",
            "description": "Utility companies with stable cash flows",
            "icon": "⚡",
            "color": "#d35400",
            "category": "industry"
        },
        "technology_&_growth.html": {
            "title": "Technology & Growth",
            "description": "High-growth tech companies with significant R&D",
            "icon": "💻",
            "color": "#2c3e50",
            "category": "industry"
        },
        "technology__and__growth.html": {  # Alternative naming
            "title": "Technology & Growth",
            "description": "High-growth tech companies with significant R&D",
            "icon": "💻",
            "color": "#2c3e50",
            "category": "industry"
        },
        "retail_&_consumer.html": {
            "title": "Retail & Consumer",
            "description": "Retail companies with seasonal patterns and inventory focus",
            "icon": "🛍️",
            "color": "#c0392b",
            "category": "industry"
        },
        "retail__and__consumer.html": {  # Alternative naming
            "title": "Retail & Consumer",
            "description": "Retail companies with seasonal patterns and inventory focus",
            "icon": "🛍️",
            "color": "#c0392b",
            "category": "industry"
        }
    }
    
    available_dashboards = []
    
    for filename, info in dashboards.items():
        filepath = os.path.join(WEB_DIR, filename)
        if os.path.exists(filepath):
            # Try to extract company count from the file
            company_count = 0
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for common patterns that indicate company count
                count_patterns = [
                    r'<div class="stat-number">(\d+)</div>\s*<div class="stat-label">Companies</div>',
                    r'(\d+)\s+Companies',
                    r'Companies Analyzed.*?(\d+)',
                    r'Companies Flagged.*?(\d+)',
                    r'Critical Alerts.*?(\d+)',
                    r'data-ticker="[^"]*"'  # Count data-ticker occurrences as fallback
                ]
                
                for pattern in count_patterns[:-1]:  # Try text patterns first
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        company_count = int(match.group(1))
                        break
                
                # Fallback: count data-ticker occurrences
                if company_count == 0:
                    ticker_matches = re.findall(count_patterns[-1], content)
                    company_count = len(ticker_matches)
                    
            except Exception as e:
                logger.warning(f"Could not extract company count from {filename}: {str(e)}")
            
            info["company_count"] = company_count
            info["filename"] = filename
            available_dashboards.append(info)
    
    return available_dashboards

def generate_dashboard_sections(dashboards):
    """Generate HTML for all dashboard sections."""
    buy_dashboards = [d for d in dashboards if d["category"] == "buy"]
    profile_dashboards = [d for d in dashboards if d["category"] == "profile"]
    sell_dashboards = [d for d in dashboards if d["category"] == "sell"]
    industry_dashboards = [d for d in dashboards if d["category"] == "industry"]

    def create_dashboard_card(dashboard):
        return f"""
        <div class="dashboard-card">
            <h3 class="dashboard-title">{dashboard['title']}</h3>
            <p class="dashboard-description">{dashboard['description']}</p>
            <div class="company-count">{dashboard['company_count']} Companies</div>
            <a href="{dashboard['filename']}" class="view-dashboard">View Dashboard</a>
        </div>
        """

    sections = {
        "{{BUY_DASHBOARDS}}": "\n".join(create_dashboard_card(d) for d in buy_dashboards),
        "{{PROFILE_DASHBOARDS}}": "\n".join(create_dashboard_card(d) for d in profile_dashboards),
        "{{SELL_DASHBOARDS}}": "\n".join(create_dashboard_card(d) for d in sell_dashboards),
        "{{INDUSTRY_DASHBOARDS}}": "\n".join(create_dashboard_card(d) for d in industry_dashboards)
    }

    return sections

def generate_overview_stats(dashboards):
    """Generate overview statistics section."""
    stats = {
        'total_companies': sum(d.get('company_count', 0) for d in dashboards),
        'buy_signals': sum(d.get('company_count', 0) for d in dashboards if d['category'] == 'buy'),
        'sell_signals': sum(d.get('company_count', 0) for d in dashboards if d['category'] == 'sell'),
        'industries': len([d for d in dashboards if d['category'] == 'industry'])
    }

    return f"""
    <div class="dashboard-card">
        <p class="stat-number">{stats['total_companies']:,}</p>
        <p class="stat-label">Companies Analyzed</p>
    </div>
    <div class="dashboard-card">
        <p class="stat-number">{stats['buy_signals']}</p>
        <p class="stat-label">Strong Buy Signals</p>
    </div>
    <div class="dashboard-card">
        <p class="stat-number">{stats['sell_signals']}</p>
        <p class="stat-label">Strong Sell Signals</p>
    </div>
    <div class="dashboard-card">
        <p class="stat-number">{stats['industries']}</p>
        <p class="stat-label">Industries Monitored</p>
    </div>
    """

def generate_main_page(dashboards):
    """Generate the main navigation page."""
    # Ensure the assets directory exists
    os.makedirs(WEB_ASSETS_DIR, exist_ok=True)
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Load template and embed CSS
    css_content = load_and_embed_css()
    embedded_css = f"<style>\n{css_content}\n</style>"
    
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Replace CSS link with embedded CSS
        template_content = template_content.replace(
            '<link rel="stylesheet" href="assets/dashboard_styles.css">',
            embedded_css
        )
        
        # Generate all sections
        sections = generate_dashboard_sections(dashboards)
        
        # Add overview stats
        sections["{{OVERVIEW_STATS}}"] = generate_overview_stats(dashboards)
        
        # Add date and version
        sections["{{GENERATION_DATE}}"] = current_date
        sections["{{VERSION}}"] = "v4.5.1"  # TODO: Get from version file
        
        # Replace all placeholders
        for placeholder, content in sections.items():
            template_content = template_content.replace(placeholder, content)
            
        return template_content
        
    except Exception as e:
        logger.error(f"Error generating main page: {str(e)}")
        return None

def main():
    """
    Main execution function.
    """
    logger.info("Starting main navigation page generation...")
    
    # Ensure the assets folder exists and is populated with required files
    ensure_assets_folder()
    
    # Get available dashboards and their stats
    dashboards = get_dashboard_stats()
    
    if not dashboards:
        logger.error("No dashboard files found")
        return
    
    logger.info(f"Found {len(dashboards)} available dashboards")
    for dashboard in dashboards:
        logger.info(f"  - {dashboard['title']}: {dashboard['company_count']} companies")
    
    if generate_main_page(dashboards):
        logger.info(f"Main navigation page successfully generated at {HTML_OUTPUT}")
    
    logger.info("Process completed")

if __name__ == "__main__":
    main()
