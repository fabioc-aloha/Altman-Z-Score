# Altman Z-Score Calculation Audit Report

**Date**: June 24, 2025  
**Auditor**: Technical Review  
**Purpose**: Comprehensive audit of Z-Score calculations against academic literature and best practices

## Executive Summary

Based on a thorough audit of the Altman Z-Score implementation, I found **multiple critical issues** that deviate from established academic literature and best practices. These issues affect calculation accuracy and model implementation.

## Critical Issues Found

### 1. **CRITICAL: Incorrect Service/Emerging Market Model Implementation**

**Issue**: The service model coefficients and thresholds are incorrectly implemented.

**Current Implementation (INCORRECT)**:
```python
# In altman_zscore/layers/zscore_calculation/zscore_calculator.py line 208
coeffs = ZSCORE_MODELS["emerging"]["coefficients"]  # Service companies use emerging market model
```

**Literature Standard (CORRECT)**:
- Service Model: Z'' = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ (NO constant)
- Emerging Market Model: Z = 3.25 + 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄ (WITH constant)

**Impact**: 
- Service companies get incorrect Z-Scores due to the +3.25 constant being incorrectly applied
- This affects risk categorization for non-manufacturing companies

### 2. **CRITICAL: Inconsistent Threshold Application**

**Issue**: The thresholds used don't match the model variants correctly.

**Found Inconsistencies**:

**Service Model Thresholds (Current)**:
```python
# From constants.py - using emerging market thresholds for service
"emerging": {
    "thresholds": {
        "safe": 5.85,
        "grey_lower": 3.75,
        "distress": 3.75
    }
}
```

**Literature Standard**:
- **Service (Non-Manufacturing)**: Safe > 2.6, Grey 1.1-2.6, Distress < 1.1
- **Emerging Markets**: Safe > 2.6, Grey 1.1-2.6, Distress < 1.1

**Wikipedia Reference Confirms**: 
> Z-score bankruptcy model (non-manufacturers):
> Z = 6.56X1 + 3.26X2 + 6.72X3 + 1.05X4
> Zones of discrimination:
> Z > 2.6 – "safe" zone
> 1.1 < Z < 2.6 – "grey" zone  
> Z < 1.1 – "distress" zone

### 3. **MAJOR: EBIT Calculation Assumption**

**Issue**: EBIT is assumed to be `operatingIncome` from FMP, but this may not always be accurate.

**Current Implementation**:
```python
# Line 113 in zscore_calculator.py
ebit = income_statement.get('operatingIncome', 0)
```

**Best Practice**: EBIT should be calculated as:
- `Net Income + Interest Expense + Taxes` OR  
- `Revenue - Operating Expenses` (excluding interest and taxes)
- Should validate that `operatingIncome` = EBIT, not EBITDA

### 4. **MAJOR: Market Value vs Book Value Confusion**

**Issue**: Inconsistent handling of market vs book value for X4 component.

**Found in Service Model** (Line 199-205):
```python
# This calculates Market-to-Book ratio, not Market Value Equity / Total Liabilities
book_value = balance_sheet.get('totalStockholdersEquity', 0)
components['market_to_book_ratio'] = data.market_cap / book_value
```

**Literature Standard**: X4 should be:
- **Public Companies**: Market Value of Equity / Total Liabilities
- **Private Companies**: Book Value of Equity / Total Liabilities  
- **Service Model**: Book Value of Equity / Total Liabilities (per literature)

### 5. **MINOR: Coefficient Precision**

**Issue**: Minor rounding differences in some coefficients.

**Original Model Coefficients**:
- Current: X5 = 1.0 ✓ (Correct)  
- Literature: X5 = 1.0 ✓ (Matches)

**Private Model Coefficients**:  
- Current: All match literature ✓ (Correct)

### 6. **CRITICAL: Retail Model Implementation Issues**

**Issue**: The retail model implementation appears to be a custom variant not based on established literature.

**Current Implementation**:
```python
# From constants.py
"retail": {
    "coefficients": {
        "X1": 1.2, "X2": 1.4, "X3": 3.3, "X4": 0.6, "X5": 1.0,
        "X6": 0.5  # Inventory turnover adjustment
    }
}
```

**Literature Gap**: No established Altman retail model with these exact coefficients exists in academic literature. This appears to be a custom implementation.

## Model-Specific Accuracy Assessment

### ✅ **Original Model (1968)**: CORRECT
- Coefficients: 1.2, 1.4, 3.3, 0.6, 1.0 ✓
- Thresholds: Safe > 2.99, Grey 1.81-2.99, Distress < 1.81 ✓
- Implementation: Accurate per Altman (1968)

### ✅ **Private Model (Z'-Score)**: CORRECT  
- Coefficients: 0.717, 0.847, 3.107, 0.420, 0.998 ✓
- Thresholds: Safe > 2.9, Grey 1.23-2.9, Distress < 1.23 ✓  
- Implementation: Accurate per literature

### ❌ **Service/Emerging Models**: CRITICAL ERRORS
- **Service Model**: Should NOT include +3.25 constant
- **Emerging Model**: Should include +3.25 constant
- **Both**: Wrong thresholds being applied

### ❓ **Financial Model**: NEEDS VERIFICATION
- Uses emerging market coefficients - verify if this matches financial institution literature

### ❌ **Retail Model**: NO ACADEMIC BASIS
- Custom implementation without literature support
- Should either remove or document as proprietary

## Data Quality Concerns

### 1. **Market Cap Scaling Detection**
- **Current**: Has scaling detection logic ✓
- **Issue**: Only checks if ratio > 1000, may miss other scaling issues

### 2. **Missing Data Handling**
- **Current**: Falls back to calculating from raw data ✓  
- **Issue**: No validation that calculated values are reasonable

### 3. **Division by Zero Protection**
- **Current**: Has basic protection ✓
- **Issue**: Uses 0 as fallback, which may skew calculations

## Recommendations

### **Immediate Fixes Required**

1. **Fix Service Model Implementation**:
   ```python
   # Remove the constant from service model calculation
   # Use correct thresholds (2.6, 1.1) not (5.85, 3.75)
   ```

2. **Separate Service and Emerging Market Models**:
   ```python
   # Service: Z = 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄
   # Emerging: Z = 3.25 + 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄  
   ```

3. **Fix X4 Component Calculation**:
   ```python
   # For service model: use book value equity / total liabilities
   # Not market cap / book value
   ```

### **Validation Improvements**

1. **Add EBIT Validation**:
   - Verify EBIT calculation against multiple sources
   - Add warnings if operating income differs significantly from calculated EBIT

2. **Enhanced Data Quality Checks**:
   - Validate reasonableness of calculated ratios
   - Add warnings for extreme values
   - Cross-validate market data with financial statement data

3. **Model Selection Documentation**:
   - Document which model variant is being used and why
   - Add confidence indicators for model selection

### **Literature Compliance**

1. **Remove or Document Custom Models**:
   - Retail model lacks academic basis - either remove or clearly mark as proprietary
   - Financial model needs literature verification

2. **Add Academic References**:
   - Include specific paper citations for each model variant
   - Document any deviations from literature with justification

## Academic References for Verification

1. **Altman, E.I. (1968)**: Original Z-Score - "Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy"
2. **Altman, E.I. (1983)**: Z'-Score for private companies  
3. **Altman, E.I. (2002)**: Z''-Score for non-manufacturing - "Revisiting Credit Scoring Models in a Basel II Environment"
4. **Altman, E.I. (2005)**: Emerging markets adaptation

## Conclusion

While the original and private models are implemented correctly, the service/emerging market models have critical errors that affect calculation accuracy. The retail and financial models need literature verification or should be removed/documented as proprietary implementations.

**Priority**: HIGH - Fix service model implementation immediately as it affects non-manufacturing company analysis.

**Risk**: Current implementation may misclassify non-manufacturing companies' bankruptcy risk due to incorrect constant application and thresholds.
