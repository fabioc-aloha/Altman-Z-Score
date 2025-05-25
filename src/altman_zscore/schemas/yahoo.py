"""Yahoo Finance API response schemas."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime
from decimal import Decimal

from .base import BaseResponse, ResponseStatus, DataQualityMetrics

@dataclass
class MarketQuote:
    """Stock market quote data."""
    symbol: str
    price: Decimal
    volume: int
    timestamp: datetime
    currency: str
    exchange: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketQuote':
        """Create market quote from dictionary."""
        return cls(
            symbol=data['symbol'],
            price=Decimal(str(data['price'])),
            volume=int(data['volume']),
            timestamp=datetime.fromtimestamp(data['timestamp']),
            currency=data['currency'],
            exchange=data['exchange']
        )

@dataclass
class HistoricalPrice:
    """Historical price data point."""
    date: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    adj_close: Decimal
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalPrice':
        """Create historical price from dictionary."""
        return cls(
            date=datetime.fromtimestamp(data['date']),
            open=Decimal(str(data['open'])),
            high=Decimal(str(data['high'])),
            low=Decimal(str(data['low'])),
            close=Decimal(str(data['close'])),
            volume=int(data['volume']),
            adj_close=Decimal(str(data['adjclose']))
        )

@dataclass
class CompanyProfile:
    """Company profile information."""
    symbol: str
    name: str
    sector: str
    industry: str
    employees: Optional[int]
    website: Optional[str]
    description: Optional[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyProfile':
        """Create company profile from dictionary."""
        return cls(
            symbol=data['symbol'],
            name=data['name'],
            sector=data['sector'],
            industry=data['industry'],
            employees=data.get('fullTimeEmployees'),
            website=data.get('website'),
            description=data.get('description')
        )

@dataclass
class YahooResponse(BaseResponse):
    """Base response for Yahoo Finance API."""
    request_id: str
    data_quality: DataQualityMetrics
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'YahooResponse':
        """Create Yahoo response from dictionary."""
        base = super().from_dict(data)
        return cls(
            status=base.status,
            timestamp=base.timestamp,
            request_id=data['requestId'],
            data_quality=DataQualityMetrics(
                completeness=data['dataQuality']['completeness'],
                accuracy=data['dataQuality']['accuracy'],
                timeliness=data['dataQuality']['timeliness'],
                consistency=data['dataQuality']['consistency']
            )
        )

@dataclass
class QuoteResponse(YahooResponse):
    """Response containing market quote."""
    quote: MarketQuote

@dataclass
class HistoryResponse(YahooResponse):
    """Response containing historical price data."""
    symbol: str
    start_date: datetime
    end_date: datetime
    interval: str
    prices: List[HistoricalPrice]

@dataclass
class ProfileResponse(YahooResponse):
    """Response containing company profile."""
    profile: CompanyProfile
