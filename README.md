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

---

## Documentation & Release Process
- Version numbers and changelogs are up to date in documentation
- See `PLAN.md` and `TODO.md` for roadmap and actionable tasks
- See `LEARNINGS.md` for technical notes and known issues

---

## Modular Architecture
The codebase is now fully modularized for maintainability and extensibility. Key modules include:
- `one_stock_analysis.py` and `one_stock_analysis_helpers.py`: Main pipeline and helpers
- `company_profile.py` and `company_profile_helpers.py`: Company data logic
- `company_status.py` and `company_status_helpers.py`: Company status logic
- `plotting.py`, `plotting_helpers.py`, `plotting_terminal.py`: Plotting and visualization
- `api/openai_client.py`, `api/openai_helpers.py`: LLM integration
- `zscore_models.py`, `enums.py`, `model_thresholds.py`, `zscore_model_base.py`: Z-Score models and configuration
- `computation/formulas.py`: Core financial formulas

All modules are independently testable. See `tests/` for coverage.

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
