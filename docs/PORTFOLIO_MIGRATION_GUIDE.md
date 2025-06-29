# Portfolio Scripts Migration Guide

## ✅ Legacy Scripts Successfully Removed!

**All legacy portfolio generation scripts have been removed and replaced with the unified modular system.**

**Removed files:**
- ❌ `generate_strong_buys.py` → ✅ `generate_portfolio_modern.py strong_buy`
- ❌ `generate_strong_buys_modular.py` → ✅ `generate_portfolio_modern.py strong_buy`
- ❌ `generate_value_picks.py` → ✅ `generate_portfolio_modern.py value`
- ❌ `generate_growth_picks.py` → ✅ `generate_portfolio_modern.py growth`
- ❌ `generate_dividend_picks.py` → ✅ `generate_portfolio_modern.py dividend`
- ❌ `generate_conservative_picks.py` → ✅ `generate_portfolio_modern.py conservative`
- ❌ `generate_aggressive_picks.py` → ✅ `generate_portfolio_modern.py aggressive`
- ❌ `generate_sell_picks.py` → ✅ `generate_portfolio_modern.py sell`
- ❌ `generate_strong_sell_picks.py` → ✅ `generate_portfolio_modern.py strong_sell`

## Quick Start - Using the New System

### Generate Individual Portfolios:
```bash
python generate_portfolio_modern.py strong_buy
python generate_portfolio_modern.py value
python generate_portfolio_modern.py growth
```

### Generate All Portfolios at Once:
```bash
python generate_portfolio_modern.py all
```

## Command Reference

**All legacy scripts have been consolidated. Use these commands instead:**

| Portfolio Type | New Command |
|----------------|-------------|
| Strong Buy | `python generate_portfolio_modern.py strong_buy` |
| Value Investor | `python generate_portfolio_modern.py value` |
| Growth | `python generate_portfolio_modern.py growth` |
| Dividend Income | `python generate_portfolio_modern.py dividend` |
| Conservative | `python generate_portfolio_modern.py conservative` |
| Aggressive | `python generate_portfolio_modern.py aggressive` |
| Sell Recommendations | `python generate_portfolio_modern.py sell` |
| Strong Sell | `python generate_portfolio_modern.py strong_sell` |

## New Features

### Generate All Portfolios at Once:
```bash
python generate_portfolio_modern.py all
```

### Advanced Options:
```bash
# Verbose logging
python generate_portfolio_modern.py strong_buy --verbose

# Custom base directory
python generate_portfolio_modern.py value --base-dir /path/to/data

# Help
python generate_portfolio_modern.py --help
```

## Python API Usage

### Direct Import:
```python
from altman_zscore.scripts.generate_portfolio import PortfolioGeneratorScript

# Create generator
generator = PortfolioGeneratorScript()

# Generate specific portfolio
success = generator.generate_portfolio('strong_buy')

# Generate all portfolios
results = generator.generate_all_portfolios()
```

### Integration Example:
```python
import logging
from altman_zscore.scripts.generate_portfolio import PortfolioGeneratorScript

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create and configure generator
generator = PortfolioGeneratorScript(base_dir="./data")

# Generate portfolios based on conditions
portfolio_types = ['strong_buy', 'value', 'growth']

for portfolio_type in portfolio_types:
    try:
        success = generator.generate_portfolio(portfolio_type)
        if success:
            print(f"✅ {portfolio_type} portfolio generated")
        else:
            print(f"⚠️ {portfolio_type} portfolio had no matching companies")
    except Exception as e:
        print(f"❌ Error generating {portfolio_type}: {e}")
```

## Migration Timeline

### ✅ Migration Complete!
The legacy portfolio generation scripts have been successfully removed and replaced with the unified modular system.

**What Changed:**
1. ✅ **All 9 legacy scripts removed** (~5,677 lines of duplicated code)
2. ✅ **Unified system implemented** (~400 lines of modular code)
3. ✅ **Same functionality maintained** with improved architecture
4. ✅ **New features added** (generate all, better error handling, API access)

**Action Required:**
- Update any automation scripts or documentation that referenced the old files
- Use `generate_portfolio_modern.py` for all portfolio generation
- Leverage new features like `all` command for efficiency

## Troubleshooting

### Common Issues:

#### 1. **Import Errors**
```
ModuleNotFoundError: No module named 'altman_zscore'
```
**Solution:** Run from project root directory or set PYTHONPATH

#### 2. **No Companies Found**
```
WARNING - Only 0 companies found for value, minimum is 5
```
**Solution:** This is normal when test data doesn't match portfolio criteria

#### 3. **Missing Output Directory**
```
WARNING - Output directory output does not exist
```
**Solution:** Ensure the `output/` directory exists with company data

### Getting Help:
```bash
python generate_portfolio_modern.py --help
```

## Benefits of Migration

### Immediate Benefits:
- ✅ **Single command** for all portfolio types
- ✅ **Consistent error handling** and logging
- ✅ **Better performance** with optimized data loading
- ✅ **Generate all portfolios** at once

### Long-term Benefits:
- ✅ **Easier maintenance** with consolidated codebase
- ✅ **New features** available immediately across all portfolio types
- ✅ **Better testing** and quality assurance
- ✅ **API access** for automation and integration

## Support

If you encounter any issues during migration:

1. **Check the logs** with `--verbose` flag
2. **Verify data format** in `output/` directory
3. **Test with single portfolio** before running all
4. **Compare outputs** with existing scripts if needed

The new system is designed to be 100% compatible with existing workflows while providing modern architecture and new capabilities.
