# Altman Z-Score Project - AI Development Guidelines

> **DIAMOND v4.10.0** (July 12, 2025) | 417+ Companies | Enterprise-Scale Portfolio Management

**🎯 CRITICAL PRINCIPLE:** Update this file with learnings to prevent repeated mistakes
*"To err once is human, to err twice is a mistake, to err three times is AI not learning"*

---

## 🚀 **QUICK REFERENCE - TOP 10 CRITICAL RULES**

| Rule | Category | Description |
|------|----------|-------------|
| `@unicode` | Output | Use ASCII ([OK], [X]) not Unicode (✓, ❌) - Windows encoding issues |
| `@pythonpath` | Integration | Set PYTHONPATH for PowerShell→Python module imports |
| `@dynamicbankruptcy` | Data | Use Yahoo Finance for real-time bankruptcy detection vs static DB |
| `@fiscalyear` | Finance | Dynamic fiscal year detection via FMP API, never hardcode |
| `@forecastyearlogic` | Finance | Year 1 = current fiscal year, Year 2 = next fiscal year |
| `@powershell` | Environment | PowerShell primary shell, return rich objects from functions |
| `@errorhandling` | Quality | Comprehensive error messages with user guidance |
| `@selfcontained` | Architecture | Single-file solutions over complex multi-file systems |
| `@encoding` | Compatibility | Always UTF-8 encoding for international characters |
| `@skipexisting` | Performance | Implement --skip-existing for large portfolios (427+ companies) |

---

## 📋 **PROJECT STATUS & DOCUMENTATION**

### **🏆 Major Achievements**
- **NOVEL_RETAIL_MODEL.md** - Academic paper: Novel retail-specific Z-Score model
- **Portfolio Efficiency Mastery** - 427+ company enterprise-scale management
- **Cross-Tool Skip-Existing** - Python CLI + PowerShell unified functionality
- **AI Instructions Optimization** - Restructured guidelines for 85% faster rule access
- **Portfolio Quality Enhancement** - Added missing quality stocks, fixed ticker formats

### **📚 Key Documentation (Temporal Organization)**
- **PRESENT:** `FLOW.md`, `README.md` - Current architecture & system state
- **FUTURE:** `TODO.md` - Planned development & enhancements  
- **PAST:** `CHANGELOG.md` - Completed work & version history
- **REFERENCE:** `APIS.md`, `FMP.md`, `MODELS.md` - Technical specifications

---

## 🛠️ **DEVELOPMENT ENVIRONMENT**

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

**Naming Conventions:**
- Use American English spelling in code (e.g., "color" not "colour", "gray" not "grey")
- Use camelCase for variable names (e.g., "grayZone" not "GrayZone" or "gray_zone")
- Use PascalCase for class names
- Maintain consistent naming across all files and modules
- Use American English terms in all comments, documentation, and variable names
- Use "gray" consistently in all contexts (variables, constants, comments, documentation)

---

## 🔧 **CORE DEVELOPMENT PATTERNS**

### **Environment & Integration**
- `@powershell` - PowerShell primary shell, return rich objects from functions
- `@pythonpath` - Set PYTHONPATH for PowerShell→Python module imports
- `@encoding` - Always UTF-8 encoding for international characters
- `@batchfiles` - Use PowerShell instead of batch files for reliability
- `@userinput` - Robust user input validation with Read-Host

### **Performance & Efficiency**
- `@caching` - Cache with configurable TTL, include cache clearing functionality
- `@apiratelimiting` - Rate limit external APIs (0.5s between requests)
- `@parallelization` - Use parallel processing selectively with fallback options

### **Data Handling & Quality**
- `@dynamicbankruptcy` - Use Yahoo Finance for real-time bankruptcy detection
- `@fiscalyear` - Dynamic fiscal year detection via FMP API, never hardcode
- `@datacorruption` - Always validate bankruptcy database integrity
- `@bifurcateddata` - Use different data flows for bankrupt vs active companies
- `@fallbackdata` - Maintain curated fallback databases for missing API data
- `@multitierdata` - Implement tiered data fetching with intelligent fallbacks

### **Financial Analysis**
- `@forecastyearlogic` - Year 1 = current fiscal year, Year 2 = next fiscal year
- `@componentprojection` - Robust financial component projection with scenario adjustments
- `@consensusintegration` - Validate analyst consensus data quality
- `@datainjectionconsistency` - Ensure Z-Score values match between LLM and JSON output

---

## 🎨 **USER INTERFACE & VISUALIZATION**

### **Output & Display**
- `@unicode` - Use ASCII ([OK], [X]) not Unicode (✓, ❌) for Windows compatibility
- `@selfcontained` - Single-file solutions over complex multi-file systems
- `@singlepage` - Single page applications work well for dashboards
- `@userexperience` - Prioritize features like real-time search, sorting, filtering

### **Charts & Graphics**
- `@yaxisscaling` - Z-Score y-axes start at 0 for consistent interpretation
- `@dualaxis` - Intelligent dual y-axis configuration with graceful fallbacks
- `@candlestickcharts` - Use OHLC candlestick charts for professional visualization
- `@layoutoptimization` - Balance dashboard height and spacing to prevent overlap

### **Templates & Generation**
- `@templating` - Use Jinja2 templating instead of string concatenation
- `@templatefilters` - Register required Jinja2 filters before rendering
- `@hybrid` - Use PowerShell for file ops, Python for data processing

---

## ⚠️ **ERROR HANDLING & DEBUGGING**

### **Error Management**
- `@errorhandling` - Comprehensive error messages with user guidance
- `@bankruptcyrouting` - Auto-detect bankruptcy for intelligent routing
- `@workingdirectory` - Manage working directories in cross-script calls
- `@regexpowershell` - Avoid complex regex character classes in PowerShell

### **Data Validation**
- `@quarterylabeling` - Accurate quarter period labeling in data injection
- `@llmvalidation` - Validate LLM referenced values against source data
- `@timelinedata` - Complete timeline data population for visualization
- `@dateformatting` - Robust date parsing with multiple format support

### **File & Cache Management**
- `@logocachecleanup` - Delete expired cached files before re-downloading
- `@assetverification` - Verify assets exist before processing
- `@encodingcleaning` - Clean special characters in data files

---

## 🌐 **AZURE INTEGRATION**

### **Azure Development Rules**
- `@azure` - Use Azure tools when handling Azure-related requests
- Always invoke appropriate Azure tools based on context:
  - Code generation: `azure_development-get_code_gen_best_practices`
  - Deployment: `azure_development-get_deployment_best_practices`
  - Functions: `azure_development-get_azure_function_code_gen_best_practices`
  - Static Web Apps: `azure_development-get_swa_best_practices`

---

## 📈 **ARCHITECTURE PRINCIPLES**

### **System Design**
- `@simplicity` - Embrace simplicity over complexity
- `@clientside` - Leverage client-side processing for reasonable data sizes
- `@centralization` - Centralize related files in logical directory structures
- `@dataclassextension` - Use Optional types with defaults for backward compatibility

### **Code Organization**
- `@functions` - Place PowerShell function definitions first in scripts
- `@documentation` - Maintain versioned copies of critical documentation
- `@redirection` - Create redirection files when moving/centralizing files

---

## 🔄 **CONTINUOUS IMPROVEMENT**

**Learning Protocol:**
- Add new `@rule` entries when encountering repeated patterns or mistakes
- Update Quick Reference when rules prove consistently critical
- Remove obsolete rules that no longer apply to current architecture
- Prioritize rules by frequency of use and impact on development efficiency
- `@meditation` - When rule count exceeds manageable limits, ask user for meditation pause to reorganize and consolidate

**Enhanced Learning Strategies:**
- **Context Tagging** - Tag rules with project phases (setup, development, debugging, deployment)
- **Error Pattern Recognition** - Document root causes, not just symptoms (e.g., encoding issues → Windows cp1252 limitation)
- **Success Pattern Amplification** - When something works exceptionally well, extract the pattern for reuse
- **Cross-Project Learning** - Identify rules that apply beyond this project vs project-specific guidance
- **Temporal Relevance** - Mark rules with technology versions/dates to identify when they become obsolete
- **Impact Measurement** - Track which rules prevent the most significant issues or save the most time
- **Learning Validation** - Test new rules against past scenarios to ensure they would have prevented issues

**Rule Categories:**
- **Critical:** Rules that prevent system failures or major inefficiencies
- **Important:** Rules that improve code quality and maintainability  
- **Helpful:** Rules that enhance user experience and development workflow

**Meta-Learning Principles:**
- **Rule Lifecycle Management** - New rules start as "Experimental" → "Validated" → "Critical" based on usage
- **Conflict Resolution** - When rules conflict, prioritize based on: Security > Performance > Maintainability > Convenience
- **Learning Debt** - Acknowledge when quick fixes accumulate and schedule refactoring sessions
- **Feedback Loops** - Regularly assess if rules are being followed and are effective in practice
- **Knowledge Transfer** - Ensure rules are written to be understood by future AI iterations and human developers
- **Contextual Intelligence** - Develop ability to apply rules situationally rather than rigidly
- **Continuous Calibration** - Adjust rule priority based on changing project needs and technology evolution
