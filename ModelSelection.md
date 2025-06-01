# ModelSelection.md

This document describes the implementation of Altman Z-Score model selection and related data processing within the Altman Z-Score Analysis Platform. All logic is core to deciding which Z-Score variant to compute, validating input data, and ensuring transparency/traceability.

---

## Overview

The platform centers on a hierarchical decision tree to choose the correct Z-Score model based on:

1. **SIC (Industry)**
2. **Emerging Market flag**
3. **Firm maturity (Public vs. Private)**

All model coefficients and thresholds are stored in a centralized configuration module (`computation/constants.py`) so that users can easily see which weights and cutoffs apply. Data fetching relies on a primary Yahoo Finance client with SEC EDGAR as a fallback. A validation layer ensures that required fields are present and that basic accounting identities hold (e.g., Assets = Liabilities + Equity).

---

## 1. Model Selection Algorithm

### 1.1. Core Selection Logic (`src/altman_zscore/computation/model_selection.py`)

The function `select_zscore_model(sic, is_public, is_emerging, maturity)` implements:

1. **Emerging Market Override**

   * If `is_emerging == True`, immediately return `"em"`.
   * (EM always uses book equity and a +3.25 intercept.)

2. **Public vs. Private Check**

   * If `is_public == False` (private), we defer to private variants of whichever industry-specific model applies.
   * If `is_public == True` (public), we use market-equity versions.

3. **Industry (SIC) Check**

   * If `2000 ≤ sic ≤ 3999` → Manufacturing

     * **Public** → return `"original"`
     * **Private** → return `"private"`
     * *(The “private” key corresponds to Altman’s private manufacturing Z′ weights.)*
   * If `4000 ≤ sic ≤ 4999`, or `6000 ≤ sic ≤ 6999`, or `7000 ≤ sic ≤ 8999`, or tech subranges (`3570–3579`, `3670–3679`, `7370–7379`) → Non-manufacturing / Service / Transport / Utilities / Finance / Tech

     * **Public** → return `"service"`
     * **Private** → return `"service_private"`
     * *(“service” and “service\_private” map to Zʺ-public and Zʺ-private.)*

4. **Fallback**

   * If SIC is outside these ranges, default to `"original"` (four-factor manufacturing for a public firm).
   * *(Rare; to avoid crashes if SIC is missing or anomalous.)*

> **Note:** The keys in `MODEL_COEFFICIENTS` include `"original"`, `"private"`, `"service"`, `"service_private"`, and `"em"`.
>
> * `"public"` is an alias for `"service"`.
> * `"tech"` is also an alias for `"service"` (identical coefficients), reserved for potential future tech-specific variations.

---

## 2. Configuration (`computation/constants.py`)

All model weights, intercepts, and thresholds live in a single file. Below is a summary:

```python
MODEL_COEFFICIENTS = {
    "original": {
        "intercept": 0.0,
        "weights": {
            "x1": 1.20,
            "x2": 1.40,
            "x3": 3.30,
            "x4": 0.60,
            "x5": 1.00
        },
        "use_market_equity": True,
        "thresholds": {
            "distress": 1.81,
            "grey_upper": 2.99,
            "safe": 2.99
        },
        "required_fields": [
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "ebit",
            "total_assets",
            "total_liabilities",
            "sales",
            "market_value_equity"
        ]
    },
    "private": {  # Z′ for private manufacturing
        "intercept": 0.0,
        "weights": {
            "x1": 0.717,
            "x2": 0.847,
            "x3": 3.107,
            "x4": 0.420,
            "x5": 0.998
        },
        "use_market_equity": False,  # Book equity
        "thresholds": {
            "distress": 1.10,
            "grey_upper": 2.60,
            "safe": 2.60
        },
        "required_fields": [
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "ebit",
            "total_assets",
            "total_liabilities",
            "sales",
            "book_value_equity"
        ]
    },
    "service": {  # Zʺ-public for non-manufacturing
        "intercept": 0.0,
        "weights": {
            "x1": 6.56,
            "x2": 3.26,
            "x3": 6.72,
            "x4": 1.05
        },
        "use_market_equity": True,
        "thresholds": {
            "distress": 1.23,
            "grey_upper": 2.90,
            "safe": 2.90
        },
        "required_fields": [
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "ebit",
            "total_assets",
            "total_liabilities",
            "market_value_equity"
        ]
    },
    "service_private": {  # Zʺ-private for non-manufacturing
        "intercept": 0.0,
        "weights": {
            "x1": 6.56,
            "x2": 3.26,
            "x3": 6.72,
            "x4": 1.05
        },
        "use_market_equity": False,  # Book equity
        "thresholds": {
            "distress": 1.10,
            "grey_upper": 2.60,
            "safe": 2.60
        },
        "required_fields": [
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "ebit",
            "total_assets",
            "total_liabilities",
            "book_value_equity"
        ]
    },
    "tech": {  # Alias for service
        "intercept": 0.0,
        "weights": {
            "x1": 6.56,
            "x2": 3.26,
            "x3": 6.72,
            "x4": 1.05
        },
        "use_market_equity": True,
        "thresholds": {
            "distress": 1.23,
            "grey_upper": 2.90,
            "safe": 2.90
        },
        "required_fields": [
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "ebit",
            "total_assets",
            "total_liabilities",
            "market_value_equity"
        ]
    },
    "public": {  # Alias for service
        "intercept": 0.0,
        "weights": {
            "x1": 6.56,
            "x2": 3.26,
            "x3": 6.72,
            "x4": 1.05
        },
        "use_market_equity": True,
        "thresholds": {
            "distress": 1.23,
            "grey_upper": 2.90,
            "safe": 2.90
        },
        "required_fields": [
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "ebit",
            "total_assets",
            "total_liabilities",
            "market_value_equity"
        ]
    },
    "em": {  # EM-adjusted Zʺ
        "intercept": 3.25,
        "weights": {
            "x1": 6.56,
            "x2": 3.26,
            "x3": 6.72,
            "x4": 1.05
        },
        "use_market_equity": False,  # Book equity by default in EM
        "thresholds": {
            "distress": 1.10,
            "grey_upper": 2.60,
            "safe": 2.60
        },
        "required_fields": [
            "current_assets",
            "current_liabilities",
            "retained_earnings",
            "ebit",
            "total_assets",
            "total_liabilities",
            "book_value_equity"
        ]
    }
}
```

---

## 3. Data Fetching and Ingestion

1. **Primary Source: Yahoo Finance**

   * Retrieves quarterly financials (balance sheet, income) and market capitalization.
   * If Yahoo fails, fallback to **SEC EDGAR** via XBRL (with the same field mapping dictionary).

2. **Field Mapping**

   * A dictionary of possible XBRL labels is maintained (e.g., “CurrentAssets,” “AssetsCurrent”).
   * All fetched fields are normalized into canonical names (`total_assets`, `current_assets`, `current_liabilities`, `retained_earnings`, `ebit`, `sales`, `market_value_equity` or `book_value_equity`, `total_liabilities`).

3. **Timing / Context Validation**

   * Each data point is validated against its reporting date (e.g., quarter-end).
   * If multiple contexts exist (consolidated vs. standalone), platform prefers consolidated.
   * If any required field is missing, an explanatory error is raised and logged.

---

## 4. Validation & Quality Checks

Before computing any Z-Score:

1. **Schema Validation (Pydantic)**

   * Ensure all required fields for the selected model are non-null and numeric.
   * Verify that total\_assets = current\_assets + non\_current\_assets (where data permits) to catch data ingestion errors.

2. **Accounting Identities**

   * Check: `total_assets ≈ total_liabilities + (market_value_equity or book_value_equity)`.
   * If discrepancy > 1% of total\_assets, raise a consistency warning (log for user).

3. **Ratio Range Checks**

   * $X₁ = (CA - CL)/TA$ must lie within \[-1.0, +1.0].
   * $X₂ = RE/TA$ typically lies within \[-1.0, +1.0].
   * $X₃ = EBIT/TA$ normally within \[-1.0, +1.0].
   * $X₄ = Equity/TL$ must be ≥ 0 for public models; can be negative for private if BVE is negative.
   * $X₅ = Sales/TA$ (manufacturing only) usually within \[0, +5].
   * If any ratio is out of “plausible” bounds, log a “Consistency Warning” in the output.

---

## 5. Computation Dispatcher (`compute_zscore()`)

1. **Input**: ticker, date (quarter-end), SIC, is\_public flag, is\_emerging flag.
2. **Model Selection**:

   * Call `select_zscore_model(sic, is_public, is_emerging, maturity)` → returns one of:
     `["original", "private", "service", "service_private", "public", "tech", "em"]`.
3. **Fetch Data**:

   * Use Yahoo Finance → if failure, fallback to SEC EDGAR.
   * Normalize with field mapping.
4. **Validate Inputs** (see Section 4).
5. **Compute Ratios X₁…X₅ (if needed)**

   * For service/service\_private/public/tech/em: compute X₁ – X₄ only.
   * For original/private: compute X₁ – X₅.
   * Use **market value** in X₄ if `use_market_equity=True`; else use **book value**.
6. **Apply Formula**:

   * `Z = intercept + ∑ weightᵢ · Xᵢ`.
7. **Assign Diagnostic**:

   * If Z ≤ distress cutoff → “Distress Zone.”
   * If distress cutoff < Z ≤ grey\_upper → “Grey Zone.”
   * If Z > grey\_upper → “Safe Zone.”
8. **Output**:

   * Computed Z‐Score (rounded to three decimals), all component ratios, Diagnostic label, plus any “Consistency Warnings.”
   * Log the exact model name, coefficients, and thresholds used (for audit).

---

## 6. Gap Analysis & Development Status

* **Core Functionality (95% Complete)**

  * Model selection and Z-Score calculation for Original, Z′, Zʺ, Zʺ-private, and Z\_EM are fully implemented.
  * Paper‐accurate coefficients, intercepts, and thresholds in constants.

* **Data Infrastructure (85% Complete)**

  * Yahoo Finance integration is robust.
  * SEC EDGAR fallback works for most tickers; occasional XBRL label mismatches require manual mapping updates.

* **Validation & Quality (60% Complete)**

  * Basic schema checks and ratio‐range checks are implemented.
  * Need to enhance identity checks (e.g., catch inter‐quarter restatements, detect stale XBRL contexts).

* **Advanced Features (40% Complete)**

  * Currency conversion (for non‐USD firms) is documented but not yet implemented.
  * AI‐powered anomaly detection (e.g., auto-flagging suspicious ratio jumps) is planned but not active.

* **Integration Points (55% Complete)**

  * Basic integration with internal dashboards is in place.
  * Advanced notifications (e.g., automated alerts when Z falls below 1.23) are not yet deployed.

---

## 7. Recommendations for Closing Gaps

1. **Phase 1: Validation & Error Handling**

   * Complete accounting‐identity checks for every fetched dataset.
   * Add cross‐quarter consistency checks (e.g., retained earnings should roll forward).
   * Implement missing‐field suggestions (e.g., request user to upload missing SEC filing).

2. **Phase 2: Data Quality & Currency Conversion**

   * Integrate FX rates for non‐USD reporting (use a reliable API).
   * Normalize all financials to millions of USD for consistency.

3. **Phase 3: AI/Advanced Analytics**

   * Add an AI module to auto-detect outliers in ratio trends.
   * Enable “what‐if” scenario analysis (allow user to adjust CAPEX, see effect on Z).

4. **Phase 4: Machine Learning & Optimization**

   * Experiment with ML models to predict future Z‐Scores based on macro indicators.
   * Optimize data caching to reduce repeated API calls.

---

## 8. Key Clarifications

* **“public” vs. “service” vs. “tech” keys:**

  * All three use identical coefficients (6.56, 3.26, 6.72, 1.05) and thresholds (1.23/2.90).
  * “service” is the canonical key for any public, non-manufacturing firm.
  * “public” is an alias to “service,” retained for backward compatibility.
  * “tech” is also an alias for “service,” reserved to allow future tech-specific customizations (e.g., adjust weights for certain software firms).

* **SIC-Specific Overrides:**

  * The codebase reserves the ability to map a specific SIC code (e.g., `sic_2834`) to a custom coefficient set.
  * Currently, no SIC-specific overrides are defined. If none exist, this step is skipped.

* **X₄ in Emerging Markets:**

  * By default, Z\_EM uses book equity in X₄ (BVE/TL).
  * If a reliable market capitalization is available for an EM firm, it may be substituted. Annotations in code must document this possibility.

---

## 9. References

1. **Altman, E. I. (1968).** “Financial ratios, discriminant analysis and the prediction of corporate bankruptcy.” *Journal of Finance*, 23(4), 589–609.
2. **Altman, E. I. (1983).** *Corporate Financial Distress: A Complete Guide to Predicting, Avoiding, and Dealing with Bankruptcy.* Wiley.
3. **Altman, E. I., Hartzell, J. C., & Peck, M. C. (1995).** “Emerging Market Corporate Bonds: A Scoring System.” Salomon Smith Barney.
4. **Altman, E. I., & Hotchkiss, E. (2006).** *Corporate Financial Distress and Bankruptcy: Predict and Avoid Bankruptcy, Analyze and Invest in Distressed Debt* (3rd ed.). Wiley.

---

*End of ModelSelection.md*
