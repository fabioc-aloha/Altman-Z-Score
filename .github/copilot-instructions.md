# Altman Z-Score Project - Development Guidelines

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
- **FLOW.md** represents the **present** - current system state and architecture
- **TODO.md** represents the **future** - planned development and enhancements
- **CHANGELOG.md** represents the **past** - completed work and version history

**🎯 Project Achievements:**
- **NOVEL_RETAIL_MODEL.md** represents a **major intellectual contribution** - a novel academic model that extends traditional Z-Score methodology for retail industry applications

**Naming Conventions:**
- Use American English spelling in code (e.g., "color" not "colour", "gray" not "Gray")
- Use camelCase for variable names (e.g., "grayZone" not "GrayZone" or "gray_zone")
- Use PascalCase for class names
- Maintain consistent naming across all files and modules
- Use American English terms in all comments, documentation, and variable names
- Use "gray" consistently in all contexts (variables, constants, comments, documentation)