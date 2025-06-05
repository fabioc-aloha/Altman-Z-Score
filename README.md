# Altman Z-Score Analysis Platform

**Version: 2.8.5 (2025-06-05)**

A robust, modular Python tool for single-stock Altman Z-Score trend analysis. Designed for reliability, transparency, and extensibility—ideal for professionals, researchers, and advanced investors.

---

## Usage
To analyze one or more stocks, run:
```sh
python main.py <TICKER1> <TICKER2> ... [--start YYYY-MM-DD] [--moving-averages] [--no-plot]
```
Examples:
```sh
python main.py AAPL MSFT TSLA
python main.py TSLA --start 2023-01-01
python main.py AAPL MSFT --moving-averages --no-plot
```
Replace `<TICKER1> <TICKER2> ...` with one or more stock ticker symbols (e.g., `AAPL`, `MSFT`).

Outputs are saved in `output/<TICKER>/`:
- Full report: `zscore_<TICKER>_zscore_full_report.md`
- Trend chart: `zscore_<TICKER>_trend.png`
- Raw data: `zscore_<TICKER>.csv` and `.json`
- If a ticker is not available, only a `TICKER_NOT_AVAILABLE.txt` marker file will be present.

### Sample Reports

The following table shows available reports for all analyzed tickers:

| Ticker | Full Report | Trend Chart | CSV Data | JSON Data |
|--------|-------------|-------------|----------|-----------|
| AAPL | [Report](output/AAPL/zscore_AAPL_zscore_full_report.md) | [Chart](output/AAPL/zscore_AAPL_trend.png) | [CSV](output/AAPL/zscore_AAPL.csv) | [JSON](output/AAPL/zscore_AAPL.json) |
| AMZN | [Report](output/AMZN/zscore_AMZN_zscore_full_report.md) | [Chart](output/AMZN/zscore_AMZN_trend.png) | [CSV](output/AMZN/zscore_AMZN.csv) | [JSON](output/AMZN/zscore_AMZN.json) |
| ASML | [Report](output/ASML/zscore_ASML_zscore_full_report.md) | [Chart](output/ASML/zscore_ASML_trend.png) | [CSV](output/ASML/zscore_ASML.csv) | [JSON](output/ASML/zscore_ASML.json) |
| BIDU | [Report](output/BIDU/zscore_BIDU_zscore_full_report.md) | [Chart](output/BIDU/zscore_BIDU_trend.png) | [CSV](output/BIDU/zscore_BIDU.csv) | [JSON](output/BIDU/zscore_BIDU.json) |
| CVNA | [Report](output/CVNA/zscore_CVNA_zscore_full_report.md) | [Chart](output/CVNA/zscore_CVNA_trend.png) | [CSV](output/CVNA/zscore_CVNA.csv) | [JSON](output/CVNA/zscore_CVNA.json) |
| GOOGL | [Report](output/GOOGL/zscore_GOOGL_zscore_full_report.md) | [Chart](output/GOOGL/zscore_GOOGL_trend.png) | [CSV](output/GOOGL/zscore_GOOGL.csv) | [JSON](output/GOOGL/zscore_GOOGL.json) |
| JNJ | [Report](output/JNJ/zscore_JNJ_zscore_full_report.md) | [Chart](output/JNJ/zscore_JNJ_trend.png) | [CSV](output/JNJ/zscore_JNJ.csv) | [JSON](output/JNJ/zscore_JNJ.json) |
| JPM | [Report](output/JPM/zscore_JPM_zscore_full_report.md) | [Chart](output/JPM/zscore_JPM_trend.png) | [CSV](output/JPM/zscore_JPM.csv) | [JSON](output/JPM/zscore_JPM.json) |
| MELI | [Report](output/MELI/zscore_MELI_zscore_full_report.md) | [Chart](output/MELI/zscore_MELI_trend.png) | [CSV](output/MELI/zscore_MELI.csv) | [JSON](output/MELI/zscore_MELI.json) |
| META | [Report](output/META/zscore_META_zscore_full_report.md) | [Chart](output/META/zscore_META_trend.png) | [CSV](output/META/zscore_META.csv) | [JSON](output/META/zscore_META.json) |
| MSFT | [Report](output/MSFT/zscore_MSFT_zscore_full_report.md) | [Chart](output/MSFT/zscore_MSFT_trend.png) | [CSV](output/MSFT/zscore_MSFT.csv) | [JSON](output/MSFT/zscore_MSFT.json) |
| NVDA | [Report](output/NVDA/zscore_NVDA_zscore_full_report.md) | [Chart](output/NVDA/zscore_NVDA_trend.png) | [CSV](output/NVDA/zscore_NVDA.csv) | [JSON](output/NVDA/zscore_NVDA.json) |
| PG | [Report](output/PG/zscore_PG_zscore_full_report.md) | [Chart](output/PG/zscore_PG_trend.png) | [CSV](output/PG/zscore_PG.csv) | [JSON](output/PG/zscore_PG.json) |
| PLTR | [Report](output/PLTR/zscore_PLTR_zscore_full_report.md) | [Chart](output/PLTR/zscore_PLTR_trend.png) | [CSV](output/PLTR/zscore_PLTR.csv) | [JSON](output/PLTR/zscore_PLTR.json) |
| RIDEQ | [Report](output/RIDEQ/zscore_RIDEQ_zscore_full_report.md) | [Chart](output/RIDEQ/zscore_RIDEQ_trend.png) | [CSV](output/RIDEQ/zscore_RIDEQ.csv) | [JSON](output/RIDEQ/zscore_RIDEQ.json) |
| SHOP | [Report](output/SHOP/zscore_SHOP_zscore_full_report.md) | [Chart](output/SHOP/zscore_SHOP_trend.png) | [CSV](output/SHOP/zscore_SHOP.csv) | [JSON](output/SHOP/zscore_SHOP.json) |
| SNOW | [Report](output/SNOW/zscore_SNOW_zscore_full_report.md) | [Chart](output/SNOW/zscore_SNOW_trend.png) | [CSV](output/SNOW/zscore_SNOW.csv) | [JSON](output/SNOW/zscore_SNOW.json) |
| SONO | [Report](output/SONO/zscore_SONO_zscore_full_report.md) | [Chart](output/SONO/zscore_SONO_trend.png) | [CSV](output/SONO/zscore_SONO.csv) | [JSON](output/SONO/zscore_SONO.json) |
| SQ | [Report](output/SQ/zscore_SQ_zscore_full_report.md) | [Chart](output/SQ/zscore_SQ_trend.png) | [CSV](output/SQ/zscore_SQ.csv) | [JSON](output/SQ/zscore_SQ.json) |
| TSLA | [Report](output/TSLA/zscore_TSLA_zscore_full_report.md) | [Chart](output/TSLA/zscore_TSLA_trend.png) | [CSV](output/TSLA/zscore_TSLA.csv) | [JSON](output/TSLA/zscore_TSLA.json) |
| UBER | [Report](output/UBER/zscore_UBER_zscore_full_report.md) | [Chart](output/UBER/zscore_UBER_trend.png) | [CSV](output/UBER/zscore_UBER.csv) | [JSON](output/UBER/zscore_UBER.json) |


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
