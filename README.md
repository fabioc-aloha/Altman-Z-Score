![Altman Z-Score Analysis Platform](banner.png)

# Altman Z-Score Analysis Platform

**Version: 3.4.2 (2025-06-17)**

A robust, modular Python tool for comprehensive Altman Z-Score trend analysis with LLM-powered qualitative insights. This platform orchestrates complete financial analysis pipelines for single or multiple stock tickers, featuring **39 pre-analyzed companies** that showcase real-world capabilities across diverse market segments and financial profiles.

---

## System Architecture

**5-Layer Pipeline Design:**
1. **Input Validation** → Ticker verification and date parameter validation
2. **Data Acquisition** → SEC EDGAR (primary) + Yahoo Finance (market data) 
3. **Data Validation** → Pydantic schemas with missing field reporting
4. **Z-Score Computation** → Model selection and calculation with error handling
5. **Report Generation** → LLM analysis + visualization + structured outputs

**Core Principles:** Modularity, robustness, comprehensive error handling, and rich visualization with company branding.

### Key Features
- **📊 Comprehensive Test Portfolio:** 39 pre-analyzed companies spanning tech giants, growth stocks, financial services, distressed companies, and established industrials
- **🔬 Multiple Z-Score Models:** Intelligent model selection based on company characteristics (see [MODELS.md](MODELS.md))
- **🎨 Company-Branded Visualization:** Professional charts with company logos and candlestick price representations
- **🤖 LLM-Powered Insights:** Comprehensive qualitative analysis with AI-generated commentary and risk assessment
- **🔄 Multi-Ticker Analysis:** Batch processing with graceful error handling and continuation on failures
- **� Rich Analytics:** Weekly price trends, financial ratios, and comprehensive Z-Score trend analysis

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
python main.py <TICKER1> <TICKER2> ... [--date YYYY-MM-DD] [--no-plot] [--test] [--log-level DEBUG]
```

Examples:
```sh
python main.py AAPL MSFT TSLA
python main.py TSLA --date 2023-01-01
python main.py AAPL MSFT --no-plot
python main.py --test
python main.py --log-level DEBUG
```
Replace `<TICKER1> <TICKER2> ...` with one or more stock ticker symbols (e.g., `AAPL`, `MSFT`).

---

## 📊 Comprehensive Test Portfolio - 39 Companies Analyzed

This repository demonstrates the platform's capabilities through **39 pre-analyzed companies** representing a strategically diverse cross-section of the U.S. market. The portfolio was designed to showcase the tool's ability to handle various financial profiles, industry patterns, and market conditions.

### Portfolio Composition by Category:

#### 🚀 **Technology Giants (6 companies)**
- **AAPL, MSFT, NVDA, GOOGL, GOOG, AMZN** - Demonstrates analysis of the world's largest tech companies with strong balance sheets and consistent profitability

#### 📈 **High-Growth SaaS & Tech (12 companies)**  
- **SNOW, PLTR, UBER, DDOG, DOCU, CRWD, NET, MDB, SHOP, ROKU, RBLX, ZM** - Tests the platform's ability to analyze fast-growing companies with varying profitability patterns and capital structures

#### 🏦 **Financial Services (3 companies)**
- **JPM, COIN, AFRM** - Covers traditional banking (JPM) and emerging fintech (COIN, AFRM) to test financial sector-specific models

#### ⚠️ **Distressed/Cyclical Companies (8 companies)**
- **AAL, UAL, AMC, CCL, F, GE, GME, T** - Intentionally includes companies with financial challenges to demonstrate error handling and distress analysis capabilities

#### 🏭 **Established Industrials & Consumer Staples (10 companies)**
- **JNJ, PG, KO, UNH, VZ, WMT, CAT, DUK, ADP, SLB** - Represents mature, dividend-paying companies across utilities, healthcare, consumer goods, and industrial sectors

### Analysis Insights from the Portfolio:

- **Model Selection Testing:** Companies span all available Z-Score models (Original, Private, Financial, Zeta, Retail)
- **Risk Spectrum Coverage:** From safe zone (MSFT, AAPL) to distress zone (AMC, AAL) companies
- **Industry Diversification:** Technology, healthcare, finance, utilities, retail, aerospace, energy, telecommunications
- **Market Cap Range:** From mega-cap ($3T+) to mid-cap companies
- **Financial Profile Diversity:** High-growth/low-profit to mature/dividend-paying companies

Each analysis includes **complete LLM-generated reports**, **trend visualizations**, and **company branding** to demonstrate the full analytical and reporting capabilities of the platform.

### Why This Portfolio Matters:

1. **🧪 Real-World Testing:** Every company represents actual market conditions and demonstrates how the platform handles different financial scenarios
2. **📚 Educational Value:** Compare analyses across industries to understand how Z-Score models adapt to different business models
3. **🔍 Edge Case Coverage:** Includes distressed companies to showcase robust error handling and edge case analysis
4. **⚖️ Risk Spectrum:** From ultra-safe (MSFT, JNJ) to high-risk (AMC, GME) companies, demonstrating the full range of Z-Score interpretations
5. **🏭 Industry Expertise:** Each sector represented shows how industry-specific factors influence financial health assessment

The following table shows available reports for all analyzed tickers:

<!-- BEGIN_TICKERS_TABLE -->
| Logo | Company Name | Full Report | Trend Chart | Investor Advice |
|------|-------------|-------------|:-------------:|:---------------:|
| <img src="output/AAL/AAL_logo.png" alt="AAL" width="80" height="80"/> | American Airlines Group Inc | [Report](output/AAL/zscore_AAL_zscore_full_report.md) | <a href="output/AAL/zscore_AAL_trend.png"><img src="output/AAL/zscore_AAL_trend.png" alt="AAL Chart" width="400"/></a> | ❓ No Data |
| <img src="output/AAPL/AAPL_logo.png" alt="AAPL" width="80" height="80"/> | Apple Inc | [Report](output/AAPL/zscore_AAPL_zscore_full_report.md) | <a href="output/AAPL/zscore_AAPL_trend.png"><img src="output/AAPL/zscore_AAPL_trend.png" alt="AAPL Chart" width="400"/></a> | 📈 BUY (4/6) |
| <img src="output/ADP/ADP_logo.png" alt="ADP" width="80" height="80"/> | Automatic Data Processing Inc | [Report](output/ADP/zscore_ADP_zscore_full_report.md) | <a href="output/ADP/zscore_ADP_trend.png"><img src="output/ADP/zscore_ADP_trend.png" alt="ADP Chart" width="400"/></a> | ⚖️ HOLD (5/5) |
| <img src="output/AFRM/AFRM_logo.png" alt="AFRM" width="80" height="80"/> | Affirm Holdings Inc | [Report](output/AFRM/zscore_AFRM_zscore_full_report.md) | <a href="output/AFRM/zscore_AFRM_trend.png"><img src="output/AFRM/zscore_AFRM_trend.png" alt="AFRM Chart" width="400"/></a> | ❓ No Data |
| <img src="output/AMC/AMC_logo.png" alt="AMC" width="80" height="80"/> | AMC Entertainment Holdings Inc | [Report](output/AMC/zscore_AMC_zscore_full_report.md) | <a href="output/AMC/zscore_AMC_trend.png"><img src="output/AMC/zscore_AMC_trend.png" alt="AMC Chart" width="400"/></a> | 📉 SELL/HOLD |
| <img src="output/AMZN/AMZN_logo.png" alt="AMZN" width="80" height="80"/> | Amazon.com Inc | [Report](output/AMZN/zscore_AMZN_zscore_full_report.md) | <a href="output/AMZN/zscore_AMZN_trend.png"><img src="output/AMZN/zscore_AMZN_trend.png" alt="AMZN Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/CAT/CAT_logo.png" alt="CAT" width="80" height="80"/> | Caterpillar Inc | [Report](output/CAT/zscore_CAT_zscore_full_report.md) | <a href="output/CAT/zscore_CAT_trend.png"><img src="output/CAT/zscore_CAT_trend.png" alt="CAT Chart" width="400"/></a> | ⚖️ HOLD (4/6) |
| <img src="output/CCL/CCL_logo.png" alt="CCL" width="80" height="80"/> | Carnival Corp | [Report](output/CCL/zscore_CCL_zscore_full_report.md) | <a href="output/CCL/zscore_CCL_trend.png"><img src="output/CCL/zscore_CCL_trend.png" alt="CCL Chart" width="400"/></a> | 📉 SELL (3/5) |
| <img src="output/COIN/COIN_logo.png" alt="COIN" width="80" height="80"/> | Coinbase Global Inc | [Report](output/COIN/zscore_COIN_zscore_full_report.md) | <a href="output/COIN/zscore_COIN_trend.png"><img src="output/COIN/zscore_COIN_trend.png" alt="COIN Chart" width="400"/></a> | 📈 BUY |
| <img src="output/CRWD/CRWD_logo.png" alt="CRWD" width="80" height="80"/> | CrowdStrike Holdings Inc | [Report](output/CRWD/zscore_CRWD_zscore_full_report.md) | <a href="output/CRWD/zscore_CRWD_trend.png"><img src="output/CRWD/zscore_CRWD_trend.png" alt="CRWD Chart" width="400"/></a> | 📈 BUY (4/6) |
| <img src="output/DDOG/DDOG_logo.png" alt="DDOG" width="80" height="80"/> | Datadog Inc | [Report](output/DDOG/zscore_DDOG_zscore_full_report.md) | <a href="output/DDOG/zscore_DDOG_trend.png"><img src="output/DDOG/zscore_DDOG_trend.png" alt="DDOG Chart" width="400"/></a> | 📈 BUY (4/6) |
| <img src="output/DOCU/DOCU_logo.png" alt="DOCU" width="80" height="80"/> | DocuSign Inc | [Report](output/DOCU/zscore_DOCU_zscore_full_report.md) | <a href="output/DOCU/zscore_DOCU_trend.png"><img src="output/DOCU/zscore_DOCU_trend.png" alt="DOCU Chart" width="400"/></a> | 📊 MIXED (3B/3H/0S) |
| <img src="output/DUK/DUK_logo.png" alt="DUK" width="80" height="80"/> | Duke Energy Corp | [Report](output/DUK/zscore_DUK_zscore_full_report.md) | <a href="output/DUK/zscore_DUK_trend.png"><img src="output/DUK/zscore_DUK_trend.png" alt="DUK Chart" width="400"/></a> | 📊 MIXED (0B/3H/3S) |
| <img src="output/F/F_logo.png" alt="F" width="80" height="80"/> | Ford Motor Co | [Report](output/F/zscore_F_zscore_full_report.md) | <a href="output/F/zscore_F_trend.png"><img src="output/F/zscore_F_trend.png" alt="F Chart" width="400"/></a> | ❓ No Data |
| <img src="output/GE/GE_logo.png" alt="GE" width="80" height="80"/> | GE Aerospace | [Report](output/GE/zscore_GE_zscore_full_report.md) | <a href="output/GE/zscore_GE_trend.png"><img src="output/GE/zscore_GE_trend.png" alt="GE Chart" width="400"/></a> | 📊 MIXED (3B/3H/0S) |
| <img src="output/GME/GME_logo.png" alt="GME" width="80" height="80"/> | GameStop Corp | [Report](output/GME/zscore_GME_zscore_full_report.md) | <a href="output/GME/zscore_GME_trend.png"><img src="output/GME/zscore_GME_trend.png" alt="GME Chart" width="400"/></a> | 📈 BUY |
| <img src="output/GOOG/GOOG_logo.png" alt="GOOG" width="80" height="80"/> | Alphabet Inc | [Report](output/GOOG/zscore_GOOG_zscore_full_report.md) | <a href="output/GOOG/zscore_GOOG_trend.png"><img src="output/GOOG/zscore_GOOG_trend.png" alt="GOOG Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/GOOGL/GOOGL_logo.png" alt="GOOGL" width="80" height="80"/> | Alphabet Inc | [Report](output/GOOGL/zscore_GOOGL_zscore_full_report.md) | <a href="output/GOOGL/zscore_GOOGL_trend.png"><img src="output/GOOGL/zscore_GOOGL_trend.png" alt="GOOGL Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/JNJ/JNJ_logo.png" alt="JNJ" width="80" height="80"/> | Johnson & Johnson | [Report](output/JNJ/zscore_JNJ_zscore_full_report.md) | <a href="output/JNJ/zscore_JNJ_trend.png"><img src="output/JNJ/zscore_JNJ_trend.png" alt="JNJ Chart" width="400"/></a> | 📈 BUY |
| <img src="output/JPM/JPM_logo.png" alt="JPM" width="80" height="80"/> | JPMorgan Chase & Co | [Report](output/JPM/zscore_JPM_zscore_full_report.md) | <a href="output/JPM/zscore_JPM_trend.png"><img src="output/JPM/zscore_JPM_trend.png" alt="JPM Chart" width="400"/></a> | 📊 MIXED (0B/3H/3S) |
| <img src="output/KO/KO_logo.png" alt="KO" width="80" height="80"/> | Coca-Cola Co | [Report](output/KO/zscore_KO_zscore_full_report.md) | <a href="output/KO/zscore_KO_trend.png"><img src="output/KO/zscore_KO_trend.png" alt="KO Chart" width="400"/></a> | 📈 BUY (4/6) |
| <img src="output/MDB/MDB_logo.png" alt="MDB" width="80" height="80"/> | MongoDB Inc | [Report](output/MDB/zscore_MDB_zscore_full_report.md) | <a href="output/MDB/zscore_MDB_trend.png"><img src="output/MDB/zscore_MDB_trend.png" alt="MDB Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/MSFT/MSFT_logo.png" alt="MSFT" width="80" height="80"/> | Microsoft Corp | [Report](output/MSFT/zscore_MSFT_zscore_full_report.md) | <a href="output/MSFT/zscore_MSFT_trend.png"><img src="output/MSFT/zscore_MSFT_trend.png" alt="MSFT Chart" width="400"/></a> | 📈 BUY (Most Profiles) |
| <img src="output/NET/NET_logo.png" alt="NET" width="80" height="80"/> | Cloudflare Inc | [Report](output/NET/zscore_NET_zscore_full_report.md) | <a href="output/NET/zscore_NET_trend.png"><img src="output/NET/zscore_NET_trend.png" alt="NET Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/NVDA/NVDA_logo.png" alt="NVDA" width="80" height="80"/> | NVIDIA Corp | [Report](output/NVDA/zscore_NVDA_zscore_full_report.md) | <a href="output/NVDA/zscore_NVDA_trend.png"><img src="output/NVDA/zscore_NVDA_trend.png" alt="NVDA Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/PG/PG_logo.png" alt="PG" width="80" height="80"/> | Procter & Gamble Co | [Report](output/PG/zscore_PG_zscore_full_report.md) | <a href="output/PG/zscore_PG_trend.png"><img src="output/PG/zscore_PG_trend.png" alt="PG Chart" width="400"/></a> | 📈 BUY (4/6) |
| <img src="output/PLTR/PLTR_logo.png" alt="PLTR" width="80" height="80"/> | Palantir Technologies Inc | [Report](output/PLTR/zscore_PLTR_zscore_full_report.md) | <a href="output/PLTR/zscore_PLTR_trend.png"><img src="output/PLTR/zscore_PLTR_trend.png" alt="PLTR Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/RBLX/RBLX_logo.png" alt="RBLX" width="80" height="80"/> | Roblox Corp | [Report](output/RBLX/zscore_RBLX_zscore_full_report.md) | <a href="output/RBLX/zscore_RBLX_trend.png"><img src="output/RBLX/zscore_RBLX_trend.png" alt="RBLX Chart" width="400"/></a> | ⚖️ HOLD (4/6) |
| <img src="output/ROKU/ROKU_logo.png" alt="ROKU" width="80" height="80"/> | Roku Inc | [Report](output/ROKU/zscore_ROKU_zscore_full_report.md) | <a href="output/ROKU/zscore_ROKU_trend.png"><img src="output/ROKU/zscore_ROKU_trend.png" alt="ROKU Chart" width="400"/></a> | 📊 MIXED (3B/3H/0S) |
| <img src="output/SHOP/SHOP_logo.png" alt="SHOP" width="80" height="80"/> | Shopify Inc | [Report](output/SHOP/zscore_SHOP_zscore_full_report.md) | <a href="output/SHOP/zscore_SHOP_trend.png"><img src="output/SHOP/zscore_SHOP_trend.png" alt="SHOP Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/SLB/SLB_logo.png" alt="SLB" width="80" height="80"/> | Schlumberger NV | [Report](output/SLB/zscore_SLB_zscore_full_report.md) | <a href="output/SLB/zscore_SLB_trend.png"><img src="output/SLB/zscore_SLB_trend.png" alt="SLB Chart" width="400"/></a> | ⚖️ HOLD (4/6) |
| <img src="output/SNOW/SNOW_logo.png" alt="SNOW" width="80" height="80"/> | Snowflake Inc | [Report](output/SNOW/zscore_SNOW_zscore_full_report.md) | <a href="output/SNOW/zscore_SNOW_trend.png"><img src="output/SNOW/zscore_SNOW_trend.png" alt="SNOW Chart" width="400"/></a> | 📈 BUY (3/6) |
| <img src="output/T/T_logo.png" alt="T" width="80" height="80"/> | AT&T Inc | [Report](output/T/zscore_T_zscore_full_report.md) | <a href="output/T/zscore_T_trend.png"><img src="output/T/zscore_T_trend.png" alt="T Chart" width="400"/></a> | ❓ No Data |
| <img src="output/TSLA/TSLA_logo.png" alt="TSLA" width="80" height="80"/> | Tesla Inc | [Report](output/TSLA/zscore_TSLA_zscore_full_report.md) | <a href="output/TSLA/zscore_TSLA_trend.png"><img src="output/TSLA/zscore_TSLA_trend.png" alt="TSLA Chart" width="400"/></a> | 📈 BUY |
| <img src="output/UAL/UAL_logo.png" alt="UAL" width="80" height="80"/> | United Airlines Holdings Inc | [Report](output/UAL/zscore_UAL_zscore_full_report.md) | <a href="output/UAL/zscore_UAL_trend.png"><img src="output/UAL/zscore_UAL_trend.png" alt="UAL Chart" width="400"/></a> | ❓ No Data |
| <img src="output/UBER/UBER_logo.png" alt="UBER" width="80" height="80"/> | Uber Technologies Inc | [Report](output/UBER/zscore_UBER_zscore_full_report.md) | <a href="output/UBER/zscore_UBER_trend.png"><img src="output/UBER/zscore_UBER_trend.png" alt="UBER Chart" width="400"/></a> | ⚖️ HOLD (4/6) |
| <img src="output/UNH/UNH_logo.png" alt="UNH" width="80" height="80"/> | UnitedHealth Group Inc | [Report](output/UNH/zscore_UNH_zscore_full_report.md) | <a href="output/UNH/zscore_UNH_trend.png"><img src="output/UNH/zscore_UNH_trend.png" alt="UNH Chart" width="400"/></a> | 📈 BUY |
| <img src="output/VZ/VZ_logo.png" alt="VZ" width="80" height="80"/> | Verizon Communications Inc | [Report](output/VZ/zscore_VZ_zscore_full_report.md) | <a href="output/VZ/zscore_VZ_trend.png"><img src="output/VZ/zscore_VZ_trend.png" alt="VZ Chart" width="400"/></a> | 📉 SELL/HOLD |
| <img src="output/WMT/WMT_logo.png" alt="WMT" width="80" height="80"/> | Walmart Inc | [Report](output/WMT/zscore_WMT_zscore_full_report.md) | <a href="output/WMT/zscore_WMT_trend.png"><img src="output/WMT/zscore_WMT_trend.png" alt="WMT Chart" width="400"/></a> | 📈 BUY (4/6) |
| <img src="output/ZM/ZM_logo.png" alt="ZM" width="80" height="80"/> | Zoom Communications Inc | [Report](output/ZM/zscore_ZM_zscore_full_report.md) | <a href="output/ZM/zscore_ZM_trend.png"><img src="output/ZM/zscore_ZM_trend.png" alt="ZM Chart" width="400"/></a> | 📈 BUY (4/6) |
<!-- END_TICKERS_TABLE -->

---

## Updating the Sample Reports Table

To automatically update the sample reports table in this README, use the provided script:

- **`generate_readme_table.py`**: Scans the `output/` directory for tickers with all required report files and automatically updates the table section in the README.md file (between the markers). Now includes **investor advice extraction** for actionable insights.

Usage:
```sh
python generate_readme_table.py
```

The script:
1. Generates the table and saves it to `table.md`
2. **NEW:** Extracts investor recommendations from each report and adds them as an "Investor Advice" column
3. Automatically updates the table in README.md between the `<!-- BEGIN_TICKERS_TABLE -->` and `<!-- END_TICKERS_TABLE -->` markers
4. Shows a confirmation message when the update is successful

**Investor Advice Column Features:**
- 📈 **BUY** recommendations with ratios (e.g., "BUY (4/6)")
- ⚖️ **HOLD** recommendations for neutral positions
- 📉 **SELL** recommendations for high-risk companies
- 📊 **MIXED** recommendations showing breakdown
- Clear visual indicators for quick decision-making

---

## Recent Improvements (3.0.0) ✅ FULLY COMPLETED
- **✅ Full modular reorganization:** All code grouped by functionality (core, models, company, validation, market, plotting, computation, misc)
- **✅ All imports fixed:** Updated to use new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`)
- **✅ Integration testing:** Added `tests/test_integration_main.py` to catch import/runtime errors in main pipeline
- **✅ Critical import fixes:** Resolved all ModuleNotFoundError issues across the codebase (fetcher_factory.py, industry_classifier.py, etc.)
- **✅ Main pipeline verified:** Successfully runs `python main.py msft` without import errors
- **✅ Improved LLM prompt templates:** Enhanced code injection for reporting with more complete, context-aware, and robust analysis outputs
- **✅ Documentation updated:** All documentation reflects new structure and completed modularization
- **✅ All tests passing:** Both unit tests and integration tests pass after reorganization
- **✅ Modularization & refactoring complete:** All refactoring work finished and fully tested

**🎯 v3.0.0 is now ready for production deployment and user feedback collection.**

---

## Documentation & Project Roadmap
- For the unified project plan, roadmap, actionable tasks, and technical references, see [TODO.md](./TODO.md)
- See `LEARNINGS.md` for technical notes and known issues
- **For LLM Copilot troubleshooting and analysis:** See [copilot.md](./copilot.md) for step-by-step instructions on analyzing pipeline outputs and debugging issues using VS Code tools

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
- Document significant learnings in `LEARNINGS.md`

## Troubleshooting & Analysis Tools

### LLM Copilot Analysis
The repository includes `copilot.md` - comprehensive instructions for LLM Copilot to systematically analyze pipeline outputs, identify issues, and troubleshoot problems using VS Code tools.

**Key Features:**
- **Automated Analysis:** Step-by-step instructions using VS Code tools (list_dir, read_file, grep_search, etc.)
- **Success Rate Assessment:** Comprehensive evaluation of ticker analysis completeness
- **Issue Pattern Detection:** Systematic identification of common failure modes
- **Root Cause Analysis:** Detailed investigation workflows for debugging
- **Solution Documentation:** Required logging of all findings before code changes

**Usage for LLM Copilot:**
1. Follow the workflow in `copilot.md` to analyze all processed tickers
2. Create detailed troubleshooting logs in `Copilot_Troubleshoot.md`
3. Identify and prioritize the most common issues
4. Develop and test solutions based on documented findings

**Human Usage:**
The same systematic approach can be followed manually for pipeline analysis and debugging.

### Quick Start for Issue Analysis
```bash
# Analyze current pipeline outputs
python -c "
import os
print('Available tickers in output/:')
for ticker in os.listdir('output'):
    print(f'  {ticker}')
"

# Test a specific ticker with debug logging
python main.py MSFT --date 2024-01-01 --log-level DEBUG
```

---

## License
MIT (see LICENSE file)

---

## Data/API Credits & Disclaimers

This project uses data and APIs from the following sources:
- **Yahoo Finance** (yfinance): Market data and financials. Not affiliated with or endorsed by Yahoo. Data may be delayed or incomplete. See Yahoo's terms of use.
- **Finnhub.io**: Company profiles, logos, and additional financial data. Not affiliated with or endorsed by Finnhub. Data provided under Finnhub's free and paid API terms.
- **SEC EDGAR/XBRL**: Official regulatory filings. Data is public domain but may be subject to update delays or errors.

**Disclaimers:**
- All trademarks, service marks, and company names are the property of their respective owners.
- This project is not affiliated with, endorsed by, or sponsored by Yahoo, Finnhub, the SEC, or any other data provider.
- Data is provided "as is" for informational and educational purposes only. No warranty is made as to accuracy, completeness, or timeliness. Use at your own risk.
- Always consult the official data provider's terms of service and licensing before commercial use.

---

For more details, see the full documentation in this repository and referenced files.

## Project Structure (as of 3.0.0)

```
src/altman_zscore/
    api/                # API clients and integrations (Finnhub, OpenAI, SEC, Yahoo, etc.)
    company/            # Company profile, status, helpers, CIK/SIC lookup
    computation/        # Z-Score computation, constants, formulas, DRY helpers
    core/               # Main pipeline, orchestration, progress tracking, reporting
    data_fetching/      # Financial and market data fetching (Yahoo, SEC, etc.)
    market/             # Market data helpers and utilities
    misc/               # Shared utilities and miscellaneous helpers
    models/             # Z-Score models, thresholds, enums, industry classifier
    plotting/           # Visualization, plotting helpers, terminal output
    schemas/            # Pydantic schemas and data validation models
    utils/              # Paths, IO, logging, error handling, etc.
    validation/         # Data validation logic
    prompts/            # LLM prompt templates
    ...
output/                 # Analysis results, reports, and plots (per ticker)
tests/                  # Unit and integration tests
```

- Each folder contains focused, testable modules.
- All imports use the new modular paths (e.g., `from altman_zscore.plotting.plotting_main import plot_zscore_trend`).
- For the project plan, roadmap, and actionable tasks, see [TODO.md](./TODO.md)

---

## Example: Plotting Z-Score Trend

To generate a Z-Score trend plot in your own script or notebook:

```python
from altman_zscore.plotting.plotting_main import plot_zscore_trend

# df: DataFrame with columns ['quarter_end', 'zscore']
# ticker: str, model: str, out_base: str
plot_zscore_trend(df, ticker, model, out_base)
```
