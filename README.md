![AI-Powered Altman Z-Score Analysis](banner.png)

# AI-Powered Altman Z-Score Analysis

**Version: 4.0.1 (2025-06-26) 🎯 SEC EDGAR Elimination - Simplified & Enhanced**

Transform your investment decisions with **AI-powered financial health analysis**. Get instant, actionable insights on company bankruptcy risk, investment opportunities, and strategic recommendations with **production-ready multi-quarter analysis**.

## 🎯 **NEW v4.0.1: SEC EDGAR ELIMINATION & PROGRESS BAR ENHANCEMENT**

### ⚡ **Simplified & Enhanced Architecture**
- **�️ SEC EDGAR Infrastructure Removed:** Complete elimination of SEC EDGAR, XBRL, and field mapping complexity
- **🎯 FMP-Only Data Source:** Streamlined Financial Modeling Prep (FMP) exclusive architecture for reliability
- **📈 Faster Performance:** Reduced code complexity, faster data fetching, simplified maintenance
- **🔄 Legacy Code Deprecation:** Clean migration path with clear warnings and upgrade guidance

### 🎯 **Account-Optimized Experience**
```bash
# CLI automatically adapts to your account type
python main.py AAPL                # Uses intelligent defaults from .env
python main.py AAPL --quarters 8   # Extended analysis for paid accounts

# Large portfolio analysis with enhanced batch script
pwsh.exe -File run_batch_examples.ps1   # Interactive menu with 8 sector groups
```

### 🏢 **Professional Portfolio Analysis**
- **🎯 8 Sector Groups:** 130+ companies across distressed, tech, consumer, industrial, energy, healthcare, mega-cap, and recent IPOs
- **📊 Smart Processing:** Individual ticker processing to respect API limits and ensure reliability
- **⏱️ Rate Limiting:** Intelligent delays between groups and tickers for optimal API usage
- **📈 Comprehensive Coverage:** From distressed companies to mega-cap tech leaders

**📖 See [QUICK_START_ENHANCED.md](QUICK_START_ENHANCED.md) for complete features guide**

---

## 🎯 **What You Get**

### 💡 **Professional Investment Intelligence v4.1.0**
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

# Analyze multiple companies with enhanced batch processing
pwsh.exe -File run_batch_examples.ps1    # Interactive menu for sector analysis

# Generate comprehensive portfolio table
python generate_readme_table.py
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
Get tailored recommendations for your investment style:

| Profile | Focus | Risk Level | Typical Holdings |
|---------|-------|------------|------------------|
| **📊 Conservative** | Capital preservation | Low | JNJ, PG, KO, VZ |
| **💰 Dividend** | Income generation | Low-Medium | VZ, T, XOM, CVX |
| **💎 Value** | Undervalued stocks | Medium | IBM, INTC, F, GM |
| **📈 Growth** | Capital appreciation | Medium-High | NVDA, TSLA, AMZN |
| **🚀 Aggressive** | Maximum returns | High | PLTR, SNOW, ROKU |

### 💼 **For Investment Professionals**
- **CEO Insights:** Strategic leadership recommendations
- **CFO Analysis:** Financial strategy and capital allocation
- **Risk Assessment:** Comprehensive financial health scoring

---

<!-- BEGIN_TICKERS_TABLE -->
| Company | Report | Investment Recommendation |
|---------|--------|---------------------------|
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AAPL/AAPL_logo.png" alt="AAPL" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Apple Inc.</span></div> | [Full Report](output/AAPL/AAPL_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 7.24 (Safe)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/AVGO/AVGO_logo.png" alt="AVGO" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Broadcom Inc.</span></div> | [Full Report](output/AVGO/AVGO_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 8.30 (Safe)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/BK/BK_logo.png" alt="BK" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Bank of New York Mellon Corporation</span></div> | [Full Report](output/BK/BK_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.26 (Distress)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/F/F_logo.png" alt="F" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Ford Motor Company</span></div> | [Full Report](output/F/F_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.48 (Distress)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/GS/GS_logo.png" alt="GS" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>The Goldman Sachs Group, Inc.</span></div> | [Full Report](output/GS/GS_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: 0.15 (Distress)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/JPM/JPM_logo.png" alt="JPM" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>JPMorgan Chase & Co.</span></div> | [Full Report](output/JPM/JPM_comprehensive_report.html) | 📉 SELL<br/><sub>Z-Score: -0.37 (Distress)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/META/META_logo.png" alt="META" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Meta Platforms, Inc.</span></div> | [Full Report](output/META/META_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 12.62 (Safe)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/MSFT/MSFT_logo.png" alt="MSFT" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Microsoft Corporation</span></div> | [Full Report](output/MSFT/MSFT_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 10.16 (Safe)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NFLX/NFLX_logo.png" alt="NFLX" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Netflix, Inc.</span></div> | [Full Report](output/NFLX/NFLX_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 13.24 (Safe)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/NVDA/NVDA_logo.png" alt="NVDA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>NVIDIA Corporation</span></div> | [Full Report](output/NVDA/NVDA_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 57.38 (Safe)</sub> |
| <div style="display: flex; flex-direction: column; align-items: center; text-align: center;"><img src="output/TSLA/TSLA_logo.png" alt="TSLA" width="40" style="margin-right:8px; border-radius:4px;"/><br/><span>Tesla, Inc.</span></div> | [Full Report](output/TSLA/TSLA_comprehensive_report.html) | 📈 STRONG BUY<br/><sub>Z-Score: 13.55 (Safe)</sub> |
<!-- END_TICKERS_TABLE -->

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

**License:** MIT License - Free for personal and commercial use

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
