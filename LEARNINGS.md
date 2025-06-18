# Technical Learnings & Decisions Log

## Core Principles
Our technical decisions are guided by our vision to set new industry standards for:
- Transparency in financial analysis
- Code extensibility and maintainability
- Actionable financial insights
- User experience excellence

See [vision.md](./vision.md) for details.

## Version History & Key Learnings

### v3.5.1+ (June 18, 2025) - LLM Prompt Optimization & Data Injection Fixes
#### Technical Decisions
1. **Analyst Recommendations Data Injection**
   - **Issue**: Market Sentiment Analysis sections showed "No analyst recommendation data was provided"
   - **Root Cause**: `recommendations.json`, `major_holders.json`, `institutional_holders.json` files were fetched but never saved
   - **Solution**: Added saving logic in `src/altman_zscore/data_fetching/financials.py` after `fetch_yfinance_full()` call
   - **Result**: Market Sentiment Analysis now uses real analyst data with trend analysis and consensus assessment

2. **LLM Prompt Template Optimization**
   - **Issue**: Prompt referenced "raw financial data" files that were intentionally excluded for performance (prompt size reduced from >10MB to 42KB)
   - **Root Cause**: Template asked for raw financial data tables that weren't being injected
   - **Solution**: Updated `src/prompts/prompt_fin_analysis.md` to remove references to:
     - "detailed financial statement data provided (from the injected raw financials)"
     - "table of raw financial data by period" in appendix section
   - **Result**: Eliminated "Not provided in injected data" messages; LLM focuses on available Z-Score and metadata

3. **LLM Report Structure Enhancement**
   - **Issue**: Reports had 10 sections but lacked space for cross-data pattern insights
   - **Root Cause**: Structured sections didn't capture interesting relationships between disparate data points
   - **Solution**: Added "Other Relevant Insights" (Section 9), expanding from 10 to 11 sections
   - **Implementation**: Updated `src/prompts/prompt_fin_analysis.md` with detailed instructions for pattern recognition
   - **Result**: LLM now identifies:
     - Stock split impact on liquidity and retail access
     - Institutional position changes signaling confidence
     - Dividend policy shifts affecting investor interest
     - Forward-looking early warning indicators
     - Strategic patterns in financial reinvestment

#### Performance Impact
- **Data Injection**: Analyst recommendations now properly included in LLM context
- **Prompt Clarity**: Removed confusion about unavailable data sources
- **Report Quality**: Market Sentiment Analysis sections now contain real data and actionable insights
- **Analysis Quality**:
  - **Cross-Pattern Recognition**: LLM connects data points across different financial domains
  - **Strategic Context**: Financial metrics linked to business strategy implications
  - **Forward-Looking**: Early detection of trend changes for proactive decision-making
  - **Institutional Perspective**: Major holder position changes provide market sentiment context

### v3.2.0 (June 16, 2025) - Visualization & Error Handling
#### Technical Decisions
1. **Chart Visualization**
   - Used compound legend entries (Rectangle + Line2D) for candlesticks
   - Implemented HandlerTuple for complex legend elements
   - Maintained visual consistency between chart and legend

2. **Error Handling**
   - Replaced sys.exit() with structured exception handling
   - Implemented per-ticker isolation for batch processing
   - Added graceful degradation for partial failures

#### Implementation Patterns
```python
# Compound Legend Pattern
def create_candlestick_legend():
    body = Rectangle((0, 0.3), 0.4, 0.4)
    wick = Line2D([0.2, 0.2], [0.1, 0.9])
    return (body, wick)  # Tuple for HandlerTuple

# Error Isolation Pattern
def process_tickers(tickers):
    results = []
    for ticker in tickers:
        try:
            result = analyze_ticker(ticker)
            results.append(result)
        except ValueError as ve:
            log.warning(f"{ticker}: {ve}")
            continue
    return results
```

#### Learnings
- Complex visualizations benefit from custom legend handlers
- Error isolation improves batch processing reliability
- User feedback should be immediate and actionable

### v3.1.1 (June 15, 2025) - Documentation & Pipeline
#### Technical Decisions
1. **Documentation Structure**
   - Added FLOW.md for architecture documentation
   - Updated output directory documentation
   - Standardized documentation format

2. **Data Pipeline**
   - Enhanced SEC EDGAR data processing
   - Improved data reconciliation
   - Added robust error reporting

#### Learnings
- Clear documentation structure aids maintenance
- Consistent error reporting improves debugging
- Data reconciliation needs careful validation

### v3.0.1 (June 7, 2025) - Modularization
#### Technical Decisions
1. **Code Organization**
   - Grouped by functionality (core, models, etc.)
   - Used relative imports for module references
   - Added integration tests

2. **Testing Strategy**
   - Main pipeline integration tests
   - Unit tests for core components
   - Continuous test running during refactoring

#### Implementation Patterns
```python
# Integration Test Pattern
def test_main_pipeline():
    result = run_pipeline('MSFT')
    assert result.success
    assert result.data is not None
    assert 'zscore' in result.data.columns
```

#### Learnings
- Integration tests catch import problems early
- Systematic refactoring reduces regression
- Clear module boundaries improve maintenance

## Best Practices Established
1. **Code Organization**
   - Group related functionality
   - Use clear import paths
   - Maintain module independence

2. **Error Handling**
   - Graceful degradation
   - Clear user feedback
   - Proper exception hierarchy

3. **Testing**
   - Integration tests for workflows
   - Unit tests for components
   - Regular test running

4. **Documentation**
   - Update with code changes
   - Include code examples
   - Document key decisions

5. **Visualization**
   - Match legend to chart elements
   - Use consistent styling
   - Consider user feedback

## 2025-06-16: Codebase Cleanup
- Deprecated `utils/terminal.py` fully removed; all terminal output now uses standard logging.
- All plotting modules now use logging for warnings/errors instead of print statements.
- Removed commented-out debug code and obsolete comments for clarity.
- Removed unused/dead code as identified by static analysis and code review.
- This improves maintainability, testability, and clarity for future contributors.
