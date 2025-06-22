# Prompts Directory

This directory contains structured prompt templates for AI-enhanced financial analysis using Azure OpenAI.

## Overview

The prompts are used by the LLM client (`altman_zscore.layers.data_fetch.llm_client`) to generate:
- Comprehensive financial analysis reports
- Data reconciliation and validation insights
- Executive summaries and strategic recommendations
- AI-powered investment insights and risk analysis

## Available Prompts

### 1. Financial Analysis (`prompt_fin_analysis.md`)
**Purpose**: Generate comprehensive financial analysis reports using Altman Z-Score framework

**Features**:
- 11-section structured report format
- Tone adaptation based on Z-Score risk level (Distress/Grey/Safe zones)
- Executive summary and strategic recommendations
- Investor recommendations with risk-aware analysis

**Usage**: Used in the report generation layer for creating comprehensive HTML reports

### 2. Financial Reconciliation (`prompt_reconcile_financials.md`)
**Purpose**: Reconcile and validate financial data across different sources

**Features**:
- Data quality validation and cross-reference checking
- Identification of inconsistencies in financial data
- Validation of Z-Score component calculations

**Usage**: Data quality validation and cross-reference checking in the validation layer

## Integration with Main Pipeline

The prompts are integrated into the main pipeline through:

```python
from altman_zscore.prompts import load_prompt, FINANCIAL_ANALYSIS_PROMPT, RECONCILE_FINANCIALS_PROMPT
from altman_zscore.layers.data_fetch.llm_client import LLMClient

# Load and use prompts in the pipeline
prompt_template = load_prompt(FINANCIAL_ANALYSIS_PROMPT)
llm_client = LLMClient()
analysis = await llm_client.generate_analysis(prompt_template, financial_data)
```

## Strategic Notes

- **FMP Pre-calculated Ratios**: The modern pipeline uses FMP standardized financial ratios, eliminating complex field mapping
- **AI Analysis Focus**: Primary use is for generating insights and comprehensive reports in the output generation layer
- **Zero Legacy Dependencies**: Prompts support the new direct calculation architecture
- **Production Ready**: Integrated with complete pipeline for real-world financial analysis

## Architecture Integration

These prompts are integrated into the modern pipeline architecture:
- ✅ Compatible with new `MergedFinancialData` structure
- ✅ Works with direct Z-Score calculation (no field mapping needed)
- ✅ Supports Azure OpenAI integration
- ✅ Ready for advanced AI analysis features
- ✅ Zero legacy dependencies maintained
