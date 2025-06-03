"""
Helper functions for company profile parsing and classification.
"""

def find_field(yf_info, possible_keys):
    """
    Helper to search for the first non-empty value among possible keys in a dict.
    """
    for key in possible_keys:
        val = yf_info.get(key)
        if val:
            return val
    return None

def is_emerging_market_country(country: str) -> bool:
    """
    Returns True if the country is considered an emerging market.
    """
    emerging_countries = get_emerging_countries()
    return (country or "").strip().lower() in emerging_countries

def get_emerging_countries() -> list:
    """
    Return the list of emerging market countries used for classification.
    """
    return [
        "china", "india", "brazil", "russia", "south africa", "mexico", "indonesia", "turkey",
        "thailand", "malaysia", "philippines", "chile", "colombia", "poland", "egypt", "hungary",
        "qatar", "uae", "peru", "greece", "czech republic", "pakistan", "saudi arabia", "south korea",
        "taiwan", "vietnam"
    ]

def get_industry_group(industry: str):
    """
    Map an industry string to an IndustryGroup enum value.
    """
    # Import here to avoid circular import
    from altman_zscore.company_profile import IndustryGroup
    if not industry:
        return IndustryGroup.OTHER
    ind_lower = str(industry).lower()
    if "tech" in ind_lower:
        return IndustryGroup.TECH
    elif "bank" in ind_lower or "financ" in ind_lower:
        return IndustryGroup.FINANCIAL
    elif (
        "manufactur" in ind_lower
        or "consumer electronics" in ind_lower
        or "hardware" in ind_lower
        or "semiconductor" in ind_lower
    ):
        return IndustryGroup.MANUFACTURING
    elif "service" in ind_lower or "entertain" in ind_lower:
        return IndustryGroup.SERVICE
    else:
        return IndustryGroup.OTHER

def get_market_category(is_emerging: bool):
    """
    Map a boolean is_emerging to the MarketCategory enum.
    """
    # Import here to avoid circular import
    from altman_zscore.company_profile import MarketCategory
    return MarketCategory.EMERGING if is_emerging else MarketCategory.DEVELOPED

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
                return "early-stage"
            elif years_since_ipo < 7:
                return "growth"
            else:
                return "mature"
        except Exception:
            pass
    if founding_year:
        try:
            years_since_founding = current_year - int(founding_year)
            if years_since_founding < 3:
                return "early-stage"
            elif years_since_founding < 7:
                return "growth"
            else:
                return "mature"
        except Exception:
            pass
    return "mature"  # Default fallback

def extract_cik_from_sec_html(html: str) -> str | None:
    """
    Extract CIK from SEC HTML response using multiple regex patterns.
    """
    import re
    patterns = [
        r"CIK=(\d+)",
        r"CIK#: (\d+)",
        r"CIK (\d+)",
        r"cik=(\d+)"
    ]
    for pat in patterns:
        match = re.search(pat, html)
        if match:
            return match.group(1).zfill(10)
    return None

def get_sec_headers() -> dict:
    """
    Return headers for SEC requests using environment variables.
    """
    import os
    return {
        "User-Agent": os.environ.get("SEC_EDGAR_USER_AGENT", "AltmanZScore/1.0"),
        "From": os.getenv("SEC_API_EMAIL", "AltmanZScore/1.0"),
    }

def classify_company_by_sec(cik: str, ticker: str):
    """
    Fetch company info from SEC EDGAR, extract SIC code, and map to industry group and maturity.
    """
    import requests
    # Import here to avoid circular import
    from altman_zscore.company_profile import CompanyProfile, IndustryGroup, MarketCategory
    headers = get_sec_headers()
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        sic = str(data.get("sic", ""))
        country = data.get("addresses", {}).get("business", {}).get("country", None)
        ig = IndustryGroup.OTHER
        maturity = None
        # --- Robust maturity assignment logic ---
        if sic:
            try:
                sic_int = int(sic)
                # Industry group mapping
                if 3570 <= sic_int <= 3579 or 3670 <= sic_int <= 3679 or 7370 <= sic_int <= 7379:
                    ig = IndustryGroup.TECH
                    maturity = "mature"
                elif 6000 <= sic_int <= 6999:
                    ig = IndustryGroup.FINANCIAL
                    maturity = "mature"
                elif 2000 <= sic_int <= 3999:
                    ig = IndustryGroup.MANUFACTURING
                    maturity = "mature"
                elif 7000 <= sic_int <= 8999:
                    ig = IndustryGroup.SERVICE
                    maturity = "mature"
                else:
                    ig = IndustryGroup.OTHER
                    maturity = "mature"
            except Exception:
                maturity = "mature"
        else:
            maturity = "mature"
        emerging_countries = get_emerging_countries()
        country_str = (country or "").lower()
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
            maturity=maturity,
        )
    except Exception as e:
        print(f"[CompanyProfile] SEC EDGAR real-time fetch failed for {ticker}: {e}")
        return None
# ...helpers will be moved here from company_profile.py...
