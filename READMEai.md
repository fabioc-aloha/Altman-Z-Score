# AI-Powered Altman Z-Score Analysis

This document provides detailed information about the AI-powered codebase in the `srcai/` folder, which complements the original financial analysis pipeline with advanced AI capabilities.

---
**Project Status (as of June 2025):**
- **AI-powered pipeline is in beta testing.**
- The original pipeline in `src/altman_zscore/` remains the production version.
- The `ai_bootstrap.py` script allows toggling between the traditional and AI-powered pipelines.
---

## Overview

The `srcai/` folder contains an AI-enhanced version of the Altman Z-Score analysis pipeline that leverages Azure OpenAI and other machine learning models to provide:

- **Enhanced financial data extraction** from unstructured reports
- **Intelligent industry classification** beyond standard SIC codes
- **Advanced model selection** based on company characteristics
- **Adaptive Z-Score calibration** for emerging industries
- **Augmented analysis** incorporating qualitative factors and market sentiment

This AI-powered codebase is designed to be fully compatible with the traditional pipeline, allowing for seamless comparison and fallback options. It maintains the same modular and extensible architecture while adding AI-specific components and configuration options.

### Comparison with Traditional Pipeline

| Feature | Traditional (`src/`) | AI-Enhanced (`srcai/`) |
|---------|----------------------|------------------------|
| Data Sources | SEC EDGAR (structured XBRL), Yahoo Finance | Adds extraction from unstructured reports, earnings calls, news |
| Industry Classification | SIC code mapping | ML-based classification with nuanced industry understanding |
| Model Selection | Rule-based | Learns from data patterns and adapts |
| Z-Score Calculation | Fixed formulas by industry | Dynamic calibration based on similar companies |
| Output | Numeric scores, trend charts | Adds explanatory insights, risk factors, forecasts |

## Configuration

The AI-powered pipeline requires additional configuration beyond the traditional pipeline setup.

### Environment Variables (.env)

Add the following variables to your `.env` file to configure the Azure OpenAI integration:

```
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_DEPLOYMENT=your-deployment-name

# Model Configuration
AI_MODEL_TEMPERATURE=0.1
AI_MAX_TOKENS=4000
AI_LOGGING_ENABLED=true
AI_LOG_PATH=./logs/ai_requests
```

### AI Prompts Configuration

The AI pipeline uses prompt templates defined in JSON configuration files:

- **Location**: `srcai/config/prompts/`
- **Format**: Each JSON file contains structured prompts for specific tasks

Example prompt configuration file (`industry_classification.json`):

```json
{
  "system_prompt": "You are a financial industry classification expert. Classify the company into the most appropriate industry category based on its description, products, and services.",
  "task_description": "Analyze the company information and assign the most specific and accurate industry classification.",
  "output_format": {
    "industry": "string",
    "sub_industry": "string",
    "confidence": "float (0-1)",
    "reasoning": "string"
  },
  "examples": [
    {
      "input": { "company_description": "..." },
      "output": { "industry": "...", "sub_industry": "...", "confidence": 0.95, "reasoning": "..." }
    }
  ]
}
```

You can customize these prompt configurations to adjust AI behavior without modifying code.

## AI Bootstrap

The `ai_bootstrap.py` file serves as the entry point for the AI-powered pipeline and provides mechanisms to toggle between the traditional and AI-enhanced pipelines.

### Key Features

- **Pipeline Selection**: Choose between traditional and AI pipelines
- **Fallback Mechanism**: Automatically falls back to the traditional pipeline if AI services are unavailable
- **Parallel Execution**: Run both pipelines in parallel for comparison
- **Configuration Management**: Load and validate AI-specific configurations

### Usage

```python
# Import the bootstrap module
from ai_bootstrap import AltmanAnalysisPipeline, PipelineMode

# Initialize with desired mode
pipeline = AltmanAnalysisPipeline(mode=PipelineMode.AI)

# Or use auto mode which tries AI first, falls back to traditional if needed
pipeline = AltmanAnalysisPipeline(mode=PipelineMode.AUTO)

# Run analysis
results = pipeline.analyze_stock("AAPL")

# Get comparison if in parallel mode
if pipeline.mode == PipelineMode.PARALLEL:
    ai_results = results.ai_results
    traditional_results = results.traditional_results
    comparison = results.comparison_metrics
```

### Command Line Interface

```sh
# Run with AI pipeline
python ai_bootstrap.py --ticker AAPL --mode ai

# Run with traditional pipeline
python ai_bootstrap.py --ticker AAPL --mode traditional

# Run both pipelines and compare results
python ai_bootstrap.py --ticker AAPL --mode parallel

# Auto mode (tries AI, falls back if needed)
python ai_bootstrap.py --ticker AAPL --mode auto
```

## Usage

### Running the AI-Powered Pipeline

1. **Setup Prerequisites**:
   - Complete all setup steps from the main README.md
   - Add Azure OpenAI credentials to your `.env` file
   - Install additional dependencies: `pip install -r requirements_ai.txt`

2. **Basic Analysis**:
   ```sh
   python ai_bootstrap.py --ticker AAPL
   ```

3. **Advanced Options**:
   ```sh
   python ai_bootstrap.py --ticker AAPL --mode parallel --output-dir ./custom_output --include-sentiment
   ```

4. **Python API**:
   ```python
   from ai_bootstrap import AltmanAnalysisPipeline
   
   # Initialize pipeline
   pipeline = AltmanAnalysisPipeline()
   
   # Run analysis
   results = pipeline.analyze_stock(
       ticker="MSFT",
       include_sentiment=True,
       save_intermediates=True
   )
   
   # Access results
   zscore_trend = results.zscore_trend
   sentiment_analysis = results.sentiment_analysis
   industry_classification = results.industry_classification
   
   # Generate reports
   pipeline.generate_reports(results, output_dir="./output")
   ```

### Comparative Testing

To validate AI pipeline results against the traditional pipeline:

```sh
python -m srcai.tools.compare_pipelines --ticker AAPL --quarters 8
```

This will:
1. Run both pipelines on the same data
2. Compare Z-Score results and highlight differences
3. Generate a comparison report with statistical metrics
4. Visualize differences in a side-by-side chart

## Testing

The AI-powered codebase includes a comprehensive testing framework to ensure accuracy and reliability.

### Test Structure

- **Unit Tests**: `tests/srcai/unit/` - Tests for individual AI components
- **Integration Tests**: `tests/srcai/integration/` - Tests for pipeline integration
- **Validation Tests**: `tests/srcai/validation/` - Tests comparing AI vs. traditional results
- **Robustness Tests**: `tests/srcai/robustness/` - Tests for edge cases and error handling

### Running Tests

```sh
# Run all AI pipeline tests
pytest tests/srcai/

# Run specific test categories
pytest tests/srcai/unit/
pytest tests/srcai/integration/
pytest tests/srcai/validation/
pytest tests/srcai/robustness/

# Run tests with specific markers
pytest -m "ai_industry_classification"
pytest -m "ai_sentiment"
```

### Validation Framework

The validation framework (`srcai/validation/`) provides tools to:

1. **Compare Pipeline Results**: Check if AI and traditional pipelines produce consistent results
2. **Measure Accuracy**: Calculate statistical measures of accuracy for AI components
3. **Detect Drift**: Monitor for performance drift over time as data changes
4. **Performance Benchmarks**: Track latency and resource usage for both pipelines

## Contribution

Guidelines for contributing to the AI-powered codebase:

### Development Setup

1. Follow all setup steps from the main repository
2. Install AI-specific dependencies: `pip install -r requirements_ai.txt`
3. Set up Azure OpenAI access for testing (contact repository maintainers for test credentials)

### Adding or Modifying Features

1. **Prompt Engineering**:
   - Update JSON files in `srcai/config/prompts/` to modify AI behavior
   - Document prompt changes and their expected impacts
   - Add examples to improve prompt effectiveness

2. **New AI Components**:
   - Follow the existing modular architecture
   - Create new modules in appropriate subpackages
   - Implement both the AI version and a fallback version

3. **Testing Requirements**:
   - All AI components must have unit tests
   - Include comparison tests against traditional methods
   - Document accuracy metrics and potential limitations

### Code Style and Documentation

- Follow the same style guides as the main repository
- Document AI-specific parameters and behaviors
- Include explanations of AI model choices and limitations
- Provide examples for any new functionality

## Future Enhancements

Planned improvements for the AI-powered pipeline:

1. **Natural Language Insights**:
   - Generate human-readable summaries of Z-Score trends
   - Provide actionable recommendations based on financial health
   - Explain key factors driving Z-Score changes

2. **AI-Enhanced Data Extraction**:
   - Extract additional financial metrics from unstructured reports
   - Intelligently handle inconsistencies in financial reporting
   - Identify and normalize industry-specific metrics

3. **Advanced Risk Assessment**:
   - Incorporate alternative data sources (patents, executive changes, etc.)
   - Detect early warning signs beyond traditional metrics
   - Generate risk factor summaries and projections

4. **Multimodal Analysis**:
   - Process earnings call transcripts and audio
   - Analyze executive sentiment through voice tone analysis
   - Extract visual data from financial reports and presentations

5. **Custom Model Fine-Tuning**:
   - Industry-specific Z-Score calibration
   - Company-specific risk assessment models
   - Customizable risk thresholds based on user risk tolerance

6. **Interactive Explanations**:
   - Visual attribution of Z-Score components
   - What-if scenario modeling for financial metrics
   - Comparative peer analysis with AI-generated insights

---

## License

Same as the main repository (see LICENSE file)