import os
import json
import re

OUTPUT_DIR = "output"
LOGO_SUFFIX = "_logo.png"
REPORT_PREFIX = "zscore_"
REPORT_SUFFIX = "_zscore_full_report.md"
CHART_SUFFIX = "_trend.png"
COMPANY_INFO = "company_info.json"


def get_company_name(info_path):
    try:
        with open(info_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Try both 'name' and fallback to uppercase ticker if not present
            return data.get("name") or os.path.basename(os.path.dirname(info_path))
    except Exception:
        return os.path.basename(os.path.dirname(info_path))


def extract_investor_advice(report_path):
    """Extract the investor recommendation summary from the report."""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for the recommendation summary pattern
        # Pattern 1: > **Recommendation: BUY across all investor profiles...
        pattern1 = r'> \*\*Recommendation(?:\s+Summary)?:\s*([^*]+?)\*\*'
        match1 = re.search(pattern1, content, re.IGNORECASE | re.DOTALL)
        
        if match1:
            advice = match1.group(1).strip()
            # Clean up the text and limit length
            advice = re.sub(r'\s+', ' ', advice)  # Replace multiple whitespace with single space
            # Extract the key recommendation (BUY, SELL, HOLD)
            if 'BUY' in advice.upper():
                if 'SELL' in advice.upper() and 'avoid' in advice.lower():
                    return "📈 BUY (Most Profiles)"
                else:
                    return "📈 BUY"
            elif 'SELL' in advice.upper():
                return "📉 SELL/HOLD"
            elif 'HOLD' in advice.upper():
                return "⚖️ HOLD"
            else:
                # Fallback: return first 50 characters
                return advice[:50] + "..." if len(advice) > 50 else advice
        
        # Pattern 2: Look for the table and extract the most common recommendation
        table_pattern = r'\|\s*Investment Profile\s*\|\s*Risk Tolerance\s*\|\s*Recommendation\s*\|.*?\n(.*?)(?=\n\s*>|\n\s*###|\n\s*---|\Z)'
        table_match = re.search(table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if table_match:
            table_content = table_match.group(1)
            # Count recommendations
            buy_count = len(re.findall(r'\|\s*Buy\s*\|', table_content, re.IGNORECASE))
            sell_count = len(re.findall(r'\|\s*Sell\s*\|', table_content, re.IGNORECASE))
            hold_count = len(re.findall(r'\|\s*Hold\s*\|', table_content, re.IGNORECASE))
            
            total_recommendations = buy_count + sell_count + hold_count
            if total_recommendations > 0:
                if buy_count > sell_count and buy_count > hold_count:
                    return f"📈 BUY ({buy_count}/{total_recommendations})"
                elif sell_count > buy_count and sell_count > hold_count:
                    return f"📉 SELL ({sell_count}/{total_recommendations})"
                elif hold_count > buy_count and hold_count > sell_count:
                    return f"⚖️ HOLD ({hold_count}/{total_recommendations})"
                else:
                    return f"📊 MIXED ({buy_count}B/{hold_count}H/{sell_count}S)"
        
        return "❓ No Data"
        
    except Exception as e:
        return f"❌ Error"

def has_all_files(ticker_dir, ticker):
    logo = os.path.join(ticker_dir, f"{ticker}{LOGO_SUFFIX}")
    report = os.path.join(ticker_dir, f"{REPORT_PREFIX}{ticker}{REPORT_SUFFIX}")
    chart = os.path.join(ticker_dir, f"{REPORT_PREFIX}{ticker}{CHART_SUFFIX}")
    info = os.path.join(ticker_dir, COMPANY_INFO)
    return all(os.path.isfile(f) for f in [logo, report, chart, info])

def generate_table():
    rows = []
    for ticker in sorted(os.listdir(OUTPUT_DIR)):
        ticker_dir = os.path.join(OUTPUT_DIR, ticker)
        if not os.path.isdir(ticker_dir):
            continue
        if not has_all_files(ticker_dir, ticker):
            continue
        
        logo_rel = f"output/{ticker}/{ticker}{LOGO_SUFFIX}"
        report_rel = f"output/{ticker}/{REPORT_PREFIX}{ticker}{REPORT_SUFFIX}"
        chart_rel = f"output/{ticker}/{REPORT_PREFIX}{ticker}{CHART_SUFFIX}"
        info_path = os.path.join(ticker_dir, COMPANY_INFO)
        report_path = os.path.join(ticker_dir, f"{REPORT_PREFIX}{ticker}{REPORT_SUFFIX}")
        
        company_name = get_company_name(info_path)
        investor_advice = extract_investor_advice(report_path)
        
        # Display actual chart image instead of just a link, maintaining original proportions by setting only width
        row = f'| <img src="{logo_rel}" alt="{ticker}" width="80" height="80"/> | {company_name} | [Report]({report_rel}) | <a href="{chart_rel}"><img src="{chart_rel}" alt="{ticker} Chart" width="400"/></a> | {investor_advice} |'
        rows.append(row)
    return rows

def save_table_to_file(filename):
    """Save the generated table to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("| Logo | Company Name | Full Report | Trend Chart | Investor Advice |\n")
        f.write("|------|-------------|-------------|:-------------:|:---------------:|\n")
        for row in generate_table():
            f.write(f"{row}\n")
    print(f"Table saved to {filename}")

def update_readme(readme_path="README.md", table_path="table.md"):
    """Update the tickers table in the README file using the markers."""
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
        return False

def main():
    # Generate the table and save to file
    save_table_to_file("table.md")
    
    # Try to update the README
    update_readme()

if __name__ == "__main__":
    main()
