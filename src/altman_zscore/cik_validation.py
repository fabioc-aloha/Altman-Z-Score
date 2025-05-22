"""Module for managing CIK lookup and validation functionality."""
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import logging
import asyncio
from dataclasses import dataclass

from .config import portfolio_config
from .api.sec_client import SECClient

logger = logging.getLogger(__name__)

@dataclass
class CIKValidationResult:
    """Result of CIK validation process."""
    ticker: str
    is_valid: bool
    cik: Optional[str] = None
    error: Optional[str] = None

class CIKValidator:
    """Handles CIK validation and portfolio management."""
    
    def __init__(self, sec_client: Optional[SECClient] = None):
        """Initialize validator with optional SEC client."""
        self.sec_client = sec_client or SECClient()
        
    async def validate_portfolio(self) -> List[CIKValidationResult]:
        """
        Validate CIKs for all active portfolio tickers.
        
        Returns:
            List of validation results for each ticker
        """
        active_tickers = portfolio_config.get_active_portfolio()
        logger.info(f"Starting validation of {len(active_tickers)} tickers...")
        results = []
        
        # Process in batches to respect rate limits
        batch_size = 5
        for i in range(0, len(active_tickers), batch_size):
            batch = active_tickers[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {batch}")
            batch_results = await asyncio.gather(
                *(self.validate_ticker(ticker) for ticker in batch)
            )
            results.extend(batch_results)
            
        self._update_portfolio_status(results)
        return results
        
    async def validate_ticker(self, ticker: str) -> CIKValidationResult:
        """
        Validate CIK for a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Validation result for the ticker
        """
        try:
            logger.info(f"Validating ticker: {ticker}")
            
            # Check if ticker is already excluded
            if ticker in portfolio_config.excluded_tickers:
                excluded = portfolio_config.excluded_tickers[ticker]
                logger.info(f"{ticker} is already excluded: {excluded.reason}")
                return CIKValidationResult(
                    ticker=ticker,
                    is_valid=False,
                    cik=excluded.cik,
                    error=excluded.reason
                )
                
            # First try to lookup CIK
            cik = self.sec_client.lookup_cik(ticker)
            if not cik:
                raise ValueError("CIK lookup failed")
            
            logger.info(f"Found CIK for {ticker}: {cik}")
                
            # Now get company info using CIK
            company_info = self.sec_client.get_company_info(cik)
            if not company_info:
                raise ValueError("Could not fetch company info")
                
            # CIK from company info should match what we found
            info_cik = company_info.get("cik")
            if not info_cik or info_cik != cik:
                raise ValueError("CIK mismatch in company info")
                
            return CIKValidationResult(
                ticker=ticker,
                is_valid=True,
                cik=cik
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"CIK validation failed for {ticker}: {error_msg}")
            
            # Update excluded tickers
            portfolio_config.exclude_ticker(
                ticker=ticker,
                reason=f"CIK lookup failed: {error_msg}"
            )
            
            return CIKValidationResult(
                ticker=ticker,
                is_valid=False,
                error=error_msg
            )
            
    def _update_portfolio_status(self, results: List[CIKValidationResult]):
        """Update portfolio status based on validation results."""
        # Count successful validations
        valid_count = sum(1 for r in results if r.is_valid)
        
        # Update excluded tickers
        for result in results:
            if not result.is_valid and result.error:
                portfolio_config.exclude_ticker(
                    ticker=result.ticker,
                    reason=result.error,
                    cik=result.cik
                )
                
        # Log portfolio health metrics
        health = portfolio_config.get_portfolio_health()
        logger.info(
            f"Portfolio health: {health.active_count}/{health.total_tickers} "
            f"tickers active (CIK success rate: {health.cik_success_rate:.1%})"
        )
        
    def get_cik(self, ticker: str) -> Optional[str]:
        """Get CIK for a ticker, respecting exclusion list."""
        # Check if ticker is excluded
        if ticker in portfolio_config.excluded_tickers:
            return None
            
        try:
            # First try to lookup CIK
            cik = self.sec_client.lookup_cik(ticker)
            if not cik:
                return None
                
            # Verify CIK by getting company info
            company_info = self.sec_client.get_company_info(cik)
            if not company_info:
                return None
                
            # Ensure CIK matches
            info_cik = company_info.get("cik")
            if not info_cik or info_cik != cik:
                return None
                
            return cik
            
        except Exception as e:
            portfolio_config.exclude_ticker(
                ticker=ticker,
                reason=f"CIK lookup failed: {str(e)}"
            )
            return None
