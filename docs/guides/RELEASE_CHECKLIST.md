# Release Checklist v3.6.0 (2025-06-20)

## Pre-Release Tasks
- [x] Update version in README.md, main.py, and TODO.md
- [x] Update CHANGELOG.md with new features, bugfixes, and breaking changes
- [x] Ensure all tests pass (unit, integration, CLI)
- [ ] Run `generate_readme_table.py` and update README sample reports table
- [x] Verify all new/changed features are documented in README.md and TODO.md
- [ ] Update requirements.txt if dependencies changed
- [ ] Review and update TODO.md for next phase

## Pre-Release Validation
- [ ] Run full test suite
- [ ] Validate CLI outputs for at least 3 tickers (success, partial, error)
  - Test multiple tickers in one command (e.g., `python main.py MSFT AAPL BBDO`)
  - Verify graceful continuation when one ticker fails
  - Check that `--date` argument works correctly
- [ ] Review logs for warnings/errors
  - Verify clean output with improved error handling
  - Check multi-ticker analysis error handling
- [ ] Confirm all new/changed files are included in the repo
- [ ] Scan the output directory and update the table of available reports in README.md

## Version 3.6.0 Specific Checks
- [x] Verify combined logo & name column in portfolio table
- [ ] Test table generation with `generate_readme_table.py`
- [ ] Confirm improved table layout and usability
- [ ] Validate all documentation reflects v3.6.0 status
- [ ] Test banner generation prompt functionality

## Release Tasks
- [ ] Tag release in git and push to remote
- [ ] Announce release
- [ ] Update any deployment scripts if needed

## Post-Release
- [ ] Monitor for bug reports or regressions
- [ ] Update roadmap and backlog in TODO.md
- [ ] Collect user feedback on table layout improvements