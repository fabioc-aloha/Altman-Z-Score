# Release Checklist v3.0.1 (2025-06-07)

- [ ] Update version in README.md, main.py, and TODO.md
- [ ] Update CHANGELOG.md with new features, bugfixes, and breaking changes
- [ ] Ensure all tests pass (unit, integration, CLI)
- [ ] Run `generate_readme_table.py` and update README sample reports table
- [ ] Verify all new/changed features are documented in README.md and TODO.md
- [ ] Update requirements.txt if dependencies changed
- [ ] Review and update TODO.md for next phase
- [ ] Tag release in git and push to remote
- [ ] Announce release (if applicable)

---

## Pre-Release Validation
- [ ] Run full test suite
- [ ] Validate CLI outputs for at least 3 tickers (success, partial, error)
- [ ] Review logs for warnings/errors
- [ ] Confirm all new/changed files are included in the repo
- [ ] Scan the output directory and update the table of available reports in README.md (ensure all tickers in output/ are included, sorted alphabetically, and only those with all four report files are listed)

---

## Post-Release
- [ ] Monitor for bug reports or regressions
- [ ] Update roadmap and backlog in TODO.md