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

def generate_main_page(dashboards):
    """
    Generate the main navigation page HTML using the external template.
    """
    # Ensure the assets directory exists
    os.makedirs(WEB_ASSETS_DIR, exist_ok=True)
    
    current_date = datetime.now().strftime("%B %d, %Y")
    total_companies = sum(d.get("company_count", 0) for d in dashboards)
    
    # Separate dashboards by category
    buy_dashboards = [d for d in dashboards if d["category"] == "buy"]
    profile_dashboards = [d for d in dashboards if d["category"] == "profile"]
    sell_dashboards = [d for d in dashboards if d["category"] == "sell"]
    industry_dashboards = [d for d in dashboards if d["category"] == "industry"]
    
    # Load template file
    try:
        with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template_content = f.read()
        logger.info(f"Successfully loaded template from {TEMPLATE_FILE}")
    except Exception as e:
        logger.error(f"Error loading template file: {str(e)}")
        # Fallback - create an empty template with placeholders
        template_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Altman Z-Score Stock Analysis Dashboard</title>
            <link rel="stylesheet" href="assets/dashboard_styles.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1 class="main-title">Altman Z-Score Analysis</h1>
                    <p class="subtitle">Comprehensive Stock Analysis Dashboard</p>
                    <p class="date">{{date}}</p>
                </header>
                
                <section class="overview-stats">
                    {{overview_stats}}
                </section>

                {{content}}

                <footer class="footer">
                    <p class="footer-text">Altman Z-Score Analysis Dashboard Suite</p>
                    <p class="footer-text">Last Updated: {{date}}</p>
                    <p class="disclaimer">
                        This analysis is for informational purposes only and should not be considered financial advice. 
                        Always consult with a qualified financial advisor before making investment decisions.
                    </p>
                </footer>
            </div>
        </body>
        </html>
        """
        logger.warning("Using fallback template")
    
    # Generate the overview stats HTML
    overview_stats_html = f"""
            <div class="stat-card">
                <div class="stat-number">{len(dashboards)}</div>
                <div class="stat-label">Available Dashboards</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_companies}</div>
                <div class="stat-label">Total Companies Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(profile_dashboards)}</div>
                <div class="stat-label">Investor Profiles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(buy_dashboards)}</div>
                <div class="stat-label">Buy Recommendations</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(sell_dashboards)}</div>
                <div class="stat-label">Sell Recommendations</div>
            </div>
    """
    
    # We no longer need to build the content_html variable here
    # The HTML for each dashboard category will be generated 
    # directly for the specific template placeholders

    # Generate HTML for each dashboard category
    buy_html = ""
    if buy_dashboards:
        for dashboard in buy_dashboards:
            buy_html += f"""<a href="{dashboard['filename']}" class="dashboard-card buy-category">
                <div class="card-header">
                    <span class="card-icon">{dashboard['icon']}</span>
                    <h3 class="card-title">{dashboard['title']}</h3>
                    <p class="card-count">{dashboard['company_count']} Companies</p>
                </div>
                <div class="card-body">
                    <p class="card-description">{dashboard['description']}</p>
                    <button class="card-button">View Dashboard</button>
                </div>
            </a>"""
    else:
        buy_html = '<div class="empty-section">No buy recommendation dashboards available at this time.</div>'
    
    profile_html = ""
    if profile_dashboards:
        for dashboard in profile_dashboards:
            profile_html += f"""<a href="{dashboard['filename']}" class="dashboard-card profile-category">
                <div class="card-header">
                    <span class="card-icon">{dashboard['icon']}</span>
                    <h3 class="card-title">{dashboard['title']}</h3>
                    <p class="card-count">{dashboard['company_count']} Companies</p>
                </div>
                <div class="card-body">
                    <p class="card-description">{dashboard['description']}</p>
                    <button class="card-button">View Dashboard</button>
                </div>
            </a>"""
    else:
        profile_html = '<div class="empty-section">Investor profile dashboards will be available soon. Run the portfolio generation scripts to create them.</div>'
    
    sell_html = ""
    if sell_dashboards:
        for dashboard in sell_dashboards:
            sell_html += f"""<a href="{dashboard['filename']}" class="dashboard-card sell-category">
                <div class="card-header">
                    <span class="card-icon">{dashboard['icon']}</span>
                    <h3 class="card-title">{dashboard['title']}</h3>
                    <p class="card-count">{dashboard['company_count']} Companies</p>
                </div>
                <div class="card-body">
                    <p class="card-description">{dashboard['description']}</p>
                    <button class="card-button">View Dashboard</button>
                </div>
            </a>"""
    else:
        sell_html = '<div class="empty-section">No sell recommendation dashboards available at this time.</div>'
    
    industry_html = ""
    if industry_dashboards:
        for dashboard in industry_dashboards:
            # Display "New Model" for industry dashboards with 0 companies (likely templates or newly created)
            company_text = "New Model" if dashboard['company_count'] == 0 else f"{dashboard['company_count']} Companies"
            industry_html += f"""<a href="{dashboard['filename']}" class="dashboard-card industry-category">
                <div class="card-header">
                    <span class="card-icon">{dashboard['icon']}</span>
                    <h3 class="card-title">{dashboard['title']}</h3>
                    <p class="card-count">{company_text}</p>
                </div>
                <div class="card-body">
                    <p class="card-description">{dashboard['description']}</p>
                    <button class="card-button">View Dashboard</button>
                </div>
            </a>"""
    else:
        industry_html = '<div class="empty-section">Industry-specific model portfolios will be available soon. Run the model portfolio generation scripts to create them.</div>'
    
    # Replace placeholders in the template with actual content
    html_output = template_content.replace("{{GENERATION_DATE}}", current_date)
    html_output = html_output.replace("{{OVERVIEW_STATS}}", overview_stats_html)
    html_output = html_output.replace("{{BUY_DASHBOARDS}}", buy_html)
    html_output = html_output.replace("{{PROFILE_DASHBOARDS}}", profile_html)
    html_output = html_output.replace("{{SELL_DASHBOARDS}}", sell_html)
    html_output = html_output.replace("{{INDUSTRY_DASHBOARDS}}", industry_html)
    html_output = html_output.replace("{{VERSION}}", "4.0.0")  # You may want to make this dynamic
    
    try:
        with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(html_output)
        logger.info(f"Successfully generated main navigation page at {HTML_OUTPUT}")
        return True
    except Exception as e:
        logger.error(f"Error generating main page: {str(e)}")
        return False

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
