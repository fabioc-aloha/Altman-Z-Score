# Retail Z-Score Model Validation Framework

This directory contains comprehensive validation tools for the novel retail Z-Score model documented in `NOVEL_RETAIL_MODEL.md`.

## Quick Start

### Option 1: PowerShell Script (Recommended)
```powershell
# Full comprehensive validation (2-3 hours)
.\run_retail_validation.ps1 -FullValidation

# Quick development test (15 minutes)
.\run_retail_validation.ps1 -QuickTest
```

### Option 2: Batch Script (Windows)
```batch
# Interactive menu-driven validation
.\run_retail_validation.bat
```

### Option 3: Python Script (Advanced)
```bash
# Custom validation with specific options
python validate_retail_model.py --portfolio portfolios/retail_backtest_portfolio.txt --comparison --detailed
```

## Validation Portfolio

The `retail_backtest_portfolio.txt` contains **75 carefully selected retail companies** across 5 categories:

- **Failed/Bankrupt Retailers (20)**: Test bankruptcy prediction accuracy
- **Retailers in Distress (15)**: Test early warning capabilities  
- **Recovery/Turnaround Stories (10)**: Test model discrimination
- **Stable/Strong Retailers (15)**: Test false positive rates
- **Seasonal/Cyclical Retailers (15)**: Test seasonal pattern handling

## Expected Outcomes

The validation framework tests the retail model's core innovations:

### 1. Bankruptcy Prediction Accuracy
- **Target**: >80% accuracy (vs ~65% traditional Z-Score)
- **Method**: Historical analysis of known retail bankruptcies
- **Key Insight**: Modified working capital (X₁) and inventory turnover (X₆) provide earlier warning signals

### 2. Inventory Component Effectiveness  
- **Innovation**: X₆ = Inventory Turnover Adjustment (normalized)
- **Method**: Compare high vs low inventory efficiency companies
- **Expected**: Companies with better inventory management show higher Z-Scores

### 3. Modified Working Capital Impact
- **Innovation**: X₁ = (Current Assets - Inventory) / Total Assets
- **Method**: Compare retail vs traditional working capital calculations
- **Expected**: More accurate liquidity assessment for retail companies

### 4. Seasonal Pattern Handling
- **Challenge**: Retail inventory varies dramatically by season
- **Method**: Quarterly Z-Score variation analysis
- **Expected**: More stable risk classifications across seasons

## Output Files

Validation generates comprehensive results:

- **`validation_report.md`**: Executive summary with key findings
- **`raw_results.json`**: Detailed company-by-company analysis  
- **`bankruptcy_prediction_analysis.csv`**: Bankruptcy prediction accuracy data
- **`comparative_analysis.xlsx`**: Retail vs traditional model comparison

## Academic Applications

This validation framework supports:

- **Peer Review**: Comprehensive testing for academic publication
- **Empirical Research**: Benchmark for future retail finance studies  
- **Industry Application**: Validation for practical implementation
- **Model Refinement**: Data-driven improvement recommendations

## Model Innovation Summary

The retail Z-Score model introduces two key innovations:

### Modified Working Capital (X₁)
```
Traditional: (Current Assets - Current Liabilities) / Total Assets
Retail:      (Current Assets - Inventory) / Total Assets
```
**Rationale**: Inventory is not truly liquid for retail operations

### Inventory Turnover Component (X₆)  
```
X₆ = min(1.0, (COGS / Inventory) / Industry_Median_Turnover)
```
**Rationale**: Inventory efficiency is critical for retail success

## Validation Methodology

The framework employs rigorous testing:

1. **Historical Accuracy**: Test against known bankruptcies 2010-2025
2. **Cross-Sectional Analysis**: Compare across retail subsectors  
3. **Temporal Analysis**: Multi-year trend validation
4. **Comparative Analysis**: Benchmark against traditional models
5. **Statistical Validation**: ROC curves, sensitivity, specificity

## Requirements

- Python 3.8+ with project dependencies
- Financial data API access (FMP recommended)
- 2-4 GB available disk space for results
- 2-3 hours for full validation runtime

## Support

For questions about the retail model validation:

1. Review `NOVEL_RETAIL_MODEL.md` for theoretical foundation
2. Check `FLOW.md` for system architecture details
3. See `MODELS.md` for model specifications
4. Consult validation output files for detailed results

## Citation

If using this validation framework for academic research:

```
Altman Z-Score Project Team. (2025). "A Novel Retail-Specific Altman Z-Score Model: 
Incorporating Inventory Turnover for Enhanced Bankruptcy Prediction in Retail Companies." 
Altman Z-Score Project Documentation.
```

---

*This validation framework represents the first comprehensive testing of a retail-specific Z-Score model, supporting the academic rigor and practical applicability of the novel retail model innovation.*
