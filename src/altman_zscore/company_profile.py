import os
import requests
import time
from enum import Enum
from typing import Optional
from altman_zscore.utils.paths import get_output_dir

"""
Company profile classification and lookup utilities for Altman Z-Score model selection.

This module provides logic to classify companies by ticker using SEC EDGAR and Yahoo Finance,
with robust fallback for delisted/edge-case tickers. Used for model selection and reporting.
"""

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

    Attributes:
        ticker (str): Stock ticker symbol (uppercase)
        industry (str): Industry string or SIC code
        is_public (bool): Whether the company is public
        is_emerging_market (bool): Whether the company is in an emerging market
        industry_group (IndustryGroup): Enum for industry group
        market_category (MarketCategory): Enum for market category
        tech_subsector (TechSubsector): Enum for tech subsector (if applicable)
        country (str): Country of headquarters
        exchange (str): Exchange name
        founding_year (Optional[int]): Year the company was founded
        ipo_date (Optional[str]): IPO date (YYYY-MM-DD) if available
        maturity (str): Company maturity (e.g., 'early-stage', 'growth', 'mature')
    """
    def __init__(self, ticker, industry=None, is_public=True, is_emerging_market=False,
                 industry_group=None, market_category=None, tech_subsector=None, country=None, exchange=None,
                 founding_year=None, ipo_date=None, maturity=None):
        self.ticker = ticker.upper()
        self.industry = industry
        self.is_public = is_public
        self.is_emerging_market = is_emerging_market
        self.industry_group = industry_group
        self.market_category = market_category
        self.tech_subsector = tech_subsector
        self.country = country
        self.exchange = exchange
        self.founding_year = founding_year
        self.ipo_date = ipo_date
        self.maturity = maturity  # Add maturity to profile

    @staticmethod
    def classify_maturity(founding_year, ipo_date, current_year=None):
        """
        Classify company as 'early-stage', 'growth', or 'mature' using founding year and IPO date.
        """
        import datetime
        if not current_year:
            current_year = datetime.datetime.now().year
        if ipo_date:
            try:
                ipo_year = int(str(ipo_date)[:4])
                years_since_ipo = current_year - ipo_year
                if years_since_ipo < 3:
                    return 'early-stage'
                elif years_since_ipo < 7:
                    return 'growth'
                else:
                    return 'mature'
            except Exception:
                pass
        if founding_year:
            try:
                years_since_founding = current_year - int(founding_year)
                if years_since_founding < 3:
                    return 'early-stage'
                elif years_since_founding < 7:
                    return 'growth'
                else:
                    return 'mature'
            except Exception:
                pass
        return 'mature'  # Default fallback

    @staticmethod
    def from_ticker(ticker):
        """
        Classify company by ticker using SEC EDGAR first, then Yahoo Finance as fallback. No static mapping.
        Robustly supports delisted/edge-case tickers by extracting company profile from most recent SEC filing if needed.

        Args:
            ticker (str): Stock ticker symbol
        Returns:
            CompanyProfile or None: Populated profile if found, else None
        """
        # print(f"[DEBUG] No static profile for: {ticker.upper()} (live classification only)")
        industry = None  # Always define upfront to avoid unbound errors
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
            yf_ticker = yf.Ticker(ticker)
            yf_info = yf_ticker.info            # Save the raw yfinance info payload for traceability
            output_path = get_output_dir("yf_info.json", ticker=ticker)
            with open(output_path, "w") as f:
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
            founding_year = find_field(["founded", "startYear", "foundingYear"])
            ipo_date = find_field(["ipoDate", "ipoYear", "ipo"])
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
            maturity = CompanyProfile.classify_maturity(founding_year, ipo_date)
            # print(f"[DEBUG] yfinance info for {ticker}: industry={industry}, country={country}, exchange={exchange}")
            if industry:
                # Map to enums if possible
                ig = None
                ind_lower = str(industry).lower()
                if 'tech' in ind_lower:
                    ig = IndustryGroup.TECH
                elif 'bank' in ind_lower or 'financ' in ind_lower:
                    ig = IndustryGroup.FINANCIAL
                elif (
                    'manufactur' in ind_lower or
                    'consumer electronics' in ind_lower or
                    'hardware' in ind_lower or
                    'semiconductor' in ind_lower
                ):
                    ig = IndustryGroup.MANUFACTURING
                elif 'service' in ind_lower:
                    ig = IndustryGroup.SERVICE
                elif 'entertain' in ind_lower:
                    ig = IndustryGroup.SERVICE
                else:
                    ig = IndustryGroup.OTHER
                # print(f"[DEBUG] yfinance classification for {ticker}: ig={ig}, is_em={is_em}")
                return CompanyProfile(
                    ticker,
                    industry,
                    is_public,
                    is_em,
                    ig,
                    MarketCategory.EMERGING if is_em else MarketCategory.DEVELOPED,
                    country=country,
                    exchange=exchange,
                    founding_year=founding_year,
                    ipo_date=ipo_date,
                    maturity=maturity
                )
            else:
                print(f"[WARN] yfinance returned no industry/sector for {ticker}. Raw info: {yf_info}")
        except Exception as e:
            print(f"[CompanyProfile] yfinance failed for {ticker}: {e}")
        # 3. If yfinance returns no industry/sector, try to fetch the most recent SEC filing for the ticker (even if delisted)
        try:
            # Try to get a historical CIK from local mapping or fallback file
            cik = lookup_cik(ticker)
            if cik:
                # Try to fetch company info from the last available SEC filing
                profile = classify_company_by_sec(cik, ticker)
                if profile and (profile.industry or profile.industry_group):
                    return profile
            # If still no CIK, try to scrape the most recent SEC filing for the ticker
            # (This is a last-ditch effort for delisted/edge-case tickers)
            # Use SEC EDGAR search API to find the most recent filing for the ticker
            search_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude&action=getcompany&count=1"
            headers = {
                'User-Agent': os.getenv('SEC_EDGAR_USER_AGENT', 'AltmanZScore/1.0'),
                'From': os.getenv('SEC_API_EMAIL', '')
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            cik = None
            if resp.status_code == 200:
                import re
                # Try multiple patterns for CIK extraction
                patterns = [
                    r'CIK=(\d+)',
                    r'CIK#: (\d+)',

                    r'CIK (\d+)',
                    r'cik=(\d+)',
                ]
                for pat in patterns:
                    match = re.search(pat, resp.text)
                    if match:
                        cik = match.group(1).zfill(10)
                        break
                if cik:
                    # print(f"[DEBUG] Fallback SEC HTML CIK for {ticker}: {cik}")
                    profile = classify_company_by_sec(cik, ticker)
                    if profile and (profile.industry or profile.industry_group):
                        return profile
                else:
                    # print(f"[DEBUG] SEC HTML for {ticker} did not yield CIK. First 500 chars:\n{resp.text[:500]}")
                    pass
            # FINAL fallback: search SEC's company_tickers.json for a historical match
            if not cik:
                try:
                    url = "https://www.sec.gov/files/company_tickers.json"
                    headers = {
                        'User-Agent': os.getenv('SEC_EDGAR_USER_AGENT', 'AltmanZScore/1.0'),
                        'From': os.getenv('SEC_API_EMAIL', '')
                    }
                    resp = requests.get(url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    for entry in data.values():
                        if entry['ticker'].upper() == ticker.upper():
                            cik = str(entry['cik_str']).zfill(10)
                            # print(f"[DEBUG] Fallback company_tickers.json CIK for {ticker}: {cik}")
                            profile = classify_company_by_sec(cik, ticker)
                            if profile and (profile.industry or profile.industry_group):
                                return profile
                    print(f"[ERROR] Ticker {ticker} not found in SEC company_tickers.json (delisted or never listed)")
                except Exception as e:
                    print(f"[CompanyProfile] Could not fetch company_tickers.json for {ticker}: {e}")
        except Exception as e:
            print(f"[CompanyProfile] Could not fetch historical CIK/profile for {ticker}: {e}")
        # No static fallback
        import inspect
        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        # Try to find the calling function and its arguments
        missing_quarter = None
        for f in outer_frames:
            args, _, _, values = inspect.getargvalues(f.frame)
            if 'quarter' in args:
                missing_quarter = values.get('quarter', None)
                break
        if missing_quarter:
            print(f"[ERROR] Could not classify company for ticker {ticker} (no industry/sector from yfinance) for quarter {missing_quarter}")
        else:
            print(f"[ERROR] Could not classify company for ticker {ticker} (no industry/sector from yfinance)")
        return None

def lookup_cik(ticker: str) -> Optional[str]:
    """
    Lookup the CIK for a given ticker using local mapping or SEC API.

    Args:
        ticker (str): Stock ticker symbol
    Returns:
        str or None: 10-digit CIK if found, else None
    """
    try:
        # CIK mapping is not available
        raise NotImplementedError("CIK mapping functionality is not available. The cik_mapping module has been removed from the codebase.")
    except Exception:
        pass
    # Fallback: SEC's public ticker-CIK mapping
    try:
        url = f"https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': os.getenv('SEC_EDGAR_USER_AGENT', 'AltmanZScore/1.0'),
            'From': os.getenv('SEC_API_EMAIL', 'AltmanZScore/1.0')
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
    """
    Fetch company info from SEC EDGAR, extract SIC code, and map to industry group and maturity.

    Args:
        cik (str): 10-digit CIK
        ticker (str): Stock ticker symbol
    Returns:
        CompanyProfile: Populated profile (may have limited info if SEC fetch fails)
    """
    import requests
    import time
    sec_api_email = os.getenv('SEC_API_EMAIL', '')
    headers = {
        'User-Agent': os.getenv('SEC_EDGAR_USER_AGENT', 'AltmanZScore/1.0'),
        'From': sec_api_email
    }
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        sic = str(data.get('sic', ''))
        country = data.get('addresses', {}).get('business', {}).get('country', None)
        ig = IndustryGroup.OTHER
        maturity = None
        # --- Robust maturity assignment logic ---
        if sic:
            try:
                sic_int = int(sic)
                # Industry group mapping
                if 3570 <= sic_int <= 3579 or 3670 <= sic_int <= 3679 or 7370 <= sic_int <= 7379:
                    ig = IndustryGroup.TECH
                    # Tech: public = mature, private = growth/early
                    maturity = 'mature'
                elif 6000 <= sic_int <= 6999:
                    ig = IndustryGroup.FINANCIAL
                    maturity = 'mature'
                elif 2000 <= sic_int <= 3999:
                    ig = IndustryGroup.MANUFACTURING
                    # Manufacturing: public = mature, private = growth/early
                    maturity = 'mature'
                elif 7000 <= sic_int <= 8999:
                    ig = IndustryGroup.SERVICE
                    # Service: public = mature, private = growth/early
                    maturity = 'mature'
                else:
                    ig = IndustryGroup.OTHER
                    maturity = 'mature'  # Default to mature for public, developed market
                # Example: If SIC is in biotech/early-stage, could set 'growth' or 'early' (future extensibility)
                # If SIC is 2834 (biotech), set to 'growth' or 'early' (not implemented here)
            except Exception:
                maturity = 'mature'  # Fallback for parse errors
        else:
            maturity = 'mature'  # Fallback if no SIC but public and developed
        emerging_countries = [
            'china', 'india', 'brazil', 'russia', 'south africa',
            'mexico', 'indonesia', 'turkey', 'thailand', 'malaysia',
            'philippines', 'chile', 'colombia', 'poland', 'egypt',
            'hungary', 'qatar', 'uae', 'peru', 'greece', 'czech republic',
            'pakistan', 'saudi arabia', 'south korea', 'taiwan', 'vietnam'
        ]
        country_str = (country or '').lower()
        is_em = country_str in emerging_countries
        return CompanyProfile(
            ticker,
            industry=f"SIC {sic}" if sic else None,
            is_public=True,
            is_emerging_market=is_em,
            industry_group=ig,
            market_category=MarketCategory.EMERGING if is_em else MarketCategory.DEVELOPED,
            country=country,
            exchange=None,
            maturity=maturity
        )
    except Exception as e:
        print(f"[CompanyProfile] SEC EDGAR real-time fetch failed for {ticker}: {e}")
        return CompanyProfile(ticker, industry_group=IndustryGroup.OTHER, market_category=MarketCategory.DEVELOPED, maturity='mature')