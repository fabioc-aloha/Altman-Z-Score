"""
AI-powered Yahoo Finance client for Altman Z-Score pipeline.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, Union
from decimal import Decimal

import yfinance as yf

from .openai_client import OpenAIClient, OpenAIError
from ..config.prompt_config import PromptConfig

logger = logging.getLogger(__name__)

class YahooAIParsingError(Exception):
    """Exception for Yahoo Finance AI parsing errors."""
    pass

class YahooFinanceAIClient:
    """
    AI-powered client for parsing Yahoo Finance API responses.
    """
    
    def __init__(
        self,
        openai_client: Optional[OpenAIClient] = None,
        prompt_config: Optional[PromptConfig] = None
    ):
        """
        Initialize AI-powered Yahoo Finance client.
        
        Args:
            openai_client: Existing OpenAI client instance
            prompt_config: Existing prompt configuration instance
        """
        # Initialize OpenAI client if not provided
        self.openai_client = openai_client or OpenAIClient()
        
        # Initialize prompt config if not provided
        self.prompt_config = prompt_config or PromptConfig()
        
    def get_ticker_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get basic information about a ticker using AI-powered parsing.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Dictionary of ticker information
            
        Raises:
            YahooAIParsingError: If AI parsing fails
        """
        try:
            # Get data from Yahoo Finance
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            # Parse data using AI
            try:
                # Get the prompt template
                prompt_template = self.prompt_config.get_prompt("yahoo_finance_parser")
                
                # Extract structured data using OpenAI
                parsed_data = self.openai_client.extract_json_from_api_payload(
                    info,
                    prompt_template
                )
                
                # Add additional metadata
                parsed_data["_metadata"] = {
                    "parsed_with": "ai",
                    "timestamp": datetime.now().isoformat()
                }
                
                return parsed_data
                
            except (OpenAIError, FileNotFoundError) as e:
                logger.warning(f"AI parsing failed for ticker {ticker}, falling back to standard parsing: {str(e)}")
                # In case of AI parsing failure, return the original data
                return info
                
        except Exception as e:
            logger.error(f"Error getting ticker info for {ticker}: {str(e)}")
            raise YahooAIParsingError(f"Failed to get ticker info: {str(e)}")

    def get_market_cap_on_date(self, ticker: str, date, span_days: int = 30) -> Tuple[Optional[float], Optional[datetime.date]]:
        """
        Fetch market cap for a ticker on a given date using AI-powered parsing.
        Tries a window of +/- span_days around the date for available price data.
        
        Args:
            ticker: Stock symbol
            date: Date to fetch market cap for
            span_days: Number of days to search around the date
            
        Returns:
            Tuple of (market_cap, actual_date) or (None, None) if unavailable
        """
        try:
            # Get data from Yahoo Finance
            ticker_obj = yf.Ticker(ticker)
            
            # Try a window of +/- span_days
            start = date - timedelta(days=span_days)
            end = date + timedelta(days=span_days)
            hist = ticker_obj.history(period="1d", start=start, end=end)
            
            if not hist.empty:
                # Find the row closest to the requested date, but prefer the most recent previous trading day if possible
                hist = hist.sort_index()
                # Only consider dates <= requested date, if available
                prior_dates = [d for d in hist.index if d.date() <= date]
                if prior_dates:
                    closest_idx = max(prior_dates)
                else:
                    # If no prior dates, use the closest available
                    closest_idx = min(hist.index, key=lambda d: abs(d.date() - date))
                    
                # Get shares outstanding and close price
                shares = ticker_obj.info.get("sharesOutstanding")
                close = hist.loc[closest_idx]["Close"]
                
                if shares and close:
                    actual_date = closest_idx.date()
                    return float(shares) * float(close), actual_date
                    
            # Try to get latest market cap
            mcap = ticker_obj.info.get("marketCap")
            if mcap:
                return float(mcap), None
                
            return None, None
            
        except Exception as e:
            logger.error(f"Error getting market cap for {ticker} on {date}: {str(e)}")
            return None, None
            
    def get_historical_data(self, ticker: str, start_date, end_date) -> Dict[str, Any]:
        """
        Get historical price data for a ticker with AI-powered parsing.
        
        Args:
            ticker: Stock symbol
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            Dictionary of historical data
            
        Raises:
            YahooAIParsingError: If AI parsing fails
        """
        try:
            # Get data from Yahoo Finance
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="1d", start=start_date, end=end_date)
            
            # Convert DataFrame to dictionary
            hist_dict = hist.reset_index().to_dict(orient="records")
            
            # Format data for AI parsing
            data_for_ai = {
                "ticker": ticker,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "historical_data": hist_dict
            }
            
            # Parse data using AI
            try:
                # Get the prompt template
                prompt_template = self.prompt_config.get_prompt("yahoo_finance_parser")
                
                # Extract structured data using OpenAI
                parsed_data = self.openai_client.extract_json_from_api_payload(
                    data_for_ai,
                    prompt_template
                )
                
                # Add additional metadata
                parsed_data["_metadata"] = {
                    "parsed_with": "ai",
                    "timestamp": datetime.now().isoformat()
                }
                
                return parsed_data
                
            except (OpenAIError, FileNotFoundError) as e:
                logger.warning(f"AI parsing failed for historical data {ticker}, falling back to standard format: {str(e)}")
                # In case of AI parsing failure, return the original data
                return data_for_ai
                
        except Exception as e:
            logger.error(f"Error getting historical data for {ticker}: {str(e)}")
            raise YahooAIParsingError(f"Failed to get historical data: {str(e)}")
            
    def get_financials(self, ticker: str) -> Dict[str, Any]:
        """
        Get financial statements for a ticker with AI-powered parsing.
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Dictionary of financial statement data
            
        Raises:
            YahooAIParsingError: If AI parsing fails
        """
        try:
            # Get data from Yahoo Finance
            ticker_obj = yf.Ticker(ticker)
            
            # Get financial statements
            income_stmt = ticker_obj.income_stmt.to_dict()
            balance_sheet = ticker_obj.balance_sheet.to_dict()
            cashflow = ticker_obj.cashflow.to_dict()
            
            # Format data for AI parsing
            data_for_ai = {
                "ticker": ticker,
                "income_statement": income_stmt,
                "balance_sheet": balance_sheet,
                "cash_flow": cashflow
            }
            
            # Parse data using AI
            try:
                # Get the prompt template
                prompt_template = self.prompt_config.get_prompt("yahoo_finance_parser")
                
                # Extract structured data using OpenAI
                parsed_data = self.openai_client.extract_json_from_api_payload(
                    data_for_ai,
                    prompt_template
                )
                
                # Add additional metadata
                parsed_data["_metadata"] = {
                    "parsed_with": "ai",
                    "timestamp": datetime.now().isoformat()
                }
                
                return parsed_data
                
            except (OpenAIError, FileNotFoundError) as e:
                logger.warning(f"AI parsing failed for financials {ticker}, falling back to standard format: {str(e)}")
                # In case of AI parsing failure, return the original data
                return data_for_ai
                
        except Exception as e:
            logger.error(f"Error getting financials for {ticker}: {str(e)}")
            raise YahooAIParsingError(f"Failed to get financials: {str(e)}")