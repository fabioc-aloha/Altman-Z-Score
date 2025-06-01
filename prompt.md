## Checklist: Prompt Refinement Ideas

### Implemented:
- Diagnostic evaluation of financial health using Altman Z-Score and supporting ratios.
- Plain-language explanations for technical terms and implications.
- Tailored recommendations for CEO, CFO, Board of Directors, and Investors.
- Structured analysis with sections for financial evaluation, recommendations, and communication strategies.
- Use of management theories (e.g., Hofer, Bibeault, Hoskisson) to justify recommendations.
- Reference to industry benchmarks and prior periods where possible.

### Pending:
- AI-powered anomaly detection for ratio trends.
- "What-if" scenario analysis for CAPEX adjustments.
- Advanced notifications for Z-Score thresholds.
- Integration of RACI chart for execution ownership.
- Currency conversion for non-USD firms.
- Optimization of data caching to reduce API calls.

---

# Prompt Refinement Ideas for Financial Analysis & Commentary

This document collects and organizes ideas for refining the prompt used to generate the "Financial Analysis & Commentary" section in the Altman Z-Score report. Use this as a living document to discuss, compare, and select the best approach for future automation or LLM-driven analysis.

---

## Goals
- Make the analysis more targeted, actionable, and context-aware
- Ensure both quantitative and qualitative insights
- Provide clear, plain-language explanations for technical terms
- Support different investor profiles with tailored recommendations
- Encourage comparison to industry benchmarks when possible
- Summarize key takeaways concisely

---

## Section Structure for Automated Analysis

### 1. Financial Analysis & Ratios Evaluation
- Provide a detailed evaluation of the company's financial health based on the Altman Z-Score and supporting ratios (current ratio, debt-to-equity, etc.).
- Explain the meaning and implications of each key ratio in plain language.
- Highlight trends, strengths, and vulnerabilities in the company's financials.
- Compare to industry benchmarks if available.

### 2. Recommendations to Stakeholders
- Offer tailored, actionable recommendations for each of the following:
    - **CEO:** Strategic actions to address financial weaknesses or leverage strengths.
    - **CFO:** Financial management, risk mitigation, and capital structure advice.
    - **Board of Directors:** Oversight, governance, and long-term risk considerations.
    - **Investors:** Buy/hold/sell guidance, risk warnings, and opportunity assessment.
- Justify each recommendation with reference to the financial analysis and current market context.

---

## Refined Prompt Structure (Informed by OneStockAnalysis.md)

### 1. Financial Analysis & Ratios Evaluation
- Begin with a diagnostic evaluation of the company's financial performance across liquidity, profitability, capital efficiency, and leverage, referencing the Altman Z-Score and supporting ratios.
- Interpret ratio-level insights as indicators of broader operational and strategic health, using both quantitative data and qualitative context.
- Highlight trends, strengths, and vulnerabilities, and connect them to the urgency of intervention (e.g., Safe, Grey, Distress Zone).
- Use plain language to explain technical terms and implications for bankruptcy risk.
- Compare to industry benchmarks and prior periods where possible.
- Summarize the primary drivers of Z-Score movement and financial stress.

### 2. Theory-Driven Strategic Recommendations
- Structure recommendations in two phases: (a) Turnaround (retrenchment, operational control), (b) Renewal (strategic repositioning, innovation, stakeholder trust).
- For each phase, link recommendations to established management theories (e.g., Hofer, Bibeault, Hoskisson) and the company's current financial/operational state.
- Justify each recommendation with reference to the diagnostic findings and relevant theory.

### 3. Role-Based Stakeholder Guidance
- Provide tailored, actionable recommendations for:
    - **CEO:** Vision, leadership, and communication priorities for turnaround and renewal.
    - **CFO:** Financial management, liquidity, and risk mitigation strategies.
    - **Board of Directors:** Oversight, governance, and contingency planning (e.g., Chapter 11 readiness).
    - **Investors:** Buy/hold/sell guidance, risk warnings, and monitoring priorities.
- For each stakeholder, clarify their role in the execution timeline and accountability matrix.
- Reference the RACI chart or similar frameworks for execution ownership.

### 4. Communication and Execution
- Recommend communication strategies for internal and external stakeholders to rebuild trust and align expectations.
- Suggest a phased execution timeline (e.g., stabilization, restructuring, renewal) with key milestones and metrics.
- Emphasize the need for transparency, feedback loops, and cultural renewal as part of the recovery process.

---

## Theoretical Frameworks and References for Analysis

When generating analysis and recommendations, explicitly draw on the following management theories and references:

- **Turnaround Strategy Theory:**
    - Hofer, C. W. (1980). Turnaround strategies. Journal of Business Strategy, 1(1), 19–31.
    - Bibeault, D. B. (1999). Corporate turnaround: How managers turn losers into winners. Beard Books.
    - Focus: Two-stage process (retrenchment and recovery), cost containment, governance, and operational accountability.

- **Strategic Renewal Theory:**
    - Hoskisson, R. E., White, R. E., & Johnson, R. A. (2004). Corporate restructuring: Managing the strategy, structure, and process of change. McGraw-Hill Education.
    - Beard, D. (2024). Strategic renewal in technology firms: Agile practices and innovation. Journal of Organizational Change, 31(2), 145–160.
    - Focus: Resource reallocation, innovation, leadership/cultural renewal, stakeholder engagement.

- **Stakeholder Theory:**
    - Freeman, R. E. (1984). Strategic management: A stakeholder approach. Pitman.
    - Focus: Stakeholder alignment, engagement, and trust-building as prerequisites for successful turnaround and renewal.

- **Financial Distress and Z-Score:**
    - Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. Journal of Finance, 23(4), 589–609.
    - Altman, E. I., & Hotchkiss, E. (2006). Corporate financial distress and bankruptcy: Predict and avoid bankruptcy, analyze and invest in distressed debt (3rd ed.). Wiley.
    - Focus: Quantitative assessment of bankruptcy risk, financial diagnostics, and urgency of intervention.

- **Additional References:**
    - Brigham, E. F., & Daves, P. R. (2021). Intermediate financial management (14th ed.). Cengage Learning.
    - Higgins, R. C. (2019). Analysis for financial management (12th ed.). McGraw-Hill Education.
    - Palepu, K. G., & Healy, P. M. (2020). Business analysis and valuation: Using financial statements (6th ed.). Cengage Learning.
    - Platt, H. D. (2004). Principles of corporate renewal (2nd ed.). University of Michigan Press.
    - Shepherd, D. A., & Rudd, J. M. (2014). The influence of ethical leadership on organizational renewal. Academy of Management Perspectives, 28(3), 257–275.

When possible, cite these theories and references in the analysis and recommendations to provide academic grounding and context.

---

## Prompt Refinement Suggestions

### 1. Analytical Depth
- Explicitly request both quantitative (ratios, trends) and qualitative (management, market sentiment) insights
- Ask for context-aware risk assessment, not just ratio interpretation
- Request actionable recommendations for different investor profiles

### 2. Structure and Clarity
- Encourage discussion of trend alignment/divergence between Z-Score and market price
- Ask for plain-language explanations of technical terms
- Request a summary of key drivers behind the Z-Score movement
- Prompt for a comparison to industry benchmarks if available
- Ask for a clear, concise bottom-line summary

### 3. Example Comprehensive Prompt
> Using the provided financial data and Altman Z-Score results, generate a structured analysis and recommendations report for the company.
> 1. Begin with a diagnostic evaluation of financial health, referencing liquidity, profitability, capital efficiency, and leverage, and interpret the Z-Score trend in context.
> 2. Apply turnaround and renewal management theory to propose a phased response, distinguishing between immediate retrenchment and long-term repositioning. Reference and cite relevant management theories and literature (e.g., Hofer, Bibeault, Hoskisson, Freeman, Altman, etc.) as listed above.
> 3. Offer role-based recommendations for the CEO, CFO, Board, and Investors, clarifying their responsibilities and actions in the recovery process, and grounding each in the cited theories where appropriate.
> 4. Suggest communication and execution strategies, including a timeline and accountability framework, to support successful implementation.
> Use plain language, justify all recommendations with data and theory, cite the provided references where relevant, and avoid generic statements.

---

## Next Steps
- Review and discuss these ideas with the team
- Select or adapt a prompt for implementation
- Track changes and rationale in this file
