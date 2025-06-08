# Prompt: Reconcile and Canonicalize Financial Data

You are a financial data expert. You are given two raw datasets for the same company and period:
- `sec_data`: Extracted from SEC EDGAR/XBRL filings (may have missing or inconsistent fields)
- `yahoo_data`: Extracted from Yahoo Finance (may have missing or inconsistent fields)

Your task:
1. Reconcile both datasets, resolving discrepancies and filling missing values where possible.
2. For each field, prefer SEC data if available and valid; otherwise, use Yahoo Finance data.
3. Standardize field names and units according to the Altman Z-Score model requirements (see below).
4. Output a single canonical JSON object with all required fields, and a `source_map` indicating which source was used for each field.
5. If a field cannot be filled, set its value to null and note this in the `source_map`.

Required fields:
- total_assets
- current_assets
- current_liabilities
- total_liabilities
- retained_earnings
- ebit
- sales

Output format:
```json
{
  "total_assets": ...,
  "current_assets": ...,
  "current_liabilities": ...,
  "total_liabilities": ...,
  "retained_earnings": ...,
  "ebit": ...,
  "sales": ...,
  "source_map": {
    "total_assets": "sec" | "yahoo" | "null",
    ...
  }
}
```

Be concise, accurate, and transparent. Do not invent values. Only use the data provided.

---

SEC Data:
{sec_data}

Yahoo Finance Data:
{yahoo_data}
