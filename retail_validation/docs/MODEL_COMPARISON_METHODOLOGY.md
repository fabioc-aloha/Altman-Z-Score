# Model Comparison Methodology
**Version 1.0 | July 2025**

## Overview

This document outlines the methodology used to compare the novel retail Z-Score model against traditional Z-Score models. The comparison framework is designed to provide rigorous, statistically sound evaluation of model performance across multiple dimensions.

## Models Under Comparison

### 1. Novel Retail Z-Score Model

The retail-specific Z-Score model incorporates inventory turnover (X₆) and modified working capital calculation (X₁):

```
Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅ + 0.5X₆
```

Where:
- X₁ = Working Capital / Total Assets (with retail-specific adjustments)
- X₂ = Retained Earnings / Total Assets
- X₃ = EBIT / Total Assets
- X₄ = Market Value of Equity / Book Value of Total Liabilities
- X₅ = Sales / Total Assets
- X₆ = Inventory Turnover Adjustment

**Key Innovation**: Addition of inventory turnover component (X₆) and retail-specific working capital adjustments in (X₁)

### 2. Original Altman Z-Score (1968)

The original Altman Z-Score model for manufacturing companies:

```
Z = 1.2X₁ + 1.4X₂ + 3.3X₃ + 0.6X₄ + 1.0X₅
```

**Risk Classification**:
- Z > 2.99: "Safe" Zone
- 1.81 ≤ Z ≤ 2.99: "Gray" Zone
- Z < 1.81: "Distress" Zone

### 3. Altman Z"-Score (Private Company Model)

The Altman Z"-Score for private companies (used as an additional reference):

```
Z" = 3.25 + 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄
```

**Risk Classification**:
- Z" > 5.85: "Safe" Zone
- 4.15 ≤ Z" ≤ 5.85: "Gray" Zone
- Z" < 4.15: "Distress" Zone

## Comparison Dimensions

The comparison methodology evaluates models across six key dimensions:

### 1. Bankruptcy Prediction Accuracy

**Metrics:**
- **True Positives**: Correctly identified bankruptcies
- **False Negatives**: Missed bankruptcies
- **Accuracy Rate**: Percentage of correctly identified bankruptcies
- **Improvement Rate**: Retail model vs. traditional model accuracy

**Analysis Approach:**
```python
for ticker, data in results.items():
    if data.get('category') == 'failed' and not data.get('error'):
        analysis['total_bankruptcies'] += 1
        
        retail_predicted = data.get('retail_risk') in ['Distress', 'Gray Zone']
        traditional_predicted = data.get('traditional_risk') in ['Distress', 'Gray Zone']
        
        if retail_predicted:
            analysis['retail_correct'] += 1
        if traditional_predicted:
            analysis['traditional_correct'] += 1
```

### 2. Early Warning Capability

**Metrics:**
- **Warning Lead Time**: Years before bankruptcy with distress signals
- **Signal Strength**: Z-Score deterioration rate
- **Signal Consistency**: Stability of warning signals

**Analysis Approach:**
- Calculate Z-Scores for each quarter leading up to bankruptcy
- Measure first appearance of distress signals
- Compare warning lead time between models

### 3. False Positive Rate

**Metrics:**
- **False Positives**: Healthy companies incorrectly classified as distressed
- **False Positive Rate**: Percentage of false alarms
- **Stability**: Consistency of correct classifications

**Analysis Approach:**
```python
for ticker, data in results.items():
    if data.get('category') == 'stable' and not data.get('error'):
        analysis['total_stable'] += 1
        
        retail_false_positive = data.get('retail_risk') in ['Distress', 'Gray Zone']
        traditional_false_positive = data.get('traditional_risk') in ['Distress', 'Gray Zone']
        
        if retail_false_positive:
            analysis['retail_false_positives'] += 1
        if traditional_false_positive:
            analysis['traditional_false_positives'] += 1
```

### 4. Inventory Component Impact

**Metrics:**
- **Component Contribution**: X₆ contribution to overall Z-Score
- **Correlation**: Inventory efficiency vs. financial distress
- **Discrimination Power**: Ability to distinguish healthy vs. distressed

**Analysis Approach:**
```python
for ticker, data in results.items():
    if not data.get('error') and data.get('components'):
        components = data['components']
        
        if 'X6' in components:
            inventory_turnover = components.get('X6', 0)
            
            # Calculate contribution to Z-Score
            contribution = 0.5 * inventory_turnover  # X₆ coefficient * value
            
            # Calculate percentage of total score
            if data.get('retail_score'):
                contribution_percentage = (contribution / data['retail_score']) * 100
```

### 5. Working Capital Modification Impact

**Metrics:**
- **Adjustment Effect**: Impact of retail-specific working capital calculation
- **Classification Changes**: Cases where adjustment changed risk category
- **Sectoral Variation**: Effect across retail subsectors

**Analysis Approach:**
- Compare retail X₁ component vs. traditional X₁ component
- Measure impact on overall Z-Score
- Identify cases where adjustment affected classification

### 6. Seasonal Stability

**Metrics:**
- **Quarterly Variation**: Z-Score volatility across quarters
- **Seasonal Bias**: Systematic seasonal patterns in scores
- **Classification Consistency**: Stability of risk classifications across seasons

**Analysis Approach:**
```python
for ticker, data in seasonal_results.items():
    quarterly_scores = data.get('quarterly_scores', {})
    
    if len(quarterly_scores) >= 4:  # Full year of quarters
        retail_scores = [q.get('retail_score') for q in quarterly_scores.values() if q.get('retail_score')]
        traditional_scores = [q.get('traditional_score') for q in quarterly_scores.values() if q.get('traditional_score')]
        
        # Calculate quarterly volatility
        retail_volatility = np.std(retail_scores) if retail_scores else 0
        traditional_volatility = np.std(traditional_scores) if traditional_scores else 0
        
        volatility_reduction = traditional_volatility - retail_volatility
```

## Statistical Validation Methodology

### 1. Paired Sample Testing

Compare model performance on identical data points:

```python
from scipy import stats

# Paired t-test for systematic difference
t_stat, p_value = stats.ttest_rel(retail_scores, traditional_scores)
```

### 2. Classification Accuracy Metrics

Evaluate classification performance:

```python
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    roc_auc_score
)

# Calculate metrics
accuracy = accuracy_score(actual_bankruptcies, predicted_bankruptcies)
precision = precision_score(actual_bankruptcies, predicted_bankruptcies)
recall = recall_score(actual_bankruptcies, predicted_bankruptcies)
f1 = f1_score(actual_bankruptcies, predicted_bankruptcies)
```

### 3. ROC Curve Analysis

Compare discrimination capabilities:

```python
from sklearn.metrics import roc_curve

# Generate ROC curves
retail_fpr, retail_tpr, _ = roc_curve(actual_bankruptcies, retail_scores)
traditional_fpr, traditional_tpr, _ = roc_curve(actual_bankruptcies, traditional_scores)

# Calculate AUC (Area Under Curve)
retail_auc = roc_auc_score(actual_bankruptcies, retail_scores)
traditional_auc = roc_auc_score(actual_bankruptcies, traditional_scores)
```

## Comparative Visualization

### 1. Z-Score Distribution Comparison

```python
plt.figure(figsize=(10, 6))
sns.histplot(retail_scores, kde=True, label='Retail Model', color='blue', alpha=0.6)
sns.histplot(traditional_scores, kde=True, label='Traditional Model', color='red', alpha=0.6)
plt.axvline(2.99, color='green', linestyle='--', label='Safe Threshold (2.99)')
plt.axvline(1.81, color='red', linestyle='--', label='Distress Threshold (1.81)')
plt.title('Z-Score Distribution Comparison')
plt.xlabel('Z-Score Value')
plt.ylabel('Frequency')
plt.legend()
```

### 2. Model Accuracy Comparison

```python
categories = ['Bankruptcy Prediction', 'False Positive Rate', 'Early Warning']
retail_metrics = [bankruptcy_accuracy, false_positive_rate, early_warning_rate]
traditional_metrics = [trad_bankruptcy_accuracy, trad_false_positive_rate, trad_early_warning_rate]

plt.figure(figsize=(10, 6))
x = np.arange(len(categories))
width = 0.35

plt.bar(x - width/2, retail_metrics, width, label='Retail Model')
plt.bar(x + width/2, traditional_metrics, width, label='Traditional Model')

plt.ylabel('Accuracy (%)')
plt.title('Model Performance Comparison')
plt.xticks(x, categories)
plt.legend()
```

### 3. ROC Curve Comparison

```python
plt.figure(figsize=(8, 8))
plt.plot(retail_fpr, retail_tpr, lw=2, label=f'Retail Model (AUC = {retail_auc:.2f})')
plt.plot(traditional_fpr, traditional_tpr, lw=2, label=f'Traditional Model (AUC = {traditional_auc:.2f})')
plt.plot([0, 1], [0, 1], 'k--', lw=2)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve Comparison')
plt.legend(loc="lower right")
```

## Implementation in the Validation Framework

The model comparison functionality is implemented in the `RetailModelValidator` class through:

1. **Dual Model Calculation**: 
   - Calculate both retail and traditional Z-Scores for each company
   - Store results in parallel for comparison

2. **Comparative Analysis Methods**:
   - `analyze_bankruptcy_prediction`: Accuracy comparison
   - `analyze_category_performance`: Category-specific comparison
   - `analyze_inventory_impact`: Inventory component effect

3. **Detailed Reporting**:
   - Side-by-side metrics in validation report
   - Improvement percentages and statistical significance
   - Visualizations of key comparative metrics

## Academic Validation Standards

The comparison methodology adheres to academic standards for bankruptcy prediction model validation:

1. **Out-of-Sample Testing**: Using companies not in the model development dataset
2. **Cross-Sectional Validation**: Testing across different retail sectors
3. **Temporal Validation**: Testing across multiple time periods
4. **Statistical Significance**: Formal hypothesis testing of improvements
5. **Effect Size Quantification**: Measuring practical significance of improvements

---

*This methodology provides a rigorous framework for quantifying the performance differences between the novel retail Z-Score model and traditional Z-Score models.*
