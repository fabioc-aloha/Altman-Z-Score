# Altman Z-Score Release Checklist

## Version: 2.4.1 (2025-05-30)

---

## Pre-Release
- [ ] Update version numbers in all relevant files (README, main.py, etc.)
- [ ] Review and update CHANGELOG/PLAN.md for all major changes
- [ ] Have the user manually review a sample of reports for formula/threshold accuracy
- [ ] Update documentation for new/changed features

## Major Features/Changes in v2.4.1
- [ ] Fixed chart embedding in Markdown reports by properly handling absolute paths
- [ ] Verified chart generation and embedding for all supported tickers
- [ ] Confirmed correct path resolution for both local and GitHub-friendly paths
- [ ] Enhanced error logging for chart generation/embedding
- [ ] Added chart presence validation to pre-release checks

## Release
- [ ] Tag release in git (v2.4.1)
- [ ] Push to remote repository
- [ ] Announce release and update documentation links

---

## Post-Release
- [ ] Monitor for bug reports or regressions
- [ ] Solicit feedback from users
- [ ] Plan next milestone in PLAN.md

---

*Checklist last reset for v2.4.1 (2025-05-30)*
