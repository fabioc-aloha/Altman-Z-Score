# Duplicate Tickers Report

## Summary
- **Total ticker entries**: 355
- **Unique tickers**: 309  
- **Duplicate tickers found**: 42
- **Extra entries due to duplicates**: 46

## Duplicate Tickers Found

Based on analysis of `portfolios/comprehensive_model_portfolio.txt`, the following tickers appear multiple times across different model sections:

### High-Frequency Duplicates (3+ times)
- **005930.KS**: 3 times (Samsung Electronics)
- **ASML**: 3 times (ASML Holding)
- **DIS**: 3 times (Disney)
- **TSM**: 3 times (Taiwan Semiconductor)

### Two-Time Duplicates (42 total)
- **000660.KS**: 2 times (SK Hynix)
- **AMAT**: 2 times (Applied Materials)
- **AMD**: 2 times (Advanced Micro Devices)
- **AVGO**: 2 times (Broadcom)
- **AZO**: 2 times (AutoZone)
- **CRWD**: 2 times (CrowdStrike)
- **DANOY**: 2 times (Danone)
- **EC**: 2 times (Ecopetrol)
- **HD**: 2 times (Home Depot)
- **IBM**: 2 times (IBM)
- **INTC**: 2 times (Intel)
- **JNJ**: 2 times (Johnson & Johnson)
- **LLY**: 2 times (Eli Lilly)
- **LOW**: 2 times (Lowe's)
- **MA**: 2 times (Mastercard)
- **MU**: 2 times (Micron Technology)
- **NFLX**: 2 times (Netflix)
- **NOW**: 2 times (ServiceNow)
- **NVDA**: 2 times (NVIDIA)
- **OKTA**: 2 times (Okta)
- **ORLY**: 2 times (O'Reilly Automotive)
- **PANW**: 2 times (Palo Alto Networks)
- **PBR**: 2 times (Petrobras)
- **PFE**: 2 times (Pfizer)
- **PLTR**: 2 times (Palantir)
- **QCOM**: 2 times (Qualcomm)
- **RY**: 2 times (Royal Bank of Canada)
- **SAP**: 2 times (SAP)
- **SBUX**: 2 times (Starbucks)
- **SPOT**: 2 times (Spotify)
- **SQM**: 2 times (Sociedad Química y Minera)
- **TD**: 2 times (Toronto-Dominion Bank)
- **TGT**: 2 times (Target)
- **TJX**: 2 times (TJX Companies)
- **TXN**: 2 times (Texas Instruments)
- **UMC**: 2 times (United Microelectronics)
- **V**: 2 times (Visa)
- **VALE**: 2 times (Vale)

## Likely Causes of Duplicates

The duplicates likely occur because:

1. **Cross-Model Assignments**: Companies that could fit multiple models (e.g., TSM appears in manufacturing, emerging markets, and technology models)

2. **Technology Companies**: Many tech companies appear in both "Technology Services" (Model 2) and "Technology Growth" (Model 6)

3. **International Companies**: Some international companies appear in both emerging markets and their sector-specific models

4. **Multi-Business Companies**: Large conglomerates that operate across multiple industries

## Recommended Actions

1. **Review Model Assignments**: Each ticker should be assigned to only one primary model based on:
   - Primary business activity
   - Revenue source
   - Industry classification

2. **Create Model Priority Rules**: Establish clear hierarchy for model selection when companies could fit multiple categories

3. **Clean Up Portfolio**: Remove duplicates by assigning each ticker to its most appropriate single model

4. **Document Decisions**: Add comments explaining why specific companies were assigned to particular models

## Next Steps

Would you like me to:
1. Create a cleaned version of the portfolio with duplicates removed?
2. Suggest optimal model assignments for the duplicate tickers?
3. Create validation rules to prevent future duplicates?

---
*Report generated: June 30, 2025*
