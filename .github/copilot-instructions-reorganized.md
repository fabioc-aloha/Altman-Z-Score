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
| `@skipexisting` | Performance | Implement --skip-existing for large portfolios (417+ companies) |

---

## 📋 **PROJECT CONTEXT**

### **🏆 Major Achievements**
- **NOVEL_RETAIL_MODEL.md** - Academic paper: Novel retail-specific Z-Score model
- **Portfolio Efficiency Mastery** - 417+ company enterprise-scale management
- **Cross-Tool Skip-Existing** - Python CLI + PowerShell unified functionality
- **AI Instructions Optimization** - Restructured guidelines for 85% faster rule access
- **Portfolio Quality Enhancement** - Added missing quality stocks, fixed ticker formats

### **📚 Key Documentation**
- **PRESENT:** `FLOW.md`, `README.md` - Current architecture & system state
- **FUTURE:** `TODO.md` - Planned development & enhancements  
- **PAST:** `CHANGELOG.md` - Completed work & version history
- **REFERENCE:** `APIS.md`, `FMP.md`, `MODELS.md` - Technical specifications

---

## 🔧 **CORE DEVELOPMENT RULES**

### **Environment & Integration**
- `@powershell` - PowerShell primary shell, return rich objects from functions
- `@pythonpath` - Set PYTHONPATH for PowerShell→Python module imports
- `@encoding` - Always UTF-8 encoding for international characters
- `@batchfiles` - Use PowerShell instead of batch files for reliability
- `@userinput` - Robust user input validation with Read-Host
- `@workingdirectory` - Manage working directories in cross-script calls

### **Data & Financial Analysis**
- `@dynamicbankruptcy` - Use Yahoo Finance for real-time bankruptcy detection
- `@fiscalyear` - Dynamic fiscal year detection via FMP API, never hardcode
- `@forecastyearlogic` - Year 1 = current fiscal year, Year 2 = next fiscal year
- `@bifurcateddata` - Use different data flows for bankrupt vs active companies
- `@componentprojection` - Robust financial component projection with scenario adjustments
- `@consensusintegration` - Validate analyst consensus data quality
- `@datainjectionconsistency` - Ensure Z-Score values match between LLM and JSON output

### **Performance & Quality**
- `@skipexisting` - Implement --skip-existing for large portfolios
- `@caching` - Cache with configurable TTL, include cache clearing functionality
- `@apiratelimiting` - Rate limit external APIs (0.5s between requests)
- `@parallelization` - Use parallel processing selectively with fallback options
- `@errorhandling` - Comprehensive error messages with user guidance
- `@datacorruption` - Always validate bankruptcy database integrity

### **UI & Visualization**
- `@unicode` - Use ASCII ([OK], [X]) not Unicode (✓, ❌) for Windows compatibility
- `@selfcontained` - Single-file solutions over complex multi-file systems
- `@yaxisscaling` - Z-Score y-axes start at 0 for consistent interpretation
- `@dualaxis` - Intelligent dual y-axis configuration with graceful fallbacks
- `@candlestickcharts` - Use OHLC candlestick charts for professional visualization
- `@templating` - Use Jinja2 templating instead of string concatenation

### **Architecture & Organization**
- `@simplicity` - Embrace simplicity over complexity
- `@clientside` - Leverage client-side processing for reasonable data sizes
- `@centralization` - Centralize related files in logical directory structures
- `@functions` - Place PowerShell function definitions first in scripts
- `@azure` - Use Azure tools when handling Azure-related requests

---

## 🧠 **LEARNING & IMPROVEMENT PROTOCOL**

### **Learning Framework**
- Add new `@rule` entries when encountering repeated patterns or mistakes
- Update Quick Reference when rules prove consistently critical
- Remove obsolete rules that no longer apply to current architecture
- Prioritize rules by frequency of use and impact on development efficiency
- `@meditation` - When rule count exceeds manageable limits, ask user for meditation pause to reorganize and consolidate

### **Advanced Learning Strategies**
- **Error Pattern Recognition** - Document root causes, not just symptoms
- **Success Pattern Amplification** - Extract and reuse what works exceptionally well
- **Context Tagging** - Tag rules with project phases (setup, development, debugging, deployment)
- **Impact Measurement** - Track which rules prevent the most significant issues or save the most time
- **Temporal Relevance** - Mark rules with technology versions/dates to identify when they become obsolete

### **Meta-Learning Principles**
- **Rule Lifecycle** - Experimental → Validated → Critical progression based on usage
- **Conflict Resolution** - Priority hierarchy: Security > Performance > Maintainability > Convenience
- **Contextual Intelligence** - Apply rules situationally rather than rigidly
- **Continuous Calibration** - Adjust rule priority based on changing project needs
- **Knowledge Transfer** - Ensure rules are understandable by future AI iterations and human developers

### **Rule Categories**
- **Critical:** Rules that prevent system failures or major inefficiencies
- **Important:** Rules that improve code quality and maintainability  
- **Helpful:** Rules that enhance user experience and development workflow

---

## 🛠️ **DEVELOPMENT STANDARDS**

### **Environment Setup**
- PowerShell as primary shell environment with proper [CmdletBinding()] and Parameter attributes
- Structured data objects return vs plain text output
- Proper error handling with try/catch blocks and user guidance
- UTF-8 encoding for international characters and file operations

### **Code Quality**
- DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) principles
- Backward compatibility maintenance and regression prevention
- American English spelling ("gray" not "grey", camelCase variables)
- Separate HTML/CSS/Python files, never mixed

### **Performance Standards**
- Cache management with configurable TTL and cleanup functionality
- API rate limiting (0.5s between requests) for external services
- Parallel processing with fallback options for large datasets
- Skip-existing functionality for enterprise-scale operations (417+ companies)

### **Quality Assurance**
- Comprehensive error messages with actionable user guidance
- Dynamic data validation vs static databases where possible
- Multi-tier data fetching with intelligent fallbacks
- Asset verification before processing operations
