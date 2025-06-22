"""
LLM Client with Prompt/Response Logging - Layer 2

Azure OpenAI client that saves prompts and responses to ticker output folders
for troubleshooting purposes. Unlike other APIs, LLM calls are NOT cached
since they can provide different insights each time.

This client handles:
- Azure OpenAI API calls
- Prompt and response logging to ticker folders
- Rate limiting for LLM calls
- Error handling and retries
- Structured prompt templates

Key Features:
- NO caching (intentional for LLM variability)
- Prompt/response logging to {output_dir}/{ticker}/llm_interactions/
- Rate limiting integration
- Structured error handling
"""

import os
import json
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ...common.logging_config import get_logger
from ...common.config import get_config
from ...common.exceptions import DataFetchError
from ...common.utils import ensure_dir_exists

logger = get_logger(__name__)

try:
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available - LLM functionality disabled")


@dataclass
class LLMConfig:
    """LLM API configuration."""
    api_key: str
    endpoint: str
    deployment: str
    api_version: str = "2024-12-01-preview"
    timeout: int = 60
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Create config from environment variables."""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not api_key:
            raise DataFetchError("AZURE_OPENAI_API_KEY environment variable is required")
        if not endpoint:
            raise DataFetchError("AZURE_OPENAI_ENDPOINT environment variable is required")
        if not deployment:
            raise DataFetchError("AZURE_OPENAI_DEPLOYMENT environment variable is required")
        
        return cls(
            api_key=api_key,
            endpoint=endpoint,
            deployment=deployment,
            api_version=api_version
        )


class LLMClient:
    """
    Azure OpenAI client with prompt/response logging.
    
    Does NOT cache LLM responses (intentional for variability).
    Saves all prompts and responses to ticker output folders for troubleshooting.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM client.
        
        Args:
            config: Optional LLM configuration (defaults to environment config)
        """
        if not OPENAI_AVAILABLE:
            raise DataFetchError("OpenAI package not installed - cannot use LLM functionality")
        
        self.config = config or LLMConfig.from_env()
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_version=self.config.api_version,
            azure_endpoint=self.config.endpoint,
            api_key=self.config.api_key,
        )
        
        logger.info(f"Initialized LLM client with endpoint: {self.config.endpoint}")
    
    def _save_interaction(self, ticker: str, prompt: str, response: str, 
                         interaction_type: str = "general") -> str:
        """
        Save LLM prompt and response to ticker output folder.
        
        Args:
            ticker: Stock ticker symbol
            prompt: The prompt sent to LLM
            response: The response from LLM
            interaction_type: Type of interaction (e.g., "field_mapping", "analysis")
            
        Returns:
            Path to saved interaction file
        """
        # Create ticker-specific LLM interaction directory
        config = get_config()
        output_dir = Path(config.output.output_dir)
        llm_dir = output_dir / ticker / "llm_interactions"
        ensure_dir_exists(str(llm_dir))
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{interaction_type}_{timestamp}.json"
        file_path = llm_dir / filename
        
        # Save interaction data
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "interaction_type": interaction_type,
            "prompt": prompt,
            "response": response,
            "model_config": {
                "deployment": self.config.deployment,
                "api_version": self.config.api_version,
                "endpoint": self.config.endpoint
            }
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(interaction_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved LLM interaction to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.warning(f"Failed to save LLM interaction for {ticker}: {e}")
            return ""
    
    def _make_llm_request(self, messages: List[Dict[str, str]], 
                         temperature: float = 0.0, max_tokens: int = 8192) -> str:
        """
        Make rate-limited request to Azure OpenAI API.
        
        Args:
            messages: List of message dictionaries for chat completion
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response text
            
        Raises:
            DataFetchError: If request fails
        """
        # Basic rate limiting for LLM calls - 1 request per second
        time.sleep(1.0)
        
        logger.debug(f"Making Azure OpenAI request with {len(messages)} messages")
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.deployment,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.config.timeout
                )
                
                response_text = response.choices[0].message.content
                
                if not response_text:
                    raise DataFetchError("Empty response from Azure OpenAI")
                
                logger.debug(f"Azure OpenAI request successful: {len(response_text)} characters")
                return response_text
                
            except Exception as e:
                logger.warning(f"Azure OpenAI request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                if attempt == self.config.max_retries - 1:
                    raise DataFetchError(f"Azure OpenAI request failed after {self.config.max_retries} attempts: {e}")
                
                # Exponential backoff
                time.sleep(2 ** attempt)
    
    def chat_completion(self, ticker: str, messages: List[Dict[str, str]], 
                       interaction_type: str = "general",
                       temperature: float = 0.0, max_tokens: int = 8192) -> str:
        """
        Get chat completion from Azure OpenAI with logging.
        
        Args:
            ticker: Stock ticker symbol (for logging)
            messages: List of message dictionaries
            interaction_type: Type of interaction for logging
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response text
        """
        # Extract prompt for logging (combine all user messages)
        prompt_parts = []
        for msg in messages:
            if msg.get("role") == "user":
                prompt_parts.append(msg.get("content", ""))
        prompt = "\n\n".join(prompt_parts)
        
        # Make LLM request (NOT cached - intentional)
        response = self._make_llm_request(messages, temperature, max_tokens)
        
        # Save prompt and response for troubleshooting
        self._save_interaction(ticker, prompt, response, interaction_type)
        
        return response
    
    def analyze_financial_data(self, ticker: str, financial_data: Dict[str, Any], 
                              zscore_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Analyze financial data and Z-Score with LLM insights.
        
        Args:
            ticker: Stock ticker symbol
            financial_data: Financial data dictionary
            zscore_data: Optional Z-Score calculation results
            
        Returns:
            LLM analysis response
        """
        # Build analysis prompt
        messages = [
            {
                "role": "system",
                "content": """You are a financial analyst expert specializing in Altman Z-Score analysis. 
                Provide insightful commentary on the company's financial health based on the provided data."""
            },
            {
                "role": "user", 
                "content": f"""Analyze the financial data for {ticker}:

Financial Data Summary:
{json.dumps(financial_data, indent=2, default=str)}

{"Z-Score Data:" if zscore_data else ""}
{json.dumps(zscore_data, indent=2, default=str) if zscore_data else ""}

Please provide:
1. Overall financial health assessment
2. Key strengths and weaknesses
3. Risk factors and opportunities
4. Z-Score interpretation (if provided)
5. Actionable insights for investors

Keep the analysis concise but comprehensive."""
            }
        ]
        
        return self.chat_completion(
            ticker=ticker,
            messages=messages,
            interaction_type="financial_analysis",
            temperature=0.1  # Slight variability for creative insights
        )
    
    def map_financial_fields(self, ticker: str, raw_fields: List[str], 
                           target_schema: Dict[str, str]) -> Dict[str, str]:
        """
        Use LLM to map raw financial fields to target schema.
        
        Args:
            ticker: Stock ticker symbol
            raw_fields: List of raw field names from API
            target_schema: Target schema with field descriptions
            
        Returns:
            Mapping dictionary from target fields to raw fields
        """
        # Build field mapping prompt
        messages = [
            {
                "role": "system",
                "content": """You are a financial data expert. Map raw financial statement fields 
                to a standardized schema. Respond with a JSON object mapping target fields to raw fields."""
            },
            {
                "role": "user",
                "content": f"""Map these raw financial fields for {ticker}:

Raw Fields Available:
{json.dumps(raw_fields, indent=2)}

Target Schema:
{json.dumps(target_schema, indent=2)}

Return a JSON object mapping each target field to the most appropriate raw field.
Use null for target fields that cannot be mapped.

Example format:
{{
  "total_assets": "totalAssets",
  "total_debt": "totalDebt",
  "net_income": "netIncome"
}}"""
            }
        ]
        
        response = self.chat_completion(
            ticker=ticker,
            messages=messages,
            interaction_type="field_mapping",
            temperature=0.0  # Deterministic for field mapping
        )
        
        # Parse JSON response
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM field mapping response for {ticker}: {e}")
            return {}
    
    def get_interaction_history(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Get saved LLM interaction history for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of interaction dictionaries
        """
        config = get_config()
        output_dir = Path(config.output.output_dir)
        llm_dir = output_dir / ticker / "llm_interactions"
        
        if not llm_dir.exists():
            return []
        
        interactions = []
        for file_path in llm_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    interaction = json.load(f)
                    interactions.append(interaction)
            except Exception as e:
                logger.warning(f"Failed to load interaction file {file_path}: {e}")
        
        # Sort by timestamp
        interactions.sort(key=lambda x: x.get("timestamp", ""))
        return interactions
