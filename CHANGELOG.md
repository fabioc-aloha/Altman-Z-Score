# Changelog

All notable changes to the Altman Z-Score Analysis Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.4] - 2025-06-03
- Major plotting refactor: plotting.py split into helpers and terminal modules
- Full test coverage for plotting_helpers and plotting_terminal
- Improved error handling and modularity in plotting pipeline
- Updated documentation and version numbers for v2.7.4
- No breaking changes; all outputs and APIs remain stable

## [2.7.3] - 2025-06-03

### Changed
- Codebase cleanup: removed dead code, verified all modules and prompt files are referenced and in use
- Updated documentation and version numbers for v2.7.3
- No breaking changes; all outputs and APIs remain stable

## [2.7.2] - 2025-06-03

### Documentation
- Verified and updated DataFetching.md with comprehensive checkmarks and implementation status
- Added RELEASE_CHECKLIST.md for reproducible release process
- Ensured all documentation files are consistent and up to date

### Technical
- No code changes; documentation and release process improvements only

## [2.7.1] - 2025-06-03

### Added
- Enhanced executive/officer information injection into LLM qualitative analysis
- Improved company profile data integration in reports
- Better error handling for missing officer data in LLM prompts

### Fixed
- Fixed issue with missing officer data in LLM prompts that could cause analysis failures
- Improved data validation for company officer information

### Changed
- Enhanced LLM commentary generation with more comprehensive executive data
- Updated prompts to better handle cases where officer information is unavailable

### Technical
- Improved error handling in `openai_client.py` for missing data scenarios
- Enhanced data fetching robustness in `sec_client.py`
- Updated reporting logic to gracefully handle incomplete officer data

## [2.7.0] - 2025-05-XX

### Added
- Multi-ticker portfolio analysis support
- Enhanced visualization with trend plotting
- Comprehensive financial metrics validation
- Industry-specific Z-Score model selection
- Executive officer data integration

### Enhanced
- Modular architecture with separate data fetching, computation, and reporting layers
- Robust error handling and logging throughout the pipeline
- Comprehensive data validation using Pydantic schemas

## [2.6.0] - 2025-04-XX

### Added
- SEC EDGAR data integration
- Advanced financial metrics computation
- Automated report generation
- Weekly price data analysis

## Earlier Versions

For changes in versions 2.5.0 and earlier, please refer to the git commit history and PLAN.md file.
