"""
cik_lookup.py
-------------
Module for common CIK mappings to avoid SEC EDGAR API rate limiting.

This module provides a dictionary of common ticker symbols mapped to their
SEC CIK (Central Index Key) numbers. This helps avoid unnecessary API calls
to the SEC EDGAR service, which has strict rate limits.
"""

# Common CIK mappings for frequently used tickers
# This helps avoid unnecessary SEC API calls
COMMON_CIK_MAPPINGS = {
    "MSFT": "0000789019",  # Microsoft
    "AAPL": "0000320193",  # Apple
    "GOOGL": "0001652044", # Alphabet (Google)
    "GOOG": "0001652044",  # Alphabet (Google) - Class C shares
    "AMZN": "0001018724",  # Amazon
    "META": "0001326801",  # Meta (Facebook)
    "TSLA": "0001318605",  # Tesla
    "NVDA": "0001045810",  # NVIDIA
    "JPM": "0000019617",   # JPMorgan Chase
    "V": "0001403161",     # Visa
    "WMT": "0000104169",   # Walmart
    "JNJ": "0000200406",   # Johnson & Johnson
    "PG": "0000080424",    # Procter & Gamble
    "MA": "0001141391",    # Mastercard
    "UNH": "0000731766",   # UnitedHealth Group
    "HD": "0000354950",    # Home Depot
    "BAC": "0000070858",   # Bank of America
    "XOM": "0000034088",   # Exxon Mobil
    "INTC": "0000050863",  # Intel
    "VZ": "0000732712",    # Verizon
    "CSCO": "0000858877",  # Cisco
    "NFLX": "0001065280",  # Netflix
    "ADBE": "0000796343",  # Adobe
    "CRM": "0001108524",   # Salesforce
    "PEP": "0000077476",   # PepsiCo
    "CMCSA": "0001166691", # Comcast
    "COST": "0000909832",  # Costco
    "ABT": "0000001800",   # Abbott Laboratories
    "TMO": "0000097745",   # Thermo Fisher Scientific
    "AVGO": "0001730168",  # Broadcom
    "MRK": "0000310158",   # Merck    
    "DIS": "0001001039",   # Walt Disney
    "SONO": "0001537073",  # Sonos Inc
    "UAL": "0000100517",   # United Airlines Holdings Inc
}
