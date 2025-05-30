# Altman Z-Score Analysis (Version 2.2.2)

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

**Release v2.2.2 (May 29, 2025):**
- Script version is now included in every report for traceability
- Tested companies documentation and release process are enforced
- Documentation, outputs, and release workflow streamlined and up to date
- All changes are fully tracked and versioned in outputs and documentation

---

## Usage
To analyze a stock, run:
```sh
python main.py <TICKER>
```
Replace `<TICKER>` with the stock ticker symbol (e.g., `AAPL`, `MSFT`).

Outputs are saved in `output/<TICKER>/`:
- Full report: `zscore_<TICKER>_zscore_full_report.md`
- Trend chart: `zscore_<TICKER>_trend.png`
- Raw data: `zscore_<TICKER>.csv` and `.json`
- If a ticker is not available, only a `TICKER_NOT_AVAILABLE.txt` marker file will be present.

---

## Documentation & Release Process
- All companies in `output/` are tracked in `output/TESTED_COMPANIES.md` (release-blocking)
- Version numbers and changelogs are up to date in documentation
- See `PLAN.md` and `TODO.md` for roadmap and actionable tasks
- See `LEARNINGS.md` for technical notes and known issues

---

## Project Status & Roadmap
- **V2.2.2 (Current):** Script version included in every report; tested companies documentation and release process enforced; improved traceability
- **V2.2.1:** Prompt-driven reporting overhaul, user-editable prompt folder, improved attribution, robust report formatting
- **V2.2:** Model selection & calibration overhaul, enhanced visualizations
- **V2.5+:** Forecasting, sentiment/news analysis, portfolio/multi-ticker analysis, advanced insights (see `PLAN.md`)

See `output/TESTED_COMPANIES.md` for tested companies and outcomes.

---

## Key Features
- **Altman Z-Score Trend Analysis:** Computes and visualizes Z-Score trends for any US-listed company using real, live data
- **Industry-Aware Model Selection:** Automatically selects the correct Z-Score model based on SIC code and industry
- **Comprehensive Reporting:** Generates full, well-formatted reports (TXT, CSV, JSON) with context, formulas, diagnostics, and raw data mapping
- **Stock Price Overlay:** Visualizes Z-Score trends alongside historical stock prices
- **Robust Error Handling:** Clear diagnostics and error outputs for missing data, delisted tickers, or API issues
- **Extensible Architecture:** Modular design for easy addition of new data sources, models, or output formats

---

## Environment Setup
- Copy `.env.example` to `.env` and fill in your API keys and configuration
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Use Python 3.11+ (see `docs/venv_setup.md` for virtual environment instructions)

---

## Development & Contribution
- All changes must pass existing and new tests
- New features require updated tests and documentation
- See `PLAN.md` for the feature roadmap and major decisions
- See `TODO.md` for actionable tasks and environment setup
- Document significant learnings in `LEARNINGS.md`

---

## License
MIT (see LICENSE file)

---

For more details, see the full documentation in this repository and referenced files.
