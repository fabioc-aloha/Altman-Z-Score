# Vision Alignment

All release criteria and quality checks are guided by the project vision:

> Our goal is to deliver an Altman Z-Score platform that not only matches but surpasses the capabilities of all current and future competitors—open-source or commercial. Every feature, architectural decision, and user experience is designed to set a new industry standard for transparency, extensibility, and actionable financial insight.

See [vision.md](./vision.md) for the full vision statement.

# Altman Z-Score Analysis — Release Checklist (v2.2.2)

This checklist ensures a clean, robust, and well-documented release for version 2.2.2. Mark each item as you complete it. Update for each new version.

---

## Pre-Release
- [x] All version numbers and changelogs updated to 2.2.2 in README.md, PLAN.md, TODO.md, and all documentation.
- [x] LLM prompt files are in `src/prompts/` and user-editable.
- [x] Deprecated code (DOCX export, old references) removed.
- [x] References, attributions, and license info are consistent and correct in all outputs.
- [x] Only one introduction and correct section order in report outputs.
- [x] "Missing" column removed from Raw Data Field Mapping Table.
- [x] Context section renamed to "Analysis Context and Z-Score Model Selection Criteria".
- [x] All tests pass (except for a single fixture warning, documented in LEARNINGS.md).
- [x] .gitignore and example outputs are up to date.
- [x] Example outputs in `output/` reviewed and updated.

## Release
- [x] All changes staged, committed, and pushed to main branch.
- [x] Release tagged as `v2.2.2` on GitHub.
- [x] Release builds and runs from a fresh Codespace.
- [x] Prompt changes reflected at runtime (no restart required).
- [x] LICENSE and attribution double-checked in all outputs.
- [x] `TESTED_COMPANIES.md` is up to date and enforced as a release-blocking item.
- [x] All output companies tracked and versioned.
- [x] Tested companies file is complete and accurate for v2.2.2.

## Post-Release
- [x] Release announced and key changes summarized in GitHub Releases and README.md.
- [x] PLAN.md and TODO.md updated for next version planning.
- [x] Feedback and bug reports solicited from users (see README.md and GitHub Issues).

---

For details on each step, see `README.md`, `PLAN.md`, and `TODO.md`.
