# SEC EDGAR Integration Plan for Delisted Companies

**Date:** July 2, 2025  
**Version:** 1.0  
**Project:** Altman Z-Score (v4.6.2+)  
**Author:** GitHub Copilot

## Executive Summary

This document outlines a comprehensive plan to integrate SEC EDGAR as a fallback data source for delisted companies in the Altman Z-Score analysis pipeline. The integration will enable analysis of bankrupt and delisted companies, which is critical for bankruptcy prediction model validation and historical performance testing. This capability is particularly important for the retail validation framework where analyzing actual bankruptcy cases provides invaluable insights.

## Background

Currently, the Altman Z-Score pipeline primarily relies on Financial Modeling Prep (FMP) API for financial data, which works well for active companies but fails when analyzing delisted or bankrupt entities. While we have established the foundational components for SEC EDGAR integration in the retail validation framework, these components are not yet integrated into the main analysis pipeline.

## Goals

1. Enable analysis of delisted/bankrupt companies through SEC EDGAR fallback mechanism
2. Maintain consistent Z-Score calculation regardless of data source
3. Preserve performance by only using SEC EDGAR when necessary
4. Provide clear indication of data source in reports and logs
5. Implement efficient caching for SEC EDGAR data

## Technical Architecture

### Current Architecture

```
[User Request] → [Main Pipeline] → [Data Merger] → [FMP API] → [Financial Data] → [Z-Score Calculation]
                                                                                  ↓
                                                                  [Market Analysis] → [Report Generation]
```

### Target Architecture

```
[User Request] → [Main Pipeline] → [Data Merger] → [FMP API] → [Success?] → Yes → [Financial Data] → [Z-Score Calculation]
                                                                    ↓                                     ↓
                                                                    No                       [Market Analysis]
                                                                    ↓                                     ↓
                                                           [SEC EDGAR API] → [Data Normalization] → [Report Generation]
                                                                    ↓
                                                           [Cache Management]
```

## Implementation Phases

### Phase 1: Core Integration (v4.7.0)

1. **Data Merger Enhancement**
   - Modify `DataMerger` class to detect FMP data retrieval failures
   - Implement fallback mechanism to SEC EDGAR connector
   - Add configuration toggle for SEC EDGAR fallback (enabled by default)

2. **SEC EDGAR Integration**
   - Move `EdgarConnector` class to main pipeline architecture
   - Implement data normalization to match FMP data structure
   - Add SEC EDGAR-specific error handling

3. **Logging & Reporting**
   - Add data source indicators in logs
   - Update reports to include data source information
   - Implement detailed logging for SEC EDGAR retrieval process

### Phase 2: Optimization & Extension (v4.8.0)

1. **Performance Optimization**
   - Implement parallel data fetching when appropriate
   - Optimize SEC EDGAR data parsing for speed
   - Enhance caching strategy for SEC EDGAR data

2. **Extended Data Coverage**
   - Expand SEC EDGAR data retrieval to cover all financial metrics
   - Implement historical data fetching for time-series analysis
   - Add support for quarterly data from SEC EDGAR

3. **Testing & Validation**
   - Create comprehensive test suite for SEC EDGAR integration
   - Validate Z-Score calculation consistency across data sources
   - Benchmark performance against FMP-only implementation

### Phase 3: User Experience & Advanced Features (v4.9.0)

1. **User Experience Enhancements**
   - Add UI indicators for data source in dashboard
   - Implement source toggling for comparative analysis
   - Create detailed documentation for users

2. **Advanced Analysis Features**
   - Enable historical bankruptcy prediction analysis
   - Support time-series analysis for delisted companies
   - Implement comparative view between active and delisted companies

## Required Code Changes

### Core Components

1. **Data Merger Modifications** (`altman_zscore/layers/data_fetch/data_merger.py`)
   ```python
   async def fetch_financial_data(self, ticker: str, period: str = "annual") -> Dict:
       """Fetch financial data from primary source or fallback to SEC EDGAR if needed."""
       try:
           # Attempt to fetch from primary source (FMP)
           data = await self._fetch_from_fmp(ticker, period)
           self.data_source = "fmp"
           return data
       except PrimaryDataSourceError:
           # Fallback to SEC EDGAR for delisted companies
           if self.config.enable_sec_edgar_fallback:
               logger.info(f"Falling back to SEC EDGAR for {ticker} (likely delisted)")
               data = await self._fetch_from_sec_edgar(ticker, period)
               self.data_source = "edgar"
               return data
           else:
               raise  # Re-raise if fallback is disabled
   ```

2. **SEC EDGAR Connector Integration** (move from retail validation to main pipeline)
   ```python
   # New file: altman_zscore/layers/data_fetch/sec_edgar_fetcher.py
   
   class SecEdgarFetcher:
       """Fetcher for SEC EDGAR financial data for delisted companies."""
       
       def __init__(self, config):
           self.config = config
           self.cache_manager = CacheManager(
               cache_dir=os.path.join(config.cache_dir, "sec_edgar"),
               ttl_days=config.sec_edgar_cache_ttl_days
           )
           
       async def fetch_financial_statements(self, ticker: str, period: str = "annual") -> Dict:
           """Fetch financial statements from SEC EDGAR."""
           cache_key = f"{ticker}_{period}_financials"
           
           # Try to get from cache first
           cached_data = self.cache_manager.get(cache_key)
           if cached_data:
               return cached_data
               
           # Fetch from SEC EDGAR
           # Implementation details here...
           
           # Cache the results
           self.cache_manager.set(cache_key, data)
           return data
   ```

3. **Configuration Updates** (`altman_zscore/common/config.py`)
   ```python
   class Config:
       # Add new configuration options
       enable_sec_edgar_fallback: bool = True
       sec_edgar_cache_ttl_days: int = 7  # SEC data changes less frequently
       
       # Load from environment variables
       def __init__(self):
           self.enable_sec_edgar_fallback = self._get_env_bool(
               "ENABLE_SEC_EDGAR_FALLBACK", True
           )
           self.sec_edgar_cache_ttl_days = self._get_env_int(
               "SEC_EDGAR_CACHE_TTL_DAYS", 7
           )
   ```

### Output Enhancements

1. **Report Generator Updates** (`altman_zscore/layers/output_generation/report_generator.py`)
   ```python
   def _generate_report_metadata(self, data, ticker):
       metadata = super()._generate_report_metadata(data, ticker)
       
       # Add data source information
       metadata["data_source"] = data.get("data_source", "fmp")
       if metadata["data_source"] == "edgar":
           metadata["data_source_note"] = "Data retrieved from SEC EDGAR (company may be delisted)"
           
       return metadata
   ```

2. **Logging Enhancements** (`altman_zscore/common/logging_config.py`)
   ```python
   def log_data_source(logger, ticker, source):
       """Log the data source used for analysis."""
       if source == "edgar":
           logger.info(f"[{ticker}] Using SEC EDGAR data (company may be delisted)")
       else:
           logger.debug(f"[{ticker}] Using primary FMP data source")
   ```

## Testing Strategy

1. **Unit Testing**
   - Test fallback detection logic
   - Test SEC EDGAR data parsing
   - Test data normalization between sources

2. **Integration Testing**
   - Test complete pipeline with known delisted companies
   - Test handling of edge cases (partial data availability)
   - Test performance impact of fallback mechanism

3. **Validation Testing**
   - Compare Z-Score results between data sources for consistency
   - Validate bankruptcy predictions for historical cases
   - Test retail model validation with actual bankruptcy cases

## Dependencies & Requirements

1. **External Dependencies**
   - SEC EDGAR API access
   - CIK lookup table for ticker-to-CIK mapping
   - XBRL parser for SEC filing data extraction

2. **Internal Dependencies**
   - Cache management system
   - Data normalization utilities
   - Enhanced error handling

## Risk Assessment

1. **Technical Risks**
   - SEC EDGAR data structure changes could break parsing
   - Performance degradation with complex SEC filings
   - Inconsistencies between data sources affecting Z-Score

2. **Mitigation Strategies**
   - Regular validation of SEC EDGAR parser
   - Performance monitoring and optimization
   - Comprehensive testing with both data sources

## Implementation Timeline

| Phase | Description | Target Version | Timeline |
|-------|-------------|----------------|----------|
| Planning & Design | Finalize architecture and implementation details | N/A | Complete |
| Phase 1: Core Integration | Basic fallback functionality | v4.7.0 | 2 weeks |
| Phase 2: Optimization | Performance improvements | v4.8.0 | 3 weeks |
| Phase 3: Advanced Features | Enhanced user experience | v4.9.0 | 4 weeks |

## Success Criteria

1. Successfully analyze at least 90% of delisted retail companies in test portfolio
2. Maintain performance within 20% of original pipeline for active companies
3. No material differences in Z-Score calculations between data sources
4. Clear indication of data source in all reports and logs
5. Comprehensive test coverage for all fallback scenarios

## Conclusion

Implementing SEC EDGAR as a fallback data source will significantly enhance the Altman Z-Score project's capabilities, particularly for bankruptcy prediction validation and historical analysis. This feature directly supports the retail validation framework and enables more comprehensive testing of the novel retail Z-Score model with actual bankruptcy cases.

The phased implementation approach allows for iterative development and testing, ensuring that the core functionality is available quickly while more advanced features are developed over time.
