# Altman Z-Score Model Guide

## Model Summary Table

| Model Name         | Formula (Z)                                      | Best For                        | Key Ratios Used                |
|--------------------|-------------------------------------------------|----------------------------------|-------------------------------|
| Original           | 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅           | Public manufacturing companies   | X₁, X₂, X₃, X₄ (market), X₅   |
| Private            | 0.717X₁ + 0.847X₂ + 3.107X₃ + 0.420X₄ + 0.998X₅ | Private manufacturing companies  | X₁, X₂, X₃, X₄ (book), X₅     |
| Emerging           | 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ + 3.25         | Non-manufacturing, emerging mkts | X₁, X₂, X₃, X₄                |
| Financial          | 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ + 3.25         | Banks, financial institutions    | X₁ (adj), X₂, X₃, X₄ (book)   |
| Retail             | Modified ratios for retail                       | Retail, e-commerce               | X₁-X₆ (see below)             |

*See [APIS.md](APIS.md) for data source mapping, [FLOW.md](FLOW.md) for architecture, and [REFACTORING_PLAN.md](REFACTORING_PLAN.md) for implementation details.*

---

## Available Models

### 1. Original Z-Score (`--model original`)
The original Altman Z-Score model designed for public manufacturing companies.

**Formula:**
Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅

**Variables:**
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

---

### 2. Private Company Z'-Score (`--model private`)
Modified version for private manufacturing companies, using book value instead of market value.

**Formula:**
Z' = 0.717X₁ + 0.847X₂ + 3.107X₃ + 0.420X₄ + 0.998X₅

**Variables:**
- X₁ = Working Capital / Total Assets
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Book Value of Equity / Total Liabilities
- X₅ = Sales / Total Assets

**Interpretation:**
- Z' > 2.9: Safe Zone
- 1.23 ≤ Z' ≤ 2.9: Grey Zone
- Z' < 1.23: Distress Zone

**Best For:**
- Private manufacturing companies
- Companies without market value data
- Industrial firms with book value focus

---

### 3. Non-Manufacturing/Emerging Markets Z''-Score (`--model emerging`)
Generalized version removing industry-sensitive asset turnover ratio.

**Formula:**
Z'' = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ + 3.25

**Variables:**
- X₁ = Working Capital / Total Assets
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Book Value of Equity / Total Liabilities

**Interpretation:**
- Z'' > 5.85: Safe Zone
- 3.75 ≤ Z'' ≤ 5.85: Grey Zone
- Z'' < 3.75: Distress Zone

**Best For:**
- Non-manufacturing companies
- Service sector firms
- Emerging market companies
- Technology companies

---

### 4. Financial Institutions Z-Score (`--model financial`)
Specialized model for banks and financial institutions.

**Formula:**
Z = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ + 3.25

**Variables:**
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

---

### 5. Retail Industry Model (`--model retail`)
Specialized model for retail sector with inventory focus.

**Formula:**
Modified ratios for retail characteristics (see below)

**Variables:**
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

---

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

---

## Model Selection Theory (Altman Z-Score)

Model selection is grounded in the original and extended Altman Z-Score research, which demonstrates that different industries, company types, and data availabilities require distinct formulas for accurate bankruptcy risk assessment. The following criteria are used to select the most appropriate model:

**1. Industry Sector**
   - Manufacturing: Use the Original or Private model depending on public/private status.
   - Financial Institutions: Use the Financial model (specialized ratios for banks, insurance, etc.).
   - Retail: Use the Retail model (accounts for inventory turnover and sector-specific risks).
   - Service/Tech/Emerging: Use the Emerging model (removes asset turnover, adapts to asset-light and new-economy firms).

**2. Public vs. Private**
   - Public companies: Prefer models using market value of equity (Original, Retail).
   - Private companies: Use models based on book value of equity (Private, Emerging).

**3. Data Availability**
   - If market value data is missing, default to book value models.
   - If inventory data is missing, avoid Retail model.
   - If company is asset-light, prefer Emerging model.

**4. Geographic Region**
   - Emerging markets: Use Emerging model to account for different accounting standards and risk profiles.

**5. Company Age & Characteristics**
   - Young, high-growth, or non-traditional firms: Use Emerging or Service model.
   - Mature, asset-intensive firms: Use Original or Private model.

**6. Fallback Logic**
   - If no model fits perfectly, select the most conservative (usually Private or Emerging).

**References:**
- Altman, E.I. (1968, 2000, 2013). [See MODELS.md, APIS.md, and FLOW.md for implementation details.]
- See [REFACTORING_PLAN.md](REFACTORING_PLAN.md) for how these rules are encoded in the codebase.

---

## Model Selection Guidelines

1. **Financial Services**
   - Banks, insurance companies, credit unions
   - Specialized financial ratios and thresholds
   - Example: JP Morgan (JPM)

2. **Retail Companies**
   - Department stores, online retail
   - Accounts for inventory turnover
   - Example: Amazon (AMZN), Walmart (WMT)

3. **Service Industry**
   - Professional services, consulting
   - Asset-light businesses
   - Example: Accenture (ACN)

4. **Manufacturing (Original)**
   - Heavy industry, traditional manufacturing
   - Asset-intensive operations
   - Example: General Electric (GE)

5. **Emerging Markets**
   - Developing economies
   - Accounts for different accounting standards
   - Example: Mercadolibre (MELI)

6. **Private Companies**
   - Default for non-public or general use
   - Conservative thresholds
   - Example: Any non-public company

---

## Example Usage

```bash
# Use retail model for Amazon
python main.py AMZN --model retail

# Use financial model for JP Morgan
python main.py JPM --model financial

# Use service model for Accenture
python main.py ACN --model service
```

---

*For implementation details, see [REFACTORING_PLAN.md](REFACTORING_PLAN.md). For API mapping, see [APIS.md](APIS.md). For data flow, see [FLOW.md](FLOW.md).*
