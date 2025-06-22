# Sample Data

This directory contains sample JSON data files used for testing, validation, and development of the Altman Z-Score analysis pipeline.

## F-Score Complete Data
Sample F-Score analysis results for various companies:
- `complete_fscore_aapl.json` - Apple Inc. complete F-Score analysis
- `complete_fscore_bbd.json` - Bombardier Inc. complete F-Score analysis  
- `complete_fscore_itub.json` - Itaú Unibanco complete F-Score analysis
- `complete_fscore_jpm.json` - JPMorgan Chase complete F-Score analysis
- `complete_fscore_msft.json` - Microsoft complete F-Score analysis
- `complete_fscore_tsla.json` - Tesla Inc. complete F-Score analysis

## Test Data Files
Development and debugging data samples:
- `debug_fmp_ratios_raw.json` - Raw FMP ratios data for debugging
- `fmp_estimates_test_aapl.json` - FMP estimates test data for Apple
- `fmp_estimates_test_sono.json` - FMP estimates test data for Sonos
- `fscore_data_test_aapl.json` - F-Score test data for Apple

## Usage

These files are used by:
- Development scripts for testing API integrations
- Validation scripts for data structure verification  
- Example data for documentation and demos
- Unit tests requiring sample data

## Data Format

All files contain JSON-formatted financial data structures matching the APIs and analysis outputs used by the pipeline.

**Note:** This data is for development/testing purposes only and may not reflect current market conditions.
