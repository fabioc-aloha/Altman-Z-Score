![AI-Powered Altman Z-Score Analysis](banner.png)

# AI-Powered Altman Z-Score Analysis

**Version: 4.3.1 (2025-06-27) 🚀 Golden Release - Table Formatting & Git Management**

Transform your investment decisions with **AI-powered financial health analysis**. Get instant, actionable insights on company bankruptcy risk, investment opportunities, and strategic recommendations with **production-ready multi-quarter analysis**.

## 🎯 **NEW v4.3.1: Golden Release - Table Formatting & Git Management**

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

# High-performance portfolio analysis (NEW v4.3.1 defaults)
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

## � **Interactive Portfolio Dashboards**

Access comprehensive portfolio analysis through professional HTML dashboards in the `web/` directory:

### 🎯 **Investment Style Portfolios**
- **[Conservative Picks](web/conservative_picks.html)** - Capital preservation focused
- **[Dividend Picks](web/dividend_picks.html)** - Income generation portfolio  
- **[Value Picks](web/value_picks.html)** - Undervalued opportunities
- **[Growth Picks](web/growth_picks.html)** - Capital appreciation focused
- **[Aggressive Picks](web/aggressive_picks.html)** - High-risk, high-reward
- **[Strong Buys](web/strong_buys.html)** - Top recommendations
- **[Sell Recommendations](web/sell_picks.html)** - Exit positions
- **[Strong Sells](web/strong_sell_picks.html)** - Urgent exit recommendations

### 🏭 **Model-Specific Industry Portfolios**
- **[Manufacturing & Industrial](web/manufacturing_&_industrial.html)** - Original Altman Z-Score (1968)
- **[Private & Service Companies](web/private_&_service_companies.html)** - Altman Z'-Score (1983)
- **[Emerging Markets](web/emerging_markets.html)** - Altman Z"-Score (2012)
- **[Financial Institutions](web/financial_institutions.html)** - CAMELS Framework
- **[Regulated Utilities](web/regulated_utilities.html)** - Utility-Specific Ratios
- **[Technology & Growth](web/technology_&_growth.html)** - Growth-Adjusted Ratios
- **[Retail & Consumer](web/retail_&_consumer.html)** - Retail-Specific Metrics

### 🏠 **Navigation Dashboards**
- **[Main Portfolio Index](web/index.html)** - Central navigation hub
- **[Model Portfolios Index](web/model_portfolios_index.html)** - Model-specific dashboard navigator

**💡 Pro Tip:** Each dashboard includes interactive charts, AI-powered insights, risk analysis, and detailed company breakdowns with Z-Score trends and investment recommendations.

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

### **Step 3: Generate Portfolio Dashboards**
```bash
# Generate investment style portfolios
python generate_main_page.py

# Generate model-specific industry portfolios
python generate_model_portfolios.py

# Analyze individual companies
python main.py AAPL MSFT GOOGL TSLA NVDA --log-level DEBUG

# Advanced batch analysis
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
- Browse **[Portfolio Dashboards](web/)** to see comprehensive analysis
- Review **[API Documentation](docs/technical/)** for configuration help

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

## 📋 **How to View Portfolio Dashboards**

**📌 Important:** GitHub displays HTML files as raw code, not rendered pages. To view the actual interactive portfolio dashboards:

### 🖥️ **Option 1: Clone Repository (Recommended for Full Experience)**
```bash
# Clone the repository
git clone https://github.com/your-username/Altman-Z-Score-1.git
cd Altman-Z-Score-1

# Open the main portfolio dashboard
start web/index.html                                     # Windows
open web/index.html                                      # macOS  
xdg-open web/index.html                                  # Linux

# Or open specific portfolio dashboards
start web/conservative_picks.html                        # Windows
start web/model_portfolios_index.html                    # Windows
```

### 📁 **Option 2: Download Individual Dashboards**
1. Navigate to the `web/` directory in this repository
2. Click on any HTML file (e.g., `conservative_picks.html`)
3. On the GitHub file page, click the "Download" button (or Raw → Save As)
4. Open the downloaded HTML file in your browser

### 🔄 **Option 3: Generate Fresh Portfolio Analysis**
```bash
# Generate all investment style portfolios
python generate_main_page.py

# Generate all model-specific industry portfolios  
python generate_model_portfolios.py

# Run individual company analysis
python main.py AAPL

# Run comprehensive batch analysis
pwsh.exe -File run_batch_examples.ps1
```

**💡 Tip:** The dashboards contain interactive charts, AI insights, Z-Score trend analysis, and comprehensive financial breakdowns that are best viewed in a browser, not on GitHub.
