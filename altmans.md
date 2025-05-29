# Plan: Altman Z-Score Model Selection and Calibration Improvements

## Objective
Enhance the Altman Z-Score pipeline to align more closely with academic best practices and Altman’s literature by refining model selection, calibration, and transparency. All model coefficients and thresholds will be centralized in `constants.py` to avoid hard-coding and ensure maintainability.

---

## 1. Use Company Age and IPO Date for Maturity
- **Goal:** Distinguish between early-stage, growth, and mature companies using founding year and IPO date.
- **Actions:**
  - Extend the company profile to include founding year and IPO date (if available).
  - Add logic to classify companies as "early-stage" (e.g., <3 years since IPO), "growth" (3–7 years), or "mature" (>7 years).
  - Use this classification to influence model selection and reporting.

## 2. Industry-Specific Thresholds and Coefficients
- **Goal:** Apply industry-calibrated Z-Score coefficients and thresholds.
- **Actions:**
  - Expand `constants.py` to include per-industry (SIC) model coefficients and thresholds, using WRDS/Compustat or open data.
  - Refactor model selection logic to pull all coefficients and thresholds from `constants.py`.
  - Remove all hard-coded values from code; reference only the centralized constants.

## 3. Adjust for International/Emerging Markets
- **Goal:** Use the EM model and region-specific thresholds for non-US and emerging-market companies.
- **Actions:**
  - Refine country/region detection in the company profile.
  - Store EM model coefficients and thresholds in `constants.py`.
  - Ensure the model selection logic uses these for flagged companies.

## 4. Consider Size and Leverage
- **Goal:** Flag results for very large/small or highly leveraged companies.
- **Actions:**
  - Add logic to check total assets and leverage ratios.
  - If outside typical ranges, add a warning or footnote in the report.

## 5. Document All Overrides and Assumptions
- **Goal:** Increase transparency and auditability.
- **Actions:**
  - Log and report all model/threshold overrides in the output report context.
  - Add a section to the report listing all assumptions and rationale for model selection.

## 6. Regularly Update Calibration
- **Goal:** Keep coefficients and thresholds current with recent bankruptcy data.
- **Actions:**
  - Document a process for updating `constants.py` with new calibration data.
  - Add a version/date field to each model/threshold set in `constants.py` for traceability.

---

## Implementation Status (as of 2025-05-29)

### v2.2 Model Selection & Calibration Overhaul
- All model coefficients, thresholds, and metadata are now centralized in `src/altman_zscore/computation/constants.py`.
- Company maturity (early-stage, growth, mature) is robustly integrated into model selection logic.
- Model selection logic uses industry, SIC, public/private status, region, and maturity.
- The dispatcher in `compute.py` dynamically handles any model key present in `MODEL_COEFFICIENTS`, including new/custom and SIC-specific keys, using the original formula and logging the override.
- NotImplementedError is only raised for truly unknown model keys.
- Reporting and override context are fully logged for transparency.
- All main model constants and thresholds match Altman literature and best practices.
- Structure supports easy addition of new models, coefficients, and thresholds.
- All changes are documented in PLAN.md and TODO.md; DECISIONS.md is deprecated.

---

## Implementation Steps
1. **Refactor `constants.py`:**
   - Move all model coefficients and thresholds (including per-industry and EM) into this file.
   - Add metadata (version, source, date) for each model/threshold set.
2. **Update Company Profile:**
   - Add founding year and IPO date fields.
   - Update maturity classification logic.
3. **Refactor Model Selection Logic:**
   - Always use `constants.py` for coefficients and thresholds.
   - Add logic for age/IPO-based maturity, industry, and region.
4. **Enhance Reporting:**
   - Add transparency section for overrides/assumptions.
   - Add warnings for size/leverage outliers.
5. **Testing and Documentation:**
   - Add/expand tests for new logic.
   - Update documentation and usage examples.
6. **Calibration Update Process:**
   - Document how to update `constants.py` with new data.

---

## References
- Altman, E. I. (1968, 2000, 2017). Various works on Z-Score models.
- WRDS/Compustat bankruptcy and industry benchmark data.
- Recent academic literature on Z-Score calibration and international adaptation.

---

**All future model changes must be made in `constants.py` and referenced throughout the codebase. No hard-coded coefficients or thresholds are allowed.**
