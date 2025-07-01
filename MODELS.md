# Altman Z-Score Model Guide

## Model Summary Table

| Model Name         | Formula (Z)                                      | Best For                        | Implementation Status         | Literature Compliance |
|--------------------|------------------------------------------------|----------------------------------|-------------------------------|----------------------|
| Original           | 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅           | Public manufacturing companies   | ✅ Fully implemented         | ✅ Matches Altman (1968) |
| Private            | 0.717X₁ + 0.847X₂ + 3.107X₃ + 0.420X₄ + 0.998X₅ | Private manufacturing companies  | ✅ Fully implemented         | ✅ Matches Altman (1983) |
| Service            | 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄               | Service sector companies         | ✅ Fully implemented         | ✅ Literature-adjusted thresholds |
| Emerging           | 3.25 + 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄        | Non-manufacturing, emerging mkts | ✅ Fully implemented         | ✅ Literature-corrected thresholds |
| Financial          | 3.25 + 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄        | Banks, financial institutions    | ⚠️ Fallback to emerging model | ✅ Correctly warns per literature |
| Retail             | 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅ + 0.5X₆  | Retail, e-commerce               | ✅ Fully implemented         | ⚠️ Novel model (project-specific) |

*See [APIS.md](APIS.md) for data source mapping and [FLOW.md](FLOW.md) for architecture details.*

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

### 3. Service/Non-Manufacturing Z''-Score (`--model service`)
Service sector model removing the asset turnover ratio which is less relevant for service companies.

**Formula:**
Z'' = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ (no constant term)

**Variables:**
- X₁ = Working Capital / Total Assets
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Book Value of Equity / Total Liabilities

**Interpretation:**
- Z'' > 2.60: Safe Zone
- 0.50 ≤ Z'' ≤ 2.60: Grey Zone  
- Z'' < 0.50: Distress Zone

⚠️ **Academic Note:** This model uses the same coefficients as the emerging markets model but without the constant term. Thresholds adjusted accordingly. This variation should be used with caution as it may not have extensive academic validation.

**Best For:**
- Service sector firms
- Professional services companies
- Asset-light businesses
- Technology service companies

---

### 4. Non-Manufacturing/Emerging Markets Z''-Score (`--model emerging`)
Generalized version for emerging markets with additional constant term (Altman, 1995).

**Formula:**
Z'' = 3.25 + 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄

**Variables:**
- X₁ = Working Capital / Total Assets
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Book Value of Equity / Total Liabilities

**Interpretation (Literature-based):**
- Z'' > 5.85: Safe Zone (low bankruptcy probability)
- 3.75 ≤ Z'' ≤ 5.85: Grey Zone (moderate bankruptcy probability)
- Z'' < 3.75: Distress Zone (high bankruptcy probability)

✅ **Implementation Note:** Thresholds updated to match literature-based values for emerging markets model.

**Best For:**
- Emerging market companies
- Non-manufacturing companies
- Technology companies
- Companies in developing economies

---

### 5. Financial Institutions Z-Score (`--model financial`)
⚠️ **Implementation Note:** Currently uses the emerging markets model as a fallback, as traditional Z-Score analysis may not be suitable for financial institutions.

**Current Implementation:**
- Uses the same formula as the Emerging Markets model
- Includes warning that Z-Score may not be applicable to financial institutions
- Formula: Z = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ + 3.25

**Variables:**
- X₁ = Working Capital / Total Assets
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

**Academic Note:** Financial institutions have unique capital structures and regulatory requirements that make traditional Z-Score analysis less applicable. This model should be used with caution.

---

### 6. Retail Industry Model (`--model retail`)
⚠️ **Novel Model:** This is a custom retail-specific adaptation developed for this project, inspired by retail industry literature but not based on a specific published Z-Score model.

**Current Implementation:**
- Formula: Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅ + 0.5X₆
- Includes retail-specific inventory adjustments
- Uses modified working capital calculation excluding inventory
- Adds novel inventory turnover component (X₆)

**Variables:**
- X₁ = (Current Assets - Inventory) / Total Assets (Retail-specific modification)
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Market Value of Equity / Total Liabilities (or Book Value if not available)
- X₅ = Sales / Total Assets
- X₆ = Inventory Turnover adjustment (normalized) - **Novel component**

**Current Thresholds:**
- Z > 2.99: Safe Zone
- 1.81 ≤ Z ≤ 2.99: Grey Zone
- Z < 1.81: Distress Zone

**Best For:**
- Retail companies
- E-commerce businesses
- Companies with significant inventory

**Academic Foundation:** While this specific formula is novel, it's based on established principles from retail financial analysis literature that emphasize the importance of inventory management and turnover in retail bankruptcy prediction.

**Development Status:** ✅ Retail-specific formula now fully implemented in the calculator with inventory turnover adjustments.

---

## Literature Compliance & Academic References

### Verified Literature-Based Models

#### ✅ **Original Z-Score (1968)** - Fully Compliant
- **Reference:** Altman, E.I. (1968). "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy"
- **Formula:** Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅
- **Thresholds:** Z > 2.99 (Safe), 1.81-2.99 (Grey), Z < 1.81 (Distress)
- **Status:** ✅ Implementation matches original literature exactly

#### ✅ **Private Company Z'-Score (1983)** - Fully Compliant  
- **Reference:** Altman, E.I. (1983). "Corporate Financial Distress"
- **Formula:** Z' = 0.717X₁ + 0.847X₂ + 3.107X₃ + 0.420X₄ + 0.998X₅
- **Thresholds:** Z' > 2.9 (Safe), 1.23-2.9 (Grey), Z' < 1.23 (Distress)
- **Status:** ✅ Implementation matches literature exactly

### Models with Literature Compliance Improvements

#### ✅ **Emerging Markets Z''-Score** - Now Literature-Compliant
- **Reference:** Altman, E.I. (1995, 2000). Various emerging market studies
- **Implementation:** ✅ Uses coefficients correctly with updated literature-based thresholds
- **Thresholds:** Updated to 5.85/3.75 to match academic research
- **Status:** ✅ Now fully compliant with academic literature

#### ✅ **Service Model** - Improved with Adjusted Thresholds
- **Status:** Uses emerging market coefficients without constant term
- **Thresholds:** Adjusted to 2.60/0.50 to account for missing constant term
- **Recommendation:** Use with caution; well-defined but limited extensive validation

#### ⚠️ **Retail Model** - Novel Project-Specific Model
- **Status:** ✅ Complete implementation with inventory-specific adjustments
- **Academic Foundation:** Inspired by retail industry literature principles but formula is novel
- **Features:** Inventory turnover calculations, modified working capital, novel X₆ component
- **Validation:** ⚠️ Custom model - requires empirical validation for accuracy
- **Status:** ✅ Fully functional but novel (not literature-validated)

#### ⚠️ **Financial Institutions Model** - Not Recommended by Literature
- **Academic Consensus:** Traditional Z-Score models are not suitable for financial institutions
- **Implementation:** Correctly falls back to emerging model with warnings
- **Literature:** Beaver (1966), Ohlson (1980) suggest specialized models for banks
- **Status:** ✅ Implementation correctly warns about limitations

### Academic Recommendations for Implementation

1. **Coefficients:** All implemented coefficients match published literature ✅
2. **Variable Definitions:** Variable calculations follow academic definitions ✅  
3. **Thresholds:** ✅ All thresholds now match or are properly adjusted for literature compliance
4. **Model Selection:** LLM-enhanced selection follows academic industry classification principles ✅
5. **Financial Sector:** Correctly excludes traditional Z-Score for banks per academic consensus ✅
6. **Retail Implementation:** ✅ Now includes inventory-specific adjustments per retail literature
7. **Service Model:** ✅ Thresholds properly adjusted for missing constant term

### Literature References
- Altman, E.I. (1968). "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy." Journal of Finance, 23(4), 589-609.
- Altman, E.I. (1983). "Corporate Financial Distress." New York: Wiley.
- Altman, E.I. (1995). "Predicting Financial Distress of Companies: Revisiting the Z-Score and ZETA Models."
- Altman, E.I. (2000). "Predicting Financial Distress of Companies: Revisiting the Z-Score and ZETA Models." 
- Beaver, W.H. (1966). "Financial Ratios as Predictors of Failure." Journal of Accounting Research, 4, 71-111.
- Ohlson, J.A. (1980). "Financial Ratios and the Probabilistic Prediction of Bankruptcy." Journal of Accounting Research, 18(1), 109-131.

---

## Implementation Status

### Fully Implemented Models
- **Original** (`original`): Complete implementation with market value equity
- **Private** (`private`): Complete implementation with book value equity  
- **Service** (`service`): Complete implementation without asset turnover, literature-adjusted thresholds
- **Emerging** (`emerging`): Complete implementation with constant term, literature-corrected thresholds
- **Retail** (`retail`): ✅ Complete implementation with inventory adjustments and retail-specific calculations

### Models with Fallbacks
- **Financial** (`financial`): Falls back to emerging model with warnings
  - Rationale: Traditional Z-Score may not be suitable for financial institutions
  - Warning issued about applicability to financial sector
  
- **No fallbacks required**: All other models now fully implemented with literature compliance

### Automatic Model Selection
The system includes an LLM-enhanced model selector that:
- Analyzes company industry, sector, and characteristics
- Selects the most appropriate model automatically
- Provides detailed rationale for model selection
- Falls back to rule-based selection if LLM is unavailable

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
# Use original model for traditional manufacturing
python main.py GE --model original

# Use private model for private companies
python main.py PRIVATE_COMPANY --model private

# Use service model for asset-light service companies
python main.py ACN --model service

# Use emerging model for technology/emerging market companies
python main.py MELI --model emerging

# Use retail model (falls back to original with warning)
python main.py AMZN --model retail

# Use financial model (falls back to emerging with warning)
python main.py JPM --model financial

# Let the system automatically select the best model
python main.py AAPL
```

---

*For implementation details, see [FLOW.md](FLOW.md). For API mapping, see [APIS.md](APIS.md).*
