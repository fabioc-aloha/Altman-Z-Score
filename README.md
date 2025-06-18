![Altman Z-Score Analysis Platform](banner.png)

# Altman Z-Score Analysis Platform

**Version: 3.5.0 (2025-06-17) 🥇 Golden Release**

A robust Python tool for comprehensive Altman Z-Score financial analysis with AI-powered insights. Features **47 pre-analyzed companies** with complete **CEO/CFO/Investor guidance matrix** - the industry's most comprehensive stakeholder decision support table.

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
- **🤖 AI-Powered Analysis:** LLM-generated comprehensive financial health reports  
- **� Professional Visualization:** Company-branded charts with trend analysis
- **🔄 Robust Data Pipeline:** SEC EDGAR + Yahoo Finance integration with error handling
- **🏢 47-Company Portfolio:** Real-world examples across 5 market segments

## Output Structure
All analysis saved to `output/<TICKER>/`:
- **Full Report:** `zscore_<TICKER>_zscore_full_report.md` (AI analysis + recommendations)
- **Trend Chart:** `zscore_<TICKER>_trend.png` (visual Z-Score analysis)
- **Data Files:** CSV/JSON with quarterly calculations and metadata

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
| <img src="output/AAL/AAL_logo.png" alt="AAL" width="50"/> | American Airlines Group Inc | [Report](output/AAL/zscore_AAL_zscore_full_report.md) | <a href="output/AAL/zscore_AAL_trend.png"><img src="output/AAL/zscore_AAL_trend.png" alt="AAL Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: 📉 SELL<br>**Aggressive**: ⚖️ HOLD<br>**Short-Seller**: 📈 BUY |
| <img src="output/AAPL/AAPL_logo.png" alt="AAPL" width="50"/> | Apple Inc | [Report](output/AAPL/zscore_AAPL_zscore_full_report.md) | <a href="output/AAPL/zscore_AAPL_trend.png"><img src="output/AAPL/zscore_AAPL_trend.png" alt="AAPL Chart" width="400"/></a> | **CEO**: 🚀 FOCUS INNOVATION<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: 📈 BUY<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/ADP/ADP_logo.png" alt="ADP" width="50"/> | Automatic Data Processing Inc | [Report](output/ADP/zscore_ADP_zscore_full_report.md) | <a href="output/ADP/zscore_ADP_trend.png"><img src="output/ADP/zscore_ADP_trend.png" alt="ADP Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: ⚖️ HOLD<br>**Growth**: 📈 BUY<br>**Aggressive**: ⚖️ HOLD<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/AFRM/AFRM_logo.png" alt="AFRM" width="50"/> | Affirm Holdings Inc | [Report](output/AFRM/zscore_AFRM_zscore_full_report.md) | <a href="output/AFRM/zscore_AFRM_trend.png"><img src="output/AFRM/zscore_AFRM_trend.png" alt="AFRM Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📈 BUY |
| <img src="output/AMC/AMC_logo.png" alt="AMC" width="50"/> | AMC Entertainment Holdings Inc | [Report](output/AMC/zscore_AMC_zscore_full_report.md) | <a href="output/AMC/zscore_AMC_trend.png"><img src="output/AMC/zscore_AMC_trend.png" alt="AMC Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: 📉 SELL<br>**Aggressive**: 📉 SELL<br>**Short-Seller**: 📉 SELL |
| <img src="output/AMZN/AMZN_logo.png" alt="AMZN" width="50"/> | Amazon.com Inc | [Report](output/AMZN/zscore_AMZN_zscore_full_report.md) | <a href="output/AMZN/zscore_AMZN_trend.png"><img src="output/AMZN/zscore_AMZN_trend.png" alt="AMZN Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/CAT/CAT_logo.png" alt="CAT" width="50"/> | Caterpillar Inc | [Report](output/CAT/zscore_CAT_zscore_full_report.md) | <a href="output/CAT/zscore_CAT_trend.png"><img src="output/CAT/zscore_CAT_trend.png" alt="CAT Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: ⚖️ HOLD<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/CCL/CCL_logo.png" alt="CCL" width="50"/> | Carnival Corp | [Report](output/CCL/zscore_CCL_zscore_full_report.md) | <a href="output/CCL/zscore_CCL_trend.png"><img src="output/CCL/zscore_CCL_trend.png" alt="CCL Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 📊 MONITOR CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/COIN/COIN_logo.png" alt="COIN" width="50"/> | Coinbase Global Inc | [Report](output/COIN/zscore_COIN_zscore_full_report.md) | <a href="output/COIN/zscore_COIN_trend.png"><img src="output/COIN/zscore_COIN_trend.png" alt="COIN Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: ⚖️ HOLD<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/CRWD/CRWD_logo.png" alt="CRWD" width="50"/> | CrowdStrike Holdings Inc | [Report](output/CRWD/zscore_CRWD_zscore_full_report.md) | <a href="output/CRWD/zscore_CRWD_trend.png"><img src="output/CRWD/zscore_CRWD_trend.png" alt="CRWD Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: 📈 BUY<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/DDOG/DDOG_logo.png" alt="DDOG" width="50"/> | Datadog Inc | [Report](output/DDOG/zscore_DDOG_zscore_full_report.md) | <a href="output/DDOG/zscore_DDOG_trend.png"><img src="output/DDOG/zscore_DDOG_trend.png" alt="DDOG Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📈 BUY<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/DOCU/DOCU_logo.png" alt="DOCU" width="50"/> | DocuSign Inc | [Report](output/DOCU/zscore_DOCU_zscore_full_report.md) | <a href="output/DOCU/zscore_DOCU_trend.png"><img src="output/DOCU/zscore_DOCU_trend.png" alt="DOCU Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/DUK/DUK_logo.png" alt="DUK" width="50"/> | Duke Energy Corp | [Report](output/DUK/zscore_DUK_zscore_full_report.md) | <a href="output/DUK/zscore_DUK_trend.png"><img src="output/DUK/zscore_DUK_trend.png" alt="DUK Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: ⚖️ HOLD<br>**Short-Seller**: 📉 SELL |
| <img src="output/F/F_logo.png" alt="F" width="50"/> | Ford Motor Co | [Report](output/F/zscore_F_zscore_full_report.md) | <a href="output/F/zscore_F_trend.png"><img src="output/F/zscore_F_trend.png" alt="F Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 📊 MONITOR CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: 📉 SELL<br>**Short-Seller**: 📈 BUY |
| <img src="output/GE/GE_logo.png" alt="GE" width="50"/> | GE Aerospace | [Report](output/GE/zscore_GE_zscore_full_report.md) | <a href="output/GE/zscore_GE_trend.png"><img src="output/GE/zscore_GE_trend.png" alt="GE Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/GME/GME_logo.png" alt="GME" width="50"/> | GameStop Corp | [Report](output/GME/zscore_GME_zscore_full_report.md) | <a href="output/GME/zscore_GME_trend.png"><img src="output/GME/zscore_GME_trend.png" alt="GME Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📈 BUY<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/GOOG/GOOG_logo.png" alt="GOOG" width="50"/> | Alphabet Inc | [Report](output/GOOG/zscore_GOOG_zscore_full_report.md) | <a href="output/GOOG/zscore_GOOG_trend.png"><img src="output/GOOG/zscore_GOOG_trend.png" alt="GOOG Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/GOOGL/GOOGL_logo.png" alt="GOOGL" width="50"/> | Alphabet Inc | [Report](output/GOOGL/zscore_GOOGL_zscore_full_report.md) | <a href="output/GOOGL/zscore_GOOGL_trend.png"><img src="output/GOOGL/zscore_GOOGL_trend.png" alt="GOOGL Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/JNJ/JNJ_logo.png" alt="JNJ" width="50"/> | Johnson & Johnson | [Report](output/JNJ/zscore_JNJ_zscore_full_report.md) | <a href="output/JNJ/zscore_JNJ_trend.png"><img src="output/JNJ/zscore_JNJ_trend.png" alt="JNJ Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: 📈 BUY<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/JPM/JPM_logo.png" alt="JPM" width="50"/> | JPMorgan Chase & Co | [Report](output/JPM/zscore_JPM_zscore_full_report.md) | <a href="output/JPM/zscore_JPM_trend.png"><img src="output/JPM/zscore_JPM_trend.png" alt="JPM Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: ⚖️ HOLD<br>**Short-Seller**: 📉 SELL |
| <img src="output/KO/KO_logo.png" alt="KO" width="50"/> | Coca-Cola Co | [Report](output/KO/zscore_KO_zscore_full_report.md) | <a href="output/KO/zscore_KO_trend.png"><img src="output/KO/zscore_KO_trend.png" alt="KO Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: 📈 BUY<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/MDB/MDB_logo.png" alt="MDB" width="50"/> | MongoDB Inc | [Report](output/MDB/zscore_MDB_zscore_full_report.md) | <a href="output/MDB/zscore_MDB_trend.png"><img src="output/MDB/zscore_MDB_trend.png" alt="MDB Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 📊 STRATEGIC INVEST<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/MSFT/MSFT_logo.png" alt="MSFT" width="50"/> | Microsoft Corp | [Report](output/MSFT/zscore_MSFT_zscore_full_report.md) | <a href="output/MSFT/zscore_MSFT_trend.png"><img src="output/MSFT/zscore_MSFT_trend.png" alt="MSFT Chart" width="400"/></a> | **CEO**: 🚀 INNOVATE & MONITOR<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: 📈 BUY<br>**Dividend**: 📈 BUY<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/NET/NET_logo.png" alt="NET" width="50"/> | Cloudflare Inc | [Report](output/NET/zscore_NET_zscore_full_report.md) | <a href="output/NET/zscore_NET_trend.png"><img src="output/NET/zscore_NET_trend.png" alt="NET Chart" width="400"/></a> | **CEO**: 🚀 FOCUS INNOVATION<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/NVDA/NVDA_logo.png" alt="NVDA" width="50"/> | NVIDIA Corp | [Report](output/NVDA/zscore_NVDA_zscore_full_report.md) | <a href="output/NVDA/zscore_NVDA_trend.png"><img src="output/NVDA/zscore_NVDA_trend.png" alt="NVDA Chart" width="400"/></a> | **CEO**: 🚀 INNOVATE & MONITOR<br>**CFO**: 📊 STRATEGIC INVEST<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/PG/PG_logo.png" alt="PG" width="50"/> | Procter & Gamble Co | [Report](output/PG/zscore_PG_zscore_full_report.md) | <a href="output/PG/zscore_PG_trend.png"><img src="output/PG/zscore_PG_trend.png" alt="PG Chart" width="400"/></a> | **CEO**: 📊 MONITOR INDICATORS<br>**CFO**: � PLAN STRATEGY<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: 📈 BUY<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/PLTR/PLTR_logo.png" alt="PLTR" width="50"/> | Palantir Technologies Inc | [Report](output/PLTR/zscore_PLTR_zscore_full_report.md) | <a href="output/PLTR/zscore_PLTR_trend.png"><img src="output/PLTR/zscore_PLTR_trend.png" alt="PLTR Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 📊 STRATEGIC INVEST<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/RBLX/RBLX_logo.png" alt="RBLX" width="50"/> | Roblox Corp | [Report](output/RBLX/zscore_RBLX_zscore_full_report.md) | <a href="output/RBLX/zscore_RBLX_trend.png"><img src="output/RBLX/zscore_RBLX_trend.png" alt="RBLX Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: ⚖️ HOLD<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/ROKU/ROKU_logo.png" alt="ROKU" width="50"/> | Roku Inc | [Report](output/ROKU/zscore_ROKU_zscore_full_report.md) | <a href="output/ROKU/zscore_ROKU_trend.png"><img src="output/ROKU/zscore_ROKU_trend.png" alt="ROKU Chart" width="400"/></a> | **CEO**: 🚀 FOCUS INNOVATION<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/SHOP/SHOP_logo.png" alt="SHOP" width="50"/> | Shopify Inc | [Report](output/SHOP/zscore_SHOP_zscore_full_report.md) | <a href="output/SHOP/zscore_SHOP_trend.png"><img src="output/SHOP/zscore_SHOP_trend.png" alt="SHOP Chart" width="400"/></a> | **CEO**: 📊 MONITOR INDICATORS<br>**CFO**: ⚖️ MAINTAIN STABILITY<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/SLB/SLB_logo.png" alt="SLB" width="50"/> | Schlumberger NV | [Report](output/SLB/zscore_SLB_zscore_full_report.md) | <a href="output/SLB/zscore_SLB_trend.png"><img src="output/SLB/zscore_SLB_trend.png" alt="SLB Chart" width="400"/></a> | **CEO**: ✂️ COST CONTROL<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: ⚖️ HOLD<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/SNOW/SNOW_logo.png" alt="SNOW" width="50"/> | Snowflake Inc | [Report](output/SNOW/zscore_SNOW_zscore_full_report.md) | <a href="output/SNOW/zscore_SNOW_trend.png"><img src="output/SNOW/zscore_SNOW_trend.png" alt="SNOW Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/T/T_logo.png" alt="T" width="50"/> | AT&T Inc | [Report](output/T/zscore_T_zscore_full_report.md) | <a href="output/T/zscore_T_trend.png"><img src="output/T/zscore_T_trend.png" alt="T Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: ⚖️ HOLD<br>**Short-Seller**: 📉 SELL |
| <img src="output/TSLA/TSLA_logo.png" alt="TSLA" width="50"/> | Tesla Inc | [Report](output/TSLA/zscore_TSLA_zscore_full_report.md) | <a href="output/TSLA/zscore_TSLA_trend.png"><img src="output/TSLA/zscore_TSLA_trend.png" alt="TSLA Chart" width="400"/></a> | **CEO**: 📊 MONITOR INDICATORS<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
| <img src="output/UAL/UAL_logo.png" alt="UAL" width="50"/> | United Airlines Holdings Inc | [Report](output/UAL/zscore_UAL_zscore_full_report.md) | <a href="output/UAL/zscore_UAL_trend.png"><img src="output/UAL/zscore_UAL_trend.png" alt="UAL Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: ⚖️ HOLD<br>**Short-Seller**: 📈 BUY |
| <img src="output/UBER/UBER_logo.png" alt="UBER" width="50"/> | Uber Technologies Inc | [Report](output/UBER/zscore_UBER_zscore_full_report.md) | <a href="output/UBER/zscore_UBER_trend.png"><img src="output/UBER/zscore_UBER_trend.png" alt="UBER Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: ⚖️ HOLD<br>**Value**: ⚖️ HOLD<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/UNH/UNH_logo.png" alt="UNH" width="50"/> | UnitedHealth Group Inc | [Report](output/UNH/zscore_UNH_zscore_full_report.md) | <a href="output/UNH/zscore_UNH_trend.png"><img src="output/UNH/zscore_UNH_trend.png" alt="UNH Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: ⚖️ HOLD<br>**Dividend**: 📈 BUY<br>**Value**: 📈 BUY<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/VZ/VZ_logo.png" alt="VZ" width="50"/> | Verizon Communications Inc | [Report](output/VZ/zscore_VZ_zscore_full_report.md) | <a href="output/VZ/zscore_VZ_trend.png"><img src="output/VZ/zscore_VZ_trend.png" alt="VZ Chart" width="400"/></a> | **CEO**: 🔧 RESTRUCTURE<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📉 SELL<br>**Dividend**: 📉 SELL<br>**Value**: ⚖️ HOLD<br>**Growth**: ⚖️ HOLD<br>**Aggressive**: ⚖️ HOLD<br>**Short-Seller**: 📉 SELL |
| <img src="output/WMT/WMT_logo.png" alt="WMT" width="50"/> | Walmart Inc | [Report](output/WMT/zscore_WMT_zscore_full_report.md) | <a href="output/WMT/zscore_WMT_trend.png"><img src="output/WMT/zscore_WMT_trend.png" alt="WMT Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE CAPITAL<br>**Conservative**: 📈 BUY<br>**Dividend**: 📈 BUY<br>**Value**: ⚖️ HOLD<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: ⚖️ HOLD |
| <img src="output/ZM/ZM_logo.png" alt="ZM" width="50"/> | Zoom Communications Inc | [Report](output/ZM/zscore_ZM_zscore_full_report.md) | <a href="output/ZM/zscore_ZM_trend.png"><img src="output/ZM/zscore_ZM_trend.png" alt="ZM Chart" width="400"/></a> | **CEO**: 📢 COMMUNICATE GROWTH<br>**CFO**: 💰 OPTIMIZE & INVEST<br>**Conservative**: 📈 BUY<br>**Dividend**: ⚖️ HOLD<br>**Value**: 📈 BUY<br>**Growth**: 📈 BUY<br>**Aggressive**: 📈 BUY<br>**Short-Seller**: 📉 SELL |
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
- **[LEARNINGS.md](./LEARNINGS.md)** - Technical notes and known issues
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and improvements

---

## License & Data Sources

**License:** MIT (see LICENSE file)

**Data Sources:**
- Yahoo Finance (market data)
- SEC EDGAR (regulatory filings)  
- Finnhub.io (company profiles/logos)

*All trademarks are property of their respective owners. This project is not affiliated with any data provider. Use for educational/informational purposes only.*
