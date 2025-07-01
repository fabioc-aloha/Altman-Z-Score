#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Special Dashboard Generator for Strong Buy/Sell pages - Standardized Version

This script creates the strong buy, sell, and strong sell dashboards using the
standardized dashboard template and utilities. It ensures company logos display correctly
and maintains a consistent look and feel across all dashboard types.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path to allow imports
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Import the dashboard generator utilities
# Use a relative import since we're in the same package
from dashboard_generator_utils import generate_dashboard_html, get_common_paths
from assets_manager import ensure_assets_folder

# Import version information
try:
    from altman_zscore._version import __version__
except ImportError:
    __version__ = "Unknown"

def load_companies(portfolio_type):
    """
    Load company data for the specified portfolio type.
    
    Args:
        portfolio_type: String representing the portfolio type ('strong_buy', 'sell', 'strong_sell')
    
    Returns:
        List of company dictionaries
    """
    # Define paths
    paths = get_common_paths()
    project_root = paths["project_root"]
    output_dir = project_root / "output"
    
    # Define file paths for different portfolio types
    if portfolio_type == "strong_buy":
        json_path = output_dir / "strong_buy_picks.json"
    elif portfolio_type == "strong_sell":
        json_path = output_dir / "strong_sell_picks.json"
    elif portfolio_type == "sell":
        json_path = output_dir / "sell_picks.json"
    else:
        print(f"Unknown portfolio type: {portfolio_type}")
        return []
    
    # Load and return company data
    try:
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("companies", [])
        else:
            print(f"Warning: {json_path} not found")
            return []
    except Exception as e:
        print(f"Error loading companies from {json_path}: {str(e)}")
        return []

def create_special_dashboard(portfolio_type, title, description):
    """
    Create a standardized dashboard for special portfolio types.
    
    Args:
        portfolio_type: Type of portfolio ('strong_buy', 'sell', 'strong_sell')
        title: Dashboard title
        description: Dashboard description
    
    Returns:
        Path to the generated HTML file
    """
    # Get common paths
    paths = get_common_paths()
    web_dir = paths["web_dir"]
    
    # Define output filename
    if portfolio_type == "strong_buy":
        output_filename = "strong_buys.html"
    elif portfolio_type == "strong_sell":
        output_filename = "strong_sell_picks.html"
    elif portfolio_type == "sell":
        output_filename = "sell_picks.html"
    else:
        output_filename = f"{portfolio_type}_picks.html"
    
    output_path = web_dir / output_filename
    
    # Load company data
    companies = load_companies(portfolio_type)
    
    if not companies:
        print(f"No companies found for {portfolio_type}, skipping dashboard generation")
        return None
    
    # Format companies for the template
    company_data = []
    safe_count = 0
    gray_count = 0
    distress_count = 0
    
    for company in companies:
        z_score = company.get('z_score', 0)
        
        # Count companies in each zone
        if z_score > 2.99:
            safe_count += 1
        elif z_score < 1.81:
            distress_count += 1
        else:
            gray_count += 1
        
        # Format metrics for display
        metrics = {
            "Industry": company.get('industry', 'N/A'),
            "Market Cap": f"${company.get('market_cap', 0):,.2f}M",
            "P/E Ratio": f"{company.get('pe_ratio', 'N/A')}",
            "ROE": f"{company.get('roe', 0):.2f}%"
        }
        
        # Add stock-specific metrics based on portfolio type
        if portfolio_type == "strong_buy":
            metrics["Growth Score"] = f"{company.get('growth_score', 0):.2f}"
            metrics["Value Score"] = f"{company.get('value_score', 0):.2f}"
        elif portfolio_type in ["sell", "strong_sell"]:
            metrics["Risk Score"] = f"{company.get('risk_score', 0):.2f}"
            metrics["Debt Ratio"] = f"{company.get('debt_ratio', 0):.2f}"
        
        # Create standardized company data
        company_data.append({
            'name': company.get('name', 'Unknown Company'),
            'ticker': company.get('ticker', ''),
            'z_score': round(z_score, 2),
            'metrics': metrics,
            'logo_path': f"output/{company.get('ticker', '').upper()}/{company.get('ticker', '').upper()}_logo.png"
        })
    
    # Generate statistics for the dashboard
    stats = {
        "Companies": len(companies),
        "Safe Zone": safe_count,
        "Gray Zone": gray_count,
        "Distress Zone": distress_count
    }
    
    # Add portfolio-specific stats
    if portfolio_type == "strong_buy":
        stats["Avg Growth"] = f"{sum(c.get('growth_score', 0) for c in companies) / len(companies):.2f}"
        stats["Avg Value"] = f"{sum(c.get('value_score', 0) for c in companies) / len(companies):.2f}"
    elif portfolio_type in ["sell", "strong_sell"]:
        stats["Avg Risk"] = f"{sum(c.get('risk_score', 0) for c in companies) / len(companies):.2f}"
    
    # Generate summary text
    summary_html = f"""
    <p>{description}. This dashboard presents {len(companies)} companies that meet the criteria.</p>
    <p>The distribution of companies by financial health:</p>
    <ul>
        <li>{safe_count} companies in the <strong>Safe Zone</strong> (Z-Score > 2.99)</li>
        <li>{gray_count} companies in the <strong>gray Zone</strong> (1.81 ≤ Z-Score ≤ 2.99)</li>
        <li>{distress_count} companies in the <strong>Distress Zone</strong> (Z-Score < 1.81)</li>
    </ul>
    """
    
    # Add portfolio-specific summaries
    if portfolio_type == "strong_buy":
        summary_html += """
        <p>These companies represent our highest-conviction investment opportunities based on:
        <ul>
            <li>Strong financial health indicated by Altman Z-Score</li>
            <li>Solid growth metrics and forward-looking potential</li>
            <li>Attractive valuation relative to industry peers</li>
        </ul>
        </p>
        """
    elif portfolio_type == "strong_sell":
        summary_html += """
        <p>These companies show significant warning signs indicating:
        <ul>
            <li>Severe financial distress indicated by low Altman Z-Score</li>
            <li>High debt levels relative to earnings capability</li>
            <li>Deteriorating fundamental metrics</li>
        </ul>
        <p><strong>Important:</strong> This analysis is based on quantitative metrics and should be supplemented with qualitative research.</p>
        </p>
        """
    elif portfolio_type == "sell":
        summary_html += """
        <p>These companies show warning signs that warrant consideration for selling:
        <ul>
            <li>Financial metrics indicating potential distress</li>
            <li>Unfavorable risk-to-reward profile</li>
            <li>Concerning trends in key performance indicators</li>
        </ul>
        <p><strong>Note:</strong> Each position should be evaluated in the context of your overall portfolio strategy.</p>
        </p>
        """
    
    # Define model information if applicable
    model_info = ""
    if portfolio_type in ["sell", "strong_sell"]:
        model_info = """
        <h3>Warning Model</h3>
        <p>This dashboard utilizes enhanced distress detection that combines traditional Altman Z-Score with 
        additional risk metrics to identify companies with concerning financial indicators.</p>
        """
    
    # Create template data
    template_data = {
        'dashboard_title': title,
        'subtitle': f"Generated with Altman Z-Score Analysis v{__version__}",
        'generation_date': datetime.now().strftime('%B %d, %Y'),
        'stats': stats,
        'summary_text': summary_html,
        'model_info': model_info,
        'companies': company_data
    }
    
    # Generate the dashboard HTML
    html_content = generate_dashboard_html(template_data)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated {portfolio_type} dashboard: {output_path}")
    return output_path

def main():
    """Main execution function"""
    # Get common paths
    paths = get_common_paths()
    web_dir = paths["web_dir"]
    
    # Ensure the web directory exists
    os.makedirs(web_dir, exist_ok=True)
    
    # Ensure assets folder exists with required templates and CSS
    ensure_assets_folder()
    
    print("Generating special dashboards with standardized template...")
    
    # Generate Strong Buy dashboard
    create_special_dashboard(
        portfolio_type="strong_buy",
        title="Strong Buy Recommendations",
        description="High-conviction investment opportunities with strong fundamentals"
    )
    
    # Generate Strong Sell dashboard
    create_special_dashboard(
        portfolio_type="strong_sell", 
        title="Strong Sell Recommendations",
        description="Companies with concerning financial metrics that may warrant selling"
    )
    
    # Generate Sell dashboard
    create_special_dashboard(
        portfolio_type="sell",
        title="Sell Recommendations",
        description="Companies requiring careful consideration for sell decisions"
    )
    
    print("All special dashboards generated successfully!")

if __name__ == "__main__":
    main()
