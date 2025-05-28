import sys
import os
import json
from dotenv import load_dotenv

# Ensure src is in the path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from src.altman_zscore.api.openai_client import AzureOpenAIClient

CANONICAL_FIELDS = [
    "total_assets", "current_assets", "current_liabilities", "retained_earnings", "ebit", "sales"
]

def run_mapping_for_ticker(ticker):
    # Read raw fields from output/bs_index_{ticker}_.txt
    bs_path = f"output/bs_index_{ticker}_.txt"
    with open(bs_path, "r", encoding="utf-8") as f:
        bs_fields = [line.strip() for line in f if line.strip() and not line.startswith("//")]
    # Try to get income statement fields
    is_fields = []
    is_index_path = f"output/is_index_{ticker}_.txt"
    if os.path.exists(is_index_path):
        with open(is_index_path, "r", encoding="utf-8") as f:
            is_fields = [line.strip() for line in f if line.strip() and not line.startswith("//")]
    else:
        # Fallback: parse from summary JSON
        summary_path = f"output/{ticker}/zscore_{ticker}_summary.txt"
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                for line in f:
                    if '"income_statement": {' in line:
                        try:
                            # Find the JSON dict in the line
                            json_start = line.index('{')
                            payload = json.loads(line[json_start:])
                            is_fields = list(payload.get('income_statement', {}).keys())
                            break
                        except Exception:
                            continue
    raw_fields = bs_fields + is_fields
    print(f"\n=== {ticker} ===")
    client = AzureOpenAIClient()
    mapping = client.suggest_field_mapping(raw_fields, CANONICAL_FIELDS)
    print("AI Field Mapping Result:")
    for canonical, raw in mapping.items():
        print(f"  {canonical}: {raw}")
    # Print which quarters are missing data for this ticker, only for quarters >= Jan 2024
    summary_path = f"output/{ticker}/zscore_{ticker}_summary.txt"
    if os.path.exists(summary_path):
        print("  [Quarter Data Validation]")
        with open(summary_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.startswith("//") and "Skipping quarter" not in line:
                    parts = line.split()
                    # Expect date in first column, format YYYY-MM-DD
                    if len(parts) > 0 and parts[0][:4].isdigit():
                        year = int(parts[0][:4])
                        month = int(parts[0][5:7])
                        if (year > 2023) or (year == 2023 and month >= 1):
                            if len(parts) > 2 and ("missing" in line or "error" in line or "False" in line):
                                print("    ", line.strip())

def main():
    for ticker in ["AAPL", "SONO", "MSFT", "FDX", "DAL", "SBUX", "TSLA"]:
        run_mapping_for_ticker(ticker)

if __name__ == "__main__":
    main()
