"""
Field Database Builder - Layer 0: Field Mapping Cache Layer

This module generates deterministic, rule-based field mappings from SEC EDGAR data.
It refactors the legacy build_field_database.py to be compatible with the new 
modular architecture.

Key Features:
- Deterministic field mapping only (no LLM/AI)
- Rule-based SEC field to canonical field mapping
- Version-controlled cache output
- Auditability and transparency

Usage:
    from altman_zscore.cache.field_database_builder import build_deterministic_field_cache
    
    cache = build_deterministic_field_cache(
        sample_size=50,
        include_companies=['AAPL', 'MSFT', 'GOOGL']
    )
"""

import logging
import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Optional, Tuple
import time
import random
from datetime import datetime

# Import shared infrastructure
from ..common.logging_config import get_logger
from ..common.config import get_config
from ..common.api_rate_limiter import rate_limiter
from ..common.exceptions import DataFetchError, ValidationError
from ..common.validators import validate_ticker_symbol, validate_cik_number
from ..common.utils import ensure_dir_exists, safe_json_read, safe_json_write
from ..common.progress import ProgressTracker

# Temporary stub implementations (to be replaced with Layer 1 implementation)
class _SECClientStub:
    """Temporary stub for SEC client."""
    def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """Stub implementation."""
        return {
            'facts': {
                'us-gaap': {
                    'Revenue': {'units': {'USD': []}},
                    'Assets': {'units': {'USD': []}},
                    'AssetsCurrent': {'units': {'USD': []}},
                    'LiabilitiesCurrent': {'units': {'USD': []}}
                }
            }
        }

def _load_sec_company_cache_stub(full: bool = False) -> Dict[str, Any]:
    """Temporary stub for company cache loading."""
    return {
        'AAPL': {'cik_str': '320193', 'title': 'Apple Inc'},
        'MSFT': {'cik_str': '789019', 'title': 'Microsoft Corp'},
        'GOOGL': {'cik_str': '1652044', 'title': 'Alphabet Inc'}
    }

logger = get_logger(__name__)

# Canonical fields that need to be mapped
CANONICAL_FIELDS = {
    'sales': ['Revenue', 'Revenues', 'SalesRevenueNet', 'SalesRevenueGoodsNet', 
              'SalesRevenueServicesNet', 'RevenueFromContractWithCustomerExcludingAssessedTax'],
    'total_assets': ['Assets', 'AssetsCurrent', 'AssetsNoncurrent'],
    'current_assets': ['AssetsCurrent'],
    'current_liabilities': ['LiabilitiesCurrent'],
    'total_liabilities': ['Liabilities', 'LiabilitiesAndStockholdersEquity'],
    'retained_earnings': ['RetainedEarningsAccumulatedDeficit'],
    'ebit': ['OperatingIncomeLoss', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'],
    'market_value_equity': [],  # Calculated from market data
    'book_value_equity': ['StockholdersEquity', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],
    'working_capital': [],  # Computed as current_assets - current_liabilities
    'inventory': ['InventoryNet'],
    'cost_of_goods_sold': ['CostOfGoodsAndServicesSold', 'CostOfRevenue']
}


def build_deterministic_field_cache(
    sample_size: int = 50,
    include_companies: Optional[List[str]] = None,
    exclude_companies: Optional[List[str]] = None,
    use_existing_cache: bool = True
) -> Dict[str, Any]:
    """
    Build a deterministic field mapping cache from SEC EDGAR data.
    
    This function uses only rule-based, deterministic mapping - no LLM/AI.
    
    Args:
        sample_size: Number of companies to sample for building the cache
        include_companies: Specific companies to include (tickers)
        exclude_companies: Companies to exclude from sampling (tickers)
        use_existing_cache: Whether to use existing cache as a starting point
        
    Returns:
        Dict containing the field mapping cache with metadata
        
    Raises:
        DataFetchError: If unable to fetch required SEC data
        ValidationError: If validation of mappings fails    """
    logger.info(f"Building deterministic field cache with {sample_size} companies")
    
    config = get_config()
    cache_dir = config.cache.cache_dir if hasattr(config, 'cache') else 'altman_zscore/cache'
    ensure_dir_exists(cache_dir)
    
    # Initialize progress tracker
    with ProgressTracker("Building Field Cache", sample_size) as progress:
        
        # Load existing cache if requested
        existing_cache = {}
        if use_existing_cache:
            existing_cache = _load_existing_cache(cache_dir)
            progress.update(1, "Loaded existing cache")
            
        # Get company list for processing
        companies_to_process = _get_companies_for_processing(
            sample_size, include_companies, exclude_companies, existing_cache
        )
        progress.update(1, f"Selected {len(companies_to_process)} companies")
        
        # Initialize cache structure
        field_cache = _initialize_cache_structure(existing_cache)
        
        # Process each company
        processed_count = 0
        failed_count = 0
        
        for ticker, cik in companies_to_process:
            try:
                progress.update(processed_count + 1, f"Processing {ticker}")
                
                # Fetch SEC facts for the company
                sec_data = _fetch_company_sec_data(ticker, cik)
                
                # Extract field mappings deterministically
                company_mappings = _extract_deterministic_mappings(ticker, sec_data)
                
                # Update cache with new mappings
                _update_cache_with_mappings(field_cache, ticker, company_mappings)
                
                processed_count += 1
                logger.debug(f"Successfully processed {ticker}")
                
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to process {ticker}: {e}")
                progress.update(processed_count + failed_count, f"Failed {ticker}")
                continue
        
        # Finalize cache with metadata
        field_cache = _finalize_cache_metadata(
            field_cache, processed_count, failed_count, sample_size
        )
        
        progress.complete(f"Built cache with {processed_count} companies")
        
    logger.info(f"Field cache build complete: {processed_count} processed, {failed_count} failed")
    return field_cache


@rate_limiter.rate_limited("sec_edgar")
def _fetch_company_sec_data(ticker: str, cik: str) -> Dict[str, Any]:
    """
    Fetch SEC facts data for a company.
    
    Args:
        ticker: Company ticker symbol
        cik: Company CIK identifier
        
    Returns:
        Dict containing SEC facts data
        
    Raises:
        DataFetchError: If unable to fetch data
    """
    try:        # Use legacy SEC client for now (to be replaced in Layer 1)
        sec_client = _SECClientStub()
          # Validate inputs
        ticker_result = validate_ticker_symbol(ticker)
        if not ticker_result.is_valid:
            raise ValidationError(f"Invalid ticker: {ticker}")
        cik_result = validate_cik_number(cik)
        if not cik_result.is_valid:
            raise ValidationError(f"Invalid CIK: {cik}")
            
        # Fetch company facts
        company_facts = sec_client.get_company_facts(cik)
        
        if not company_facts or 'facts' not in company_facts:
            raise DataFetchError(f"No facts data available for {ticker} (CIK: {cik})")
            
        return company_facts
        
    except Exception as e:
        logger.error(f"Failed to fetch SEC data for {ticker}: {e}")
        raise DataFetchError(f"SEC data fetch failed for {ticker}: {e}")


def _extract_deterministic_mappings(ticker: str, sec_data: Dict[str, Any]) -> Dict[str, Set[str]]:
    """
    Extract field mappings using deterministic rules.
    
    Args:
        ticker: Company ticker
        sec_data: SEC facts data
        
    Returns:
        Dict mapping canonical fields to sets of SEC field names
    """
    mappings = defaultdict(set)
    
    # Extract available SEC fields
    sec_facts = sec_data.get('facts', {})
    us_gaap_fields = sec_facts.get('us-gaap', {})
    dei_fields = sec_facts.get('dei', {})
    
    all_sec_fields = set(us_gaap_fields.keys()) | set(dei_fields.keys())
    
    # Apply deterministic mapping rules
    for canonical_field, known_sec_fields in CANONICAL_FIELDS.items():
        for sec_field in known_sec_fields:
            if sec_field in all_sec_fields:
                mappings[canonical_field].add(sec_field)
    
    # Apply fuzzy matching rules for additional coverage
    mappings = _apply_fuzzy_matching_rules(mappings, all_sec_fields)
    
    logger.debug(f"Extracted {len(mappings)} canonical field mappings for {ticker}")
    return dict(mappings)


def _apply_fuzzy_matching_rules(
    mappings: Dict[str, Set[str]], 
    all_sec_fields: Set[str]
) -> Dict[str, Set[str]]:
    """
    Apply fuzzy matching rules to find additional field mappings.
    
    Args:
        mappings: Existing mappings to extend
        all_sec_fields: All available SEC field names
        
    Returns:
        Extended mappings with fuzzy matches
    """
    # Define fuzzy matching patterns
    fuzzy_patterns = {
        'sales': ['Revenue', 'Sales', 'Income'],
        'total_assets': ['Assets'],
        'current_assets': ['AssetsCurrent', 'CurrentAssets'],
        'current_liabilities': ['LiabilitiesCurrent', 'CurrentLiabilities'],
        'total_liabilities': ['Liabilities'],
        'retained_earnings': ['RetainedEarnings', 'Earnings'],
        'ebit': ['Operating', 'EBIT', 'Income'],
        'book_value_equity': ['Equity', 'Stockholders']
    }
    
    for canonical_field, patterns in fuzzy_patterns.items():
        for pattern in patterns:
            matching_fields = [f for f in all_sec_fields if pattern in f]
            mappings[canonical_field].update(matching_fields)
    
    return mappings


def _get_companies_for_processing(
    sample_size: int,
    include_companies: Optional[List[str]],
    exclude_companies: Optional[List[str]],
    existing_cache: Dict[str, Any]
) -> List[Tuple[str, str]]:
    """
    Get list of companies to process for cache building.
    
    Returns:
        List of (ticker, cik) tuples
    """    # Load SEC company cache
    sec_companies = _load_sec_company_cache_stub(full=True)
    
    # Filter already processed companies
    processed_companies = set(existing_cache.get('metadata', {}).get('companies_analyzed', []))
    
    available_companies = []
    for ticker, company_data in sec_companies.items():
        if ticker in processed_companies:
            continue
        if exclude_companies and ticker in exclude_companies:
            continue
        if include_companies and ticker not in include_companies:
            continue
            
        cik = str(company_data.get('cik_str', '')).zfill(10)
        if cik and cik != '0000000000':
            available_companies.append((ticker, cik))
    
    # Include specific companies first, then sample randomly
    companies_to_process = []
    if include_companies:
        for ticker in include_companies:
            if ticker in sec_companies:
                cik = str(sec_companies[ticker].get('cik_str', '')).zfill(10)
                companies_to_process.append((ticker, cik))
    
    # Fill remaining slots with random sampling
    remaining_slots = sample_size - len(companies_to_process)
    if remaining_slots > 0:
        remaining_companies = [c for c in available_companies if c[0] not in (include_companies or [])]
        random.shuffle(remaining_companies)
        companies_to_process.extend(remaining_companies[:remaining_slots])
    
    return companies_to_process[:sample_size]


def _load_existing_cache(cache_dir: str) -> Dict[str, Any]:
    """Load existing field mapping cache if available."""
    cache_file = os.path.join(cache_dir, 'field_mapping_cache.json')
    return safe_json_read(cache_file) or {}


def _initialize_cache_structure(existing_cache: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the cache data structure."""
    return {
        'canonical_to_sec_mappings': existing_cache.get('canonical_to_sec_mappings', {}),
        'company_mappings': existing_cache.get('company_mappings', {}),
        'field_frequency': existing_cache.get('field_frequency', {}),
        'all_sec_fields': existing_cache.get('all_sec_fields', []),
        'metadata': existing_cache.get('metadata', {})
    }


def _update_cache_with_mappings(
    cache: Dict[str, Any], 
    ticker: str, 
    company_mappings: Dict[str, Set[str]]
) -> None:
    """Update the cache with new company mappings."""
    # Store company-specific mappings
    cache['company_mappings'][ticker] = {k: list(v) for k, v in company_mappings.items()}
    
    # Update canonical to SEC mappings
    for canonical_field, sec_fields in company_mappings.items():
        if canonical_field not in cache['canonical_to_sec_mappings']:
            cache['canonical_to_sec_mappings'][canonical_field] = []
        
        existing_fields = set(cache['canonical_to_sec_mappings'][canonical_field])
        cache['canonical_to_sec_mappings'][canonical_field] = list(existing_fields | sec_fields)
    
    # Update field frequency
    field_frequency = Counter(cache['field_frequency'])
    for sec_fields in company_mappings.values():
        field_frequency.update(sec_fields)
    cache['field_frequency'] = dict(field_frequency)
    
    # Update all SEC fields
    all_sec_fields = set(cache['all_sec_fields'])
    for sec_fields in company_mappings.values():
        all_sec_fields.update(sec_fields)
    cache['all_sec_fields'] = list(all_sec_fields)


def _finalize_cache_metadata(
    cache: Dict[str, Any], 
    processed_count: int, 
    failed_count: int, 
    sample_size: int
) -> Dict[str, Any]:
    """Add final metadata to the cache."""
    companies_analyzed = set(cache['metadata'].get('companies_analyzed', []))
    companies_analyzed.update(cache['company_mappings'].keys())
    
    cache['metadata'] = {
        'created_at': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'companies_analyzed': list(companies_analyzed),
        'total_companies': len(companies_analyzed),
        'sample_size': sample_size,
        'processed_count': processed_count,
        'failed_count': failed_count,
        'canonical_fields_covered': len(cache['canonical_to_sec_mappings']),
        'total_sec_fields': len(cache['all_sec_fields']),
        'mapping_method': 'deterministic_rules',
        'description': 'Deterministic field mapping cache for SEC EDGAR to canonical fields'
    }
    
    return cache
