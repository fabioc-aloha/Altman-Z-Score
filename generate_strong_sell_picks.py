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
HTML_OUTPUT = os.path.join(BASE_DIR, "strong_sell_picks.html")

def get_company_data():
    """
    Read all company summary and comprehensive reports to find stocks with STRONG SELL recommendations.
    These companies exhibit severe financial distress indicators:
    - Very low Z-Score (deep in the distress zone)
    - Multiple strong sell recommendations across investor profiles
    - Critical financial or market red flags
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
            
            # Store all profile recommendations
            profile_recs = {}
            strong_sell_count = 0
            sell_count = 0
            
            # Check comprehensive report for profile-specific recommendations
            if os.path.exists(report_path):
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    
                    # Look for recommendations across all investor profiles
                    profile_patterns = {
                        "conservative": r'📊\s*(?:<strong>)?Conservative(?:</strong>)?.*?<strong>(BUY|HOLD|SELL|STRONG BUY|STRONG SELL)</strong>',
                        "dividend": r'💰\s*(?:<strong>)?Dividend(?:</strong>)?.*?<strong>(BUY|HOLD|SELL|STRONG BUY|STRONG SELL)</strong>',
                        "value": r'💎\s*(?:<strong>)?Value(?:</strong>)?.*?<strong>(BUY|HOLD|SELL|STRONG BUY|STRONG SELL)</strong>',
                        "growth": r'📈\s*(?:<strong>)?Growth(?:</strong>)?.*?<strong>(BUY|HOLD|SELL|STRONG BUY|STRONG SELL)</strong>',
                        "aggressive": r'🚀\s*(?:<strong>)?Aggressive(?:</strong>)?.*?<strong>(BUY|HOLD|SELL|STRONG BUY|STRONG SELL)</strong>'
                    }
                    
                    for profile, pattern in profile_patterns.items():
                        match = re.search(pattern, report_content, re.DOTALL | re.IGNORECASE)
                        if match:
                            rec = match.group(1).strip().upper()
                            profile_recs[profile] = rec
                            if rec == "STRONG SELL":
                                strong_sell_count += 1
                            elif rec == "SELL":
                                sell_count += 1
                except Exception as e:
                    logger.error(f"Error parsing comprehensive report for {ticker}: {str(e)}")
            
            # Strong Sell criteria:
            # 1. Overall recommendation is STRONG SELL, or
            # 2. Z-Score is extremely low (below 1.0) and at least one profile has STRONG SELL, or
            # 3. At least 2 investor profiles have STRONG SELL recommendations
            # 4. Z-Score is below 0.5 (extreme distress)
            
            should_include = (
                recommendation.upper() == "STRONG SELL" or 
                (z_score < 1.0 and strong_sell_count > 0) or
                strong_sell_count >= 2 or
                z_score < 0.5
            )
            
            if should_include:
                # Get company name from README.md
                company_name = get_company_name(ticker)
                
                # Extract warning signs if available
                warning_signs = []
                if os.path.exists(report_path):
                    try:
                        with open(report_path, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        # Look for key risks or warnings in the report
                        risk_section = re.search(r'Key Risks:(.*?)(?:<\/div>|<\/section>)', report_content, re.DOTALL)
                        if risk_section:
                            risks_content = risk_section.group(1)
                            # Extract bullet points or individual risks
                            risks = re.findall(r'<li>(.*?)<\/li>|<div[^>]*>(.*?)<\/div>', risks_content, re.DOTALL)
                            for risk in risks:
                                risk_text = risk[0] if risk[0] else risk[1]
                                if risk_text:
                                    # Clean HTML tags and normalize whitespace
                                    risk_text = re.sub(r'<[^>]+>', '', risk_text).strip()
                                    risk_text = re.sub(r'\s+', ' ', risk_text)
                                    if risk_text:
                                        warning_signs.append(risk_text)
                    except Exception as e:
                        logger.error(f"Error extracting warning signs for {ticker}: {str(e)}")
                
                # Limit to top 3 warning signs
                warning_signs = warning_signs[:3] if warning_signs else ["Low Z-Score indicating financial distress"]
                
                company_data.append({
                    "ticker": ticker,
                    "name": company_name,
                    "z_score": z_score,
                    "risk_category": risk_category,
                    "recommendation": recommendation,
                    "profile_recs": profile_recs,
                    "strong_sell_count": strong_sell_count,
                    "sell_count": sell_count,
                    "warning_signs": warning_signs
                })
                logger.info(f"Added {ticker} - {company_name} with Z-Score {z_score} to strong sell recommendations list")
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}")
    
    # Sort by Z-Score (ascending - worst first)
    company_data.sort(key=lambda x: x["z_score"])
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
    Generate HTML file with company cards for strong sell recommendations.
    """
    if not company_data:
        logger.error("No company data to generate HTML")
        return False
    
    current_date = datetime.now().strftime("%B %d, %Y")
    company_count = len(company_data)
    
    # Find highest risk companies (lowest Z-scores)
    highest_risk = company_data[:min(3, len(company_data))]
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STRONG SELL Recommendations | Altman Z-Score Analysis</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #fef2f2;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background-color: #7f0000;
            color: white;
            padding: 30px 0;
            text-align: center;
            border-bottom: 5px solid #560000;
        }}
        .dashboard-title {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .dashboard-subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .urgent-warning {{
            background-color: #fecaca;
            border-left: 5px solid #991b1b;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
            font-weight: 500;
        }}
        .urgent-title {{
            color: #991b1b;
            font-size: 1.2em;
            margin-top: 0;
            margin-bottom: 10px;
        }}
        .summary-stats {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin: 20px 0;
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
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #991b1b;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #7b8a8b;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .highest-risk-section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 1.5em;
            border-bottom: 2px solid #fecaca;
            padding-bottom: 10px;
            margin-bottom: 20px;
            color: #991b1b;
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
            background-color: #991b1b;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
        }}
        .danger-label {{
            background-color: #b91c1c;
            color: white;
            padding: 5px 15px;
            border-radius: 3px;
            font-size: 0.8em;
            position: absolute;
            top: -10px;
            right: 10px;
        }}
        .card-body {{
            padding: 20px;
            position: relative;
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
            margin-bottom: 15px;
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
        .zscore {{
            font-size: 1.8em;
            text-align: center;
            padding: 10px;
            margin: 15px 0;
            font-weight: bold;
            color: #991b1b;
        }}
        .warning-list {{
            background-color: #fef2f2;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
        }}
        .warning-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 8px;
        }}
        .warning-icon {{
            color: #991b1b;
            margin-right: 10px;
            font-weight: bold;
        }}
        .profile-recs {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        .profile-rec {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }}
        .view-link {{
            display: block;
            text-align: center;
            margin-top: 15px;
            padding: 10px;
            background-color: #991b1b;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            transition: background-color 0.3s;
        }}
        .view-link:hover {{
            background-color: #7f0000;
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
            background-color: #fef2f2;
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
            background-color: #7f0000;
            color: #ecf0f1;
        }}
        .footer-text {{
            opacity: 0.7;
            font-size: 0.9em;
        }}
        .sortable {{
            cursor: pointer;
        }}
        .sortable:after {{
            content: " ⇅";
            font-size: 12px;
            color: #7b8a8b;
        }}
        .alert-icon {{
            font-size: 1.2em;
            margin-right: 8px;
        }}
        .critical {{
            color: #991b1b;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <header>
        <h1 class="dashboard-title">STRONG SELL Recommendations</h1>
        <p class="dashboard-subtitle">Altman Z-Score Analysis | {current_date}</p>
    </header>
    
    <div class="container">
        <div class="urgent-warning">
            <h3 class="urgent-title"><span class="alert-icon">⚠️</span> URGENT FINANCIAL DISTRESS WARNING</h3>
            <p>This dashboard identifies stocks showing <strong>severe financial distress</strong> indicators that warrant immediate attention. Companies listed here have extremely low Z-Scores, multiple STRONG SELL recommendations, or critical financial warning signs.</p>
            <p>Always conduct thorough due diligence and consider consulting a financial advisor before making any investment decisions.</p>
        </div>
        
        <section class="summary-stats">
            <h2>Dashboard Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <p class="stat-label">Critical Alerts</p>
                    <p class="stat-value">{company_count}</p>
                </div>
                <div class="stat-card">
                    <p class="stat-label">Average Z-Score</p>
                    <p class="stat-value">{sum(c["z_score"] for c in company_data) / company_count:.2f}</p>
                </div>
                <div class="stat-card">
                    <p class="stat-label">Lowest Z-Score</p>
                    <p class="stat-value">{min(c["z_score"] for c in company_data):.2f}</p>
                </div>
                <div class="stat-card">
                    <p class="stat-label">Strong Sell Signals</p>
                    <p class="stat-value">{sum(c["strong_sell_count"] for c in company_data)}</p>
                </div>
            </div>
        </section>
        
        <section class="highest-risk-section">
            <h2 class="section-title">Critical Financial Risk Companies</h2>
            <div class="card-grid">
"""
    
    # Generate cards for highest risk companies
    for i, company in enumerate(highest_risk):
        html_content += f"""                <div class="company-card">
                    <div class="card-header">
                        <h3>{company["ticker"]}</h3>
                    </div>
                    <div class="card-body">
                        <div class="danger-label">CRITICAL RISK</div>
                        <p class="company-name">{company["name"]}</p>
                        
                        <div class="zscore">Z-Score: {company["z_score"]:.2f}</div>
                        
                        <div class="metrics-grid">
                            <div class="metric">
                                <div class="metric-label">Risk Category</div>
                                <div class="metric-value critical">{company["risk_category"]}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Recommendation</div>
                                <div class="metric-value critical">{company["recommendation"]}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Strong Sell Signals</div>
                                <div class="metric-value">{company["strong_sell_count"]}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Total Sell Signals</div>
                                <div class="metric-value">{company["strong_sell_count"] + company["sell_count"]}</div>
                            </div>
                        </div>
                        
                        <div class="warning-list">
                            <h4>Key Warning Signs:</h4>
"""
        
        # Add warning signs
        for warning in company["warning_signs"]:
            html_content += f"""                            <div class="warning-item">
                                <span class="warning-icon">⚠️</span>
                                <span>{warning}</span>
                            </div>
"""
        
        html_content += f"""                        </div>
                        
                        <div class="profile-recs">
                            <h4>Investor Profile Recommendations:</h4>
"""
        
        # Add profile recommendations
        for profile, rec in company["profile_recs"].items():
            rec_class = "critical" if rec == "STRONG SELL" or rec == "SELL" else ""
            html_content += f"""                            <div class="profile-rec">
                                <span>{profile.title()}</span>
                                <strong class="{rec_class}">{rec}</strong>
                            </div>
"""
        
        html_content += f"""                        </div>
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
                <select id="filterSellSignals" class="filter-dropdown">
                    <option value="all">All</option>
                    <option value="high">3+ Strong Sell Signals</option>
                    <option value="medium">1-2 Strong Sell Signals</option>
                    <option value="low">No Strong Sell Signals</option>
                </select>
            </div>
            
            <table id="companyTable">
                <thead>
                    <tr>
                        <th class="sortable" data-sort="ticker">Ticker</th>
                        <th class="sortable" data-sort="name">Company Name</th>
                        <th class="sortable" data-sort="zscore">Z-Score ↓</th>
                        <th class="sortable" data-sort="risk">Risk Category</th>
                        <th class="sortable" data-sort="recommendation">Recommendation</th>
                        <th class="sortable" data-sort="strongSellCount">Strong Sell Signals</th>
                        <th>Key Warning</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Generate table rows for all companies
    for company in company_data:
        strong_sell_level = "high" if company["strong_sell_count"] >= 3 else "medium" if company["strong_sell_count"] > 0 else "low"
        primary_warning = company["warning_signs"][0] if company["warning_signs"] else "Critical financial distress"
        
        html_content += f"""                    <tr data-ticker="{company["ticker"]}" data-name="{company["name"]}" data-zscore="{company["z_score"]:.2f}" data-risk="{company["risk_category"]}" data-recommendation="{company["recommendation"]}" data-strongsellcount="{company["strong_sell_count"]}" data-sellsignals="{strong_sell_level}">
                        <td>{company["ticker"]}</td>
                        <td>{company["name"]}</td>
                        <td class="critical">{company["z_score"]:.2f}</td>
                        <td>{company["risk_category"]}</td>
                        <td>{company["recommendation"]}</td>
                        <td>{company["strong_sell_count"]}</td>
                        <td>{primary_warning[:50]}{'...' if len(primary_warning) > 50 else ''}</td>
                        <td><a href="output/{company["ticker"]}/{company["ticker"]}_comprehensive_report.html" target="_blank">View</a></td>
                    </tr>
"""
    
    html_content += """                </tbody>
            </table>
        </section>
    </div>
    
    <footer>
        <p>Altman Z-Score Strong Sell Recommendations Dashboard</p>
        <p class="footer-text">Generated on """ + current_date + """</p>
    </footer>
    
    <script>
        // Search and filter functionality
        document.getElementById('searchBox').addEventListener('input', filterTable);
        document.getElementById('filterRisk').addEventListener('change', filterTable);
        document.getElementById('filterSellSignals').addEventListener('change', filterTable);
        
        function filterTable() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const riskFilter = document.getElementById('filterRisk').value;
            const sellSignalsFilter = document.getElementById('filterSellSignals').value;
            
            const rows = document.querySelectorAll('#companyTable tbody tr');
            
            rows.forEach(row => {
                const ticker = row.getAttribute('data-ticker').toLowerCase();
                const name = row.getAttribute('data-name').toLowerCase();
                const risk = row.getAttribute('data-risk');
                const sellSignals = row.getAttribute('data-sellsignals');
                
                const matchesSearch = ticker.includes(searchTerm) || name.includes(searchTerm);
                const matchesRisk = riskFilter === 'all' || risk === riskFilter;
                const matchesSellSignals = sellSignalsFilter === 'all' || sellSignals === sellSignalsFilter;
                
                if (matchesSearch && matchesRisk && matchesSellSignals) {
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
                    let valueA = a.getAttribute(`data-${sortBy.toLowerCase()}`);
                    let valueB = b.getAttribute(`data-${sortBy.toLowerCase()}`);
                    
                    if (sortBy === 'zscore') {
                        valueA = parseFloat(valueA);
                        valueB = parseFloat(valueB);
                    } else if (sortBy === 'strongSellCount') {
                        valueA = parseInt(valueA);
                        valueB = parseInt(valueB);
                    }
                    
                    if (valueA < valueB) return currentOrder === 'asc' ? -1 : 1;
                    if (valueA > valueB) return currentOrder === 'asc' ? 1 : -1;
                    return 0;
                });
                
                // Reappend in sorted order
                rows.forEach(row => tbody.appendChild(row));
            });
        });
        
        // Initial sort by Z-Score ascending (lowest first)
        document.querySelector('th[data-sort="zscore"]').click();
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
    logger.info("Starting Strong Sell Recommendations Dashboard generation...")
    company_data = get_company_data()
    
    if not company_data:
        logger.error("No strong sell recommendations found")
        return
    
    logger.info(f"Found {len(company_data)} companies with strong sell recommendations")
    
    if generate_html(company_data):
        logger.info(f"Strong Sell Recommendations Dashboard successfully generated at {HTML_OUTPUT}")
    
    logger.info("Process completed")

if __name__ == "__main__":
    main()
