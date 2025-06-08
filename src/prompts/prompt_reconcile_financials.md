# Prompt: Reconcile and Canonicalize Financial Data

You are a financial data expert. You are given two raw datasets for the same company with quarterly data:
- `sec_data`: Extracted from SEC EDGAR/XBRL filings (may have missing or inconsistent fields)
- `yahoo_data`: Extracted from Yahoo Finance (may have missing or inconsistent fields)

Your task:
1. Reconcile both datasets, resolving discrepancies and filling missing values where possible.
2. For each field in each quarter, prefer SEC data if available and valid; otherwise, use Yahoo Finance data.
3. Standardize field names and units according to the Altman Z-Score model requirements (see below).
4. Output a quarterly structure with all available quarters and required fields.
5. If a field cannot be filled for a quarter, set its value to null.

Required fields for each quarter:
- total_assets
- current_assets
- current_liabilities
- total_liabilities
- retained_earnings
- ebit
- sales

Output format (return quarters in chronological order, most recent first):
```json
{
  "quarters": [
    {
      "period_end": "YYYY-MM-DD",
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
  ]
}
```

Be concise, accurate, and transparent. Do not invent values. Only use the data provided.

---

SEC Data:
{sec_data}

Yahoo Finance Data:
{yahoo_data}
