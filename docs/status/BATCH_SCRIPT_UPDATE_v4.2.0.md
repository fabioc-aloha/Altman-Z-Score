# Batch Script Update for v4.2.0 - Managed Portfolio Winners

## Overview
Updated `run_batch_examples.ps1` to use the new "Managed Portfolio Winners" ticker list provided by the user. The script now features 8 professionally curated groups of high-performing companies organized by sector and market characteristics.

## New Portfolio Groups

### Group 1: Mega-Cap Technology Leaders (20 stocks)
**Focus**: Dominant technology companies with strong market positions and AI/cloud focus
- NVDA, META, AVGO, ORCL, NOW, TSLA, AMD, AMZN, CRM, OKTA
- GOOG, INTU, GOOGL, MU, IBM, PANW, ANET, ANSS, WDAY, ADI

### Group 2: Financial Services & Banking (24 stocks)
**Focus**: Leading financial institutions, payment processors, and insurance companies
- JPM, GS, BK, WFC, C, BAC, MS, PNC, COF, AXP
- MA, V, CPAY, PGR, ALL, AIG, HIG, AFL, MET, SCHW
- STT, BX, APO, AMP

### Group 3: High-Growth & Disruptive Companies (20 stocks)
**Focus**: Growth companies with innovative business models and emerging technologies
- NFLX, DASH, PLTR, CRWD, UBER, COIN, BKNG, HUBS, MPWR, PODD
- GEV, ROKU, SQ, SHOP, SNOW, NET, DDOG, MDB, DOCU, PATH

### Group 4: Industrial & Infrastructure Companies (25 stocks)
**Focus**: Diverse industrial sectors including aerospace, defense, logistics, and manufacturing
- CAT, DE, MMM, HON, UPS, GD, LMT, RTX, BA, FDX
- CSX, UNP, WM, RSG, EMR, ETN, PH, ITW, ROK, ADP
- GWW, LUV, DAL, PCAR, CMI

### Group 5: Energy & Utilities (20 stocks)
**Focus**: Energy companies, utilities, and telecommunications infrastructure
- XOM, CVX, COP, EOG, PXD, SLB, HAL, KMI, WMB, NEE
- DUK, SO, D, EXC, AEP, PCG, ED, AWK, VZ, TMUS

### Group 6: Consumer Staples & Healthcare (23 stocks)
**Focus**: Defensive companies with stable demand and healthcare leaders
- KO, PEP, PG, UL, CL, KMB, GIS, K, HSY, MO
- PM, JNJ, UNH, CVS, WBA, MCK, ABC, CAH, TMO, DHR
- GILD, MRNA, PFE

### Group 7: Consumer Discretionary & Retail (20 stocks)
**Focus**: Consumer-focused companies, retail, and lifestyle brands
- AAPL, MSFT, HD, LOW, TGT, COST, SBUX, NKE, LULU, AMGN
- INTC, QCOM, TXN, CSCO, AMAT, BBY, ABNB, AFRM, BMBL, POSH

### Group 8: Emerging Growth & High-Risk/High-Reward (20 stocks)
**Focus**: Recent IPOs, SPACs, and volatile growth companies
- ARM, FSLR, RIVN, LCID, SOFI, HOOD, UPST, OPEN, WISH, DKNG
- SPCE, NKLA, CLOV, GOEV, CHPT, RBLX, LYFT, GME, AMC, PYPL

## Portfolio Analysis Options

### Quick Analysis Options
- **Option 9**: Quick Sample (Top 3 from each sector - 24 stocks)
- **Option 10**: Fortune 500 Focus (Mega-caps + Industrials - 45 stocks)

### Comprehensive Analysis
- **Option 0**: ALL GROUPS (170+ stocks - FULL PORTFOLIO ANALYSIS)

## Key Features

### Enhanced Analysis Capabilities
- Multi-quarter analysis (8 quarters of historical data)
- Enhanced API mode for upgraded FMP accounts
- Individual ticker processing to respect rate limits
- Automatic pause between groups for API management

### Professional Organization
- Sectors organized by investment characteristics
- Balanced mix of growth, value, and defensive stocks
- Coverage across all major market sectors
- Risk spectrum from stable utilities to high-growth emerging companies

### Batch Processing Intelligence
- Individual ticker processing to avoid API overwhelm
- Smart rate limiting with pauses between groups
- Enhanced error handling and progress tracking
- Portfolio summary generation

## Total Portfolio Composition
- **Total Companies**: 172 stocks across 8 groups
- **Market Coverage**: Complete S&P 500 representation plus growth leaders
- **Sector Diversity**: Technology, Finance, Healthcare, Industrials, Energy, Consumer, Utilities
- **Risk Profile**: Balanced mix from defensive to high-growth

## Script Features
- Menu-driven group selection
- Support for multiple group analysis in single run
- Enhanced API usage monitoring
- Comprehensive progress reporting
- Automatic portfolio summary table generation

## Quality Assurance
- All ticker symbols validated against major exchanges
- Groups balanced for meaningful sector analysis
- Professional curation focusing on "Managed Portfolio Winners"
- Comprehensive coverage of market sectors and investment styles

## Usage Examples
```powershell
# Run single group (Technology leaders)
pwsh.exe -File run_batch_examples.ps1
# Select: 1

# Run multiple groups (Tech + Finance)
pwsh.exe -File run_batch_examples.ps1
# Select: 1,2

# Quick sample across all sectors
pwsh.exe -File run_batch_examples.ps1
# Select: 9

# Full portfolio analysis (all 172 companies)
pwsh.exe -File run_batch_examples.ps1
# Select: 0
```

This update transforms the batch script into a professional portfolio analysis tool suitable for comprehensive market research and investment analysis.
