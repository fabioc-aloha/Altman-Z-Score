# Quick Start Guide - v4.0.0 Enhanced Features

## 🚀 Professional Investment Analysis Platform v4.0.0

Your investment analysis platform now includes powerful v4.0.0 features including multi-quarter analysis, environment-driven configuration, and enhanced chart generation.

## Immediate Benefits v4.0.0

### ✅ What's New in v4.0.0
- **Multi-Quarter Analysis**: 4-20+ quarters of historical Z-Score trends with intelligent defaults
- **Environment-Driven Configuration**: Smart CLI defaults based on your FMP account type
- **Enhanced Chart Generation**: Risk zone colored markers with improved visualization
- **Intelligent Batch Processing**: Optimized for both free (5-10 stocks) and paid accounts (20-50 stocks)
- **Account Optimization**: Platform automatically adapts to your FMP account capabilities

## Quick Commands to Try v4.0.0

### 1. Environment-Driven Analysis (NEW)
```bash
# CLI automatically uses intelligent defaults from .env
python main.py AAPL                # Uses DEFAULT_QUARTERS from .env
python main.py AAPL MSFT GOOGL     # Uses MAX_BATCH_SIZE from .env

# Override defaults when needed
python main.py AAPL --quarters 8   # Extended analysis
python main.py AAPL --log-level DEBUG  # Enhanced logging
```

### 2. Multi-Quarter Analysis (ENHANCED)
```bash
# 8-quarter historical analysis with enhanced features
python main.py AAPL --quarters 8 --enhanced-analysis

# 12-quarter analysis for deeper trends (paid accounts)
python main.py MSFT --quarters 12 --enhanced-analysis

# Batch multi-quarter analysis
python main.py AAPL MSFT GOOGL --quarters 6 --batch-size 15
```

### 3. Account-Optimized Batch Processing (NEW)
```bash
# Automatically optimized for your account type
python main.py AAPL MSFT GOOGL NVDA TSLA    # Smart batch sizing

# Large portfolio processing (paid accounts)
python main.py --sector technology --quarters 8

# Cache management
python main.py --cache-stats        # View cache performance
python main.py --clear-cache        # Force fresh data
```

## v4.0.0 Configuration Guide

### Use Enhanced Settings
Copy the enhanced configuration:
```bash
cp .env.enhanced .env
```

This enables:
- Higher concurrent processing (10 simultaneous requests)
- Extended quarterly analysis (8 quarters default)
- Larger batch sizes (25 stocks per batch)
- Advanced analytics features

## Recommended First Test

### Start with a Small Portfolio
```bash
# Test with 5 mega-cap stocks
python enhanced_analysis.py AAPL MSFT GOOGL AMZN META --quarters 8 --batch-size 5
```

This will:
- ✅ Validate your enhanced API access
- ✅ Show multi-quarter trend analysis
- ✅ Demonstrate faster processing speeds
- ✅ Generate comparative portfolio reports

## Performance Comparison

### Before (Free Account)
- 📊 Analysis: 4 quarters maximum
- ⏱️ Processing: 5 requests/minute (very slow)
- 📈 Portfolio: 5-10 stocks maximum per day
- 🔄 Batch Size: 1-2 stocks at a time

### After (Upgraded Account)
- 📊 Analysis: 8-20 quarters of historical data
- ⏱️ Processing: 300+ requests/minute (60x faster!)
- 📈 Portfolio: 100+ stocks in single session
- 🔄 Batch Size: 20-50 stocks simultaneously

## Sample Workflows

### Daily Portfolio Check (5 minutes)
```bash
python enhanced_analysis.py --portfolio-file portfolios/diversified_portfolio.txt --quarters 4
```

### Weekly Deep Analysis (15 minutes)
```bash
python enhanced_analysis.py --portfolio-file portfolios/tech_portfolio.txt --quarters 8
```

### Monthly Full Market Scan (30 minutes)
```bash
# Run full batch analysis
pwsh.exe -File run_batch_examples.ps1
# Select option 0 for all 110+ companies
```

## What to Expect

### Enhanced Output Features
- **Multi-Quarter Charts**: 8+ quarters of Z-Score trends
- **Portfolio Summaries**: Cross-company risk analysis
- **Sector Comparisons**: Industry-wide financial health
- **Correlation Analysis**: Inter-company relationships

### Faster Results
- **Previous**: 1 stock per minute (free account)
- **Now**: 10+ stocks per minute (upgraded account)
- **Large Portfolios**: Complete in minutes, not hours

## Troubleshooting

### If You See Rate Limiting
- Even upgraded accounts have limits (just much higher)
- Use `--batch-size` to control concurrent requests
- Monitor usage in FMP dashboard

### For Best Performance
- Use batch processing for multiple stocks
- Enable caching with `--cache-stats` to check efficiency
- Process during off-peak hours for fastest speeds

## Next Steps

1. **✅ Test Enhanced Features**: Run the sample commands above
2. **📁 Create Portfolio Files**: Add your own stock lists to `portfolios/`
3. **⚙️ Optimize Settings**: Adjust batch sizes based on your needs
4. **📊 Schedule Analysis**: Set up regular portfolio monitoring

---

**Need Help?**
- Check `logs/altman_zscore.log` for detailed processing info
- Use `--log-level DEBUG` for troubleshooting
- See `ENHANCED_FEATURES.md` for complete feature documentation

**Enjoy your upgraded analysis capabilities! 🚀**
