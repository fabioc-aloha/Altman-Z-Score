#!/usr/bin/env python3
"""
Simple README Table Generator for Altman Z-Score v4.3.0
Creates a clean, compatible Markdown table without complex HTML styling.
"""

import os
import re
import json
from pathlib import Path

# Constants
OUTPUT_DIR = "output"
REPORT_SUFFIX = "_comprehensive_report.html"
JSON_SUFFIX = "_zscore_data.json"

def safe_print(message):
    """Safe print function that handles encoding issues."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('ascii', 'ignore').decode('ascii'))

def get_company_info_from_json(json_path):
    """Extract company information from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle list format (get first element)
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        ticker = data.get('ticker', 'N/A')
        
        # Simple company name mapping for common tickers
        company_names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'GOOG': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NVDA': 'NVIDIA Corporation',
            'NFLX': 'Netflix Inc.',
            'JPM': 'JPMorgan Chase & Co.',
            'GS': 'Goldman Sachs Group Inc.',
            'BK': 'Bank of New York Mellon Corp.',
            'AVGO': 'Broadcom Inc.',
            '005930.KS': 'Samsung Electronics Co., Ltd.',
            'BABA': 'Alibaba Group Holding Ltd.',
            'TSM': 'Taiwan Semiconductor Manufacturing Company',
            'ASML': 'ASML Holding N.V.',
            'LIN': 'Linde plc',
            'TM': 'Toyota Motor Corporation',
            'UNH': 'UnitedHealth Group Inc.'
        }
        
        company_name = company_names.get(ticker, ticker)
        
        return company_name, ticker
    except Exception as e:
        safe_print(f"Error reading JSON {json_path}: {e}")
        return "Unknown Company", "N/A"

def get_zscore_and_recommendation(json_path):
    """Extract Z-Score and recommendation from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle list format (get first element)
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        
        # Get Z-Score from analysis_summary
        analysis = data.get('analysis_summary', {})
        zscore = analysis.get('z_score', 'N/A')
        risk_category = analysis.get('risk_category', 'Unknown')
        
        if zscore != 'N/A':
            zscore = round(float(zscore), 2)
        
        # Determine recommendation based on Z-Score
        if zscore == 'N/A':
            recommendation = "HOLD"
            risk_zone = "Unknown"
        elif zscore >= 3.0:
            recommendation = "STRONG BUY"
            risk_zone = "Safe"
        elif zscore >= 1.8:
            recommendation = "HOLD"
            risk_zone = "Gray Zone"
        else:
            recommendation = "SELL"
            risk_zone = "Distress"
        
        # Use risk_category from data if available
        if risk_category and risk_category != 'Unknown':
            risk_zone = risk_category
        
        return zscore, recommendation, risk_zone
    except Exception as e:
        safe_print(f"Error processing Z-Score from {json_path}: {e}")
        return 'N/A', "HOLD", "Unknown", "⚖️"

def generate_simple_table():
    """Generate a simple, clean table for README."""
    rows = []
    
    if not os.path.exists(OUTPUT_DIR):
        safe_print(f"Warning: Output directory '{OUTPUT_DIR}' not found")
        return rows
    
    for ticker in sorted(os.listdir(OUTPUT_DIR)):
        ticker_dir = os.path.join(OUTPUT_DIR, ticker)
        if not os.path.isdir(ticker_dir):
            continue
        
        # Check for required files
        json_path = os.path.join(ticker_dir, f"{ticker}{JSON_SUFFIX}")
        report_path = os.path.join(ticker_dir, f"{ticker}{REPORT_SUFFIX}")
        
        if not (os.path.exists(json_path) and os.path.exists(report_path)):
            safe_print(f"Warning: Missing required files for {ticker}, skipping")
            continue
        
        # Get company information
        company_name, ticker_code = get_company_info_from_json(json_path)
        zscore, recommendation, risk_zone = get_zscore_and_recommendation(json_path)
        
        # Create relative paths
        report_rel = f"output/{ticker}/{ticker}{REPORT_SUFFIX}"
        
        # Format company cell (simple format)
        company_cell = f"**{ticker}**<br/>{company_name}"
        
        # Format recommendation cell with better compatibility
        recommendation_cell = f"**{recommendation}**<br/>*Z-Score: {zscore} ({risk_zone})*"
        
        # Create the row with text-based indicators for maximum compatibility
        row = f"| {company_cell} | [View Report]({report_rel}) | {recommendation_cell} |"
        rows.append(row)
    
    safe_print(f"Generated simple table with {len(rows)} companies")
    return rows

def create_simple_table_file(filename="table_simple.md"):
    """Create a simple table file."""
    table_rows = generate_simple_table()
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("| Company | Report | Investment Recommendation |\n")
        f.write("|---------|--------|----------------------------|\n")
        for row in table_rows:
            f.write(f"{row}\n")
    
    safe_print(f"Simple table saved to {filename}")
    return len(table_rows)

def update_readme_with_simple_table(readme_path="README.md"):
    """Update README with the simplified table."""
    
    # Generate the simple table
    table_rows = generate_simple_table()
    
    if not table_rows:
        safe_print("No table rows generated, skipping README update")
        return
    
    try:
        # Read current README
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
        
        # Create the new table content
        table_content = "| Company | Report | Investment Recommendation |\n"
        table_content += "|---------|--------|----------------------------|\n"
        for row in table_rows:
            table_content += f"{row}\n"
        
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
            
            # Write the updated README
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            
            safe_print(f"✅ README updated successfully with {len(table_rows)} companies")
            
        else:
            safe_print("❌ Table markers not found in README.md")
            safe_print("Please ensure the README contains:")
            safe_print("<!-- BEGIN_TICKERS_TABLE -->")
            safe_print("<!-- END_TICKERS_TABLE -->")
            
    except Exception as e:
        safe_print(f"❌ Error updating README: {e}")

def main():
    """Main function."""
    print("🔄 Generating simplified README table...")
    
    # Update README with simple table
    update_readme_with_simple_table()
    
    # Also create a standalone simple table file
    create_simple_table_file()
    
    print("✅ Simple table generation complete!")

if __name__ == "__main__":
    main()
