"""
industry_classifier.py
---------------------
Industry classifier for Altman Z-Score pipeline (MVP scaffold).

This module provides a function to classify companies by industry, public/private status, and emerging market status.
Uses SEC EDGAR and Yahoo Finance for robust classification.

Functions:
    classify_company(ticker): Returns a CompanyProfile for the given ticker using SEC EDGAR first, then Yahoo Finance as fallback.
"""

# All imports should be at the top of the file, per Python best practices.

# DEPRECATED: Old classify_company using Yahoo API (rate-limited, unreliable)
# def classify_company(ticker: str):
#     """
#     Classify company by industry, public/private, and emerging market status using Yahoo Finance profile API.
#     Returns a profile object with .industry, .is_public, .is_emerging_market attributes.
#     """
#     class Profile:
#         def __init__(self, industry, is_public=True, is_emerging_market=False):
#             self.industry = industry
#             self.is_public = is_public
#             self.is_emerging_market = is_emerging_market
#
#     # Use Yahoo Finance public API for company summary/profile
#     url = f'https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=assetProfile'
#     try:
#         resp = requests.get(url, timeout=10)
#         data = resp.json()
#         # print(f"[DEBUG] Yahoo Finance API response for {ticker}: {data}")  # Debug output
#         profile = data['quoteSummary']['result'][0]['assetProfile']
#         industry = profile.get('industry', '').lower()
#         country = profile.get('country', '').lower()
#         # Heuristic: treat US, CA, UK, EU as developed; others as emerging
#         is_emerging = country not in ['united states', 'canada', 'united kingdom', 'germany', 'france', 'japan', 'australia', 'netherlands', 'switzerland', 'sweden', 'norway', 'finland', 'denmark', 'belgium', 'austria', 'ireland', 'italy', 'spain', 'portugal', 'new zealand']
#         return Profile(industry=industry, is_public=True, is_emerging_market=is_emerging)
#     except Exception as e:
#         # print(f"[DEBUG] Exception in classify_company for {ticker}: {e}")  # Debug output
#         # Fallback: unknown industry, assume public, not emerging
#         return Profile(industry='unknown', is_public=True, is_emerging_market=False)

# New robust classifier using SEC EDGAR and Yahoo Finance


def classify_company(ticker):
    """
    Return a CompanyProfile for the given ticker, using SEC EDGAR first, then Yahoo Finance as fallback.

    Args:
        ticker (str): Stock ticker symbol.
    Returns:
        CompanyProfile: Populated company profile if found, else None.
    """
    from ..company.company_profile import CompanyProfile

    return CompanyProfile.from_ticker(ticker)
