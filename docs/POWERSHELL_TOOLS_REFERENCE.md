# PowerShell Tools Reference - v5.1.0 EMERALD

This document provides quick reference for the PowerShell tools in the Altman Z-Score project v5.1.0 EMERALD.

## 💎 EMERALD v5.1.0: Major Version 5.1 & IUPAC Element Naming

**IUPAC Element Naming**: Systematic scientific naming convention (PENTUNNILIUM) with enhanced architecture and production-ready stability for enterprise-scale portfolio management.Shell Tools Reference - v5.0.0 EMERALD

This document provides quick reference for the PowerShell tools in the Altman Z-Score project v5.0.0 EMERALD.

## � EMERALD v5.0.0: Major Version 5.0 & IUPAC Element Naming

**IUPAC Element Naming**: Systematic scientific naming convention (PENTNILNILIUM) with enhanced architecture and production-ready stability for enterprise-scale portfolio management.

## Main Tools

### 📊 `analyze_portfolio_parallel_v2.ps1` - Parallel Portfolio Analyzer

**Purpose**: Multi-threaded analysis for large portfolios with progress tracking and efficiency features.

**Key Features**:
- ✅ **Skip-Existing**: `-SkipExisting` parameter to skip already analyzed tickers
- ✅ **Parallel Processing**: Configurable thread count with intelligent defaults
- ✅ **Progress Tracking**: Real-time progress with ETA calculations
- ✅ **Flexible Input**: Portfolio files, individual tickers, or predefined sectors
- ✅ **Error Handling**: Continue-on-error logic with comprehensive reporting

**Usage Examples**:
```powershell
# Basic portfolio analysis
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt"

# Skip existing analysis (efficiency mode)
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt" -SkipExisting

# Custom threading and batch configuration
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\tech_portfolio.txt" -MaxThreads 8 -BatchSize 10

# Dry run (preview what would be processed)
.\analyze_portfolio_parallel_v2.ps1 -Tickers @("AAPL", "MSFT", "GOOGL") -DryRun

# Sector analysis
.\analyze_portfolio_parallel_v2.ps1 -Sector technology -SkipExisting
```

**Key Parameters**:
- `-PortfolioFile` - Path to portfolio file (supports inline comments)
- `-Tickers` - Array of individual ticker symbols
- `-Sector` - Predefined sector (technology, healthcare, financial, industrial, energy)
- `-SkipExisting` - Skip tickers with existing analysis outputs
- `-MaxThreads` - Maximum parallel threads (default: CPU core count)
- `-BatchSize` - Tickers per batch (default: 5)
- `-DryRun` - Show what would be processed without running analysis
- `-ClearCache` - Clear cached data before starting
- `-Timeout` - Timeout in minutes per ticker (default: 10)

### 🌐 `generate_web.ps1` - Dashboard Generator

**Purpose**: Generate modern interactive dashboards with self-contained HTML output.

**Usage**:
```powershell
# Generate main dashboard
.\generate_web.ps1

# Additional dashboard generation tools
.\generate_all_dashboards.ps1  # Generate all portfolio dashboards
```

### 🛠️ Other Tools

**Portfolio Management**:
- `extract_recommendations.ps1` - Extract investment recommendations from analysis
- `check_empty_files.ps1` - Validate output files for completeness
- `count_lines.ps1` - Count lines in project files

**Azure Integration**:
- `monitor_azure_costs.ps1` - Monitor Azure resource costs

## Skip-Existing Feature

The `-SkipExisting` parameter is designed for efficiency when working with large portfolios:

### How It Works
1. **File Detection**: Checks for key analysis outputs (CSV, JSON, summary files)
2. **Size Validation**: Ensures files are non-empty (> 0 bytes)
3. **Smart Filtering**: Only processes tickers without complete analysis
4. **Progress Reporting**: Shows original/skipped/remaining counts

### Use Cases
- **Incremental Updates**: Add new tickers to existing portfolio without reprocessing
- **Resume Interrupted Analysis**: Continue from where previous analysis stopped
- **Portfolio Maintenance**: Regular updates to large portfolios (427+ companies)
- **Development Testing**: Quick iteration when developing new features

### Example Output
```
🔍 Checking for existing analysis outputs...
   ⏭️  Skipping AAPL (analysis exists)
   ⏭️  Skipping AMZN (analysis exists)
   ⏭️  Skipping COST (analysis exists)
📊 Skip-existing filter results:
   • Original tickers: 427
   • Skipped (existing): 380
   • Remaining to process: 47
🎯 Ready to process 47 unique tickers
```

## Portfolio File Format

Portfolio files support inline comments for organization:

```
# Technology Leaders
AAPL    # Apple Inc.
MSFT    # Microsoft Corporation
GOOGL   # Alphabet Inc.

# Financial Services
JPM     # JPMorgan Chase
BAC     # Bank of America
WFC     # Wells Fargo

# Comments and blank lines are ignored
# Tickers can have inline comments after the symbol
```

## Best Practices

### Performance Optimization
- Use `-SkipExisting` for large portfolios to avoid redundant processing
- Adjust `-MaxThreads` based on system capabilities (default: CPU cores)
- Use `-BatchSize` to balance memory usage vs parallelization
- Enable `-ClearCache` when data freshness is critical

### Error Handling
- Default `-ContinueOnError` keeps processing if individual tickers fail
- Use `-DryRun` to validate portfolio before full analysis
- Check logs for detailed error information
- Use `-Timeout` to prevent hanging on problematic tickers

### Large Portfolio Management
- Start with comprehensive portfolio (427 companies)
- Use `-SkipExisting` for incremental updates
- Monitor progress with built-in ETA calculations
- Validate results with `check_empty_files.ps1`

## Integration with Python CLI

Both tools provide consistent skip-existing functionality:

```bash
# Python CLI
python main.py --portfolio-file portfolios/comprehensive_portfolio.txt --skip-existing

# PowerShell equivalent
.\analyze_portfolio_parallel_v2.ps1 -PortfolioFile "portfolios\comprehensive_portfolio.txt" -SkipExisting
```

This ensures seamless workflow integration across different automation scenarios.
