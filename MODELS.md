# Altman Z-Score Model Guide

## Available Models

### 1. Original Z-Score (--model original)
The original Altman Z-Score model designed for public manufacturing companies.

**Formula:** Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅

Where:
- X₁ = Working Capital / Total Assets
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Market Value of Equity / Total Liabilities
- X₅ = Sales / Total Assets

**Interpretation:**
- Z > 2.99: Safe Zone
- 1.81 ≤ Z ≤ 2.99: Grey Zone
- Z < 1.81: Distress Zone

**Best For:**
- Public manufacturing companies
- Companies with market value data
- Traditional industrial firms

### 2. Private Company Z'-Score (--model private)
Modified version for private manufacturing companies, using book value instead of market value.

**Formula:** Z' = 0.717X₁ + 0.847X₂ + 3.107X₃ + 0.420X₄ + 0.998X₅

Where:
- X₄ = Book Value of Equity / Total Liabilities
- Other ratios same as original model

**Interpretation:**
- Z' > 2.9: Safe Zone
- 1.23 ≤ Z' ≤ 2.9: Grey Zone
- Z' < 1.23: Distress Zone

**Best For:**
- Private manufacturing companies
- Companies without market value data
- Industrial firms with book value focus

### 3. Non-Manufacturing/Emerging Markets Z''-Score (--model emerging)
Generalized version removing industry-sensitive asset turnover ratio.

**Formula:** Z'' = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ + 3.25

**Interpretation:**
- Z'' > 5.85: Safe Zone
- 3.75 ≤ Z'' ≤ 5.85: Grey Zone
- Z'' < 3.75: Distress Zone

**Best For:**
- Non-manufacturing companies
- Service sector firms
- Emerging market companies
- Technology companies

### 4. Financial Institutions Z-Score (--model financial)
Specialized model for banks and financial institutions.

**Formula:** Z = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ + 3.25

Where:
- X₁ = (Equity - Intangible Assets) / Total Assets
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Book Value of Equity / Total Liabilities

**Interpretation:**
- Z > 2.6: Safe Zone
- 1.1 ≤ Z ≤ 2.6: Grey Zone
- Z < 1.1: Distress Zone

**Best For:**
- Banks
- Insurance companies
- Financial services firms
- Investment companies

### 5. Zeta® Model (--model zeta)
Enhanced model with additional variables for mature companies.

**Formula:** Uses seven variables including stability metrics

Where:
- X₁ = Return on Assets (EBIT / Total Assets)
- X₂ = Stability of Earnings
- X₃ = Debt Service
- X₄ = Cumulative Profitability
- X₅ = Liquidity
- X₆ = Capitalization
- X₇ = Size

**Best For:**
- Mature public companies
- Companies with 5+ years of history
- Complex corporate structures

### 6. Retail Industry Model (--model retail)
Specialized model for retail sector with inventory focus.

**Formula:** Modified ratios for retail characteristics

Where:
- X₁ = (Current Assets - Inventory) / Total Assets
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Market Value of Equity / Total Liabilities
- X₅ = Sales / Total Assets
- X₆ = Inventory Turnover

**Best For:**
- Retail companies
- E-commerce businesses
- Companies with significant inventory

## Automatic Model Selection

The tool can automatically select the appropriate model based on:
1. Industry sector
2. Public/private status
3. Geographic region
4. Company characteristics
5. Data availability
6. Company age

To use automatic selection, simply run without the --model flag:
```bash
python main.py TICKER
```

The tool will explain which model was selected and why.

## Model Selection Guidelines

1. **Financial Companies**
   - Always use financial model for banks, insurance, and financial services
   - Examples:
     - JPMorgan Chase (JPM): Financial model due to banking sector
     - Goldman Sachs (GS): Financial model for investment banking
     - Visa (V): Financial model for payment services

2. **Retail Companies**
   - Use retail model for companies with significant inventory
   - Applicable to both online and traditional retail
   - Examples:
     - Walmart (WMT): Retail model for traditional retail
     - Amazon (AMZN): Retail model despite tech presence
     - Target (TGT): Retail model with inventory focus

3. **Manufacturing**
   - Public companies: Use original model
   - Private companies: Use private model
   - Examples:
     - Boeing (BA): Original model for public manufacturing
     - Ford (F): Original model for automotive
     - Private manufacturing: Private model with book values

4. **Mature Companies**
   - Consider Zeta model if 5+ years of history available
   - Particularly useful for complex organizations
   - Examples:
     - Microsoft (MSFT): Zeta model for mature tech
     - Johnson & Johnson (JNJ): Zeta model for established healthcare
     - Procter & Gamble (PG): Zeta model for consumer goods

5. **Other Companies**
   - Use emerging markets model as general purpose solution
   - Suitable for service companies and tech firms
   - Examples:
     - Netflix (NFLX): Emerging model for digital services
     - Airbnb (ABNB): Emerging model for platform business
     - Spotify (SPOT): Emerging model for tech services

## Model Override Guidelines

While the tool automatically selects the most appropriate model, you can force a specific model using the `--model` flag. Use this with caution and consider these guidelines:

### Appropriate Override Cases

1. **Testing Different Models**
   ```bash
   # Compare different model results for the same company
   python main.py MSFT --model original
   python main.py MSFT --model zeta
   ```
   Useful for understanding how different models evaluate the same company.

2. **Industry Transition Cases**
   ```bash
   # Example: Amazon transitioning from tech to retail
   python main.py AMZN --model retail  # Focus on retail operations
   python main.py AMZN --model emerging  # Focus on tech operations
   ```
   Companies straddling multiple sectors might benefit from analysis under different models.

3. **Research Purposes**
   ```bash
   # Analyze how financial metrics compare across models
   python main.py JPM --model financial
   python main.py JPM --model original
   ```
   Useful for academic research or detailed financial analysis.

### Warning Signs

The tool will warn you when:
1. Using manufacturing models for financial institutions
2. Using financial models for retail companies
3. Using retail models for service companies

Example warning scenarios:
```bash
# These will generate appropriateness warnings
python main.py JPM --model original   # Warning: Financial institution with manufacturing model
python main.py WMT --model financial  # Warning: Retail company with financial model
python main.py MSFT --model retail    # Warning: Tech company with retail model
```

### Best Practices for Model Override

1. **Default to Automatic Selection**
   ```bash
   python main.py TICKER  # Let the tool choose the appropriate model
   ```

2. **Document Override Reasons**
   ```bash
   # Example comment explaining override
   # Using retail model for AMZN due to focus on retail operations
   python main.py AMZN --model retail
   ```

3. **Compare with Default**
   ```bash
   # Run both automatic and forced model for comparison
   python main.py TICKER
   python main.py TICKER --model your_choice
   ```

4. **Consider Company Evolution**
   ```bash
   # Example: Company transitioning from manufacturing to services
   python main.py TICKER --model original  # Historical manufacturing focus
   python main.py TICKER --model emerging  # Current service focus
   ```

### Model Appropriateness Matrix

| Company Type      | Most Appropriate     | Potentially Suitable | Not Recommended    |
|------------------|---------------------|---------------------|-------------------|
| Banks            | financial           | emerging            | retail, original  |
| Manufacturers    | original, private   | zeta                | financial        |
| Retailers        | retail             | original            | financial        |
| Tech Companies   | emerging           | zeta                | retail, financial |
| Mature Companies | zeta               | original, emerging  | -                |
| Service Firms    | emerging           | zeta                | retail           |

Remember: The automatic model selection is designed to choose the most appropriate model based on company characteristics. Override this only when you have a specific analytical purpose or research goal.

## Example Commands

```bash
# Financial Institution Analysis
python main.py JPM --model financial

# Retail Company Analysis
python main.py WMT --model retail

# Manufacturing Company Analysis
python main.py BA --model original

# Mature Company Analysis
python main.py MSFT --model zeta

# Service Company Analysis
python main.py NFLX --model emerging

# Automatic Model Selection
python main.py TICKER  # Auto-selects appropriate model
```

## Common Use Cases

1. **Bank Analysis**
   ```bash
   python main.py JPM BAC GS --model financial
   ```
   Analyzes multiple banks using the financial institutions model.

2. **Retail Comparison**
   ```bash
   python main.py WMT TGT COST --model retail
   ```
   Compares multiple retail companies with inventory-focused metrics.

3. **Mixed Industry Analysis**
   ```bash
   python main.py MSFT JPM WMT
   ```
   Auto-selects appropriate model for each company:
   - MSFT → Zeta model (mature tech)
   - JPM → Financial model (banking)
   - WMT → Retail model (retail)
