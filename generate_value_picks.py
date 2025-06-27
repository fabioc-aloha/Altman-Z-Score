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
HTML_OUTPUT = os.path.join(BASE_DIR, "value_picks.html")

def get_company_data():
    """
    Read all company summary and comprehensive reports to find suitable picks for value investors.
    Value investors prioritize:
    - Undervalued stocks with strong fundamentals
    - Focus on stocks trading below intrinsic value
    - Long-term investment perspective
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
            
            # Check the recommendation for Value profile in comprehensive report if available
            value_rec = None
            if os.path.exists(report_path):
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    # Look for Value recommendation
                    value_match = re.search(r'💎\s*(?:<strong>)?Value(?:</strong>)?.*?<strong>(BUY|HOLD|SELL|STRONG BUY|SPECULATIVE BUY)</strong>', 
                                               report_content, re.DOTALL | re.IGNORECASE)
                    if value_match:
                        value_rec = value_match.group(1).strip()
                except Exception as e:
                    logger.error(f"Error parsing comprehensive report for {ticker}: {str(e)}")
            
            # Value investor criteria:
            # 1. Z-Score should be at least 2.6 (Safe)
            # 2. Recommendation for Value profile is BUY or STRONG BUY
            
            # Include if Value recommendation is favorable and Z-Score is good
            if value_rec is not None and value_rec.upper() in ["BUY", "STRONG BUY"] and z_score >= 2.6:
                # Get company name from README.md
                company_name = get_company_name(ticker)
                
                company_data.append({
                    "ticker": ticker,
                    "name": company_name,
                    "z_score": z_score,
                    "risk_category": risk_category,
                    "recommendation": recommendation,
                    "value_rec": value_rec
                })
                logger.info(f"Added {ticker} - {company_name} with Z-Score {z_score} for Value profile")
            
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
    Generate HTML file with company cards for value investors.
    """
    if not company_data:
        logger.error("No company data to generate HTML")
        return False
    
    current_date = datetime.now().strftime("%B %d, %Y")
    company_count = len(company_data)
    
    # Find top 3 companies for highlighting
    top_companies = company_data[:3] if len(company_data) >= 3 else company_data
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Value Investor Dashboard | Altman Z-Score Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f5f7fb;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background-color: #2c3e50;
            color: white;
            padding: 30px 0;
            text-align: center;
            border-bottom: 5px solid #34495e;
        }}
        .dashboard-title {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .dashboard-subtitle {{
            font-size: 1.2em;
            opacity: 0.8;
        }}
        .summary-stats {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #7b8a8b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .featured-picks {{
            margin: 30px 0;
        }}
        .featured-title {{
            font-size: 1.5em;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        .company-card {{
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
        }}
        .company-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }}
        .card-header {{
            background-color: #34495e;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
        }}
        .top-pick .card-header {{
            background-color: #27ae60;
        }}
        .card-body {{
            padding: 20px;
        }}
        .company-name {{
            font-size: 1.2em;
            margin-bottom: 15px;
            font-weight: bold;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .metric {{
            margin-bottom: 10px;
        }}
        .metric-label {{
            font-size: 0.75em;
            text-transform: uppercase;
            color: #95a5a6;
            letter-spacing: 0.5px;
        }}
        .metric-value {{
            font-size: 1.1em;
            font-weight: 600;
        }}
        .zscore-safe {{
            color: #27ae60;
        }}
        .zscore-grey {{
            color: #7f8c8d;
        }}
        .zscore-distress {{
            color: #c0392b;
        }}
        .recommendation {{
            margin-top: 15px;
            text-align: center;
            padding: 8px;
            border-radius: 5px;
            font-weight: bold;
        }}
        .strong-buy {{
            background-color: #27ae60;
            color: white;
        }}
        .buy {{
            background-color: #2ecc71;
            color: white;
        }}
        .hold {{
            background-color: #f39c12;
            color: white;
        }}
        .sell {{
            background-color: #e74c3c;
            color: white;
        }}
        .view-link {{
            display: block;
            text-align: center;
            margin-top: 15px;
            text-decoration: none;
            color: #3498db;
            font-weight: 600;
        }}
        .table-section {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin: 30px 0;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e1e1e1;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
            position: sticky;
            top: 0;
            box-shadow: 0 1px 0 rgba(0, 0, 0, 0.1);
        }}
        tr:hover {{
            background-color: #f5f7fb;
        }}
        .search-filter {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .search-box {{
            padding: 10px 15px;
            border-radius: 5px;
            border: 1px solid #ddd;
            flex-grow: 1;
            min-width: 200px;
            font-size: 16px;
        }}
        .filter-dropdown {{
            padding: 10px 15px;
            border-radius: 5px;
            border: 1px solid #ddd;
            background-color: white;
            min-width: 150px;
            font-size: 16px;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background-color: #2c3e50;
            color: #ecf0f1;
        }}
        .footer-text {{
            opacity: 0.7;
            font-size: 0.9em;
        }}
        .profile-info {{
            background-color: #fbfcfd;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        .profile-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        .sortable {{
            cursor: pointer;
        }}
        .sortable:after {{
            content: " ⇅";
            font-size: 12px;
            color: #7b8a8b;
        }}
    </style>
</head>
<body>
    <header>
        <h1 class="dashboard-title">Value Investor Dashboard</h1>
        <p class="dashboard-subtitle">Altman Z-Score Analysis | {current_date}</p>
    </header>
    
    <div class="container">
        <section class="summary-stats">
            <h2>Dashboard Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <p class="stat-label">Companies Analyzed</p>
                    <p class="stat-value">{company_count}</p>
                </div>
                <div class="stat-card">
                    <p class="stat-label">Average Z-Score</p>
                    <p class="stat-value">{sum(c["z_score"] for c in company_data) / company_count:.2f}</p>
                </div>
                <div class="stat-card">
                    <p class="stat-label">Highest Z-Score</p>
                    <p class="stat-value">{max(c["z_score"] for c in company_data):.2f}</p>
                </div>
                <div class="stat-card">
                    <p class="stat-label">Lowest Z-Score</p>
                    <p class="stat-value">{min(c["z_score"] for c in company_data):.2f}</p>
                </div>
            </div>
        </section>
        
        <section class="profile-info">
            <h3 class="profile-title">💎 Value Investor Profile</h3>
            <p>Value investors focus on companies trading below their intrinsic value, with strong fundamentals and long-term growth potential. This dashboard highlights stocks with solid financial health (Z-Score ≥ 2.6) that are specifically recommended for value investors based on comprehensive analysis.</p>
        </section>
        
        <section class="featured-picks">
            <h2 class="featured-title">Top Value Picks</h2>
            <div class="card-grid">
"""
    
    # Generate cards for top companies
    for i, company in enumerate(top_companies):
        zscore_class = "zscore-safe" if company["z_score"] >= 3.0 else "zscore-grey" if company["z_score"] >= 1.8 else "zscore-distress"
        rec_class = "strong-buy" if company["value_rec"].upper() == "STRONG BUY" else "buy" if company["value_rec"].upper() == "BUY" else "hold"
        
        html_content += f"""                <div class="company-card top-pick">
                    <div class="card-header">
                        <h3>{company["ticker"]}</h3>
                    </div>
                    <div class="card-body">
                        <p class="company-name">{company["name"]}</p>
                        <div class="metrics-grid">
                            <div class="metric">
                                <div class="metric-label">Z-Score</div>
                                <div class="metric-value {zscore_class}">{company["z_score"]:.2f}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Risk</div>
                                <div class="metric-value">{company["risk_category"]}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Overall Rec</div>
                                <div class="metric-value">{company["recommendation"]}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Value Investor</div>
                                <div class="metric-value">{company["value_rec"]}</div>
                            </div>
                        </div>
                        <div class="recommendation {rec_class}">{company["value_rec"]}</div>
                        <a href="output/{company["ticker"]}/{company["ticker"]}_comprehensive_report.html" target="_blank" class="view-link">View Full Analysis »</a>
                    </div>
                </div>
"""
    
    html_content += """            </div>
        </section>
        
        <section class="table-section">
            <div class="search-filter">
                <input type="text" id="searchBox" class="search-box" placeholder="Search companies...">
                <select id="filterRisk" class="filter-dropdown">
                    <option value="all">All Risk Levels</option>
                    <option value="Safe">Safe</option>
                    <option value="Grey">Grey</option>
                    <option value="Distress">Distress</option>
                </select>
                <select id="filterRec" class="filter-dropdown">
                    <option value="all">All Recommendations</option>
                    <option value="STRONG BUY">Strong Buy</option>
                    <option value="BUY">Buy</option>
                    <option value="HOLD">Hold</option>
                    <option value="SELL">Sell</option>
                </select>
            </div>
            
            <table id="companyTable">
                <thead>
                    <tr>
                        <th class="sortable" data-sort="ticker">Ticker</th>
                        <th class="sortable" data-sort="name">Company Name</th>
                        <th class="sortable" data-sort="zscore">Z-Score</th>
                        <th class="sortable" data-sort="risk">Risk Category</th>
                        <th class="sortable" data-sort="rec">Value Recommendation</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Generate table rows for all companies
    for company in company_data:
        zscore_class = "zscore-safe" if company["z_score"] >= 3.0 else "zscore-grey" if company["z_score"] >= 1.8 else "zscore-distress"
        
        html_content += f"""                    <tr data-ticker="{company["ticker"]}" data-name="{company["name"]}" data-zscore="{company["z_score"]:.2f}" data-risk="{company["risk_category"]}" data-rec="{company["value_rec"]}">
                        <td>{company["ticker"]}</td>
                        <td>{company["name"]}</td>
                        <td class="{zscore_class}">{company["z_score"]:.2f}</td>
                        <td>{company["risk_category"]}</td>
                        <td>{company["value_rec"]}</td>
                        <td><a href="output/{company["ticker"]}/{company["ticker"]}_comprehensive_report.html" target="_blank">View</a></td>
                    </tr>
"""
    
    html_content += """                </tbody>
            </table>
        </section>
    </div>
    
    <footer>
        <p>Altman Z-Score Value Investors Dashboard</p>
        <p class="footer-text">Generated on """ + current_date + """</p>
    </footer>
    
    <script>
        // Search functionality
        document.getElementById('searchBox').addEventListener('input', filterTable);
        document.getElementById('filterRisk').addEventListener('change', filterTable);
        document.getElementById('filterRec').addEventListener('change', filterTable);
        
        function filterTable() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const riskFilter = document.getElementById('filterRisk').value;
            const recFilter = document.getElementById('filterRec').value;
            
            const rows = document.querySelectorAll('#companyTable tbody tr');
            
            rows.forEach(row => {
                const ticker = row.getAttribute('data-ticker').toLowerCase();
                const name = row.getAttribute('data-name').toLowerCase();
                const risk = row.getAttribute('data-risk');
                const rec = row.getAttribute('data-rec');
                
                const matchesSearch = ticker.includes(searchTerm) || name.includes(searchTerm);
                const matchesRisk = riskFilter === 'all' || risk === riskFilter;
                const matchesRec = recFilter === 'all' || rec === recFilter;
                
                if (matchesSearch && matchesRisk && matchesRec) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
        
        // Sorting functionality
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', function() {
                const sortBy = this.getAttribute('data-sort');
                const tbody = document.querySelector('#companyTable tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                // Determine sort order
                const currentOrder = this.classList.contains('asc') ? 'desc' : 'asc';
                
                // Reset all headers
                document.querySelectorAll('.sortable').forEach(h => {
                    h.classList.remove('asc', 'desc');
                });
                
                this.classList.add(currentOrder);
                
                // Sort rows
                rows.sort((a, b) => {
                    let valueA = a.getAttribute(`data-${sortBy}`);
                    let valueB = b.getAttribute(`data-${sortBy}`);
                    
                    if (sortBy === 'zscore') {
                        valueA = parseFloat(valueA);
                        valueB = parseFloat(valueB);
                    }
                    
                    if (valueA < valueB) return currentOrder === 'asc' ? -1 : 1;
                    if (valueA > valueB) return currentOrder === 'asc' ? 1 : -1;
                    return 0;
                });
                
                // Reappend in sorted order
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    </script>
</body>
</html>
"""
    
    try:
        with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Successfully generated HTML dashboard at {HTML_OUTPUT}")
        return True
    except Exception as e:
        logger.error(f"Error generating HTML: {str(e)}")
        return False

def main():
    """
    Main execution function.
    """
    logger.info("Starting Value Investor Dashboard generation...")
    company_data = get_company_data()
    
    if not company_data:
        logger.error("No suitable companies found for Value investors")
        return
    
    logger.info(f"Found {len(company_data)} companies suitable for Value investors")
    
    if generate_html(company_data):
        logger.info(f"Value Investor Dashboard successfully generated at {HTML_OUTPUT}")
    
    logger.info("Process completed")

if __name__ == "__main__":
    main()
