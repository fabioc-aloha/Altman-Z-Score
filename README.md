# Altman Z-Score Analysis (Version 2.2.2)

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

> **Vision:** This project is committed to exceeding the capabilities of all competing Altman Z-Score analysis tools—open-source or commercial. Our ambition is to set a new industry standard for transparency, extensibility, and actionable financial insight.

---

## Quick Start

To analyze a stock, run:
```sh
python main.py <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol you want to analyze (e.g., `AAPL`, `MSFT`).

**Environment Setup:**
```sh
export SEC_EDGAR_USER_AGENT="YourCompany/1.0 (contact@yourcompany.com)"
# Optional for enhanced features:
# export OPENAI_API_KEY="your-openai-key" 
# export NEWSAPI_KEY="your-news-api-key"
```

**Output:** Results saved in `output/<TICKER>/`:
- Full report: `zscore_<TICKER>_zscore_full_report.md`
- Trend chart: `zscore_<TICKER>_trend.png`
- Raw data: `zscore_<TICKER>.csv` and `.json`

---

## Current Version (v2.2.2)

**Release Notes (May 29, 2025):**
- Script version tracking in all reports for improved traceability
- Enhanced model selection with industry-specific calibration
- Centralized constants and improved error handling
- Robust environment variable validation
- Streamlined documentation and release process

**Key Features:**
- Single-stock Altman Z-Score trend analysis
- Industry-specific model selection (manufacturing, service, tech, emerging markets)
- Interactive visualizations with stock price overlay
- Comprehensive markdown reports with AI-powered insights
- Robust data fetching from SEC EDGAR and Yahoo Finance
- Fail-safe error handling and data validation

---

## Roadmap

- [x] **MVP:** Single-Stock Z-Score Trend Analysis
- [x] **v2.1:** Enhanced Reporting & Visualization
- [x] **v2.2:** Model Selection & Calibration Overhaul
- [ ] **v2.5:** Z-Score Forecasting & Sentiment Analysis
- [ ] **v2.6:** Portfolio Analysis
- [ ] **v2.7:** Advanced Correlation & Insights

---

## Architecture & Features

**Purpose:** Analyze the financial health and bankruptcy risk of public companies using industry-specific Altman Z-Score models with comprehensive trend analysis.

**Key Capabilities:**
- Automatic model selection based on SIC code and industry classification
- Multi-source data integration (SEC EDGAR, Yahoo Finance)
- Comprehensive risk assessment with threshold analysis
- Interactive visualizations with stock price overlay
- Robust error handling and data validation
- Extensible architecture for new models and data sources

**Tech Stack:** Python, pandas, pydantic, yfinance, sec-edgar-downloader, matplotlib/plotly

---

## Documentation & Development

- **Planning:** See `PLAN.md` for roadmap and architectural decisions
- **Tasks:** See `TODO.md` for current development tasks
- **Technical Notes:** See `LEARNINGS.md` for implementation details
- **Release Process:** All releases tracked with tested companies in `output/TESTED_COMPANIES.md`
- **Development Environment:** GitHub Codespaces compatible

---

## Installation & Setup

**Prerequisites:**
- Python 3.11+
- Required environment variables

**Installation:**
```sh
# Clone the repository
git clone https://github.com/fabioc-aloha/Altman-Z-Score.git
cd Altman-Z-Score

# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export SEC_EDGAR_USER_AGENT="YourCompany/1.0 (contact@yourcompany.com)"
```

**Optional Environment Variables:**
```sh
export OPENAI_API_KEY="your-openai-key"   # For AI-powered analysis
export NEWSAPI_KEY="your-news-api-key"    # For sentiment analysis (future)
```

---

## Example Usage

```sh
# Basic analysis
python main.py AAPL

# Analysis with custom start date  
python main.py MSFT --start 2023-01-01
```

**Output Structure:**
```
output/AAPL/
├── zscore_AAPL_zscore_full_report.md    # Comprehensive analysis report
├── zscore_AAPL_trend.png                # Visualization with trend analysis
├── zscore_AAPL.csv                      # Raw data in CSV format
└── zscore_AAPL.json                     # Raw data in JSON format
```

---

## Development & Testing

**Running Tests:**
```sh
PYTHONPATH=src python -m pytest scripts/ -v
```

**Code Structure:**
- `src/altman_zscore/` - Main package
- `src/altman_zscore/computation/` - Z-Score calculation logic
- `src/altman_zscore/api/` - Data fetching clients
- `src/altman_zscore/utils/` - Utility functions

**Contributing:**
- Follow PEP 8 style guidelines (4 spaces for indentation)
- Add tests for new features
- Update documentation as needed
- See `PLAN.md` and `TODO.md` for current priorities

---

> **Vision:** See [vision.md](./vision.md) for our complete vision to exceed all competing Altman Z-Score analysis tools.
