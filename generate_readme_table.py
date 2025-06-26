#!/usr/bin/env python3
"""
README Table Generator - Update portfolio table with latest analysis results

Automatically generates and updates the comprehensive portfolio table in README.md
with the latest Z-Score analysis results, company logos, and investment recommendations.

Usage:
    python generate_readme_table.py

Features:
- Extracts company names and logos from HTML reports
- Generates investment recommendations based on Z-Score thresholds
- Creates interactive dashboard links
- Updates README.md automatically between markers
- Supports the new file structure (HTML reports, interactive dashboards)
"""

import os
import json
import re
import sys
from pathlib import Path

# Ensure we can import from the altman_zscore package
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = "output"
# File structure for new analysis pipeline
REPORT_SUFFIX = "_comprehensive_report.html"
DASHBOARD_SUFFIX = "_zscore_dashboard.html"
JSON_SUFFIX = "_zscore_data.json"
CSV_SUFFIX = "_zscore_report.csv"


def get_company_info_from_html(html_path):
    """Extract company name and logo path from HTML report."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract company name from <h2> tag pattern: "Company Name (TICKER)"
        name_pattern = r'<h2>([^<]+)\s*\(([^)]+)\)</h2>'
        name_match = re.search(name_pattern, content)
        
        if name_match:
            company_name = name_match.group(1).strip()
            ticker = name_match.group(2).strip()
        else:
            # Fallback to ticker from filename
            ticker = os.path.basename(html_path).split('_')[0]
            company_name = ticker
        
        # Check for local logo file in the same directory
        logo_filename = f"{ticker}_logo.png"
        logo_path = os.path.join(os.path.dirname(html_path), logo_filename)
        
        if os.path.exists(logo_path):
            # Use relative path for GitHub display
            logo_url = f"output/{ticker}/{logo_filename}"
        else:
            # Fallback to extract logo URL from img src
            logo_pattern = r'<img src="([^"]+)" alt="[^"]*Logo"'
            logo_match = re.search(logo_pattern, content)
            logo_url = logo_match.group(1) if logo_match else None
        
        return company_name, logo_url, ticker
        
    except Exception as e:
        # Fallback to ticker from filename
        ticker = os.path.basename(html_path).split('_')[0]
        return ticker, None, ticker


def extract_investment_recommendation_from_json(json_path):
    """Extract investment recommendation from Z-Score JSON data."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            analysis = data[0]
        else:
            analysis = data
        
        # Extract Z-Score and risk category
        summary = analysis.get("analysis_summary", {})
        z_score = summary.get("z_score", 0)
        risk_category = summary.get("risk_category", "Unknown")
        
        # Generate recommendation based on Z-Score thresholds
        if z_score > 2.99:
            return f"📈 STRONG BUY<br/><sub>Z-Score: {z_score:.2f} ({risk_category})</sub>"
        elif z_score > 1.8:
            return f"⚖️ HOLD<br/><sub>Z-Score: {z_score:.2f} ({risk_category})</sub>"
        else:
            return f"📉 SELL<br/><sub>Z-Score: {z_score:.2f} ({risk_category})</sub>"
            
    except Exception as e:
        return f"❌ Error: {str(e)[:30]}..."


def has_required_files(ticker_dir, ticker):
    """Check if ticker directory has all required files for new structure."""
    report = os.path.join(ticker_dir, f"{ticker}{REPORT_SUFFIX}")
    dashboard = os.path.join(ticker_dir, f"{ticker}{DASHBOARD_SUFFIX}")
    json_file = os.path.join(ticker_dir, f"{ticker}{JSON_SUFFIX}")
    
    return all(os.path.isfile(f) for f in [report, dashboard, json_file])


def generate_table():
    """Generate the table for README with new file structure."""
    rows = []
    
    if not os.path.exists(OUTPUT_DIR):
        print(f"Warning: Output directory '{OUTPUT_DIR}' not found")
        return rows
    
    for ticker in sorted(os.listdir(OUTPUT_DIR)):
        ticker_dir = os.path.join(OUTPUT_DIR, ticker)
        if not os.path.isdir(ticker_dir):
            continue
        if not has_required_files(ticker_dir, ticker):
            print(f"Warning: Missing required files for {ticker}, skipping")
            continue
        
        # File paths for new structure
        report_rel = f"output/{ticker}/{ticker}{REPORT_SUFFIX}"
        dashboard_rel = f"output/{ticker}/{ticker}{DASHBOARD_SUFFIX}"
        json_path = os.path.join(ticker_dir, f"{ticker}{JSON_SUFFIX}")
        html_path = os.path.join(ticker_dir, f"{ticker}{REPORT_SUFFIX}")
        
        # Extract company information from HTML report
        company_name, logo_url, ticker_code = get_company_info_from_html(html_path)
        investment_rec = extract_investment_recommendation_from_json(json_path)
        
        # Create logo display (use logo_url if available, otherwise use a placeholder)
        if logo_url:
            logo_display = f'<img src="{logo_url}" alt="{ticker}" width="40" style="margin-right:8px; border-radius:4px;"/>'
        else:
            logo_display = f'<div style="width:40px;height:40px;background:#2c3e50;color:white;display:flex;align-items:center;justify-content:center;margin-right:8px;font-weight:bold;border-radius:4px;">{ticker}</div>'
        
        # Combine logo and company name in one column
        logo_and_name = f'<div style="display: flex; align-items: center;">{logo_display} <span>{company_name}</span></div>'
        
        # Create dashboard preview (using iframe for interactive chart)
        dashboard_preview = f'<a href="{dashboard_rel}" target="_blank"><div style="border:1px solid #ddd;padding:10px;text-align:center;border-radius:4px;background:#f8f9fa;">📊 Interactive Dashboard<br/><small>Click to view full dashboard</small></div></a>'
        
        row = f'| {logo_and_name} | [Full Report]({report_rel}) | {dashboard_preview} | {investment_rec} |'
        rows.append(row)
        
    print(f"Generated table with {len(rows)} companies")
    return rows


def save_table_to_file(filename):
    """Save the generated table to a file."""
    table_rows = generate_table()
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("| Company | Report | Dashboard | Investment Recommendation |\n")
        f.write("|---------|--------|:---------:|---------------------------|\n")
        for row in table_rows:
            f.write(f"{row}\n")
    print(f"Table saved to {filename}")
    return len(table_rows)


def update_readme(readme_path="README.md", table_path="table.md"):
    """Update the tickers table in the README file using the markers."""
    try:
        # Read the current README content
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
        
        # Read the generated table
        with open(table_path, "r", encoding="utf-8") as f:
            table_content = f.read()
        
        # Define the markers
        start_marker = "<!-- BEGIN_TICKERS_TABLE -->"
        end_marker = "<!-- END_TICKERS_TABLE -->"
        
        # Find the positions of the markers
        start_pos = readme_content.find(start_marker)
        end_pos = readme_content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Extract the content before and after the markers
            before_table = readme_content[:start_pos + len(start_marker)]
            after_table = readme_content[end_pos:]
            
            # Create the updated README content
            updated_content = f"{before_table}\n{table_content}{after_table}"
            
            # Write the updated content back to README.md
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            print(f"Successfully updated table in {readme_path}")
            return True
        else:
            print(f"Could not find markers in {readme_path}. Table not updated.")
            print("Make sure your README.md contains the markers:")
            print(f"  {start_marker}")
            print(f"  {end_marker}")
            return False
            
    except Exception as e:
        print(f"Error updating README: {e}")
        return False


def main():
    """Main entry point for the README table generator."""
    print("🔄 Generating README Portfolio Table")
    print("=" * 50)
    
    # Generate the table and save to file
    table_count = save_table_to_file("table.md")
    
    if table_count > 0:
        # Try to update the README
        success = update_readme()
        
        if success:
            print("✅ README table successfully updated!")
            print(f"📊 Portfolio now includes {table_count} companies")
        else:
            print("❌ Failed to update README, but table.md was generated")
    else:
        print("⚠️  No companies found in output directory")
        print("   Run some analyses first: python main.py AAPL MSFT TSLA")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
