# ModelReference.md

This document provides a clear, literature-aligned reference for selecting the appropriate Altman Z-Score variant based on industry (SIC code) and firm maturity (public, private, or emerging). Each row specifies:

1. **Model Name**
2. **Formula (coefficients and X-variables)**
3. **Thresholds** (Distress / Grey / Safe)
4. **Clarification on “Maturity”** (public vs. private vs. emerging)

All numbers and assignments are drawn from Altman’s peer-reviewed publications (1968, 1983, 1995, and subsequent revisions).

---

## 1. Manufacturing Firms (SIC 2000–3999)

| Maturity | Model Name                  | Formula & X Definitions                                                                                                                                                                                                                                                                                                                             | Thresholds (Distress / Grey / Safe)      |
| -------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Public   | **Original Z-Score (1968)** |     **Zₒᵣᵢg** = 1.20·X₁ + 1.40·X₂ + 3.30·X₃ + 0.60·X₄ + 1.00·X₅  <br>  • X₁ = (Current Assets – Current Liabilities) / Total Assets  <br>  • X₂ = Retained Earnings / Total Assets  <br>  • X₃ = EBIT / Total Assets  <br>  • X₄ = Market Value of Equity / Total Liabilities  <br>  • X₅ = Sales / Total Assets  <br>  • Uses market equity in X₄. | Z ≤ 1.81 / 1.81 < Z ≤ 2.99 / Z > 2.99    |
| Private  | **Z′-Score (1983)**         |     **Z′** = 0.717·X₁ + 0.847·X₂ + 3.107·X₃ + 0.420·X₄ + 0.998·X₅  <br>  • X₁ = (Current Assets – Current Liabilities) / Total Assets  <br>  • X₂ = Retained Earnings / Total Assets  <br>  • X₃ = EBIT / Total Assets  <br>  • X₄ = Book Value of Equity / Total Liabilities  <br>  • X₅ = Sales / Total Assets  <br>  • Uses book equity in X₄.   | Z′ ≤ 1.10 / 1.10 < Z′ ≤ 2.60 / Z′ > 2.60 |

> **Clarification on “Maturity” (Manufacturing):**
>
> * **Public** (SIC 2000–3999) ⇒ use **Original Z-Score** with market equity in X₄.
> * **Private** (SIC 2000–3999) ⇒ use **Z′-Score** with book equity in X₄.

---

## 2. Non-Manufacturing Firms (Service / Transport / Utilities / Finance / Retail)

> **Relevant SIC Ranges:**
>
> * Transportation & Utilities: SIC 4000–4999 (e.g., Airlines = 4512)
> * Finance & Insurance: SIC 6000–6999
> * Services / Retail / Tech: SIC 7000–8999 (including Tech/Software sub-ranges: 3570–3579, 3670–3679, 7370–7379)

| Maturity | Model Name                            | Formula & X Definitions                                                                                                                                                                                                                                                                                                                        | Thresholds (Distress / Grey / Safe)      |
| -------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Public   | **Zʺ-Score (1995, Public Non-Mfg.)**  |     **Zʺₚᵤ\_b** = 6.56·X₁ + 3.26·X₂ + 6.72·X₃ + 1.05·X₄  <br>  • X₁ = (Current Assets – Current Liabilities) / Total Assets  <br>  • X₂ = Retained Earnings / Total Assets  <br>  • X₃ = EBIT / Total Assets  <br>  • X₄ = Market Value of Equity / Total Liabilities  <br>  • Four-ratio model (drops X₅).  <br>  • Uses market equity in X₄. | Zʺ ≤ 1.23 / 1.23 < Zʺ ≤ 2.90 / Zʺ > 2.90 |
| Private  | **Zʺ-Score (1995, Private Non-Mfg.)** |     **Zʺₚᵣᵢᵥ** = 6.56·X₁ + 3.26·X₂ + 6.72·X₃ + 1.05·X₄  <br>  • X₁ = (Current Assets – Current Liabilities) / Total Assets  <br>  • X₂ = Retained Earnings / Total Assets  <br>  • X₃ = EBIT / Total Assets  <br>  • X₄ = Book Value of Equity / Total Liabilities  <br>  • Four-ratio model with book equity in X₄.                           | Zʺ ≤ 1.10 / 1.10 < Zʺ ≤ 2.60 / Zʺ > 2.60 |

> **Clarification on “Maturity” (Non-Manufacturing):**
>
> * **Public** (SIC ≥ 4000) ⇒ use **Zʺ-Score (1995, Public)** with market equity in X₄.
> * **Private** (SIC ≥ 4000) ⇒ use **Zʺ-Score (1995, Private)** with book equity in X₄.

---

## 3. Emerging Market Firms (Any SIC)

| Firm Type | Model Name                          | Formula & X Definitions                                                                                                                                                                                                                                                                                                                                    | Thresholds (Distress / Grey / Safe)         |
| --------- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Any SIC   | **Z\_EM-Score (1995, EM-Adjusted)** |     **Zₑₘ** = 3.25 + 6.56·X₁ + 3.26·X₂ + 6.72·X₃ + 1.05·X₄  <br>  • X₁ = (Current Assets – Current Liabilities) / Total Assets  <br>  • X₂ = Retained Earnings / Total Assets  <br>  • X₃ = EBIT / Total Assets  <br>  • X₄ = Book Value of Equity / Total Liabilities  <br>  • Four-ratio model + 3.25 intercept.  <br>  • Always uses book equity in X₄. | Zₑₘ ≤ 1.10 / 1.10 < Zₑₘ ≤ 2.60 / Zₑₘ > 2.60 |

> **Clarification on “Maturity” (Emerging Market):**
>
> * If flagged “Emerging Market,” use **Z\_EM-Score** regardless of SIC.
> * By default, X₄ uses **book equity**. If a reliable market-equity quote is available, MVE may be substituted.

---

## 4. At-a-Glance Quick Reference

| SIC Range                  | Emerging? | Maturity | Model                       | X₄ Uses       | Coefficients / Intercept                             | Thresholds (Distress / Grey / Safe) |
| -------------------------- | --------- | -------- | --------------------------- | ------------- | ---------------------------------------------------- | ----------------------------------- |
| 2000–3999 (Manufacturing)  | No        | Public   | Original Z (1968)           | Market Equity | 1.20·X₁ + 1.40·X₂ + 3.30·X₃ + 0.60·X₄ + 1.00·X₅      | 1.81 / 2.99 / Safe > 2.99           |
| 2000–3999 (Manufacturing)  | No        | Private  | Z′ (1983)                   | Book Equity   | 0.717·X₁ + 0.847·X₂ + 3.107·X₃ + 0.420·X₄ + 0.998·X₅ | 1.10 / 2.60 / Safe > 2.60           |
| ≥ 4000 (Non-Manufacturing) | No        | Public   | Zʺ (1995, Public Non-Mfg.)  | Market Equity | 6.56·X₁ + 3.26·X₂ + 6.72·X₃ + 1.05·X₄                | 1.23 / 2.90 / Safe > 2.90           |
| ≥ 4000 (Non-Manufacturing) | No        | Private  | Zʺ (1995, Private Non-Mfg.) | Book Equity   | 6.56·X₁ + 3.26·X₂ + 6.72·X₃ + 1.05·X₄                | 1.10 / 2.60 / Safe > 2.60           |
| Any SIC (Emerging Market)  | Yes       | —        | Z\_EM (1995, EM-Adjusted)   | Book Equity   | 3.25 + 6.56·X₁ + 3.26·X₂ + 6.72·X₃ + 1.05·X₄         | 1.10 / 2.60 / Safe > 2.60           |

> **Key for Ratios (Xᵢ):**
>
> * X₁ = (Current Assets – Current Liabilities) / Total Assets
> * X₂ = Retained Earnings / Total Assets
> * X₃ = EBIT / Total Assets
> * X₄ = Equity / Total Liabilities  (Market Equity if public; otherwise Book Equity)
> * X₅ = Sales / Total Assets  (only in five-ratio manufacturing models)

---

## 5. References

1. Altman, E. I. (1968). “Financial ratios, discriminant analysis and the prediction of corporate bankruptcy.” *Journal of Finance*, 23(4), 589–609.
2. Altman, E. I. (1983). *Corporate Financial Distress: A Complete Guide to Predicting, Avoiding, and Dealing with Bankruptcy.* Wiley.
3. Altman, E. I., Hartzell, J. C., & Peck, M. C. (1995). “Emerging Market Corporate Bonds: A Scoring System.” Salomon Smith Barney.
4. Altman, E. I., & Hotchkiss, E. (2006). *Corporate Financial Distress and Bankruptcy: Predict and Avoid Bankruptcy, Analyze and Invest in Distressed Debt* (3rd ed.). Wiley.

*End of ModelReference.md*
