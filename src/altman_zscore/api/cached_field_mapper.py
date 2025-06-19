#!/usr/bin/env python3
"""
Cached Field Mapper - Fast SEC field to canonical field mapping using pre-built cache.

This module provides cached field mapping functionality to eliminate the need for LLM calls
when mapping SEC GAAP concepts to canonical Z-Score fields.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Set
from decimal import Decimal

logger = logging.getLogger(__name__)


class CachedFieldMapper:
    """
    Fast field mapper using pre-built cache of SEC field mappings.
    
    This replaces the AI/LLM-based field mapping with a fast lookup table.
    """
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize the cached field mapper.
        
        Args:
            cache_dir: Directory containing cached mapping files. 
                      Defaults to src/altman_zscore/api/cache
        """
        if cache_dir is None:
            # Default to the cache directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            cache_dir = os.path.join(current_dir, "cache")
        
        self.cache_dir = cache_dir
        self.lookup_file = os.path.join(cache_dir, "field_mapping_lookup.json")
        self.database_file = os.path.join(cache_dir, "field_mapping_database.json")
        
        self._lookup_data = None
        self._database_data = None
        
        # Load the cache on initialization
        self._load_cache()
    
    def _load_cache(self):
        """Load the cached mapping data."""
        try:
            with open(self.lookup_file, "r", encoding="utf-8") as f:
                self._lookup_data = json.load(f)
            logger.debug(f"Loaded field mapping lookup from {self.lookup_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load lookup cache from {self.lookup_file}: {e}")
            self._lookup_data = {"primary_mappings": {}, "all_mappings": {}}
        
        try:
            with open(self.database_file, "r", encoding="utf-8") as f:
                self._database_data = json.load(f)
            logger.debug(f"Loaded field mapping database from {self.database_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load database cache from {self.database_file}: {e}")
            self._database_data = {}
    
    def get_primary_mapping(self, canonical_field: str) -> Optional[str]:
        """
        Get the primary (most reliable) SEC field mapping for a canonical field.
        
        Args:
            canonical_field: The canonical field name (e.g., 'sales', 'total_assets')
            
        Returns:
            The primary SEC field name, or None if not found
        """
        if not self._lookup_data:
            return None
        
        primary_mappings = self._lookup_data.get("primary_mappings", {})
        return primary_mappings.get(canonical_field)
    
    def get_all_mappings(self, canonical_field: str) -> List[str]:
        """
        Get all possible SEC field mappings for a canonical field, ordered by reliability.
        
        Args:
            canonical_field: The canonical field name
            
        Returns:
            List of SEC field names, ordered by reliability/frequency
        """
        if not self._lookup_data:
            return []
        
        all_mappings = self._lookup_data.get("all_mappings", {})
        return all_mappings.get(canonical_field, [])
    
    def map_sec_quarter_to_canonical(self, sec_quarter: Dict, canonical_fields: List[str], ticker: str = None) -> Dict:
        """
        Map a SEC quarterly data dict to canonical fields using cached mappings.
        
        Args:
            sec_quarter: Dictionary containing SEC field data for one quarter
            canonical_fields: List of canonical field names to map
            ticker: Optional ticker symbol for company-specific mappings
            
        Returns:
            Dictionary with canonical fields mapped and metadata
        """
        mapped_quarter = {"period_end": sec_quarter.get("period_end")}
        field_mapping = {}
        missing_fields = []
        
        # Try to get company-specific mappings first if ticker is provided
        company_mappings = None
        if ticker and self._database_data:
            company_mappings = self._database_data.get("company_mappings", {}).get(ticker, {}).get("mappings", {})
        
        for canonical_field in canonical_fields:
            value = None
            mapped_sec_field = None
            
            # Try company-specific mapping first if available
            if company_mappings and canonical_field in company_mappings:
                company_field = company_mappings[canonical_field]
                if company_field and company_field in sec_quarter:
                    raw_value = sec_quarter[company_field]
                    if raw_value is not None:
                        value = self._safe_to_decimal(str(raw_value))
                        mapped_sec_field = company_field
                        logger.debug(f"Used company-specific mapping: {canonical_field} -> {company_field}")
            
            # Try primary mapping if company-specific failed
            if value is None:
                primary_field = self.get_primary_mapping(canonical_field)
                if primary_field and primary_field in sec_quarter:
                    raw_value = sec_quarter[primary_field]
                    if raw_value is not None:
                        value = self._safe_to_decimal(str(raw_value))
                        mapped_sec_field = primary_field
            
            # If primary mapping failed, try all alternative mappings
            if value is None:
                for alternative_field in self.get_all_mappings(canonical_field):
                    if alternative_field in sec_quarter:
                        raw_value = sec_quarter[alternative_field]
                        if raw_value is not None:
                            value = self._safe_to_decimal(str(raw_value))
                            if value is not None:
                                mapped_sec_field = alternative_field
                                logger.debug(f"Used alternative mapping: {canonical_field} -> {alternative_field}")
                                break
            
            # Special handling for calculated fields
            if value is None and canonical_field == "working_capital":
                # Calculate working_capital = current_assets - current_liabilities
                current_assets = mapped_quarter.get("current_assets")
                current_liabilities = mapped_quarter.get("current_liabilities")
                if current_assets is not None and current_liabilities is not None:
                    value = current_assets - current_liabilities
                    mapped_sec_field = "Calculated: current_assets - current_liabilities"
            
            # Store the result
            if value is not None and value not in [0, Decimal("0")]:
                mapped_quarter[canonical_field] = value
                field_mapping[canonical_field] = mapped_sec_field
            else:
                missing_fields.append(canonical_field)
        
        # Add metadata
        if field_mapping:
            mapped_quarter["field_mapping"] = json.dumps(field_mapping, default=str)
        
        # Log missing fields for debugging
        if missing_fields:
            logger.debug(f"Missing fields for {sec_quarter.get('period_end', 'unknown')}: {missing_fields}")
        
        return mapped_quarter
    
    def _safe_to_decimal(self, value_str: str) -> Optional[Decimal]:
        """
        Safely convert a string value to Decimal.
        
        Args:
            value_str: String representation of a number
            
        Returns:
            Decimal value or None if conversion fails
        """
        try:
            # Handle scientific notation and various formats
            if value_str.lower() in ['none', 'null', '', 'n/a', 'na']:
                return None
            
            # Remove any currency symbols or commas
            cleaned = str(value_str).replace(',', '').replace('$', '').strip()
            
            if not cleaned:
                return None
            
            decimal_value = Decimal(cleaned)
              # Return None for zero values as they're typically not useful for Z-Score
            if decimal_value == 0:
                return None
                
            return decimal_value
            
        except (ValueError, TypeError, Exception):
            logger.debug(f"Could not convert '{value_str}' to Decimal")
            return None
    
    def apply_cached_mapping(self, sec_quarters: List[Dict], canonical_fields: List[str], ticker: str = None) -> List[Dict]:
        """
        Apply cached field mapping to a list of SEC quarters.
        
        This is a drop-in replacement for the AI-powered apply_ai_field_mapping function.
        
        Args:
            sec_quarters: List of quarterly data from SEC facts
            canonical_fields: Required canonical field names
            ticker: Optional ticker symbol for company-specific mappings
            
        Returns:
            List of quarters with mapped canonical fields
        """
        if not sec_quarters:
            return []
        
        if ticker:
            logger.info(f"Applying cached field mapping to {len(sec_quarters)} quarters for {ticker}")
        else:
            logger.info(f"Applying cached field mapping to {len(sec_quarters)} quarters")
        
        mapped_quarters = []
        for quarter in sec_quarters:
            mapped_quarter = self.map_sec_quarter_to_canonical(quarter, canonical_fields, ticker)
            
            # Only include quarters that have some canonical data (not just period_end)
            if len(mapped_quarter) > 1:  # More than just period_end
                mapped_quarters.append(mapped_quarter)
        
        logger.info(f"Successfully mapped {len(mapped_quarters)} quarters with cached mappings")
        return mapped_quarters
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the cached mappings.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self._database_data:
            return {}
        
        metadata = self._database_data.get("metadata", {})
        primary_mappings = self._lookup_data.get("primary_mappings", {}) if self._lookup_data else {}
        all_mappings = self._lookup_data.get("all_mappings", {}) if self._lookup_data else {}
        
        return {
            "cache_build_date": metadata.get("build_date"),
            "companies_analyzed": metadata.get("companies_analyzed", 0),
            "total_sec_fields": metadata.get("total_sec_fields", 0),
            "canonical_fields_with_primary_mapping": len(primary_mappings),
            "canonical_fields_with_any_mapping": len([k for k, v in all_mappings.items() if v]),
            "cache_files": {
                "lookup_file": self.lookup_file,
                "database_file": self.database_file,
                "lookup_exists": os.path.exists(self.lookup_file),
                "database_exists": os.path.exists(self.database_file)
            }
        }


# Convenience functions for easy integration
def get_cached_field_mapping(canonical_field: str, cache_dir: str = None) -> Optional[str]:
    """
    Quick lookup for a single canonical field mapping.
    
    Args:
        canonical_field: The canonical field name
        cache_dir: Cache directory (optional)
        
    Returns:
        Primary SEC field name or None
    """
    mapper = CachedFieldMapper(cache_dir)
    return mapper.get_primary_mapping(canonical_field)


def apply_cached_field_mapping(sec_quarters: List[Dict], canonical_fields: List[str], 
                               cache_dir: str = None, ticker: str = None) -> List[Dict]:
    """
    Apply cached field mapping to SEC quarters - drop-in replacement for AI mapping.
    
    Args:
        sec_quarters: List of quarterly SEC data
        canonical_fields: List of canonical field names to map
        cache_dir: Cache directory (optional)
        ticker: Ticker symbol for company-specific mappings (optional)
        
    Returns:
        List of quarters with mapped canonical fields
    """
    mapper = CachedFieldMapper(cache_dir)
    return mapper.apply_cached_mapping(sec_quarters, canonical_fields, ticker)
