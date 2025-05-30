# Altman Z-Score Release Checklist

## Version: 2.4 (2025-05-30)

---

## Pre-Release
- [x] Update version numbers in all relevant files (README, main.py, etc.)
- [x] Review and update CHANGELOG/PLAN.md for all major changes
- [x] Have the user manually review a sample of reports for formula/threshold accuracy
- [x] Update documentation for new/changed features

## Major Features/Changes in v2.4
- [x] Reporting layer always uses coefficients/thresholds from calculation (override_context)
- [x] No hard-coded formulas or thresholds in reporting output
- [x] Full fidelity for SIC/industry overrides and custom calibrations
- [x] Model/threshold overrides and assumptions are logged in report
- [x] All model constants and thresholds centralized in computation/constants.py
- [x] Robust error handling and logging throughout pipeline

## Release
- [x] Tag release in git (v2.4)
- [x] Push to remote repository
- [x] Announce release and update documentation links

---

## Post-Release
- [x] Monitor for bug reports or regressions
- [x] Solicit feedback from users
- [x] Plan next milestone in PLAN.md

---

*Checklist last reset for v2.4 (2025-05-30)*
