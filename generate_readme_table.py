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
        company_name = get_company_name(info_path)
        row = f'| <img src="{logo_rel}" alt="{ticker}" width="40" height="40"/> | {company_name} | [Report]({report_rel}) | [Chart]({chart_rel}) |'
        rows.append(row)
    return rows

def main():
    print("| Logo | Company Name | Full Report | Trend Chart |")
    print("|------|-------------|-------------|-------------|")
    for row in generate_table():
        print(row)

if __name__ == "__main__":
    main()
