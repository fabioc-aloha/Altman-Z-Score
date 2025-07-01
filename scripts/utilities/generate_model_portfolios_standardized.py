#!/usr/bin/env python3
"""
Model-Specific Portfolio Analysis Generator - Standardized Version

This script replaces the original generate_model_portfolios.py with a version that uses
the common dashboard template and styling for consistency.
"""

import os
import sys
import json
import random
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
sys.path.append(PROJECT_ROOT)

# Import from utility modules
from dashboard_generator_utils import generate_dashboard_html, get_common_paths
from assets_manager import ensure_assets_folder

# Try to import from the project's main pipeline for real data
try:
    from altman_zscore.main_pipeline import AltmanZScorePipeline
    REAL_DATA_AVAILABLE = True
except ImportError:
    print("Warning: AltmanZScorePipeline not available, using sample data")
    REAL_DATA_AVAILABLE = False
    
# Always ensure assets folder exists with all required templates
assets_dir = ensure_assets_folder()
    

def create_model_portfolio_dashboard(portfolio_name, model_type, model_description, stocks, output_dir):
    """
    Create an HTML dashboard for a specific model portfolio using the common template
    
    Args:
        portfolio_name: Display name for the portfolio
        model_type: Type of Z-Score model used (e.g., "Original Z-Score", "Z'-Score", etc.)
        model_description: Description of the model and its application
        stocks: List of stock dictionaries with analysis data
        output_dir: Directory to save the output HTML file
    
    Returns:
        Path to the generated HTML file
    """
    # Convert portfolio name to filename
    filename = portfolio_name.lower().replace('&', '_and_').replace(' ', '_') + '.html'
    filepath = os.path.join(output_dir, filename)
    
    # Format current date
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Prepare companies data
    companies = []
    safe_count = 0
    gray_count = 0
    distress_count = 0
    total_z_score = 0
    
    for stock in stocks:
        z_score = stock.get('z_score', 0)
        
        # Count stocks in each zone
        if z_score > 2.99:
            safe_count += 1
        elif z_score < 1.81:
            distress_count += 1
        else:
            gray_count += 1
            
        # Accumulate total Z-Score for average calculation
        total_z_score += z_score
        
        # Format metrics for the company card
        metrics = {
            "Industry": stock.get('industry', 'N/A'),
            "Market Cap": f"${stock.get('market_cap', 0):,.2f}M",
            "P/E Ratio": stock.get('pe_ratio', 'N/A'),
            "ROE": f"{stock.get('roe', 0):.2f}%"
        }
        
        # Create company data dictionary
        company = {
            'name': stock.get('name', 'Unknown Company'),
            'ticker': stock.get('ticker', ''),
            'z_score': round(z_score, 2),
            'metrics': metrics,
            'logo_path': f"output/{stock.get('ticker', '').upper()}/{stock.get('ticker', '').upper()}_logo.png"
        }
        
        companies.append(company)
    
    # Calculate average Z-Score
    avg_z_score = round(total_z_score / len(stocks), 2) if stocks else 0
    
    # Prepare statistics for the stats grid
    stats = {
        "Companies": len(stocks),
        "Safe Zone": safe_count,
        "Gray Zone": gray_count,
        "Distress Zone": distress_count,
        "Avg Z-Score": avg_z_score
    }
    
    # Generate model information HTML
    model_info_html = f"""
    <h3>Model: {model_type}</h3>
    <p>{model_description}</p>
    <p>This dashboard applies the {model_type} specifically designed for {portfolio_name} companies.</p>
    """
    
    # Generate summary text HTML
    summary_text_html = f"""
    <p>This portfolio presents <strong>{portfolio_name}</strong> companies analyzed using the <strong>{model_type}</strong>.</p>
    <p>Among the {len(stocks)} companies analyzed:</p>
    <ul>
        <li>{safe_count} companies are in the <strong>Safe Zone</strong> (Z-Score > 2.99)</li>
        <li>{gray_count} companies are in the <strong>gray Zone</strong> (1.81 ≤ Z-Score ≤ 2.99)</li>
        <li>{distress_count} companies are in the <strong>Distress Zone</strong> (Z-Score < 1.81)</li>
    </ul>
    <p>The average Z-Score across all companies is <strong>{avg_z_score}</strong>.</p>
    """
    
    # Prepare template data
    template_data = {
        'dashboard_title': f"{portfolio_name}",
        'subtitle': f"Industry-specific financial analysis using {model_type}",
        'generation_date': current_date,
        'stats': stats,
        'summary_text': summary_text_html,
        'model_info': model_info_html,
        'companies': companies
    }
    
    # Generate the complete dashboard HTML
    dashboard_html = generate_dashboard_html(template_data)
    
    # Write the HTML to file
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    return filepath

def generate_model_portfolios_index(portfolios, output_dir):
    """
    Create an index page for all model portfolios
    
    Args:
        portfolios: List of portfolio dictionaries
        output_dir: Directory to save the output HTML file
    
    Returns:
        Path to the generated HTML file
    """
    # Implementation details for the index page...
    # This would be similar but simpler than the individual portfolio pages
    # We could expand this later if needed
    pass

def load_stock_data(industry_type=None):
    """
    Load stock data from available sources:
    1. Try to load from output/*.json files
    2. If not available, generate sample data
    
    Args:
        industry_type: Optional industry to filter by
        
    Returns:
        List of stock dictionaries
    """
    paths = get_common_paths()
    project_root = paths["project_root"]
    output_dir = os.path.join(project_root, "output")
    
    # Try to load from strong_buy_picks.json as a data source
    json_sources = [
        os.path.join(output_dir, "strong_buy_picks.json"),
        os.path.join(output_dir, "value_picks.json"),
        os.path.join(output_dir, "growth_picks.json"),
        os.path.join(output_dir, "conservative_picks.json")
    ]
    
    all_stocks = []
    
    for json_path in json_sources:
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stocks = data.get("companies", [])
                    all_stocks.extend(stocks)
                    if len(all_stocks) > 30:  # Enough data
                        break
            except Exception as e:
                print(f"Error loading {json_path}: {e}")
    
    # Filter by industry if specified
    if industry_type and all_stocks:
        filtered_stocks = [s for s in all_stocks if industry_type.lower() in s.get('industry', '').lower()]
        # If we got at least some stocks, use them, otherwise use all stocks
        if len(filtered_stocks) >= 5:
            all_stocks = filtered_stocks
    
    # If we couldn't get enough stocks, generate sample data
    if len(all_stocks) < 10:
        print(f"Insufficient stock data found, generating sample data for {industry_type if industry_type else 'all industries'}")
        all_stocks = generate_sample_stocks(industry_type)
    
    # Limit to 30 stocks and ensure they have all required fields
    stocks = all_stocks[:30]
    for stock in stocks:
        if 'name' not in stock:
            stock['name'] = f"{stock.get('ticker', 'UNKNOWN')} Inc."
        if 'industry' not in stock:
            stock['industry'] = industry_type if industry_type else "General Industry"
        if 'z_score' not in stock:
            stock['z_score'] = round(random.uniform(1.0, 5.0), 2)
        if 'market_cap' not in stock:
            stock['market_cap'] = round(random.uniform(100, 10000), 2)
        if 'pe_ratio' not in stock:
            stock['pe_ratio'] = round(random.uniform(5, 40), 2)
        if 'roe' not in stock:
            stock['roe'] = round(random.uniform(5, 25), 2)
    
    return stocks

def generate_sample_stocks(industry_type=None):
    """
    Generate sample stock data for demonstration purposes
    
    Args:
        industry_type: Type of industry to generate stocks for
        
    Returns:
        List of sample stock dictionaries
    """
    # Sample tickers by industry
    industry_tickers = {
        "manufacturing": ["MMM", "CAT", "DE", "GE", "HON", "LMT", "RTX", "ETN", "EMR", "ITW", "PH", "ROK", "IR", "SWK", "TT"],
        "technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA", "NVDA", "INTC", "CSCO", "ADBE", "CRM", "AMD", "QCOM", "TXN", "IBM"],
        "retail": ["WMT", "TGT", "COST", "HD", "LOW", "AMZN", "EBAY", "ETSY", "JWN", "M", "DG", "DLTR", "BBY", "KR", "ULTA"],
        "financial": ["JPM", "BAC", "C", "WFC", "GS", "MS", "AXP", "V", "MA", "BLK", "SCHW", "COF", "USB", "PNC", "TFC"],
        "utilities": ["NEE", "DUK", "SO", "D", "AEP", "XEL", "ED", "EXC", "SRE", "PCG", "WEC", "ES", "PEG", "DTE", "CMS"],
        "private": ["BF-B", "CHTR", "DELL", "KKR", "BX", "APO", "CG", "CBRE", "JLL", "SPGI", "MCO", "INFO", "FAF", "MTG", "RDN"],
        "emerging": ["BABA", "JD", "PDD", "BIDU", "TCEHY", "NTES", "MELI", "SE", "GRAB", "DIDI", "CPNG", "NU", "TSM", "VIPS", "WB"]
    }
    
    # Default industry if none specified
    if not industry_type:
        industry_type = random.choice(list(industry_tickers.keys()))
    
    # Try to match industry_type to our categories
    matched_industry = None
    for key in industry_tickers.keys():
        if key in industry_type.lower():
            matched_industry = key
            break
    
    # Use matched industry or default to first category
    tickers = industry_tickers.get(matched_industry or list(industry_tickers.keys())[0], [])
    
    # Generate sample stocks
    stocks = []
    company_names = {
        "MMM": "3M Company",
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "AMZN": "Amazon.com, Inc.",
        "GOOGL": "Alphabet Inc.",
        "FB": "Meta Platforms, Inc.",
        "TSLA": "Tesla, Inc.",
        "NVDA": "NVIDIA Corporation",
        "JPM": "JPMorgan Chase & Co.",
        "BAC": "Bank of America Corporation",
        "WMT": "Walmart Inc.",
        "TGT": "Target Corporation",
        "NEE": "NextEra Energy, Inc.",
        "DUK": "Duke Energy Corporation"
    }
    
    for ticker in tickers[:20]:  # Limit to 20 stocks
        # Generate realistic Z-Score based on industry
        if matched_industry == "technology" or matched_industry == "retail":
            z_score = round(random.uniform(2.0, 4.5), 2)  # Higher scores for tech/retail
        elif matched_industry == "financial":
            z_score = round(random.uniform(1.5, 3.0), 2)  # Lower scores for financials
        else:
            z_score = round(random.uniform(1.8, 3.8), 2)  # Average scores for others
        
        stock = {
            "ticker": ticker,
            "name": company_names.get(ticker, f"{ticker} Inc."),
            "z_score": z_score,
            "industry": industry_type.title() if industry_type else "General Industry",
            "market_cap": round(random.uniform(1000, 100000), 2),
            "pe_ratio": round(random.uniform(10, 35), 2),
            "roe": round(random.uniform(5, 25), 2),
            "risk_score": round(random.uniform(0, 10), 2),
            "growth_score": round(random.uniform(0, 10), 2),
            "value_score": round(random.uniform(0, 10), 2)
        }
        stocks.append(stock)
    
    return stocks

def main():
    """Main execution function"""
    # Get common paths
    paths = get_common_paths()
    web_dir = paths["web_dir"]
    
    # Ensure the web directory exists
    os.makedirs(web_dir, exist_ok=True)
    
    # Ensure assets folder exists
    ensure_assets_folder()
    
    # Define model portfolios
    model_portfolios = [
        {
            "name": "Manufacturing & Industrial",
            "model_type": "Original Z-Score",
            "description": "The original Altman Z-Score model developed in 1968, optimized for public manufacturing companies.",
            "industry": "manufacturing"
        },
        {
            "name": "Private & Service Companies",
            "model_type": "Z'-Score",
            "description": "An adaptation of the Z-Score that eliminates the market value/book value ratio, making it suitable for private firms and non-manufacturing sectors.",
            "industry": "private"
        },
        {
            "name": "Emerging Markets",
            "model_type": "Z\"-Score",
            "description": "Modified version for emerging markets that removes the sensitivity to industry and country variations by eliminating the sales/total assets ratio.",
            "industry": "emerging"
        },
        {
            "name": "Financial Institutions",
            "model_type": "CAMELS Framework",
            "description": "Specialized framework for banks and financial institutions that evaluates Capital adequacy, Asset quality, Management, Earnings, Liquidity, and Sensitivity to market risk.",
            "industry": "financial"
        },
        {
            "name": "Regulated Utilities",
            "model_type": "Utilities Z-Score",
            "description": "Adjusted model for regulated utilities that accounts for their stable cash flows, capital structure, and regulatory environment.",
            "industry": "utilities"
        },
        {
            "name": "Technology & Growth",
            "model_type": "Growth-Adjusted Z-Score",
            "description": "Enhanced model for high-growth technology companies that incorporates R&D spending, intellectual property value, and growth trajectory metrics.",
            "industry": "technology"
        },
        {
            "name": "Retail & Consumer",
            "model_type": "Retail Z-Score",
            "description": "Specialized model for retail companies that places greater emphasis on inventory turnover, seasonality, and consumer spending patterns.",
            "industry": "retail"
        }
    ]
    
    # Generate dashboard for each portfolio
    for portfolio in model_portfolios:
        # Load stocks for this industry
        stocks = load_stock_data(portfolio.get("industry"))
        
        filepath = create_model_portfolio_dashboard(
            portfolio["name"], 
            portfolio["model_type"],
            portfolio["description"],
            stocks,
            web_dir
        )
        print(f"Generated {portfolio['name']} dashboard: {filepath}")
    
    print("All model portfolios generated successfully!")

if __name__ == "__main__":
    main()
