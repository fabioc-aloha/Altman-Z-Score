# Altman Z-Score Analyzer

## Overview

A Python-based financial analysis tool that calculates the Altman Z-Score for AI and tech companies. The Altman Z-Score is a financial metric that predicts the probability of a business going bankrupt within the next two years.

This tool automatically:
- Fetches financial data from SEC EDGAR and Yahoo Finance
- Calculates Z-Score components and diagnostics
- Produces detailed analysis reports
- Tracks company performance over time

You can run the analysis manually or schedule it (e.g., via cron) to track companies' financial health over time.

## Background on Altman's Z-Score

The Altman Z-Score, developed by NYU Professor Edward Altman in 1968, is a predictive model that assesses a company's bankruptcy risk. The model combines five financial ratios into a single score that indicates a company's financial health.

### Formula and Components

Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E

Where:
1. **A = Working Capital / Total Assets**
   - Measures liquid assets relative to company size
   - Higher ratio indicates better short-term financial stability
   - Working Capital = Current Assets - Current Liabilities

2. **B = Retained Earnings / Total Assets**
   - Measures accumulated profitability over time
   - Indicates company age and earning power
   - Higher values suggest sustainable growth

3. **C = EBIT / Total Assets**
   - Measures operating efficiency and productivity
   - EBIT (Earnings Before Interest & Taxes) shows core profitability
   - Key indicator of asset utilization effectiveness

4. **D = Market Value of Equity / Total Liabilities**
   - Measures financial leverage and market confidence
   - Shows how much assets can decline before liabilities exceed assets
   - Market value indicates investor confidence

5. **E = Sales / Total Assets**
   - Measures asset turnover and efficiency
   - Shows how effectively company uses assets to generate sales
   - Industry-specific benchmark for operational efficiency

### Diagnostic Zones

The resulting Z-Score falls into one of three zones:

- **Safe Zone (Z > 2.99)**
  - Company is financially healthy
  - Low probability of bankruptcy
  - Strong financial position

- **Grey Zone (1.81 ≤ Z ≤ 2.99)**
  - Some financial distress signs
  - Requires careful monitoring
  - Could go either way within 2 years

- **Distress Zone (Z < 1.81)**
  - High bankruptcy risk
  - Significant financial challenges
  - Immediate action required

### Modern Applications

While originally developed for manufacturing companies, the model has been adapted for:
- Technology companies
- Service-based businesses
- Private companies
- Non-US markets

This tool specifically focuses on AI and technology companies, adapting the interpretation for modern business models while maintaining the core analytical framework.

## Features

- **Automated Data Collection**
  - Fetches financial statements from SEC EDGAR
  - Retrieves market data from Yahoo Finance
  - Supports batch processing of multiple companies

- **Comprehensive Analysis**
  - Calculates all Z-Score components (A-E ratios)
  - Provides diagnostic assessments (Safe/Grey/Distress zones)
  - Includes trend analysis across quarters
  - Tracks stock price performance

- **Data Quality**
  - Validates financial metrics
  - Implements ratio sanity checks
  - Includes data quality metrics
  - Handles missing or invalid data

- **Performance**
  - Parallel processing for multiple companies
  - Caching for API responses
  - Rate limiting for API requests
  - Efficient data structures

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Altman-Z-Score.git
cd Altman-Z-Score
```

2. Set up a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Configuration

1. Create a `.env` file with your SEC EDGAR API credentials:
```env
SEC_EDGAR_USER_AGENT=your_name your_email@domain.com
```

2. (Optional) Modify the portfolios in `src/altman_zscore/config.py`:
   - Use predefined portfolios or create your own
   - Each portfolio includes tickers and analysis settings
   - CIK numbers are automatically looked up using SEC EDGAR
   - Changes take effect immediately

### Portfolio System
The tool uses a flexible portfolio management system that:
- Supports multiple predefined portfolios (e.g., "genai")
- Includes company tickers with descriptions
- Configures analysis parameters per portfolio
- Automatically handles CIK lookups with caching
- Validates all portfolio configurations

Example portfolio configuration:
```python
PORTFOLIOS = {
    "genai": {
        "name": "GenAI Leaders",
        "description": "Top public companies in generative AI and enabling infrastructure.",
        "tickers": [
            "MSFT",   # Microsoft Corporation
            "GOOGL",  # Alphabet Inc.
            "AMZN",   # Amazon.com, Inc.
        ],
        "diagnostic_assumptions": {
            "safe_zone_threshold": 2.99,
            "grey_zone_min": 1.81,
            "grey_zone_max": 2.99,
            "distress_zone_max": 1.80,
        },
        "currency": "USD",
        "region": "US"
    }
}
```

## Usage

1. Run the analysis:
```bash
python -m altman_zscore.main
```

2. Results will be saved in:
   - CSV format: `zscore_analysis_DATE.csv`
   - Console output with summary

## Project Structure

```
src/altman_zscore/      # Main package directory
├── __init__.py         # Package initialization
├── config.py           # Configuration and constants
├── compute_zscore.py   # Z-score calculation logic
├── fetch_financials.py # SEC EDGAR data fetching
├── fetch_prices.py     # Market data retrieval
└── main.py            # Main execution script

tests/                  # Test directory
└── test_compute_zscore.py  # Unit tests
```

## Understanding Z-Score Components

- **A ratio** (Working Capital/Total Assets): Measures liquid assets relative to size
- **B ratio** (Retained Earnings/Total Assets): Measures profitability and age
- **C ratio** (EBIT/Total Assets): Measures operating efficiency
- **D ratio** (Market Value of Equity/Total Liabilities): Measures solvency
- **E ratio** (Sales/Total Assets): Measures asset efficiency

Interpretation:
- Z-Score > 2.99: "Safe" Zone
- 1.81 ≤ Z-Score ≤ 2.99: "Grey" Zone
- Z-Score < 1.81: "Distress" Zone

## Development

See our documentation for development guidelines:
- [Architectural Decisions](DECISIONS.md)
- [Implementation Learnings](LEARNINGS.md)
- [Todo List](TODO.md)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on Edward Altman's Z-Score model
- Uses data from SEC EDGAR and Yahoo Finance
- Inspired by the need for automated financial health analysis

## References

- Altman, E. I. (1968). "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy."
- [SEC EDGAR](https://www.sec.gov/edgar)
- [Yahoo Finance](https://finance.yahoo.com/)

This app:

Fetches and parses each company’s Q1 2025 filing from EDGAR.

Retrieves share counts and price data via yfinance.

Computes the A–E components, Z-Score, and diagnostic.

Calculates stock price performance over the same period.

Outputs a consolidated Markdown table of results.

You can schedule main.py via cron or integrate with the monthly automation task created earlier.

## Environment Variables

The following environment variables can be set in your `.env` file:

```env
# Required - Your SEC EDGAR API credentials (email required by SEC)
SEC_EDGAR_USER_AGENT=your_name your_email@domain.com
# Alternative name for the same setting
SEC_USER_AGENT=your_name your_email@domain.com

# Optional - Analysis configuration
DEFAULT_PORTFOLIO=genai  # Which portfolio to analyze by default
```

## Caching

The tool caches data to improve performance and respect SEC EDGAR rate limits:

- **Company CIKs**: Cached in `.cache/cik_cache.json`
- **Financial Data**: Cached in `.cache/financial_data/`

The cache is created automatically and updates when new companies are added to your portfolio. All cached data respects SEC EDGAR's rate limiting requirements.