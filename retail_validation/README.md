# Retail Z-Score Model Validation Framework

This directory contains the centralized validation framework for the novel retail Z-Score model documented in `docs/NOVEL_RETAIL_MODEL.md`. The framework provides comprehensive testing, analysis, and reporting capabilities for academic and production validation of the retail-specific bankruptcy prediction model.

## 🏗️ Framework Structure

```
retail_validation/
├── config/
│   └── validation_config.py      # Centralized configuration and settings
├── docs/
│   ├── NOVEL_RETAIL_MODEL.md     # Complete academic paper on retail model
│   ├── VALIDATION_PROCESS_OVERVIEW.md  # Validation methodology overview
│   ├── VALIDATION_TECHNICAL_DETAILS.md # Technical implementation details
│   ├── PORTFOLIO_COMPOSITION.md  # Test portfolio structure and categories
│   ├── PORTFOLIO_USAGE_GUIDE.md  # Guide for portfolio usage with delisted companies
│   ├── MODEL_COMPARISON_METHODOLOGY.md # Model comparison approach
│   └── DELISTED_COMPANIES_HANDLING.md  # Technical guide for handling bankrupt companies
├── scripts/
│   ├── validate_retail_model.py  # Main Python validation script
│   └── run_retail_validation.ps1 # PowerShell orchestrator script
├── results/                      # Timestamped validation results
│   └── [run_timestamp]/
│       ├── validation_report.md
│       ├── raw_results.json
│       └── validation_config_snapshot.json
└── README.md                     # This file
```

## 🎯 Key Features

### ✅ Centralized Configuration
- All validation settings, company categories, and test parameters in `config/validation_config.py`
- External portfolio file import from `portfolios/retail_backtest_portfolio.txt`
- Configurable validation thresholds and test criteria

### ✅ Comprehensive Testing Framework
- **Bankruptcy Prediction Testing**: Validates accuracy using the comprehensive bankruptcy database (139+ companies)
- **Category Performance Analysis**: Tests across different retail company types
- **Inventory Impact Analysis**: Measures effectiveness of X₆ component
- **Model Comparison**: Benchmarks against traditional Z-Score models
- **Academic Reporting**: Publication-ready validation reports

### ✅ Flexible Execution Options
- **Full Validation**: Complete analysis (~2-3 hours, all companies)
- **Quick Test**: Development testing (~15-30 minutes, subset of companies)
- **Model Comparison**: Side-by-side analysis with traditional models
- **Configuration Display**: View current validation settings

## 🚀 Quick Start

### Using the Interactive Launcher (Recommended)
```powershell
# From the retail_validation directory
.\retail_validation_launcher.ps1
```

The launcher provides a user-friendly menu with options for:
- Quick Test (12 companies, ~7-10 minutes)
- Full Validation (61 companies, ~2-3 hours)
- Failed Company Analysis (Pre-Bankruptcy Quarters)
- Visualize Results (Interactive Z-Score Charts)
- Show Configuration
- Help

### Prerequisites
```powershell
# Ensure Python dependencies are installed
pip install -r requirements.txt

# Verify you're in the project root directory
cd c:\Development\Altman-Z-Score
```

### Direct Script Execution

```powershell
# Show validation configuration
.\retail_validation\scripts\run_retail_validation.ps1 -ShowConfig

# Quick development test (11 representative companies)
.\retail_validation\scripts\run_retail_validation.ps1 -QuickTest

# Full comprehensive validation (61 companies, academic quality)
.\retail_validation\scripts\run_retail_validation.ps1 -FullValidation

# Model comparison analysis
.\retail_validation\scripts\run_retail_validation.ps1 -FullValidation -CompareModels

# Handling delisted/bankrupt companies
.\retail_validation\scripts\run_retail_validation.ps1 -AvailableOnly            # Skip unavailable tickers
.\retail_validation\scripts\run_retail_validation.ps1 -SampleBankruptcy         # Use sample bankruptcy data
.\retail_validation\scripts\run_retail_validation.ps1 -UseHistoricalResults     # Use previous validation results
```

### Python Direct Usage

```python
# Run validation directly with Python
python retail_validation/scripts/validate_retail_model.py --quick-test
python retail_validation/scripts/validate_retail_model.py --comparison --detailed
```

## 📊 Validation Tests

The framework implements several standardized validation tests:

### 1. Bankruptcy Prediction Test
- **Target**: >80% accuracy (vs ~65% traditional)
- **Scope**: Failed/bankrupt retailers
- **Metric**: Sensitivity for Distress/Gray Zone classifications

### 2. Early Warning Test
- **Target**: 2-3 years advance warning
- **Scope**: Retailers in distress
- **Metric**: Lead time analysis and trend detection

### 3. False Positive Test
- **Target**: <15% false positive rate (vs ~25% traditional)
- **Scope**: Stable/strong retailers
- **Metric**: Specificity for Safe Zone classifications

### 4. Seasonal Stability Test
- **Target**: <50% quarterly variation
- **Scope**: Seasonal/cyclical retailers
- **Metric**: Quarterly classification consistency

### 5. Inventory Impact Test
- **Target**: >10% measurable component impact
- **Scope**: All retailers with inventory data
- **Metric**: X₆ component effectiveness analysis

## 📈 Output Files

Each validation run creates a timestamped directory with:

- **`validation_report.md`**: Comprehensive academic-quality report
- **`raw_results.json`**: Detailed company-by-company analysis data
- **`validation_config_snapshot.json`**: Configuration used for the run

## 🎓 Academic Applications

The validation framework is designed to support:

- **Peer Review**: Academic-quality reports with statistical rigor
- **Reproducibility**: Complete configuration snapshots and timestamped results
- **Benchmarking**: Standardized comparison with traditional models
- **Publication**: Ready-to-use analysis and visualizations

## ⚙️ Configuration

All validation settings are centralized in `config/validation_config.py`:

- **Company Categories**: Predefined groupings for different validation scenarios
- **Test Parameters**: Configurable thresholds and success criteria
- **Portfolio Management**: External file import and ticker validation
- **Report Settings**: Output formats and academic formatting options

## 🔧 Development

### Adding New Validation Tests

1. Define test configuration in `validation_config.py`:
```python
VALIDATION_TESTS['new_test'] = {
    'description': 'Test description',
    'target_categories': ['category_list'],
    'success_threshold': 0.75,
    'additional_params': {}
}
```

2. Implement test method in `validate_retail_model.py`:
```python
def analyze_new_test(self, results: Dict) -> Dict:
    # Test implementation
    return analysis_results
```

3. Add test results to validation report generation.

### Extending Company Categories

Update `COMPANY_CATEGORIES` in `validation_config.py`:
```python
COMPANY_CATEGORIES['new_category'] = ['TICKER1', 'TICKER2', ...]
```

## 📋 Portfolio Management

The framework imports the retail backtest portfolio from:
```
portfolios/retail_backtest_portfolio.txt
```

This external file contains:
- 61 retail companies (active and historical)
- Multiple financial health categories
- Comprehensive industry coverage
- Comment-based documentation

## 🏆 Expected Results

Based on the novel retail Z-Score model design:

- **Improved Accuracy**: Better bankruptcy prediction than traditional models
- **Enhanced Discrimination**: More accurate risk categorization for retail companies
- **Inventory Intelligence**: Measurable improvement from X₆ component
- **Seasonal Robustness**: Better handling of seasonal inventory patterns

## 📞 Support

For issues or questions about the validation framework:

1. Check validation configuration: `-ShowConfig`
2. Review prerequisite requirements: `-Help`
3. Examine validation reports for detailed diagnostics
4. Verify portfolio file integrity and company ticker validity

---

*Framework Version: 2.0*  
*Compatible with: Altman Z-Score Analysis v4.5.0+*  
*Last Updated: 2025-07-02*
