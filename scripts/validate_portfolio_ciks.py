"""
Script to validate CIKs for all portfolio tickers.

This script verifies the correctness of all CIK (Central Index Key) identifiers
in the portfolio configuration against the SEC EDGAR database, reporting any
discrepancies or missing identifiers.

Note: This code follows PEP 8 style guidelines.
"""
import asyncio
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from altman_zscore.cik_validation import CIKValidator
from altman_zscore.config import portfolio_config
from altman_zscore.api.sec_client import SECClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Validate CIKs for all portfolio tickers."""
    logger.info("Starting CIK validation for portfolio...")
    
    # Initialize validator
    validator = CIKValidator(SECClient())
    
    # Run validation
    results = await validator.validate_portfolio()
    
    # Print results
    logger.info("\nValidation Results:")
    logger.info("-" * 60)
    
    for result in results:
        status = "✓" if result.is_valid else "✗"
        if result.is_valid:
            logger.info(f"{status} {result.ticker:6} : CIK {result.cik}")
        else:
            logger.info(f"{status} {result.ticker:6} : {result.error}")
    
    # Print portfolio health
    health = portfolio_config.get_portfolio_health()
    logger.info("\nPortfolio Health:")
    logger.info("-" * 60)
    logger.info(f"Total Tickers: {health.total_tickers}")
    logger.info(f"Active Tickers: {health.active_count}")
    logger.info(f"Excluded Tickers: {health.excluded_count}")
    logger.info(f"CIK Success Rate: {health.cik_success_rate:.1%}")
    logger.info(f"Data Quality Score: {health.data_quality_score:.1%}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
