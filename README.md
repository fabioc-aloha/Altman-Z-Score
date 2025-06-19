![Al**Version: 3.5.5 (2025-06-18) 📚 Documentation Excellence**man Z-Score Analysis Platform](banner.png)

# Altman Z-Score Analysis Platform

**Version: 3.5.3 (2025-06-18) �️ Ford Sales Field Fix**

A robust Python tool for comprehensive Altman Z-Score financial analysis with AI-powered insights. Features **47 pre-analyzed companies** with complete **CEO/CFO/Investor guidance matrix** - the industry's most comprehensive stakeholder decision support table.

**Latest (v3.5.5):** Comprehensive documentation enhancement with clear Past/Present/Future strategy. Enhanced FLOW.md with detailed system architecture, field mapping innovations, and performance metrics.

---

## Quick Start

```sh
# Analyze a single company
python main.py MSFT

# Analyze with specific date
python main.py AAPL --date 2024-01-01

# Multiple companies
python main.py AAPL MSFT TSLA

# Generate portfolio table
python generate_readme_table.py
```

## Key Features

- **� Actionable Portfolio Table:** Immediate investment recommendations with visual indicators
- **🤖 AI-Powered Analysis:** 11-section comprehensive financial health reports with pattern recognition
- **📈 Enhanced Insights:** New "Other Relevant Insights" section identifies cross-data patterns  
- **📊 Real Data Integration:** Market sentiment analysis using actual analyst recommendations
- **🔄 Robust Data Pipeline:** SEC EDGAR + Yahoo Finance integration with error handling
- **🏢 47-Company Portfolio:** Real-world examples across 5 market segments

## Output Structure
All analysis saved to `output/<TICKER>/`:
- **Full Report:** `zscore_<TICKER>_zscore_full_report.md` (11-section AI analysis + strategic recommendations)
- **Trend Chart:** `zscore_<TICKER>_trend.png` (visual Z-Score analysis)
- **Data Files:** CSV/JSON with quarterly calculations and real analyst recommendations

---

## 📊 Portfolio Analysis - 47 Companies

Strategic test portfolio demonstrating platform capabilities across market segments:

**🚀 Tech Giants (7):** AAPL, MSFT, NVDA, GOOGL, GOOG, AMZN, META  
**📈 High-Growth SaaS (12):** SNOW, PLTR, UBER, DDOG, DOCU, CRWD, NET, MDB, SHOP, ROKU, RBLX, ZM  
**🏦 Financial Services (3):** JPM, COIN, AFRM  
**⚠️ Distressed/Cyclical (8):** AAL, UAL, AMC, CCL, F, GE, GME, T  
**🏭 Established Industrials (17):** JNJ, PG, KO, UNH, VZ, WMT, CAT, DUK, ADP, SLB, and others

### Portfolio Table

**Recommendations by Role:**
- **CEO**: Strategic leadership focus • **CFO**: Financial strategy focus • **Conservative**: Capital Preservation • **Dividend**: Income-focused  
- **Value**: Value investing • **Growth**: Capital Appreciation  
- **Aggressive**: High-risk growth • **Short-Seller**: Bearish positions  
- **📈 BUY** • **⚖️ HOLD** • **📉 SELL**

**CEO Recommendations:** 🚀 FOCUS INNOVATION • 📢 COMMUNICATE GROWTH • 🔧 RESTRUCTURE • ⚡ EXECUTION FOCUS • 🎯 STRATEGIC FOCUS  
**CFO Recommendations:** 💰 OPTIMIZE & INVEST • 💰 OPTIMIZE CAPITAL • 📊 STRATEGIC INVEST • 📊 MONITOR CAPITAL • ⚖️ MAINTAIN STABILITY

<!-- BEGIN_TICKERS_TABLE -->
| Logo | Company Name | Full Report | Trend Chart | CEO/CFO & Investor Advice |
|------|-------------|-------------|:-------------:|:---------------------------:|
| <img src="output/MSFT/MSFT_logo.png" alt="MSFT" width="50"/> | Microsoft Corp | [Report](output/MSFT/zscore_MSFT_zscore_full_report.md) | <a href="output/MSFT/zscore_MSFT_trend.png"><img src="output/MSFT/zscore_MSFT_trend.png" alt="MSFT Chart" width="500"/></a> | <sup>CEO: 🚀 INNOVATE & MONITOR</sup><br><sup>CFO: 📈 ENHANCE IR</sup><br><sup>Conservative: ⚖️ HOLD</sup><br><sup>Dividend: ⚖️ HOLD</sup><br><sup>Value: 📈 BUY</sup><br><sup>Growth: 📈 BUY</sup><br><sup>Aggressive: 📈 BUY</sup><br><sup>Short-Seller: 📉 SELL</sup> |
| <img src="output/SONO/SONO_logo.png" alt="SONO" width="50"/> | Sonos Inc | [Report](output/SONO/zscore_SONO_zscore_full_report.md) | <a href="output/SONO/zscore_SONO_trend.png"><img src="output/SONO/zscore_SONO_trend.png" alt="SONO Chart" width="500"/></a> | <sup>CEO: 📢 COMMUNICATE GROWTH</sup><br><sup>CFO: 📊 MANAGE DEBT</sup><br><sup>Conservative: ⚖️ HOLD</sup><br><sup>Dividend: ⚖️ HOLD</sup><br><sup>Value: ⚖️ HOLD</sup><br><sup>Growth: ⚖️ HOLD</sup><br><sup>Aggressive: 📈 BUY</sup><br><sup>Short-Seller: ⚖️ HOLD</sup> |
<!-- END_TICKERS_TABLE -->

---

## Table Generation

Update the portfolio table automatically:

```sh
python generate_readme_table.py
```

**Enhanced Features:**
- **Detailed Investor Profiles**: Shows BUY/HOLD/SELL for each investor type
- **Multi-line Format**: Clear, readable recommendations in table cells
- **Professional Layout**: Full profile names with emoji indicators
- **Comprehensive Coverage**: 6 investor profiles per company analysis

**Features:**
- **Profile-Based Recommendations:** Shows BUY/HOLD/SELL for each investor type
- **Conservative to Aggressive:** Covers all risk tolerance levels  
- **Visual Indicators:** 📈 BUY, ⚖️ HOLD, 📉 SELL with compact notation
- **Auto-updates README** between table markers

---

## Setup & Installation

```sh
# Install dependencies
pip install -r requirements.txt

# Copy environment template (add your API keys)
cp .env.example .env

# Test installation
python main.py --test
```

**Requirements:** Python 3.11+

---

## Documentation

- **[TODO.md](./TODO.md)** - Project roadmap and completed milestones
- **[MODELS.md](MODELS.md)** - Z-Score model details and selection logic
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and improvements

> **Known Limitation:** The Zeta model implementation currently uses a single-period approach. X₂ (Stability of Earnings) is set to 0 due to lack of multi-year net income history. This limitation is documented in MODELS.md, and will be revisited in future releases.

---

## License & Data Sources

**License:** MIT (see LICENSE file)

**Data Sources:**
- Yahoo Finance (market data)
- SEC EDGAR (regulatory filings)  
- Finnhub.io (company profiles/logos)

*All trademarks are property of their respective owners. This project is not affiliated with any data provider. Use for educational/informational purposes only.*
