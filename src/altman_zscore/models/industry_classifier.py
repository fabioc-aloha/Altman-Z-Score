"""
industry_classifier.py
---------------------
Industry classifier for Altman Z-Score pipeline (MVP scaffold).
Currently limited to U.S.-based companies only.

This module provides a function to classify companies by industry and public/private status.
Uses SEC EDGAR and Yahoo Finance for robust classification.

Functions:
    classify_company(ticker): Returns a CompanyProfile for the given ticker using SEC EDGAR first, then Yahoo Finance as fallback.
"""

import logging
import yfinance as yf
from altman_zscore.api.sec_client import SECClient
from altman_zscore.company.sic_lookup import sic_map

logger = logging.getLogger(__name__)

def classify_company(ticker):
    """
    Return a CompanyProfile for the given ticker, using SEC EDGAR first, then Yahoo Finance as fallback.
    Currently limited to U.S.-based companies only.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        CompanyProfile: Object containing company classification info
    """
    try:
        # Try SEC EDGAR first
        sec_client = SECClient()
        cik = sec_client.lookup_cik(ticker)
        if cik:
            company_info = sec_client.get_company_info(cik)
            sic = company_info.get("sic")
            industry = sic_map.get(str(sic), "Unknown") if sic else "Unknown"
            # Also fetch sector from Yahoo Finance for better classification
            try:
                yf_info = yf.Ticker(ticker).info
                sector = yf_info.get("sector", "Unknown")
            except Exception:
                sector = "Unknown"
            return {
                "industry": industry,
                "sector": sector,
                "sic": sic,
                "is_public": True  # If in SEC EDGAR, it's public
            }
            
        # Fallback to Yahoo Finance
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        return {
            "industry": info.get("industry", "Unknown"),
            "sector": info.get("sector", "Unknown"),
            "is_public": True  # If we can get Yahoo Finance info, it's public
        }
            
    except Exception as e:
        logger.error(f"Error classifying company {ticker}: {str(e)}")
        # Return unknown classification with both industry and sector keys for consistency
        return {
            "industry": "Unknown",
            "sector": "Unknown",
            "is_public": True,  # Default to public
            "error": str(e)
        }
