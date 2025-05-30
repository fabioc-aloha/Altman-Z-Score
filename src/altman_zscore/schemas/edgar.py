"""SEC EDGAR API response schemas."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import BaseResponse, DataQualityMetrics


@dataclass
class FilingInfo:
    """Information about an SEC filing."""

    accession_number: str
    file_number: str
    form_type: str
    filing_date: datetime
    accepted_date: datetime
    report_date: datetime
    size: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FilingInfo":
        """Create filing info from dictionary."""
        return cls(
            accession_number=data["accessionNumber"],
            file_number=data["fileNumber"],
            form_type=data["form"],
            filing_date=datetime.fromisoformat(data["filingDate"]),
            accepted_date=datetime.fromisoformat(data["acceptedDate"]),
            report_date=datetime.fromisoformat(data["reportDate"]),
            size=int(data["size"]),
        )


@dataclass
class CompanyInfo:
    """Company information from SEC."""

    cik: str
    name: str
    sic: Optional[str]
    sic_description: Optional[str]
    state_of_incorporation: str
    fiscal_year_end: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompanyInfo":
        """Create company info from dictionary."""
        return cls(
            cik=data["cik"],
            name=data["name"],
            sic=data.get("sic"),
            sic_description=data.get("sicDescription"),
            state_of_incorporation=data["stateOfIncorporation"],
            fiscal_year_end=data["fiscalYearEnd"],
        )


@dataclass
class XBRLData:
    """XBRL financial data."""

    taxonomy: str
    version: str
    schema_ref: str
    facts: Dict[str, Any]
    contexts: Dict[str, Any]
    units: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "XBRLData":
        """Create XBRL data from dictionary."""
        return cls(
            taxonomy=data["taxonomy"],
            version=data["version"],
            schema_ref=data["schemaRef"],
            facts=data["facts"],
            contexts=data["contexts"],
            units=data["units"],
        )


@dataclass
class EDGARResponse(BaseResponse):
    """Base response for SEC EDGAR API."""

    request_id: str
    data_quality: DataQualityMetrics

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EDGARResponse":
        """Create EDGAR response from dictionary."""
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
class CompanyResponse(EDGARResponse):
    """Response containing company information."""

    company: CompanyInfo
    filings: List[FilingInfo]


@dataclass
class FilingResponse(EDGARResponse):
    """Response containing filing data."""

    filing: FilingInfo
    xbrl_data: Optional[XBRLData] = None
    raw_text: Optional[str] = None


@dataclass
class SearchResponse(EDGARResponse):
    """Response for company search."""

    total_results: int
    page_size: int
    page_number: int
    companies: List[CompanyInfo]
