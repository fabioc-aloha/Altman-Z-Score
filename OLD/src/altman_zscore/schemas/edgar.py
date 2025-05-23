"""SEC EDGAR API response schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from .base import BaseResponse, DataQualityMetrics

class FilingInfo(BaseModel):
    """Information about an SEC filing."""
    accession_number: str = Field(..., alias='accessionNumber')
    file_number: str = Field(..., alias='fileNumber')
    form_type: str = Field(..., alias='form')
    filing_date: datetime = Field(..., alias='filingDate')
    accepted_date: datetime = Field(..., alias='acceptedDate')
    report_date: datetime = Field(..., alias='reportDate')
    size: int = Field(..., alias='size')

    class Config:
        allow_population_by_field_name = True

class CompanyInfo(BaseModel):
    """Company information from SEC."""
    cik: str
    name: str
    sic: Optional[str]
    sic_description: Optional[str] = Field(None, alias='sicDescription')
    state_of_incorporation: str = Field(..., alias='stateOfIncorporation')
    fiscal_year_end: str = Field(..., alias='fiscalYearEnd')

    class Config:
        allow_population_by_field_name = True

class XBRLData(BaseModel):
    """XBRL financial data."""
    taxonomy: str
    version: str
    schema_ref: str = Field(..., alias='schemaRef')
    facts: Dict[str, Any]
    contexts: Dict[str, Any]
    units: Dict[str, Any]

    class Config:
        allow_population_by_field_name = True

class EDGARResponse(BaseResponse):
    """Base response for SEC EDGAR API."""
    request_id: str = Field(..., alias='requestId')
    data_quality: DataQualityMetrics = Field(..., alias='dataQuality')

    class Config:
        allow_population_by_field_name = True

class CompanyResponse(EDGARResponse):
    """Response containing company information."""
    company: CompanyInfo
    filings: List[FilingInfo]

class FilingResponse(EDGARResponse):
    """Response containing filing data."""
    filing: FilingInfo
    xbrl_data: Optional[XBRLData] = Field(None, alias='xbrlData')
    raw_text: Optional[str] = Field(None, alias='rawText')

    class Config:
        allow_population_by_field_name = True

class SearchResponse(EDGARResponse):
    """Response for company search."""
    total_results: int = Field(..., alias='totalResults')
    page_size: int = Field(..., alias='pageSize')
    page_number: int = Field(..., alias='pageNumber')
    companies: List[CompanyInfo]

    class Config:
        allow_population_by_field_name = True
