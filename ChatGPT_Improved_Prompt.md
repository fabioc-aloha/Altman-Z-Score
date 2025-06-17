**Configuration**  
- **TICKER:** `[ENTER_TICKER]`  
- **START_DATE:** `[YYYY-MM-DD]`  
- **PEER_TICKERS:** `[ENTER_PEER_TICKERS_COMMA_SEPARATED]`  

---

Analyze **[TICKER]** by calculating Altman Z-Scores for each quarter since **[START_DATE]** using publicly available data (quarterly balance sheets, income statements, and weekly closing prices) from Yahoo Finance. Compute a trailing-twelve-month Z-Score for the most recent quarter and compare its five Altman components and overall score against peers: **[PEER_TICKERS]**.

# Financial Analysis Report Instructions

## ROLE AND CONTEXT  
You are an expert financial analyst tasked with producing a structured, executive-ready report using the Altman Z-Score framework.

## DATA SOURCES  
- Quarterly balance sheet and income-statement line items from Yahoo Finance since **[START_DATE]**  
- Weekly closing share prices from Yahoo Finance for market-cap calculations  

## PEER GROUP  
**[PEER_TICKERS]**

## REPORT STRUCTURE (10 SECTIONS)  
1  TL;DR / Executive Summary  
2  Company Profile  
3  Diagnostic Evaluation of Financial Health  
4  Turnaround & Renewal Theory Application  
5  Internal Stakeholder Recommendations  
6  Communication, Marketing & Execution Strategy  
7  Investor Recommendation (Risk-Aware)  
8  Market Sentiment Analysis (Analyst Recommendations)  
9  References and Data Sources  
10 Appendices (LLM-Generated)

## CRITICAL REQUIREMENTS  
- Adapt tone to Z-Score risk level (Distress <1.8, Grey 1.8–3.0, Safe >3.0)  
- Leverage all available data (Z-Score components, financials, price trends, peer context, management changes, news)  
- Include Z-Score vs. price-trend analysis in every recommendation  
- Justify all conclusions with data citations  
- Write in plain, executive-friendly language

---

**Next Step:** Replace `[ENTER_TICKER]`, `[YYYY-MM-DD]`, and `[ENTER_PEER_TICKERS_COMMA_SEPARATED]` with your desired values, then use this template to generate the full 10-section report. ```
