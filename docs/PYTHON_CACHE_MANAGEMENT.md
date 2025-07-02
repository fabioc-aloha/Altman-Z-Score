# Python Cache Management and Dependency Checking Update

## Overview

Updated the retail validation PowerShell script to better handle Python cache management and dependency checking. These changes help resolve issues with stale bytecode files and provide more detailed information about Python module dependencies.

## Changes Made

### 1. Added Cache Management

- Added a new `-ClearCache` parameter to clear Python cache files before running validation
- Added `Clear-PythonCache` function that recursively removes:
  - All `__pycache__` directories
  - All `.pyc` bytecode files
- The function reports the number of cache items removed and approximate disk space recovered

### 2. Enhanced Module Dependency Checking

- Improved the Python module checking process with more detailed output
- Added display of Python's module search path to help debug import issues
- Shows module versions in the check output for easier troubleshooting
- Separated module checks to display more specific error messages
- Added better error handling with stack traces for debugging

### 3. Improved Workflow Integration

- Added support for clearing cache as a standalone operation
- Added documentation and examples for the new parameter
- Updated help information to include the new cache clearing functionality

## Usage

To clear Python cache files and run the SEC EDGAR test:
```powershell
.\retail_validation\scripts\run_retail_validation.ps1 -TestEDGAR SHLDQ -ClearCache
```

To only clear Python cache files:
```powershell
.\retail_validation\scripts\run_retail_validation.ps1 -ClearCache
```

## Troubleshooting

If you encounter module import issues even after installing requirements and clearing the cache:

1. Check the Python path output to ensure the correct environment is being used
2. Verify module versions match requirements in the output
3. Look for any custom environment variables that might be affecting Python's module search path
4. Try completely reinstalling the problematic packages

This update makes it easier to diagnose and resolve Python dependency and import issues when running the retail validation framework.
