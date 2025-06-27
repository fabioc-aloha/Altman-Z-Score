#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import glob
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Current directory where the script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
HTML_OUTPUT = os.path.join(BASE_DIR, "dividend_picks.html")

def get_company_data():
    """
    Read all company summary and comprehensive reports to find suitable picks for dividend investors.
    Dividend investors prioritize:
    - Income generation
    - Dividend stability
    - Moderate growth potential
    """
    company_data = []
    
    # Get all company directories in the output folder
    company_dirs = [d for d in os.listdir(OUTPUT_DIR) 
                    if os.path.isdir(os.path.join(OUTPUT_DIR, d))]
    
    logger.info(f"Found {len(company_dirs)} company directories to process")
    
    for ticker in company_dirs:
        summary_path = os.path.join(OUTPUT_DIR, ticker, f"{ticker}_summary.txt")
        report_path = os.path.join(OUTPUT_DIR, ticker, f"{ticker}_comprehensive_report.html")
        
        if not os.path.exists(summary_path):
            logger.warning(f"No summary file found for {ticker}")
            continue
            
        try:
            # Read the summary file
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract Z-Score
            z_score_match = re.search(r'Z-SCORE: ([0-9.]+)', content)
            if not z_score_match:
                logger.warning(f"Couldn't find Z-Score for {ticker}")
                continue
                
            z_score = float(z_score_match.group(1))
            
            # Extract Risk Category
            risk_match = re.search(r'Risk Category: (\w+)', content)
            if not risk_match:
                logger.warning(f"Couldn't find Risk Category for {ticker}")
                continue
                
            risk_category = risk_match.group(1)
            
            # Extract Investment Recommendation
            recommendation_match = re.search(r'Action: (.+?)\n', content)
            if not recommendation_match:
                logger.warning(f"Couldn't find Recommendation for {ticker}")
                continue
                
            recommendation = recommendation_match.group(1).strip()
            
            # Check the recommendation for Dividend profile in comprehensive report if available
            dividend_rec = None
            if os.path.exists(report_path):
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    # Look for Dividend recommendation
                    dividend_match = re.search(r'💰\s*(?:<strong>)?Dividend(?:</strong>)?.*?<strong>(BUY|HOLD|SELL)</strong>', 
                                               report_content, re.DOTALL)
                    if dividend_match:
                        dividend_rec = dividend_match.group(1).strip()
                except Exception as e:
                    logger.error(f"Error parsing comprehensive report for {ticker}: {str(e)}")
            
            # Dividend investor criteria:
            # 1. Z-Score > 2.5 (reasonably safe)
            # 2. Dividend recommendation is BUY or HOLD (if available)
            # 3. General recommendation is not SELL
            
            if z_score > 2.5 and recommendation.lower() != "sell":
                if dividend_rec is not None and dividend_rec.lower() in ["buy", "hold"]:
                    # Get company name from README.md
                    company_name = get_company_name(ticker)
                    
                    company_data.append({
                        "ticker": ticker,
                        "name": company_name,
                        "z_score": z_score,
                        "risk_category": risk_category,
                        "recommendation": recommendation,
                        "dividend_rec": dividend_rec
                    })
                    logger.info(f"Added {ticker} - {company_name} with Z-Score {z_score} for Dividend profile")
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
    
    # Sort by Z-Score (descending)
    company_data.sort(key=lambda x: x["z_score"], reverse=True)
    return company_data

def get_company_name(ticker):
    """
    Extract company name from README.md.
    Fall back to using ticker if company name can't be found.
    """
    readme_path = os.path.join(BASE_DIR, "README.md")
    company_name = ticker
    
    try:
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for the ticker in README.md and extract the company name
            pattern = rf'alt="{ticker}".*?\*\*(.+?)\*\*'
            match = re.search(pattern, content)
            if match:
                company_name = match.group(1).strip()
    except Exception as e:
        logger.error(f"Error finding company name for {ticker}: {str(e)}")
    
    return company_name

def generate_html(company_data):
    """
    Generate HTML file with company cards for dividend investors.
    """
    if not company_data:
        logger.error("No company data to generate HTML")
        return False
    
    current_date = datetime.now().strftime("%B %d, %Y")
    company_count = len(company_data)
    
    # Find top 3 companies for highlighting
    top_companies = company_data[:3] if len(company_data) >= 3 else company_data
    top_company_text = f"{top_companies[0]['name']} ({top_companies[0]['ticker']})" if company_data else "N/A"
    second_company_text = f"{top_companies[1]['name']} ({top_companies[1]['ticker']})" if len(top_companies) > 1 else "N/A"
    third_company_text = f"{top_companies[2]['name']} ({top_companies[2]['ticker']})" if len(top_companies) > 2 else "N/A"
    
    # Start generating HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dividend Investor Stock Picks - Altman Z-Score</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            line-height: 1.6;
            background-color: #f9f9f9;
        }}
        h1, h2 {{
            color: #1a5276;
            margin-top: 30px;
        }}
        h1 {{
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .header-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .date {{
            text-align: right;
            font-size: 1.1em;
            color: #666;
        }}
        .company-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .company-card {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            padding: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
        }}
        .company-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        .company-logo {{
            width: 50px;
            height: 50px;
            border-radius: 4px;
            object-fit: cover;
            margin-right: 15px;
        }}
        .company-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .company-name {{
            font-weight: 600;
            font-size: 1.2em;
            color: #2c3e50;
            flex: 1;
        }}
        .ticker {{
            background-color: #eef2f5;
            padding: 3px 10px;
            border-radius: 4px;
            font-weight: 500;
            color: #34495e;
            display: inline-block;
            margin-top: 3px;
            margin-left: auto;
        }}
        .z-score {{
            font-size: 1.5em;
            font-weight: bold;
            color: #27ae60;
            margin: 15px 0;
        }}
        .recommendation {{
            background-color: #27ae60;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            font-weight: 600;
        }}
        .recommendation.buy {{
            background-color: #27ae60;
        }}
        .recommendation.hold {{
            background-color: #f39c12;
        }}
        .label {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 3px;
        }}
        .view-report {{
            display: block;
            text-align: center;
            margin-top: 20px;
            padding: 8px 15px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: background-color 0.3s;
        }}
        .view-report:hover {{
            background-color: #2980b9;
        }}
        .filters {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 30px 0;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .filter-group {{
            display: flex;
            align-items: center;
        }}
        select, input {{
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid #ddd;
            margin-left: 10px;
        }}
        .total-count {{
            background-color: #eef2f5;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 500;
        }}
        .summary {{
            background-color: #e8f4fd;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .highest-z-score {{
            color: #27ae60;
            font-weight: bold;
        }}
        .disclaimer {{
            margin-top: 40px;
            padding: 15px;
            background-color: #efefef;
            border-radius: 6px;
            font-size: 0.9em;
            color: #666;
            text-align: center;
        }}
        .category-label {{
            position: absolute;
            top: -10px;
            left: 20px;
            background-color: #2e86c1;
            color: white;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        .risk-category {{
            color: #27ae60;
            font-weight: 500;
        }}
        .profile-icon {{
            font-size: 24px;
            margin-right: 10px;
            vertical-align: middle;
        }}
        .profile-description {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #2e86c1;
        }}
    </style>
</head>
<body>
    <div class="header-container">
        <h1><span class="profile-icon">💰</span> Dividend Investor Stock Picks</h1>
        <div class="date">{current_date}</div>
    </div>

    <div class="profile-description">
        <p><strong>Dividend Investor Profile:</strong> Focused on income generation with low to medium risk tolerance. 
        These investors prioritize companies with sustainable dividend payments, stable cash flows, and solid financial health. 
        All stocks in this list have been identified as suitable for dividend-focused investors based on their financial stability and income potential.</p>
    </div>

    <div class="summary">
        <h2>Investment Summary</h2>
        <p>Based on the Altman Z-Score analysis and dividend investor criteria, we have identified <strong>{company_count}</strong> companies that meet the requirements for income-focused investors. These companies demonstrate solid financial health with sufficient Z-Scores to support sustainable dividend payments.</p>
        <p>The highest Z-Score belongs to <span class="highest-z-score">{top_company_text}</span> with Z-Score of {top_companies[0]["z_score"]:.2f} (if available), followed by <span class="highest-z-score">{second_company_text}</span> and <span class="highest-z-score">{third_company_text}</span>.</p>
        <p>These recommendations are particularly suitable for investors focused on income generation and dividend sustainability.</p>
    </div>

    <div class="filters">
        <div class="filter-group">
            <label for="sort-by">Sort by:</label>
            <select id="sort-by">
                <option value="z-score-desc">Z-Score (Highest First)</option>
                <option value="z-score-asc">Z-Score (Lowest First)</option>
                <option value="name-asc">Company Name (A-Z)</option>
                <option value="name-desc">Company Name (Z-A)</option>
                <option value="rec-buy">Buy Recommendations First</option>
            </select>
        </div>
        <div class="filter-group">
            <label for="search">Search:</label>
            <input type="text" id="search" placeholder="Company or ticker...">
        </div>
        <div class="total-count">{company_count} Companies</div>
    </div>

    <div class="company-grid" id="company-container">'''
    
    # Generate a card for each company
    for i, company in enumerate(company_data):
        ticker = company["ticker"]
        logo_path = f"output/{ticker}/{ticker}_logo.png"
        
        # Add a special label for the top company
        top_label = ""
        if i == 0:
            top_label = '<span class="category-label">Top Dividend Pick</span>'
        
        # Set recommendation class
        rec_class = company["dividend_rec"].lower()
            
        html_content += f'''
        <div class="company-card" data-ticker="{ticker}" data-z-score="{company["z_score"]}" data-rec="{rec_class}">
            {top_label}
            <div class="company-header">
                <img src="output/{ticker}/{ticker}_logo.png" alt="{ticker}" class="company-logo">
                <div>
                    <div class="company-name">{company["name"]}</div>
                    <span class="ticker">{ticker}</span>
                </div>
            </div>
            <div class="label">Altman Z-Score:</div>
            <div class="z-score">{company["z_score"]:.2f}</div>
            <div class="label">Risk Category:</div>
            <div class="risk-category">{company["risk_category"]}</div>
            <div class="label">Dividend Investor:</div>
            <div class="recommendation {rec_class}">{company["dividend_rec"]}</div>
            <a href="output/{ticker}/{ticker}_comprehensive_report.html" class="view-report" target="_blank">View Full Report</a>
        </div>'''
    
    # Add JavaScript and close HTML
    html_content += '''
    </div>

    <div class="disclaimer">
        <p><strong>Disclaimer:</strong> This information is based on Altman Z-Score analysis as of the current date shown. 
        These recommendations are tailored for dividend-focused investors and are derived from financial health metrics. 
        They do not guarantee future performance or dividend sustainability. Always consult with a financial advisor before 
        making investment decisions. This analysis is not financial advice.</p>
    </div>

    <script>
        // Simple sorting and filtering functionality
        document.addEventListener('DOMContentLoaded', function() {
            const companyContainer = document.getElementById('company-container');
            const sortBySelect = document.getElementById('sort-by');
            const searchInput = document.getElementById('search');
            const companies = Array.from(document.querySelectorAll('.company-card'));
            
            // Sort function
            function sortCompanies() {
                const sortValue = sortBySelect.value;
                const sortedCompanies = [...companies].sort((a, b) => {
                    switch(sortValue) {
                        case 'z-score-desc':
                            return parseFloat(b.dataset.zScore) - parseFloat(a.dataset.zScore);
                        case 'z-score-asc':
                            return parseFloat(a.dataset.zScore) - parseFloat(b.dataset.zScore);
                        case 'name-asc':
                            return a.querySelector('.company-name').textContent.localeCompare(b.querySelector('.company-name').textContent);
                        case 'name-desc':
                            return b.querySelector('.company-name').textContent.localeCompare(a.querySelector('.company-name').textContent);
                        case 'rec-buy':
                            if (a.dataset.rec === 'buy' && b.dataset.rec !== 'buy') return -1;
                            if (a.dataset.rec !== 'buy' && b.dataset.rec === 'buy') return 1;
                            return parseFloat(b.dataset.zScore) - parseFloat(a.dataset.zScore);
                        default:
                            return 0;
                    }
                });
                
                companyContainer.innerHTML = '';
                sortedCompanies.forEach(company => companyContainer.appendChild(company));
            }
            
            // Filter function
            function filterCompanies() {
                const searchTerm = searchInput.value.toLowerCase();
                companies.forEach(company => {
                    const companyName = company.querySelector('.company-name').textContent.toLowerCase();
                    const ticker = company.dataset.ticker.toLowerCase();
                    
                    if (companyName.includes(searchTerm) || ticker.includes(searchTerm)) {
                        company.style.display = '';
                    } else {
                        company.style.display = 'none';
                    }
                });
            }
            
            // Event listeners
            sortBySelect.addEventListener('change', sortCompanies);
            searchInput.addEventListener('input', filterCompanies);
            
            // Initial sort
            sortCompanies();
        });
    </script>
</body>
</html>'''

    # Write the HTML file
    try:
        with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"HTML file generated successfully: {HTML_OUTPUT}")
        return True
    except Exception as e:
        logger.error(f"Error writing HTML file: {str(e)}")
        return False

def main():
    logger.info("Starting Dividend Investor Picks Generator")
    
    # Get company data
    company_data = get_company_data()
    logger.info(f"Found {len(company_data)} companies matching Dividend investor criteria")
    
    # Generate HTML
    success = generate_html(company_data)
    
    if success:
        logger.info("HTML generation complete")
    else:
        logger.error("HTML generation failed")

if __name__ == "__main__":
    main()
