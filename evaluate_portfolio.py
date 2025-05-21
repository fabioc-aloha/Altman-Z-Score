import argparse
import pandas as pd
from config import (
    PORTFOLIOS,
    DEFAULT_PORTFOLIO,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    DEFAULT_DATE_RANGE,
)
from financials import analyze_portfolio_financial_health_last_n_filings
from reporting import build_summary_table, export_table
import yfinance as yf


def get_last_available_date(ticker: str) -> str:
    data = yf.download(ticker, period="5d", progress=False)
    if not data.empty:
        return str(data.index[-1].date())
    raise RuntimeError(f"No data found for {ticker}")


def evaluate_portfolio():
    parser = argparse.ArgumentParser(description="GenAI Health Metrics")
    parser.add_argument(
        "--portfolio",
        default=DEFAULT_PORTFOLIO,
        choices=list(PORTFOLIOS.keys()),
        help="Portfolio to analyze",
    )
    parser.add_argument(
        "--export", choices=["csv", "excel"], help="Export results to file"
    )
    parser.add_argument(
        "--output", default=None, help="Output filename (default: genai_health.<ext>)"
    )
    args = parser.parse_args()

    portfolio = PORTFOLIOS[args.portfolio]
    tickers = portfolio["tickers"]
    assumptions = portfolio["diagnostic_assumptions"]

    # Use new per-ticker last three filings analysis
    summary_df = analyze_portfolio_financial_health_last_n_filings(tickers, n=3)

    pd.set_option("display.max_rows", None)
    print(f"\nPortfolio: {portfolio['name']}")
    print(f"Description: {portfolio['description']}")
    print(f"Diagnostic assumptions: {assumptions['notes']}")
    print(f"GenAI Company Health Table (Last three filings per stock):\n")
    print(summary_df.to_string(index=False))

    if args.export:
        ext = args.export if args.export != "excel" else "xlsx"
        base_name = portfolio["name"].replace(" ", "_").lower()
        filename = args.output or f"{base_name}.{ext}"
        (
            summary_df.to_csv(filename, index=False)
            if args.export == "csv"
            else summary_df.to_excel(filename, index=False)
        )
        print(f"\nExported results to {filename}")


if __name__ == "__main__":
    evaluate_portfolio()
