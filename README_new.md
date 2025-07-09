![Altman Z-Score Analysis](banner.png)

# AI-Powered Altman Z-Score Analysis

**Version: 4.8.0 (2025-07-09) 🚀 Z-Score Forecasting Engine**

Transform your investment decisions with **AI-powered financial health analysis** and **breakthrough academic research**. Get instant, actionable insights on company bankruptcy risk, investment opportunities, and strategic recommendations.

## 🚀 **What's New in v4.8.0**

### 🔮 **Z-Score Forecasting Engine**
- **Multi-Year Projections:** 1-3 year Z-Score forecasts using analyst consensus data
- **Scenario Analysis:** Optimistic, Base Case, and Pessimistic scenarios with confidence scoring
- **Visual Integration:** Dashed forecast lines extending historical trends in charts
- **Component-Level Modeling:** Individual Z-Score component projections with growth scenarios
- **Fiscal Year Precision:** Company-specific fiscal calendar alignment

### 📊 **Enhanced Visualizations** 
- **Candlestick Charts:** Professional OHLC visualization with color-coded price movements
- **Dual-Axis Display:** Z-Score (blue) and Stock Price (green) on same chart
- **Range Selector Optimization:** Reduced height for better chart proportions
- **Interactive Dashboards:** Real-time filtering, sorting, and search capabilities

## 🚀 **Quick Start**

```bash
# Install and analyze your first stock
pip install -r requirements.txt
python main.py AAPL

# 🆕 Z-Score Forecasting
python main.py AAPL --forecast-years 2              # 2-year projections
python main.py MSFT --forecast-years 1              # 1-year forecast (default)
python main.py TSLA --forecast-off                  # Disable forecasting

# Multi-stock analysis
python main.py AAPL MSFT GOOGL TSLA                 # Multiple stocks
python main.py --portfolio-file portfolios/tech_portfolio.txt   # Portfolio from file
python main.py --sector technology                  # Pre-defined sector

# Analysis options
python main.py AAPL --quarters 12                   # Extended historical analysis
python main.py NVDA --model retail                  # Force specific Z-Score model
python main.py META --log-level DEBUG               # Verbose logging

# Cache management
python main.py --clear-cache                        # Clear API cache
python main.py --cache-stats                        # View cache statistics
```

## 💡 **What You Get**

### 📊 **Comprehensive Analysis**
- **📋 11-Section AI Report:** Strategic insights with investment recommendations
- **📈 Interactive Charts:** Professional dashboards with trend analysis
- **🔮 Z-Score Forecasts:** Multi-year projections with scenario modeling
- **💾 Data Export:** CSV/JSON files for further analysis
- **🏆 Novel Retail Model:** Inventory turnover integration for retail companies

### 🎯 **Investment Intelligence**
- **Risk Assessment:** Safe, Gray Zone, or Distress categorization
- **AI-Powered Insights:** Azure OpenAI-generated commentary and recommendations
- **Profile-Specific Advice:** Tailored for Conservative, Growth, Value, Dividend, Aggressive investors
- **Market Correlation:** Z-Score vs price trend analysis for timing insights

### 🏢 **Portfolio Analysis**
- **130+ Companies:** Major market leaders and growth stocks
- **8 Sector Groups:** Technology, Healthcare, Financial, Industrial, Energy, Consumer, Utilities, Materials
- **Investment Styles:** Conservative, Growth, Value, Dividend, Aggressive portfolios
- **Modern Dashboard:** Self-contained HTML with advanced filtering and search

## ⚙️ **Setup**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Configure APIs**
Create a `.env` file:
```bash
# Required
FINANCIAL_MODELING_PREP_API_KEY="your-fmp-key"
AZURE_OPENAI_ENDPOINT="your-azure-endpoint"  
AZURE_OPENAI_API_KEY="your-azure-key"
AZURE_OPENAI_DEPLOYMENT="your-deployment"
SEC_EDGAR_USER_AGENT="YourCompany/1.0 your.email@domain.com"

# Optional
LOG_LEVEL="INFO"
LOG_DIR="logs"
```

### **3. Generate Dashboards**
```bash
# Modern interactive dashboard
.\generate_web.ps1

# Portfolio analysis
.\run_parallel_portfolio.ps1 -PortfolioFile "portfolios/tech_portfolio.txt"

# Retail model validation
.\run_retail_validation.ps1
```

## 🏆 **Key Features**

### 💎 **Academic Innovation**
- **Novel Retail Z-Score Model:** First retail-specific enhancement with inventory turnover (X₆ component)
- **Peer-Review Documentation:** Complete academic paper in `NOVEL_RETAIL_MODEL.md`
- **Empirical Validation:** 75-company backtest portfolio with statistical analysis

### 🔄 **Smart Architecture**
- **Bifurcated Data Flow:** Active companies (FMP + Yahoo) vs Delisted/Bankrupt (SEC EDGAR)
- **Intelligent Caching:** 48-hour TTL with 95% performance improvement
- **Automatic Model Selection:** Industry-specific Z-Score models (Original, Private, Service, Retail, Financial, Emerging)

### 🤖 **AI Integration**
- **Azure OpenAI:** Professional investment commentary and strategic insights
- **Risk Profiling:** Customized recommendations by investor type
- **Executive Analysis:** CEO/CFO strategic guidance and governance insights

## 📊 **Investment Profiles**

| Profile | Risk Level | Focus | Example Recommendation |
|---------|------------|-------|------------------------|
| **📊 Conservative** | Low | Capital preservation | "Safe Zone Z>3.0: HOLD - Strong fundamentals support stability" |
| **💰 Dividend** | Low-Medium | Income generation | "Safe Zone: BUY - Sustainable dividend growth supported by Z-Score" |
| **💎 Value** | Medium | Undervalued stocks | "Gray Zone: BUY - Potential turnaround with favorable risk/reward" |
| **📈 Growth** | Medium-High | Capital appreciation | "Safe Zone: STRONG BUY - Growth supported by solid financials" |
| **🚀 Aggressive** | High | Maximum returns | "Gray Zone: BUY - Volatility opportunity for strong recovery" |

## 📈 **Market Intelligence**

### 🔍 **Z-Score vs Price Trend Analysis**
| Pattern | Signal | Insight |
|---------|--------|---------|
| **Z-Score ↓, Price ↑** | **WARNING** | Market hasn't recognized financial stress |
| **Z-Score ↑, Price ↑** | **CONFIRMATION** | Sustainable growth with fundamental support |
| **Z-Score ↑, Price ↓** | **OPPORTUNITY** | Undervalued recovery play |
| **Z-Score ↓, Price ↓** | **CRISIS** | High bankruptcy risk - avoid/exit |

## 📚 **Documentation**

- **[FLOW.md](FLOW.md)** - Complete technical architecture
- **[MODELS.md](MODELS.md)** - Z-Score models and methodology  
- **[NOVEL_RETAIL_MODEL.md](NOVEL_RETAIL_MODEL.md)** - 🏆 Academic paper on retail innovation
- **[APIS.md](APIS.md)** - API integration documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## 🏢 **Portfolio Coverage**

### **Market Leaders**
- **Tech Giants:** AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA
- **Growth Champions:** NVDA, TSLA, NFLX, CRM, ADBE, NOW
- **Dividend Aristocrats:** KO, PG, JNJ, CAT, MMM, VZ
- **Retail Focus:** WMT, COST, TGT, HD, LOW, AMZN

### **Specialized Analysis**
- **🏪 Retail Companies:** Novel X₆ inventory turnover model
- **🏛️ Financial Institutions:** CAMELS framework integration
- **🌍 Emerging Markets:** EM-specific Z-Score thresholds
- **💼 Private Companies:** Non-manufacturing model variants

---

**Ready to revolutionize your investment analysis?** Start with `python main.py AAPL --forecast-years 2` and experience the future of financial intelligence.

## 📋 **CLI Reference**

```bash
# Basic usage
python main.py TICKER [TICKER2 ...]

# Key options
--forecast-years {1,2,3}    # Z-Score forecasting (NEW!)
--forecast-off              # Disable forecasting
--quarters QUARTERS         # Historical analysis periods (default: 8)
--model {original,private,financial,retail,service,emerging}
--portfolio-file FILE       # Analyze portfolio from file
--sector {technology,healthcare,financial,industrial,energy}
--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
--clear-cache              # Clear API cache
--cache-stats              # View cache statistics

# Examples
python main.py AAPL --forecast-years 2
python main.py --sector technology
python main.py --portfolio-file portfolios/my_stocks.txt
```

For complete CLI help: `python main.py --help`
