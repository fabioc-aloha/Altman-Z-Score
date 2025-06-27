![AI-Powered Altman Z-Score Analysis](banner.png)

# AI-Powered Altman Z-Score Analysis

**Version: 4.3.0 (2025-06-27) 🚀 Enhanced Configuration & Modern Defaults**

Transform your investment decisions with **AI-powered financial health analysis**. Get instant, actionable insights on company bankruptcy risk, investment opportunities, and strategic recommendations with **production-ready multi-quarter analysis**.

## 🎯 **NEW v4.3.0: Enhanced Configuration & Modern Defaults**

### ⚡ **LLM Configuration Management**
- **🔧 Environment-Driven Config:** All LLM temperature and token settings now configurable via `.env`
- **🎯 Dynamic Configuration:** Temperature settings for insights (0.7), narrative (0.8), and analysis (0.5)
- **� Token Control:** Configurable max tokens for different LLM response types
- **✅ Validation Tools:** Built-in configuration validation and testing scripts

### 🚀 **Modern High-Performance Defaults**
- **⚡ Parallel Processing:** Default 8 parallel processes (up from 4) for modern systems
- **📈 Extended Analysis:** Default 12 quarters (up from 4) for better trend analysis
- **🎯 Enhanced by Default:** Advanced analysis features now enabled out-of-the-box
- **🔧 Smart Scaling:** Optimized for both older systems and high-performance setups

### 📋 **Enhanced User Experience**
- **📖 Comprehensive Help:** Detailed help system for all PowerShell and batch scripts
- **🎯 Error Handling:** Robust error handling and user guidance
- **📁 Organized Structure:** Documentation moved to logical directories (`docs/technical/`, `docs/guides/`)
- **🧹 Clean Workspace:** Test scripts organized, temporary files removed

**📖 See [docs/guides/QUICK_START_ENHANCED.md](docs/guides/QUICK_START_ENHANCED.md) for complete features guide**

---

## 🎯 **What You Get**

### 💡 **Professional Investment Intelligence v4.2.0**
- **🎯 Simplified Architecture:** Streamlined FMP-only data source with eliminated SEC EDGAR complexity
- **🚨 Multi-Quarter Risk Assessment:** Z-Score trend analysis over 4-20+ quarters with predictive insights
- **💡 Investment Recommendations:** Clear BUY/HOLD/SELL guidance with historical context and confidence scoring
- **🤖 AI-Powered Insights:** Comprehensive reports integrating multi-quarter trends and market intelligence
- **⚡ Enhanced Performance:** Reduced code complexity, faster data fetching, simplified maintenance

### 💡 **Smart Investment Decisions with Historical Context**
- **🎯 Risk-Adjusted Recommendations:** Tailored advice with multi-quarter trend analysis for all investor profiles
- **📱 Enhanced Interactive Dashboards:** Professional charts with risk zone markers and multi-quarter visualizations
- **🔍 Trend Pattern Recognition:** AI identifies seasonal patterns, trends, and turning points in financial health
- **📊 Intelligent Portfolio Optimization:** Analyze multiple stocks with account-optimized batch processing

---

## 🚀 **Get Started in 60 Seconds**

```bash
# Install and analyze your first stock
pip install -r requirements.txt
python main.py AAPL

# High-performance portfolio analysis (NEW v4.3.0 defaults)
.\run_parallel_portfolio.ps1 -PortfolioFile "portfolios/tech_portfolio.txt"
# ⚡ Now uses 8 parallel processes, 12 quarters, enhanced analysis by default

# Legacy batch processing (still available)
pwsh.exe -File run_batch_examples.ps1    # Interactive menu for sector analysis
```

### 🚀 **NEW: Enhanced Parallel Processing**
```powershell
# Modern high-performance defaults (optimized for 2025 systems)
.\run_parallel_portfolio.ps1 -PortfolioFile "portfolios/sp500.txt"

# Conservative settings for older systems
.\run_parallel_portfolio.ps1 -PortfolioFile "portfolios/large_portfolio.txt" -ParallelProcesses 4 -Quarters 8

# Maximum performance for powerful systems
.\run_parallel_portfolio.ps1 -PortfolioFile "portfolios/mega_cap.txt" -ParallelProcesses 12 -Quarters 20
```

### 💡 **What You'll Receive**
- **📋 Comprehensive Report:** 11-section AI analysis with strategic insights
- **📈 Interactive Dashboard:** Professional charts and trend analysis
- **💾 Data Export:** CSV/JSON files for your own analysis
- **💡 Investment Recommendations:** Personalized for your risk profile
- **🏢 Portfolio Analysis:** 8 sector groups with 130+ companies

---

## 📊 **Investment Portfolio - Major Companies**

**Analyze the companies that matter to your portfolio.** From blue-chip dividend stocks to high-growth tech darlings, get professional-grade analysis on the stocks you care about.

### 🏆 **Market Leaders Included**
- **💎 Mega-Cap Tech:** AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA
- **🏛️ Warren Buffett Holdings:** AAPL, KO, PG, CVX
- **📈 Growth Champions:** NVDA, TSLA, NFLX, CRM, ADBE, NOW
- **💰 Dividend Aristocrats:** KO, PG, JNJ, CAT, MMM, VZ
- **🚀 AI & Cloud Leaders:** NVDA, MSFT, GOOGL, SNOW, CRWD
- **⚡ High-Growth SaaS:** SNOW, PLTR, CRWD, NOW, DDOG

### 🎯 **Investment Profiles Supported**
Get tailored AI-powered recommendations for your investment style:

| Profile | Focus | Risk Level | Sample AI Recommendations by Z-Score Zone |
|---------|-------|------------|-------------------------------------------|
| **📊 Conservative** | Capital preservation | Low | **Safe Zone (Z>3.0)**: "HOLD - Strong fundamentals support dividend stability"<br/>**Grey Zone (1.8-3.0)**: "HOLD - Monitor closely, reduce position size"<br/>**Distress (<1.8)**: "SELL - Capital preservation priority, exit position" |
| **💰 Dividend** | Income generation | Low-Medium | **Safe Zone**: "BUY - Sustainable dividend growth supported by Z-Score strength"<br/>**Grey Zone**: "HOLD - Dividend at risk, evaluate payout ratio trends"<br/>**Distress**: "SELL - Dividend cut likely, seek income alternatives" |
| **💎 Value** | Undervalued stocks | Medium | **Safe Zone**: "BUY - Value with quality, Z-Score confirms financial strength"<br/>**Grey Zone**: "BUY - Potential turnaround, favorable risk/reward"<br/>**Distress**: "HOLD - Deep value play, but high bankruptcy risk" |
| **📈 Growth** | Capital appreciation | Medium-High | **Safe Zone**: "STRONG BUY - Growth supported by solid financials"<br/>**Grey Zone**: "HOLD - Growth story intact, but execution risk elevated"<br/>**Distress**: "SELL - Growth unsustainable with current financial health" |
| **🚀 Aggressive** | Maximum returns | High | **Safe Zone**: "BUY - Momentum play with fundamental backing"<br/>**Grey Zone**: "BUY - Volatility opportunity, potential for strong recovery"<br/>**Distress**: "SPECULATIVE BUY - High risk/high reward contrarian play" |

### 💡 **Example: How AI Adapts Recommendations by Profile**
**Sample Stock: Company with Z-Score 2.1 (Grey Zone) and declining price trend**

| Profile | AI Recommendation | Rationale |
|---------|------------------|-----------|
| **📊 Conservative** | **SELL** | "Grey Zone Z-Score indicates elevated risk - prioritize capital preservation over potential upside" |
| **💰 Dividend** | **HOLD** | "Monitor dividend coverage closely - Z-Score suggests payout may be sustainable but risky" |
| **💎 Value** | **BUY** | "Attractive entry point with potential for Z-Score recovery - favorable risk/reward for patient capital" |
| **📈 Growth** | **HOLD** | "Execution risk elevated but growth trajectory may drive Z-Score improvement" |
| **🚀 Aggressive** | **STRONG BUY** | "High volatility creates opportunity - potential for significant returns if turnaround succeeds" |

**🔍 Professional Analysis**: CEO should focus on Z-Score stabilization through working capital management, while CFO implements early warning systems for covenant monitoring.

---

## 💼 **For Investment Professionals**
**AI-Enhanced Executive Analysis:**
- **CEO Insights:** Strategic leadership effectiveness in Z-Score management and stakeholder communication
- **CFO Analysis:** Capital allocation efficiency, financial reporting quality, and liquidity optimization  
- **Risk Assessment:** Multi-factor scoring, stress testing scenarios, and early warning indicators

---

<!-- BEGIN_TICKERS_TABLE -->
| Company | Report | Investment Recommendation |
|---------|--------|--------------------------|
| <span style="display:inline-block;width:32px;height:32px;background:#2c3e50;color:white;text-align:center;line-height:32px;font-weight:bold;border-radius:4px;font-size:10px;">0059</span> **Samsung Electronics Co., Ltd.** | [Full Report](output/005930.KS/005930.KS_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.65 (Safe)</sub> |
| <img src="output/AAPL/AAPL_logo.png" alt="AAPL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Apple Inc.** | [Full Report](output/AAPL/AAPL_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 7.27 (Safe)</sub> |
| <img src="output/ABBV/ABBV_logo.png" alt="ABBV" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **AbbVie Inc.** | [Full Report](output/ABBV/ABBV_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.48 (Distress)</sub> |
| <img src="output/ABEV/ABEV_logo.png" alt="ABEV" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Ambev S.A.** | [Full Report](output/ABEV/ABEV_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.77 (Distress)</sub> |
| <img src="output/ADBE/ADBE_logo.png" alt="ADBE" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Adobe Inc.** | [Full Report](output/ADBE/ADBE_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 8.43 (Safe)</sub> |
| <img src="output/ADDYY/ADDYY_logo.png" alt="ADDYY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **adidas AG** | [Full Report](output/ADDYY/ADDYY_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.67 (Gray Zone)</sub> |
| <img src="output/ADI/ADI_logo.png" alt="ADI" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Analog Devices, Inc.** | [Full Report](output/ADI/ADI_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 6.21 (Safe)</sub> |
| <img src="output/AFL/AFL_logo.png" alt="AFL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Aflac Incorporated** | [Full Report](output/AFL/AFL_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.73 (Distress)</sub> |
| <img src="output/AIG/AIG_logo.png" alt="AIG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **American International Group, Inc.** | [Full Report](output/AIG/AIG_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.73 (Distress)</sub> |
| <img src="output/AJG/AJG_logo.png" alt="AJG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Arthur J. Gallagher & Co.** | [Full Report](output/AJG/AJG_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.43 (Distress)</sub> |
| <img src="output/ALL/ALL_logo.png" alt="ALL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Allstate Corporation** | [Full Report](output/ALL/ALL_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.45 (Distress)</sub> |
| <img src="output/AMD/AMD_logo.png" alt="AMD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Advanced Micro Devices, Inc.** | [Full Report](output/AMD/AMD_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 10.66 (Safe)</sub> |
| <img src="output/AMP/AMP_logo.png" alt="AMP" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Ameriprise Financial, Inc.** | [Full Report](output/AMP/AMP_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.46 (Distress)</sub> |
| <img src="output/AMX/AMX_logo.png" alt="AMX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **América Móvil, S.A.B. de C.V.** | [Full Report](output/AMX/AMX_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.13 (Distress)</sub> |
| <img src="output/AMZN/AMZN_logo.png" alt="AMZN" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Amazon.com, Inc.** | [Full Report](output/AMZN/AMZN_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.86 (Safe)</sub> |
| <img src="output/ANET/ANET_logo.png" alt="ANET" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Arista Networks, Inc.** | [Full Report](output/ANET/ANET_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 19.24 (Safe)</sub> |
| <img src="output/ANSS/ANSS_logo.png" alt="ANSS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **ANSYS, Inc.** | [Full Report](output/ANSS/ANSS_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 11.49 (Safe)</sub> |
| <img src="output/APH/APH_logo.png" alt="APH" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Amphenol Corporation** | [Full Report](output/APH/APH_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 6.67 (Safe)</sub> |
| <img src="output/APO/APO_logo.png" alt="APO" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Apollo Global Management, Inc.** | [Full Report](output/APO/APO_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.01 (Distress)</sub> |
| <img src="output/ASML/ASML_logo.png" alt="ASML" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **ASML Holding N.V.** | [Full Report](output/ASML/ASML_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 7.46 (Safe)</sub> |
| <img src="output/AVGO/AVGO_logo.png" alt="AVGO" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Broadcom Inc.** | [Full Report](output/AVGO/AVGO_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 8.26 (Safe)</sub> |
| <img src="output/AXP/AXP_logo.png" alt="AXP" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **American Express Company** | [Full Report](output/AXP/AXP_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.28 (Distress)</sub> |
| <img src="output/AZN/AZN_logo.png" alt="AZN" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **AstraZeneca PLC** | [Full Report](output/AZN/AZN_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.25 (Gray Zone)</sub> |
| <img src="output/AZO/AZO_logo.png" alt="AZO" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **AutoZone, Inc.** | [Full Report](output/AZO/AZO_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.87 (Gray Zone)</sub> |
| <img src="output/BA/BA_logo.png" alt="BA" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Boeing Company** | [Full Report](output/BA/BA_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.04 (Distress)</sub> |
| <img src="output/BABA/BABA_logo.png" alt="BABA" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Alibaba Group Holding Limited** | [Full Report](output/BABA/BABA_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.09 (Distress)</sub> |
| <img src="output/BAC/BAC_logo.png" alt="BAC" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Bank of America Corporation** | [Full Report](output/BAC/BAC_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.44 (Distress)</sub> |
| <img src="output/BBD/BBD_logo.png" alt="BBD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Banco Bradesco S.A.** | [Full Report](output/BBD/BBD_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.20 (Distress)</sub> |
| <img src="output/BCS/BCS_logo.png" alt="BCS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Barclays PLC** | [Full Report](output/BCS/BCS_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.06 (Distress)</sub> |
| <img src="output/BIDU/BIDU_logo.png" alt="BIDU" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Baidu, Inc.** | [Full Report](output/BIDU/BIDU_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.47 (Distress)</sub> |
| <img src="output/BILI/BILI_logo.png" alt="BILI" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Bilibili Inc.** | [Full Report](output/BILI/BILI_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.69 (Distress)</sub> |
| <img src="output/BK/BK_logo.png" alt="BK" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Bank of New York Mellon Corporation** | [Full Report](output/BK/BK_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.26 (Distress)</sub> |
| <img src="output/BKNG/BKNG_logo.png" alt="BKNG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Booking Holdings Inc.** | [Full Report](output/BKNG/BKNG_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 5.63 (Safe)</sub> |
| <img src="output/BP/BP_logo.png" alt="BP" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **BP p.l.c.** | [Full Report](output/BP/BP_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.52 (Distress)</sub> |
| <img src="output/BSX/BSX_logo.png" alt="BSX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Boston Scientific Corporation** | [Full Report](output/BSX/BSX_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 5.62 (Safe)</sub> |
| <img src="output/BX/BX_logo.png" alt="BX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Blackstone Inc.** | [Full Report](output/BX/BX_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.65 (Safe)</sub> |
| <img src="output/C/C_logo.png" alt="C" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Citigroup Inc.** | [Full Report](output/C/C_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.48 (Distress)</sub> |
| <img src="output/CAT/CAT_logo.png" alt="CAT" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Caterpillar Inc.** | [Full Report](output/CAT/CAT_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.04 (Safe)</sub> |
| <img src="output/CBRE/CBRE_logo.png" alt="CBRE" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **CBRE Group, Inc.** | [Full Report](output/CBRE/CBRE_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.77 (Distress)</sub> |
| <img src="output/CEG/CEG_logo.png" alt="CEG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Constellation Energy Corporation** | [Full Report](output/CEG/CEG_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.90 (Gray Zone)</sub> |
| <img src="output/CHKP/CHKP_logo.png" alt="CHKP" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Check Point Software Technologies Ltd.** | [Full Report](output/CHKP/CHKP_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 8.87 (Safe)</sub> |
| <img src="output/CMI/CMI_logo.png" alt="CMI" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Cummins Inc.** | [Full Report](output/CMI/CMI_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.74 (Gray Zone)</sub> |
| <img src="output/COF/COF_logo.png" alt="COF" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Capital One Financial Corporation** | [Full Report](output/COF/COF_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.35 (Distress)</sub> |
| <img src="output/COIN/COIN_logo.png" alt="COIN" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Coinbase Global, Inc.** | [Full Report](output/COIN/COIN_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 6.10 (Safe)</sub> |
| <img src="output/COR/COR_logo.png" alt="COR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Cencora, Inc.** | [Full Report](output/COR/COR_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.61 (Distress)</sub> |
| <img src="output/COST/COST_logo.png" alt="COST" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Costco Wholesale Corporation** | [Full Report](output/COST/COST_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 6.75 (Safe)</sub> |
| <img src="output/CPAY/CPAY_logo.png" alt="CPAY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Corpay, Inc.** | [Full Report](output/CPAY/CPAY_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.81 (Gray Zone)</sub> |
| <img src="output/CPRT/CPRT_logo.png" alt="CPRT" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Copart, Inc.** | [Full Report](output/CPRT/CPRT_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 34.16 (Safe)</sub> |
| <img src="output/CRM/CRM_logo.png" alt="CRM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Salesforce, Inc.** | [Full Report](output/CRM/CRM_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.53 (Safe)</sub> |
| <img src="output/CRWD/CRWD_logo.png" alt="CRWD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **CrowdStrike Holdings, Inc.** | [Full Report](output/CRWD/CRWD_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 14.72 (Safe)</sub> |
| <img src="output/DASH/DASH_logo.png" alt="DASH" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **DoorDash, Inc.** | [Full Report](output/DASH/DASH_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 11.80 (Safe)</sub> |
| <img src="output/DB/DB_logo.png" alt="DB" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Deutsche Bank AG** | [Full Report](output/DB/DB_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.30 (Distress)</sub> |
| <img src="output/DELL/DELL_logo.png" alt="DELL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Dell Technologies Inc.** | [Full Report](output/DELL/DELL_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.77 (Distress)</sub> |
| <img src="output/DIS/DIS_logo.png" alt="DIS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Walt Disney Company** | [Full Report](output/DIS/DIS_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.00 (Gray Zone)</sub> |
| <img src="output/DLR/DLR_logo.png" alt="DLR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Digital Realty Trust, Inc.** | [Full Report](output/DLR/DLR_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.68 (Distress)</sub> |
| <img src="output/E/E_logo.png" alt="E" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Eni S.p.A.** | [Full Report](output/E/E_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.98 (Distress)</sub> |
| <img src="output/EFX/EFX_logo.png" alt="EFX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Equifax Inc.** | [Full Report](output/EFX/EFX_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.72 (Safe)</sub> |
| <img src="output/ETN/ETN_logo.png" alt="ETN" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Eaton Corporation plc** | [Full Report](output/ETN/ETN_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.73 (Safe)</sub> |
| <img src="output/ETR/ETR_logo.png" alt="ETR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Entergy Corporation** | [Full Report](output/ETR/ETR_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.74 (Distress)</sub> |
| <img src="output/FAST/FAST_logo.png" alt="FAST" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Fastenal Company** | [Full Report](output/FAST/FAST_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 26.44 (Safe)</sub> |
| <img src="output/GE/GE_logo.png" alt="GE" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **General Electric Company** | [Full Report](output/GE/GE_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.62 (Gray Zone)</sub> |
| <img src="output/GEV/GEV_logo.png" alt="GEV" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **GE Vernova Inc.** | [Full Report](output/GEV/GEV_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.22 (Gray Zone)</sub> |
| <img src="output/GGAL/GGAL_logo.png" alt="GGAL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Grupo Financiero Galicia S.A.** | [Full Report](output/GGAL/GGAL_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.42 (Distress)</sub> |
| <img src="output/GILD/GILD_logo.png" alt="GILD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Gilead Sciences, Inc.** | [Full Report](output/GILD/GILD_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.77 (Gray Zone)</sub> |
| <img src="output/GM/GM_logo.png" alt="GM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **General Motors Company** | [Full Report](output/GM/GM_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.68 (Distress)</sub> |
| <img src="output/GOOG/GOOG_logo.png" alt="GOOG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Alphabet Inc.** | [Full Report](output/GOOG/GOOG_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 11.09 (Safe)</sub> |
| <img src="output/GOOGL/GOOGL_logo.png" alt="GOOGL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Alphabet Inc.** | [Full Report](output/GOOGL/GOOGL_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 11.09 (Safe)</sub> |
| <img src="output/GRMN/GRMN_logo.png" alt="GRMN" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Garmin Ltd.** | [Full Report](output/GRMN/GRMN_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 16.42 (Safe)</sub> |
| <img src="output/GS/GS_logo.png" alt="GS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Goldman Sachs Group, Inc.** | [Full Report](output/GS/GS_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.15 (Distress)</sub> |
| <img src="output/GSK/GSK_logo.png" alt="GSK" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **GSK plc** | [Full Report](output/GSK/GSK_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.38 (Distress)</sub> |
| <img src="output/GWW/GWW_logo.png" alt="GWW" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **W.W. Grainger, Inc.** | [Full Report](output/GWW/GWW_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 7.32 (Safe)</sub> |
| <img src="output/HD/HD_logo.png" alt="HD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Home Depot, Inc.** | [Full Report](output/HD/HD_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.28 (Safe)</sub> |
| <img src="output/HDB/HDB_logo.png" alt="HDB" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **HDFC Bank Limited** | [Full Report](output/HDB/HDB_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.13 (Distress)</sub> |
| <img src="output/HIG/HIG_logo.png" alt="HIG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Hartford Financial Services Group, Inc.** | [Full Report](output/HIG/HIG_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.96 (Distress)</sub> |
| <img src="output/HUBS/HUBS_logo.png" alt="HUBS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **HubSpot, Inc.** | [Full Report](output/HUBS/HUBS_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 9.35 (Safe)</sub> |
| <img src="output/IBM/IBM_logo.png" alt="IBM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **International Business Machines Corporation** | [Full Report](output/IBM/IBM_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.96 (Gray Zone)</sub> |
| <img src="output/INFY/INFY_logo.png" alt="INFY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Infosys Limited** | [Full Report](output/INFY/INFY_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 9.22 (Safe)</sub> |
| <img src="output/ING/ING_logo.png" alt="ING" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **ING Groep N.V.** | [Full Report](output/ING/ING_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.66 (Distress)</sub> |
| <img src="output/INTU/INTU_logo.png" alt="INTU" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Intuit Inc.** | [Full Report](output/INTU/INTU_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 9.29 (Safe)</sub> |
| <img src="output/IR/IR_logo.png" alt="IR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Ingersoll Rand Inc.** | [Full Report](output/IR/IR_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.14 (Safe)</sub> |
| <img src="output/ISRG/ISRG_logo.png" alt="ISRG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Intuitive Surgical, Inc.** | [Full Report](output/ISRG/ISRG_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 58.20 (Safe)</sub> |
| <img src="output/ITUB/ITUB_logo.png" alt="ITUB" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Itaú Unibanco Holding S.A.** | [Full Report](output/ITUB/ITUB_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.34 (Distress)</sub> |
| <img src="output/JD/JD_logo.png" alt="JD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **JD.com, Inc.** | [Full Report](output/JD/JD_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.70 (Distress)</sub> |
| <img src="output/JNJ/JNJ_logo.png" alt="JNJ" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Johnson & Johnson** | [Full Report](output/JNJ/JNJ_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.38 (Safe)</sub> |
| <img src="output/JPM/JPM_logo.png" alt="JPM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **JPMorgan Chase & Co.** | [Full Report](output/JPM/JPM_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.37 (Distress)</sub> |
| <img src="output/K/K_logo.png" alt="K" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Kellanova** | [Full Report](output/K/K_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.52 (Gray Zone)</sub> |
| <img src="output/LHX/LHX_logo.png" alt="LHX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **L3Harris Technologies, Inc.** | [Full Report](output/LHX/LHX_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.55 (Distress)</sub> |
| <img src="output/LI/LI_logo.png" alt="LI" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Li Auto Inc.** | [Full Report](output/LI/LI_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.79 (Distress)</sub> |
| <img src="output/LIN/LIN_logo.png" alt="LIN" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Linde plc** | [Full Report](output/LIN/LIN_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.44 (Safe)</sub> |
| <img src="output/LLY/LLY_logo.png" alt="LLY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Eli Lilly and Company** | [Full Report](output/LLY/LLY_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 6.55 (Safe)</sub> |
| <img src="output/LNG/LNG_logo.png" alt="LNG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Cheniere Energy, Inc.** | [Full Report](output/LNG/LNG_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.43 (Distress)</sub> |
| <img src="output/LVMUY/LVMUY_logo.png" alt="LVMUY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **LVMH Moët Hennessy - Louis Vuitton, Société Européenne** | [Full Report](output/LVMUY/LVMUY_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.51 (Gray Zone)</sub> |
| <img src="output/MA/MA_logo.png" alt="MA" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Mastercard Incorporated** | [Full Report](output/MA/MA_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 9.78 (Safe)</sub> |
| <img src="output/MET/MET_logo.png" alt="MET" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **MetLife, Inc.** | [Full Report](output/MET/MET_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.71 (Distress)</sub> |
| <img src="output/META/META_logo.png" alt="META" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Meta Platforms, Inc.** | [Full Report](output/META/META_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 12.61 (Safe)</sub> |
| <img src="output/MLM/MLM_logo.png" alt="MLM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Martin Marietta Materials, Inc.** | [Full Report](output/MLM/MLM_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.46 (Gray Zone)</sub> |
| <img src="output/MMM/MMM_logo.png" alt="MMM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **3M Company** | [Full Report](output/MMM/MMM_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.14 (Safe)</sub> |
| <img src="output/MNDY/MNDY_logo.png" alt="MNDY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **monday.com Ltd.** | [Full Report](output/MNDY/MNDY_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 14.66 (Safe)</sub> |
| <img src="output/MPC/MPC_logo.png" alt="MPC" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Marathon Petroleum Corporation** | [Full Report](output/MPC/MPC_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.64 (Distress)</sub> |
| <img src="output/MPWR/MPWR_logo.png" alt="MPWR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Monolithic Power Systems, Inc.** | [Full Report](output/MPWR/MPWR_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 40.90 (Safe)</sub> |
| <img src="output/MS/MS_logo.png" alt="MS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Morgan Stanley** | [Full Report](output/MS/MS_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.03 (Distress)</sub> |
| <img src="output/MSFT/MSFT_logo.png" alt="MSFT" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Microsoft Corporation** | [Full Report](output/MSFT/MSFT_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 10.16 (Safe)</sub> |
| <img src="output/MU/MU_logo.png" alt="MU" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Micron Technology, Inc.** | [Full Report](output/MU/MU_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.36 (Safe)</sub> |
| <img src="output/NFLX/NFLX_logo.png" alt="NFLX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Netflix, Inc.** | [Full Report](output/NFLX/NFLX_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 13.27 (Safe)</sub> |
| <img src="output/NICE/NICE_logo.png" alt="NICE" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **NICE Ltd.** | [Full Report](output/NICE/NICE_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.07 (Safe)</sub> |
| <img src="output/NIO/NIO_logo.png" alt="NIO" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **NIO Inc.** | [Full Report](output/NIO/NIO_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.16 (Distress)</sub> |
| <img src="output/NKE/NKE_logo.png" alt="NKE" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **NIKE, Inc.** | [Full Report](output/NKE/NKE_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.48 (Safe)</sub> |
| <img src="output/NOW/NOW_logo.png" alt="NOW" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **ServiceNow, Inc.** | [Full Report](output/NOW/NOW_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 12.14 (Safe)</sub> |
| <img src="output/NVDA/NVDA_logo.png" alt="NVDA" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **NVIDIA Corporation** | [Full Report](output/NVDA/NVDA_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 57.11 (Safe)</sub> |
| <img src="output/NVO/NVO_logo.png" alt="NVO" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Novo Nordisk A/S** | [Full Report](output/NVO/NVO_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.18 (Distress)</sub> |
| <img src="output/OKTA/OKTA_logo.png" alt="OKTA" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Okta, Inc.** | [Full Report](output/OKTA/OKTA_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.50 (Safe)</sub> |
| <img src="output/ORCL/ORCL_logo.png" alt="ORCL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Oracle Corporation** | [Full Report](output/ORCL/ORCL_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.57 (Gray Zone)</sub> |
| <img src="output/ORLY/ORLY_logo.png" alt="ORLY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **O'Reilly Automotive, Inc.** | [Full Report](output/ORLY/ORLY_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.70 (Gray Zone)</sub> |
| <img src="output/PANW/PANW_logo.png" alt="PANW" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Palo Alto Networks, Inc.** | [Full Report](output/PANW/PANW_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 5.72 (Safe)</sub> |
| <img src="output/PBR/PBR_logo.png" alt="PBR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Petróleo Brasileiro S.A. - Petrobras** | [Full Report](output/PBR/PBR_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.57 (Distress)</sub> |
| <img src="output/PCAR/PCAR_logo.png" alt="PCAR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **PACCAR Inc** | [Full Report](output/PCAR/PCAR_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.65 (Gray Zone)</sub> |
| <img src="output/PDD/PDD_logo.png" alt="PDD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **PDD Holdings Inc.** | [Full Report](output/PDD/PDD_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.83 (Gray Zone)</sub> |
| <img src="output/PFE/PFE_logo.png" alt="PFE" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Pfizer Inc.** | [Full Report](output/PFE/PFE_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.70 (Distress)</sub> |
| <img src="output/PGR/PGR_logo.png" alt="PGR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Progressive Corporation** | [Full Report](output/PGR/PGR_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.08 (Gray Zone)</sub> |
| <img src="output/PH/PH_logo.png" alt="PH" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Parker-Hannifin Corporation** | [Full Report](output/PH/PH_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.76 (Safe)</sub> |
| <img src="output/PLTR/PLTR_logo.png" alt="PLTR" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Palantir Technologies Inc.** | [Full Report](output/PLTR/PLTR_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 167.83 (Safe)</sub> |
| <img src="output/PM/PM_logo.png" alt="PM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Philip Morris International Inc.** | [Full Report](output/PM/PM_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.49 (Gray Zone)</sub> |
| <img src="output/PNC/PNC_logo.png" alt="PNC" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The PNC Financial Services Group, Inc.** | [Full Report](output/PNC/PNC_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.53 (Distress)</sub> |
| <img src="output/PODD/PODD_logo.png" alt="PODD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Insulet Corporation** | [Full Report](output/PODD/PODD_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 6.84 (Safe)</sub> |
| <img src="output/RCL/RCL_logo.png" alt="RCL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Royal Caribbean Cruises Ltd.** | [Full Report](output/RCL/RCL_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.68 (Distress)</sub> |
| <img src="output/RHHBY/RHHBY_logo.png" alt="RHHBY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Roche Holding AG** | [Full Report](output/RHHBY/RHHBY_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.80 (Safe)</sub> |
| <img src="output/RIO/RIO_logo.png" alt="RIO" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Rio Tinto Group** | [Full Report](output/RIO/RIO_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.44 (Gray Zone)</sub> |
| <img src="output/RTX/RTX_logo.png" alt="RTX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **RTX Corporation** | [Full Report](output/RTX/RTX_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.75 (Distress)</sub> |
| <img src="output/SAP/SAP_logo.png" alt="SAP" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Sap Se** | [Full Report](output/SAP/SAP_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 8.16 (Safe)</sub> |
| <img src="output/SBUX/SBUX_logo.png" alt="SBUX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Starbucks Corporation** | [Full Report](output/SBUX/SBUX_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.47 (Distress)</sub> |
| <img src="output/SCHW/SCHW_logo.png" alt="SCHW" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The Charles Schwab Corporation** | [Full Report](output/SCHW/SCHW_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.09 (Distress)</sub> |
| <img src="output/SHEL/SHEL_logo.png" alt="SHEL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Shell plc** | [Full Report](output/SHEL/SHEL_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.52 (Distress)</sub> |
| <img src="output/SIEGY/SIEGY_logo.png" alt="SIEGY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Siemens AG** | [Full Report](output/SIEGY/SIEGY_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.81 (Gray Zone)</sub> |
| <img src="output/SNY/SNY_logo.png" alt="SNY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Sanofi** | [Full Report](output/SNY/SNY_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.47 (Distress)</sub> |
| <img src="output/SONY/SONY_logo.png" alt="SONY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Sony Group Corporation** | [Full Report](output/SONY/SONY_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.25 (Distress)</sub> |
| <img src="output/SPGI/SPGI_logo.png" alt="SPGI" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **S&P Global Inc.** | [Full Report](output/SPGI/SPGI_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.41 (Safe)</sub> |
| <img src="output/SQM/SQM_logo.png" alt="SQM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Sociedad Química y Minera de Chile S.A.** | [Full Report](output/SQM/SQM_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.97 (Gray Zone)</sub> |
| <img src="output/SSNC/SSNC_logo.png" alt="SSNC" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **SS&C Technologies Holdings, Inc.** | [Full Report](output/SSNC/SSNC_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.06 (Distress)</sub> |
| <img src="output/STT/STT_logo.png" alt="STT" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **State Street Corporation** | [Full Report](output/STT/STT_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.09 (Distress)</sub> |
| <img src="output/SYK/SYK_logo.png" alt="SYK" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Stryker Corporation** | [Full Report](output/SYK/SYK_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.46 (Safe)</sub> |
| <img src="output/T/T_logo.png" alt="T" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **AT&T Inc.** | [Full Report](output/T/T_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.54 (Distress)</sub> |
| <img src="output/TDG/TDG_logo.png" alt="TDG" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **TransDigm Group Incorporated** | [Full Report](output/TDG/TDG_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.88 (Gray Zone)</sub> |
| <img src="output/TEVA/TEVA_logo.png" alt="TEVA" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Teva Pharmaceutical Industries Limited** | [Full Report](output/TEVA/TEVA_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.02 (Distress)</sub> |
| <img src="output/TJX/TJX_logo.png" alt="TJX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **The TJX Companies, Inc.** | [Full Report](output/TJX/TJX_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.12 (Safe)</sub> |
| <img src="output/TM/TM_logo.png" alt="TM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Toyota Motor Corporation** | [Full Report](output/TM/TM_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.81 (Distress)</sub> |
| <img src="output/TMO/TMO_logo.png" alt="TMO" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Thermo Fisher Scientific Inc.** | [Full Report](output/TMO/TMO_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.18 (Gray Zone)</sub> |
| <img src="output/TMUS/TMUS_logo.png" alt="TMUS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **T-Mobile US, Inc.** | [Full Report](output/TMUS/TMUS_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.33 (Distress)</sub> |
| <img src="output/TSLA/TSLA_logo.png" alt="TSLA" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Tesla, Inc.** | [Full Report](output/TSLA/TSLA_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 13.52 (Safe)</sub> |
| <img src="output/TSM/TSM_logo.png" alt="TSM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Taiwan Semiconductor Manufacturing Company Limited** | [Full Report](output/TSM/TSM_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.65 (Distress)</sub> |
| <img src="output/UAL/UAL_logo.png" alt="UAL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **United Airlines Holdings, Inc.** | [Full Report](output/UAL/UAL_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.35 (Distress)</sub> |
| <img src="output/UBER/UBER_logo.png" alt="UBER" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Uber Technologies, Inc.** | [Full Report](output/UBER/UBER_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.70 (Safe)</sub> |
| <img src="output/UL/UL_logo.png" alt="UL" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Unilever PLC** | [Full Report](output/UL/UL_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.87 (Gray Zone)</sub> |
| <img src="output/UNH/UNH_logo.png" alt="UNH" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **UnitedHealth Group Incorporated** | [Full Report](output/UNH/UNH_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.64 (Distress)</sub> |
| <img src="output/UPS/UPS_logo.png" alt="UPS" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **United Parcel Service, Inc.** | [Full Report](output/UPS/UPS_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 1.80 (Distress)</sub> |
| <img src="output/URI/URI_logo.png" alt="URI" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **United Rentals, Inc.** | [Full Report](output/URI/URI_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.42 (Gray Zone)</sub> |
| <img src="output/V/V_logo.png" alt="V" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Visa Inc.** | [Full Report](output/V/V_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 7.98 (Safe)</sub> |
| <img src="output/VALE/VALE_logo.png" alt="VALE" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Vale S.A.** | [Full Report](output/VALE/VALE_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.73 (Distress)</sub> |
| <img src="output/VOD/VOD_logo.png" alt="VOD" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Vodafone Group Public Limited Company** | [Full Report](output/VOD/VOD_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -1.00 (Distress)</sub> |
| <img src="output/VRTX/VRTX_logo.png" alt="VRTX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Vertex Pharmaceuticals Incorporated** | [Full Report](output/VRTX/VRTX_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 11.86 (Safe)</sub> |
| <img src="output/WDAY/WDAY_logo.png" alt="WDAY" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Workday, Inc.** | [Full Report](output/WDAY/WDAY_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 4.96 (Safe)</sub> |
| <img src="output/WFC/WFC_logo.png" alt="WFC" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Wells Fargo & Company** | [Full Report](output/WFC/WFC_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.41 (Distress)</sub> |
| <img src="output/WIT/WIT_logo.png" alt="WIT" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Wipro Limited** | [Full Report](output/WIT/WIT_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 1.56 (Distress)</sub> |
| <img src="output/WIX/WIX_logo.png" alt="WIX" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Wix.com Ltd.** | [Full Report](output/WIX/WIX_comprehensive_report.html) | ⚖️ HOLD<br/><sub>Z-Score: 2.12 (Gray Zone)</sub> |
| <img src="output/WMT/WMT_logo.png" alt="WMT" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **Walmart Inc.** | [Full Report](output/WMT/WMT_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 3.78 (Safe)</sub> |
| <img src="output/YPF/YPF_logo.png" alt="YPF" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **YPF Sociedad Anónima** | [Full Report](output/YPF/YPF_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.11 (Distress)</sub> |
| <img src="output/ZIM/ZIM_logo.png" alt="ZIM" width="32" height="32" style="border-radius:4px; vertical-align: middle;"/> **ZIM Integrated Shipping Services Ltd.** | [Full Report](output/ZIM/ZIM_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.75 (Distress)</sub> |
<!-- END_TICKERS_TABLE -->

---

## 📊 **AI-Powered Z-Score vs Price Trend Analysis**
Our LLM identifies critical market inefficiencies by analyzing Z-Score health vs stock price movements:

| Trend Pattern | AI Assessment | Investment Signal | Example Insight |
|---------------|---------------|-------------------|-----------------|
| **🔻 Z-Score Declining, 📈 Price Rising** | **URGENT WARNING** | Potential short opportunity | "Hidden fundamental deterioration - market hasn't recognized financial stress" |
| **🔺 Z-Score Improving, 📈 Price Rising** | **STRONG CONFIRMATION** | Fundamental support for rally | "Price appreciation backed by improving financial health - sustainable growth" |
| **🔺 Z-Score Improving, 📉 Price Lagging** | **VALUE OPPORTUNITY** | Undervalued recovery play | "Market hasn't recognized financial turnaround - communication opportunity" |
| **🔻 Z-Score Declining, 📉 Price Declining** | **CRISIS MODE** | Avoid/Exit positions | "Both fundamentals and market sentiment deteriorating - high bankruptcy risk" |

**🎯 Key Advantage**: While traditional analysis focuses on either fundamentals OR technicals, our AI combines both to identify market timing opportunities and hidden risks that others miss.

---

## 🔄 **Update Your Analysis**

Keep your portfolio analysis current with a single command:

```bash
python generate_readme_table.py
```

This updates the comprehensive investment table with the latest market data and AI insights for all 135+ companies.

---

## ⚙️ **Quick Setup**

### **Step 1: Install**
```bash
pip install -r requirements.txt
```

### **Step 2: Configure APIs** 
Create a `.env` file with your API keys:
```bash
# Required for financial data
FINANCIAL_MODELING_PREP_API_KEY="your-fmp-key"

# Required for AI insights  
AZURE_OPENAI_ENDPOINT="your-azure-endpoint"
AZURE_OPENAI_API_KEY="your-azure-key"
AZURE_OPENAI_DEPLOYMENT="your-deployment"

# Required for SEC compliance
SEC_EDGAR_USER_AGENT="YourCompany/1.0 your.email@domain.com"

# Optional: Logging configuration
LOG_LEVEL="INFO"                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR="logs"                      # Directory for log files
LOG_FILE_LEVEL="DEBUG"              # File logging level
LOG_STRUCTURED="false"              # Enable structured JSON logging
```

### **Step 3: Start Analyzing**
```bash
# Single company
python main.py AAPL

# Your favorite stocks with custom logging
python main.py AAPL MSFT GOOGL TSLA NVDA --log-level DEBUG

# Advanced logging options
python main.py AAPL --log-level INFO --log-file-level DEBUG --log-dir "custom_logs" --log-structured
```

### **📊 Logging Options**
Control application logging via CLI arguments or `.env` variables:

| CLI Argument | Environment Variable | Default | Description |
|-------------|---------------------|---------|-------------|
| `--log-level` | `LOG_LEVEL` | `INFO` | Console log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--log-file-level` | `LOG_FILE_LEVEL` | `DEBUG` | File log level for detailed debugging |
| `--log-dir` | `LOG_DIR` | `logs` | Directory for log files |
| `--log-structured` | `LOG_STRUCTURED` | `false` | Enable structured JSON logging |

```bash
# Examples:
python main.py AAPL --log-level DEBUG                    # Verbose console output
python main.py AAPL --log-dir "analysis_logs"           # Custom log directory
python main.py AAPL --log-structured                    # JSON formatted logs
```

### **📊 API Costs**
- **Free Tier Available:** 250 API calls/day (analyze ~50 companies)
- **Paid Plans:** Unlimited analysis for serious investors
- **Smart Caching:** Reduces API usage by 95%

---

## 🎯 **Perfect For**

### 👨‍💼 **Individual Investors**
- Research stocks before buying
- Monitor portfolio health
- Get AI-powered insights
- Identify bankruptcy risks early

### 🏢 **Investment Professionals**
- Due diligence automation
- Client reporting
- Risk assessment
- Portfolio optimization

### 📚 **Students & Educators**
- Learn financial analysis
- Understand Z-Score methodology
- Practice with real data
- Academic research projects

---

## � **Support & Community**

### 🚀 **Getting Started**
- Check the **[Quick Start Guide](docs/guides/)** for detailed setup
- Browse **[Sample Reports](output/)** to see what you'll get
- Review **[API Documentation](APIS.md)** for configuration help

### 📈 **Advanced Features**
- **[Technical Documentation](docs/)** for developers
- **[Customization Guide](docs/guides/)** for power users
- **[Integration Examples](scripts/exploration/)** for workflows

---

## 📄 **Legal & Data Sources**

**License:** Proprietary License - All Rights Reserved by Fabio Correa

**Data Sources:**
- 📊 **Financial Modeling Prep** - Professional financial data
- 📈 **Yahoo Finance** - Real-time market pricing  
- 🤖 **Azure OpenAI** - AI-powered analysis and insights

**Disclaimer:** This tool is for educational and informational purposes. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

---

## 📋 **How to View Reports & Dashboards**

**📌 Important:** GitHub displays HTML files as raw code, not rendered pages. To view the actual interactive reports and dashboards:

### 🖥️ **Option 1: Clone Repository (Recommended for Full Experience)**
```bash
# Clone the repository
git clone https://github.com/your-username/Altman-Z-Score-1.git
cd Altman-Z-Score-1

# Open any report in your browser
start output/AAPL/AAPL_comprehensive_report.html        # Windows
open output/AAPL/AAPL_comprehensive_report.html         # macOS
xdg-open output/AAPL/AAPL_comprehensive_report.html     # Linux
```

### 📁 **Option 2: Download Individual Reports**
1. Click "📄 Download Report" or "📊 Download Dashboard" links in the table below
2. On the GitHub file page, click the "Download" button (or Raw → Save As)
3. Open the downloaded HTML file in your browser

### 🔄 **Option 3: Generate Fresh Analysis**
```bash
# Run analysis for any company
python main.py AAPL

# Run comprehensive portfolio analysis
pwsh.exe -File run_batch_examples.ps1
```

**💡 Tip:** The reports contain interactive charts, AI insights, and comprehensive financial analysis that are best viewed in a browser, not on GitHub.
