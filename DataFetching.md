## Checklist: Data Fetching Ideas

### Implemented:
- Fetch historical prices, dividends, and stock splits from `yfinance`.
- Fetch and save `company_info`, `major_holders`, `institutional_holders`, and `recommendations` from `yfinance`.
- Fetch company information from SEC EDGAR.
- Ensure all JSON files are pretty-formatted.

### Pending:
- Validate the accuracy and usefulness of SEC EDGAR data.
- Improve error handling for both `yfinance` and SEC EDGAR data fetching.
- Finalize and implement the checklist in `DataFetching.mp`.

---

## Checklist: Data Fetching Ideas

### Implemented:
- Fetch and save historical prices, dividends, and stock splits from `yfinance`.
- Fetch and save `company_info`, `major_holders`, `institutional_holders`, and `recommendations` from `yfinance`.
- Fetch company information from SEC EDGAR.
- Ensure all JSON files are pretty-formatted.

### Pending:
- Finalize and implement the checklist at the top of the file.
- Validate the accuracy and usefulness of SEC EDGAR data.
- Improve error handling for both `yfinance` and SEC EDGAR data fetching.

---

Below is a consolidated set of “data‐fetching rules” that would avoid the kinds of mismatches we saw in both the AAL and TSLA reports. First, I briefly recap the main discrepancies we encountered in the AAL analysis (and how we resolved them), then I describe the analogous issues in the TSLA appendix, and finally I lay out a unified set of rules you should apply whenever you pull data from SEC Edgar (or any XBRL source) so that your Z‐Score inputs stay consistent from quarter to quarter.

---

## 1. Recap: AAL Analysis “Data Issues” and How We Fixed Them

When we compared the AAL appendix values to public sources, we found that:

1. **EBIT Differences**

   * The appendix sometimes used a non‐GAAP “EBIT” (or a line tagged `<us-gaap:EBIT>`) rather than GAAP “Operating Income (Loss)” (`<us-gaap:OperatingIncomeLoss>`).
   * As a result, for 2025 Q1 AAL the appendix showed \$–220 M EBIT, whereas GAAP “Operating Income” was \$–270 M.
   * **Fix:** Always fetch and use the GAAP tag `<us-gaap:OperatingIncomeLoss>` if you want the true “EBIT” line. If you instead want a non‐GAAP “EBIT” variant (e.g., excluding stock‐comp), be explicit—do not mix up tags.

2. **Market-Value vs. Book-Value Equity for X₄**

   * In AAL’s case, we knew the original Altman model uses **Market Value of Equity** ÷ **Total Liabilities** for $X_4$.
   * The appendix had “Book Value Equity,” so they had effectively replaced $X_4 = \tfrac{\text{MVE}}{\text{TL}}$ with $X_4 = \tfrac{\text{BVE}}{\text{TL}}$.
   * **Fix:** Decide up front whether you are using (a) market‐cap as the numerator for $X_4$, or (b) book‐equity (as a proxy). If you choose (b), consistently fetch `<us-gaap:StockholdersEquity>` (or `<us-gaap:CommonStockEquity>`) and document that choice. If you want true market‐value equity, you must pull the share-count × share-price at quarter-end instead of any XBRL tag.

3. **Rounding & Minor Timing Differences**

   * We saw that AAL’s “Total Liabilities” in the appendix (e.g., \$67 117 M for 2025 Q1) sometimes differed by \$50–60 M from MacroTrends or WSJ Q (e.g., \$67 155 M). That turned out to be simple rounding, or a slight amendment in the SEC filing.
   * **Fix:** Accept rounding differences of ±0.2% (±0.3%) as immaterial. But if you want to pin numbers exactly, use the same rounding convention every quarter (e.g., always round to the nearest \$1 M).

4. **Exact “Sales” / “Revenue” Line**

   * AAL’s appendix used “Total Revenue” (`<us-gaap:Revenues>`), which matched perfectly. No segmentation issues arose.
   * **Fix:** For any company, fetch `<us-gaap:Revenues>` (the top‐line GAAP revenue) so you never accidentally grab “Automotive sales” or “Product sales” or “Services revenue” unless that is your explicit intention.

Because of steps 1–4, we ended up with a fully transparent pipeline:

* For EBIT: `<us-gaap:OperatingIncomeLoss>`.
* For Sales: `<us-gaap:Revenues>`.
* For Book Equity: `<us-gaap:StockholdersEquity>` (if using book equity) or share‐count × quarter-end price (if using market equity).
* For Balance Sheet items: `<us-gaap:Assets>`, `<us-gaap:AssetsCurrent>`, `<us-gaap:Liabilities>`, `<us-gaap:LiabilitiesCurrent>`, and `<us-gaap:RetainedEarningsAccumulatedDeficit>`.

---

## 2. TSLA Appendix: Parallel Issues

When we ran the TSLA appendix through the same checks, these mismatches emerged:

1. **EBIT**

   * Appendix (TSLA 2025 Q1): “EBIT = \$680 M”
   * GAAP “Operating Income (Loss)” (`<us-gaap:OperatingIncomeLoss>` from Tesla’s 10-Q): \$399 M.
   * **Likely cause:** The appendix probably scraped a non-GAAP XBRL tag named `<us-gaap:EBIT>` (or a footnote line that excludes certain charges).
   * **Rule:** If you mean “Operating Income,” explicitly fetch `<us-gaap:OperatingIncomeLoss>`. Avoid scraping `<us-gaap:EBIT>` unless your goal is to use that non-GAAP measure.

2. **Sales (Revenue)**

   * Appendix (TSLA 2024 Q3): “Sales = \$13 647 M”
   * True GAAP `<us-gaap:Revenues>` for Q3 2024: \$25 182 M.
   * **Likely cause:** Appendix grabbed `<us-gaap:AutomotiveSalesRevenue>` or a segment‐specific tag instead of `<us-gaap:Revenues>`.
   * **Rule:** Always fetch exactly `<us-gaap:Revenues>` for total revenue. If you ever want “Automotive” or “Energy” sales separately, do so in a dedicated column, but do not mix them into the single “Sales” line for Z-Score.

3. **Total Liabilities & Rounding**

   * TSLA 2025 Q1: Appendix says \$49 693 M; MacroTrends says \$49 755 M (a \$62 M difference, \~0.13%).
   * **Likely cause:** Either a rounding difference or the aggregator captured an early vs. amended 10-Q line.
   * **Rule:** Decide on a rounding convention—e.g., “Round every line to the nearest \$1 M, as reported in the final Edgar 1.0 fil­ing”—and stick with it every quarter. Anywhere you see a mismatch < 0.3%, you can safely attribute it to rounding and comment on it as immaterial.

4. **Retained Earnings**

   * TSLA appendix values matched MacroTrends exactly (no discrepancy).
   * **Rule:** Fetch `<us-gaap:RetainedEarningsAccumulatedDeficit>` for “Retained Earnings.” Do not use any footnote tags like “Accumulated Comprehensive Income” or “Accumulated Depreciation.”

5. **Book Value Equity**

   * TSLA appendix: “Book Value Equity = \$74 653 M for 2025 Q1.”
   * WSJ Q (TradingView) also says \$74 650 M.
   * **Rule:** If you mean book equity, grab `<us-gaap:StockholdersEquity>` (or `<us-gaap:CommonStockEquity>` if you want to exclude minority interest). If you want market‐cap, do a separate step: share-count (`<us-gaap:CommonStockSharesOutstanding>`) × quarter‐end price.

---

## 3. Unified Data‐Fetching Rules

Below is a canonical list of **exact tags or procedures** you should use whenever you build a “quarterly Z-Score pipeline” from SEC Edgar (or any XBRL feed). These rules cover both AAL, TSLA, and any other company:

1. **Balance Sheet & Retained Earnings**

   * **Total Assets (TA):** XBRL tag `<us-gaap:Assets>`.

   * **Current Assets (CA):** `<us-gaap:AssetsCurrent>`.

   * **Current Liabilities (CL):** `<us-gaap:LiabilitiesCurrent>`.

   * **Total Liabilities (TL):** `<us-gaap:Liabilities>`.

   * **Retained Earnings (RE):** `<us-gaap:RetainedEarningsAccumulatedDeficit>`.

   * **Book Value Equity (BVE):** `<us-gaap:StockholdersEquity>` (or `<us-gaap:CommonStockEquity>` if you want to isolate common shareholders).

   > **Rounding Rule:** After you parse each of these tags, round to the nearest \$1 M. If you see tiny differences (± 0.2%), call them rounding and move on.

2. **EBIT / Operating Income**

   * **GAAP Operating Income (EBIT):** `<us-gaap:OperatingIncomeLoss>` (this is your primary “EBIT” input).
   * **Do not** use `<us-gaap:EBIT>` or any non-GAAP XBRL tag unless you have a documented reason—those often exclude stock‐based compensation or include other adjustments.
   * **Rounding Rule:** Round the GAAP “OperatingIncomeLoss” to nearest \$1 M.

3. **Sales / Total Revenue**

   * **Total Revenue:** `<us-gaap:Revenues>`.
   * If you ever need segment detail (e.g., “Automotive sales” vs. “Energy sales”), fetch those under separate tags (e.g., `<us-gaap:AutomotiveSalesRevenue>`), but do not mix them into your “Sales” column.
   * **Rounding Rule:** Round `<us-gaap:Revenues>` to the nearest \$1 M.

4. **Market vs. Book Equity for $X_{4}$**
   Choose one approach per quarter (and stick to it consistently):

   * **Book-Equity Approach:** Use `<us-gaap:StockholdersEquity>` ÷ `<us-gaap:Liabilities>`.
   * **Market-Equity Approach:**

     1. Fetch `<us-gaap:CommonStockSharesOutstanding>` (number of shares) from the balance sheet footnote.
     2. Multiply by the actual quarter-end stock price (e.g., Nasdaq close on March 31).
     3. Divide by `<us-gaap:Liabilities>`.
   * Document explicitly which one you picked.
   * **Rounding Rule:** After you compute market-cap (= shares × price), round to the nearest \$1 M. Then divide by `<us-gaap:Liabilities>`, rounding the ratio to at least four decimal places for precision.

5. **Quarter-End Alignment**

   * Ensure you are pulling these tags for the exact same period. For example, if you want Q1 2025 for Tesla, the XBRL context must correspond to “Period = 2025-03-31 to 2025-03 31.”
   * Aggregators sometimes tag a “quarter” as any date in April if the 10-Q was filed mid-April. You must filter XBRL contexts by the true “EndDate=03-31-2025” (etc.).
   * **Rule:** Always use the XBRL context whose `endDate` field exactly equals the quarter’s last calendar day. If you cannot find an exact match, manually inspect and pick the context that aggregates “three months ended …” rather than “six months ended …” or “twelve months ended ….”

6. **Documentation & Metadata**

   * For each quarter, record:

     1. **Filing Date** of the 10-Q/10-K.
     2. **XBRL Context ID** you used for each line (so you can trace back if the tag names change).
     3. **Rounding Convention** (e.g., “Round each GAAP value to the nearest \$1 M”).
     4. **Any Non-GAAP Adjustments** (e.g., if you deliberately grabbed a non-GAAP “EBIT,” note that in a “Footnotes” column).

7. **Consistency Checks**

   * After you pull all five input ratios, do a quick plausibility check:

     * Is $\tfrac{CA - CL}{TA}$ between –1 and +1 (so you didn’t accidentally invert something)?
     * Is EBIT/TA < 1 (so you didn’t accidentally grab EBITDA)?
     * Is Sales/TA < 5 (almost no company has revenue > 5× total‐assets in a single quarter)?
   * If any ratio is wildly out of the expected range, flag it for manual review.

---

## 4. Putting It All Together

Below is pseudocode (Python‐style) for a quarter-by-quarter pipeline that guarantees you pull exactly the same numbers we used in the AAL and TSLA analyses:

```python
def fetch_zscore_inputs_from_XBRL(xbrl_document, quarter_end_date):
    """
    Given an XBRL document (parsed) and a quarter_end_date string (e.g., "2025-03-31"),
    return a dict of GAAP inputs: TA, CA, CL, RE, TL, BVE, EBIT, SALES.
    Each value is rounded to the nearest $1M.
    """

    # 1. Extract each XBRL tag with context == quarter_end_date
    TA   = get_tag_value(xbrl_document, "us-gaap:Assets", context_end=quarter_end_date)
    CA   = get_tag_value(xbrl_document, "us-gaap:AssetsCurrent", context_end=quarter_end_date)
    CL   = get_tag_value(xbrl_document, "us-gaap:LiabilitiesCurrent", context_end=quarter_end_date)
    TL   = get_tag_value(xbrl_document, "us-gaap:Liabilities", context_end=quarter_end_date)
    RE   = get_tag_value(xbrl_document, "us-gaap:RetainedEarningsAccumulatedDeficit", context_end=quarter_end_date)
    BVE  = get_tag_value(xbrl_document, "us-gaap:StockholdersEquity", context_end=quarter_end_date)

    # 2. Grab GAAP Operating Income (EBIT)
    EBIT = get_tag_value(xbrl_document, "us-gaap:OperatingIncomeLoss", context_end=quarter_end_date)

    # 3. Grab Total Revenues
    SALES = get_tag_value(xbrl_document, "us-gaap:Revenues", context_end=quarter_end_date)

    # 4. Round every value to the nearest $1M
    TA, CA, CL, TL, RE, BVE = [round(v / 1e6) * 1e6 for v in (TA, CA, CL, TL, RE, BVE)]
    EBIT, SALES = [round(v / 1e6) * 1e6 for v in (EBIT, SALES)]

    # 5. (Optional) If you want Market Cap for X4 instead of Book Equity:
    #    shares = get_tag_value(xbrl_document, "us-gaap:CommonStockSharesOutstanding", context_end=quarter_end_date)
    #    price  = fetch_price_on_date("TSLA", quarter_end_date)  # from a market API
    #    MVE    = round((shares * price) / 1e6) * 1e6
    #    return { …, "MVE": MVE }
    #
    # Otherwise, just document that X4 = BVE / TL.

    return {
        "TA":   TA,
        "CA":   CA,
        "CL":   CL,
        "TL":   TL,
        "RE":   RE,
        "BVE":  BVE,
        "EBIT": EBIT,
        "SALES": SALES
    }
```

Once you have those eight fields (all uniformly rounded to \$1 M), you can compute:

```python
X1 = (CA - CL) / TA
X2 = RE / TA
X3 = EBIT / TA
X4 = BVE / TL         # or MVE/TL if you grabbed market cap
X5 = SALES / TA
Z  = 1.2 * X1 + 1.4 * X2 + 3.3 * X3 + 0.6 * X4 + 1.0 * X5
```

and compare $Z$ against $1.81$ (distress) and $2.99$ (safe).

---

## 5. Why These Rules Solve AAL & TSLA Issues

1. **EBIT Consistency**:

   * You will always hit `<us-gaap:OperatingIncomeLoss>`, never the non-GAAP “EBIT” tag. That eliminates the \$680 M vs. \$399 M confusion we saw in Tesla’s 2025 Q1.
   * For AAL, it prevents a mismatch between an appendix’s “–\$220 M” and MacroTrends’s “–\$270 M.”

2. **Sales Clarity**:

   * By targeting `<us-gaap:Revenues>`, you guarantee “Total Revenue,” not just a segment. That fixes TSLA’s “\$13 647 M” (automotive only) versus \$25 182 M “Total Revenue.”
   * For AAL, it ensured we never accidentally grabbed some narrow “Support Services” subset—AAL’s appendix exactly matched public revenue.

3. **Book vs. Market Equity**:

   * If you explicitly choose “Book Equity” you always use `<us-gaap:StockholdersEquity>`. That makes AAL’s and TSLA’s $X_4$ calculation transparent.
   * If you want “Market Equity,” you do a separate step (fetch shares × price) rather than falling back on any random XBRL tag named `<us-gaap:Equity>` or “CommonStockEquity.”
   * This consistency helped us recognize that AAL’s appendix substituted BVE for MVE, and TSLA’s appendix substituted BVE for MVE—even though the “true” Altman model calls for market value. At least now it’s a documented, deliberate choice.

4. **Rounding & Timing**:

   * Rounding every value to \$1 M (rather than letting one source truncate at \$1 M and another round at \$0.5 M) avoids \$62 M or \$86 M line‐item discrepancies.
   * Making sure you pull the XBRL context with `endDate = “YYYY-MM-DD”` ensures you never mix “three months ended” with “twelve months ended” accidentally. That solves the “amended” issue where an aggregator might have read a pre-amendment value.

---

## 6. Final Recommendation

Whenever you build (or refactor) your “SEC → XBRL → Z-Score” pipeline, follow these concrete steps **every quarter**:

1. **Locate XBRL Context** exactly matching “Period End = Quarter-End Date” (e.g., 2025-03-31).
2. **Fetch exactly** these tags (with that context):

   * `us-gaap:Assets`
   * `us-gaap:AssetsCurrent`
   * `us-gaap:LiabilitiesCurrent`
   * `us-gaap:Liabilities`
   * `us-gaap:RetainedEarningsAccumulatedDeficit`
   * `us-gaap:StockholdersEquity`
   * `us-gaap:OperatingIncomeLoss`
   * `us-gaap:Revenues`
3. **Round** all values to the nearest \$1 M, and record them in your “Appendix” or data table.
4. **Decide up front** whether X₄ = Book Equity/Total Liabilities or X₄ = Market Equity/Total Liabilities. If you choose Market Equity, do a separate share-count × price step.
5. **Compute**

   $$
   X_{1} = \frac{CA - CL}{TA},\quad 
   X_{2} = \frac{RE}{TA},\quad 
   X_{3} = \frac{EBIT}{TA},\quad 
   X_{4} = \frac{\text{Equity (book or market)}}{TL},\quad 
   X_{5} = \frac{SALES}{TA},
   $$

   then

   $$
   Z = 1.2\,X_{1} + 1.4\,X_{2} + 3.3\,X_{3} + 0.6\,X_{4} + 1.0\,X_{5}.
   $$
6. **Annotate** any cases where a number deviates by > 0.5% from a well-known aggregator (MacroTrends, WSJ Q). Decide if it’s “rounding,” “pre-amendment vs. final,” or a mis-tag.
7. **Document** the exact XBRL tag and rounding convention in a “Data Sources” section of your analysis, so future reviewers know precisely which lines you pulled.

By following these rules, you will eliminate the kinds of mismatches we saw in both the AAL analysis and the TSLA appendix—ensuring that your quarterly Z-Score inputs are fully traceable back to the correct GAAP line items in each 10-Q or 10-K.
