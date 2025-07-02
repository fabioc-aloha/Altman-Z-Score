# Retail Backtest Portfolio Guide

This document provides guidance on using the `retail_backtest_portfolio.txt` file for validating the retail Z-Score model, with special emphasis on handling delisted companies.

## Portfolio Structure

The retail backtest portfolio contains approximately 75 carefully selected retail companies across 5 categories:

1. **Failed/Bankrupt Retailers (20)**: Companies that have declared bankruptcy
2. **Retailers in Distress (15)**: Currently operating companies showing distress signals
3. **Recovery/Turnaround Stories (10)**: Companies that successfully navigated challenges
4. **Stable/Strong Retailers (15)**: Benchmark companies with strong financials
5. **Seasonal/Cyclical Retailers (15)**: Companies with pronounced seasonal patterns

## Handling Delisted Companies

Many of the companies in Category 1 (Failed/Bankrupt Retailers) are delisted and no longer trade on public exchanges. Their ticker symbols typically end with Q (e.g., NMRCQ, JCPNQ) to indicate bankruptcy status.

### Challenges with Delisted Companies

When attempting to analyze these companies with standard financial APIs, you will encounter errors like:

```
ERROR - Failed to fetch data for NMRCQ: Invalid ticker symbol 'NMRCQ' - not found in financial databases
```

This occurs because these companies are no longer traded, and current financial data APIs don't maintain comprehensive historical data for delisted securities.

### Solutions for Validation

1. **Focus on Available Companies**: The portfolio includes many currently trading companies in distress (Category 2) that provide valuable validation opportunities without requiring historical bankruptcy data.

2. **Use Configuration Options**: The validation framework includes configuration options for handling delisted companies:

   ```powershell
   # Skip unavailable tickers and continue
   .\retail_validation\scripts\run_retail_validation.ps1 -AvailableOnly
   
   # Use sample bankruptcy data for testing
   .\retail_validation\scripts\run_retail_validation.ps1 -SampleBankruptcy
   
   # Use previous validation results for reference
   .\retail_validation\scripts\run_retail_validation.ps1 -UseHistoricalResults
   ```

3. **Modify the Portfolio**: You can edit the portfolio file to comment out delisted companies:

   ```
   # JCPNQ  # Commented out - delisted company
   ```

## Best Practices for Validation

### For Academic Validation

When validating for academic purposes:

1. **Document Data Limitations**: Clearly note which companies could not be analyzed due to data availability
2. **Use External References**: Cite published studies that analyze these companies before delisting
3. **Consider Historical Databases**: For comprehensive historical validation, academic institutions often have access to specialized databases like WRDS, Compustat, or CRSP

### For Practical Implementation

For practical model validation:

1. **Focus on Current Distress Detection**: Validate the model's ability to identify current companies showing distress signals
2. **Comparative Analysis**: Compare the retail model against traditional models using currently available companies
3. **Forward Testing**: Implement ongoing validation by tracking companies currently in the "gray zone"

## Available Alternative Data Sources

If historical bankruptcy data is essential for your validation:

1. **Academic Databases**: WRDS, Compustat, CRSP (require institutional access)
2. **Commercial Services**: Bloomberg Terminal, FactSet, S&P Capital IQ (subscription required)
3. **SEC EDGAR Archives**: Historical filings are available but require manual extraction
4. **Financial Research Papers**: Academic papers often include analyzed data from bankrupt companies

## Synthetic Testing Approach

The validation framework includes options for synthetic testing of bankruptcy prediction:

1. **Pattern Replication**: Apply known bankruptcy pattern ratios to test detection
2. **Case Studies**: Integrate documented financial patterns from well-studied bankruptcies
3. **Sensitivity Analysis**: Test model thresholds against synthetic degradation patterns

## Portfolio Maintenance

To maintain the validation portfolio:

1. **Regular Updates**: Add newly identified distressed retailers
2. **Status Tracking**: Update the status of companies as they move between categories
3. **Historical Reference**: Maintain the list of bankrupt companies for reference even if data is unavailable

## Conclusion

While historical bankruptcy data presents challenges for validation, the retail backtest portfolio provides multiple approaches to effectively validate the retail Z-Score model. By focusing on currently available companies and utilizing the framework's handling options, you can still achieve meaningful validation results.
