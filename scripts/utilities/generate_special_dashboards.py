#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Special Dashboard Generator for Strong Buy/Sell pages

This script creates the strong buy, sell, and strong sell dashboards with proper logo support,
by directly working with the HTML and ensuring correct logo paths. It fixes the persistent issue
with company logos not displaying correctly on special dashboard pages.

Usage:
    python scripts/utilities/generate_special_dashboards.py
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path to allow imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from altman_zscore.common.logging_config import get_logger
from altman_zscore._version import __version__

# Configure logging
logger = get_logger(__name__)

class SpecialDashboardGenerator:
    """Generate special dashboard pages with correct logo handling."""
    
    def __init__(self):
        self.project_root = project_root
        self.output_dir = project_root / "output"
        self.web_dir = project_root / "web"
        self.web_output_dir = self.web_dir / "output"
        self.assets_dir = self.web_dir / "assets"
        self.default_logo_path = "assets/default_logo.png"
        
        # Ensure required directories exist
        self.web_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
    def generate_all(self):
        """Generate all special dashboards."""
        logger.info("Generating special dashboards with proper logo support...")
        
        # Generate Strong Buy dashboard
        self.generate_dashboard(
            portfolio_type="strong_buy",
            title="Strong Buy Portfolio",
            description="High-conviction investment opportunities with strong fundamentals",
            output_filename="strong_buys.html"
        )
        
        # Generate Strong Sell dashboard
        self.generate_dashboard(
            portfolio_type="strong_sell",
            title="Strong Sell Recommendations",
            description="Companies with concerning financial metrics that may warrant selling",
            output_filename="strong_sell_picks.html"
        )
        
        # Generate Sell dashboard
        self.generate_dashboard(
            portfolio_type="sell",
            title="Sell Recommendations",
            description="Companies requiring careful consideration for sell decisions",
            output_filename="sell_picks.html"
        )
        
        logger.info("✅ Special dashboards generated successfully")
        return True
        
    def generate_dashboard(self, portfolio_type, title, description, output_filename):
        """Generate a special dashboard for the given portfolio type."""
        logger.info(f"Generating {portfolio_type} dashboard...")
        
        # Load company data for this portfolio type
        companies = self._load_companies(portfolio_type)
        if not companies:
            logger.warning(f"No company data found for {portfolio_type}")
            return False
            
        # Generate HTML content
        html_content = self._generate_html(
            companies=companies,
            portfolio_type=portfolio_type,
            title=title,
            description=description
        )
        
        # Write HTML file
        output_path = self.web_dir / output_filename
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Generated {portfolio_type} portfolio HTML: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write HTML file {output_path}: {e}")
            return False
    
    def _load_companies(self, portfolio_type):
        """Load company data for the given portfolio type."""
        data_file = self.output_dir / f"{portfolio_type}_picks.json"
        
        if not data_file.exists():
            logger.warning(f"Data file not found: {data_file}")
            return []
            
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            companies = data.get('companies', [])
            logger.info(f"Loaded {len(companies)} companies from {data_file}")
            return companies
        except Exception as e:
            logger.error(f"Failed to load company data from {data_file}: {e}")
            return []
    
    def _generate_html(self, companies, portfolio_type, title, description):
        """Generate HTML content for the dashboard."""
        current_date = datetime.now().strftime("%B %d, %Y")
        company_count = len(companies)
        
        # Calculate statistics
        safe_count = len([c for c in companies if c.get('z_score', 0) > 2.99])
        avg_zscore = sum(c.get('z_score', 0) for c in companies) / len(companies) if companies else 0
        
        # Generate company cards
        company_cards_html = self._generate_company_cards(companies)
        
        # Generate portfolio summary text
        summary_text = self._generate_summary_text(companies[:3], portfolio_type)
        
        # Get color scheme
        color_scheme = self._get_color_scheme(portfolio_type)
        
        # Load CSS template
        css_content = self._generate_css(color_scheme)
        
        # Generate the final HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-content">
                <h1>{title}</h1>
                <p class="description">{description}</p>
                <p class="generated-date">Generated: {current_date}</p>
            </div>
        </header>

        <section class="portfolio-summary">
            <h2>Portfolio Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>{company_count}</h3>
                    <p>Companies</p>
                </div>
                <div class="summary-card">
                    <h3>{safe_count}</h3>
                    <p>Safe Zone</p>
                </div>
                <div class="summary-card">
                    <h3>{avg_zscore:.2f}</h3>
                    <p>Avg. Z-Score</p>
                </div>
            </div>

            <div class="summary-text">
                <p>{summary_text}</p>
            </div>
        </section>

        <section class="company-analysis">
            <h2>Company Analysis</h2>
            <div class="company-grid">
{company_cards_html}
            </div>
        </section>

        <footer>
            <p>Altman Z-Score Analysis v{__version__} | <a href="index.html">Back to Main Dashboard</a></p>
        </footer>
    </div>
</body>
</html>"""
        return html
    
    def _generate_company_cards(self, companies):
        """Generate HTML for company cards."""
        cards_html = []
        
        for i, company in enumerate(companies, 1):
            ticker = company.get('ticker', 'N/A')
            name = company.get('name', ticker)
            z_score = company.get('z_score', 0)
            risk_category = company.get('risk_category', 'Unknown')
            recommendation = company.get('recommendation', 'N/A')
            
            # Determine risk class for styling
            risk_class = self._get_risk_class(z_score)
            
            # Check for logo in both the original output/ and web/output/ directories
            logo_path_output = self.output_dir / ticker / "logo.png"
            logo_path_web = self.web_output_dir / ticker / "logo.png"
            
            # Use the logo path that exists
            logo_exists = logo_path_web.exists() or logo_path_output.exists()
            
            # Build HTML with the correct logo path and fallback
            if logo_exists:
                # Set up HTML to load from web/output path, with a fallback to the default logo
                logo_html = f'<img src="output/{ticker}/logo.png" alt="{ticker}" class="company-logo" onerror="this.src=\'{self.default_logo_path}\';">'
                logger.debug(f"Using logo path for {ticker}")
                
                # If logo exists in the output/ directory but not in web/output/ directory,
                # create a directory in web/output for this ticker
                if logo_path_output.exists() and not logo_path_web.exists():
                    logger.debug(f"Logo exists in output but not web/output for {ticker}")
                    
                    # We won't copy it here - the PowerShell script will copy it at the end
            else:
                logo_html = f'<img src="{self.default_logo_path}" alt="{ticker}" class="company-logo">'
                logger.warning(f"No logo found for {ticker}, using default logo")
            
            # Build recommendation class
            rec_class = recommendation.lower().replace(' ', '-')
            
            # Generate company card HTML
            card_html = f"""                <div class="company-card">
                    <div class="company-header">
                        <div class="logo-container">
                            {logo_html}
                        </div>
                        <div class="company-info">
                            <h3>** {name} ({ticker})</h3>
                            <span class="rank">#{i}</span>
                        </div>
                    </div>
                    <div class="company-data">
                        <div class="z-score">
                            <h4>Z-SCORE</h4>
                            <span class="{risk_class}">{z_score:.2f}</span>
                        </div>
                        <div class="risk-category">
                            <h4>RISK CATEGORY</h4>
                            <span class="{risk_class}">{risk_category}</span>
                        </div>
                        <div class="recommendation">
                            <h4>RECOMMENDATION</h4>
                            <span class="{rec_class}">{recommendation}</span>
                        </div>
                    </div>
                    <div class="company-actions">
                        <a href="output/{ticker}/report.html" class="view-report">View Full Report</a>
                    </div>
                </div>"""
            cards_html.append(card_html)
        
        return "\n".join(cards_html)
    
    def _generate_summary_text(self, top_companies, portfolio_type):
        """Generate portfolio summary text."""
        if not top_companies:
            return "No companies found matching the criteria."
            
        portfolio_descriptions = {
            'strong_buy': 'companies with exceptional financial strength and Strong Buy recommendations',
            'buy': 'companies with strong financial metrics and Buy recommendations', 
            'value': 'undervalued companies with solid fundamentals',
            'growth': 'companies showing strong growth potential',
            'dividend': 'reliable dividend-paying companies',
            'conservative': 'low-risk companies for conservative investors',
            'aggressive': 'high-growth potential companies for aggressive investors',
            'sell': 'companies requiring careful consideration for sell decisions',
            'strong_sell': 'companies with concerning financial metrics'
        }
        
        description = portfolio_descriptions.get(
            portfolio_type, 
            'companies matching specific investment criteria'
        )
        
        summary = f"This portfolio presents <strong>{description}</strong> based on comprehensive Altman Z-Score analysis. The selection emphasizes financial stability, market position, and investment potential."
        
        # Add top pick information
        if top_companies:
            top_pick = top_companies[0]
            top_ticker = top_pick.get('ticker', 'N/A')
            top_zscore = top_pick.get('z_score', 0)
            
            summary += f"<br><br>Top Pick: ** {top_pick.get('name', top_ticker)} ({top_ticker}) leads with a Z-Score of {top_zscore:.2f}"
            
            # Add notable mentions
            if len(top_companies) > 1:
                summary += "<br><br>Notable Mentions: ** "
                mentions = []
                
                for i, company in enumerate(top_companies[1:3], 1):
                    ticker = company.get('ticker', 'N/A')
                    name = company.get('name', ticker)
                    z_score = company.get('z_score', 0)
                    mentions.append(f"{name} (Ticker: {ticker}) ({z_score:.2f})")
                
                summary += " and ".join(mentions) + " also demonstrate strong fundamentals with Z-Scores of " + " and ".join([f"{c.get('z_score', 0):.2f}" for c in top_companies[1:3]]) + " respectively."
        
        return summary
    
    def _get_risk_class(self, z_score):
        """Get CSS risk class based on Z-Score."""
        if z_score > 2.99:
            return "risk-safe"
        elif z_score > 1.8:
            return "risk-moderate"
        else:
            return "risk-high"
    
    def _get_color_scheme(self, portfolio_type):
        """Get color scheme for the given portfolio type."""
        schemes = {
            'strong_buy': {
                'primary': '#27ae60',
                'secondary': '#2ecc71',
                'accent': '#82e0aa'
            },
            'buy': {
                'primary': '#2980b9',
                'secondary': '#3498db',
                'accent': '#85c1e9'
            },
            'value': {
                'primary': '#8e44ad',
                'secondary': '#9b59b6',
                'accent': '#d2b4de'
            },
            'growth': {
                'primary': '#16a085',
                'secondary': '#1abc9c',
                'accent': '#76d7c4'
            },
            'dividend': {
                'primary': '#f39c12',
                'secondary': '#f1c40f',
                'accent': '#f9e79f'
            },
            'conservative': {
                'primary': '#2c3e50',
                'secondary': '#6c7b7f',
                'accent': '#a6acaf'
            },
            'aggressive': {
                'primary': '#c0392b',
                'secondary': '#e74c3c',
                'accent': '#f1948a'
            },
            'sell': {
                'primary': '#e67e22',
                'secondary': '#f39c12',
                'accent': '#f8c471'
            },
            'strong_sell': {
                'primary': '#c0392b',
                'secondary': '#e74c3c',
                'accent': '#f1948a'
            }
        }
        
        return schemes.get(portfolio_type, {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#5d6d7e'
        })
    
    def _generate_css(self, color_scheme):
        """Generate CSS with the given color scheme."""
        css = f"""/* General styles */
body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f5f5f5;
    margin: 0;
    padding: 0;
    color: #333;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

/* Header styles */
header {{
    background-color: {color_scheme['primary']};
    color: white;
    padding: 30px 0;
    margin-bottom: 30px;
    border-radius: 5px;
}}

.header-content {{
    text-align: center;
    padding: 0 20px;
}}

h1 {{
    margin: 0;
    font-size: 2.5em;
    font-weight: 700;
}}

.description {{
    font-size: 1.2em;
    margin: 10px 0 5px;
    opacity: 0.9;
}}

.generated-date {{
    font-size: 0.9em;
    margin-top: 5px;
    opacity: 0.7;
}}

/* Section styles */
section {{
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 30px;
    padding: 25px;
}}

h2 {{
    color: {color_scheme['primary']};
    margin-top: 0;
    font-size: 1.8em;
    padding-bottom: 10px;
    border-bottom: 2px solid {color_scheme['accent']};
}}

/* Summary grid */
.summary-grid {{
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    flex-wrap: wrap;
}}

.summary-card {{
    flex: 1;
    min-width: 150px;
    text-align: center;
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 5px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin: 10px;
}}

.summary-card h3 {{
    margin: 0;
    font-size: 2.5em;
    color: {color_scheme['secondary']};
}}

.summary-card p {{
    margin: 5px 0 0;
    font-weight: 500;
}}

.summary-text {{
    margin: 20px 0;
    line-height: 1.6;
}}

/* Company grid */
.company-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}}

.company-card {{
    background-color: #fff;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.company-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.15);
}}

.company-header {{
    display: flex;
    align-items: center;
    padding: 15px;
    background-color: #f9f9f9;
}}

.logo-container {{
    width: 50px;
    height: 50px;
    margin-right: 15px;
    overflow: hidden;
    background-color: white;
    border-radius: 4px;
}}

.company-logo {{
    width: 100%;
    height: 100%;
    object-fit: contain;
}}

.company-info {{
    flex-grow: 1;
}}

.company-info h3 {{
    margin: 0;
    font-size: 1.1em;
    line-height: 1.3;
}}

.rank {{
    display: inline-block;
    background-color: {color_scheme['secondary']};
    color: white;
    font-size: 0.8em;
    padding: 3px 8px;
    border-radius: 20px;
    margin-top: 5px;
}}

.company-data {{
    display: flex;
    justify-content: space-between;
    padding: 15px;
    border-top: 1px solid #eee;
    text-align: center;
}}

.company-data > div {{
    flex: 1;
    padding: 0 10px;
}}

.company-data h4 {{
    margin: 0 0 5px;
    font-size: 0.8em;
    font-weight: 600;
    color: #777;
}}

.company-data span {{
    display: block;
    font-weight: 600;
    font-size: 1.1em;
}}

.company-actions {{
    padding: 15px;
    border-top: 1px solid #eee;
    text-align: center;
}}

.view-report {{
    display: inline-block;
    background-color: {color_scheme['primary']};
    color: white;
    text-decoration: none;
    padding: 8px 20px;
    border-radius: 4px;
    font-weight: 600;
    transition: background-color 0.3s ease;
}}

.view-report:hover {{
    background-color: {color_scheme['secondary']};
}}

/* Risk and recommendation styling */
.risk-safe {{
    color: #27ae60;
}}

.risk-moderate {{
    color: #f39c12;
}}

.risk-high {{
    color: #e74c3c;
}}

.strong-buy {{
    color: #27ae60;
}}

.buy {{
    color: #2ecc71;
}}

.hold {{
    color: #f39c12;
}}

.sell {{
    color: #e67e22;
}}

.strong-sell {{
    color: #c0392b;
}}

/* Footer styles */
footer {{
    text-align: center;
    margin-top: 40px;
    padding: 20px;
    color: #777;
    font-size: 0.9em;
}}

footer a {{
    color: {color_scheme['secondary']};
    text-decoration: none;
}}

footer a:hover {{
    text-decoration: underline;
}}

/* Responsive adjustments */
@media (max-width: 768px) {{
    .summary-grid {{
        flex-direction: column;
    }}
    
    .company-grid {{
        grid-template-columns: 1fr;
    }}
    
    .company-data {{
        flex-direction: column;
    }}
    
    .company-data > div {{
        margin-bottom: 10px;
    }}
}}"""
        return css


def main():
    """Main function to generate special dashboards."""
    try:
        generator = SpecialDashboardGenerator()
        success = generator.generate_all()
        
        if success:
            print("✅ Special dashboards generated successfully")
            return 0
        else:
            print("❌ Error generating special dashboards")
            return 1
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
