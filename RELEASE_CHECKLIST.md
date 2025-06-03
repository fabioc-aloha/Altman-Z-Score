# Release Checklist

- [ ] Update version number in all relevant files (README.md, setup.py, etc.)
- [ ] Update CHANGELOG.md with new version and summary of changes
- [ ] Ensure all tests pass (CI and local)
- [ ] Manually test all major features and outputs
- [ ] Review and update documentation (README.md, PLAN.md, TODO.md, LEARNINGS.md)
- [ ] Check for dead code, unused files, and unnecessary dependencies
- [ ] Tag the release in git (e.g., vX.Y.Z)
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
