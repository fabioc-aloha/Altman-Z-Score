"""
industry_classifier.py
---------------------
Industry classifier for Altman Z-Score pipeline (MVP scaffold).
Currently limited to U.S.-based companies only.

This module provides a function to classify companies by industry and public/private status.
Uses cached CIK lookup for better performance and reliability.

Functions:
    classify_company(ticker): Returns a CompanyProfile for the given ticker using cached CIK data first, then Yahoo Finance as fallback.
"""

import logging
import yfinance as yf
from altman_zscore.company.cik_cache import get_cache
from altman_zscore.api.sec_client import SECClient
from altman_zscore.company.sic_lookup import sic_map

logger = logging.getLogger(__name__)

def classify_company(ticker):
    """
    Return a CompanyProfile for the given ticker, using cached CIK data first, then Yahoo Finance as fallback.
    Currently limited to U.S.-based companies only.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary containing company classification info with keys:
            - industry: Industry description based on SIC code
            - sector: Sector from Yahoo Finance
            - sic: SIC code as string
            - is_public: Boolean indicating if company is public
    """
    try:
        # Try cached CIK lookup first for better performance
        cache = get_cache()
        if cache:
            cik = cache.lookup_cik(ticker)
            if cik:
                logger.debug(f"Found CIK {cik} for {ticker} in cache")
                
                # Use SEC client to get company info with SIC code
                try:
                    sec_client = SECClient()
                    company_info = sec_client.get_company_info(cik)
                    sic = company_info.get("sic")
                    
                    if sic:
                        # Convert SIC to industry description
                        industry = sic_map.get(str(sic), f"SIC: {sic}")
                        
                        # Also fetch sector from Yahoo Finance for better classification
                        try:
                            yf_info = yf.Ticker(ticker).info
                            sector = yf_info.get("sector", "Unknown")
                        except Exception as e:
                            logger.debug(f"Could not fetch sector from Yahoo Finance for {ticker}: {e}")
                            sector = "Unknown"
                        
                        logger.info(f"Found {ticker} with CIK {cik}: SIC={sic}, Industry={industry}")
                        return {
                            "industry": industry,
                            "sector": sector,
                            "sic": str(sic),  # Ensure SIC is returned as string
                            "is_public": True  # If in SEC database, it's public
                        }
                    else:
                        logger.debug(f"No SIC code found for CIK {cik}")
                        
                except Exception as e:
                    logger.debug(f"Failed to get company info for CIK {cik}: {e}")
            else:
                logger.debug(f"No CIK found for ticker {ticker} in cache")
            
        # Fallback to Yahoo Finance
        logger.info(f"Falling back to Yahoo Finance for {ticker}")
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        return {
            "industry": info.get("industry", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "sic": None,  # No SIC available from Yahoo Finance
            "is_public": True  # If we can get Yahoo Finance info, it's public
        }
            
    except Exception as e:
        logger.error(f"Error classifying company {ticker}: {str(e)}")
        # Return unknown classification with both industry and sector keys for consistency
        return {
            "industry": "Unknown",
            "sector": "Unknown",
            "sic": None,
            "is_public": True,  # Default to public
            "error": str(e)
        }
