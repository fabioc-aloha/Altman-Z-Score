# Release Checklist v3.2.0 (2025-06-16)

- [x] Update version in README.md, main.py, and TODO.md
- [x] Update CHANGELOG.md with new features, bugfixes, and breaking changes
- [ ] Ensure all tests pass (unit, integration, CLI)
- [ ] Run `generate_readme_table.py` and update README sample reports table
- [x] Verify all new/changed features are documented in README.md and TODO.md
- [x] Update requirements.txt if dependencies changed
- [x] Review and update TODO.md for next phase
- [ ] Tag release in git and push to remote
- [ ] Announce release (if applicable)

---

## Pre-Release Validation
- [ ] Run full test suite
- [ ] Validate CLI outputs for at least 3 tickers (success, partial, error)
  - Test multiple tickers in one command (e.g., `python main.py MSFT AAPL BBDO`)
  - Verify graceful continuation when one ticker fails
  - Check candlestick visualization in charts
- [ ] Review logs for warnings/errors
  - Verify improved error messages for missing financial data
  - Check multi-ticker analysis error handling
- [ ] Confirm all new/changed files are included in the repo
- [ ] Scan the output directory and update the table of available reports in README.md

## Version 3.2.0 Specific Checks
- [ ] Verify candlestick legend matches chart style
- [ ] Test multi-ticker analysis with various scenarios:
  - All tickers succeed
  - One ticker fails, others continue
  - Missing financial data handling
- [ ] Check visualization improvements:
  - Candlestick representation in legends
  - Up/down candlestick distinction
  - Weekly price range display

---

## Post-Release
- [ ] Monitor for bug reports or regressions
- [ ] Update roadmap and backlog in TODO.md