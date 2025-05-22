# main.py
"""
Core implementation module for the Altman Z-Score analysis pipeline.

This module contains the primary analysis logic but is NOT the main entry point
of the application. Users should run analyze.py in the root directory instead.

This module provides:
- Portfolio analysis functionality
- Integration of financial data fetching
- Z-Score calculation coordination
- Industry classification
- Results compilation and export

The main function in this module (analyze_portfolio) is called by the entry point
script (analyze.py) after setting up the environment and managing the cache.
"""

import os
import pandas as pd
import logging
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
from .fetch_financials import fetch_batch_financials
from .fetch_prices import get_quarter_price_change, get_market_value, get_start_end_prices
from .compute_zscore import ZScoreCalculator, FinancialMetrics, determine_zscore_model, validate_model_selection
from .config import (
    PORTFOLIO,
    PERIOD_END,
    PRICE_START,
    PRICE_END,
    OUTPUT_DIR
)
from .industry_classifier import classify_company
from .cik_mapping import get_cik_mapping

# Load environment variables and configure logging
load_dotenv()
logging.basicConfig(
    level=logging.ERROR,  # Only show errors
    format='%(levelname)s: %(message)s'
)

def analyze_portfolio():
    """
    Core analysis function for processing the configured portfolio.
    
    Note:
        This function is not meant to be called directly by users. Instead, use the
        analyze.py script in the root directory, which handles environment setup
        and cache management before calling this function.
    
    The analysis process includes:
    1. Loading configuration and date ranges
    2. Mapping tickers to CIK numbers
    3. Classifying companies by industry
    4. Fetching and validating financial data
    5. Computing Z-scores using appropriate models
    6. Compiling and exporting results
    
    The function processes each company in the portfolio, handling errors
    gracefully to ensure the analysis continues even if individual
    companies fail.
    
    Raises:
        ValueError: If no valid CIK numbers are found for the portfolio
    """
    print(f"Analyzing financial data for period ending {PERIOD_END}")
    print(f"Price comparison period: {PRICE_START} to {PRICE_END}\n")

    records = []
    total_companies = len(PORTFOLIO)
    successful_companies = 0

    # Get CIK mappings
    cik_map = get_cik_mapping(PORTFOLIO)
    if not cik_map:
        raise ValueError("No valid CIK numbers found for any companies in the portfolio")

    # Create company profiles first for efficient model selection
    print("\nClassifying companies...")
    company_profiles = {}
    filtered_tickers = [t for t in PORTFOLIO if t and not t.startswith("#")]
    for ticker in tqdm(filtered_tickers, desc="Classifying companies", unit="company"):
        try:
            cik = cik_map.get(ticker)
            if cik:
                profile = classify_company(cik, ticker)
                company_profiles[ticker] = profile
        except Exception as e:
            logging.error(f"Failed to classify {ticker}: {e}")
            continue

    # Group companies by industry for optimized data fetching
    tech_companies = [ticker for ticker, profile in company_profiles.items() if profile.is_tech_or_ai]
    manufacturing_companies = [ticker for ticker, profile in company_profiles.items() if profile.is_manufacturing]
    service_companies = [ticker for ticker, profile in company_profiles.items() 
                        if not profile.is_tech_or_ai and not profile.is_manufacturing]

    print("\nIndustry Distribution:")
    print(f"Tech/AI Companies: {len(tech_companies)}")
    print(f"Manufacturing Companies: {len(manufacturing_companies)}")
    print(f"Service Companies: {len(service_companies)}\n")

    # Process tech companies first for optimized XBRL tag parsing
    print("Fetching financial data by industry group...")
    financial_data = {}
    
    # Process each industry group with appropriate context
    for industry_group, companies in [
        ("Tech/AI", tech_companies),
        ("Manufacturing", manufacturing_companies),
        ("Service", service_companies)
    ]:
        if companies:
            print(f"\nProcessing {industry_group} companies...")
            industry_profiles = {ticker: company_profiles[ticker] for ticker in companies}
            industry_data = fetch_batch_financials(companies, PERIOD_END, company_profiles=industry_profiles)
            financial_data.update(industry_data)

    # Process companies with progress bar
    progress_bar = tqdm(filtered_tickers, desc="Processing companies", unit="company")
    
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
            
            # Get the pre-computed company profile
            profile = company_profiles.get(ticker)
            if not profile:
                progress_bar.write(f"Error: No classification found for {ticker}")
                continue
            
            # Compute Z-score components
            metrics = FinancialMetrics.from_dict(fin, mve, datetime.strptime(PERIOD_END, "%Y-%m-%d"))
            
            # Select model and validate selection
            model, reason = determine_zscore_model(profile)
            calculator = ZScoreCalculator(model)
            comps = calculator.add_calculation(metrics)
            
            # Validate model selection and log any warnings
            warnings = validate_model_selection(model, metrics, profile)
            for warning in warnings:
                progress_bar.write(f"Warning: {ticker} - {warning}")
            
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
        return

    df = pd.DataFrame(records)
    
    # Reorder and rename columns for better presentation
    columns = {
        "Ticker": "Ticker",
        "Filing Date": "Filing Date",
        "Start Price": "Start $",
        "End Price": "End $",
        "Working Capital/Total Assets": "WC/TA",
        "Retained Earnings/Total Assets": "RE/TA",
        "EBIT/Total Assets": "EBIT/TA",
        "Market Value of Equity/Total Liabilities": "MVE/TL",
        "Sales/Total Assets": "S/TA",
        "Z-Score": "Z-Score",
        "Diagnostic": "Status",
        "Model": "Model",
        "Price Δ%": "Price Δ%"
    }
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
    df = df[["Ticker", "Filing Date", "Start $", "End $", "WC/TA", "RE/TA", "EBIT/TA", "MVE/TL", "S/TA", "Z-Score", "Status", "Model", "Price Δ%"]]
    
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
        'Model': 'left',
        'Price Δ%': 'decimal'
    }
    
    # Format table with custom alignments
    print("\nResults:")
    print("=" * 140)
    print(df.to_markdown(index=False, 
                        tablefmt='pipe',
                        colalign=[alignments[col] for col in df.columns],
                        floatfmt=("", "", ".2f", ".2f", ".3f", ".3f", ".3f", ",.0f", ".3f", ",.0f", "", "", ".2f")))
    
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
