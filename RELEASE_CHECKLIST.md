# Altman Z-Score Analysis — Release Checklist (v2.2.2)

This checklist ensures a clean, robust, and well-documented release for version 2.2.2. Mark each item as you complete it. Update for each new version.

---

## Pre-Release
- [ ] Update version number to 2.2.2 in all relevant files (`README.md`, `PLAN.md`, `TODO.md`, etc.)
- [ ] Update changelogs and documentation for new features and changes
- [ ] Ensure all LLM prompt files are in `src/prompts/` and are user-editable
- [ ] Remove any deprecated or unused code (e.g., DOCX export, old references)
- [ ] Confirm all references, attributions, and license info are consistent and correct
- [ ] Ensure only one introduction and correct section order in report outputs
- [ ] Remove the "Missing" column from the Raw Data Field Mapping Table
- [ ] Rename context section to "Analysis Context and Z-Score Model Selection Criteria"
- [ ] Run all tests and confirm Codespaces compatibility
- [ ] Update LEARNINGS.md 
- [ ] Check if we have any leftover legacy files that could be deleted
- [ ] Ensure .gitignore is up to date
- [ ] Review and update example outputs in `output/`

## Release
- [ ] Stage, commit, and push all changes to the main branch
- [ ] Tag the release as `v2.2.2` on GitHub
- [ ] Verify that the release builds and runs from a fresh Codespace
- [ ] Confirm that prompt changes are reflected at runtime (no restart required)
- [ ] Double-check LICENSE and attribution in all outputs
- [ ] **TESTED_COMPANIES.md is up to date:** All companies in `output/` are listed, with correct outcome and notes. This is a release-blocking item.
- [ ] After running the pipeline for new companies or regions, update `output/TESTED_COMPANIES.md` to reflect the latest tested tickers and outcomes. This ensures documentation and results remain accurate for all users and contributors.
- [ ] **Tested Companies File Up To Date (v2.2.2):**
    - Confirm that every company with an output folder in `output/` is listed in `output/TESTED_COMPANIES.md`.
    - Update the Outcome, Script Version, and Notes/Issues columns for all new or changed tickers.
    - Remove any companies from the table if their output folder has been removed.
    - This is a release-blocking item: do not release unless this file is complete and accurate.

## Post-Release
- [ ] Announce the release and summarize key changes
- [ ] Update `PLAN.md` and `TODO.md` for next version planning
- [ ] Solicit feedback and bug reports from users

---

For details on each step, see `README.md`, `PLAN.md`, and `TODO.md`.
