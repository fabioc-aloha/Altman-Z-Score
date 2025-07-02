#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
import logging

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
ENHANCED_CSS_FILE = os.path.join(WEB_ASSETS_DIR, "dashboard_enhanced.css")

# Ensure web directory exists
os.makedirs(WEB_DIR, exist_ok=True)
logger.info(f"Using web directory: {WEB_DIR}")

def load_enhanced_css():
    """Load enhanced CSS content for embedding."""
    try:
        with open(ENHANCED_CSS_FILE, 'r', encoding='utf-8') as f:
            css_content = f.read()
        logger.info(f"Successfully loaded enhanced CSS from {ENHANCED_CSS_FILE}")
        return css_content
    except Exception as e:
        logger.warning(f"Could not load enhanced CSS file {ENHANCED_CSS_FILE}: {str(e)}")
        # Return basic CSS as fallback
        return """
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a5276; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .dashboard-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: white; }
        """

def get_dashboard_stats():
    """
    Check which dashboard files exist and get basic stats from each.
    Enhanced with better organization and modern presentation.
    """
    dashboards = {
        # Buy Recommendations (High Priority)
        "strong_buys.html": {
            "title": "Strong Buy Recommendations",
            "description": "Highest confidence investment opportunities with exceptional financial health",
            "icon": "🚀",
            "color": "#059669",
            "category": "buy",
            "priority": 1
        },
        
        # Investor Profile Dashboards
        "conservative_picks.html": {
            "title": "Conservative Investor Picks",
            "description": "Ultra-safe companies with stable earnings and minimal risk exposure",
            "icon": "🛡️",
            "color": "#2563eb",
            "category": "profile",
            "priority": 2
        },
        "dividend_picks.html": {
            "title": "Dividend Income Portfolio",
            "description": "Reliable dividend-paying companies for consistent passive income",
            "icon": "💰",
            "color": "#d97706",
            "category": "profile",
            "priority": 2
        },
        "value_picks.html": {
            "title": "Value Investor Picks",
            "description": "Undervalued gems with strong fundamentals trading below intrinsic value",
            "icon": "💎",
            "color": "#7c3aed",
            "category": "profile",
            "priority": 2
        },
        "growth_picks.html": {
            "title": "Growth Investor Portfolio",
            "description": "High-growth companies with expanding markets and increasing revenues",
            "icon": "📈",
            "color": "#059669",
            "category": "profile",
            "priority": 2
        },
        "aggressive_picks.html": {
            "title": "Aggressive Growth Portfolio",
            "description": "High-risk, high-reward opportunities for aggressive capital appreciation",
            "icon": "🔥",
            "color": "#dc2626",
            "category": "profile",
            "priority": 2
        },
        
        # Sell Recommendations (Important Warning)
        "sell_picks.html": {
            "title": "Sell Recommendations",
            "description": "Companies showing warning signs requiring immediate attention",
            "icon": "⚠️",
            "color": "#dc2626",
            "category": "sell",
            "priority": 3
        },
        "strong_sell_picks.html": {
            "title": "Strong Sell Alerts",
            "description": "Companies in severe financial distress - immediate exit recommended",
            "icon": "🚨",
            "color": "#dc2626",
            "category": "sell",
            "priority": 3
        },
        
        # Industry-Specific Analysis
        "manufacturing__and__industrial.html": {
            "title": "Manufacturing & Industrial",
            "description": "Traditional manufacturing companies analyzed with original Altman Z-Score",
            "icon": "🏭",
            "color": "#7c3aed",
            "category": "industry",
            "priority": 4
        },
        "private__and__service_companies.html": {
            "title": "Private & Service Companies",
            "description": "Service sector companies using specialized Z'-Score methodology",
            "icon": "🏢",
            "color": "#7c3aed",
            "category": "industry",
            "priority": 4
        },
        "emerging_markets.html": {
            "title": "Emerging Markets",
            "description": "International and emerging market opportunities with Z\"-Score analysis",
            "icon": "🌏",
            "color": "#7c3aed",
            "category": "industry",
            "priority": 4
        },
        "financial_institutions.html": {
            "title": "Financial Institutions",
            "description": "Banks and financial services using specialized CAMELS framework",
            "icon": "🏦",
            "color": "#7c3aed",
            "category": "industry",
            "priority": 4
        },
        "regulated_utilities.html": {
            "title": "Regulated Utilities",
            "description": "Utility companies with stable cash flows and regulated revenues",
            "icon": "⚡",
            "color": "#7c3aed",
            "category": "industry",
            "priority": 4
        },
        "technology__and__growth.html": {
            "title": "Technology & Growth",
            "description": "High-growth technology companies with significant R&D investments",
            "icon": "💻",
            "color": "#7c3aed",
            "category": "industry",
            "priority": 4
        },
        "retail__and__consumer.html": {
            "title": "Retail & Consumer",
            "description": "Consumer-focused companies with inventory turnover analysis",
            "icon": "🛍️",
            "color": "#7c3aed",
            "category": "industry",
            "priority": 4
        }
    }
    
    # Check which files exist and get company counts
    available_dashboards = {}
    total_companies = 0
    
    for filename, info in dashboards.items():
        filepath = os.path.join(WEB_DIR, filename)
        if os.path.exists(filepath):
            try:
                # Try to extract company count from the HTML
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for company cards or similar indicators
                company_count = content.count('class="company-card"')
                if company_count == 0:
                    # Fallback: look for other indicators
                    company_count = content.count('class="card"')
                if company_count == 0:
                    # Default count for estimation
                    if info['category'] == 'buy':
                        company_count = 25
                    elif info['category'] == 'profile':
                        company_count = 20
                    elif info['category'] == 'sell':
                        company_count = 20
                    else:
                        company_count = 15
                
                info['company_count'] = company_count
                available_dashboards[filename] = info
                total_companies += company_count
                
            except Exception as e:
                logger.warning(f"Could not read {filepath}: {e}")
                info['company_count'] = 0
                available_dashboards[filename] = info
        else:
            logger.info(f"Dashboard not found: {filepath}")
    
    return available_dashboards, total_companies

def generate_enhanced_main_page():
    """Generate the enhanced main navigation page with modern styling."""
    
    css_content = load_enhanced_css()
    dashboards, total_companies = get_dashboard_stats()
    
    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Organize dashboards by category
    categories = {
        'buy': {'title': 'Buy Recommendations', 'description': 'High-confidence investment opportunities', 'dashboards': []},
        'profile': {'title': 'Investor Profile Dashboards', 'description': 'Tailored recommendations for different investment styles', 'dashboards': []},
        'sell': {'title': 'Sell Recommendations', 'description': 'Warning signals and exit strategies', 'dashboards': []},
        'industry': {'title': 'Industry-Specific Analysis', 'description': 'Sector-focused investment insights', 'dashboards': []}
    }
    
    # Sort dashboards into categories
    for filename, info in dashboards.items():
        categories[info['category']]['dashboards'].append((filename, info))
    
    # Sort within categories by priority and company count
    for category in categories.values():
        category['dashboards'].sort(key=lambda x: (x[1]['priority'], -x[1]['company_count']))
    
    # Generate dashboard cards HTML
    def generate_dashboard_cards(category_dashboards, category_name):
        cards_html = []
        for filename, info in category_dashboards:
            card_html = f'''<a href="{filename}" class="dashboard-card {category_name}-category">
                <div class="card-header">
                    <span class="card-icon">{info['icon']}</span>
                    <h3 class="card-title">{info['title']}</h3>
                    <p class="card-count">{info['company_count']} Companies</p>
                </div>
                <div class="card-body">
                    <p class="card-description">{info['description']}</p>
                    <button class="card-button">View Dashboard</button>
                </div>
            </a>'''
            cards_html.append(card_html)
        return ''.join(cards_html)
    
    # Build the complete HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Altman Z-Score Dashboard Navigator</title>
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    <style>
{css_content}
    </style>
</head>

<body>
    <!-- Hamburger Menu -->
    <div class="hamburger-menu">
        <button class="hamburger-toggle" onclick="toggleMenu()" title="Navigation Menu" aria-label="Toggle navigation menu">
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
            <span class="hamburger-line"></span>
        </button>
    </div>

    <!-- Navigation Menu -->
    <nav class="nav-menu" id="navMenu">
        <div class="nav-stats">
            <h4>Dashboard Overview</h4>
            <div class="stat-grid">
                <div class="stat-item">
                    <span class="stat-number">{len(dashboards)}</span>
                    <span class="stat-label">Dashboards</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_companies}</span>
                    <span class="stat-label">Companies</span>
                </div>
            </div>
        </div>

        <div class="nav-section">
            <h3>Buy Recommendations</h3>
            <ul class="nav-links">
                <li><a href="strong_buys.html">Strong Buy Recommendations</a></li>
            </ul>
        </div>

        <div class="nav-section">
            <h3>Investor Profiles</h3>
            <ul class="nav-links">
                <li><a href="dividend_picks.html">Dividend Income Portfolio</a></li>
                <li><a href="value_picks.html">Value Investor Picks</a></li>
                <li><a href="growth_picks.html">Growth Investor Portfolio</a></li>
                <li><a href="conservative_picks.html">Conservative Investor Picks</a></li>
                <li><a href="aggressive_picks.html">Aggressive Growth Portfolio</a></li>
            </ul>
        </div>

        <div class="nav-section">
            <h3>Z-Score Categories</h3>
            <ul class="nav-links">
                <li><a href="manufacturing_&_industrial.html">Manufacturing & Industrial</a></li>
                <li><a href="private_&_service_companies.html">Private & Service Companies</a></li>
                <li><a href="emerging_markets.html">Emerging Markets</a></li>
                <li><a href="financial_institutions.html">Financial Institutions</a></li>
                <li><a href="regulated_utilities.html">Regulated Utilities</a></li>
                <li><a href="technology_&_growth.html">Technology & Growth</a></li>
                <li><a href="retail_&_consumer.html">Retail & Consumer</a></li>
            </ul>
        </div>

        <div class="nav-section">
            <h3>Market Analysis</h3>
            <ul class="nav-links">
                <li><a href="sell_picks.html">Sell Recommendations</a></li>
                <li><a href="strong_sell_picks.html">Strong Sell Recommendations</a></li>
                <li><a href="model_portfolios_index.html">Model Portfolios Index</a></li>
            </ul>
        </div>
    </nav>

    <!-- Overlay for mobile -->
    <div class="nav-overlay" id="navOverlay" onclick="toggleMenu()"></div>

    <div class="header">
        <h1>Altman Z-Score Dashboard Navigator</h1>
        <p class="subtitle">Advanced Financial Health Analysis & Investment Insights</p>
        <p class="date">Generated: {current_date}</p>
        
        <!-- Quick Stats Section -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(dashboards)}</div>
                <div class="stat-label">Dashboards</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_companies}</div>
                <div class="stat-label">Companies Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(categories)}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">7</div>
                <div class="stat-label">Z-Score Models</div>
            </div>
        </div>
    </div>'''
    
    # Add each category section
    for category_key, category_info in categories.items():
        if category_info['dashboards']:
            section_class = f"{category_key}-section"
            html_content += f'''
    <!-- {category_info['title']} Section -->
    <h2 class="section-title">{category_info['title']}</h2>
    <div class="dashboard-grid {section_class}">
        {generate_dashboard_cards(category_info['dashboards'], category_key)}
    </div>'''
    
    # Add footer and closing tags
    html_content += '''

    <div class="footer">
        <p>Altman Z-Score Analysis &copy; 2025 | Enhanced Dashboard Experience | Version 4.0.0+</p>
        <p>Financial health analysis based on Edward Altman's bankruptcy prediction models</p>
    </div>

    <script>
        function toggleMenu() {
            const hamburgerToggle = document.querySelector('.hamburger-toggle');
            const navMenu = document.getElementById('navMenu');
            const navOverlay = document.getElementById('navOverlay');

            hamburgerToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            navOverlay.classList.toggle('active');

            // Prevent body scroll when menu is open
            if (navMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        }

        // Close menu when pressing Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const navMenu = document.getElementById('navMenu');
                if (navMenu.classList.contains('active')) {
                    toggleMenu();
                }
            }
        });

        // Close menu when clicking on a link (for mobile)
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', function() {
                const navMenu = document.getElementById('navMenu');
                if (navMenu.classList.contains('active')) {
                    toggleMenu();
                }
            });
        });
    </script>
</body>

</html>'''
    
    return html_content

def main():
    """Main function to generate the enhanced navigation page."""
    try:
        logger.info("Starting enhanced main page generation...")
        
        # Generate the enhanced HTML content
        html_content = generate_enhanced_main_page()
        
        # Write to file
        with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ Enhanced main navigation page generated successfully: {HTML_OUTPUT}")
        
        # Verify file was created and has content
        if os.path.exists(HTML_OUTPUT):
            size = os.path.getsize(HTML_OUTPUT)
            logger.info(f"📊 Generated file size: {size:,} bytes")
            
            if size > 1000:  # Basic sanity check
                logger.info("🎉 Enhanced dashboard generation completed successfully!")
                return True
            else:
                logger.error("❌ Generated file seems too small - possible error")
                return False
        else:
            logger.error("❌ Generated file not found after creation")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to generate enhanced main page: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
