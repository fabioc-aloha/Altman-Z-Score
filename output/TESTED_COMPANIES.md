# ---
# BEFORE EVERY RELEASE:
# - Ensure every company with an output folder in `output/` is listed in the table below.
# - For each ticker, update the Outcome, Script Version, and Notes/Issues columns as needed.
# - If new companies are added to `output/`, add them here before release.
# - If companies are removed from `output/`, remove them from this table.
# - This file is a release-blocking item: see `README.md` and `RELEASE_CHECKLIST.md` for details.
# ---

# Tested Companies and Pipeline Outcomes (as of May 29, 2025)

- **Before every release, ensure this file is up to date:**
    - Every company in the `output/` folder must be listed in this table, with outcome and notes.
    - If you add or remove companies, update this file accordingly.
    - Review the latest pipeline runs and outputs for accuracy.
    - This is a release-blocking checklist item.

| Ticker      | Company Name                  | Region      | Sector/Type         | Outcome     | Script Version | Notes/Issues                                                                 |
|-------------|-------------------------------|-------------|---------------------|------------|---------------|-------------------------------------------------------------------------------|
| MSFT        | Microsoft Corp.               | US          | Tech                | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| AAPL        | Apple Inc.                    | US          | Tech                | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| AMZN        | Amazon.com Inc.               | US          | Tech/Retail         | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| TSLA        | Tesla Inc.                    | US          | Auto/Tech           | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| SBUX        | Starbucks Corp.               | US          | Consumer            | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| FDX         | FedEx Corp.                   | US          | Logistics           | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| DAL         | Delta Air Lines Inc.          | US          | Airlines            | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| META        | Meta Platforms Inc.            | US          | Tech/Social Media   | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| GOOGL       | Alphabet Inc.                  | US          | Tech/Search         | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| NVDA        | NVIDIA Corp.                   | US          | Tech/Semiconductors | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| PRGS        | Progress Software Corp.        | US          | Software            | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| HURC        | Hurco Companies Inc.           | US          | Industrials         | Success    | v2.2.2        | Full report, chart, and data generated                                        |
| SPWR        | SunPower Corp.                 | US          | Energy/Solar        | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| OLLI        | Ollie's Bargain Outlet         | US          | Retail              | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| AOUT        | American Outdoor Brands        | US          | Consumer            | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| CMTL        | Comtech Telecommunications     | US          | Telecom             | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| FLWS        | 1-800-Flowers.com Inc.         | US          | Consumer            | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| GPRO        | GoPro Inc.                     | US          | Consumer/Electronics| Success    | v2.2.1        | Full report, chart, and data generated                                        |
| ITUB        | Itau Unibanco                 | Brazil      | Bank/Financial      | Error      | v2.2.1        | Field mapping/formatting issue (AI output not strict JSON); no report         |
| BBD         | Banco Bradesco                | Brazil      | Bank/Financial      | Partial    | v2.2.1        | Report generated, but 'sales' missing for all quarters (bank proxy logic)     |
| PBR         | Petrobras                     | Brazil      | Energy              | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| VALE        | Vale S.A.                     | Brazil      | Mining              | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| ABEV        | Ambev S.A.                    | Brazil      | Consumer            | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| GOL         | Gol Linhas Aéreas             | Brazil      | Airlines            | Error      | v2.2.1        | Ticker not found; no report generated                                         |
| CBD         | Companhia Brasileira Dist.    | Brazil      | Retail              | Error      | v2.2.1        | Ticker not found; no report generated                                         |
| SAP         | SAP SE                        | Europe      | Tech                | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| SIEGY       | Siemens AG                    | Europe      | Industrials         | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| ASML        | ASML Holding                  | Europe      | Tech/Semiconductors | Partial    | v2.2.1        | Report generated, but missing 'retained_earnings' for all quarters            |
| AIR         | Airbus SE                     | Europe      | Aerospace           | Success    | v2.2.1        | Full report, chart, and data generated                                        |
| ...         | ...                           | ...         | ...                 | ...        | ...           | ...                                                                           |

- **Success**: Full pipeline ran, report and chart generated, no critical missing fields.
- **Partial**: Report generated, but some fields missing or partial analysis only.
- **Error**: Pipeline failed due to missing ticker, mapping/formatting issue, or critical missing data.

This table is updated as new companies and regions are tested. See `output/<TICKER>/` for per-company results and details.
