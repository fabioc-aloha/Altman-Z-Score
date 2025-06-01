## Checklist: Qualitative Validation Ideas

### Implemented:
- Design of a prompt template summarizing company details, Z-Score, and financial highlights.
- Integration of LLM call to generate qualitative validation.
- Appending qualitative validation section to `zscore_full_report` with LLM summary, news headlines, and references.
- Error handling for LLM call failures with fallback messaging.
- Testing on multiple tickers to ensure relevance and accuracy of LLM output.
- Documentation of the qualitative validation feature in `README.md` and `PLAN.md`.

### Pending:
- Caching of LLM responses for auditability and cost control.
- Advanced notifications for Z-Score thresholds.
- Refinement of prompt and output formatting based on user feedback.

---

# Implementation Plan: Qualitative Validation with LLM in Z-Score Reports

## Goal
Enhance the Altman Z-Score reporting pipeline by appending a qualitative, LLM-generated validation section to each `zscore_full_report`. This section will contextualize the quantitative Z-Score result using recent news, analyst sentiment, credit/market data, and explicit references with links, making the report more actionable and user-friendly.

---

## Steps

### 1. Design Prompt Template
- Create a prompt template that summarizes:
  - Company name, ticker, industry, and analysis date
  - Latest Z-Score and diagnostic (e.g., "Distress Zone")
  - Recent financial highlights (revenue, net income, debt, margins, etc.)
  - Request for the LLM to validate or contextualize the Z-Score using recent news, analyst sentiment, and credit ratings
  - **Explicitly request 2-3 recent news headlines with links and a list of references (credit ratings, analyst reports, etc.)**

### 2. Integrate LLM Call
- Add a function to the reporting pipeline (e.g., in `reporting.py`) that:
  - Gathers the above data for the current report
  - Calls the LLM (e.g., Azure OpenAI) with the prompt
  - Receives and parses the qualitative summary, news headlines (with links), and references

### 3. Append to Report
- At the end of each `zscore_full_report`, append a section:
  - `## Qualitative Validation (LLM)`
  - Include the LLM's summary as a blockquote
  - Add a markdown list of recent news headlines with links
  - Add a markdown list of explicit references (credit ratings, analyst reports, etc.)
  - Ensure clear spacing and formatting for readability

### 4. Error Handling & Caching
- If the LLM call fails, append a message indicating qualitative validation was unavailable
- Optionally, cache LLM responses for auditability and cost control

### 5. Testing
- Test on multiple tickers (e.g., F, MSFT, JPM, TSM) to ensure:
  - The LLM summary, news, and references are relevant and accurate
  - The section is appended and formatted correctly
  - The pipeline handles failures gracefully

### 6. Documentation
- Update `README.md` and `PLAN.md` to describe the new qualitative validation feature
- Document prompt template and LLM usage for future maintainers

---

## Example Section (to be appended)

```
## Qualitative Validation (LLM)

> The Altman Z-Score for Microsoft Corporation indicates "Safe Zone" for all recent quarters, suggesting a very low risk of bankruptcy. This is supported by strong analyst sentiment, robust financials, and positive news coverage of Microsoft's AI and cloud growth.

### Recent News Headlines
- [Microsoft's AI Strategy: A Game Changer for Cloud Growth](https://www.example.com/news/microsoft-ai-strategy) (News)
- [Analyst Upgrades Microsoft Following Strong Earnings Report](https://www.example.com/news/microsoft-analyst-upgrade) (Analyst Report)
- [Microsoft Maintains AAA Credit Rating Amidst Strong Financial Performance](https://www.example.com/news/microsoft-credit-rating) (Credit Rating)

### References
- Credit Ratings: Moody's, S&P Global Ratings
- Analyst Reports: Goldman Sachs, Morgan Stanley
- News Articles: Bloomberg, Reuters, CNBC
```

---

## Next Steps
- Implement the above steps in the reporting pipeline
- Review and refine the prompt and output formatting based on user feedback
