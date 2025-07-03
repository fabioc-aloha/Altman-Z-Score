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

**Dashboard & Web Development Guidelines:**
- Use hybrid Python/PowerShell architecture for complex workflows (PowerShell for file ops, Python for data processing)
- Always specify UTF-8 encoding when reading/writing files to support international characters
- Use Jinja2 templating for HTML generation with proper template organization
- Create self-contained HTML files with embedded CSS/JS for better portability
- Implement proper error handling in both PowerShell and Python components
- Use dataclasses in Python for structured data with proper type hints
- Follow separation of concerns: PowerShell for orchestration, Python for logic
