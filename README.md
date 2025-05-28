# Altman Z-Score Analysis (V1)

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

## Project Status (May 2025)
- **MVP (Single-Stock Z-Score Trend Analysis):** Complete and stable
- **v1 (Stock Price Overlay):** Complete
- **v2 (Forecasting, Sentiment, Portfolio Analysis):** In planning (see PLAN.md)
- All development and testing uses a local Python 3.11+ virtual environment (`.venv`)

---

## What Does This Project Do?
- **Purpose:** Analyze the financial health and bankruptcy risk of a public company over time using the Altman Z-Score, with industry-aware model selection.
- **Scope:** Single-ticker analysis (portfolio/multi-ticker coming in v2+)
- **Data Sources:** SEC EDGAR (XBRL), Yahoo Finance, NewsAPI, public industry benchmarks
- **Tech Stack:** Python, pandas, pydantic, yfinance, sec-edgar-downloader, xbrlparse, matplotlib/plotly

---

## Key Features
- **Altman Z-Score Trend Analysis:** Computes and visualizes Z-Score trends for any US-listed company using real, live data
- **Industry-Aware Model Selection:** Automatically selects the correct Z-Score model based on SIC code and industry
- **Comprehensive Reporting:** Generates full, well-formatted reports (TXT, CSV, JSON) with context, formulas, diagnostics, and raw data mapping
- **Stock Price Overlay:** Visualizes Z-Score trends alongside historical stock prices
- **Robust Error Handling:** Clear diagnostics and error outputs for missing data, delisted tickers, or API issues
- **Extensible Architecture:** Modular design for easy addition of new data sources, models, or output formats

---

## Usage
To analyze a stock, run:
```pwsh
python altman_zscore.py --ticker <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol you want to analyze (e.g., `AAPL`, `MSFT`).

Example:
```pwsh
python altman_zscore.py --ticker AAPL
```

Outputs will be saved in the `output/<TICKER>/` directory:
- Full report: `zscore_<TICKER>_zscore_full_report.txt`
- Component table: `zscore_<TICKER>_zscore_components.txt`
- Trend chart: `zscore_<TICKER>_trend.png`
- Raw data: `zscore_<TICKER>.csv` and `.json`
- Profile/summary: `zscore_<TICKER>_profile.txt`

Reports include mapped industry, SIC code, model selection rationale, and risk diagnostics for each quarter. Charts show Z-Score trends with risk zones and optional price overlay.

---

## Typical Workflow
1. **Clone the Repository**
2. **Set Up Your Environment** (see below)
3. **Run the Analysis Pipeline** for a ticker (see Usage above)
4. **Review Outputs** in the output directory
5. **Interpret Results** using the generated reports and charts

---

## Advanced Usage
- **Custom Analysis:** Extend the pipeline to new models, data sources, or output formats by following the modular structure
- **Batch/Portfolio Analysis:** (Planned for v2+) Analyze multiple tickers or portfolios with a single command
- **Forecasting & Sentiment:** (v2 Roadmap) Integrate consensus estimates and news sentiment for forward-looking risk analysis

---

## Environment Setup
- Copy `.env.example` to `.env` and fill in your API keys and configuration
- Install dependencies:
  ```pwsh
  pip install -r requirements.txt
  ```
- Use Python 3.11+ with a `.venv` virtual environment (see `docs/venv_setup.md` for setup instructions)

---

## Documentation & Support
- See `PLAN.md` and `TODO.md` for roadmap, progress, and technical decisions
- The GitHub Wiki provides extended guides, usage examples, and troubleshooting
- For questions or contributions, open an issue or pull request on GitHub

---

MVP and v1 are complete as of May 2025. v2 (forecasting, sentiment, portfolio analysis) is in planning—see PLAN.md for details.
