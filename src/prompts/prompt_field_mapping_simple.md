# Prompt: Map Financial Data Fields to Canonical Altman Z-Score Fields

You are a financial data expert. Your task is to map the available SEC field names to the canonical Altman Z-Score fields.

## Canonical fields:
- total_assets
- current_assets
- current_liabilities
- total_liabilities
- retained_earnings
- ebit
- sales

## Available field names:
- SEC: [list of SEC field names, e.g., "Assets", "AssetsCurrent", ...]

## Instructions:
- For each canonical field, return a list of all plausible candidate SEC field names, ordered by likelihood (best first). If no plausible field is found, use an empty list.
- Output a JSON object with this structure (no commentary, markdown, or code block):

{
  "total_assets": ["BestSECField1", "AltSECField2", ...],
  "current_assets": [...],
  "current_liabilities": [...],
  "total_liabilities": [...],
  "retained_earnings": [...],
  "ebit": [...],
  "sales": [...]
}

If a canonical field is not present in SEC, set its value to an empty list.

---

Example (for illustration only):

Available field names:
- SEC: ["Assets", "AssetsCurrent", "LiabilitiesCurrent", ...]

Output:
{
  "total_assets": ["Assets", "TotalAssets"],
  "current_assets": ["AssetsCurrent"],
  ...
}
