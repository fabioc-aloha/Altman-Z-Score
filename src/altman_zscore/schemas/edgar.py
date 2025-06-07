"""
SEC EDGAR API response schemas.

Defines dataclasses for SEC filing, company, and XBRL data, as well as response wrappers for EDGAR API integration and validation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import BaseResponse, DataQualityMetrics


@dataclass
class FilingInfo:
    """Information about an SEC filing.

    Attributes:
        accession_number (str): Unique accession number for the filing.
        file_number (str): SEC file number.
        form_type (str): SEC form type (e.g., 10-K, 10-Q).
        filing_date (datetime): Date the filing was made.
        accepted_date (datetime): Date the filing was accepted by the SEC.
        report_date (datetime): Date of the report covered by the filing.
        size (int): Size of the filing in bytes.
    """

    accession_number: str
    file_number: str
    form_type: str
    filing_date: datetime
    accepted_date: datetime
    report_date: datetime
    size: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FilingInfo":
        """Create FilingInfo from a dictionary.

        Args:
            data (dict): Dictionary with filing info fields.
        Returns:
            FilingInfo: Instantiated FilingInfo object.
        """
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
    """Company information from SEC.

    Attributes:
        cik (str): Central Index Key.
        name (str): Company name.
        sic (str, optional): SIC code.
        sic_description (str, optional): SIC code description.
        state_of_incorporation (str): State of incorporation.
        fiscal_year_end (str): Fiscal year end month/day.
    """

    cik: str
    name: str
    sic: Optional[str]
    sic_description: Optional[str]
    state_of_incorporation: str
    fiscal_year_end: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompanyInfo":
        """Create CompanyInfo from a dictionary.

        Args:
            data (dict): Dictionary with company info fields.
        Returns:
            CompanyInfo: Instantiated CompanyInfo object.
        """
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
    """XBRL financial data for a filing.

    Attributes:
        taxonomy (str): XBRL taxonomy name.
        version (str): XBRL taxonomy version.
        schema_ref (str): Schema reference URL.
        facts (dict): XBRL facts.
        contexts (dict): XBRL contexts.
        units (dict): XBRL units.
    """

    taxonomy: str
    version: str
    schema_ref: str
    facts: Dict[str, Any]
    contexts: Dict[str, Any]
    units: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "XBRLData":
        """Create XBRLData from a dictionary.

        Args:
            data (dict): Dictionary with XBRL data fields.
        Returns:
            XBRLData: Instantiated XBRLData object.
        """
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
    """Base response for SEC EDGAR API.

    Attributes:
        request_id (str): Unique request identifier.
        data_quality (DataQualityMetrics): Data quality metrics for the response.
    """

    request_id: str
    data_quality: DataQualityMetrics

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EDGARResponse":
        """Create EDGARResponse from a dictionary.

        Args:
            data (dict): Dictionary with response fields.
        Returns:
            EDGARResponse: Instantiated EDGARResponse object.
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
class CompanyResponse(EDGARResponse):
    """Response containing company information and filings.

    Attributes:
        company (CompanyInfo): Company information.
        filings (list of FilingInfo): List of company filings.
    """

    company: CompanyInfo
    filings: List[FilingInfo]


@dataclass
class FilingResponse(EDGARResponse):
    """Response containing filing data and optional XBRL/Raw text.

    Attributes:
        filing (FilingInfo): Filing information.
        xbrl_data (XBRLData, optional): XBRL data if available.
        raw_text (str, optional): Raw filing text if available.
    """

    filing: FilingInfo
    xbrl_data: Optional[XBRLData] = None
    raw_text: Optional[str] = None


@dataclass
class SearchResponse(EDGARResponse):
    """Response for company search queries.

    Attributes:
        total_results (int): Total number of results.
        page_size (int): Number of results per page.
        page_number (int): Current page number.
        companies (list of CompanyInfo): List of matching companies.
    """

    total_results: int
    page_size: int
    page_number: int
    companies: List[CompanyInfo]
