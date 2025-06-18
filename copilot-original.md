# LLM Copilot Instructions: Altman Z-Score Report Analysis & Troubleshooting

## Quick Start Guide for LLMs

**Essential Tools Available:**
- `list_dir` - List files and folders in a directory
- `read_file` - Read file contents (specify line range)
- `file_search` - Search for files by pattern
- `grep_search` - Search for text within files
- `run_in_terminal` - Execute commands (use for testing tickers)
- `create_file` - Create new files (for logging)
- `replace_string_in_file` - Edit existing files
- `insert_edit_into_file` - Insert code into files

**Key Workflow:**
1. Use `list_dir` to identify processed tickers in `output/`
2. For each ticker, use `list_dir` and `read_file` to analyze completeness
3. Use `grep_search` to find error patterns in source code
4. Use `run_in_terminal` to test fixes
5. Use `create_file` to log all findings before making changes

## Task Overview
Analyze all reports generated using `main.py` with start date 2024-01-01, identify successful vs incomplete runs, and troubleshoot the most common issues.

**IMPORTANT:** Use the available VS Code tools (list_dir, read_file, file_search, run_in_terminal, etc.) rather than manual commands. All analysis should be performed using these tools.

## Step 1: Identify Processed Tickers

First, examine the `output/` folder to identify all tickers that were processed:

**Tool to use:** `list_dir` with path `c:\Development\Altman-Z-Score-1\output`

**Example tool call:**
```
Tool: list_dir
Parameters: {"path": "c:\\Development\\Altman-Z-Score-1\\output"}
```

This will return all directories (tickers) that have been processed. Document each ticker found and proceed to analyze their completeness.

**Tool to use:** `create_file` to start logging your analysis

**Example tool call:**
```
Tool: create_file
Parameters: {
  "filePath": "c:\\Development\\Altman-Z-Score-1\\Copilot_Analysis_Session.md",
  "content": "# Copilot Analysis Session\n\n**Start Time:** [Current timestamp]\n\n## Tickers Found:\n[List tickers from list_dir results]\n\n## Analysis Progress:\n- [ ] Ticker inventory complete\n- [ ] File completeness analysis\n- [ ] Issue pattern identification\n- [ ] Root cause analysis\n- [ ] Solution development\n"
}
```

## Step 2: Define Success Criteria

A 100% successful run should contain ALL of the following files for each ticker:
- `company_info.json` - Company profile data
- `{TICKER}_logo.png` - Company logo
- `yf_info.json` - Yahoo Finance info
- `sec_facts_raw.json` - SEC EDGAR raw data
- `financials_raw.json` - Raw financial statements
- `financials_quarterly.json` - Processed quarterly data
- `zscore_{TICKER}.csv` - Z-Score calculations by quarter
- `zscore_{TICKER}.json` - Structured Z-Score data
- `zscore_{TICKER}_metadata.json` - Analysis metadata
- `zscore_{TICKER}_trend.png` - Z-Score trend chart
- `zscore_{TICKER}_zscore_full_report.md` - LLM-generated analysis report
- `weekly_prices.csv` - Stock price data
- `weekly_prices.json` - Stock price data (JSON format)
- `llm_commentary_prompt.txt` - LLM prompt used for analysis

## Step 3: Systematic Analysis Template

For each ticker found, use this analysis template:

### Ticker: [TICKER_NAME]
**Status:** [COMPLETE/INCOMPLETE/FAILED]

**Files Present:**
```
[ ] company_info.json
[ ] {TICKER}_logo.png  
[ ] yf_info.json
[ ] sec_facts_raw.json
[ ] financials_raw.json
[ ] financials_quarterly.json
[ ] zscore_{TICKER}.csv
[ ] zscore_{TICKER}.json
[ ] zscore_{TICKER}_metadata.json
[ ] zscore_{TICKER}_trend.png
[ ] zscore_{TICKER}_zscore_full_report.md
[ ] weekly_prices.csv
[ ] weekly_prices.json
[ ] llm_commentary_prompt.txt
```

**Missing Files:** [List any missing files]

**Data Quality Checks:**
- Check `zscore_{TICKER}.csv` for valid Z-Score calculations:
  ```bash
  Get-Content "output/{TICKER}/zscore_{TICKER}.csv" | Select-Object -First 10
  ```
- Look for quarters with `valid=True` vs `valid=False`
- Check if Z-Score values are reasonable (typically 0-10 range)
- Verify date range covers 2024-01-01 onwards

**Chart Analysis:**
- Verify `zscore_{TICKER}_trend.png` exists and was recently generated
- Check file size (should be >50KB for a proper chart)
- If chart is missing, note the pipeline step that likely failed

**Error Indicators:**
- Check for error messages in any JSON files
- Look for empty or truncated files
- Check timestamps to ensure recent generation

## Step 4: Automated Analysis Process

Use these tools systematically to assess all tickers:

### 4.1: Identify All Tickers
**Tool to use:** `list_dir` with path `c:\Development\Altman-Z-Score-1\output`

### 4.2: For Each Ticker Found, Run This Analysis Sequence

**Replace {TICKER} with the actual ticker symbol in each path:**

#### File Existence Check:
**Tool to use:** `list_dir` with path `c:\Development\Altman-Z-Score-1\output\{TICKER}`

**Example tool call:**
```
Tool: list_dir
Parameters: {"path": "c:\\Development\\Altman-Z-Score-1\\output\\MSFT"}
```

This will show all files present for the ticker. Check against the required files list:
- `company_info.json`
- `{TICKER}_logo.png`
- `yf_info.json`
- `sec_facts_raw.json`
- `financials_raw.json`
- `financials_quarterly.json`
- `zscore_{TICKER}.csv`
- `zscore_{TICKER}.json`
- `zscore_{TICKER}_metadata.json`
- `zscore_{TICKER}_trend.png`
- `zscore_{TICKER}_zscore_full_report.md`
- `weekly_prices.csv`
- `weekly_prices.json`
- `llm_commentary_prompt.txt`

#### File Size Check:
**Tool to use:** `read_file` with specific file paths to check if files exist and have content.

For key files, use `read_file` with a small line range (e.g., lines 1-5) to verify the file exists and has content:
- `c:\Development\Altman-Z-Score-1\output\{TICKER}\zscore_{TICKER}.csv`
- `c:\Development\Altman-Z-Score-1\output\{TICKER}\zscore_{TICKER}_zscore_full_report.md`

For PNG files, use `list_dir` on the ticker folder and look for files ending in `.png`.

#### Data Quality Check:
**Tool to use:** `read_file` to examine the Z-Score CSV content

**Example tool call:**
```
Tool: read_file
Parameters: {
  "filePath": "c:\\Development\\Altman-Z-Score-1\\output\\MSFT\\zscore_MSFT.csv",
  "startLineNumber": 1,
  "endLineNumber": 20
}
```

Look for:
- Headers in the first row
- Columns with `valid=True` vs `valid=False`
- Reasonable Z-Score values (typically 0-10 range)
- Date range covering 2024-01-01 onwards

**Tool to use:** `grep_search` to count valid vs invalid entries

**Example tool call:**
```
Tool: grep_search
Parameters: {
  "query": "valid=True",
  "includePattern": "output/MSFT/zscore_MSFT.csv",
  "isRegexp": false
}
```

Search for both `"valid=True"` and `"valid=False"` patterns to count successful vs failed quarters.

### 4.3: Document Results for Each Ticker

For each ticker, create this analysis entry in your troubleshooting log:

```markdown
### Ticker: [TICKER_NAME]
**Status:** [COMPLETE/INCOMPLETE/FAILED]

**Files Present (✓ = True, ✗ = False):**
- [ ] company_info.json
- [ ] yf_info.json  
- [ ] sec_facts_raw.json
- [ ] financials_raw.json
- [ ] financials_quarterly.json
- [ ] zscore_{TICKER}.csv
- [ ] zscore_{TICKER}.json
- [ ] zscore_{TICKER}_metadata.json
- [ ] zscore_{TICKER}_trend.png
- [ ] zscore_{TICKER}_zscore_full_report.md
- [ ] weekly_prices.csv
- [ ] weekly_prices.json
- [ ] llm_commentary_prompt.txt
- [ ] {TICKER}_logo.png

**File Sizes:**
- Chart PNG: [SIZE] bytes
- Z-Score CSV: [SIZE] bytes  
- Report MD: [SIZE] bytes

**Data Quality:**
- Total quarters in CSV: [NUMBER]
- Valid Z-Score calculations: [NUMBER]
- Invalid/missing calculations: [NUMBER]
- Completion rate: [PERCENTAGE]%

**Missing Files:** [List any missing files]

**Issues Noted:** [Any problems observed]
```

## Step 5: Common Issue Categories

Based on typical pipeline failures, categorize issues into:

### Category A: Data Fetching Issues
- **Symptoms:** Missing `sec_facts_raw.json`, `yf_info.json`, or financial data files
- **Likely Causes:** API rate limits, network issues, invalid tickers
- **Investigation:** Check file sizes, look for error messages in JSON files

### Category B: Z-Score Computation Issues  
- **Symptoms:** Z-Score CSV has many `valid=False` entries
- **Likely Causes:** Missing financial fields, data quality issues
- **Investigation:** Examine error messages in CSV, check financial data completeness

### Category C: Chart Generation Issues
- **Symptoms:** Missing or corrupted trend PNG files
- **Likely Causes:** Plotting library issues, insufficient data for charting
- **Investigation:** Check file sizes, verify Z-Score data availability

### Category D: LLM Report Issues
- **Symptoms:** Missing or incomplete markdown reports
- **Likely Causes:** API issues, prompt formatting problems
- **Investigation:** Check prompt files, verify OpenAI integration

## Step 6: Troubleshooting Analysis

After analyzing all tickers, create a summary:

```markdown
## Analysis Summary

**Total Tickers Processed:** [NUMBER]
**Fully Successful (100%):** [NUMBER] ([PERCENTAGE]%)
**Partially Successful (80-99%):** [NUMBER] ([PERCENTAGE]%)
**Failed/Incomplete (<80%):** [NUMBER] ([PERCENTAGE]%)

## Most Common Issues (Ranked by Frequency)

1. **[Issue Type]:** [NUMBER] tickers affected
   - **Examples:** [Ticker1, Ticker2, ...]
   - **Pattern:** [Describe common pattern]
   - **Root Cause:** [Likely cause]

2. **[Issue Type]:** [NUMBER] tickers affected
   - **Examples:** [Ticker1, Ticker2, ...]
   - **Pattern:** [Describe common pattern]
   - **Root Cause:** [Likely cause]

[Continue for top 3-5 issues]
```

## Step 7: Code Investigation Commands

For the most common issue identified, use these tools to investigate:

**Tool to use:** `grep_search` to search for error patterns:

**Example tool call:**
```
Tool: grep_search
Parameters: {
  "query": "error",
  "includePattern": "src/altman_zscore/**/*.py",
  "isRegexp": false
}
```

**Tool to use:** `read_file` to examine specific modules related to the most common issue:

**Example tool calls for data fetching issues:**
```
Tool: read_file
Parameters: {
  "filePath": "c:\\Development\\Altman-Z-Score-1\\src\\altman_zscore\\data_fetching\\financials.py",
  "startLineNumber": 1,
  "endLineNumber": 50
}
```

**Key files to examine based on issue type:**

For data fetching issues:
- `c:\Development\Altman-Z-Score-1\src\altman_zscore\data_fetching\financials.py`
- `c:\Development\Altman-Z-Score-1\src\altman_zscore\api\yahoo_helpers.py`
- `c:\Development\Altman-Z-Score-1\src\altman_zscore\api\sec_client.py`

For Z-Score computation issues:
- `c:\Development\Altman-Z-Score-1\src\altman_zscore\computation\compute.py`
- `c:\Development\Altman-Z-Score-1\src\altman_zscore\core\one_stock_analysis.py`

For chart generation issues:
- `c:\Development\Altman-Z-Score-1\src\altman_zscore\plotting\plotting_main.py`

For LLM report issues:
- Use `file_search` to find OpenAI-related files:
```
Tool: file_search
Parameters: {"query": "**/*openai*"}
```

## Step 8: Solution Development

Once the most common issue is identified:

1. **Reproduce the Issue:**
   **Tool to use:** `run_in_terminal`
   
   **Example tool call:**
   ```
   Tool: run_in_terminal
   Parameters: {
     "command": "python main.py FAILING_TICKER --date 2024-01-01 --log-level DEBUG",
     "explanation": "Running debug analysis on failing ticker",
     "isBackground": false
   }
   ```

2. **Analyze Debug Logs:** Look for error patterns, API failures, or data processing issues in the terminal output

3. **Develop Fix:** Based on root cause analysis

4. **Test Fix:** 
   **Tool to use:** `run_in_terminal`
   
   **Example tool call:**
   ```
   Tool: run_in_terminal
   Parameters: {
     "command": "python main.py FAILING_TICKER --date 2024-01-01",
     "explanation": "Testing fix with previously failing ticker",
     "isBackground": false
   }
   ```

5. **Validate:** Use `list_dir` and `read_file` tools to ensure all expected files are generated correctly

## Step 9: Log Troubleshooting Analysis

**IMPORTANT:** Before implementing any code changes, create a detailed troubleshooting log in `Copilot_Troubleshoot.md`. This provides an audit trail and reasoning for all changes.

### Create Troubleshooting Log File

**Tool to use:** `create_file`

**Example tool call:**
```
Tool: create_file
Parameters: {
  "filePath": "c:\\Development\\Altman-Z-Score-1\\Copilot_Troubleshoot.md",
  "content": "# Copilot Troubleshooting Analysis Log\n\n**Analysis Date:** [CURRENT_DATE]\n**Analysis Start Time:** [TIMESTAMP]\n**Data Range Analyzed:** 2024-01-01 onwards\n**Total Tickers in Output Folder:** [NUMBER]\n\n## Discovery Phase Results\n\n### Ticker Inventory\n[List all tickers found in output/ directory]\n\n### Success Rate Summary\n- **Complete Success (100%):** [NUMBER] tickers\n  - Tickers: [List successful tickers]\n- **Partial Success (80-99%):** [NUMBER] tickers  \n  - Tickers: [List partially successful tickers]\n- **Failed/Incomplete (<80%):** [NUMBER] tickers\n  - Tickers: [List failed tickers]\n"
}
```
# Copilot Troubleshooting Analysis Log

**Analysis Date:** [CURRENT_DATE]
**Analysis Start Time:** [TIMESTAMP]
**Data Range Analyzed:** 2024-01-01 onwards
**Total Tickers in Output Folder:** [NUMBER]

## Discovery Phase Results

### Ticker Inventory
[List all tickers found in output/ directory]

### Success Rate Summary
- **Complete Success (100%):** [NUMBER] tickers
  - Tickers: [List successful tickers]
- **Partial Success (80-99%):** [NUMBER] tickers  
  - Tickers: [List partially successful tickers]
- **Failed/Incomplete (<80%):** [NUMBER] tickers
  - Tickers: [List failed tickers]

### File Completion Analysis
[For each ticker, document the completion status using the checklist template]

## Issue Pattern Analysis

### Issue #1: [Most Common Issue Name]
**Frequency:** [X] out of [Y] tickers ([Z]%
**Affected Tickers:** [List]

**Symptoms Observed:**
- [Specific symptom 1]
- [Specific symptom 2]
- [Specific symptom 3]

**Investigation Findings:**
- [Finding 1 with evidence]
- [Finding 2 with evidence]
- [Finding 3 with evidence]

**Error Messages Captured:**
```
[Paste actual error messages found in logs/files]
```

**Files Examined:**
- [List specific files checked]
- [Include file sizes, timestamps, content samples]

**Root Cause Hypothesis:**
[Detailed explanation of what you believe is causing this issue]

**Supporting Evidence:**
- [Evidence point 1]
- [Evidence point 2]
- [Evidence point 3]

**Code Areas Implicated:**
- [File path 1]: [Specific function/method]
- [File path 2]: [Specific function/method]
- [File path 3]: [Specific function/method]

### Issue #2: [Second Most Common Issue]
[Repeat the same analysis structure]

### Issue #3: [Third Most Common Issue]
[Repeat the same analysis structure]

## Deep Dive Investigation

### Code Analysis Performed
[Document specific tools used and their outputs]

**Tools executed:**
- `grep_search` with query "error_pattern" in src/altman_zscore/**/*.py
- Output: [paste grep_search results]

- `read_file` for specific files showing problematic functions
- Files examined: [list file paths]
- Relevant code sections: [paste code snippets from read_file results]

### Debug Test Results
[If you ran debug tests on failing tickers using run_in_terminal]

**Tool used:** `run_in_terminal`
- Command: `python main.py [TICKER] --date 2024-01-01 --log-level DEBUG`
- Results: [summarize debug output from terminal]

## Solution Development

### Proposed Solution for Issue #1
**Problem:** [Clear problem statement]
**Solution Approach:** [High-level solution]
**Files to Modify:** [List files that need changes]
**Specific Changes:** [Detailed code changes needed]
**Risk Assessment:** [Potential risks of the changes]
**Testing Plan:** [How to verify the fix works]

### Proposed Solution for Issue #2
[Repeat structure]

### Proposed Solution for Issue #3
[Repeat structure]

## Impact Assessment

### Expected Improvement
- **Success Rate:** Should improve from [X]% to [Y]%
- **Affected Tickers:** [List tickers expected to be fixed]
- **Risk Factors:** [List any potential negative impacts]

### Implementation Priority
1. **Critical (Implement First):** [Issue affecting most tickers]
2. **High Priority:** [Issue affecting data quality]
3. **Medium Priority:** [Issue affecting user experience]
4. **Low Priority:** [Minor cosmetic issues]

## Pre-Implementation Checklist
- [ ] All issues documented with evidence
- [ ] Root causes identified and verified
- [ ] Solutions designed and reviewed
- [ ] Test plan created
- [ ] Backup plan identified
- [ ] Impact assessment completed

## Next Steps
1. [Specific next action]
2. [Specific next action]
3. [Specific next action]

---
**Analysis Completed:** [TIMESTAMP]
**Ready for Implementation:** [YES/NO]
**Recommended Starting Point:** [Which issue to tackle first]
```

### Log File Creation

**Tool to use:** `create_file`
- Path: `c:\Development\Altman-Z-Score-1\Copilot_Troubleshoot.md`
- Content: Start with the troubleshooting template and populate it systematically as you work through the analysis, **BEFORE** making any code changes.

## Step 10: Final Report Template

Conclude with this structured report:

```markdown
# Altman Z-Score Pipeline Analysis Report

**Analysis Date:** [DATE]
**Data Range:** 2024-01-01 onwards
**Total Tickers Analyzed:** [NUMBER]
**Detailed Analysis:** See `Copilot_Troubleshoot.md` for complete investigation

## Success Rate Summary
- **Complete Success:** [XX]% ([NUMBER] tickers)
- **Partial Success:** [XX]% ([NUMBER] tickers)  
- **Failures:** [XX]% ([NUMBER] tickers)

## Most Critical Issue: [ISSUE_NAME]
**Frequency:** [NUMBER] tickers affected ([XX]% of total)
**Root Cause:** [Brief summary - full details in Copilot_Troubleshoot.md]
**Affected Tickers:** [List]
**Proposed Solution:** [High-level summary - implementation details in troubleshoot log]

## Implementation Priority
1. **High Priority:** [Most common issue - affects XX% of runs]
2. **Medium Priority:** [Second most common - affects XX% of runs]
3. **Low Priority:** [Less frequent issues]

## Recommended Next Steps
1. Review detailed analysis in `Copilot_Troubleshoot.md`
2. Implement solutions in priority order
3. Test fixes with previously failing tickers
4. Update pipeline documentation

## Files Created During Analysis
- `Copilot_Troubleshoot.md` - Complete troubleshooting analysis and solution design
- `analyze_reports.ps1` - Automated analysis script (if created)
- This summary report

**Note:** All code changes should be implemented based on the detailed analysis and solution design documented in `Copilot_Troubleshoot.md`
```

## Implementation Workflow

1. **Analysis Phase:** Complete Steps 1-8 to identify issues
2. **Documentation Phase:** Create detailed `Copilot_Troubleshoot.md` log  
3. **Review Phase:** Review the troubleshooting log for completeness
4. **Implementation Phase:** Apply code changes based on documented solutions
5. **Testing Phase:** Verify fixes work with previously failing tickers
6. **Documentation Phase:** Update pipeline docs with lessons learned

This systematic approach ensures all troubleshooting decisions are documented, reviewable, and traceable before any code modifications are made.

## Example Complete Workflow

Here's a complete example of how to execute this analysis using the available tools:

### Phase 1: Initial Discovery
```
1. Call list_dir with path "c:\Development\Altman-Z-Score-1\output"
2. Create analysis log with create_file
3. For each ticker found, call list_dir on the ticker folder
4. Document findings in the log file
```

### Phase 2: Quality Assessment
```
1. For each ticker, call read_file on zscore_{TICKER}.csv (lines 1-20)
2. Call grep_search to count "valid=True" vs "valid=False" occurrences
3. Call read_file on key report files to check completeness
4. Update analysis log with findings
```

### Phase 3: Issue Investigation
```
1. Call grep_search to find error patterns in source code
2. Call read_file on suspect source files
3. Call run_in_terminal to test failing tickers
4. Document all findings in Copilot_Troubleshoot.md
```

### Phase 4: Solution Implementation
```
1. Use insert_edit_into_file or replace_string_in_file to implement fixes
2. Call run_in_terminal to test fixes
3. Call list_dir and read_file to validate results
4. Update documentation with lessons learned
```

**Remember:** Always use create_file to log your analysis before making any code changes. This ensures a complete audit trail of your troubleshooting process.
