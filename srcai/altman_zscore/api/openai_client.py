"""
Azure OpenAI client wrapper for the Altman Z-Score project.

This module provides a client for interacting with Azure OpenAI services
for parsing financial data from SEC EDGAR and Yahoo Finance APIs.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
import time

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIError(Exception):
    """Base exception for OpenAI API errors."""
    pass

class OpenAIClient:
    """
    Client for interacting with Azure OpenAI.
    """
    
    def __init__(
        self,
        api_type: str = "azure",
        max_retries: int = 3,
        retry_delay: int = 2,
        timeout: int = 30
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            api_type: Type of API to use ('azure' or 'openai')
            max_retries: Maximum number of retries for API calls
            retry_delay: Delay between retries in seconds
            timeout: Timeout for API calls in seconds
        """
        self.api_type = api_type
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # Load configuration based on API type
        self._load_config()
        
    def _load_config(self):
        """Load OpenAI configuration from environment variables."""
        if self.api_type == "azure":
            # Azure OpenAI configuration
            self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
            self.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
            self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
            self.default_model = os.getenv("AZURE_OPENAI_MODEL", "gpt-4")
            
            # Check required environment variables
            if not self.api_key or not self.api_base:
                logger.warning("Azure OpenAI credentials not found, API calls will fail")
                
            # Configure OpenAI client for Azure
            self.client = openai.AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.api_base
            )
                
        else:
            # Standard OpenAI configuration
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.default_model = os.getenv("OPENAI_MODEL", "gpt-4")
            
            # Check required environment variables
            if not self.api_key:
                logger.warning("OpenAI API key not found, API calls will fail")
                
            # Configure standard OpenAI client
            self.client = openai.OpenAI(
                api_key=self.api_key
            )
    
    def extract_json_from_api_payload(
        self,
        payload: Dict[str, Any],
        prompt_template: str,
        model_name: Optional[str] = None,
        temperature: float = 0.1,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract structured JSON data from API response using OpenAI.
        
        Args:
            payload: API response payload to parse
            prompt_template: Template for prompt to OpenAI
            model_name: OpenAI model to use
            temperature: Model temperature (lower for deterministic outputs)
            stream: Whether to stream the response
            
        Returns:
            Extracted JSON data
            
        Raises:
            OpenAIError: If API call fails
        """
        # Select model
        model = model_name or self.default_model
        
        # Format payload for prompt
        payload_str = json.dumps(payload, indent=2)
        
        # Format the prompt with the payload
        prompt = prompt_template.format(payload=payload_str)
        
        # Make API call with retry logic
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a financial data extraction assistant. Extract the requested data from the API payload as valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    stream=stream,
                    timeout=self.timeout
                )
                
                if stream:
                    # Handle streaming response - not implemented in this version
                    pass
                else:
                    # Process complete response
                    result = response.choices[0].message.content
                    
                    # Try to parse JSON from the response
                    try:
                        # Find JSON in the response (in case there's additional text)
                        json_start = result.find('{')
                        json_end = result.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = result[json_start:json_end]
                            parsed_data = json.loads(json_str)
                            return parsed_data
                        else:
                            raise OpenAIError("No JSON found in OpenAI response")
                    except json.JSONDecodeError as e:
                        raise OpenAIError(f"Failed to parse JSON from OpenAI response: {e}")
                        
            except Exception as e:
                logger.warning(f"OpenAI API call failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise OpenAIError(f"Failed to extract data from API payload after {self.max_retries} attempts: {str(e)}")
        
        # This should not be reached due to the exception above
        raise OpenAIError("Failed to extract data from API payload")