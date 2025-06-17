# Copilot.md: LLM Troubleshooting Integration

## Overview
The `copilot.md` file provides comprehensive instructions for LLM Copilot to systematically analyze Altman Z-Score pipeline outputs, identify issues, and troubleshoot problems using VS Code's built-in tools.

## Key Features

### 1. VS Code Tool Integration
- **list_dir**: Inventory processed tickers and analyze file completeness
- **read_file**: Examine output files for data quality and errors
- **grep_search**: Find error patterns in source code and output files
- **run_in_terminal**: Test fixes and validate solutions
- **create_file**: Document analysis findings and troubleshooting steps

### 2. Systematic Analysis Workflow
1. **Discovery Phase**: Identify processed tickers and assess completeness
2. **Quality Assessment**: Evaluate success rates and identify failure patterns
3. **Issue Investigation**: Root cause analysis using code examination
4. **Solution Development**: Test fixes and validate improvements
5. **Documentation**: Mandatory audit trail creation

### 3. Quality Assurance
- **Audit Trail**: Requires creation of `Copilot_Troubleshoot.md` before code changes
- **Evidence-Based**: All findings must be supported by tool outputs
- **Reproducible**: Step-by-step instructions ensure consistent analysis
- **Traceable**: Complete documentation of analysis decisions and reasoning

## Usage Context

### For LLM Copilot
Follow the workflow in `copilot.md` when tasked with:
- Analyzing pipeline output quality
- Troubleshooting ticker analysis failures
- Identifying common error patterns
- Developing and testing fixes

### For Human Developers
The same systematic approach can be applied manually for:
- Pipeline debugging and optimization
- Quality assurance of batch analysis runs
- Understanding failure modes and their causes
- Documenting troubleshooting procedures

## Files Created During Analysis
- `Copilot_Analysis_Session.md` - Session tracking and progress
- `Copilot_Troubleshoot.md` - Detailed analysis log and audit trail
- Various output validation reports as needed

## Integration with Existing Documentation
- **README.md**: References copilot.md in troubleshooting section
- **FLOW.md**: Links to copilot.md for debugging workflows
- **TODO.md**: Documents copilot integration as completed milestone

## Benefits
1. **Consistency**: Standardized analysis approach across all troubleshooting sessions
2. **Completeness**: Ensures no critical analysis steps are skipped
3. **Traceability**: Full audit trail of all decisions and changes
4. **Tool Optimization**: Leverages VS Code's built-in capabilities effectively
5. **Knowledge Transfer**: Systematic approach can be used by both LLMs and humans

This integration represents a significant enhancement to the project's maintainability and debugging capabilities, providing a structured framework for systematic issue analysis and resolution.
