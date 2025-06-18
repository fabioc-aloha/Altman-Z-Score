# ## Pre-Release Tasks
- [x] Update version in README.md, main.py, and TODO.md
- [x] Update CHANGELOG.md with new features, bugfixes, and breaking changes
- [x] Ensure all tests pass (unit, integration, CLI)
- [ ] Run `generate_readme_table.py` and update README sample reports table
- [x] Verify all new/changed features are documented in README.md and TODO.md
- [x] Update requirements.txt if dependencies changed
- [x] Review and update TODO.md for next phaseChecklist v3.4.0 (2025-06-17)

## Pre-Release Tasks
- [x] Update version in README.md, main.py, and TODO.md
- [x] Update CHANGELOG.md with new features, bugfixes, and breaking changes
- [x] Ensure all tests pass (unit, integration, CLI)
- [x] Run `generate_readme_table.py` and update README sample reports table
- [x] Verify all new/changed features are documented in README.md and TODO.md
- [x] Update requirements.txt if dependencies changed
- [x] Review and update TODO.md for next phase

## Pre-Release Validation
- [x] Run full test suite
- [x] Validate CLI outputs for at least 3 tickers (success, partial, error)
  - Test multiple tickers in one command (e.g., `python main.py MSFT AAPL BBDO`)
  - Verify graceful continuation when one ticker fails
  - Check that `--date` argument works correctly (replacing old `--start`)
- [x] Review logs for warnings/errors
  - Verify clean output with improved error handling
  - Check multi-ticker analysis error handling
- [x] Confirm all new/changed files are included in the repo
- [x] Scan the output directory and update the table of available reports in README.md

## Version 3.4.0 Specific Checks
- [x] Verify CLI argument change from `--start` to `--date` works correctly
- [x] Test `--date` parameter validation and error messages
- [x] Confirm all documentation examples use `--date` instead of `--start`
- [x] Verify backward compatibility warnings are clear for users
- [x] Test CIK cache and lookup fallback functionality
- [x] Validate error handling improvements for SEC API calls

## Release Tasks
- [ ] Tag release in git and push to remote
- [ ] Announce release (if applicable)
- [ ] Update CLI_UPDATE_SUMMARY.md if needed

## Post-Release
- [ ] Monitor for bug reports or regressions
- [ ] Update roadmap and backlog in TODO.md
- [ ] Collect user feedback on CLI argument change

---

## Release Notes Template

### Version 3.4.0 Highlights
- **CLI Improvement**: Changed `--start` to `--date` for better user experience
- **Error Handling**: Enhanced CIK lookup and cache management
- **Documentation**: Comprehensive update of all documentation files

### Breaking Changes
- CLI argument `--start` has been replaced with `--date`
- Users must update scripts and commands to use the new argument name