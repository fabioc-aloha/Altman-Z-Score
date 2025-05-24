from enum import Enum
from typing import Optional
import requests
import os
import time

class IndustryGroup(Enum):
    TECH = "Technology"
    AI = "Artificial Intelligence"
    MANUFACTURING = "Manufacturing"
    FINANCIAL = "Financial Services"
    SERVICE = "Service"
    OTHER = "Other"

class MarketCategory(Enum):
    DEVELOPED = "Developed Markets"
    EMERGING = "Emerging Markets"

class TechSubsector(Enum):
    SAAS = "Software as a Service"
    AI_ML = "Artificial Intelligence/Machine Learning"
    HARDWARE = "Hardware/Semiconductors"
    CLOUD = "Cloud Infrastructure"
    ECOMMERCE = "E-commerce/Internet"
    CYBERSECURITY = "Cybersecurity"
    FINTECH = "Financial Technology"
    OTHER_TECH = "Other Technology"

class CompanyProfile:
    """
    Company profile for Altman Z-Score model selection.
    """
    def __init__(self, ticker, industry=None, is_public=True, is_emerging_market=False,
                 industry_group=None, market_category=None, tech_subsector=None, country=None, exchange=None):
        self.ticker = ticker.upper()
        self.industry = industry
        self.is_public = is_public
        self.is_emerging_market = is_emerging_market
        self.industry_group = industry_group
        self.market_category = market_category
        self.tech_subsector = tech_subsector
        self.country = country
        self.exchange = exchange

    @staticmethod
    def from_ticker(ticker):
        """
        Classify company by ticker using SEC EDGAR first, then Yahoo Finance as fallback. No static mapping.
        """
        print(f"[DEBUG] No static profile for: {ticker.upper()} (live classification only)")
        # 1. Try SEC EDGAR for US tickers
        try:
            cik = lookup_cik(ticker)
            if cik:
                profile = classify_company_by_sec(cik, ticker)
                if profile and profile.industry_group is not None:
                    return profile
        except Exception as e:
            print(f"[CompanyProfile] SEC EDGAR failed for {ticker}: {e}")
        # 2. Try yfinance as fallback
        try:
            import yfinance as yf
            import json
            import os
            yf_ticker = yf.Ticker(ticker)
            yf_info = yf_ticker.info
            # Save the raw yfinance info payload for traceability
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, f"yf_info_{ticker.upper()}.json"), "w") as f:
                json.dump(yf_info, f, indent=2)
            # Helper to search for the first non-empty value among possible keys
            def find_field(possible_keys):
                for key in possible_keys:
                    val = yf_info.get(key)
                    if val:
                        return val
                return None
            # Dynamically resolve fields
            industry = find_field(["industry", "industryKey", "industryDisp", "sector", "sectorKey", "sectorDisp"])
            country = find_field(["country", "countryKey", "countryDisp"])
            exchange = find_field(["exchange", "fullExchangeName", "exchangeTimezoneName"])
            is_public = True
            emerging_countries = [
                'china', 'india', 'brazil', 'russia', 'south africa',
                'mexico', 'indonesia', 'turkey', 'thailand', 'malaysia',
                'philippines', 'chile', 'colombia', 'poland', 'egypt',
                'hungary', 'qatar', 'uae', 'peru', 'greece', 'czech republic',
                'pakistan', 'saudi arabia', 'south korea', 'taiwan', 'vietnam'
            ]
            country_str = (country or '').lower()
            is_em = country_str in emerging_countries
            print(f"[DEBUG] yfinance info for {ticker}: industry={industry}, country={country}, exchange={exchange}")
            if industry:
                # Map to enums if possible
                ig = None
                ind_lower = str(industry).lower()
                if 'tech' in ind_lower:
                    ig = IndustryGroup.TECH
                elif 'bank' in ind_lower or 'financ' in ind_lower:
                    ig = IndustryGroup.FINANCIAL
                elif 'manufactur' in ind_lower:
                    ig = IndustryGroup.MANUFACTURING
                elif 'service' in ind_lower:
                    ig = IndustryGroup.SERVICE
                elif 'entertain' in ind_lower:
                    ig = IndustryGroup.SERVICE
                else:
                    ig = IndustryGroup.OTHER
                print(f"[DEBUG] yfinance classification for {ticker}: ig={ig}, is_em={is_em}")
                return CompanyProfile(
                    ticker,
                    industry,
                    is_public,
                    is_em,
                    ig,
                    MarketCategory.EMERGING if is_em else MarketCategory.DEVELOPED,
                    country=country,
                    exchange=exchange
                )
            else:
                print(f"[WARN] yfinance returned no industry/sector for {ticker}. Raw info: {yf_info}")
        except Exception as e:
            print(f"[CompanyProfile] yfinance failed for {ticker}: {e}")
        # No static fallback
        print(f"[ERROR] Could not classify company for ticker {ticker} (no industry/sector from yfinance)")
        return None

def lookup_cik(ticker: str) -> Optional[str]:
    """
    Lookup the CIK for a given ticker using local mapping or SEC API.
    """
    try:
        # Try local mapping first
        from altman_zscore.cik_mapping import get_cik_mapping
        mapping = get_cik_mapping([ticker])
        cik = mapping.get(ticker.upper())
        if cik:
            return str(cik)
    except Exception:
        pass
    # Fallback: SEC's public ticker-CIK mapping
    try:
        url = f"https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': os.getenv('SEC_EDGAR_USER_AGENT', 'AltmanZScore/1.0'),
            'From': os.getenv('SEC_API_EMAIL', '')
        }
        if not headers['From']:
            import warnings
            warnings.warn("SEC_API_EMAIL is not set in environment. SEC requests may be rejected.")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for entry in data.values():
            if entry['ticker'].upper() == ticker.upper():
                return str(entry['cik_str']).zfill(10)
    except Exception:
        pass
    return None

def classify_company_by_sec(cik: str, ticker: str) -> CompanyProfile:
    # Minimal stub: in real code, use SEC API and logic from OLD/industry_classifier.py
    return CompanyProfile(ticker, industry_group=IndustryGroup.OTHER, market_category=MarketCategory.DEVELOPED)