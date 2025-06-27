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
|---------|--------|----------------------------|
| **005930.KS**<br/>Samsung Electronics Co., Ltd. | [View Report](output/005930.KS/005930.KS_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.65 (Safe)* |
| **AAPL**<br/>Apple Inc. | [View Report](output/AAPL/AAPL_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 7.27 (Safe)* |
| **ABBV**<br/>ABBV | [View Report](output/ABBV/ABBV_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.48 (Distress)* |
| **ABEV**<br/>ABEV | [View Report](output/ABEV/ABEV_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.77 (Distress)* |
| **ADBE**<br/>ADBE | [View Report](output/ADBE/ADBE_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 8.43 (Safe)* |
| **ADDYY**<br/>ADDYY | [View Report](output/ADDYY/ADDYY_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.67 (Gray Zone)* |
| **ADI**<br/>ADI | [View Report](output/ADI/ADI_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 6.21 (Safe)* |
| **AFL**<br/>AFL | [View Report](output/AFL/AFL_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.73 (Distress)* |
| **AIG**<br/>AIG | [View Report](output/AIG/AIG_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.73 (Distress)* |
| **AJG**<br/>AJG | [View Report](output/AJG/AJG_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.43 (Distress)* |
| **ALL**<br/>ALL | [View Report](output/ALL/ALL_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.45 (Distress)* |
| **AMD**<br/>AMD | [View Report](output/AMD/AMD_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 10.66 (Safe)* |
| **AMP**<br/>AMP | [View Report](output/AMP/AMP_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.46 (Distress)* |
| **AMX**<br/>AMX | [View Report](output/AMX/AMX_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.13 (Distress)* |
| **AMZN**<br/>Amazon.com Inc. | [View Report](output/AMZN/AMZN_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.86 (Safe)* |
| **ANET**<br/>ANET | [View Report](output/ANET/ANET_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 19.24 (Safe)* |
| **ANSS**<br/>ANSS | [View Report](output/ANSS/ANSS_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 11.49 (Safe)* |
| **APH**<br/>APH | [View Report](output/APH/APH_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 6.67 (Safe)* |
| **APO**<br/>APO | [View Report](output/APO/APO_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.01 (Distress)* |
| **ASML**<br/>ASML Holding N.V. | [View Report](output/ASML/ASML_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 7.46 (Safe)* |
| **AVGO**<br/>Broadcom Inc. | [View Report](output/AVGO/AVGO_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 8.26 (Safe)* |
| **AXP**<br/>AXP | [View Report](output/AXP/AXP_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.28 (Distress)* |
| **AZN**<br/>AZN | [View Report](output/AZN/AZN_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.25 (Gray Zone)* |
| **AZO**<br/>AZO | [View Report](output/AZO/AZO_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.87 (Gray Zone)* |
| **BA**<br/>BA | [View Report](output/BA/BA_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.04 (Distress)* |
| **BABA**<br/>Alibaba Group Holding Ltd. | [View Report](output/BABA/BABA_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.09 (Distress)* |
| **BAC**<br/>BAC | [View Report](output/BAC/BAC_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.44 (Distress)* |
| **BBD**<br/>BBD | [View Report](output/BBD/BBD_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.2 (Distress)* |
| **BCS**<br/>BCS | [View Report](output/BCS/BCS_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.06 (Distress)* |
| **BIDU**<br/>BIDU | [View Report](output/BIDU/BIDU_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.47 (Distress)* |
| **BILI**<br/>BILI | [View Report](output/BILI/BILI_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.69 (Distress)* |
| **BK**<br/>Bank of New York Mellon Corp. | [View Report](output/BK/BK_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.26 (Distress)* |
| **BKNG**<br/>BKNG | [View Report](output/BKNG/BKNG_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 5.63 (Safe)* |
| **BP**<br/>BP | [View Report](output/BP/BP_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.52 (Distress)* |
| **BSX**<br/>BSX | [View Report](output/BSX/BSX_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 5.62 (Safe)* |
| **BX**<br/>BX | [View Report](output/BX/BX_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.65 (Safe)* |
| **C**<br/>C | [View Report](output/C/C_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.48 (Distress)* |
| **CAT**<br/>CAT | [View Report](output/CAT/CAT_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.04 (Safe)* |
| **CBRE**<br/>CBRE | [View Report](output/CBRE/CBRE_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.77 (Distress)* |
| **CEG**<br/>CEG | [View Report](output/CEG/CEG_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.9 (Gray Zone)* |
| **CHKP**<br/>CHKP | [View Report](output/CHKP/CHKP_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 8.87 (Safe)* |
| **CMI**<br/>CMI | [View Report](output/CMI/CMI_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.74 (Gray Zone)* |
| **COF**<br/>COF | [View Report](output/COF/COF_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.35 (Distress)* |
| **COIN**<br/>COIN | [View Report](output/COIN/COIN_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 6.1 (Safe)* |
| **COR**<br/>COR | [View Report](output/COR/COR_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.61 (Distress)* |
| **COST**<br/>COST | [View Report](output/COST/COST_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 6.75 (Safe)* |
| **CPAY**<br/>CPAY | [View Report](output/CPAY/CPAY_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.81 (Gray Zone)* |
| **CPRT**<br/>CPRT | [View Report](output/CPRT/CPRT_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 34.16 (Safe)* |
| **CRM**<br/>CRM | [View Report](output/CRM/CRM_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.53 (Safe)* |
| **CRWD**<br/>CRWD | [View Report](output/CRWD/CRWD_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 14.72 (Safe)* |
| **DASH**<br/>DASH | [View Report](output/DASH/DASH_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 11.8 (Safe)* |
| **DB**<br/>DB | [View Report](output/DB/DB_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.3 (Distress)* |
| **DELL**<br/>DELL | [View Report](output/DELL/DELL_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.77 (Distress)* |
| **DIS**<br/>DIS | [View Report](output/DIS/DIS_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.0 (Gray Zone)* |
| **DLR**<br/>DLR | [View Report](output/DLR/DLR_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.68 (Distress)* |
| **E**<br/>E | [View Report](output/E/E_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.98 (Distress)* |
| **EFX**<br/>EFX | [View Report](output/EFX/EFX_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.72 (Safe)* |
| **ETN**<br/>ETN | [View Report](output/ETN/ETN_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.73 (Safe)* |
| **ETR**<br/>ETR | [View Report](output/ETR/ETR_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.74 (Distress)* |
| **FAST**<br/>FAST | [View Report](output/FAST/FAST_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 26.44 (Safe)* |
| **GE**<br/>GE | [View Report](output/GE/GE_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.62 (Gray Zone)* |
| **GEV**<br/>GEV | [View Report](output/GEV/GEV_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.22 (Gray Zone)* |
| **GGAL**<br/>GGAL | [View Report](output/GGAL/GGAL_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.42 (Distress)* |
| **GILD**<br/>GILD | [View Report](output/GILD/GILD_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.77 (Gray Zone)* |
| **GM**<br/>GM | [View Report](output/GM/GM_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.68 (Distress)* |
| **GOOG**<br/>Alphabet Inc. | [View Report](output/GOOG/GOOG_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 11.09 (Safe)* |
| **GOOGL**<br/>Alphabet Inc. | [View Report](output/GOOGL/GOOGL_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 11.09 (Safe)* |
| **GRMN**<br/>GRMN | [View Report](output/GRMN/GRMN_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 16.42 (Safe)* |
| **GS**<br/>Goldman Sachs Group Inc. | [View Report](output/GS/GS_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.15 (Distress)* |
| **GSK**<br/>GSK | [View Report](output/GSK/GSK_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.38 (Distress)* |
| **GWW**<br/>GWW | [View Report](output/GWW/GWW_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 7.32 (Safe)* |
| **HD**<br/>HD | [View Report](output/HD/HD_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.28 (Safe)* |
| **HDB**<br/>HDB | [View Report](output/HDB/HDB_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.13 (Distress)* |
| **HIG**<br/>HIG | [View Report](output/HIG/HIG_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.96 (Distress)* |
| **HUBS**<br/>HUBS | [View Report](output/HUBS/HUBS_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 9.35 (Safe)* |
| **IBM**<br/>IBM | [View Report](output/IBM/IBM_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.96 (Gray Zone)* |
| **INFY**<br/>INFY | [View Report](output/INFY/INFY_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 9.22 (Safe)* |
| **ING**<br/>ING | [View Report](output/ING/ING_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.66 (Distress)* |
| **INTU**<br/>INTU | [View Report](output/INTU/INTU_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 9.29 (Safe)* |
| **IR**<br/>IR | [View Report](output/IR/IR_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.14 (Safe)* |
| **ISRG**<br/>ISRG | [View Report](output/ISRG/ISRG_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 58.2 (Safe)* |
| **ITUB**<br/>ITUB | [View Report](output/ITUB/ITUB_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.34 (Distress)* |
| **JD**<br/>JD | [View Report](output/JD/JD_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.7 (Distress)* |
| **JNJ**<br/>JNJ | [View Report](output/JNJ/JNJ_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.38 (Safe)* |
| **JPM**<br/>JPMorgan Chase & Co. | [View Report](output/JPM/JPM_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.37 (Distress)* |
| **K**<br/>K | [View Report](output/K/K_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.52 (Gray Zone)* |
| **LHX**<br/>LHX | [View Report](output/LHX/LHX_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.55 (Distress)* |
| **LI**<br/>LI | [View Report](output/LI/LI_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.79 (Distress)* |
| **LIN**<br/>Linde plc | [View Report](output/LIN/LIN_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.44 (Safe)* |
| **LLY**<br/>LLY | [View Report](output/LLY/LLY_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 6.55 (Safe)* |
| **LNG**<br/>LNG | [View Report](output/LNG/LNG_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.43 (Distress)* |
| **LVMUY**<br/>LVMUY | [View Report](output/LVMUY/LVMUY_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.51 (Gray Zone)* |
| **MA**<br/>MA | [View Report](output/MA/MA_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 9.78 (Safe)* |
| **MET**<br/>MET | [View Report](output/MET/MET_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.71 (Distress)* |
| **META**<br/>Meta Platforms Inc. | [View Report](output/META/META_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 12.61 (Safe)* |
| **MLM**<br/>MLM | [View Report](output/MLM/MLM_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.46 (Gray Zone)* |
| **MMM**<br/>MMM | [View Report](output/MMM/MMM_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.14 (Safe)* |
| **MNDY**<br/>MNDY | [View Report](output/MNDY/MNDY_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 14.66 (Safe)* |
| **MPC**<br/>MPC | [View Report](output/MPC/MPC_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.64 (Distress)* |
| **MPWR**<br/>MPWR | [View Report](output/MPWR/MPWR_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 40.9 (Safe)* |
| **MS**<br/>MS | [View Report](output/MS/MS_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.03 (Distress)* |
| **MSFT**<br/>Microsoft Corporation | [View Report](output/MSFT/MSFT_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 10.16 (Safe)* |
| **MU**<br/>MU | [View Report](output/MU/MU_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.36 (Safe)* |
| **NFLX**<br/>Netflix Inc. | [View Report](output/NFLX/NFLX_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 13.27 (Safe)* |
| **NICE**<br/>NICE | [View Report](output/NICE/NICE_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.07 (Safe)* |
| **NIO**<br/>NIO | [View Report](output/NIO/NIO_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.16 (Distress)* |
| **NKE**<br/>NKE | [View Report](output/NKE/NKE_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.48 (Safe)* |
| **NOW**<br/>NOW | [View Report](output/NOW/NOW_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 12.14 (Safe)* |
| **NVDA**<br/>NVIDIA Corporation | [View Report](output/NVDA/NVDA_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 57.11 (Safe)* |
| **NVO**<br/>NVO | [View Report](output/NVO/NVO_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.18 (Distress)* |
| **OKTA**<br/>OKTA | [View Report](output/OKTA/OKTA_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.5 (Safe)* |
| **ORCL**<br/>ORCL | [View Report](output/ORCL/ORCL_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.57 (Gray Zone)* |
| **ORLY**<br/>ORLY | [View Report](output/ORLY/ORLY_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.7 (Gray Zone)* |
| **PANW**<br/>PANW | [View Report](output/PANW/PANW_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 5.72 (Safe)* |
| **PBR**<br/>PBR | [View Report](output/PBR/PBR_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.57 (Distress)* |
| **PCAR**<br/>PCAR | [View Report](output/PCAR/PCAR_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.65 (Gray Zone)* |
| **PDD**<br/>PDD | [View Report](output/PDD/PDD_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.83 (Gray Zone)* |
| **PFE**<br/>PFE | [View Report](output/PFE/PFE_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.7 (Distress)* |
| **PGR**<br/>PGR | [View Report](output/PGR/PGR_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.08 (Gray Zone)* |
| **PH**<br/>PH | [View Report](output/PH/PH_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.76 (Safe)* |
| **PLTR**<br/>PLTR | [View Report](output/PLTR/PLTR_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 167.83 (Safe)* |
| **PM**<br/>PM | [View Report](output/PM/PM_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.49 (Gray Zone)* |
| **PNC**<br/>PNC | [View Report](output/PNC/PNC_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.53 (Distress)* |
| **PODD**<br/>PODD | [View Report](output/PODD/PODD_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 6.84 (Safe)* |
| **RCL**<br/>RCL | [View Report](output/RCL/RCL_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.68 (Distress)* |
| **RHHBY**<br/>RHHBY | [View Report](output/RHHBY/RHHBY_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.8 (Safe)* |
| **RIO**<br/>RIO | [View Report](output/RIO/RIO_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.44 (Gray Zone)* |
| **RTX**<br/>RTX | [View Report](output/RTX/RTX_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.75 (Distress)* |
| **SAP**<br/>SAP | [View Report](output/SAP/SAP_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 8.16 (Safe)* |
| **SBUX**<br/>SBUX | [View Report](output/SBUX/SBUX_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.47 (Distress)* |
| **SCHW**<br/>SCHW | [View Report](output/SCHW/SCHW_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.09 (Distress)* |
| **SHEL**<br/>SHEL | [View Report](output/SHEL/SHEL_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.52 (Distress)* |
| **SIEGY**<br/>SIEGY | [View Report](output/SIEGY/SIEGY_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.81 (Gray Zone)* |
| **SNY**<br/>SNY | [View Report](output/SNY/SNY_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.47 (Distress)* |
| **SONY**<br/>SONY | [View Report](output/SONY/SONY_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.25 (Distress)* |
| **SPGI**<br/>SPGI | [View Report](output/SPGI/SPGI_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.41 (Safe)* |
| **SQM**<br/>SQM | [View Report](output/SQM/SQM_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.97 (Gray Zone)* |
| **SSNC**<br/>SSNC | [View Report](output/SSNC/SSNC_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.06 (Distress)* |
| **STT**<br/>STT | [View Report](output/STT/STT_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.09 (Distress)* |
| **SYK**<br/>SYK | [View Report](output/SYK/SYK_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.46 (Safe)* |
| **T**<br/>T | [View Report](output/T/T_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.54 (Distress)* |
| **TDG**<br/>TDG | [View Report](output/TDG/TDG_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.88 (Gray Zone)* |
| **TEVA**<br/>TEVA | [View Report](output/TEVA/TEVA_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.02 (Distress)* |
| **TJX**<br/>TJX | [View Report](output/TJX/TJX_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.12 (Safe)* |
| **TM**<br/>Toyota Motor Corporation | [View Report](output/TM/TM_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.81 (Distress)* |
| **TMO**<br/>TMO | [View Report](output/TMO/TMO_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.18 (Gray Zone)* |
| **TMUS**<br/>TMUS | [View Report](output/TMUS/TMUS_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.33 (Distress)* |
| **TSLA**<br/>Tesla Inc. | [View Report](output/TSLA/TSLA_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 13.52 (Safe)* |
| **TSM**<br/>Taiwan Semiconductor Manufacturing Company | [View Report](output/TSM/TSM_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.65 (Distress)* |
| **UAL**<br/>UAL | [View Report](output/UAL/UAL_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.35 (Distress)* |
| **UBER**<br/>UBER | [View Report](output/UBER/UBER_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.7 (Safe)* |
| **UL**<br/>UL | [View Report](output/UL/UL_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.87 (Gray Zone)* |
| **UNH**<br/>UnitedHealth Group Inc. | [View Report](output/UNH/UNH_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.64 (Distress)* |
| **UPS**<br/>UPS | [View Report](output/UPS/UPS_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 1.8 (Distress)* |
| **URI**<br/>URI | [View Report](output/URI/URI_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.42 (Gray Zone)* |
| **V**<br/>V | [View Report](output/V/V_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 7.98 (Safe)* |
| **VALE**<br/>VALE | [View Report](output/VALE/VALE_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.73 (Distress)* |
| **VOD**<br/>VOD | [View Report](output/VOD/VOD_comprehensive_report.html) | **SELL**<br/>*Z-Score: -1.0 (Distress)* |
| **VRTX**<br/>VRTX | [View Report](output/VRTX/VRTX_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 11.86 (Safe)* |
| **WDAY**<br/>WDAY | [View Report](output/WDAY/WDAY_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 4.96 (Safe)* |
| **WFC**<br/>WFC | [View Report](output/WFC/WFC_comprehensive_report.html) | **SELL**<br/>*Z-Score: -0.41 (Distress)* |
| **WIT**<br/>WIT | [View Report](output/WIT/WIT_comprehensive_report.html) | **SELL**<br/>*Z-Score: 1.56 (Distress)* |
| **WIX**<br/>WIX | [View Report](output/WIX/WIX_comprehensive_report.html) | **HOLD**<br/>*Z-Score: 2.12 (Gray Zone)* |
| **WMT**<br/>WMT | [View Report](output/WMT/WMT_comprehensive_report.html) | **STRONG BUY**<br/>*Z-Score: 3.78 (Safe)* |
| **YPF**<br/>YPF | [View Report](output/YPF/YPF_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.11 (Distress)* |
| **ZIM**<br/>ZIM | [View Report](output/ZIM/ZIM_comprehensive_report.html) | **SELL**<br/>*Z-Score: 0.75 (Distress)* |
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
