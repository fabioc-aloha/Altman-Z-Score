# Altman Z-Score Analyzer

## Overview

A Python-based financial analysis tool that calculates the Altman Z-Score for AI and tech companies. The Altman Z-Score is a financial metric that predicts the probability of a business going bankrupt within the next two years.

This tool automatically:
- Fetches financial data from SEC EDGAR and Yahoo Finance
- Calculates Z-Score components and diagnostics
- Produces detailed analysis reports
- Tracks company performance over time

You can run the analysis manually or schedule it (e.g., via cron) to track companies' financial health over time.

## Background on Altman's Z-Score

The Altman Z-Score, developed by NYU Professor Edward Altman in 1968, is a predictive model that assesses a company's bankruptcy risk. The model combines five financial ratios into a single score that indicates a company's financial health.

### Formula and Components

Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E

Where:
- **A = Working Capital / Total Assets**: Measures liquid assets relative to company size
- **B = Retained Earnings / Total Assets**: Measures accumulated profitability over time
- **C = EBIT / Total Assets**: Measures operating efficiency and productivity
- **D = Market Value of Equity / Total Liabilities**: Measures financial leverage and market confidence
- **E = Sales / Total Assets**: Measures asset turnover and efficiency

### Diagnostic Zones

| Z-Score Range | Interpretation         |
|---------------|-----------------------|
| > 2.99        | Safe Zone             |
| 1.81 – 2.99   | Grey Zone             |
| < 1.81        | Distress Zone         |

### Model Variants and Industry Calibrations

The Altman Z-Score has evolved to support different company types and industries. This tool implements the following variants:

| Model Type         | Formula                                   | Thresholds                                 | Key Characteristics                                 |
|--------------------|-------------------------------------------|--------------------------------------------|-----------------------------------------------------|
| Original (1968)    | 1.2A + 1.4B + 3.3C + 0.6D + 1.0E          | Safe > 2.99<br>Grey 1.81-2.99<br>Distress < 1.81 | Manufacturing, market value, most validated         |
| Private (1983)     | 0.717A + 0.847B + 3.107C + 0.420D + 0.998E| Safe > 2.90<br>Grey 1.23-2.90<br>Distress < 1.23 | Private companies, book value, modified weights     |
| Service (1995)     | 6.56A + 3.26B + 6.72C + 1.05D             | Safe > 2.60<br>Grey 1.10-2.60<br>Distress < 1.10 | Service sector, no asset turnover, higher working capital |
| Emerging (1995)    | 3.25A + 6.25B + 3.25C + 1.05D             | Safe > 2.99<br>Grey 1.81-2.99<br>Distress < 1.81 | Emerging markets, higher profitability, conservative |

#### Tech Company Adaptations

The tool provides specialized handling for tech companies based on their subsector and growth stage. While using the base models above, it includes additional analysis and adjustments:

| Company Stage    | Model Used | Additional Considerations                                    |
|-----------------|------------|-------------------------------------------------------------|
| Tech (Hardware) | Original   | Traditional metrics with inventory and asset focus           |
| Tech (Software) | Service    | Emphasis on intangible assets and R&D                       |
| SaaS           | Service    | Focus on recurring revenue and customer metrics              |
| AI/ML (Early)  | Service    | R&D intensity and pre-revenue metrics                       |
| AI/ML (Growth) | Service    | Unit economics and scale metrics                            |
| AI/ML (Mature) | Service    | Profitability and infrastructure efficiency                 |

**Key Tech Company Considerations:**
- High R&D intensity and growth investments may affect traditional ratios
- Intangible assets (IP, data, algorithms) require special consideration
- Pre-revenue status is common in early-stage tech
- Asset-light business models may skew traditional metrics

## Features

1. **Automated Analysis Pipeline**
   - Fetches financial data from SEC EDGAR
   - Retrieves market data from Yahoo Finance
   - Performs company classification
   - Selects appropriate Z-Score model
   - Calculates and validates results

2. **Intelligent Model Selection**
   - Automatic company classification
   - Context-aware model choice
   - Tech sector specialization
   - Validation warnings system

3. **Comprehensive Analysis**
   - Z-Score components calculation
   - Industry benchmarking
   - Tech sector adjustments
   - Peer group comparison
   - Growth stage consideration

4. **Data Quality Assurance**
   - Ratio sanity checks
   - Cross-source validation
   - Missing data handling
   - Outlier detection

5. **Results Presentation**
   - Detailed CSV reports
   - Formatted console output
   - Industry context
   - Diagnostic warnings
   - Performance metrics

## Project Documentation

This project maintains several key documentation files, each serving a specific purpose:

### Core Documentation
- **README.md** (this file)
  - Project overview and background
  - Feature documentation
  - Setup and usage instructions
  - Basic concepts and terminology

- **APIS.md**
  - Detailed API specifications
  - Rate limits and authentication
  - Response formats
  - Error handling

### Development Documentation
- **DECISIONS.md**
  - Architectural decisions record (ADR)
  - Technical standards
  - Core technology choices
  - API and code standards
  - Testing requirements

- **LEARNINGS.md**
  - Implementation insights
  - Solutions to technical challenges
  - Performance optimizations
  - Current challenges and next steps

- **TODO.md**
  - Current project priorities
  - Active sprint tasks
  - Implementation status
  - Completion tracking

### Planning Documentation
- **PLAN.md**
  - Detailed implementation plans
  - Risk assessments
  - Rollback procedures
  - Success criteria

Each document is maintained with a specific focus to avoid duplication and ensure clarity:
- DECISIONS.md answers "What and Why"
- LEARNINGS.md covers "How and What's Next"
- TODO.md tracks "What's Pending"
- PLAN.md details "How to Implement"

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Altman-Z-Score.git
   cd Altman-Z-Score
   ```

2. **(Recommended) Create and activate a Python virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the package and dependencies:**
   ```bash
   pip install -e .
   ```

> **Note:** This project is fully compatible with GitHub Codespaces. Codespaces users can skip manual environment setup—dependencies are installed automatically on first open.

For troubleshooting or advanced setup, see the [APIS.md](APIS.md) and [DECISIONS.md] documentation.

## Configuration

1. Create a `.env` file with your SEC EDGAR API credentials:
```env
SEC_EDGAR_USER_AGENT=your_name your_email@domain.com
```

2. (Optional) Configure API cache settings in `.env`:
```env
FINANCIAL_CACHE_TTL_DAYS=30  # Cache duration for financial data
CACHE_DIR=.cache            # Cache directory location
```

3. (Optional) Modify the portfolios in `src/altman_zscore/config.py`:
   - Use predefined portfolios or create your own
   - Each portfolio includes tickers and analysis settings
   - CIK numbers are automatically looked up using SEC EDGAR
   - Changes take effect immediately

See [APIS.md](APIS.md) for detailed API configuration and usage guidelines.

### Portfolio System

Portfolios are defined in `portfolio.py` as lists of stock tickers grouped by theme or sector. CIK numbers are automatically looked up and validated for each ticker using the SEC EDGAR API.

- You can add or remove tickers from any portfolio by editing `portfolio.py`.
- To create a new portfolio, add a new entry to the `PORTFOLIOS` dictionary with a name, description, and list of tickers.
- All portfolio changes take effect immediately—no manual CIK management is required.
- Portfolio validation and CIK caching are handled automatically.

Example portfolio definition:
```python
PORTFOLIO: list[str] = [
    # Technology/Software Companies (Service Model)
    "MSFT",   # Microsoft Corporation
    "ORCL",   # Oracle Corporation
    "CRM",    # Salesforce, Inc.
    "ADBE",   # Adobe Inc.
    "NOW",    # ServiceNow, Inc.
    "SNOW",   # Snowflake Inc.
    
    # Manufacturing Companies (Original Model)
    "F",      # Ford Motor Company
    "GM",     # General Motors Company
    "CAT",    # Caterpillar Inc.
    "BA",     # Boeing Company
    "MMM",    # 3M Company
    "HON",    # Honeywell International Inc.
    
    # Mixed Hardware/Software (Original/Service Model)
    "AAPL",   # Apple Inc.
    "IBM",    # International Business Machines
    "NVDA",   # NVIDIA Corporation
    "AMD",    # Advanced Micro Devices
    
    # Emerging Market ADRs (EM Model)
    "BABA",   # Alibaba Group Holding Ltd.
    "TSM",    # Taiwan Semiconductor Manufacturing
    "TCEHY",  # Tencent Holdings Ltd.
    "NIO",    # NIO Inc.
    "PDD",    # PDD Holdings Inc.
    
    # Recent IPOs/SPACs (Private Model)
    "LCID",   # Lucid Group Inc.
    "AI",     # C3.ai, Inc.
    "PLTR",   # Palantir Technologies Inc.
    
    # Pure Service Companies (Service Model)
    "UBER",   # Uber Technologies Inc.
    "ABNB",   # Airbnb, Inc.
    "DIS",    # The Walt Disney Company
    "NFLX",   # Netflix, Inc.
    "MA"      # Mastercard Incorporated
    
    # Distressed/Turnaround Companies (Various Models)
    "RIVN",   # Rivian Automotive - EV maker with cash burn concerns
    "MAT",    # Mattel Inc. - Historical restructuring case
    "BBBY",   # Bed Bath & Beyond - Recent bankruptcy case
    "AMC",    # AMC Entertainment - Theater chain restructuring
    "CVNA",   # Carvana - Car retailer with debt concerns
    "HOOD",   # Robinhood - Fintech with regulatory challenges
    "BYND",   # Beyond Meat - Food tech with market challenges
    "WISH",   # ContextLogic (Wish) - E-commerce turnaround attempt
    "VYGR",   # Voyager Digital - Crypto bankruptcy case
    "PRTY"    # Party City - Retail restructuring case
]
```

See comments in `portfolio.py` for more details and customization options.

## Usage

1. Run the analysis using the bootstrap script:
```bash
./analyze.py
# or
python analyze.py
```

2. Results will be saved in:
   - CSV format: `zscore_analysis_DATE.csv`
   - Console output with summary

The script will:
- Set up the environment automatically
- Prompt you to clear the cache if needed
- Show progress during analysis
- Display a summary of results

## Project Structure

```
src/altman_zscore/                # Main package directory
├── __init__.py                  # Package initialization
├── analysis_strategy.py         # Analysis strategy definitions
├── calibration.py              # Model calibration utilities
├── cik_lookup.py               # CIK number lookup functionality
├── cik_mapping.py              # CIK to ticker mapping
├── cik_validation.py           # CIK validation utilities
├── company_profile.py          # Company classification
├── compute_zscore.py           # Core Z-Score calculations
├── config.py                   # Configuration and constants
├── data_validation.py          # Data validation utilities
├── fetch_financials.py         # SEC EDGAR data fetching
├── fetch_prices.py             # Market data retrieval
├── industry_classifier.py      # Industry classification
├── industry_comparison.py      # Industry comparison logic
├── main.py                     # Main execution script
├── models.py                   # Z-Score model definitions
├── api/                        # API integration modules
│   ├── base_fetcher.py        # Base data fetcher
│   ├── fetcher_factory.py     # Data fetcher creation
│   ├── rate_limiter.py        # API rate limiting
│   ├── request_manager.py     # Request handling
│   ├── sec_client.py          # SEC EDGAR client
│   └── yahoo_client.py        # Yahoo Finance client
├── models/                     # Model implementation
│   ├── base.py               # Base model class
│   ├── factory.py            # Model factory
│   └── original.py           # Original Z-Score model
└── utils/                      # Utility functions
    ├── financial_metrics.py   # Financial calculations
    └── time_series.py        # Time series analysis

tests/                         # Test directory
└── test_zscore.py            # Unit tests
```

See [APIS.md](APIS.md) for detailed API documentation.

## Development

See our documentation for development guidelines:
- [Architectural Decisions](DECISIONS.md)
- [Implementation Learnings](LEARNINGS.md)
- [Todo List](TODO.md)
- [API Documentation](APIS.md) - Detailed specifications for SEC EDGAR and Yahoo Finance APIs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on Edward Altman's Z-Score model
- Uses data from SEC EDGAR and Yahoo Finance
- Inspired by the need for automated financial health analysis

## References

- Altman, E. I. (1968). "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy."
- [SEC EDGAR](https://www.sec.gov/edgar)
- [Yahoo Finance](https://finance.yahoo.com/)

This app:

Fetches and parses each company’s Q1 2025 filing from EDGAR.

Retrieves share counts and price data via yfinance.

Computes the A–E components, Z-Score, and diagnostic.

Calculates stock price performance over the same period.

Outputs a consolidated Markdown table of results.

You can schedule main.py via cron or integrate with the monthly automation task created earlier.

## Environment Variables

The following environment variables can be set in your `.env` file:

```env
# Required - Your SEC EDGAR API credentials (email required by SEC)
SEC_EDGAR_USER_AGENT=your_name your_email@domain.com
# Alternative name for the same setting
SEC_USER_AGENT=your_name your_email@domain.com

# Optional - Analysis configuration
DEFAULT_PORTFOLIO=genai  # Which portfolio to analyze by default
```

## Implementation Details

### Model Selection

The tool automatically selects and calibrates models based on company characteristics:

```
ZScoreModel
├── ORIGINAL        # Public manufacturing companies
├── PRIVATE        # Private manufacturing companies
├── SERVICE        # Non-manufacturing/service companies
└── EM (Emerging)  # Companies in emerging markets
```

Model selection logic follows this priority:

1. Market Category:
   - Emerging markets: Uses EM model regardless of sector
   - Developed markets: Proceeds to sector analysis

2. Tech/AI Companies:
   - Hardware/Mixed Tech: Uses ORIGINAL model (significant physical assets)
   - Software/Service Tech: Uses SERVICE model (intangible value and R&D focus)

3. Manufacturing Companies:
   - Public: Uses ORIGINAL model (most validated)
   - Private: Uses PRIVATE model (book value based)

4. Service Companies:
   - Uses SERVICE model (excludes asset turnover)

The selection process includes automatic validation with warnings for:
- Model appropriateness for company type
- Extreme ratio values
- Tech-specific metrics
- Growth stage considerations

### Analysis Features

The tool provides comprehensive analysis capabilities:

1. **Industry Comparison**
   - Peer group benchmarking
   - Subsector trend analysis
   - Performance percentiles
   - Context-aware interpretation

2. **Tech-Specific Analysis**
   - R&D intensity metrics
   - Growth stage adjustments
   - Unit economics validation
   - Industry-specific warnings

3. **Data Quality**
   - Ratio sanity checks
   - Market value validation
   - Outlier detection
   - Cross-source verification

Example for AI/Tech Company Analysis:
```python
from altman_zscore import classify_company, compute_zscore

# Classify the company
profile = classify_company("0001318605", "TSLA")  # Tesla example

# Get model recommendation
model, reason = determine_zscore_model(profile)
print(f"Using model: {model.value}")
print(f"Reason: {reason}")

# Calculate Z-score with validation
z_score = compute_zscore(metrics, model)
warnings = validate_model_selection(model, metrics, profile)

for warning in warnings:
    print(f"Warning: {warning}")
```

### Advanced Tech Company Analysis

The tool provides specialized analysis capabilities for technology companies, built into the `IndustryComparison` class:

1. **Industry Comparison**
   - Computes industry median scores
   - Calculates percentile rankings
   - Tracks subsector performance
   - Provides peer benchmarking

2. **Tech Subsector Analysis**
   - Hardware/Mixed Tech
   - Software/Services
   - SaaS/Enterprise
   - AI/Machine Learning
   - Other Tech Categories

3. **R&D Investment Analysis**
   - Calculates R&D intensity (R&D/Revenue ratio)
   - Provides intensity-based insights:
     * High (>15%): Strong innovation focus
     * Moderate (5-15%): Balanced investment
     * Low (<5%): Potential underinvestment

4. **Performance Analytics**
   - Industry median comparison
   - Subsector percentile ranking
   - Peer group analysis
   - Growth stage consideration

Example Tech Company Analysis:
```python
from altman_zscore import classify_company, compute_zscore, IndustryComparison

# Initialize industry comparison
industry_comp = IndustryComparison()

# Classify company and get tech profile
profile = classify_company("0001318605", "TSLA")  # Tesla example

# Calculate Z-score with validation
model, reason = determine_zscore_model(profile)
z_score = compute_zscore(metrics, model)

# Get insights
industry_metrics = industry_comp.get_industry_metrics(profile, z_score.z_score)
tech_insights = industry_comp.get_tech_specific_insights(profile, z_score.z_score)

# Analysis results
print(f"Industry Percentile: {industry_metrics['industry_percentile']:.1%}")
print(f"Subsector Performance: {industry_metrics.get('subsector_median', 'N/A')}")
```

### Interpreting Results

The tool provides context-aware interpretation of Z-Score results based on company characteristics:

#### Core Metrics

| Component          | Interpretation Guidelines                                      |
|-------------------|-------------------------------------------------------------|
| Working Capital   | Measures liquidity and short-term stability                  |
| Retained Earnings | Indicates cumulative profitability and reinvestment         |
| EBIT             | Shows operating efficiency and core business strength        |
| Market Value     | Reflects market confidence and financial leverage           |
| Sales            | Measures asset utilization (not used in Service model)      |

#### Industry-Specific Context

| Company Type       | Key Considerations                                           |
|-------------------|-------------------------------------------------------------|
| Tech/Software     | - R&D investment levels<br>- Intangible asset value<br>- Growth vs. profitability balance |
| Manufacturing     | - Working capital efficiency<br>- Asset utilization<br>- Operating leverage |
| Services          | - Revenue stability<br>- Operating margins<br>- Capital structure |
| Emerging Markets  | - Market volatility<br>- Currency effects<br>- Country risk factors |

#### Validation Warnings

The tool includes automatic validation that may generate warnings for:

1. **Model Selection Issues**
   - Using Original model for non-public company
   - Using Service model with high asset turnover
   - Emerging market company not using EM model

2. **Tech-Specific Concerns**
   - Low market value relative to assets
   - Unusual asset turnover for tech company
   - R&D investment misalignment

3. **Data Quality Issues**
   - Extreme ratio values
   - Missing critical metrics
   - Inconsistent financial data

### Diagnostic Recommendations

1. **Early-Stage Tech**
   - Prioritize growth metrics
   - Monitor cash runway
   - Track unit economics
   - Consider funding needs

2. **Growth-Stage Tech**
   - Balance growth and efficiency
   - Focus on scaling operations
   - Monitor competitive position
   - Track market expansion

3. **Mature Tech**
   - Emphasize profitability
   - Watch market share
   - Monitor innovation metrics
   - Track industry position

4. **Special Situations**
   - Pre-revenue: Focus on burn rate and development milestones
   - Hardware/Software Hybrid: Use blended thresholds
   - Platform Companies: Consider network effects

# OLD Directory

This folder contains the previous version of the Altman Z-Score project, including all code, documentation, and scripts prior to the 2025 refactor. It is preserved for reference, rollback, and migration of useful components or learnings.

## Contents
- **analyze.py, portfolio.py**: Previous main scripts for analysis and portfolio processing.
- **APIS.md**: Documentation of APIs and data sources used in the old codebase.
- **debug_xbrl.py**: Utility for debugging XBRL data extraction.
- **DECISIONS.md**: Architectural and technical decisions from the previous version.
- **LEARNINGS.md**: Key learnings and technical notes from the old codebase.
- **OneStockAnalysis.md**: Early concept and design notes for single-stock analysis.
- **PLAN.md, TODO.md, README.md**: Project planning, task tracking, and documentation from the old version.
- **src/**: All previous source code modules and packages.
- **tests/**: Previous test suite.

## Usage
- **Reference Only:** Do not modify files in this folder. Use them for migration, rollback, or historical context.
- **Migration:** If a feature or function is needed in the new codebase, migrate and refactor it in the new `src/` directory.
- **Rollback:** In case of critical issues with the new codebase, the old version can be restored from this folder.

---
For the current project plan, see the root `PLAN.md`. For new code, see the root `src/` directory.