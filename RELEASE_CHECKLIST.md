# Altman Z-Score Release Checklist

## Version: 2.7 (2025-06-10)

---

## Pre-Release
- [x] Update version numbers in all relevant files (README, main.py, etc.)
- [x] Review and update CHANGELOG/PLAN.md for all major changes
- [x] Have the user manually review a sample of reports for formula/threshold accuracy
- [x] Update documentation for new/changed features (including SEC EDGAR fallback and error reporting for balance-sheet-only cases)

## Major Features/Changes in v2.7
- [x] Robust fallback to SEC EDGAR for financials if yfinance fails
- [x] Improved error reporting: pipeline now transparently reports when only balance sheet data is available (e.g., TUP), and no Z-Score can be computed due to missing income statement data
- [x] Documentation and release process updated for new fallback and error handling features

## Release
- [x] Tag release in git (v2.7)
- [x] Push to remote repository
- [x] Announce release and update documentation links

---

## Post-Release
- [x] Monitor for bug reports or regressions
- [x] Solicit feedback from users
- [x] Plan next milestone in PLAN.md

---

*Checklist last reset for v2.7 (2025-06-10)*
