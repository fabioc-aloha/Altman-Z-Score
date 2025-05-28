# Altman Z-Score Analysis (Version 2.0)

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

**Project Status (as of May 27, 2025):**
- **MVP (Single-Stock Z-Score Trend Analysis):** Complete and stable
- **v1 (Stock Price Overlay):** Complete
- **v2 (Per-ticker outputs, main.py entry point, codebase cleanup):** Complete and merged to main
- **v2.5 (Forecasting, Sentiment, Portfolio Analysis):** In planning (see PLAN.md)
- All development and testing uses a local Python 3.11+ virtual environment (`.venv`)

---

## What Does This Project Do?
- **Purpose:** Analyze the financial health and bankruptcy risk of a public company over time using the Altman Z-Score, with industry-aware model selection.
- **Scope:** Single-ticker analysis (portfolio/multi-ticker coming in v2.5+)
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

## Usage
To analyze a stock, run:
```pwsh
python main.py <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol you want to analyze (e.g., `AAPL`, `MSFT`).

Example:
```pwsh
python main.py AAPL
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
- **Batch/Portfolio Analysis:** (Planned for v2.5+) Analyze multiple tickers or portfolios with a single command
- **Forecasting & Sentiment:** (v2.5 Roadmap) Integrate consensus estimates and news sentiment for forward-looking risk analysis

---

## Roadmap
- [x] MVP: Single-Stock Z-Score Trend Analysis
- [x] v1: Overlay Stock Price Trend
- [x] v2: Enhanced Reporting (Full report file generation)
- [ ] v2.5: Sentiment & News Analysis
- [ ] v3: Portfolio Analysis
- [ ] v4: Advanced Correlation & Insights

---

## Environment Setup
- Copy `.env.example` to `.env` and fill in your API keys and configuration
- Install dependencies:
  ```pwsh
  pip install -r requirements.txt
  ```
- Use Python 3.11+ with a `.venv` virtual environment (see `docs/venv_setup.md` for setup instructions)

### Environment Variables
The project uses a `.env` file in the root directory to manage API keys and configuration. For security, your real `.env` should never be committed to version control. Instead, use the provided `.env.example` as a template:

1. Copy `.env.example` to `.env` in the project root.
2. Fill in your real credentials and configuration values.

Example:
```
SEC_EDGAR_USER_AGENT=AltmanZScore/1.0 (your@email.com) Python-Requests/3.0
SEC_API_EMAIL=your@email.com
```

### Python Virtual Environment Setup
- This project uses a Python virtual environment (`.venv`) for dependency management and isolation.
- Requires Python 3.11+.
- See `docs/venv_setup.md` for detailed instructions on setting up and activating the virtual environment.

---

## Usage

### Setup
1. Install Python 3.11+ if not already installed.
2. Activate your `.venv` and install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure your `.env` file as described above.

### Run Analysis
To analyze a stock, use the CLI in `main.py`:
```sh
python main.py <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol you want to analyze (e.g., `AAPL`, `MSFT`).

#### Example
```sh
python main.py MSFT --start 2023-01-01
```
This will generate the Z-Score trend analysis for Microsoft starting from January 1, 2023, and save the results in the `output/` directory.

---

## Outputs
- **Full Analysis Report**: `output/<TICKER>/zscore_<TICKER>_zscore_full_report.txt`
- **Summary and Profile**: `output/<TICKER>/zscore_<TICKER>_summary.txt`, `output/<TICKER>/zscore_<TICKER>_profile.txt`
- **Raw Data**: CSV and JSON files for Z-Score components and price data.
- **Trend Chart**: `output/<TICKER>/zscore_<TICKER>_trend.png` with enhanced price overlay.

---

## Known Limitations
- **SIC/Industry Mapping**: May not always reflect true business maturity.
- **Quarterly Data Gaps**: Missing or irregular filings may result in gaps.
- **International Companies**: Designed for US-listed equities; non-US companies may have incomplete data.
- **Portfolio Analysis**: Only single-ticker analysis is supported.
- **Data Source Reliability**: Dependent on public APIs; outages may affect functionality.

For more details, see `LEARNINGS.md` and the project Wiki.

---

## Development & Contribution
- All changes must pass existing and new tests.
- New features require updated tests and documentation.
- See `PLAN.md` for the feature roadmap and major decisions.
- See `TODO.md` for actionable tasks and environment setup.
- Document significant learnings in `LEARNINGS.md`.

## License
MIT (see LICENSE file)
