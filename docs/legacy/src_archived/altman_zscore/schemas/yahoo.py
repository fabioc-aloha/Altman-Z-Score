"""
Yahoo Finance API response schemas.

Defines dataclasses for Yahoo Finance market quote, historical price, and company profile data, as well as response wrappers for Yahoo API integration and validation.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .base import BaseResponse, DataQualityMetrics


@dataclass
class MarketQuote:
    """Stock market quote data.

    Attributes:
        symbol (str): Stock ticker symbol.
        price (Decimal): Last traded price.
        volume (int): Trading volume.
        timestamp (datetime): Time of the quote.
        currency (str): Currency code.
        exchange (str): Exchange name.
    """

    symbol: str
    price: Decimal
    volume: int
    timestamp: datetime
    currency: str
    exchange: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketQuote":
        """Create MarketQuote from a dictionary.

        Args:
            data (dict): Dictionary with quote fields.
        Returns:
            MarketQuote: Instantiated MarketQuote object.
        """
        return cls(
            symbol=data["symbol"],
            price=Decimal(str(data["price"])),
            volume=int(data["volume"]),
            timestamp=datetime.fromtimestamp(data["timestamp"]),
            currency=data["currency"],
            exchange=data["exchange"],
        )


@dataclass
class HistoricalPrice:
    """Historical price data point for a stock.

    Attributes:
        date (datetime): Date of the price record.
        open (Decimal): Opening price.
        high (Decimal): Highest price.
        low (Decimal): Lowest price.
        close (Decimal): Closing price.
        volume (int): Trading volume.
        adj_close (Decimal): Adjusted closing price.
    """

    date: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adj_close: Decimal

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HistoricalPrice":
        """Create HistoricalPrice from a dictionary.

        Args:
            data (dict): Dictionary with price fields.
        Returns:
            HistoricalPrice: Instantiated HistoricalPrice object.
        """
        return cls(
            date=datetime.fromtimestamp(data["date"]),
            open=Decimal(str(data["open"])),
            high=Decimal(str(data["high"])),
            low=Decimal(str(data["low"])),
            close=Decimal(str(data["close"])),
            volume=int(data["volume"]),
            adj_close=Decimal(str(data["adjclose"])),
        )


@dataclass
class CompanyProfile:
    """Company profile information from Yahoo Finance.

    Attributes:
        symbol (str): Stock ticker symbol.
        name (str): Company name.
        sector (str): Sector name.
        industry (str): Industry name.
        employees (int, optional): Number of employees.
        website (str, optional): Company website URL.
        description (str, optional): Company description.
    """

    symbol: str
    name: str
    sector: str
    industry: str
    employees: Optional[int]
    website: Optional[str]
    description: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompanyProfile":
        """Create CompanyProfile from a dictionary.

        Args:
            data (dict): Dictionary with profile fields.
        Returns:
            CompanyProfile: Instantiated CompanyProfile object.
        """
        return cls(
            symbol=data["symbol"],
            name=data["name"],
            sector=data["sector"],
            industry=data["industry"],
            employees=data.get("fullTimeEmployees"),
            website=data.get("website"),
            description=data.get("description"),
        )


@dataclass
class YahooResponse(BaseResponse):
    """Base response for Yahoo Finance API.

    Attributes:
        request_id (str): Unique request identifier.
        data_quality (DataQualityMetrics): Data quality metrics for the response.
    """

    request_id: str
    data_quality: DataQualityMetrics

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "YahooResponse":
        """Create YahooResponse from a dictionary.

        Args:
            data (dict): Dictionary with response fields.
        Returns:
            YahooResponse: Instantiated YahooResponse object.
        """
        base = super().from_dict(data)
        return cls(
            status=base.status,
            timestamp=base.timestamp,
            request_id=data["requestId"],
            data_quality=DataQualityMetrics(
                completeness=data["dataQuality"]["completeness"],
                accuracy=data["dataQuality"]["accuracy"],
                timeliness=data["dataQuality"]["timeliness"],
                consistency=data["dataQuality"]["consistency"],
            ),
        )


@dataclass
class QuoteResponse(YahooResponse):
    """Response containing a market quote.

    Attributes:
        quote (MarketQuote): Market quote data.
    """

    quote: MarketQuote


@dataclass
class HistoryResponse(YahooResponse):
    """Response containing historical price data for a symbol.

    Attributes:
        symbol (str): Stock ticker symbol.
        start_date (datetime): Start date of the price history.
        end_date (datetime): End date of the price history.
        interval (str): Data interval (e.g., '1d', '1wk').
        prices (list of HistoricalPrice): List of historical price records.
    """

    symbol: str
    start_date: datetime
    end_date: datetime
    interval: str
    prices: List[HistoricalPrice]


@dataclass
class ProfileResponse(YahooResponse):
    """Response containing company profile data.

    Attributes:
        profile (CompanyProfile): Company profile information.
    """

    profile: CompanyProfile
