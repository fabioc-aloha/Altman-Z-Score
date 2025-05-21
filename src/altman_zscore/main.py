# main.py
import os
import pandas as pd
import logging
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
from .fetch_financials import fetch_filing_url, parse_financials
from .fetch_prices import get_quarter_price_change, get_market_value, get_start_end_prices
from .compute_zscore import ZScoreCalculator, FinancialMetrics
from .config import PORTFOLIO, get_current_dates, OUTPUT_DIR

# Load environment variables and configure logging
load_dotenv()
logging.basicConfig(
    level=logging.ERROR,  # Only show errors
    format='%(levelname)s: %(message)s'
)

# Get date ranges from config
PRICE_START, PRICE_END, PERIOD_END = get_current_dates()

print(f"Analyzing financial data for period ending {PERIOD_END}")
print(f"Price comparison period: {PRICE_START} to {PRICE_END}\n")

records = []
total_companies = len(PORTFOLIO)
successful_companies = 0

# Process each company
from .cik_mapping import get_cik_mapping
from .fetch_financials import fetch_batch_financials

# Get CIK mappings
cik_map = get_cik_mapping(PORTFOLIO)
if not cik_map:
    raise ValueError("No valid CIK numbers found for any companies in the portfolio")

# Fetch financial data in batch
financial_data = fetch_batch_financials(PORTFOLIO, PERIOD_END)

# Process companies with progress bar
filtered_tickers = [t for t in PORTFOLIO if t and not t.startswith("#")]
progress_bar = tqdm(filtered_tickers, desc="Processing companies", unit="company")

records: list[dict[str, str | float]] = []  # Type hint for records list

for ticker in progress_bar:
    try:
        progress_bar.set_postfix({"current": ticker}, refresh=True)
        
        # Skip if we couldn't get financials
        if not financial_data.get(ticker, {}).get("success", False):
            error_msg = financial_data.get(ticker, {}).get('error', 'Unknown error')
            progress_bar.write(f"Error: Failed to process {ticker} - {error_msg}")
            continue
            
        # Get market value and price change
        mve = get_market_value(ticker, PRICE_END)
        delta = get_quarter_price_change(ticker, PRICE_START, PRICE_END)
        start_price, end_price = get_start_end_prices(ticker, PRICE_START, PRICE_END)
        
        fin = financial_data[ticker]["data"]
        
        # Compute Z-score components
        calculator = ZScoreCalculator()
        metrics = FinancialMetrics.from_dict(fin, mve, datetime.strptime(PERIOD_END, "%Y-%m-%d"))
        comps = calculator.compute_components(metrics)
        
        # Create result dictionary with proper typing
        base_dict = dict(comps.as_dict)
        result_dict: dict[str, str | float] = {
            **base_dict,
            "Ticker": str(ticker),
            "Price Δ%": float(delta),
            "Start Price": float(start_price),
            "End Price": float(end_price),
            "Filing Date": str(PERIOD_END)
        }
        records.append(result_dict)
        
        successful_companies += 1
        progress_bar.set_postfix({"success": successful_companies, "current": ticker}, refresh=True)
        
    except Exception as e:
        progress_bar.write(f"Error: Failed to process {ticker} - {str(e)}")
        continue

progress_bar.close()

if not records:
    print("\nNo data available for the specified period.")
else:
    df = pd.DataFrame(records)
    
    # Reorder and rename columns for better presentation
    columns = {
        "Ticker": "Ticker",
        "Filing Date": "Filing Date",
        "Start Price": "Start $",
        "End Price": "End $",
        "A": "WC/TA",
        "B": "RE/TA",
        "C": "EBIT/TA",
        "D": "MVE/TL",
        "E": "S/TA",
        "Z-Score": "Z-Score",
        "Diagnostic": "Status",
        "Price Δ%": "Price Δ%"
    }
    df = df[list(columns.keys())]
    df = df.rename(columns=columns)
    
    # Sort by Ticker alphabetically
    df = df.sort_values("Ticker", ascending=True)
    
    # Format numeric columns
    pd.options.display.float_format = None  # Reset any global format
    format_dict = {
        'WC/TA': '{:8.3f}',      # Width of 8 for alignment
        'RE/TA': '{:8.3f}',
        'EBIT/TA': '{:8.3f}',
        'MVE/TL': '{:12,.0f}',   # Width of 12 for larger numbers
        'S/TA': '{:8.3f}',
        'Z-Score': '{:12,.0f}',  # Width of 12 for larger numbers
        'Start $': '{:8.2f}',    # Width of 8 for price
        'End $': '{:8.2f}',      # Width of 8 for price
        'Price Δ%': '{:8.2f}'    # Width of 8 for percentage
    }
    
    # Apply formatting
    for col, fmt in format_dict.items():
        df[col] = df[col].apply(lambda x: fmt.format(x))
    
    # Remove extra whitespace in Filing Date
    df['Filing Date'] = df['Filing Date'].str.strip()
    
    # Configure column alignments and padding
    alignments = {
        'Ticker': 'left',
        'Filing Date': 'left',
        'Start $': 'decimal',
        'End $': 'decimal',
        'WC/TA': 'decimal',
        'RE/TA': 'decimal',
        'EBIT/TA': 'decimal',
        'MVE/TL': 'decimal',
        'S/TA': 'decimal',
        'Z-Score': 'decimal',
        'Status': 'left',
        'Price Δ%': 'decimal'
    }
    
    # Format table with custom alignments
    print("\nResults:")
    print("=" * 140)  # Extended past table edges for better visual separation
    print(df.to_markdown(index=False, 
                        tablefmt='pipe',
                        colalign=[alignments[col] for col in df.columns],
                        floatfmt=("", "", ".2f", ".2f", ".3f", ".3f", ".3f", ",.0f", ".3f", ",.0f", "", ".2f")))
    
    # Save results to output directory
    output_file = os.path.join(OUTPUT_DIR, f'zscore_analysis_{PERIOD_END}.csv')
    
    # Create a copy for CSV export with original numeric values
    df_csv = pd.DataFrame(records)
    df_csv = df_csv[list(columns.keys())]
    df_csv = df_csv.rename(columns=columns)
    df_csv = df_csv.sort_values("Ticker", ascending=True)
    df_csv.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")
    
    # Get original numeric values for calculations
    df_orig = pd.DataFrame(records)
    
    # Summary statistics with thousands separators
    print("\nSummary:")
    print("-" * 80)
    print(f"Companies successfully analyzed: {successful_companies} out of {total_companies}")
    print(f"Average Z-Score: {df_orig['Z-Score'].mean():,.0f}")
    print(f"Companies in distress: {len(df[df['Status'] == 'Distress Zone'])}")
    print(f"Average price change: {df_orig['Price Δ%'].mean():.2f}%")
