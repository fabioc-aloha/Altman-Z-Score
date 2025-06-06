# Release Checklist v2.9.0 (2025-06-05)

- [x] Update version in README.md and main.py
- [x] Update CHANGELOG.md with new features, bugfixes, and breaking changes
- [x] Ensure all tests pass (unit, integration, CLI)
- [x] Run `generate_readme_table.py` and update README sample reports table
- [x] Verify all new/changed features are documented in README.md and PLAN.md
- [x] Update requirements.txt if dependencies changed
- [x] Review and update PLAN.md and TODO.md for next phase
- [x] Tag release in git and push to remote
- [x] Announce release (if applicable)

---

# Release Checklist — v2.8.6 (CLI Improvements)

- [x] Update version number to 2.8.6 in all relevant files (README.md, main.py)
- [x] Update CHANGELOG.md with v2.8.6 and summary of CLI improvements
- [x] Ensure all tests pass (CI and local)
- [x] Manually test all CLI features and outputs
- [x] Review and update documentation (README.md, PLAN.md, TODO.md, LEARNINGS.md)
    - [x] Ensure CLI usage, arguments, and examples are up to date
    - [x] Integrate any new CLI docstrings or help text into README.md
- [x] Check for dead code, unused files, and unnecessary dependencies
- [x] Tag the release in git (e.g., v2.8.6)
- [x] Push all commits and tags to remote
- [x] Announce release (if public)
- [ ] Scan the output directory and update the table of available reports in README.md (ensure all tickers in output/ are included, sorted alphabetically, and only those with all four report files are listed; use `ls output/` to get the list of folders)

---

## Pre-Release Validation
- [x] Run full test suite
- [x] Validate CLI outputs for at least 3 tickers (success, partial, error)
- [x] Review logs for warnings/errors
- [x] Confirm all new/changed files are included in the repo

---

## Post-Release
- [x] Monitor for bug reports or regressions
- [x] Update roadmap and backlog