# AI-Powered Financial Data Parsing

This document describes the AI-powered parsing pipeline for extracting financial data from SEC EDGAR and Yahoo Finance API responses.

## Overview

The AI-powered parsing pipeline uses Azure OpenAI models to extract structured financial data from API responses, adapting to the variations in payload structure and formats. This approach provides more flexibility and robustness compared to traditional parsing methods.

The system is designed to fall back to traditional parsing methods if AI parsing fails, ensuring reliability and continuity of operations.

## Architecture

The AI-powered parsing pipeline consists of the following components:

1. **OpenAI Client**: A wrapper around the Azure OpenAI API for extracting structured data from API payloads.
2. **Prompt Configuration**: Configuration files for defining prompt templates for different parsing tasks.
3. **AI-Powered API Clients**: API clients for SEC EDGAR and Yahoo Finance that use the OpenAI client for parsing responses.
4. **Bootstrap Utility**: A utility for initializing and managing the AI pipeline.

## Configuration

### Environment Variables

The following environment variables must be set to use the AI-powered parsing pipeline:

```bash
# Azure OpenAI configuration (preferred)
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint
AZURE_OPENAI_API_VERSION=your-azure-openai-api-version  # Default: 2023-05-15
AZURE_OPENAI_MODEL=your-azure-openai-model  # Default: gpt-4

# OR standard OpenAI configuration (fallback)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=your-openai-model  # Default: gpt-4
```

## Usage

### Initializing the AI Pipeline

To initialize the AI pipeline:

```bash
python ai_bootstrap.py --init
```

This will check prerequisites, verify credentials, and set up the necessary configuration.

### Enabling/Disabling the AI Pipeline

To enable or disable the AI pipeline:

```bash
# Enable
python ai_bootstrap.py --enable

# Disable
python ai_bootstrap.py --disable
```

### Checking Status

To check the status of the AI pipeline:

```bash
python ai_bootstrap.py --status
```

### Running Tests

To run tests for the AI pipeline:

```bash
python ai_bootstrap.py --test
```

## Using AI-Powered Parsing in Code

### SEC EDGAR Parsing

```python
from srcai.altman_zscore.api.sec_ai_client import SECAIClient

# Initialize the client
sec_client = SECAIClient()

# Get company info
company_info = sec_client.get_company_info("MSFT")

# Get company facts
company_facts = sec_client.get_company_facts("0000789019")
```

### Yahoo Finance Parsing

```python
from srcai.altman_zscore.api.yahoo_ai_client import YahooFinanceAIClient

# Initialize the client
yahoo_client = YahooFinanceAIClient()

# Get ticker info
ticker_info = yahoo_client.get_ticker_info("AAPL")

# Get market cap on a specific date
from datetime import datetime
market_cap, date = yahoo_client.get_market_cap_on_date("AAPL", datetime.now())
```

## Customizing Prompts

Prompt templates are stored in the `srcai/altman_zscore/config/prompts` directory. You can customize these templates to improve parsing accuracy or extract additional data.

For example, to update the SEC EDGAR parser prompt:

```python
from srcai.altman_zscore.config.prompt_config import PromptConfig

# Initialize the config
prompt_config = PromptConfig()

# Get the current prompt
sec_prompt = prompt_config.get_prompt("sec_edgar_parser")

# Update with a new prompt
prompt_config.add_prompt("sec_edgar_parser", "Your new prompt template here")
```

## Fallback Mechanism

If the AI-powered parsing fails for any reason (e.g., API errors, credential issues), the system will automatically fall back to traditional parsing methods. This ensures that the application continues to function even if AI services are unavailable.

## Performance Considerations

- The AI-powered parsing pipeline adds some latency due to the API calls to OpenAI.
- Consider caching parsed results for frequently accessed data.
- Use the `--disable` option in performance-critical scenarios where speed is more important than adaptability.