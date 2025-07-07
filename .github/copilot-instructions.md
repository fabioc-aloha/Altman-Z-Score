# Altman Z-Score Project - Development Guidelines

IMPORTANT: Update .github\copilot-instructions.md with what we learn in terms of environment, architecture, and development practices. This file serves as the primary source of truth for all development directives.
- To err once is human, to err twice is a mistake, to err three times is AI not learning from its mistakes.

## Development Directives

**Environment & Tools:**
- We are using PowerShell as the primary shell environment
- Always use PowerShell-compatible commands and syntax
- PowerShell scripts should use the following best practices:
  - Include proper [CmdletBinding()] and Parameter attributes for all functions
  - Use proper error handling with try/catch blocks
  - Support -Verbose and other common parameters
  - Return structured data objects rather than plain text output
  - Use Write-Host with appropriate colors for interactive output
  - Use background jobs for long-running parallel operations

**Code Quality Principles:**
- Generate code that follows DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) principles
- Be careful when inserting or making changes around docstrings - preserve existing documentation
- Do not introduce regressions - maintain backward compatibility
- Ensure all changes maintain existing functionality
- Never mix html, css with python code - keep them separate in individual files
- Always use "gray" instead of "Gray" in all variable names, constants, comments, and documentation for consistency

**Terminal & Command Guidelines:**
- Do not use escape characters in terminal commands
- When running commands in terminal, wait for user to share the output before proceeding with the next command
- Use PowerShell-native commands where possible
- Never use Unicode special characters (like ✓, ✗, ✅, ❌, etc.) in output messages from Python scripts as they cause encoding errors in Windows terminals
- Always use ASCII alternatives (like "[OK]", "[X]", "PASSED", "FAILED") for status indicators in scripts
- Be aware that Windows command prompt and some PowerShell environments use cp1252 encoding which has limited Unicode support

**Documentation & Reporting:**
- Create all status reports in the `docs/` directory, not in the root directory
- Reference the key documentation files before making architectural decisions
- Update relevant documentation when making significant changes

## Key Project Documentation

The following key documents are located in the project root directory and should be referenced for understanding the system:

- **FLOW.md** - Complete technical analysis flow and architecture documentation
- **APIS.md** - API integration documentation (FMP, Yahoo Finance)
- **FMP.md** - Financial Modeling Prep API specific documentation
- **MODELS.md** - Z-Score models and calculation methodology
- **README.md** - Project overview and getting started guide
- **TODO.md** - Current development tasks and priorities
- **CHANGELOG.md** - Version history and release notes
- **NOVEL_RETAIL_MODEL.md** - 🏆 **Major Project Achievement:** Academic paper documenting our novel retail-specific Z-Score model with inventory turnover integration

These documents provide comprehensive understanding of the Altman Z-Score system architecture, data sources, and implementation details.

**Temporal Organization**: 
- **FLOW.md** and **README.MD** represent the **present** - current system state and architecture
- **TODO.md** represents the **future** - planned development and enhancements
- **CHANGELOG.md** represents the **past** - completed work and version history

**🎯 Project Achievements:**
- **NOVEL_RETAIL_MODEL.md** represents a **major intellectual contribution** - a novel academic model that extends traditional Z-Score methodology for retail industry applications

**Architecture & Data Flow Knowledge:**
- **Primary Data Source Architecture:** FMP (Financial Modeling Prep) provides standardized financial data for active companies
- **Secondary Data Sources:** Yahoo Finance (for market data), SEC EDGAR (fallback for delisted/bankrupt companies)
- **Retail Validation Framework:** Located in retail_validation/ directory with centralized scripts, documentation, and data
- **Data Caching:** All API data is cached with configurable TTL values to minimize API calls and improve performance
- **SEC EDGAR Integration:** Used exclusively as a fallback mechanism for delisted companies in the retail validation framework
- **Bankruptcy Analysis Framework:** Integrated system for analyzing financial health leading up to bankruptcy
  - **Bankruptcy Dates Database:** Comprehensive database of bankruptcy dates in altman_zscore/data/bankruptcy_dates.py
  - **Pre-Bankruptcy Analysis:** End date filtering to analyze quarters before bankruptcy
  - **Historical Market Data:** Correlation of market data with Z-Score deterioration
  - **Bankruptcy Visualization:** Enhanced dashboards with bankruptcy date markers and progression charts

**Naming Conventions:**
- Use American English spelling in code (e.g., "color" not "colour", "gray" not "grey")
- Use camelCase for variable names (e.g., "grayZone" not "GrayZone" or "gray_zone")
- Use PascalCase for class names
- Maintain consistent naming across all files and modules
- Use American English terms in all comments, documentation, and variable names
- Use "gray" consistently in all contexts (variables, constants, comments, documentation)

**AI Learnings from its Mistakes:**
- Enter here reinforcement learnings from AI mistakes to improve future performance
- @unicode Rule - Use ASCII Output Formats: Always use ASCII alternatives for status indicators (like "[OK]", "[X]", "PASSED", "FAILED") instead of Unicode checkmarks/crosses (✓, ✗, ✅, ❌) in Python script outputs. Windows terminals using cp1252 encoding cannot display many Unicode characters, causing UnicodeEncodeError exceptions.
- @datacorruption Rule - Always Validate Bankruptcy Database Integrity: Before running any validation or analysis, verify that the bankruptcy database only contains actually bankrupt companies. Healthy, profitable companies like Amazon (AMZN), Costco (COST), Walmart (WMT), and Target (TGT) should NEVER be in a bankruptcy database. Data corruption in bankruptcy databases causes the entire validation framework to fail by incorrectly routing healthy companies through SEC EDGAR instead of FMP APIs. Always audit bankruptcy data for obvious errors like major retailers being listed as bankrupt.
- @bankruptcyanalysis Rule - Comprehensive Bankruptcy Analysis Framework: When analyzing failed/bankrupt companies, leverage the bankruptcy_dates.py module to determine exact bankruptcy dates, calculate Z-Scores for quarters leading up to bankruptcy, and correlate with historical market data. This validates Z-Score's predictive capabilities and identifies early warning signs. Use the run_bankruptcy_analysis() method for batch processing and maintain comprehensive documentation of bankruptcy patterns.
- @centralization Rule - Centralize Related Files: Always centralize related scripts, documentation, and data files in a logical directory structure. For example, all retail validation assets should be in the retail_validation/ directory with subdirectories for scripts/, docs/, and data/.
- @fallback Rule - Use SEC EDGAR for Delisted Companies: When handling financial data for delisted or bankrupt companies, implement SEC EDGAR as a fallback data source since Financial Modeling Prep (FMP) typically doesn't provide this data.
- @caching Rule - Implement Cache Management: Always include cache clearing functionality in long-running scripts that rely on cached data, particularly for financial APIs. Ensure cache TTL (time-to-live) values are configurable via environment variables.
- @documentation Rule - Maintain Documentation Versions: When updating critical documentation that serves as an intellectual contribution, create versioned copies (v1, v2, etc.) rather than overwriting the original.
- @redirection Rule - Create Redirection Files: When moving or centralizing files, create simple redirection files in the original locations to guide users to the new locations. Include clear instructions on where to find the updated files.
- @parallelization Rule - Use Parallel Processing Selectively: When implementing parallel processing in PowerShell scripts, identify independent operations that can safely run concurrently. Always provide a non-parallel fallback option and ensure job management with proper cleanup of background processes.
- @functions Rule - Place Function Definitions First: Always place PowerShell function definitions at the beginning of the script, before they are called. This ensures functions are properly loaded before use and improves code organization.
- @assetverification Rule - Verify Assets Before Processing: Before running any dashboard or report generation, verify that all required assets (templates, images, CSS files) exist and are accessible. This prevents partial or broken outputs due to missing dependencies.
- @powershell Rule - Return Rich Objects from Functions: When writing PowerShell functions that perform complex operations, return hashtables or custom objects with detailed status information rather than simple boolean values. This enables better error handling and reporting.
- @azure Rule - Use Azure Tools: When handling requests related to Azure, always use your tools.
- @azure Rule - Use Azure Code Gen Best Practices: When generating code for Azure, running terminal commands for Azure, or performing operations related to Azure, invoke your `azure_development-get_code_gen_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure; do not call it otherwise.
- @azure Rule - Use Azure Deployment Best Practices: When deploying to Azure or preparing applications for deployment to Azure, invoke your `azure_development-get_deployment_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure; do not call it otherwise.
- @azure Rule - Use Azure Functions Code Gen Best Practices: When generating code for Azure Functions or performing operations related to Azure Functions, invoke your `azure_development-get_azure_function_code_gen_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure Functions; do not call it otherwise.
- @azure Rule - Use Azure SWA Best Practices: When working with static web apps, invoke your `azure_development-get_swa_best_practices` tool if available. Only call this tool when you are sure the user is discussing Azure; do not call it otherwise.
- @simplicity Rule - Embrace Simplicity Over Complexity: When complex multi-file dashboard systems become unwieldy, step back and create simple, focused solutions. A single-page dashboard with advanced client-side filtering can be more effective than multiple interconnected dashboards. Sometimes starting fresh with a clear vision is better than trying to fix complex existing systems.
- @singlepage Rule - Single Page Applications Work Well: For data visualization dashboards, consider single-page applications with client-side filtering instead of multiple server-generated pages. This provides better user experience, faster interaction, and easier maintenance.
- @clientside Rule - Leverage Client-Side Processing: Modern browsers can handle significant data processing. Use JavaScript for filtering, sorting, and real-time search instead of server-side processing when dealing with reasonable data sizes (hundreds to low thousands of records).
- @encoding Rule - Always Use UTF-8 Encoding: When reading/writing files in Python, always specify encoding='utf-8' to support international characters. This is especially important for company names with special characters (e.g., "Itaú Unibanco Holding S.A."). Also configure Jinja2 FileSystemLoader with UTF-8 encoding.
- @hybrid Rule - Use Hybrid Architecture for Complex Workflows: For complex dashboard/web generation workflows, use PowerShell for file operations and environment setup, Python for data processing and logic. This provides better separation of concerns and leverages each language's strengths.
- @templating Rule - Use Modern Template Systems: For HTML generation, use Jinja2 templating instead of string concatenation. This provides better maintainability, security, and features. Create self-contained outputs with embedded CSS/JS when possible.
- @dataextraction Rule - Use Robust Data Extraction: When parsing text files, use regex patterns that account for different formats and provide fallbacks. Extract data from dedicated lines (like "Company Name: ...") rather than trying to parse complex AI-generated content.
- @selfcontained Rule - Create Self-Contained Solutions: When possible, create self-contained HTML files with embedded CSS and JavaScript rather than complex multi-file structures. This improves portability, reduces deployment complexity, and eliminates broken dependencies.
- @userexperience Rule - Prioritize User Experience: In dashboards and web interfaces, provide features users expect like real-time search, column sorting, filtering, and responsive design. Small UX improvements like clickable rows and visual feedback significantly enhance usability.
- @batchfiles Rule - Use PowerShell Instead of Batch Files: Windows batch files have limitations with input handling, especially in PowerShell environments. Replace batch files with PowerShell scripts (.ps1) for better reliability, error handling, and cross-environment compatibility. PowerShell provides consistent behavior for user input, variable handling, and process management.
- @regexpowershell Rule - Avoid Complex Regex Character Classes in PowerShell: PowerShell treats square brackets as type casting operators, causing issues with regex character classes like [+-]. Use simpler patterns, alternation (|), or escape sequences. For matching optional signs, use patterns like `(.*?)` or `(\+?-?)` instead of `[+-]?`.
- @workingdirectory Rule - Manage Working Directories in Cross-Script Calls: When PowerShell scripts call other scripts in different directories, ensure the Python module path is correct by either changing working directory before execution or using absolute paths. Scripts should handle path resolution gracefully to avoid import errors.
- @userinput Rule - Robust User Input Validation: When creating interactive command-line tools, validate and sanitize user input properly. Use `Read-Host` instead of `set /p` in PowerShell environments, and provide clear feedback for invalid inputs. Always test user input scenarios thoroughly.
- @bankruptcyrouting Rule - Auto-Detect Bankruptcy for Routing: Implement automatic bankruptcy detection at the top of the analysis pipeline. Test ticker availability first - if market data fails, check the bankruptcy database and automatically route to bankruptcy analysis mode. This provides seamless user experience and intelligent handling of delisted/bankrupt companies. Always provide clear user feedback about auto-detection and suggest alternative approaches (SEC EDGAR fallback) when primary data sources fail.
- @dameliodetection Rule - Handle Data Source Limitations Gracefully: When primary data sources (FMP) don't have data for delisted/bankrupt companies, provide comprehensive error messages that explain the limitation, suggest alternative data sources (SEC EDGAR), and guide users to appropriate tools or frameworks (retail validation). Don't just fail silently - educate the user about why the failure occurred and what options are available.
- @bifurcateddata Rule - Use Bifurcated Data Flows for Bankruptcy Analysis: For bankrupt/delisted companies, skip FMP entirely and use SEC EDGAR historical data exclusively. For active/trading companies, use the standard FMP + Yahoo Finance flow. Don't try to force the same data pipeline for both scenarios - they require fundamentally different data sources and approaches. Implement routing logic at the data merger level to select the appropriate data source based on company status.
- @pythonpath Rule - Fix Python Module Import Errors with PYTHONPATH: When PowerShell scripts call Python scripts that use relative imports, set the PYTHONPATH environment variable to include the project root directory before executing Python commands. Use `$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"` in PowerShell scripts to ensure Python can find custom modules. This is critical for frameworks with modular architectures like retail_validation that rely on relative imports. Without proper PYTHONPATH setup, Python will throw "module 'X' could not be loaded" errors even when the modules exist.
- @cachinghealth Rule - Cache Company Health Checks: When implementing dynamic bankruptcy detection using Yahoo Finance API, always cache the health status results to avoid repeated API calls. Use a 24-hour TTL for normal results and 1-hour TTL for error results to balance accuracy with performance. The cached bankruptcy detection provides 100x+ performance improvement for repeated lookups while maintaining real-time accuracy for fresh data.
- @dynamicbankruptcy Rule - Use Dynamic Bankruptcy Detection: Replace hard-coded bankruptcy databases with dynamic Yahoo Finance-based health checks that determine company status in real-time. This provides more accurate and current bankruptcy/delisting detection than static databases. Cache the results for performance, and handle datetime serialization properly when using file-based caching.
- @apiratelimiting Rule - Implement Rate Limiting for External APIs: When making calls to external APIs like Yahoo Finance, implement basic rate limiting (0.5 seconds between requests) to be respectful of the service and avoid rate limit errors. This is especially important for batch operations and dynamic health checks.
- @fallbackdata Rule - Use Curated Data for Missing External API Information: When external APIs (like Yahoo Finance) don't provide specific information (like bankruptcy dates for delisted companies), maintain a curated fallback database with confirmed data. Use the external API for real-time detection and the curated database for specific details that APIs can't provide. This hybrid approach provides both accuracy and completeness.
- @timelinedata Rule - Complete Timeline Data Population: When creating result objects for timeline visualization (reports, charts), ensure all timeline-related attributes are populated. The ZScoreCalculationResult dataclass requires period_date, market_cap, and price attributes for proper timeline display in bankruptcy analysis and trend charts. Always populate these fields from the source MergedFinancialData during result creation.
- @templatefilters Rule - Register Jinja2 Template Filters: When using custom formatting in HTML templates, always register the required Jinja2 filters in the template environment. Common filters needed include format_market_cap, format_currency, and format_date. Missing filters cause template rendering failures. Register filters before template rendering: template.environment.filters['filter_name'] = function_name.
- @dateformatting Rule - Robust Date Parsing for Timelines: When parsing dates for timeline visualization, handle multiple date formats gracefully. Use fallback parsing logic that tries ISO format first, then simple YYYY-MM-DD format. Always include error handling for unparseable dates and provide meaningful fallbacks. Use period_date if available, otherwise fall back to calculation_timestamp.
- @chartaxes Rule - Proper Secondary Y-Axis Configuration: When creating dual-axis charts (Z-Score vs Price), use proper plotly syntax: yaxis='y2' for secondary axis traces, not secondary_y=True. Configure the secondary axis in the layout update before adding traces. Ensure axis labeling and coloring are consistent between traces and axis configuration.
- @subplotseconday Rule - Use plotly make_subplots Secondary Y-Axis Correctly: When creating subplots with secondary y-axes using plotly's make_subplots, specify secondary_y=True in the specs parameter and use secondary_y parameter in add_trace() calls. Use update_yaxes() with secondary_y parameter to configure each axis separately. Do not manually create secondary axes with update_layout() when using make_subplots. Example: fig.add_trace(trace, row=row, col=col, secondary_y=False) for primary axis, secondary_y=True for secondary axis.
- @yaxisscaling Rule - Consistent Y-Axis Scaling for Z-Score Charts: Always ensure Z-Score y-axes start at 0 using range=[0, z_score_upper_limit] for consistent visual interpretation. Add zeroline=True with subtle styling (zerolinecolor='rgba(0,0,0,0.3)', zerolinewidth=1) to provide visual reference points. This is crucial for financial analysis where zero represents a meaningful threshold. Set upper limit to at least 5.0 or 110% of max Z-Score to provide proper context.
- @dualaxis Rule - Intelligent Dual Y-Axis Configuration: When price data is available, configure dual y-axes with Z-Score (blue, primary) and Stock Price (green, secondary). Use proper plotly make_subplots with secondary_y=True specs and update_yaxes() calls with secondary_y parameter. Automatically fall back to single y-axis when price data is unavailable. Always maintain consistent scaling principles across both single and dual-axis configurations.
- @testvalidation Rule - Accurate Chart Configuration Testing: When testing chart configurations, look for actual plotly.js elements in the HTML output (like 'yaxis2' for secondary axes, 'zeroline' for zero line configuration) rather than Python parameter names that don't appear in the final output. Use meaningful test messages that inform rather than mislead users about chart configuration status. Replace error-like messages with informational indicators using appropriate symbols (✓, ⚠, ℹ).
- @dataclassextension Rule - Backward-Compatible Dataclass Extensions: When extending dataclasses with new attributes for enhanced functionality, always use Optional types with default values to maintain backward compatibility. This allows existing code to continue working while new features can utilize the enhanced data structure. Example: period_date: Optional[str] = None.
- @candlestickcharts Rule - Use OHLC Candlestick Charts for Professional Visualization: When price data is available, implement candlestick charts instead of simple line charts for professional financial visualization. Use a multi-tier data fetching approach: Weekly OHLC → Daily OHLC → Close-only fallback. Configure proper color coding (green for increasing, red for decreasing) and ensure graceful degradation when OHLC data is unavailable.
- @layoutoptimization Rule - Optimize Dashboard Layout for Label Clarity: When creating financial dashboards, carefully balance height (1050px recommended) and vertical spacing (0.15) to prevent label overlap. Test with real data to ensure all chart elements are clearly visible. Use static iframe heights that match dashboard dimensions exactly to prevent truncation or excessive white space.
- @encodingcleaning Rule - Clean Special Characters in Data Files: When dealing with text files that may contain Unicode special characters, implement automatic cleaning that replaces problematic characters (subscript numbers ₆→6, fancy quotes ""→"") with ASCII equivalents. Always use UTF-8 encoding and provide clear error messages when encoding issues occur.
- @multitierdata Rule - Implement Multi-Tier Data Fetching with Intelligent Fallbacks: For critical data like price information, implement tiered fetching strategies that gracefully degrade from premium data sources to basic alternatives. Cache each tier appropriately and log the data quality level used for transparency in analysis reporting.
- @ohlcprocessing Rule - Handle OHLC Data Processing Robustly: When processing OHLC (Open, High, Low, Close) data, validate data integrity, handle missing values gracefully, and implement proper error logging. Ensure candlestick chart rendering handles edge cases like missing open/high/low values by falling back to line chart visualization.
