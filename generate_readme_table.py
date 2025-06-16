import os
import json

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
        company_name = get_company_name(info_path)        # Display actual chart image instead of just a link, maintaining original proportions by setting only width
        row = f'| <img src="{logo_rel}" alt="{ticker}" width="40" height="40"/> | {company_name} | [Report]({report_rel}) | <a href="{chart_rel}"><img src="{chart_rel}" alt="{ticker} Chart" width="400"/></a> |'
        rows.append(row)
    return rows

def save_table_to_file(filename):
    """Save the generated table to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("| Logo | Company Name | Full Report | Trend Chart |\n")
        f.write("|------|-------------|-------------|:-------------:|\n")
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
