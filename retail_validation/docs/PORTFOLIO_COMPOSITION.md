# Retail Z-Score Model Validation Portfolio Composition
**Version 1.0 | July 2025**

## Portfolio Overview

This document details the composition of the retail backtest portfolio used for validating the novel retail Z-Score model. The portfolio has been carefully curated to represent the full spectrum of retail financial health scenarios, enabling comprehensive testing of the model's predictive capabilities.

## Portfolio Structure

The backtest portfolio is structured into five distinct categories designed to test specific model capabilities:

1. **Failed/Bankrupt Retailers**
2. **Retailers in Distress**
3. **Recovery/Turnaround Stories**
4. **Stable/Strong Retailers**
5. **Seasonal/Cyclical Retailers**

## Company Categories in Detail

### 1. Failed/Bankrupt Retailers

This category includes companies that have filed for bankruptcy protection, enabling testing of the model's ability to predict retail failure. These companies represent the critical "true positive" test cases.

| Ticker | Company | Bankruptcy Date | Notes |
|--------|---------|----------------|-------|
| TOY | Toys"R"Us | 2017-09-18 | Inventory management challenges |
| SHLDQ | Sears Holdings | 2018-10-15 | Legacy retailer failure |
| JCPNQ | JC Penney | 2020-05-15 | Department store distress |
| NMRCQ | Neiman Marcus | 2020-05-07 | Luxury retail bankruptcy |
| BRKSQ | Brooks Brothers | 2020-07-08 | Apparel retailer |
| PIRRQ | Pier 1 Imports | 2020-05-18 | Home goods retailer |
| BONTQ | Bon-Ton Stores | 2018-02-04 | Regional department store |
| RSHCQ | RadioShack | 2015-02-05 | Electronics retailer |
| TSAQ | Sports Authority | 2016-05-18 | Sports retailer |
| PSDSQ | Payless ShoeSource | 2017-04-04 | Footwear retailer |
| F21Q | Forever 21 | 2019-09-29 | Fast fashion retailer |
| GYMQ | Gymboree | 2017-06-11 | Children's apparel |

*Note: Historical financial data for bankrupt companies may not be readily available through current API providers. For comprehensive historical testing, specialized historical data sources may be required.*

### 2. Retailers in Distress

This category includes currently operating retailers showing signs of financial distress, providing test cases for the model's early warning capabilities.

| Ticker | Company | Notes |
|--------|---------|-------|
| BBBY | Bed Bath & Beyond | Home goods retailer with declining performance |
| PRTY | Party City | Specialty retailer with debt challenges |
| GME | GameStop | Physical game retailer with digital disruption |
| EXPR | Express | Apparel retailer with mall exposure |
| BIG | Big Lots | Discount retailer with margin pressure |
| M | Macy's | Department store with adaptation challenges |
| JWN | Nordstrom | Upscale department store |
| DDS | Dillard's | Mid-tier department store |
| BBWI | Bath & Body Works | Specialty retailer |
| AEO | American Eagle | Youth apparel retailer |
| ANF | Abercrombie & Fitch | Apparel retailer |
| URBN | Urban Outfitters | Lifestyle retailer |
| GPS | Gap | Apparel retailer with multiple brands |
| FL | Foot Locker | Footwear retailer |

### 3. Recovery/Turnaround Stories

This category includes retailers that have previously faced distress but implemented successful turnaround strategies, testing the model's ability to track improvement.

| Ticker | Company | Notes |
|--------|---------|-------|
| BBY | Best Buy | Electronics retailer that overcame e-commerce disruption |
| TGT | Target | General merchandise retailer with successful reinvention |
| DKS | Dick's Sporting Goods | Sports retailer with omnichannel success |
| BURL | Burlington Stores | Off-price retailer with growth |
| TJX | TJX Companies | Off-price retail leader |
| AZO | AutoZone | Auto parts retailer with consistent performance |
| ORLY | O'Reilly Auto | Auto parts retailer |
| AAP | Advance Auto Parts | Auto parts retailer |
| LOW | Lowe's | Home improvement retailer |

### 4. Stable/Strong Retailers

This category includes financially robust retailers, providing "true negative" test cases to ensure the model correctly identifies healthy companies.

| Ticker | Company | Notes |
|--------|---------|-------|
| AMZN | Amazon | E-commerce leader with diverse operations |
| COST | Costco | Warehouse club with subscription model |
| WMT | Walmart | Leading general merchandise retailer |
| BJ | BJ's Wholesale | Warehouse club |
| HD | Home Depot | Home improvement leader |
| DG | Dollar General | Discount retailer with rural focus |
| DLTR | Dollar Tree | Value retailer |
| SHW | Sherwin-Williams | Specialty retailer with professional segment |

### 5. Seasonal/Cyclical Retailers

This category includes retailers with pronounced seasonal inventory patterns, testing the model's ability to handle seasonal fluctuations appropriately.

| Ticker | Company | Seasonal Pattern |
|--------|---------|-----------------|
| SPIR | Spirit Halloween | Extreme seasonality (Halloween) |
| JWN | Nordstrom | Holiday-driven department store |
| ROST | Ross Stores | Off-price with seasonal inventory |
| TSCO | Tractor Supply | Rural retailer with seasonal demand |
| BGFV | Big 5 Sporting Goods | Sporting goods with seasonal patterns |
| SBH | Sally Beauty | Beauty retailer with moderate seasonality |
| POOL | Pool Corporation | Extreme seasonality (summer) |
| BBW | Build-A-Bear Workshop | Gift retailer with holiday concentration |
| AM | American Greetings | Card retailer with holiday spikes |
| PRTY | Party City | Party supplies with holiday/seasonal focus |

## Portfolio Usage Guidelines

### Portfolio Location

```
portfolios/retail_backtest_portfolio.txt
```

### Portfolio Format

```
# Category header (comments)
TICKER  # Optional inline comment
```

### Testing Methodology

For effective model validation:

1. **Complete Testing**: Process all companies for comprehensive validation
2. **Category-Specific Testing**: Test individual categories to focus on specific model aspects:
   - `failed` - Test bankruptcy prediction
   - `distressed` - Test early warning
   - `recovery` - Test model discrimination
   - `stable` - Test false positive rate
   - `seasonal` - Test seasonal pattern handling

3. **Time Period Testing**: Use historical data when available:
   - Pre-bankruptcy (2-3 years prior) for failed companies
   - Multi-year trends for recovery stories
   - Quarterly data for seasonal retailers

## Portfolio Maintenance

To keep the portfolio current and effective:

1. **Annual Review**: Evaluate company categories annually
2. **New Bankruptcies**: Add significant retail bankruptcies
3. **Category Transitions**: Move companies between categories as financial health changes
4. **Data Availability**: Confirm financial data availability for all tickers
5. **Industry Coverage**: Ensure representation across retail subsectors

## Academic Applications

This portfolio is designed to support academic validation of the retail Z-Score model:

1. **Empirical Testing**: Provides diverse test cases for empirical validation
2. **Literature Standards**: Aligns with academic bankruptcy prediction literature
3. **Publication Support**: Enables peer-review ready results

---

*This portfolio composition is optimized for comprehensive testing of the novel retail Z-Score model across the full spectrum of retail financial health scenarios.*
