# Bankruptcy Database Update Guide

**Quick Reference for Updating Bankruptcy Dates**

## File Location
```
altman_zscore/data/bankruptcy_dates.py
```

## Adding New Entries

### 1. Basic Format
```python
BANKRUPTCY_DATES = {
    # Retail Bankruptcies
    'TICKER': 'YYYY-MM-DD',  # Company Name
    # ... existing entries
}
```

### 2. Required Information
- **Exact Filing Date**: Use Chapter 11 filing date (not announcement)
- **Correct Ticker**: Use bankruptcy ticker (often ends in 'Q')
- **Company Name**: Add as comment for clarity

### 3. Verification Steps
1. Check SEC filings for exact date
2. Verify ticker symbol accuracy
3. Confirm data availability for analysis
4. Test new entry with `get_bankruptcy_date()`

### 4. Example Addition
```python
# Research: NewRetail Corp filed Chapter 11 on 2023-06-15
# Ticker changed from NRTL to NRTLQ during bankruptcy

BANKRUPTCY_DATES = {
    # Retail Bankruptcies
    'TOY': '2017-09-18',     # Toys"R"Us
    'NRTLQ': '2023-06-15',   # NewRetail Corp  # <-- New entry
    'SHLDQ': '2018-10-15',   # Sears Holdings
    # ... rest of entries
}
```

### 5. Testing New Entries
```python
# Test in Python console
from altman_zscore.data.bankruptcy_dates import get_bankruptcy_date
date = get_bankruptcy_date('NRTLQ')
print(f"Date: {date}")  # Should show: 2023-06-15 00:00:00
```

## Common Sources for Bankruptcy Information

- **SEC EDGAR**: Official filing documents
- **Court Records**: Bankruptcy court filings
- **Financial News**: Bloomberg, Reuters, Wall Street Journal
- **Company Press Releases**: Official announcements

## Section Organization

- **Retail Bankruptcies**: Department stores, specialty retail, e-commerce, sporting goods
- **Energy Sector**: Oil & gas, renewable energy, utilities, mining companies
- **Technology**: Software, hardware, social media, cryptocurrency, AI/ML companies
- **Airlines & Transportation**: Airlines, car rental, logistics, automotive, mobility
- **Healthcare & Pharmaceuticals**: Biotech, pharma, medical devices, healthcare services
- **Real Estate & Construction**: Real estate, construction, property management, REITs
- **Financial Services**: Fintech, lending, payments, trading, insurance
- **Media & Entertainment**: Streaming, social media, gaming, publishing, broadcasting
- **Other Notable**: Cross-industry or unique bankruptcy cases

## Recent Additions (2022-2025)

### Major Recent Bankruptcies
- **FTX Trading (2022)**: Cryptocurrency exchange collapse
- **Bed Bath & Beyond (2023)**: Retail chain closure
- **Revlon (2020)**: Beauty products company
- **Multiple Energy Companies (2020-2023)**: Oil price volatility impacts
- **Tech Company Restructurings (2022-2023)**: Post-pandemic adjustments

### Emerging Sectors
- **Cryptocurrency/Blockchain**: Exchange failures and token collapses
- **EV/Mobility**: Electric vehicle startups and traditional auto restructuring
- **Streaming/Content**: Post-pandemic content industry adjustments
- **Fintech**: Interest rate impacts on lending and payment companies

## Maintenance Schedule

- **Monthly**: Add new major bankruptcies
- **Quarterly**: Review and verify recent additions
- **Annually**: Comprehensive database review and cleanup

## Industry-Specific Considerations

### Technology Companies
- **Rapid Valuation Changes**: Tech companies can experience dramatic valuation swings
- **Restructuring vs. Bankruptcy**: Many tech companies restructure rather than file bankruptcy
- **Acquisition Speculation**: Include companies with acquisition rumors that may indicate distress
- **Data Availability**: Some tech companies have limited financial history

### Energy Sector
- **Commodity Price Sensitivity**: Energy bankruptcies often correlate with oil/gas price cycles
- **Regulatory Impact**: Environmental regulations can trigger financial distress
- **Seasonal Variations**: Consider seasonal impacts on energy company finances
- **Geographic Concentration**: Regional energy market conditions affect company viability

### Healthcare/Pharmaceuticals
- **Regulatory Approvals**: FDA approvals/rejections can trigger financial crises
- **Patent Cliff Effects**: Patent expirations can lead to revenue collapses
- **Litigation Risks**: Ongoing lawsuits (especially opioid-related) can cause bankruptcies
- **R&D Intensity**: High R&D costs can strain cash flows

### Financial Services
- **Regulatory Scrutiny**: Financial companies face stricter regulatory oversight
- **Interest Rate Sensitivity**: Rate changes significantly impact financial company profitability
- **Credit Risk**: Lending companies are particularly vulnerable to economic downturns
- **Liquidity Requirements**: Financial companies must maintain specific liquidity ratios

### Real Estate/Construction
- **Market Cyclicality**: Real estate markets are highly cyclical
- **Interest Rate Impact**: Rising rates can severely impact real estate companies
- **Geographic Concentration**: Local market conditions heavily influence company performance
- **Leverage Sensitivity**: Real estate companies typically carry high debt loads

## Data Quality Notes

### Common Issues by Industry
- **Tech Companies**: Limited historical data, frequent ticker changes
- **Energy Companies**: Commodity price volatility affects data interpretation
- **Healthcare**: Regulatory event impacts may not be captured in financial metrics
- **Financial Services**: Regulatory changes can make historical comparisons difficult
- **Real Estate**: Market timing effects can skew Z-Score calculations

### Verification Challenges
- **Private Company Data**: Some companies go private before bankruptcy
- **Ticker Changes**: Companies often change tickers during distress
- **Merger/Acquisition Activity**: Distinguish between distressed sales and strategic acquisitions
- **Restructuring vs. Bankruptcy**: Some companies restructure outside of formal bankruptcy

## Industry-Specific Z-Score Considerations

### Model Selection by Industry
- **Retail**: Use retail-specific Z-Score with inventory turnover
- **Energy**: Consider commodity price adjustments
- **Technology**: Focus on cash flow and burn rate metrics
- **Financial Services**: Use financial institution-specific models
- **Healthcare**: Consider R&D intensity and regulatory pipeline

### Threshold Adjustments
- **High-Growth Industries**: May require adjusted thresholds for normal business cycles
- **Cyclical Industries**: Consider industry-specific seasonal adjustments
- **Regulated Industries**: Account for regulatory capital requirements
- **Asset-Heavy Industries**: Adjust for depreciation and asset valuation methods
