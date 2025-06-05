# Altman Z-Score Analysis Platform

**Version: 2.8.6 (2025-06-05)**

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with LLM-powered qualitative insights. This script orchestrates the analysis pipeline for single or multiple stock tickers.

---

## Architecture Overview
1. **Input Layer:** Accepts ticker(s) and analysis date; validates input.
2. **Data Fetching Layer:** Fetches financials (SEC EDGAR/XBRL) and market data (Yahoo Finance).
3. **Validation Layer:** Validates raw data using Pydantic schemas; reports missing/invalid fields.
4. **Computation Layer:** Computes Altman Z-Score using validated data; returns result object.
5. **Reporting Layer:** Outputs results to CSV, JSON, or stdout; logs all steps and errors.

### Key Principles
- **Modularity:** Each phase is implemented as a separate, testable module.
- **Robustness:** Strong error handling, logging, and data validation at every step.
- **Extensibility:** Easy to add new data sources, models, or output formats.
- **Testability:** Each module is independently testable with clear interfaces.

### Data Sources
- **Primary:** Yahoo Finance (real-time financials and market data)
- **Fallback:** SEC EDGAR/XBRL (official regulatory filings)
- **Executive Data:** Multi-source aggregation for comprehensive profiles

### Output Structure
All outputs are saved to `output/<TICKER>/`:
- `zscore_<TICKER>_zscore_full_report.md` (comprehensive analysis with LLM insights)
- `zscore_<TICKER>_trend.png` (trend visualization chart)
- `zscore_<TICKER>.csv` and `.json` (raw analytical data)
- `<TICKER>_NOT_AVAILABLE.txt` (marker for unavailable tickers)

---

## Usage
To analyze one or more stocks, run:
```sh
python main.py <TICKER1> <TICKER2> ... [--start YYYY-MM-DD] [--no-plot] [--test] [--log-level DEBUG]
```

Examples:
```sh
python main.py AAPL MSFT TSLA
python main.py TSLA --start 2023-01-01
python main.py AAPL MSFT --no-plot
python main.py --test
python main.py --log-level DEBUG
```
Replace `<TICKER1> <TICKER2> ...` with one or more stock ticker symbols (e.g., `AAPL`, `MSFT`).

---

## Sample Reports

The following table shows available reports for all analyzed tickers:

| Ticker | Full Report | Trend Chart | CSV Data | JSON Data |
|--------|-------------|-------------|----------|-----------|
| AAPL | [Report](output/AAPL/zscore_AAPL_zscore_full_report.md) | [Chart](output/AAPL/zscore_AAPL_trend.png) | [CSV](output/AAPL/zscore_AAPL.csv) | [JSON](output/AAPL/zscore_AAPL.json) |
| AMZN | [Report](output/AMZN/zscore_AMZN_zscore_full_report.md) | [Chart](output/AMZN/zscore_AMZN_trend.png) | [CSV](output/AMZN/zscore_AMZN.csv) | [JSON](output/AMZN/zscore_AMZN.json) |
| ASML | [Report](output/ASML/zscore_ASML_zscore_full_report.md) | [Chart](output/ASML/zscore_ASML_trend.png) | [CSV](output/ASML/zscore_ASML.csv) | [JSON](output/ASML/zscore_ASML.json) |
| BABA | [Report](output/BABA/zscore_BABA_zscore_full_report.md) | [Chart](output/BABA/zscore_BABA_trend.png) | [CSV](output/BABA/zscore_BABA.csv) | [JSON](output/BABA/zscore_BABA.json) |
| BIDU | [Report](output/BIDU/zscore_BIDU_zscore_full_report.md) | [Chart](output/BIDU/zscore_BIDU_trend.png) | [CSV](output/BIDU/zscore_BIDU.csv) | [JSON](output/BIDU/zscore_BIDU.json) |
| CAT | [Report](output/CAT/zscore_CAT_zscore_full_report.md) | [Chart](output/CAT/zscore_CAT_trend.png) | [CSV](output/CAT/zscore_CAT.csv) | [JSON](output/CAT/zscore_CAT.json) |
| CRESY | [Report](output/CRESY/zscore_CRESY_zscore_full_report.md) | [Chart](output/CRESY/zscore_CRESY_trend.png) | [CSV](output/CRESY/zscore_CRESY.csv) | [JSON](output/CRESY/zscore_CRESY.json) |
| CVNA | [Report](output/CVNA/zscore_CVNA_zscore_full_report.md) | [Chart](output/CVNA/zscore_CVNA_trend.png) | [CSV](output/CVNA/zscore_CVNA.csv) | [JSON](output/CVNA/zscore_CVNA.json) |
| DUK | [Report](output/DUK/zscore_DUK_zscore_full_report.md) | [Chart](output/DUK/zscore_DUK_trend.png) | [CSV](output/DUK/zscore_DUK.csv) | [JSON](output/DUK/zscore_DUK.json) |
| F | [Report](output/F/zscore_F_zscore_full_report.md) | [Chart](output/F/zscore_F_trend.png) | [CSV](output/F/zscore_F.csv) | [JSON](output/F/zscore_F.json) |
| GGB | [Report](output/GGB/zscore_GGB_zscore_full_report.md) | [Chart](output/GGB/zscore_GGB_trend.png) | [CSV](output/GGB/zscore_GGB.csv) | [JSON](output/GGB/zscore_GGB.json) |
| GOOG | [Report](output/GOOG/zscore_GOOG_zscore_full_report.md) | [Chart](output/GOOG/zscore_GOOG_trend.png) | [CSV](output/GOOG/zscore_GOOG.csv) | [JSON](output/GOOG/zscore_GOOG.json) |
| GOOGL | [Report](output/GOOGL/zscore_GOOGL_zscore_full_report.md) | [Chart](output/GOOGL/zscore_GOOGL_trend.png) | [CSV](output/GOOGL/zscore_GOOGL.csv) | [JSON](output/GOOGL/zscore_GOOGL.json) |
| HMC | [Report](output/HMC/zscore_HMC_zscore_full_report.md) | [Chart](output/HMC/zscore_HMC_trend.png) | [CSV](output/HMC/zscore_HMC.csv) | [JSON](output/HMC/zscore_HMC.json) |
| INFY | [Report](output/INFY/zscore_INFY_zscore_full_report.md) | [Chart](output/INFY/zscore_INFY_trend.png) | [CSV](output/INFY/zscore_INFY.csv) | [JSON](output/INFY/zscore_INFY.json) |
| JD | [Report](output/JD/zscore_JD_zscore_full_report.md) | [Chart](output/JD/zscore_JD_trend.png) | [CSV](output/JD/zscore_JD.csv) | [JSON](output/JD/zscore_JD.json) |
| MELI | [Report](output/MELI/zscore_MELI_zscore_full_report.md) | [Chart](output/MELI/zscore_MELI_trend.png) | [CSV](output/MELI/zscore_MELI.csv) | [JSON](output/MELI/zscore_MELI.json) |
| META | [Report](output/META/zscore_META_zscore_full_report.md) | [Chart](output/META/zscore_META_trend.png) | [CSV](output/META/zscore_META.csv) | [JSON](output/META/zscore_META.json) |
| MSFT | [Report](output/MSFT/zscore_MSFT_zscore_full_report.md) | [Chart](output/MSFT/zscore_MSFT_trend.png) | [CSV](output/MSFT/zscore_MSFT.csv) | [JSON](output/MSFT/zscore_MSFT.json) |
| NTES | [Report](output/NTES/zscore_NTES_zscore_full_report.md) | [Chart](output/NTES/zscore_NTES_trend.png) | [CSV](output/NTES/zscore_NTES.csv) | [JSON](output/NTES/zscore_NTES.json) |
| NVDA | [Report](output/NVDA/zscore_NVDA_zscore_full_report.md) | [Chart](output/NVDA/zscore_NVDA_trend.png) | [CSV](output/NVDA/zscore_NVDA.csv) | [JSON](output/NVDA_zscore_NVDA.json) |
| PBR | [Report](output/PBR/zscore_PBR_zscore_full_report.md) | [Chart](output/PBR/zscore_PBR_trend.png) | [CSV](output/PBR/zscore_PBR.csv) | [JSON](output/PBR/zscore_PBR.json) |
| PG | [Report](output/PG/zscore_PG_zscore_full_report.md) | [Chart](output/PG/zscore_PG_trend.png) | [CSV](output/PG/zscore_PG.csv) | [JSON](output/PG/zscore_PG.json) |
| PLTR | [Report](output/PLTR/zscore_PLTR_zscore_full_report.md) | [Chart](output/PLTR/zscore_PLTR_trend.png) | [CSV](output/PLTR/zscore_PLTR.csv) | [JSON](output/PLTR/zscore_PLTR.json) |
| SAP | [Report](output/SAP/zscore_SAP_zscore_full_report.md) | [Chart](output/SAP/zscore_SAP_trend.png) | [CSV](output/SAP/zscore_SAP.csv) | [JSON](output/SAP/zscore_SAP.json) |
| SBS | [Report](output/SBS/zscore_SBS_zscore_full_report.md) | [Chart](output/SBS/zscore_SBS_trend.png) | [CSV](output/SBS/zscore_SBS.csv) | [JSON](output/SBS/zscore_SBS.json) |
| SFTBY | [Report](output/SFTBY/zscore_SFTBY_zscore_full_report.md) | [Chart](output/SFTBY/zscore_SFTBY_trend.png) | [CSV](output/SFTBY/zscore_SFTBY.csv) | [JSON](output/SFTBY/zscore_SFTBY.json) |
| SIEGY | [Report](output/SIEGY/zscore_SIEGY_zscore_full_report.md) | [Chart](output/SIEGY/zscore_SIEGY_trend.png) | [CSV](output/SIEGY/zscore_SIEGY.csv) | [JSON](output/SIEGY/zscore_SIEGY.json) |
| SHOP | [Report](output/SHOP/zscore_SHOP_zscore_full_report.md) | [Chart](output/SHOP/zscore_SHOP_trend.png) | [CSV](output/SHOP/zscore_SHOP.csv) | [JSON](output/SHOP/zscore_SHOP.json) |
| SNOW | [Report](output/SNOW/zscore_SNOW_zscore_full_report.md) | [Chart](output/SNOW/zscore_SNOW_trend.png) | [CSV](output/SNOW/zscore_SNOW.csv) | [JSON](output/SNOW/zscore_SNOW.json) |
| SONO | [Report](output/SONO/zscore_SONO_zscore_full_report.md) | [Chart](output/SONO/zscore_SONO_trend.png) | [CSV](output/SONO/zscore_SONO.csv) | [JSON](output/SONO/zscore_SONO.json) |
| SONY | [Report](output/SONY/zscore_SONY_zscore_full_report.md) | [Chart](output/SONY/zscore_SONY_trend.png) | [CSV](output/SONY/zscore_SONY.csv) | [JSON](output/SONY/zscore_SONY.json) |
| TM | [Report](output/TM/zscore_TM_zscore_full_report.md) | [Chart](output/TM/zscore_TM_trend.png) | [CSV](output/TM/zscore_TM.csv) | [JSON](output/TM/zscore_TM.json) |
| TSM | [Report](output/TSM/zscore_TSM_zscore_full_report.md) | [Chart](output/TSM/zscore_TSM_trend.png) | [CSV](output/TSM/zscore_TSM.csv) | [JSON](output/TSM/zscore_TSM.json) |
| TSLA | [Report](output/TSLA/zscore_TSLA_zscore_full_report.md) | [Chart](output/TSLA/zscore_TSLA_trend.png) | [CSV](output/TSLA/zscore_TSLA.csv) | [JSON](output/TSLA/zscore_TSLA.json) |
| UBER | [Report](output/UBER/zscore_UBER_zscore_full_report.md) | [Chart](output/UBER/zscore_UBER_trend.png) | [CSV](output/UBER/zscore_UBER.csv) | [JSON](output/UBER/zscore_UBER.json) |
| UNH | [Report](output/UNH/zscore_UNH_zscore_full_report.md) | [Chart](output/UNH/zscore_UNH_trend.png) | [CSV](output/UNH/zscore_UNH.csv) | [JSON](output/UNH/zscore_UNH.json) |
| VALE | [Report](output/VALE/zscore_VALE_zscore_full_report.md) | [Chart](output/VALE/zscore_VALE_trend.png) | [CSV](output/VALE/zscore_VALE.csv) | [JSON](output/VALE/zscore_VALE.json) |
| WMT | [Report](output/WMT/zscore_WMT_zscore_full_report.md) | [Chart](output/WMT/zscore_WMT_trend.png) | [CSV](output/WMT/zscore_WMT.csv) | [JSON](output/WMT/zscore_WMT.json) |


---

## Documentation & Release Process
- Version numbers and changelogs are up to date in documentation
- See `PLAN.md` and `TODO.md` for roadmap and actionable tasks
- See `LEARNINGS.md` for technical notes and known issues

---

## Environment Setup
- Copy `.env.example` to `.env` and fill in your API keys and configuration
- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Use Python 3.11+ (see virtual environment setup instructions below)

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
