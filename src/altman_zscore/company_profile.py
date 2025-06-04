import os
from enum import Enum
from typing import Optional

import requests

from altman_zscore.utils.paths import get_output_dir
from altman_zscore.company_profile_helpers import find_field, is_emerging_market_country, get_industry_group, get_market_category, classify_maturity, extract_cik_from_sec_html, get_sec_headers, get_emerging_countries, classify_company_by_sec

"""
Company profile classification and lookup utilities for Altman Z-Score model selection.

This module provides logic to classify companies by ticker using SEC EDGAR and Yahoo Finance,
with robust fallback for delisted/edge-case tickers. Used for model selection and reporting.

Classes:
    IndustryGroup (Enum): Industry group classification.
    MarketCategory (Enum): Market category (developed/emerging).
    TechSubsector (Enum): Technology subsector classification.
    CompanyProfile: Company profile for Altman Z-Score model selection.

Functions:
    lookup_cik(ticker): Lookup the CIK for a given ticker using local mapping or SEC API.
    classify_company_by_sec(cik, ticker): Fetch company info from SEC EDGAR and map to industry group and maturity.
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

    Methods:
        classify_maturity(founding_year, ipo_date, current_year): Classify company maturity.
        from_ticker(ticker): Classify company by ticker using SEC EDGAR and Yahoo Finance.
    """

    def __init__(
        self,
        ticker,
        industry=None,
        is_public=True,
        is_emerging_market=False,
        industry_group=None,
        market_category=None,
        tech_subsector=None,
        country=None,
        exchange=None,
        founding_year=None,
        ipo_date=None,
        maturity=None,
    ):
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
        return classify_maturity(founding_year, ipo_date, current_year)

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
            import json

            import yfinance as yf

            yf_ticker = yf.Ticker(ticker)
            yf_info = yf_ticker.info  # Save the raw yfinance info payload for traceability
            output_path = get_output_dir("yf_info.json", ticker=ticker)
            with open(output_path, "w") as f:
                json.dump(yf_info, f, indent=2)

            # Dynamically resolve fields
            industry = find_field(yf_info, ["industry", "industryKey", "industryDisp", "sector", "sectorKey", "sectorDisp"])
            country = find_field(yf_info, ["country", "countryKey", "countryDisp"])
            exchange = find_field(yf_info, ["exchange", "fullExchangeName", "exchangeTimezoneName"])
            founding_year = find_field(yf_info, ["founded", "startYear", "foundingYear"])
            ipo_date = find_field(yf_info, ["ipoDate", "ipoYear", "ipo"])
            is_public = True
            country_str = (country or "").lower()
            is_em = is_emerging_market_country(country_str)
            maturity = classify_maturity(founding_year, ipo_date)
            market_category = get_market_category(is_em)
            # print(f"[DEBUG] yfinance info for {ticker}: industry={industry}, country={country}, exchange={exchange}")
            if industry:
                # Map to enums if possible
                ig = get_industry_group(industry)
                # print(f"[DEBUG] yfinance classification for {ticker}: ig={ig}, is_em={is_em}")
                return CompanyProfile(
                    ticker,
                    industry,
                    is_public,
                    is_em,
                    ig,
                    market_category,
                    country=country,
                    exchange=exchange,
                    founding_year=founding_year,
                    ipo_date=ipo_date,
                    maturity=maturity,
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
            from altman_zscore.api.sec_client import SECClient
            search_url = (
                f"{SECClient.BROWSE_EDGAR_URL}?CIK={ticker}&owner=exclude&action=getcompany&count=1"
            )
            headers = {
                "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"],
                "From": os.getenv("SEC_API_EMAIL", ""),
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            cik = None
            if resp.status_code == 200:
                # Use extract_cik_from_sec_html for CIK extraction from SEC HTML
                cik = extract_cik_from_sec_html(resp.text)
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
                    url = SECClient.COMPANY_TICKERS_URL
                    headers = {
                        "User-Agent": os.environ["SEC_EDGAR_USER_AGENT"],
                        "From": os.getenv("SEC_API_EMAIL", ""),
                    }
                    resp = requests.get(url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    for entry in data.values():
                        if entry["ticker"].upper() == ticker.upper():
                            cik = str(entry["cik_str"]).zfill(10)
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
            if "quarter" in args:
                missing_quarter = values.get("quarter", None)
                break
        if missing_quarter:
            print(
                f"[ERROR] Could not classify company for ticker {ticker} (no industry/sector from yfinance) for quarter {missing_quarter}"
            )
        else:
            print(f"[ERROR] Could not classify company for ticker {ticker} (no industry/sector from yfinance)")
        return None

    def __str__(self):
        # Fix F541: f-string is missing placeholders
        return f"CompanyProfile(ticker={self.ticker}, industry={self.industry}, is_public={self.is_public})"


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
        raise NotImplementedError(
            "CIK mapping functionality is not available. The cik_mapping module has been removed from the codebase."
        )
    except Exception:
        pass
    # Fallback: SEC's public ticker-CIK mapping
    try:
        from altman_zscore.api.sec_client import SECClient
        url = SECClient.COMPANY_TICKERS_URL
        headers = get_sec_headers()
        if not headers["From"]:
            import warnings

            warnings.warn("SEC_API_EMAIL is not set in environment. SEC requests may be rejected.")
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for entry in data.values():
            if entry["ticker"].upper() == ticker.upper():
                return str(entry["cik_str"]).zfill(10)
    except Exception:
        pass
    return None
