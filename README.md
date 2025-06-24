![AI-Powered Altman Z-Score Analysis](banner.png)

# AI-Powered Altman Z-Score Analysis

**Version: 3.11.0 (2025-06-24) 🚀 Complete Investment Analysis Platform**

A comprehensive investment analysis platform combining fundamental financial health assessment (Altman Z-Score) with advanced market intelligence. Features **technical analysis**, **valuation metrics**, **performance analysis**, and **actionable investment recommendations** powered by AI.

**Latest Update (June 24, 2025):** ✅ **MARKET ANALYSIS INTEGRATION COMPLETE** - Transformed from basic Z-Score calculator to comprehensive investment analysis platform. Now provides technical analysis (RSI, MACD, volatility), valuation analysis (P/E, P/B, PEG, sector comparison), performance analysis (returns, risk metrics), and clear investment recommendations with confidence levels and price targets.

---

## 🎯 **Strategic Architecture: FMP-First Data Pipeline**

### 🚀 **Production-Ready API Infrastructure**
- **⚡ FMP Pre-Calculated Ratios:** All Z-Score metrics (Working Capital/Total Assets, EBIT/Total Assets, etc.) provided **calculation-ready** from Financial Modeling Prep
- **🎯 Eliminates Field Mapping Complexity:** No need for SEC EDGAR XBRL parsing or complex field transformations
- **📊 48-Hour Intelligent Caching:** All FMP and Yahoo Finance API calls cached for optimal performance
- **🤖 Smart LLM Integration:** Azure OpenAI prompts/responses logged (not cached) for maximum insight variability
- **🔧 Complete Environment Configuration:** All API keys and user agents properly configured
- **🔒 Production Security:** Thread-safe operations with proper error handling
- **� Performance Optimized:** ~95% faster response times with deterministic data pipeline

### 🏗️ **API-First Data Sources**
- **Primary Financial Data:** FMP API with pre-calculated Z-Score ratios (eliminates field mapping)
- **Market Data:** Yahoo Finance integration for real-time pricing and market cap
- **AI Analysis:** Azure OpenAI for intelligent insights and commentary generation
- **Rate Limiting:** Intelligent API call management to prevent throttling
- **Cache Management:** Automatic 48-hour TTL with thread-safe file operations

**Strategic Advantage:** With FMP providing calculation-ready financial ratios, the system focuses on data integration and quality assurance rather than complex field transformations.

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

## 🚀 Key Features

- **🤖 Advanced AI Analysis:** 11-section comprehensive financial health reports with intelligent pattern recognition
- **📊 AI-Generated Portfolio Table:** Immediate investment recommendations with AI-driven stakeholder insights
- **🧠 Smart Cross-Data Analysis:** AI identifies hidden patterns across financial metrics and market data
- **💡 AI-Enhanced Insights:** Intelligent detection of market sentiment and financial health indicators
- **🛡️ Robust Data Validation:** Excludes non-standard company types (e.g., ETFs, BDCs) to ensure analysis is performed only on standard corporate structures.
- **🔄 Robust Data Pipeline:** SEC EDGAR + Yahoo Finance integration with intelligent error handling
- **🏢 135-Company AI Portfolio:** Real-world examples with comprehensive AI-generated recommendations

## 📁 Output Structure

All analysis saved to `output/<TICKER>/`:

- **📋 Full Report:** `zscore_<TICKER>_zscore_full_report.md` (11-section AI analysis + strategic recommendations)
- **📈 Trend Chart:** `zscore_<TICKER>_trend.png` (visual Z-Score analysis)
- **💾 Data Files:** CSV/JSON with quarterly calculations and real analyst recommendations

---

## 📊 Portfolio Analysis - 135 Companies

Comprehensive test portfolio demonstrating platform capabilities across diverse market segments and industries:

### 🏭 Market Segments

- **⚠️ Distressed/Cyclical (15):** T, UAL, AAL, AMC, GME, CCL, NCLH, GE, F, GM, X, FCX, BBY, M, SONO
- **� High-Growth Tech & SaaS (20):** SNOW, PLTR, UBER, LYFT, DASH, ROKU, DOCU, ZM, DDOG, NET, CRWD, MDB, SHOP, SQ, AFRM, COIN, RBLX, U, TWLO, OKTA
- **🛒 Consumer & Growth (20):** NFLX, DIS, SBUX, NKE, LULU, HD, LOW, TGT, COST, WMT, AMGN, GILD, MRNA, PFE, ABBV, TMO, DHR, CRM, ADBE, PYPL
- **� Industrial & Infrastructure (20):** CAT, DE, MMM, HON, GD, LMT, RTX, BA, UPS, FDX, CSX, UNP, WM, RSG, EMR, ETN, PH, ITW, ROK, ADP
- **⚡ Energy & Utilities (20):** XOM, CVX, COP, EOG, PXD, SLB, HAL, KMI, WMB, NEE, DUK, SO, D, EXC, AEP, PCG, ED, AWK, VZ, TMUS
- **🥤 Consumer Staples & Healthcare (20):** KO, PEP, PG, UL, CL, KMB, GIS, K, HSY, MO, PM, JNJ, UNH, CVS, WBA, MCK, ABC, CAH, CI, HUM
- **💎 Mega-Cap Tech Leaders (20):** AAPL, MSFT, GOOGL, GOOG, AMZN, META, TSLA, NVDA, AVGO, ORCL, INTC, AMD, QCOM, TXN, CSCO, IBM, INTU, NOW, PANW, AMAT

### ⭐ Notable Investor Favorites Included

**Warren Buffett Holdings:** AAPL, KO, PG, CVX  
**Growth Darlings:** TSLA, NVDA, NFLX, CRM, ADBE, NOW  
**Dividend Aristocrats:** KO, PG, JNJ, CAT, MMM, VZ  
**ESG Leaders:** MSFT, AAPL, NEE, UNH, TMO  
**Meme Stocks:** GME, AMC, TSLA, ROKU  
**AI/Cloud Plays:** NVDA, MSFT, GOOGL, SNOW, CRWD

### 🎯 Recommendation Framework

**Investment Profiles:**
- **CEO**: Strategic leadership focus 
- **CFO**: Financial strategy focus 
- **Conservative**: Capital Preservation 
- **Dividend**: Income-focused  
- **Value**: Value investing 
- **Growth**: Capital Appreciation  
- **Aggressive**: High-risk growth 
- **Short-Seller**: Bearish positions  

**Recommendation Indicators:**
- **📈 BUY** • **⚖️ HOLD** • **📉 SELL**

**CEO Action Categories:** 
- 🚀 FOCUS INNOVATION 
- 📢 COMMUNICATE GROWTH 
- 🔧 RESTRUCTURE 
- ⚡ EXECUTION FOCUS 
- 🎯 STRATEGIC FOCUS  

**CFO Action Categories:** 
- 💰 OPTIMIZE & INVEST 
- 💰 OPTIMIZE CAPITAL 
- 📊 STRATEGIC INVEST 
- 📊 MONITOR CAPITAL 
- ⚖️ MAINTAIN STABILITY

---

### 📋 How to Use This Table

1. **🔍 Find Your Company**: Browse by ticker symbol or company name
2. **📊 View Analysis**: Click "Report" for detailed 11-section AI analysis  
3. **📈 See Trends**: Click chart thumbnail for full Z-Score trend visualization
4. **🎯 Get Advice**: Review tailored recommendations for your investment profile
5. **📱 Mobile Friendly**: Table scales for viewing on any device

**💡 Pro Tip**: Use Ctrl+F to quickly find specific companies or sectors in your browser.

---

<!-- BEGIN_TICKERS_TABLE -->

<!-- END_TICKERS_TABLE -->

## 🔄 Table Generation

Update the comprehensive portfolio table automatically:

```sh
python generate_readme_table.py
```

### ✨ Enhanced Features

- **📊 Detailed Investor Profiles**: Shows BUY/HOLD/SELL for each investor type across 135 companies
- **📝 Multi-line Format**: Clear, readable recommendations in table cells
- **🎨 Professional Layout**: Full profile names with emoji indicators
- **📈 Comprehensive Coverage**: 7 industry segments with complete investment guidance
- **🔧 Profile-Based Recommendations**: Shows BUY/HOLD/SELL for each investor type
- **⚖️ Conservative to Aggressive**: Covers all risk tolerance levels  
- **📊 Visual Indicators**: 📈 BUY, ⚖️ HOLD, 📉 SELL with compact notation
- **🔄 Auto-updates README**: Updates content between table markers for all 135 companies

## ⚙️ Setup & Installation

### Prerequisites
- **Python 3.11+** required

### Installation Steps

```sh
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment template (add your API keys)
cp .env.example .env

# 3. Test installation
python main.py --test
```

## 🔧 Environment Setup & Configuration

### Required Environment Variables

Create a `.env` file in the project root with the following configuration:

```bash
# Financial Modeling Prep API Key (Required)
FINANCIAL_MODELING_PREP_API_KEY="your-fmp-api-key"

# SEC EDGAR User-Agent (Required for SEC compliance)
SEC_EDGAR_USER_AGENT="YourCompany/1.0 your.email@domain.com"

# Azure OpenAI Configuration (Required for AI analysis)
AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-azure-openai-key"
AZURE_OPENAI_DEPLOYMENT="your-deployment-name"

# Optional: Additional API Services
FINNHUB_API_KEY="your-finnhub-key"
YAHOO_FINANCE_USER_AGENT="YourCompany/1.0 your.email@domain.com"
```

### Quick Configuration Test

```bash
# Test all API configurations
python comprehensive_api_test.py

# Test specific components
python api_caching_demo.py  # API caching demonstration
python llm_demo.py          # LLM client testing
```

### 📊 API Services Integration

| Service | Purpose | Caching | TTL | Status |
|---------|---------|---------|-----|--------|
| **FMP API** | Financial statements, ratios | ✅ Yes | 48h | ✅ Production Ready |
| **Yahoo Finance** | Market data, prices | ✅ Yes | 48h | ✅ Production Ready |
| **Azure OpenAI** | AI analysis, insights | ❌ No* | N/A | ✅ Production Ready |
| **SEC EDGAR** | Regulatory filings | - | - | 🔄 Legacy Support |
| **Finnhub** | Additional market data | - | - | 🔄 Optional |

*_Azure OpenAI responses are logged (not cached) to preserve response variability_

## 🧪 Testing

The project now features a clean, modern test infrastructure:

```sh
# Run all infrastructure tests
python run_tests.py

# Or use pytest directly
python -m pytest tests/ -v
```

**Test Organization:**
- **Clean Structure**: Removed old legacy tests to avoid confusion
- **Infrastructure Tests**: 61 comprehensive tests for all core modules
- **Layered Architecture**: Tests organized by architectural layers

## 📚 Documentation

### Core Project Documentation
- **[README.md](./README.md)** - This main project overview and quick start guide
- **[FLOW.md](./FLOW.md)** - Current system architecture and data flow
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and completed features
- **[TODO.md](./TODO.md)** - Development roadmap and planned features
- **[MODELS.md](./MODELS.md)** - Z-Score model specifications and selection logic
- **[APIS.md](./APIS.md)** - API configuration and integration guide
- **[REFACTORING_PLAN.md](./REFACTORING_PLAN.md)** - Architecture modernization plan

### Detailed Documentation (`docs/`)
Comprehensive documentation organized by category:
- **[Implementation Details](./docs/implementation/)** - Feature implementation summaries and completion reports
- **[Analysis & Research](./docs/analysis/)** - Data analysis, validation studies, and research findings
- **[Guides & References](./docs/guides/)** - Development guides, testing references, and API documentation
- **[Status Reports](./docs/status/)** - Project progress and component status tracking

See **[docs/README.md](./docs/README.md)** for complete documentation index and navigation guide.

> **⚠️ Note:** Advanced multiperiod analysis features will be added in future releases.

---

## 📄 License & Data Sources

### License
**MIT License** (see [LICENSE](LICENSE) file)

### Data Sources
- **📊 Yahoo Finance** - Market data and pricing
- **🏛️ SEC EDGAR** - Regulatory filings and financial statements  
- **🏢 Finnhub.io** - Company profiles and logos

### Disclaimer
*All trademarks are property of their respective owners. This project is not affiliated with any data provider. Use for educational and informational purposes only.*
