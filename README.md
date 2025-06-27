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
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><div style="width:40px;height:40px;background:#2c3e50;color:white;display:flex;align-items:center;justify-content:center;margin-right:8px;font-weight:bold;border-radius:4px;">005930.KS</div><br/><span>Samsung Electronics Co., Ltd.</span></div> | [Full Report](output/005930.KS/005930.KS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.65 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AAPL/AAPL_logo.png" alt="AAPL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Apple Inc.</span></div> | [Full Report](output/AAPL/AAPL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 7.27 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ABBV/ABBV_logo.png" alt="ABBV" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>AbbVie Inc.</span></div> | [Full Report](output/ABBV/ABBV_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.48 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ABEV/ABEV_logo.png" alt="ABEV" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Ambev S.A.</span></div> | [Full Report](output/ABEV/ABEV_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.77 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ADBE/ADBE_logo.png" alt="ADBE" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Adobe Inc.</span></div> | [Full Report](output/ADBE/ADBE_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 8.43 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ADDYY/ADDYY_logo.png" alt="ADDYY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>adidas AG</span></div> | [Full Report](output/ADDYY/ADDYY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.67 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ADI/ADI_logo.png" alt="ADI" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Analog Devices, Inc.</span></div> | [Full Report](output/ADI/ADI_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 6.21 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AFL/AFL_logo.png" alt="AFL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Aflac Incorporated</span></div> | [Full Report](output/AFL/AFL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.73 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AIG/AIG_logo.png" alt="AIG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>American International Group, Inc.</span></div> | [Full Report](output/AIG/AIG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.73 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AJG/AJG_logo.png" alt="AJG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Arthur J. Gallagher & Co.</span></div> | [Full Report](output/AJG/AJG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.43 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ALL/ALL_logo.png" alt="ALL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Allstate Corporation</span></div> | [Full Report](output/ALL/ALL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.45 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AMD/AMD_logo.png" alt="AMD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Advanced Micro Devices, Inc.</span></div> | [Full Report](output/AMD/AMD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 10.66 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AMP/AMP_logo.png" alt="AMP" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Ameriprise Financial, Inc.</span></div> | [Full Report](output/AMP/AMP_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.46 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AMX/AMX_logo.png" alt="AMX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>América Móvil, S.A.B. de C.V.</span></div> | [Full Report](output/AMX/AMX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.13 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AMZN/AMZN_logo.png" alt="AMZN" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Amazon.com, Inc.</span></div> | [Full Report](output/AMZN/AMZN_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.86 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ANET/ANET_logo.png" alt="ANET" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Arista Networks, Inc.</span></div> | [Full Report](output/ANET/ANET_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 19.24 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ANSS/ANSS_logo.png" alt="ANSS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>ANSYS, Inc.</span></div> | [Full Report](output/ANSS/ANSS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 11.49 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/APH/APH_logo.png" alt="APH" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Amphenol Corporation</span></div> | [Full Report](output/APH/APH_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 6.67 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/APO/APO_logo.png" alt="APO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Apollo Global Management, Inc.</span></div> | [Full Report](output/APO/APO_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.01 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ASML/ASML_logo.png" alt="ASML" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>ASML Holding N.V.</span></div> | [Full Report](output/ASML/ASML_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 7.46 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AVGO/AVGO_logo.png" alt="AVGO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Broadcom Inc.</span></div> | [Full Report](output/AVGO/AVGO_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 8.26 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AXP/AXP_logo.png" alt="AXP" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>American Express Company</span></div> | [Full Report](output/AXP/AXP_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.28 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AZN/AZN_logo.png" alt="AZN" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>AstraZeneca PLC</span></div> | [Full Report](output/AZN/AZN_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.25 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AZO/AZO_logo.png" alt="AZO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>AutoZone, Inc.</span></div> | [Full Report](output/AZO/AZO_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.87 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BA/BA_logo.png" alt="BA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Boeing Company</span></div> | [Full Report](output/BA/BA_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.04 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BABA/BABA_logo.png" alt="BABA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Alibaba Group Holding Limited</span></div> | [Full Report](output/BABA/BABA_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.09 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BAC/BAC_logo.png" alt="BAC" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Bank of America Corporation</span></div> | [Full Report](output/BAC/BAC_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.44 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BBD/BBD_logo.png" alt="BBD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Banco Bradesco S.A.</span></div> | [Full Report](output/BBD/BBD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.20 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BCS/BCS_logo.png" alt="BCS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Barclays PLC</span></div> | [Full Report](output/BCS/BCS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.06 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BIDU/BIDU_logo.png" alt="BIDU" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Baidu, Inc.</span></div> | [Full Report](output/BIDU/BIDU_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.47 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BILI/BILI_logo.png" alt="BILI" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Bilibili Inc.</span></div> | [Full Report](output/BILI/BILI_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.69 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BK/BK_logo.png" alt="BK" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Bank of New York Mellon Corporation</span></div> | [Full Report](output/BK/BK_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.26 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BKNG/BKNG_logo.png" alt="BKNG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Booking Holdings Inc.</span></div> | [Full Report](output/BKNG/BKNG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 5.63 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BP/BP_logo.png" alt="BP" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>BP p.l.c.</span></div> | [Full Report](output/BP/BP_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.52 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BSX/BSX_logo.png" alt="BSX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Boston Scientific Corporation</span></div> | [Full Report](output/BSX/BSX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 5.62 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BX/BX_logo.png" alt="BX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Blackstone Inc.</span></div> | [Full Report](output/BX/BX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.65 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/C/C_logo.png" alt="C" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Citigroup Inc.</span></div> | [Full Report](output/C/C_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.48 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CAT/CAT_logo.png" alt="CAT" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Caterpillar Inc.</span></div> | [Full Report](output/CAT/CAT_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.04 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CBRE/CBRE_logo.png" alt="CBRE" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>CBRE Group, Inc.</span></div> | [Full Report](output/CBRE/CBRE_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.77 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CEG/CEG_logo.png" alt="CEG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Constellation Energy Corporation</span></div> | [Full Report](output/CEG/CEG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.90 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CHKP/CHKP_logo.png" alt="CHKP" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Check Point Software Technologies Ltd.</span></div> | [Full Report](output/CHKP/CHKP_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 8.87 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CMI/CMI_logo.png" alt="CMI" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Cummins Inc.</span></div> | [Full Report](output/CMI/CMI_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.74 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/COF/COF_logo.png" alt="COF" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Capital One Financial Corporation</span></div> | [Full Report](output/COF/COF_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.35 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/COIN/COIN_logo.png" alt="COIN" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Coinbase Global, Inc.</span></div> | [Full Report](output/COIN/COIN_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 6.10 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/COR/COR_logo.png" alt="COR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Cencora, Inc.</span></div> | [Full Report](output/COR/COR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.61 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/COST/COST_logo.png" alt="COST" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Costco Wholesale Corporation</span></div> | [Full Report](output/COST/COST_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 6.75 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CPAY/CPAY_logo.png" alt="CPAY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Corpay, Inc.</span></div> | [Full Report](output/CPAY/CPAY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.81 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CPRT/CPRT_logo.png" alt="CPRT" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Copart, Inc.</span></div> | [Full Report](output/CPRT/CPRT_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 34.16 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CRM/CRM_logo.png" alt="CRM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Salesforce, Inc.</span></div> | [Full Report](output/CRM/CRM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.53 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/CRWD/CRWD_logo.png" alt="CRWD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>CrowdStrike Holdings, Inc.</span></div> | [Full Report](output/CRWD/CRWD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 14.72 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/DASH/DASH_logo.png" alt="DASH" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>DoorDash, Inc.</span></div> | [Full Report](output/DASH/DASH_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 11.80 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/DB/DB_logo.png" alt="DB" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Deutsche Bank AG</span></div> | [Full Report](output/DB/DB_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.30 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/DELL/DELL_logo.png" alt="DELL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Dell Technologies Inc.</span></div> | [Full Report](output/DELL/DELL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.77 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/DIS/DIS_logo.png" alt="DIS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Walt Disney Company</span></div> | [Full Report](output/DIS/DIS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.00 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/DLR/DLR_logo.png" alt="DLR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Digital Realty Trust, Inc.</span></div> | [Full Report](output/DLR/DLR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.68 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/E/E_logo.png" alt="E" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Eni S.p.A.</span></div> | [Full Report](output/E/E_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.98 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/EFX/EFX_logo.png" alt="EFX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Equifax Inc.</span></div> | [Full Report](output/EFX/EFX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.72 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ETN/ETN_logo.png" alt="ETN" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Eaton Corporation plc</span></div> | [Full Report](output/ETN/ETN_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.73 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ETR/ETR_logo.png" alt="ETR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Entergy Corporation</span></div> | [Full Report](output/ETR/ETR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.74 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/FAST/FAST_logo.png" alt="FAST" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Fastenal Company</span></div> | [Full Report](output/FAST/FAST_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 26.44 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GE/GE_logo.png" alt="GE" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>General Electric Company</span></div> | [Full Report](output/GE/GE_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.62 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GEV/GEV_logo.png" alt="GEV" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>GE Vernova Inc.</span></div> | [Full Report](output/GEV/GEV_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.22 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GGAL/GGAL_logo.png" alt="GGAL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Grupo Financiero Galicia S.A.</span></div> | [Full Report](output/GGAL/GGAL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.42 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GILD/GILD_logo.png" alt="GILD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Gilead Sciences, Inc.</span></div> | [Full Report](output/GILD/GILD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.77 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GM/GM_logo.png" alt="GM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>General Motors Company</span></div> | [Full Report](output/GM/GM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.68 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GOOG/GOOG_logo.png" alt="GOOG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Alphabet Inc.</span></div> | [Full Report](output/GOOG/GOOG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 11.09 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GOOGL/GOOGL_logo.png" alt="GOOGL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Alphabet Inc.</span></div> | [Full Report](output/GOOGL/GOOGL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 11.09 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GRMN/GRMN_logo.png" alt="GRMN" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Garmin Ltd.</span></div> | [Full Report](output/GRMN/GRMN_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 16.42 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GS/GS_logo.png" alt="GS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Goldman Sachs Group, Inc.</span></div> | [Full Report](output/GS/GS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.15 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GSK/GSK_logo.png" alt="GSK" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>GSK plc</span></div> | [Full Report](output/GSK/GSK_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.38 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GWW/GWW_logo.png" alt="GWW" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>W.W. Grainger, Inc.</span></div> | [Full Report](output/GWW/GWW_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 7.32 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/HD/HD_logo.png" alt="HD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Home Depot, Inc.</span></div> | [Full Report](output/HD/HD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.28 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/HDB/HDB_logo.png" alt="HDB" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>HDFC Bank Limited</span></div> | [Full Report](output/HDB/HDB_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.13 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/HIG/HIG_logo.png" alt="HIG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Hartford Financial Services Group, Inc.</span></div> | [Full Report](output/HIG/HIG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.96 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/HUBS/HUBS_logo.png" alt="HUBS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>HubSpot, Inc.</span></div> | [Full Report](output/HUBS/HUBS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 9.35 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/IBM/IBM_logo.png" alt="IBM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>International Business Machines Corporation</span></div> | [Full Report](output/IBM/IBM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.96 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/INFY/INFY_logo.png" alt="INFY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Infosys Limited</span></div> | [Full Report](output/INFY/INFY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 9.22 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ING/ING_logo.png" alt="ING" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>ING Groep N.V.</span></div> | [Full Report](output/ING/ING_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.66 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/INTU/INTU_logo.png" alt="INTU" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Intuit Inc.</span></div> | [Full Report](output/INTU/INTU_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 9.29 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/IR/IR_logo.png" alt="IR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Ingersoll Rand Inc.</span></div> | [Full Report](output/IR/IR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.14 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ISRG/ISRG_logo.png" alt="ISRG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Intuitive Surgical, Inc.</span></div> | [Full Report](output/ISRG/ISRG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 58.20 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ITUB/ITUB_logo.png" alt="ITUB" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Itaú Unibanco Holding S.A.</span></div> | [Full Report](output/ITUB/ITUB_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.34 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/JD/JD_logo.png" alt="JD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>JD.com, Inc.</span></div> | [Full Report](output/JD/JD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.70 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/JNJ/JNJ_logo.png" alt="JNJ" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Johnson & Johnson</span></div> | [Full Report](output/JNJ/JNJ_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.38 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/JPM/JPM_logo.png" alt="JPM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>JPMorgan Chase & Co.</span></div> | [Full Report](output/JPM/JPM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.37 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/K/K_logo.png" alt="K" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Kellanova</span></div> | [Full Report](output/K/K_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.52 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/LHX/LHX_logo.png" alt="LHX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>L3Harris Technologies, Inc.</span></div> | [Full Report](output/LHX/LHX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.55 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/LI/LI_logo.png" alt="LI" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Li Auto Inc.</span></div> | [Full Report](output/LI/LI_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.79 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/LIN/LIN_logo.png" alt="LIN" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Linde plc</span></div> | [Full Report](output/LIN/LIN_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.44 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/LLY/LLY_logo.png" alt="LLY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Eli Lilly and Company</span></div> | [Full Report](output/LLY/LLY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 6.55 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/LNG/LNG_logo.png" alt="LNG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Cheniere Energy, Inc.</span></div> | [Full Report](output/LNG/LNG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.43 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/LVMUY/LVMUY_logo.png" alt="LVMUY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>LVMH Moët Hennessy - Louis Vuitton, Société Européenne</span></div> | [Full Report](output/LVMUY/LVMUY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.51 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MA/MA_logo.png" alt="MA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Mastercard Incorporated</span></div> | [Full Report](output/MA/MA_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 9.78 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MET/MET_logo.png" alt="MET" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>MetLife, Inc.</span></div> | [Full Report](output/MET/MET_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.71 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/META/META_logo.png" alt="META" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Meta Platforms, Inc.</span></div> | [Full Report](output/META/META_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 12.61 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MLM/MLM_logo.png" alt="MLM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Martin Marietta Materials, Inc.</span></div> | [Full Report](output/MLM/MLM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.46 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MMM/MMM_logo.png" alt="MMM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>3M Company</span></div> | [Full Report](output/MMM/MMM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.14 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MNDY/MNDY_logo.png" alt="MNDY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>monday.com Ltd.</span></div> | [Full Report](output/MNDY/MNDY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 14.66 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MPC/MPC_logo.png" alt="MPC" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Marathon Petroleum Corporation</span></div> | [Full Report](output/MPC/MPC_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.64 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MPWR/MPWR_logo.png" alt="MPWR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Monolithic Power Systems, Inc.</span></div> | [Full Report](output/MPWR/MPWR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 40.90 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MS/MS_logo.png" alt="MS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Morgan Stanley</span></div> | [Full Report](output/MS/MS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.03 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MSFT/MSFT_logo.png" alt="MSFT" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Microsoft Corporation</span></div> | [Full Report](output/MSFT/MSFT_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 10.16 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MU/MU_logo.png" alt="MU" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Micron Technology, Inc.</span></div> | [Full Report](output/MU/MU_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.36 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NFLX/NFLX_logo.png" alt="NFLX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Netflix, Inc.</span></div> | [Full Report](output/NFLX/NFLX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 13.27 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NICE/NICE_logo.png" alt="NICE" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>NICE Ltd.</span></div> | [Full Report](output/NICE/NICE_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.07 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NIO/NIO_logo.png" alt="NIO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>NIO Inc.</span></div> | [Full Report](output/NIO/NIO_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.16 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NKE/NKE_logo.png" alt="NKE" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>NIKE, Inc.</span></div> | [Full Report](output/NKE/NKE_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.48 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NOW/NOW_logo.png" alt="NOW" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>ServiceNow, Inc.</span></div> | [Full Report](output/NOW/NOW_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 12.14 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NVDA/NVDA_logo.png" alt="NVDA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>NVIDIA Corporation</span></div> | [Full Report](output/NVDA/NVDA_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 57.11 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NVO/NVO_logo.png" alt="NVO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Novo Nordisk A/S</span></div> | [Full Report](output/NVO/NVO_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.18 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/OKTA/OKTA_logo.png" alt="OKTA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Okta, Inc.</span></div> | [Full Report](output/OKTA/OKTA_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.50 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ORCL/ORCL_logo.png" alt="ORCL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Oracle Corporation</span></div> | [Full Report](output/ORCL/ORCL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.57 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ORLY/ORLY_logo.png" alt="ORLY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>O'Reilly Automotive, Inc.</span></div> | [Full Report](output/ORLY/ORLY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.70 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PANW/PANW_logo.png" alt="PANW" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Palo Alto Networks, Inc.</span></div> | [Full Report](output/PANW/PANW_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 5.72 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PBR/PBR_logo.png" alt="PBR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Petróleo Brasileiro S.A. - Petrobras</span></div> | [Full Report](output/PBR/PBR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.57 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PCAR/PCAR_logo.png" alt="PCAR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>PACCAR Inc</span></div> | [Full Report](output/PCAR/PCAR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.65 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PDD/PDD_logo.png" alt="PDD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>PDD Holdings Inc.</span></div> | [Full Report](output/PDD/PDD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.83 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PFE/PFE_logo.png" alt="PFE" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Pfizer Inc.</span></div> | [Full Report](output/PFE/PFE_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.70 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PGR/PGR_logo.png" alt="PGR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Progressive Corporation</span></div> | [Full Report](output/PGR/PGR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.08 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PH/PH_logo.png" alt="PH" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Parker-Hannifin Corporation</span></div> | [Full Report](output/PH/PH_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.76 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PLTR/PLTR_logo.png" alt="PLTR" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Palantir Technologies Inc.</span></div> | [Full Report](output/PLTR/PLTR_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 167.83 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PM/PM_logo.png" alt="PM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Philip Morris International Inc.</span></div> | [Full Report](output/PM/PM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.49 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PNC/PNC_logo.png" alt="PNC" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The PNC Financial Services Group, Inc.</span></div> | [Full Report](output/PNC/PNC_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.53 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/PODD/PODD_logo.png" alt="PODD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Insulet Corporation</span></div> | [Full Report](output/PODD/PODD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 6.84 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/RCL/RCL_logo.png" alt="RCL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Royal Caribbean Cruises Ltd.</span></div> | [Full Report](output/RCL/RCL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.68 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/RHHBY/RHHBY_logo.png" alt="RHHBY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Roche Holding AG</span></div> | [Full Report](output/RHHBY/RHHBY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.80 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/RIO/RIO_logo.png" alt="RIO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Rio Tinto Group</span></div> | [Full Report](output/RIO/RIO_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.44 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/RTX/RTX_logo.png" alt="RTX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>RTX Corporation</span></div> | [Full Report](output/RTX/RTX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.75 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SAP/SAP_logo.png" alt="SAP" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Sap Se</span></div> | [Full Report](output/SAP/SAP_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 8.16 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SBUX/SBUX_logo.png" alt="SBUX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Starbucks Corporation</span></div> | [Full Report](output/SBUX/SBUX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.47 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SCHW/SCHW_logo.png" alt="SCHW" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Charles Schwab Corporation</span></div> | [Full Report](output/SCHW/SCHW_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.09 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SHEL/SHEL_logo.png" alt="SHEL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Shell plc</span></div> | [Full Report](output/SHEL/SHEL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.52 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SIEGY/SIEGY_logo.png" alt="SIEGY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Siemens AG</span></div> | [Full Report](output/SIEGY/SIEGY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.81 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SNY/SNY_logo.png" alt="SNY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Sanofi</span></div> | [Full Report](output/SNY/SNY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.47 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SONY/SONY_logo.png" alt="SONY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Sony Group Corporation</span></div> | [Full Report](output/SONY/SONY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.25 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SPGI/SPGI_logo.png" alt="SPGI" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>S&P Global Inc.</span></div> | [Full Report](output/SPGI/SPGI_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.41 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SQM/SQM_logo.png" alt="SQM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Sociedad Química y Minera de Chile S.A.</span></div> | [Full Report](output/SQM/SQM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.97 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SSNC/SSNC_logo.png" alt="SSNC" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>SS&C Technologies Holdings, Inc.</span></div> | [Full Report](output/SSNC/SSNC_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.06 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/STT/STT_logo.png" alt="STT" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>State Street Corporation</span></div> | [Full Report](output/STT/STT_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.09 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/SYK/SYK_logo.png" alt="SYK" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Stryker Corporation</span></div> | [Full Report](output/SYK/SYK_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.46 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/T/T_logo.png" alt="T" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>AT&T Inc.</span></div> | [Full Report](output/T/T_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.54 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TDG/TDG_logo.png" alt="TDG" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>TransDigm Group Incorporated</span></div> | [Full Report](output/TDG/TDG_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.88 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TEVA/TEVA_logo.png" alt="TEVA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Teva Pharmaceutical Industries Limited</span></div> | [Full Report](output/TEVA/TEVA_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.02 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TJX/TJX_logo.png" alt="TJX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The TJX Companies, Inc.</span></div> | [Full Report](output/TJX/TJX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.12 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TM/TM_logo.png" alt="TM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Toyota Motor Corporation</span></div> | [Full Report](output/TM/TM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.81 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TMO/TMO_logo.png" alt="TMO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Thermo Fisher Scientific Inc.</span></div> | [Full Report](output/TMO/TMO_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.18 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TMUS/TMUS_logo.png" alt="TMUS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>T-Mobile US, Inc.</span></div> | [Full Report](output/TMUS/TMUS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.33 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TSLA/TSLA_logo.png" alt="TSLA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Tesla, Inc.</span></div> | [Full Report](output/TSLA/TSLA_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 13.52 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TSM/TSM_logo.png" alt="TSM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Taiwan Semiconductor Manufacturing Company Limited</span></div> | [Full Report](output/TSM/TSM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.65 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/UAL/UAL_logo.png" alt="UAL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>United Airlines Holdings, Inc.</span></div> | [Full Report](output/UAL/UAL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.35 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/UBER/UBER_logo.png" alt="UBER" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Uber Technologies, Inc.</span></div> | [Full Report](output/UBER/UBER_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.70 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/UL/UL_logo.png" alt="UL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Unilever PLC</span></div> | [Full Report](output/UL/UL_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.87 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/UNH/UNH_logo.png" alt="UNH" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>UnitedHealth Group Incorporated</span></div> | [Full Report](output/UNH/UNH_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.64 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/UPS/UPS_logo.png" alt="UPS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>United Parcel Service, Inc.</span></div> | [Full Report](output/UPS/UPS_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 1.80 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/URI/URI_logo.png" alt="URI" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>United Rentals, Inc.</span></div> | [Full Report](output/URI/URI_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.42 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/V/V_logo.png" alt="V" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Visa Inc.</span></div> | [Full Report](output/V/V_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 7.98 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/VALE/VALE_logo.png" alt="VALE" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Vale S.A.</span></div> | [Full Report](output/VALE/VALE_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.73 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/VOD/VOD_logo.png" alt="VOD" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Vodafone Group Public Limited Company</span></div> | [Full Report](output/VOD/VOD_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -1.00 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/VRTX/VRTX_logo.png" alt="VRTX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Vertex Pharmaceuticals Incorporated</span></div> | [Full Report](output/VRTX/VRTX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 11.86 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/WDAY/WDAY_logo.png" alt="WDAY" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Workday, Inc.</span></div> | [Full Report](output/WDAY/WDAY_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 4.96 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/WFC/WFC_logo.png" alt="WFC" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Wells Fargo & Company</span></div> | [Full Report](output/WFC/WFC_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: -0.41 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/WIT/WIT_logo.png" alt="WIT" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Wipro Limited</span></div> | [Full Report](output/WIT/WIT_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 1.56 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/WIX/WIX_logo.png" alt="WIX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Wix.com Ltd.</span></div> | [Full Report](output/WIX/WIX_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">⚖️ HOLD<br/><sub>Z-Score: 2.12 (Gray Zone)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/WMT/WMT_logo.png" alt="WMT" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Walmart Inc.</span></div> | [Full Report](output/WMT/WMT_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📈 STRONG BUY<br/><sub>Z-Score: 3.78 (Safe)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/YPF/YPF_logo.png" alt="YPF" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>YPF Sociedad Anónima</span></div> | [Full Report](output/YPF/YPF_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.11 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/ZIM/ZIM_logo.png" alt="ZIM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>ZIM Integrated Shipping Services Ltd.</span></div> | [Full Report](output/ZIM/ZIM_comprehensive_report.html) | 
<div style="margin-bottom: 8px;">📉 SELL<br/><sub>Z-Score: 0.75 (Distress)</sub></div>
<details style="font-size: 0.9em;">
<summary style="cursor: pointer; font-weight: bold; color: #0366d6;">🎯 AI Investment Profiles</summary>
<div style="margin-top: 4px; padding: 4px 0;">🔍 Analysis Pending</div>
</details> |
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
