# AI Peer Company Identification Prompt

As a financial analyst specializing in peer company identification, analyze {ticker} and identify 5-7 publicly traded peer companies.

## TARGET COMPANY FINANCIAL PROFILE:
- Ticker: {ticker}
- Total Assets: {total_assets}
- Annual Revenue: {revenue}
- Market Capitalization: {market_cap}
- Sector: {sector}
- Industry: {industry}
- Current Ratio: {current_ratio}
- Debt-to-Equity: {debt_to_equity}
- Gross Margin: {gross_margin}
- Operating Margin: {operating_margin}

## PEER SELECTION METHODOLOGY:
1. **Industry Classification**: Same GICS sector/sub-industry preferred
2. **Business Model Similarity**: Revenue streams, customer base, operational structure
3. **Financial Scale**: Market cap between 0.3x to 3x of target ({market_cap})
4. **Geographic Presence**: Similar market exposure (domestic vs international)
5. **Capital Structure**: Comparable debt levels and asset intensity
6. **Profitability Profile**: Similar margin structures and business economics

## SPECIFIC ANALYSIS REQUIREMENTS:
- If {ticker} is in **Technology**: Focus on software vs hardware, B2B vs B2C models
- If {ticker} is in **Healthcare**: Distinguish pharma, biotech, devices, services
- If {ticker} is in **Financial Services**: Bank vs insurance vs asset management
- If {ticker} is in **Industrial**: Manufacturing vs services vs distribution

## OUTPUT FORMAT - Provide ONLY ticker symbols with brief rationale:
TICKER: Specific reason for peer selection (focus on business model & financial similarity)

### EXAMPLE:
MSFT: Cloud infrastructure and enterprise software with similar recurring revenue model
GOOGL: Digital advertising platform with comparable tech infrastructure and margins

**CRITICAL**: Focus on operational and financial similarity, not just sector classification.
