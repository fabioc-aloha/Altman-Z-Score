# Altman Z-Score Analysis System - User Manual

**Version: 5.0.0 PENTNILNILIUM (2025-07-23) – EMERALD Release Series**

![Altman Z-Score Analysis](ALEX-INVESTMENT.png)

## 📋 Table of Contents

1. [System Overview](#-system-overview)
2. [Quick Start Guide](#-quick-start-guide)
3. [Installation & Setup](#️-installation--setup)
4. [Portfolio Management](#-portfolio-management)
5. [Running Analysis](#-running-analysis)
6. [Dashboard Generation](#-dashboard-generation)
7. [Understanding Results](#-understanding-results)
8. [Advanced Features](#-advanced-features)
9. [Troubleshooting](#-troubleshooting)
10. [API Configuration](#-api-configuration)
11. [Best Practices](#-best-practices)
12. [Reference](#-reference)

---

## 🎯 System Overview

The Altman Z-Score Analysis System is a comprehensive financial health assessment tool that combines:

- **🔍 Multi-Model Z-Score Analysis**: Traditional, retail-specific, and industry-optimized models
- **🤖 AI-Powered Insights**: Azure OpenAI integration for intelligent commentary and recommendations
- **📊 Professional Reporting**: Interactive dashboards, detailed reports, and visualizations
- **⚡ High Performance**: Smart caching, parallel processing, and enterprise-scale optimization
- **🌐 Multi-Platform**: Python CLI, PowerShell automation, and web dashboard interfaces

### Key Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Bankruptcy Risk Assessment** | Altman Z-Score calculation with industry-specific models | Early warning system for financial distress |
| **Investment Recommendations** | AI-powered buy/hold/sell guidance | Actionable investment decisions |
| **Portfolio Analysis** | Batch processing of multiple companies | Efficient large-scale analysis |
| **Interactive Dashboards** | Real-time filtering and visualization | Professional presentation tools |
| **Academic Research** | Novel retail-specific Z-Score model | Cutting-edge financial analysis |

---

## 🚀 Quick Start Guide

### 1. Single Company Analysis (Python CLI)

```bash
# Analyze a single stock
python main.py AAPL

# Analyze with specific settings
python main.py MSFT --quarters 8 --ai-analysis
```

### 2. Portfolio Analysis (PowerShell)

```powershell
# Analyze a pre-built portfolio
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt"

# Quick analysis with skip-existing
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\retail_quick_test.txt" -SkipExisting
```

### 3. Generate Web Dashboard

```powershell
# Create interactive dashboard
.\generate_web.ps1

# Generate with verbose output
.\generate_web.ps1 -Verbose
```

---

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+** (Recommended: Python 3.11)
- **PowerShell 5.1+** (Windows) or **PowerShell Core 6+** (Cross-platform)
- **Internet Connection** for API access
- **4GB+ RAM** for large portfolio analysis

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-repo/Altman-Z-Score.git
   cd Altman-Z-Score
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   ```bash
   # Copy and edit configuration template
   cp altman_zscore/common/config.py.template altman_zscore/common/config.py
   ```

4. **Verify Installation**
   ```bash
   python main.py --help
   ```

### API Configuration

Create or edit `altman_zscore/common/config.py`:

```python
# Financial Data API Configuration
FMP_API_KEY = "your_fmp_api_key_here"  # Required for financial data

# AI Analysis Configuration (Optional)
AZURE_OPENAI_API_KEY = "your_azure_openai_key"
AZURE_OPENAI_ENDPOINT = "https://your-endpoint.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT = "your-deployment-name"

# Cache Settings
CACHE_DURATION_HOURS = 48  # Default cache TTL
```

### Obtaining API Keys

1. **Financial Modeling Prep (FMP)**
   - Visit: https://financialmodelingprep.com/
   - Sign up for free tier or paid plan
   - Copy API key to config file

2. **Azure OpenAI (Optional - for AI insights)**
   - Azure account required
   - Create OpenAI resource in Azure Portal
   - Deploy GPT-4 model
   - Copy endpoint and key details

---

## 📁 Portfolio Management

### Creating Custom Portfolios

Portfolio files are simple text files with one ticker per line. Comments start with `#`.

#### Example Portfolio File (`my_portfolio.txt`)

```text
# My Custom Technology Portfolio
# Created: 2025-07-23

# Large Cap Technology
AAPL
MSFT
GOOGL
AMZN

# Cloud Infrastructure
CRM
SNOW
PLTR

# International Technology
ASML    # Netherlands - Advanced chipmaking
TSM     # Taiwan - Semiconductor manufacturing

# Emerging Growth
RKLB    # Space technology
PLTR    # Data analytics
```

### Pre-Built Portfolios

| Portfolio File | Description | Company Count | Use Case |
|----------------|-------------|---------------|----------|
| `comprehensive_portfolio.txt` | Complete market coverage | 410+ | Full market analysis |
| `retail_backtest_portfolio.txt` | Retail industry focus | 75+ | Retail-specific analysis |
| `retail_quick_test.txt` | Fast retail validation | 20+ | Quick testing |
| `retail_validation_minimal.txt` | Minimal test set | 10+ | Development/testing |

### Portfolio Organization Best Practices

1. **Group by Sector/Industry**
   ```text
   # Technology Sector
   AAPL
   MSFT

   # Healthcare Sector
   JNJ
   PFE
   ```

2. **Add Descriptive Comments**
   ```text
   TSLA    # Electric vehicles - high volatility
   NFLX    # Streaming - subscription model
   ```

3. **Use Exchange Suffixes for International Stocks**
   ```text
   ASML.AS  # Netherlands
   SAP.DE   # Germany
   NESN.SW  # Switzerland
   ```

---

## 🔍 Running Analysis

### Python CLI (main.py)

The main Python script provides detailed analysis for individual companies or small batches.

#### Basic Usage

```bash
# Single company analysis
python main.py AAPL

# Multiple companies
python main.py AAPL MSFT GOOGL

# With custom settings
python main.py TSLA --quarters 12 --ai-analysis --verbose
```

#### Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--quarters` | Number of quarters to analyze | 8 | `--quarters 12` |
| `--ai-analysis` | Enable AI-powered insights | False | `--ai-analysis` |
| `--no-cache` | Disable API response caching | False | `--no-cache` |
| `--verbose` | Detailed output logging | False | `--verbose` |
| `--output-format` | Output format (csv, json, all) | all | `--output-format json` |
| `--skip-existing` | Skip companies with existing analysis | False | `--skip-existing` |

#### Usage Examples

```bash
# Quick analysis without AI
python main.py AAPL --quarters 4

# Full analysis with AI insights
python main.py MSFT --quarters 12 --ai-analysis --verbose

# Batch analysis with caching disabled
python main.py AAPL MSFT GOOGL --no-cache

# JSON output only
python main.py TSLA --output-format json

# Skip existing analysis files
python main.py NVDA --skip-existing
```

### PowerShell Portfolio Analysis

For large-scale portfolio analysis, use the PowerShell scripts that provide parallel processing and enterprise-scale optimizations.

#### analyze_portfolio_parallel_v2.ps1

The primary portfolio analysis tool with advanced features:

```powershell
# Basic portfolio analysis
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt"

# With performance optimization
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt" -SkipExisting -MaxThreads 8

# Custom ticker list
.\analyze_portfolio_parallel_v2.ps1 -Tickers @("AAPL", "MSFT", "GOOGL", "AMZN")

# Sector-based analysis
.\analyze_portfolio_parallel_v2.ps1 -Sector technology -MaxThreads 16
```

#### PowerShell Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `-PortfolioFile` | String | Path to portfolio file | `-PortfolioFile "portfolios\my_portfolio.txt"` |
| `-Tickers` | Array | List of tickers to analyze | `-Tickers @("AAPL", "MSFT")` |
| `-Sector` | String | Analyze companies by sector | `-Sector technology` |
| `-SkipExisting` | Switch | Skip companies with existing analysis | `-SkipExisting` |
| `-MaxThreads` | Int | Maximum parallel threads | `-MaxThreads 8` |
| `-BatchSize` | Int | Companies per batch | `-BatchSize 10` |
| `-Quarters` | Int | Number of quarters to analyze | `-Quarters 12` |
| `-DryRun` | Switch | Preview without execution | `-DryRun` |
| `-Timeout` | Int | Timeout per company (minutes) | `-Timeout 15` |

#### Advanced PowerShell Examples

```powershell
# Enterprise-scale analysis (400+ companies)
.\analyze_portfolio_parallel_v2.ps1 `
    -PortfolioFile "portfolios\comprehensive_portfolio.txt" `
    -SkipExisting `
    -MaxThreads 16 `
    -BatchSize 15 `
    -Timeout 20

# Quick retail sector validation
.\analyze_portfolio_parallel_v2.ps1 `
    -PortfolioFile "portfolios\retail_quick_test.txt" `
    -SkipExisting `
    -MaxThreads 4

# Technology sector deep-dive
.\analyze_portfolio_parallel_v2.ps1 `
    -Sector technology `
    -MaxThreads 8 `
    -Quarters 16 `
    -BatchSize 10

# Preview large portfolio (no execution)
.\analyze_portfolio_parallel_v2.ps1 `
    -PortfolioFile "portfolios\comprehensive_portfolio.txt" `
    -DryRun
```

---

## 📊 Dashboard Generation

### Web Dashboard (generate_web.ps1)

Creates interactive web dashboards for portfolio visualization and analysis.

#### Basic Dashboard Generation

```powershell
# Generate standard dashboard
.\generate_web.ps1

# Generate with detailed logging
.\generate_web.ps1 -Verbose

# Skip data copy (use existing analysis)
.\generate_web.ps1 -SkipDataCopy
```

#### Dashboard Features

- **📊 Interactive Tables**: Sortable columns with real-time filtering
- **🔍 Advanced Search**: Company names, sectors, industries, and tickers
- **🎨 Visual Indicators**: Color-coded Z-Scores and risk categories
- **📱 Responsive Design**: Works on desktop, tablet, and mobile
- **💾 Self-Contained**: Single HTML file with embedded assets
- **⚡ Fast Performance**: Client-side processing for instant updates

#### Dashboard Workflow

1. **Prepare Environment**
   - Creates `web/` directory structure
   - Copies analysis data from `output/` to `web/output/`
   - Copies essential assets (logos, favicon)

2. **Generate Dashboard**
   - Calls `scripts/generate_dashboard.py`
   - Processes all analysis data
   - Creates `web/dashboard.html`

3. **Open in Browser**
   - Automatically launches dashboard in default browser
   - Dashboard works offline (file:// protocol)

#### Dashboard Parameters

| Parameter | Description | Usage |
|-----------|-------------|-------|
| `-SkipDataCopy` | Use existing web/output/ data | For faster iterations |
| `-Verbose` | Show detailed generation process | For troubleshooting |
| `-Help` | Display help information | For command reference |

---

## 📈 Understanding Results

### Output Structure

Each analyzed company creates a folder structure in `output/<TICKER>/`:

```
output/AAPL/
├── AAPL_zscore_data.json           # Core financial and Z-Score data
├── AAPL_comprehensive_report.html  # Detailed HTML report
├── AAPL_zscore_dashboard.html      # Interactive single-company dashboard
├── AAPL_analysis_summary.csv       # Summary CSV for spreadsheet use
├── charts/
│   ├── AAPL_zscore_trend.png      # Z-Score trend chart
│   ├── AAPL_stock_price.png       # Stock price chart
│   └── AAPL_dual_axis.png         # Combined Z-Score and price
└── llm_interactions/
    ├── direct_financial_analysis_*.json  # AI analysis sessions
    └── investment_recommendation_*.json  # AI recommendations
```

### Z-Score Interpretation

| Z-Score Range | Risk Category | Interpretation | Action |
|---------------|---------------|----------------|--------|
| **> 3.0** | 🟢 **Safe Zone** | Low bankruptcy risk | Consider for investment |
| **1.8 - 3.0** | 🟡 **Gray Zone** | Moderate risk | Proceed with caution |
| **< 1.8** | 🔴 **Distress Zone** | High bankruptcy risk | Avoid or exit positions |

### Report Sections

#### 1. Financial Health Summary
- Current Z-Score and risk category
- Historical trend (8+ quarters)
- Key financial ratios
- Market data and valuation metrics

#### 2. AI Investment Analysis (if enabled)
- Executive summary with investment recommendation
- Risk assessment and key factors
- Peer comparison and industry context
- Forward-looking analysis and scenarios

#### 3. Technical Charts
- Z-Score trend over time
- Stock price performance
- Dual-axis visualization combining both metrics

#### 4. Data Quality Assessment
- Data completeness scores
- Reliability indicators
- Anomaly detection results
- Source attribution

### Investment Recommendations

The AI analysis provides structured investment guidance:

| Recommendation | Description | Risk Level | Typical Z-Score Range |
|----------------|-------------|------------|---------------------|
| **Strong Buy** | High conviction opportunity | Low-Medium | > 2.5 |
| **Buy** | Favorable risk/reward | Medium | 2.0 - 3.0 |
| **Hold** | Maintain current position | Medium | 1.8 - 2.5 |
| **Sell** | Reduce exposure | High | 1.2 - 1.8 |
| **Strong Sell** | Exit immediately | Very High | < 1.2 |

---

## 🔧 Advanced Features

### Smart Caching System

The system implements intelligent caching to optimize performance:

- **48-hour TTL**: API responses cached for 2 days
- **Automatic Invalidation**: Old cache entries automatically removed
- **Performance Boost**: ~95% reduction in API calls for repeat analysis
- **Cache Management**: Manual cache clearing available

```bash
# Disable cache for fresh data
python main.py AAPL --no-cache

# Clear all cached data
python -c "from altman_zscore.cache.cache_manager import CacheManager; CacheManager().clear_cache()"
```

### Skip-Existing Functionality

Enterprise-scale optimization that intelligently skips completed analysis:

```powershell
# Skip companies with existing complete analysis
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\large_portfolio.txt" -SkipExisting
```

**Validation Criteria:**
- ✅ CSV file exists and has valid data
- ✅ JSON file exists and has required fields
- ✅ HTML report exists and is not empty
- ✅ Files were created recently (configurable threshold)

### Multi-Model Z-Score Analysis

The system automatically selects the optimal Z-Score model based on company characteristics:

| Model Type | Industry Focus | Key Features |
|------------|----------------|--------------|
| **Traditional** | General manufacturing | Classic Altman formulation |
| **Retail-Specific** | Retail/consumer goods | Novel X₆ inventory component |
| **Service-Oriented** | Technology/services | Modified asset turnover weighting |
| **Financial** | Banks/insurance | Regulatory capital considerations |
| **REIT** | Real estate investment trusts | Property-specific adjustments |

### Parallel Processing

PowerShell scripts utilize advanced parallel processing:

```powershell
# Configure threading for your system
.\analyze_portfolio_parallel_v2.ps1 `
    -PortfolioFile "portfolios\comprehensive_portfolio.txt" `
    -MaxThreads 16 `      # Use 16 parallel threads
    -BatchSize 15 `       # Process 15 companies per batch
    -Timeout 20           # 20-minute timeout per company
```

**Threading Guidelines:**
- **CPU Cores × 2**: Good starting point (e.g., 8 cores = 16 threads)
- **Memory Considerations**: Each thread uses ~500MB RAM
- **API Rate Limits**: More threads = faster completion but higher API usage

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. API Key Issues

**Problem**: "API key not configured" or authentication errors

**Solution**:
```bash
# Check config file exists
ls altman_zscore/common/config.py

# Verify API key format
python -c "from altman_zscore.common.config import FMP_API_KEY; print('OK' if FMP_API_KEY else 'Missing')"
```

#### 2. Network/Connectivity Issues

**Problem**: Connection timeouts or API unavailable

**Solution**:
```bash
# Test connectivity
python -c "import requests; print(requests.get('https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=demo').status_code)"

# Use longer timeout
python main.py AAPL --timeout 30
```

#### 3. Memory Issues (Large Portfolios)

**Problem**: Out of memory errors during large portfolio analysis

**Solution**:
```powershell
# Reduce thread count and batch size
.\analyze_portfolio_parallel_v2.ps1 `
    -PortfolioFile "portfolios\large_portfolio.txt" `
    -MaxThreads 4 `
    -BatchSize 5

# Use skip-existing to avoid reprocessing
.\analyze_portfolio_parallel_v2.ps1 `
    -PortfolioFile "portfolios\large_portfolio.txt" `
    -SkipExisting
```

#### 4. PowerShell Execution Policy

**Problem**: "Cannot be loaded because running scripts is disabled"

**Solution**:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single script
powershell -ExecutionPolicy Bypass -File .\analyze_portfolio_parallel_v2.ps1
```

#### 5. Python Module Import Issues

**Problem**: "ModuleNotFoundError" or import errors

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Verify installation
python -c "import altman_zscore; print('OK')"
```

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
# Python CLI with debug output
python main.py AAPL --verbose

# PowerShell with verbose output
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\test.txt" -Verbose
```

### Log Files

The system creates detailed log files:

- `logs/altman_zscore.log`: Main application log
- `logs/errors.log`: Error-specific events
- Individual analysis folders contain execution logs

---

## 🔑 API Configuration

### Financial Modeling Prep (FMP)

**Primary data source for financial metrics**

1. **Sign Up**: Visit https://financialmodelingprep.com/
2. **Choose Plan**:
   - **Free**: 250 requests/day
   - **Starter**: $15/month, 10,000 requests/day
   - **Professional**: $50/month, 100,000 requests/day

3. **Configure**:
   ```python
   # In altman_zscore/common/config.py
   FMP_API_KEY = "your_api_key_here"
   ```

### Azure OpenAI (Optional)

**For AI-powered analysis and recommendations**

1. **Azure Account**: Create at https://portal.azure.com/
2. **Create Resource**: Search "OpenAI" and create new resource
3. **Deploy Model**: Deploy GPT-4 or GPT-3.5-turbo
4. **Configure**:
   ```python
   # In altman_zscore/common/config.py
   AZURE_OPENAI_API_KEY = "your_key"
   AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
   AZURE_OPENAI_DEPLOYMENT = "your-deployment-name"
   ```

### API Usage Optimization

**Best Practices for Cost Management:**

1. **Use Caching**: Default 48-hour cache reduces API calls by ~95%
2. **Skip-Existing**: Avoid reprocessing completed analysis
3. **Batch Processing**: More efficient than individual requests
4. **Rate Limiting**: Built-in 0.5-second delays prevent throttling

```python
# Monitor API usage
python -c "
from altman_zscore.cache.cache_manager import CacheManager
cm = CacheManager()
stats = cm.get_cache_stats()
print(f'Cache hits: {stats.hits}, API calls saved: {stats.hits_percentage:.1f}%')
"
```

---

## 💡 Best Practices

### Portfolio Organization

1. **Use Descriptive Filenames**
   ```
   ✅ portfolios/technology_large_cap.txt
   ✅ portfolios/retail_bankruptcy_study.txt
   ❌ portfolios/portfolio1.txt
   ```

2. **Add Portfolio Metadata**
   ```text
   # Technology Portfolio - Q3 2025
   # Focus: Large cap growth stocks
   # Created: 2025-07-23
   # Last Updated: 2025-07-23
   # Expected companies: 50
   ```

3. **Group by Analysis Purpose**
   ```text
   # High-conviction picks
   AAPL
   MSFT

   # Speculative positions
   RKLB
   PLTR

   # International exposure
   ASML.AS
   TSM
   ```

### Analysis Workflow

1. **Start Small**: Test with `retail_quick_test.txt` before large portfolios
2. **Use Skip-Existing**: Leverage existing analysis to save time and API costs
3. **Monitor Resources**: Check system memory and API quotas for large runs
4. **Regular Updates**: Refresh analysis monthly or after significant market events

### Performance Optimization

1. **Threading Guidelines**:
   - Desktop: 4-8 threads
   - Server: 16-32 threads
   - Cloud: Scale based on vCPUs

2. **Memory Management**:
   - Each thread: ~500MB RAM
   - Large portfolios: Monitor with Task Manager/htop
   - Batch size: Reduce if memory constrained

3. **API Efficiency**:
   - Use skip-existing for incremental updates
   - Cache duration: 48 hours balances freshness vs. efficiency
   - Off-peak analysis: Better API response times

### Quality Assurance

1. **Validate Results**:
   ```bash
   # Check for failed analysis
   python scripts/utilities/validate_analysis.py

   # Verify data completeness
   python scripts/utilities/check_missing_data.py
   ```

2. **Review Logs**:
   ```bash
   # Check for errors
   grep -i error logs/altman_zscore.log

   # Monitor API issues
   grep -i "api" logs/altman_zscore.log | tail -20
   ```

3. **Data Backup**:
   ```bash
   # Backup analysis results
   tar -czf backup_$(date +%Y%m%d).tar.gz output/
   ```

---

## 📚 Reference

### File Extensions and Formats

| Extension | Description | Content |
|-----------|-------------|---------|
| `.json` | Core analysis data | Financial metrics, Z-Scores, metadata |
| `.csv` | Spreadsheet-compatible summary | Key metrics for Excel/Google Sheets |
| `.html` | Comprehensive reports | Interactive analysis with charts |
| `.png` | Chart images | Trend visualizations and graphs |
| `.txt` | Portfolio files | Company ticker lists with comments |

### Key Directories

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `output/` | Analysis results | Company-specific analysis folders |
| `portfolios/` | Portfolio definitions | Ticker lists and custom portfolios |
| `scripts/` | Utility scripts | Dashboard generation and tools |
| `web/` | Dashboard output | Generated web dashboard files |
| `logs/` | System logs | Application and error logs |
| `altman_zscore/` | Core package | Python modules and libraries |

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `FMP_API_KEY` | Financial data access | `"abc123xyz789"` |
| `AZURE_OPENAI_API_KEY` | AI analysis access | `"sk-..."` |
| `CACHE_DURATION_HOURS` | Cache TTL override | `"24"` |
| `MAX_RETRIES` | API retry limit | `"3"` |

### Model Selection Logic

The system automatically selects Z-Score models based on:

1. **Primary Business Activity**: Manufacturing vs. services vs. financial
2. **Revenue Composition**: >50% rule for primary business
3. **Asset Structure**: Capital intensity and asset turnover patterns
4. **Industry Classification**: SIC/NAICS codes and sector assignments
5. **Geographic Factors**: Accounting standards and regulatory environment

### Support and Community

- **Documentation**: Complete technical documentation in `/docs/`
- **Examples**: Sample portfolios and use cases in `/portfolios/`
- **Updates**: Version history and changes in `CHANGELOG.md`
- **Issues**: Report problems via GitHub Issues
- **Contributing**: See `CONTRIBUTING.md` for development guidelines

---

## 🎯 Quick Reference Commands

### Essential Commands

```bash
# Single company analysis
python main.py AAPL

# Portfolio analysis with optimization
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt" -SkipExisting

# Generate interactive dashboard
.\generate_web.ps1

# Clear cache for fresh data
python -c "from altman_zscore.cache.cache_manager import CacheManager; CacheManager().clear_cache()"
```

### Performance Commands

```powershell
# Fast incremental analysis
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\my_portfolio.txt" -SkipExisting -MaxThreads 8

# Memory-efficient large portfolio
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt" -MaxThreads 4 -BatchSize 5 -SkipExisting

# Quick validation run
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\retail_quick_test.txt" -DryRun
```

### Troubleshooting Commands

```bash
# Test API connectivity
python -c "import requests; print(requests.get('https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=demo').status_code)"

# Check system status
python scripts/utilities/system_health_check.py

# Validate analysis results
python scripts/utilities/validate_analysis.py
```

---

**End of User Manual - Version 5.0.0 PENTNILNILIUM – EMERALD Release Series**

*For technical documentation, see `/docs/` directory. For latest updates, see `CHANGELOG.md`.*
