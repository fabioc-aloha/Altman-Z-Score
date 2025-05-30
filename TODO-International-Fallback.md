# Altman Z-Score: International & Fallback Logic Enhancement Plan

This checklist tracks the implementation of robust field mapping, fallback logic, error handling, and international/emerging market support. Each step is modular—stop after any phase if diminishing returns are reached.

---

## 1. Expand Field Mapping Synonyms and Contextual Matching
- [x] Expand `FIELD_SYNONYMS` in `src/altman_zscore/api/openai_client.py` to include:
    - [x] "Turnover" (UK/EU) for sales
    - [x] "Share Capital", "Shareholder Funds" for equity
    - [x] "Profit Before Tax", "Operating Profit" for EBIT
    - [x] "Net Assets" for total assets
    - [x] "Current Liab." for current liabilities
    - [x] "Ret. Earnings" for retained earnings
    - [x] Other common international/IFRS/abbreviated field names

## 2. Improve Fallback and Partial Analysis Logic
- [x] If any canonical field is missing after mapping, proceed with partial Z-Score analysis
- [x] Clearly flag/report missing fields and omitted/estimated Z-Score components
- [x] Add a warning section in the report about missing fields and reliability impact

## 3. Add Fallback to Alternative Data Sources
- [x] If primary data (Yahoo/SEC) is missing/incomplete, attempt backup sources (Alpha Vantage, Stooq, etc.)
- [x] Log and report all fallback attempts/results in the output and report

## 4. Enhance Error Handling and Logging
- [ ] Replace broad `except Exception:` blocks with specific exception handling and detailed logging
- [x] Ensure all errors in field mapping, data fetching, and validation are logged and reported in the output
- [ ] Centralize logging configuration if not already done

## 5. Refine International/EM Company Support
- [x] Refine company profile logic to detect country/region from XBRL, Yahoo, or SEC metadata
- [x] Use this to select the correct Z-Score model (e.g., EM model for emerging markets) and field mapping rules
- [x] Ensure `constants.py` includes EM and region-specific coefficients/thresholds
- [x] Document all model/threshold overrides in the report

## 6. Expand and Automate Testing
- [x] Add/expand tests in `scripts/test_openai_field_mapping.py` for international tickers and edge cases
- [x] For each test, print/log which fields were mapped, which were missing, and fallback logic used
- [x] After improving mapping/fallback logic, rerun pipeline for previously failed tickers and document results in `LEARNINGS.md` and `output/`

## 7. Documentation
- [x] Update `PLAN.md`, `TODO.md`, and `README.md` to describe new fallback logic, expanded synonym support, and internationalization improvements
- [ ] Add examples of partial analysis and fallback reporting to docs and sample reports

## 8. Make All Prompt and Mapping Logic User-Editable
- [x] Ensure all prompt/mapping logic is user-editable in `src/prompts/`
- [x] Encourage users to add new synonyms or mapping rules as needed

## 9. Codespaces Compatibility
- [x] Ensure all changes are Codespaces-compatible and tested in that environment

---

Check off each item as it is completed. Stop after any phase if further work yields diminishing returns.
