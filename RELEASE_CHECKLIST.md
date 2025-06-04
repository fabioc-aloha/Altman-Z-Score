# Release Checklist — v2.8.1 (DRY Refactor)

- [ ] Update version number to 2.8.1 in all relevant files (README.md, setup.py, etc.)
- [ ] Update CHANGELOG.md with v2.8.1 and summary: "Major DRY refactor—centralized all error handling, constants, and logic."
- [ ] Ensure all tests pass (CI and local)
- [ ] Manually test all major features and outputs
- [ ] Review and update documentation (README.md, PLAN.md, TODO.md, LEARNINGS.md)
- [ ] Check for dead code, unused files, and unnecessary dependencies
- [ ] Tag the release in git (e.g., v2.8.1)
- [ ] Push all commits and tags to remote
- [ ] Announce release (if public)

---

## Pre-Release Validation
- [ ] Run full test suite
- [ ] Validate outputs for at least 3 tickers (success, partial, error)
- [ ] Review logs for warnings/errors
- [ ] Confirm all new/changed files are included in the repo

---

## Post-Release
- [ ] Monitor for bug reports or regressions
- [ ] Update roadmap and backlog
