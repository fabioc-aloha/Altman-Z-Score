"""
API client package for Altman Z-Score analysis.

DEPRECATED: This package is part of the legacy SEC EDGAR architecture.
New development should use: altman_zscore/layers/data_fetch/
"""

from .yahoo_client import YahooFinanceClient
from .finnhub_client import FinnhubClient

# DEPRECATED: SECClient has been removed
# from .sec_client import SECClient

__all__ = ["YahooFinanceClient", "FinnhubClient"]
