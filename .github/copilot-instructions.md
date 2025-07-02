# Altman Z-Score Project - Development Guidelines

IMPORTANT: Update .github\copilot-instructions.md with what we learn in terms of environment, architecture, and development practices. This file serves as the primary source of truth for all development directives.
- To err once is human, to err twice is a mistake, to err three times is AI not learning from its mistakes.

## Development Directives

**Environment & Tools:**
- We are using PowerShell as the primary shell environment
- Always use PowerShell-compatible commands and syntax

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
- Use American English spelling in code (e.g., "color" not "colour", "gray" not "Gray")
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
- @documentation Rule - Maintain Documentation Versions: When updating critical documentation that serves as an intellectual contribution (like NOVEL_RETAIL_MODEL.md), create versioned copies (v1, v2, etc.) rather than overwriting the original.
- @redirection Rule - Create Redirection Files: When moving or centralizing files, create simple redirection files in the original locations to guide users to the new locations. Include clear instructions on where to find the updated files.
