"""
AI-powered SEC EDGAR API client module for parsing SEC EDGAR responses.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
import os
import logging
import json

from .openai_client import OpenAIClient, OpenAIError
from ..config.prompt_config import PromptConfig

# Import original SEC client for API access
from src.altman_zscore.api.sec_client import SECClient, SECError, SECRateError, SECResponseError

logger = logging.getLogger(__name__)

class SECAIParsingError(Exception):
    """Exception for SEC AI parsing errors."""
    pass

class SECAIClient:
    """
    AI-powered client for parsing SEC EDGAR API responses.
    """
    
    def __init__(
        self, 
        openai_client: Optional[OpenAIClient] = None,
        prompt_config: Optional[PromptConfig] = None,
        sec_client: Optional[SECClient] = None,
        email: Optional[str] = None
    ):
        """
        Initialize AI-powered SEC client.
        
        Args:
            openai_client: Existing OpenAI client instance
            prompt_config: Existing prompt configuration instance
            sec_client: Existing SEC client instance for API calls
            email: Email for SEC API authentication (if sec_client not provided)
        """
        # Initialize OpenAI client if not provided
        self.openai_client = openai_client or OpenAIClient()
        
        # Initialize prompt config if not provided
        self.prompt_config = prompt_config or PromptConfig()
        
        # Initialize SEC client for API calls if not provided
        self.sec_client = sec_client or SECClient(email=email)
        
    def lookup_cik(self, ticker: str) -> Optional[str]:
        """
        Look up CIK number for a ticker symbol.
        
        Delegates to the standard SEC client.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            10-digit CIK if found, None otherwise
        """
        return self.sec_client.lookup_cik(ticker)
        
    def get_company_info(self, ticker_or_cik: str) -> Optional[Dict[str, Any]]:
        """
        Get company info from SEC EDGAR using AI-powered parsing.
        
        Args:
            ticker_or_cik: Stock ticker symbol or CIK number
            
        Returns:
            Parsed company info if found, None otherwise
            
        Raises:
            SECAIParsingError: If AI parsing fails
        """
        try:
            # Get raw company info from SEC API
            raw_company_info = self.sec_client.get_company_info(ticker_or_cik)
            
            if not raw_company_info:
                logger.warning(f"No company info found for {ticker_or_cik}")
                return None
                
            # Parse company info using AI
            try:
                # Get the prompt template
                prompt_template = self.prompt_config.get_prompt("sec_edgar_parser")
                
                # Extract structured data using OpenAI
                parsed_data = self.openai_client.extract_json_from_api_payload(
                    raw_company_info,
                    prompt_template
                )
                
                # Add additional metadata
                parsed_data["_metadata"] = {
                    "parsed_with": "ai",
                    "timestamp": datetime.now().isoformat()
                }
                
                return parsed_data
                
            except (OpenAIError, FileNotFoundError) as e:
                logger.warning(f"AI parsing failed for {ticker_or_cik}, falling back to standard parsing: {str(e)}")
                # In case of AI parsing failure, return the original data
                return raw_company_info
                
        except SECError as e:
            logger.error(f"Error getting company info for {ticker_or_cik}: {str(e)}")
            return None
            
    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Get company facts from SEC XBRL API with AI-powered parsing.
        
        Args:
            cik: Company CIK number (will be zero-padded)
            
        Returns:
            Parsed company facts
            
        Raises:
            SECAIParsingError: If AI parsing fails
        """
        try:
            # Get raw company facts from SEC API
            raw_facts = self.sec_client.get_company_facts(cik)
            
            # Parse facts using AI
            try:
                # Get the prompt template
                prompt_template = self.prompt_config.get_prompt("sec_edgar_parser")
                
                # Extract structured data using OpenAI
                parsed_data = self.openai_client.extract_json_from_api_payload(
                    raw_facts,
                    prompt_template
                )
                
                # Add additional metadata
                parsed_data["_metadata"] = {
                    "parsed_with": "ai",
                    "timestamp": datetime.now().isoformat()
                }
                
                return parsed_data
                
            except (OpenAIError, FileNotFoundError) as e:
                logger.warning(f"AI parsing failed for company facts {cik}, falling back to standard parsing: {str(e)}")
                # In case of AI parsing failure, return the original data
                return raw_facts
                
        except SECError as e:
            logger.error(f"Error getting company facts for {cik}: {str(e)}")
            raise SECAIParsingError(f"Failed to get company facts: {str(e)}")
            
    def get_company_concept(self, cik: str, concept: str) -> Dict[str, Any]:
        """
        Get specific company concept data with AI-powered parsing.
        
        Args:
            cik: Company CIK number (will be zero-padded)
            concept: The US GAAP concept to fetch
            
        Returns:
            Parsed concept data
            
        Raises:
            SECAIParsingError: If AI parsing fails
        """
        try:
            # Get raw concept data from SEC API
            raw_concept = self.sec_client.get_company_concept(cik, concept)
            
            # Parse concept using AI
            try:
                # Get the prompt template
                prompt_template = self.prompt_config.get_prompt("sec_edgar_parser")
                
                # Extract structured data using OpenAI
                parsed_data = self.openai_client.extract_json_from_api_payload(
                    raw_concept,
                    prompt_template
                )
                
                # Add additional metadata
                parsed_data["_metadata"] = {
                    "parsed_with": "ai",
                    "timestamp": datetime.now().isoformat()
                }
                
                return parsed_data
                
            except (OpenAIError, FileNotFoundError) as e:
                logger.warning(f"AI parsing failed for concept {concept}, falling back to standard parsing: {str(e)}")
                # In case of AI parsing failure, return the original data
                return raw_concept
                
        except SECError as e:
            logger.error(f"Error getting company concept {concept} for {cik}: {str(e)}")
            raise SECAIParsingError(f"Failed to get company concept: {str(e)}")
            
    def get_sic_data(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        Get company SIC code and industry classification with AI-powered parsing.
        
        Args:
            cik: Company CIK number
            
        Returns:
            Parsed SIC code and industry information
            
        Raises:
            SECAIParsingError: If AI parsing fails
        """
        try:
            # Delegate to the standard SEC client for SIC data
            sic_data = self.sec_client.get_sic_data(cik)
            
            if not sic_data:
                logger.warning(f"No SIC data found for CIK {cik}")
                return None
                
            return sic_data
            
        except SECError as e:
            logger.error(f"Error getting SIC data for {cik}: {str(e)}")
            return None