# PowerShell Validation Script Update

## Overview

Updated the prerequisite check in the PowerShell validation script (`run_retail_validation.ps1`) to better handle the required Python modules for SEC EDGAR integration. This complements the earlier updates to `requirements.txt`.

## Changes Made

1. **Improved Module Checking**:
   - Split the module check into two parts:
     - Basic modules (pandas, numpy) that are always required
     - SEC EDGAR specific modules (bs4, aiohttp) that are only checked when using SEC EDGAR functionality

2. **Conditional Checking**:
   - Only checks for SEC EDGAR modules when using `-UseSECEDGAR` or `-TestEDGAR` parameters
   - Provides more specific error messages for each module group

3. **Better Error Reporting**:
   - Added detailed exception message output for troubleshooting

## Benefits

1. **Targeted Dependency Validation**: The script now only checks for the modules needed for the specific functionality being used.

2. **Clearer Error Messages**: If modules are missing, the error message now specifies which modules need to be installed.

3. **Reduced False Negatives**: By separating checks, we avoid failing the entire validation when only certain modules are missing.

## Next Steps

After this update, running the SEC EDGAR test with:
```powershell
.\retail_validation\scripts\run_retail_validation.ps1 -TestEDGAR SHLDQ
```

Should properly check for the required modules and either:
1. Continue if all modules are available
2. Fail with a specific error message about which modules are missing

This update completes the integration of the SEC EDGAR module check into the validation framework's prerequisite checks.
