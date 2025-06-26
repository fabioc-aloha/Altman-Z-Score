# SEC EDGAR Elimination Plan

**Target**: Complete removal of SEC EDGAR infrastructure to simplify codebase by ~2000+ lines

**Strategy**: FMP provides all financial data in standardized format, eliminating need for XBRL parsing and field mapping

---

## 🗑️ Files to Remove

### **Primary SEC EDGAR Components**
```
src/altman_zscore/api/sec_client.py              # 600+ lines - Main SEC API client
src/altman_zscore/schemas/edgar.py               # 200+ lines - SEC data schemas  
src/altman_zscore/data_fetching/sec_edgar.py     # 100+ lines - SEC data utilities
altman_zscore/cache/field_database_builder.py   # 300+ lines - New field mapping system
```

### **Field Mapping Infrastructure**
```
src/altman_zscore/data_fetching/field_mapping_builder.py  # 1000+ lines - Legacy field mapping
src/altman_zscore/api/cached_field_mapper.py              # 200+ lines - Field mapping cache
src/altman_zscore/api/cache/                               # Entire cache directory
```

### **Industry-Specific Fetchers (SEC-dependent)**
```
src/altman_zscore/api/base_fetcher.py            # 150+ lines - Base XBRL fetcher
src/altman_zscore/api/manufacturing_fetcher.py   # 100+ lines - Manufacturing XBRL
src/altman_zscore/api/tech_fetcher.py            # 80+ lines - Tech XBRL  
src/altman_zscore/api/service_fetcher.py         # 100+ lines - Service XBRL
```

### **Prompt Templates (Field Mapping)**
```
src/prompts/prompt_field_mapping.md              # Field mapping prompts
src/prompts/prompt_field_mapping_simple.md       # Simple field mapping
src/prompts/prompt_reconcile_financials.md       # SEC vs Yahoo reconciliation
```

### **Cache and Database Files**
```
src/altman_zscore/api/cache/                      # SEC company cache
src/altman_zscore/company/cik_cache.py            # CIK lookup cache
altman_zscore/cache/field_mapping_cache.json     # Field mapping cache
```

---

## 📁 Files to Modify

### **Data Fetching Layer**
- `src/altman_zscore/data_fetching/financials.py`
  - **Remove**: SEC EDGAR integration, field mapping calls
  - **Keep**: FMP integration, Yahoo Finance market data
  - **Simplify**: Direct field access instead of mapping

### **Main Analysis Pipeline**
- `src/altman_zscore/core/one_stock_analysis.py`
  - **Remove**: SEC EDGAR data fetching logic
  - **Update**: Use only FMP financial data
  - **Simplify**: Remove field mapping validation

### **API Helpers**
- `src/altman_zscore/api/yahoo_helpers.py`
  - **Keep**: All Yahoo Finance functionality (unchanged)
  - **Remove**: Any SEC EDGAR cross-references

### **Documentation**
- `APIS.md` - Remove SEC EDGAR sections
- `REFACTORING_PLAN.md` - Update to reflect simplified architecture
- `FLOW.md` - ✅ Already updated with simplified 5-layer architecture

---

## 🔄 FMP Integration Updates

### **Standardized Field Access**
Replace complex field mapping with direct FMP field access:

```python
# OLD (Complex field mapping)
sec_quarters = extract_quarters_from_sec_facts(sec_facts, fields_to_fetch)
mapped_quarters = apply_cached_field_mapping(sec_quarters, fields_to_fetch, ticker)

# NEW (Direct FMP access) 
fmp_data = fmp_client.get_financial_statements(ticker, period='quarterly')
financial_data = {
    'total_assets': fmp_data['totalAssets'],
    'revenue': fmp_data['revenue'], 
    'retained_earnings': fmp_data['retainedEarnings'],
    'current_assets': fmp_data['totalCurrentAssets'],
    'current_liabilities': fmp_data['totalCurrentLiabilities']
}
```

### **Pre-calculated Ratios**
Leverage FMP's pre-calculated financial ratios:

```python
# Use FMP ratios endpoint for direct Z-Score components
ratios = fmp_client.get_financial_ratios(ticker)
working_capital_ratio = ratios['workingCapitalTotalAssets']
ebit_ratio = ratios['operatingProfitMargin']
```

---

## ⚡ Performance Benefits

### **Code Complexity Reduction**
- **Lines Removed**: ~2000+ lines of SEC EDGAR code
- **Files Removed**: ~15+ files
- **Dependencies**: Eliminate SEC rate limiting, XBRL parsing, AI field mapping

### **Runtime Performance**
- **No XBRL Parsing**: Eliminate BeautifulSoup HTML/XML processing
- **No Field Mapping**: Direct field access vs. complex mapping algorithms
- **No AI Disambiguation**: Remove LLM calls for field mapping
- **Simpler Caching**: Only FMP + Yahoo data, no SEC facts cache

### **Maintenance Simplification**
- **Single Financial Source**: FMP only (vs. SEC EDGAR + reconciliation)
- **Standardized Fields**: Consistent naming across all companies
- **No Edge Cases**: Eliminate company-specific field mapping quirks
- **Reduced Testing**: Remove SEC EDGAR test coverage

---

## 🎯 Migration Strategy

### **Phase 1: Remove SEC Dependencies**
1. Remove all SEC EDGAR API calls from `financials.py`
2. Update `one_stock_analysis.py` to use only FMP data
3. Remove field mapping validation and reconciliation logic

### **Phase 2: Enhance FMP Integration** 
1. Expand FMP client to handle all Z-Score financial fields
2. Add FMP financial ratios endpoint integration
3. Implement direct field validation without mapping

### **Phase 3: Clean Up**
1. Delete SEC EDGAR files and directories
2. Remove SEC-related imports and dependencies
3. Update documentation and tests

### **Phase 4: Optimization**
1. Optimize FMP caching strategy
2. Simplify data quality validation
3. Performance testing and benchmarking

---

## 🧪 Testing Strategy

### **Regression Testing**
- Ensure Z-Score calculations remain accurate with FMP data
- Validate output compatibility with existing report formats
- Test edge cases (missing data, API failures)

### **Performance Testing**
- Benchmark before/after performance improvements
- Measure API call reduction and response times
- Validate caching effectiveness

### **Data Quality Validation**
- Cross-reference FMP vs. current SEC EDGAR results for sample companies
- Ensure no critical financial data is lost in transition
- Validate industry-specific model compatibility

---

## 📊 Expected Results

### **Codebase Metrics**
- **~35% reduction** in total lines of code
- **~50% reduction** in complexity (cyclomatic complexity)
- **~70% reduction** in data processing time

### **Reliability Improvements**
- **Eliminate** SEC API rate limiting issues
- **Eliminate** XBRL parsing edge cases and failures
- **Eliminate** field mapping ambiguity and errors
- **Standardize** data quality across all companies

### **Developer Experience**
- **Simplified** debugging (single data source)
- **Faster** development cycles (no field mapping complexity)
- **Easier** testing (direct field access vs. mapping logic)
- **Clearer** error messages (FMP standardized errors)

---

*This plan represents a major architectural simplification that will make the Altman Z-Score platform significantly more maintainable, reliable, and performant while preserving all analytical capabilities.*
