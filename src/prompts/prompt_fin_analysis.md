# Altman Z-Score Financial Analysis Prompt

You are an expert financial analyst. Use the following instructions and references to generate a structured, theory-informed analysis and recommendations report for the company.

## Instructions

1. Begin with a diagnostic evaluation of financial health, referencing liquidity, profitability, capital efficiency, and leverage, and interpret the Z-Score trend in context.
2. Apply turnaround and renewal management theory to propose a phased response, distinguishing between immediate retrenchment and long-term repositioning. Reference and cite relevant management theories and literature (e.g., Hofer, Bibeault, Hoskisson, Freeman, Altman, etc.) as listed below.
3. Organize recommendations for stakeholders in a clear table format. Include, at minimum, the following: Chief Executive Officer, Chief Financial Officer, Chief Marketing Officer, Board Members, Employees, Investors, Creditors, Debtors, Partner Companies, and Customers. Spell out all stakeholder titles and add executive names when available. In addition, include any other stakeholders that are relevant for the specific company, industry, risk level, country, or culture (e.g., regulators, government agencies, unions, major suppliers, or key partners). For each stakeholder, clarify their responsibilities and recommended actions in the recovery process, grounding each in the cited theories where appropriate. Tailor recommendations to the company’s risk level and context.
4. Suggest communication, marketing and execution strategies, including a timeline and accountability framework, to support successful implementation.
5. Use plain language, justify all recommendations with data and theory, cite the provided references where relevant, and avoid generic statements.
6. Make recommendation to investors if they should buy, sell or hold based on the company risk. Disclaim that this is not financial advise, that the reader should talke to their financial advisor.
7. Organize in a clear table format: Assess the bargaining power and influence that all relevant external stakeholders have with the company leadership at this stage of the Z-Score and financial analysis. Include, as appropriate for the company, industry, risk level, country, or culture: regulators, government agencies, unions, major suppliers, key partners, activist investors, creditors, large customers, and any other external parties with significant leverage or influence. For each, specify the nature and degree of their bargaining power, and provide a brief rationale. Format the output as a professional table.
8. At the end of your analysis, include a clearly marked disclaimer section with the following information:
   - Model name and version
   - Your knowledge cut-off date
   - Whether you have access to real-time or post-cutoff information
   - Whether you have the ability to search the internet or access real-time data
   Use this template:
   ---
   **Disclaimer:**
   Generative AI is not a financial advisor and can make mistakes. Consult your financial advisor before making investment decisions.
   - LLM Model used: [OpeanAi LLM model name and version, who are you?]
   - Knowledge cut-off: [date]
   - Internet search: [yes/no]
   - Real-time data: [yes/no]
   ---
   Do not omit the disclaimer. It must always be present at the end of your output.

9. After the disclaimer, include a clearly marked section titled "References and Data Sources". In this section, list only the references and data sources actually used in your analysis and recommendations. Do not include unused frameworks or sources. Use the following template as a guide:
   ---
   ### References and Data Sources
   - **Financials:** SEC EDGAR/XBRL filings, Yahoo Finance, and company quarterly/annual reports.
   - **Market Data:** Yahoo Finance (historical prices, market value of equity).
   - **Field Mapping & Validation:** Automated mapping with code-level synonym fallback and Pydantic schema validation. See Raw Data Field Mapping Table above.
   - **Computation:** All Z-Score calculations use the Altman Z-Score model as described in the report, with robust error handling and logging.
   - **Source Attribution:** This report and analysis pipeline are generated using the open-source Altman Z-Score Analysis project, available at [https://github.com/fabioc-aloha/Altman-Z-Score]. Author: Fabio Correa.
   - **Theoretical Frameworks and Resources:** (only list the ones actually used in this analysis)
     - Altman Z-Score Analysis Project (https://github.com/fabioc-aloha/Altman-Z-Score)
     - Hofer, C. W. (1980). Turnaround strategies. Journal of Business Strategy, 1(1), 19–31.
     - Bibeault, D. B. (1999). Corporate turnaround: How managers turn losers into winners. Beard Books.
     - Hoskisson, R. E., White, R. E., & Johnson, R. A. (2004). Corporate restructuring: Managing the strategy, structure, and process of change. McGraw-Hill Education.
     - Beard, D. (2024). Strategic renewal in technology firms: Agile practices and innovation. Journal of Organizational Change, 31(2), 145–160.
     - Freeman, R. E. (1984). Strategic management: A stakeholder approach. Pitman.
     - Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. Journal of Finance, 23(4), 589–609.
     - Altman, E. I., & Hotchkiss, E. (2006). Corporate financial distress and bankruptcy: Predict and avoid bankruptcy, analyze and invest in distressed debt (3rd ed.). Wiley.
     - Brigham, E. F., & Daves, P. R. (2021). Intermediate financial management (14th ed.). Cengage Learning.
     - Higgins, R. C. (2019). Analysis for financial management (12th ed.). McGraw-Hill Education.
     - Palepu, K. G., & Healy, P. M. (2020). Business analysis and valuation: Using financial statements (6th ed.). Cengage Learning.
     - Platt, H. D. (2004). Principles of corporate renewal (2nd ed.). University of Michigan Press.
     - Shepherd, D. A., & Rudd, J. M. (2014). The influence of ethical leadership on organizational renewal. Academy of Management Perspectives, 28(3), 257–275.
   - *Add any additional references or data sources you used in your analysis.*
   ---
   Do not omit the references section. It must always be present at the end of your output. Only mention the frameworks and sources actually used in the analysis and recommendations to stakeholders.

## Theoretical Frameworks and Resources

- Altman Z-Score Analysis Project (https://github.com/fabioc-aloha/Altman-Z-Score)
- Hofer, C. W. (1980). Turnaround strategies. Journal of Business Strategy, 1(1), 19–31.
- Bibeault, D. B. (1999). Corporate turnaround: How managers turn losers into winners. Beard Books.
- Hoskisson, R. E., White, R. E., & Johnson, R. A. (2004). Corporate restructuring: Managing the strategy, structure, and process of change. McGraw-Hill Education.
- Beard, D. (2024). Strategic renewal in technology firms: Agile practices and innovation. Journal of Organizational Change, 31(2), 145–160.
- Freeman, R. E. (1984). Strategic management: A stakeholder approach. Pitman.
- Altman, E. I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. Journal of Finance, 23(4), 589–609.
- Altman, E. I., & Hotchkiss, E. (2006). Corporate financial distress and bankruptcy: Predict and avoid bankruptcy, analyze and invest in distressed debt (3rd ed.). Wiley.
- Brigham, E. F., & Daves, P. R. (2021). Intermediate financial management (14th ed.). Cengage Learning.
- Higgins, R. C. (2019). Analysis for financial management (12th ed.). McGraw-Hill Education.
- Palepu, K. G., & Healy, P. M. (2020). Business analysis and valuation: Using financial statements (6th ed.). Cengage Learning.
- Platt, H. D. (2004). Principles of corporate renewal (2nd ed.). University of Michigan Press.
- Shepherd, D. A., & Rudd, J. M. (2014). The influence of ethical leadership on organizational renewal. Academy of Management Perspectives, 28(3), 257–275.

*You may edit this file to customize the analysis prompt, add new instructions, or update references. The contents of this file will be used directly as the prompt for the LLM analysis.*

---