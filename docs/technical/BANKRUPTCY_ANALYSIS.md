# Bankruptcy Analysis Framework

**Implementation Date:** July 6, 2025  
**Version:** 1.0

## Overview

The Bankruptcy Analysis Framework is a major enhancement to the Altman Z-Score system that enables comprehensive analysis of companies' financial health leading up to bankruptcy. By examining Z-Score progression and market data in the quarters before bankruptcy, this framework provides valuable insights into the predictive capabilities of different Z-Score models and helps identify early warning signs of financial distress.

## Key Features

- **Pre-Bankruptcy Z-Score Progression**: Calculate and visualize Z-Scores for multiple quarters leading up to bankruptcy.
- **Market Data Correlation**: Track stock price, market cap, and other market metrics alongside Z-Score deterioration.
- **Specialized Reporting**: Generate comprehensive reports with bankruptcy-specific analysis sections.
- **Visual Trend Analysis**: Create dashboards with clear visualization of financial decline patterns.
- **Validation Framework**: Test different Z-Score models against known bankruptcy outcomes.
- **Batch Processing**: Analyze multiple bankrupt companies to establish pattern recognition.

## Implementation Details

The bankruptcy analysis functionality is fully integrated across the pipeline:

### 1. Bankruptcy Dates Database

Located in `altman_zscore/data/bankruptcy_dates.py`, this module maintains:

- Database of historical bankruptcy filings with exact dates
- Categorized by industry sector (retail, energy, etc.)
- Utility functions to retrieve and check bankruptcy dates

### 2. Main Pipeline Integration

In `altman_zscore/main_pipeline.py`:

- Added `bankruptcy_analysis` and `pre_bankruptcy_quarters` parameters to `analyze_ticker()`
- Implemented bankruptcy date lookup and end date filtering
- Created `run_bankruptcy_analysis()` method for batch processing all bankrupt companies
- Enhanced progress tracking for bankruptcy analysis mode

### 3. Data Processing Enhancements

In `altman_zscore/layers/data_fetch/data_merger.py`:

- Modified `merge_financial_data()` to support end date filtering
- Updated `_fetch_multiple_quarters_fmp_data()` to filter quarters before bankruptcy
- Enhanced `_fetch_yahoo_market_data()` to retrieve historical market data for each quarter
- Added metadata tagging for bankruptcy analysis data

### 4. Report Generation

In `altman_zscore/layers/output_generation/report_generator.py`:

- Added bankruptcy information section to reports
- Created pre-bankruptcy Z-Score progression tables
- Enhanced template with bankruptcy-specific styling

### 5. Dashboard Visualization

In `altman_zscore/layers/output_generation/charts/trend_analysis.py`:

- Added bankruptcy date markers on Z-Score trend charts
- Enhanced trend visualization for pre-bankruptcy periods
- Added annotations for key bankruptcy events

## Usage

To analyze a specific bankrupt company:

```python
from altman_zscore.main_pipeline import AltmanZScorePipeline

pipeline = AltmanZScorePipeline()
result = await pipeline.analyze_ticker(
    "SHLDQ",  # Sears Holdings
    bankruptcy_analysis=True,
    pre_bankruptcy_quarters=3
)
```

To analyze all bankrupt companies in the database:

```python
results = await pipeline.run_bankruptcy_analysis(
    pre_bankruptcy_quarters=3,
    generate_charts=True,
    generate_reports=True
)
```

## Analytical Benefits

This framework provides several key analytical benefits:

1. **Model Validation**: Test how accurately different Z-Score models predict bankruptcy.
2. **Early Warning Detection**: Identify how many quarters in advance Z-Scores begin to decline.
3. **Threshold Calibration**: Determine optimal threshold values for distress prediction.
4. **Cross-Industry Comparison**: Compare bankruptcy patterns across different industry sectors.
5. **Market Correlation**: Analyze how market data correlates with Z-Score deterioration.

## Future Enhancements

Planned enhancements for the bankruptcy analysis framework:

1. Machine learning model for predicting time-to-bankruptcy based on Z-Score patterns
2. Integration with additional failure prediction models (Springate, Zmijewski, etc.)
3. Enhanced SEC EDGAR integration for delisted companies
4. Sector-specific bankruptcy warning patterns
5. Expanded bankruptcy database with international companies

## Implementation Notes

- Bankruptcy analysis can be computationally intensive when analyzing many quarters
- Historical market data may have gaps for long-delisted companies
- Recommend using enhanced FMP accounts for comprehensive bankruptcy analysis
