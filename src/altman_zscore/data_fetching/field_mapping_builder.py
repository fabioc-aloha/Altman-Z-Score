"""
Field Mapping Database Builder

This module analyzes SEC XBRL data from multiple companies to build a comprehensive
mapping database from SEC field names to canonical Altman Z-Score fields.
"""

import logging
import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Optional
import time
import random
import sys
from tqdm import tqdm
from colorama import Fore, Style, init as colorama_init

from src.altman_zscore.api.sec_client import SECClient
from src.altman_zscore.api.openai_client import AzureOpenAIClient
from src.altman_zscore.data_fetching.financials import extract_quarters_from_sec_facts
from src.altman_zscore.computation.constants import MODEL_FIELDS

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Canonical fields we need to map
CANONICAL_FIELDS = [
    "sales",
    "total_assets", 
    "current_assets",
    "current_liabilities",
    "total_liabilities",
    "retained_earnings",
    "ebit",
    "market_value_equity",
    "book_value_equity",
    "working_capital"
]

SEC_CACHE_PATH = "src/altman_zscore/api/cache/sec_company_tickers_cache.json"


def load_sec_company_cache(cache_path=SEC_CACHE_PATH, full=False):
    """
    Load SEC company cache from a JSON file.

    Args:
        cache_path (str): Path to the SEC cache JSON file.
        full (bool): If True, return dict of {ticker: {cik_str, ticker, title}}.
                     If False, return {ticker: cik_str}.

    Returns:
        dict: Company info keyed by ticker.
    """
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if full:
        # Return full company info for each ticker
        return {entry["ticker"]: entry for entry in data.values() if entry.get("ticker") and entry.get("cik_str")}
    # Return just ticker to cik_str mapping
    return {
        entry["ticker"]: str(entry["cik_str"]).zfill(10)
        for entry in data.values() if entry.get("ticker") and entry.get("cik_str")
    }


def sample_companies_from_cache(n=50, exclude_tickers=None, full=False):
    """
    Randomly sample n companies from the SEC cache, optionally excluding tickers.

    Args:
        n (int): Number of companies to sample.
        exclude_tickers (list or set): Tickers to exclude from sampling.
        full (bool): If True, return full company info.

    Returns:
        dict: Sampled companies keyed by ticker.
    """
    all_companies = load_sec_company_cache(full=full)
    if exclude_tickers:
        for t in exclude_tickers:
            all_companies.pop(t, None)
    # Randomly sample up to n companies
    sample = dict(
        random.sample(list(all_companies.items()), min(n, len(all_companies)))
    )
    return sample


def load_existing_field_db(db_path="src/altman_zscore/api/cache/field_mapping_database.json"):
    """
    Load existing field mapping database from a JSON file.

    Args:
        db_path (str): Path to the field mapping database JSON file.

    Returns:
        dict or None: Parsed JSON data as a dictionary, or None if file doesn't exist or is empty.
    """
    import os, json
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_field_db(db, db_path="src/altman_zscore/api/cache/field_mapping_database.json"):
    """
    Save the field mapping database to a JSON file.

    Args:
        db (dict): Database content to save.
        db_path (str): Path to the field mapping database JSON file.
    """
    import json
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, default=str)


def deterministic_field_mapping(company_fields, canonical_fields, sample_values=None, ticker=None):
    """
    Deterministic mapping from canonical fields to SEC fields using a static dictionary and fallback rules.

    Args:
        company_fields (set): Set of field names available for the company.
        canonical_fields (list): List of canonical field names to map to.
        sample_values (dict, optional): Sample values for fields, used for AI mapping context.
        ticker (str, optional): Ticker symbol of the company, used for logging.

    Returns:
        dict: Mapping results, indicating found fields for each canonical field.    """    # Main dictionary for common mappings with extensive fallback alternatives
    mapping_dict = {
        "sales": [
            "Revenues", 
            "RevenueFromContractWithCustomerExcludingAssessedTax", 
            "Revenue",
            "OperatingRevenues",  # Insurance/utility companies
            "PremiumsEarnedNet",  # Insurance companies
            "InterestAndDividendIncomeOperating"  # Financial companies
        ],
        "total_assets": ["Assets"],
        "current_assets": [
            "AssetsCurrent",
            "ShortTermInvestments",  # Investment companies
            "MarketableSecurities"   # Some financial companies
        ],
        "current_liabilities": [
            "LiabilitiesCurrent",
            "AccruedLiabilitiesCurrentAndNoncurrent",  # AFRM pattern
            "AccountsPayableAndAccruedLiabilitiesCurrentAndNoncurrent",  # O, JPM pattern
            "EmployeeRelatedLiabilitiesCurrentAndNoncurrent",  # GS pattern
            "PolicyholderFundsCurrent"  # Insurance companies
        ],
        "total_liabilities": ["Liabilities", "LiabilitiesNoncurrent"],
        "retained_earnings": [
            "RetainedEarningsAccumulatedDeficit",
            "AccumulatedDistributionsInExcessOfNetIncome",  # REITs
            "PartnerCapital"  # Partnerships
        ],
        "ebit": [
            "OperatingIncomeLoss", 
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "UnderwritingIncomeLoss",  # Insurance companies
            "OperatingIncome"  # Alternative naming
        ],
        "market_value_equity": [],  # Not directly available in SEC XBRL
        "book_value_equity": [
            "StockholdersEquity", 
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
            "PartnersCapital",  # Partnerships
            "MembersEquity"     # LLCs
        ],
        "working_capital": [],  # Can be computed as AssetsCurrent - LiabilitiesCurrent
    }
    result = {}
    for canonical in canonical_fields:
        candidates = mapping_dict.get(canonical, [])
        found = None
        # Try direct match
        for c in candidates:
            if c in company_fields:
                found = c
                break
        # Fallback: case-insensitive match
        if not found:
            for f in company_fields:
                if f.lower() == canonical.lower():
                    found = f
                    break        # Fallback: substring match
        if not found:
            for f in company_fields:
                if canonical.replace('_', '').lower() in f.replace('_', '').lower():
                    found = f
                    break        # Special handling for total_liabilities - try to compute or find alternatives
        if not found and canonical == "total_liabilities":
            # Try current + noncurrent liabilities
            if "LiabilitiesCurrent" in company_fields and "LiabilitiesNoncurrent" in company_fields:
                found = "COMPUTED_LiabilitiesCurrent_plus_LiabilitiesNoncurrent"
            # As last resort, compute from balance sheet equation: Assets - Equity = Liabilities
            elif "LiabilitiesAndStockholdersEquity" in company_fields and "StockholdersEquity" in company_fields:
                found = "COMPUTED_LiabilitiesAndStockholdersEquity_minus_StockholdersEquity"
        
        # Special handling for current_liabilities - patterns for financial companies and REITs
        if not found and canonical == "current_liabilities":
            # Pattern for companies with combined current/noncurrent fields
            combined_fields = [f for f in company_fields if "CurrentAndNoncurrent" in f and ("Liabilit" in f or "Payable" in f)]
            if combined_fields:
                found = combined_fields[0]  # Use the first match
        
        # Special handling for current_assets - financial companies often don't classify
        if not found and canonical == "current_assets":
            # For financial companies, sometimes cash equivalents are the main "current" asset
            if "CashAndCashEquivalentsAtCarryingValue" in company_fields and any(bank in (ticker or "") for bank in ["JPM", "GS", "BAC", "WFC", "C"]):
                found = "CashAndCashEquivalentsAtCarryingValue"  # Best proxy for banks
          # Special handling for retained_earnings - REITs have different patterns
        if not found and canonical == "retained_earnings":
            # For REITs, look for accumulated distributions or deficit patterns
            reit_patterns = [f for f in company_fields if "AccumulatedDistributionsInExcessOfNetIncome" in f]
            if not reit_patterns:
                reit_patterns = [f for f in company_fields if "Accumulated" in f and ("Deficit" in f or "Earning" in f or "Income" in f)]
            if reit_patterns:
                found = reit_patterns[0]
        
        # Special handling for working_capital - can be computed as AssetsCurrent - LiabilitiesCurrent
        if not found and canonical == "working_capital":
            if "AssetsCurrent" in company_fields and "LiabilitiesCurrent" in company_fields:
                found = "COMPUTED_AssetsCurrent_minus_LiabilitiesCurrent"
                
        if found:
            result[canonical] = {"FoundField": found}
        else:
            result[canonical] = {"FoundField": None}
    return result


def build_field_database(use_llm=False, companies_input=None, requested_n=None):
    """
    Build a comprehensive field mapping database by analyzing multiple companies.

    Args:
        use_llm (bool): Whether to use LLM-based mapping (Azure OpenAI) or deterministic mapping.
        companies_input (dict, optional): Input companies data, keyed by ticker. If None, samples companies randomly.
        requested_n (int, optional): Number of companies to process, used for progress reporting.

    Returns:
        dict: The constructed field mapping database.
    """    
    # Suppress all logging except errors
    logging.getLogger().setLevel(logging.ERROR)
    colorama_init(autoreset=True)
    if companies_input is None:
        companies_input = load_sec_company_cache(full=True)
    all_companies_full = companies_input
    all_companies = {k: str(v["cik_str"]).zfill(10) for k, v in companies_input.items()}
    # Load existing DB for cumulative build
    output_dir = "src/altman_zscore/api/cache"
    output_file = os.path.join(output_dir, "field_mapping_database.json")
    existing_db = load_existing_field_db(output_file)
    if existing_db:
        all_sec_fields = set(existing_db.get("all_sec_fields", []))
        field_frequency = Counter(existing_db.get("field_frequency", {}))
        company_field_mappings = existing_db.get("company_mappings", {})
        canonical_to_sec_mappings = defaultdict(set, {k: set(v) for k, v in existing_db.get("canonical_to_sec_mappings", {}).items()})
        companies_analyzed = set(existing_db.get("metadata", {}).get("companies_analyzed", []))
    else:
        all_sec_fields = set()
        field_frequency = Counter()
        company_field_mappings = {}
        canonical_to_sec_mappings = defaultdict(set)
        companies_analyzed = set()
    sec_client = SECClient()
    ai_client = AzureOpenAIClient()    # Determine how many new companies to process
    unprocessed_tickers = [t for t in all_companies if t not in companies_analyzed]
    if requested_n is None:
        requested_n = len(unprocessed_tickers)
    
    # Adjust requested_n if we don't have enough unprocessed companies
    actual_companies_to_process = min(requested_n, len(unprocessed_tickers))
    
    # Show info about what we're about to process
    if len(unprocessed_tickers) == 0:
        print("All companies in the sample have already been processed.")
        print(f"Database contains {len(companies_analyzed)} companies.")
        return existing_db if existing_db else {}
    elif len(unprocessed_tickers) < requested_n:
        print(f"Only {len(unprocessed_tickers)} unprocessed companies available (requested {requested_n}).")
        print(f"Will process {actual_companies_to_process} new companies.")
    
    status_dict = {}
    processed_count = 0
    failed_count = 0
    # Track which companies have each SEC field
    sec_field_company_count = defaultdict(set)
    # Main deterministic sampling loop
    with tqdm(total=actual_companies_to_process, unit="company", desc="Processing", ncols=160, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}') as pbar:
        while processed_count < actual_companies_to_process and unprocessed_tickers:
            ticker = random.choice(unprocessed_tickers)
            cik = all_companies[ticker]
            # Fetch company title from SEC cache if possible
            company_title = ticker
            if ticker in all_companies_full and all_companies_full[ticker].get('title'):
                company_title = all_companies_full[ticker]['title']
            # Pad or truncate company title to fixed width (e.g., 50 chars)
            fixed_company_title = (company_title[:47] + '...') if len(company_title) > 50 else company_title.ljust(50)
            pbar.set_postfix_str(fixed_company_title)
            try:                # Fetch SEC facts
                facts = sec_client.get_company_facts(cik)
                if not facts:
                    status_dict[ticker] = "failed"
                    failed_count += 1
                    unprocessed_tickers.remove(ticker)
                    pbar.update(1)  # Update progress even for failed companies
                    continue
                
                # Extract quarters to get field names
                quarters = extract_quarters_from_sec_facts(facts, CANONICAL_FIELDS)
                if not quarters:
                    status_dict[ticker] = "failed"
                    failed_count += 1
                    unprocessed_tickers.remove(ticker)
                    pbar.update(1)  # Update progress even for failed companies
                    continue
                
                # Collect all field names from this company
                company_fields = set()
                sample_values = {}
                
                for quarter in quarters:
                    for field, value in quarter.items():
                        if field not in ["period_end", "field_mapping"] and value is not None:
                            company_fields.add(field)
                            all_sec_fields.add(field)
                            field_frequency[field] += 1
                            sec_field_company_count[field].add(ticker)
                            # Store sample values for context
                            if field not in sample_values:
                                sample_values[field] = value
                
                logger.info(f"{ticker}: Found {len(company_fields)} unique fields")
                
                # Use AI to map fields for this company
                if company_fields:
                    try:
                        if use_llm:
                            ai_mapping = ai_client.suggest_field_mapping(
                                list(company_fields), 
                                CANONICAL_FIELDS, 
                                sample_values, 
                                ticker=ticker
                            )
                        else:
                            ai_mapping = deterministic_field_mapping(
                                company_fields,
                                CANONICAL_FIELDS,
                                sample_values,
                                ticker=ticker
                            )
                          # Store successful mappings
                        company_mappings = {}
                        for canonical_field, mapping_info in ai_mapping.items():
                            if isinstance(mapping_info, dict):
                                sec_field = mapping_info.get("FoundField")
                                if sec_field:
                                    # Handle computed fields and regular fields
                                    if sec_field.startswith("COMPUTED_") or sec_field in company_fields:
                                        company_mappings[canonical_field] = sec_field
                                        canonical_to_sec_mappings[canonical_field].add(sec_field)
                                        logger.info(f"{ticker}: {canonical_field} -> {sec_field}")
                        company_field_mappings[ticker] = {
                            "mappings": company_mappings,
                            "all_fields": sorted(list(company_fields)),
                            "sample_values": {k: str(v) for k, v in sample_values.items() if k in list(sample_values.keys())[:10]}
                        }
                        
                        processed_count += 1
                        companies_analyzed.add(ticker)
                            # If processed successfully:
                        status_dict[ticker] = "success"
                        pbar.update(1)
                    except Exception as e:
                        status_dict[ticker] = "failed"
                        failed_count += 1
                        pbar.update(1)  # Update progress for failed mapping
                else:
                    status_dict[ticker] = "failed"
                    failed_count += 1
                    pbar.update(1)  # Update progress for companies with no fields
            except Exception as e:
                status_dict[ticker] = "failed"
                failed_count += 1
                pbar.update(1)  # Update progress for exception cases
            unprocessed_tickers.remove(ticker)
            time.sleep(0.5)
    
    logger.info(f"Processed {processed_count} companies successfully")
    failed_tickers = [t for t, s in status_dict.items() if s == "failed"]
    if failed_tickers:
        logger.warning(f"Failed companies: {failed_tickers}")
    
    # Analyze patterns and build the final mapping database
    logger.info("Analyzing field patterns...")
    
    # Create priority-ordered mappings based on frequency and consistency
    final_mappings = {}
    for canonical_field in CANONICAL_FIELDS:
        sec_fields = canonical_to_sec_mappings[canonical_field]
        if sec_fields:
            # Sort by frequency (how often this field appears across companies)
            sorted_fields = sorted(sec_fields, key=lambda f: field_frequency[f], reverse=True)
            final_mappings[canonical_field] = sorted_fields
            logger.info(f"{canonical_field}: {len(sorted_fields)} candidate fields, top: {sorted_fields[:3]}")
    
    # Build comprehensive field database
    field_database = {
        "metadata": {
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "companies_analyzed": sorted(list(companies_analyzed)),
            "successful_companies": len(companies_analyzed),
            "failed_companies": failed_tickers,
            "total_unique_fields": len(all_sec_fields),
        },
        "canonical_to_sec_mappings": {k: list(v) for k, v in final_mappings.items()},
        "field_frequency": dict(field_frequency.most_common(100)),  # Top 100 most common fields
        "company_mappings": company_field_mappings,
        "all_sec_fields": sorted(list(all_sec_fields)),
    }
      # Save the database in the API cache directory
    output_dir = "src/altman_zscore/api/cache"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "field_mapping_database.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(field_database, f, indent=2, default=str)
    
    logger.info(f"Field mapping database saved to {output_file}")
      # Create a simplified lookup table for fast access
    simple_lookup = {}
    for canonical_field, sec_fields in final_mappings.items():
        if sec_fields:
            # Primary mapping (most common/reliable)
            simple_lookup[canonical_field] = sec_fields[0]
    
    simple_lookup_file = os.path.join(output_dir, "field_mapping_lookup.json")
    with open(simple_lookup_file, "w", encoding="utf-8") as f:
        json.dump({
            "primary_mappings": simple_lookup,
            "all_mappings": {k: list(v) for k, v in final_mappings.items()},
            "metadata": field_database["metadata"]
        }, f, indent=2)
    
    logger.info(f"Simple lookup table saved to {simple_lookup_file}")
    
    # Generate completeness report
    generate_completeness_report_from_db(os.path.join(output_dir, "field_mapping_database.json"), output_dir)
    
    # Print summary
    print("\n" + "="*60)
    print("FIELD MAPPING DATABASE SUMMARY")
    print("="*60)
    print(f"Companies analyzed: {len(companies_analyzed)}")
    print(f"Total unique SEC fields found: {len(all_sec_fields)}")
    print(f"Canonical fields mapped: {len(final_mappings)}")
    
    print("\nPrimary mappings discovered:")
    for canonical_field in CANONICAL_FIELDS:
        if canonical_field in simple_lookup:
            print(f"  {canonical_field:20} -> {simple_lookup[canonical_field]}")
        else:
            print(f"  {canonical_field:20} -> NOT FOUND")
    
    print(f"\nMost common SEC fields (by number of companies):")
    # Sort by number of companies, descending
    top_fields = sorted(sec_field_company_count.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for field, companies in top_fields:
        print(f"  {field:50} ({len(companies)} companies)")
    
    print("\n" + "="*60)
    
    return field_database


def generate_completeness_report_from_db(db_path, output_dir):
    """
    Generate a completeness report from the full mapping database, not just the last run.

    Args:
        db_path (str): Path to the field mapping database JSON file.
        output_dir (str): Directory to save the completeness report.

    Returns:
        None
    """
    import json
    if not os.path.exists(db_path):
        logger.warning(f"Mapping database not found at {db_path}, cannot generate completeness report.")
        return
    with open(db_path, "r", encoding="utf-8") as f:
        field_database = json.load(f)
    canonical_fields = list(field_database["canonical_to_sec_mappings"].keys())
    company_mappings = field_database["company_mappings"]
    companies = list(company_mappings.keys())
    total_companies = len(companies)    # For each canonical field, count companies with a mapping (including computable fields)
    field_coverage = {}
    for canonical in canonical_fields:
        count = 0
        for c in companies:
            mapping = company_mappings[c]["mappings"].get(canonical)
            available_fields = set(company_mappings[c]["all_fields"])
            
            # Check if field is directly mapped
            if mapping:
                count += 1
            # Check if field can be computed from available fields
            elif can_compute_field(canonical, available_fields):
                count += 1
        field_coverage[canonical] = count    # Companies with incomplete mappings (accounting for computable fields and dependencies)
    incomplete_companies = []
    expected_limitations = []
    
    for c in companies:
        available_fields = set(company_mappings[c]["all_fields"])
        company_title = field_database.get("metadata", {}).get("companies_analyzed", {})
        
        # Get company title if available (from SEC cache or database)
        title = ""
        if isinstance(company_title, list) and c in company_title:
            title = c  # Fallback to ticker
        
        # Categorize company type
        company_type = categorize_company_type(c, available_fields, title)
        
        missing = []
        for f in canonical_fields:
            if should_report_as_missing(f, company_mappings, c):
                missing.append(f)
        
        if missing:
            if company_type in ['bank', 'etf', 'reit', 'insurance', 'limited_data']:
                expected_limitations.append((c, missing, company_type))
            else:
                incomplete_companies.append((c, missing))
    # Canonical fields with no mappings at all
    unmapped_fields = [f for f, n in field_coverage.items() if n == 0]
    # Write markdown report
    report_lines = [
        "# Field Mapping Database Completeness Report (Full Database)",
        "",
        f"**Date:** {field_database['metadata']['created_date']}",
        f"**Companies in database:** {total_companies}",
        "",
        "## Canonical Field Coverage",
        "| Canonical Field | Companies with Mapping | Coverage (%) |",
        "|-----------------|-----------------------|--------------|",
    ]
    for f in canonical_fields:
        n = field_coverage[f]
        pct = 100.0 * n / total_companies if total_companies else 0
        report_lines.append(f"| {f} | {n} | {pct:.1f} |")
    report_lines.append("")
    report_lines.append("## Canonical Fields with No Mappings")
    if unmapped_fields:
        for f in unmapped_fields:
            report_lines.append(f"- {f}")
    else:
        report_lines.append("- None")
    report_lines.append("")
    report_lines.append("## Companies with Incomplete Mappings")
    if incomplete_companies:
        for c, missing in incomplete_companies:
            report_lines.append(f"- **{c}**: missing {', '.join(missing)}")
    else:
        report_lines.append("- None")
    
    report_lines.append("")
    report_lines.append("## Companies with Expected Limitations (by Business Model)")
    if expected_limitations:
        # Group by company type
        by_type = {}
        for c, missing, company_type in expected_limitations:
            if company_type not in by_type:
                by_type[company_type] = []
            by_type[company_type].append((c, missing))
        
        for company_type, companies_list in by_type.items():
            type_names = {
                'bank': 'Banks/Financial Services',
                'etf': 'ETFs/Funds',
                'reit': 'REITs/Real Estate',
                'insurance': 'Insurance Companies',
                'limited_data': 'Companies with Limited Data'
            }
            type_name = type_names.get(company_type, company_type.title())
            report_lines.append(f"### {type_name}")
            for c, missing in companies_list:
                report_lines.append(f"- **{c}**: missing {', '.join(missing)}")
            report_lines.append("")
    else:
        report_lines.append("- None")
    report_lines.append("")
    # Save to file
    report_path = os.path.join(output_dir, "field_mapping_completeness_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    logger.info(f"Completeness report saved to {report_path}")


def lookup_field_mapping(canonical_field: str, cache_dir: str = "src/altman_zscore/api/cache") -> Optional[str]:
    """
    Look up the primary SEC field mapping for a canonical field.

    Args:
        canonical_field: The canonical field name (e.g., 'sales', 'total_assets')
        cache_dir: Directory containing the cached mapping files

    Returns:
        The primary SEC field name, or None if not found
    """
    lookup_file = os.path.join(cache_dir, "field_mapping_lookup.json")
    
    try:
        with open(lookup_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        primary_mappings = data.get("primary_mappings", {})
        return primary_mappings.get(canonical_field)
    
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Could not load field mapping from {lookup_file}: {e}")
        return None


def get_all_mappings(canonical_field: str, cache_dir: str = "src/altman_zscore/api/cache") -> List[str]:
    """
    Get all possible SEC field mappings for a canonical field.

    Args:
        canonical_field: The canonical field name
        cache_dir: Directory containing the cached mapping files

    Returns:
        List of SEC field names, ordered by reliability/frequency
    """
    lookup_file = os.path.join(cache_dir, "field_mapping_lookup.json")
    
    try:
        with open(lookup_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        all_mappings = data.get("all_mappings", {})
        return all_mappings.get(canonical_field, [])
    
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Could not load field mappings from {lookup_file}: {e}")
        return []


def test_field_lookup():
    """Test the field lookup functionality."""
    print("\n" + "="*50)
    print("TESTING FIELD LOOKUP FUNCTIONALITY")
    print("="*50)
    
    # Test primary mappings
    for canonical_field in CANONICAL_FIELDS:
        primary_mapping = lookup_field_mapping(canonical_field)
        all_mappings = get_all_mappings(canonical_field)
        
        print(f"\n{canonical_field}:")
        print(f"  Primary mapping: {primary_mapping}")
        print(f"  All mappings ({len(all_mappings)}): {all_mappings[:3]}{'...' if len(all_mappings) > 3 else ''}")


def robust_json_parse(response_text):
    """
    Robustly parse JSON from LLM response, handling explanations after JSON.
    
    Args:
        response_text: Raw response text from LLM
        
    Returns:
        Parsed JSON object
    """
    import json
    import re
    
    # First, try to parse as-is
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract just the JSON part (everything between first { and matching })
    try:
        # Find the first opening brace
        start = response_text.find('{')
        if start == -1:
            raise ValueError("No JSON object found in response")
        
        # Find the matching closing brace
        brace_count = 0
        end = start
        for i, char in enumerate(response_text[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        # Extract and parse the JSON part
        json_part = response_text[start:end]
        return json.loads(json_part)
    
    except (json.JSONDecodeError, ValueError) as e:
        # If all else fails, try to find JSON-like content and clean it
        try:
            # Look for content between triple quotes or code blocks
            patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
                r'(\{[^}]*\})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            
            raise ValueError(f"Could not extract valid JSON from response: {e}")
        
        except Exception as inner_e:
            raise ValueError(f"JSON parsing failed completely: {inner_e}")


def get_companies_for_run(tickers_arg, sample_n, exclude_tickers):
    """
    Get companies for this run, either by explicit tickers or by random sampling.

    Args:
        tickers_arg (str): Comma-separated tickers string, or None.
        sample_n (int): Number of companies to sample if tickers_arg is None.
        exclude_tickers (list or set): Tickers to exclude from selection.

    Returns:
        dict: {ticker: {cik_str, ticker, title, ...}} for selected companies.
    """
    all_companies_full = load_sec_company_cache(full=True)
    if exclude_tickers:
        for t in exclude_tickers:
            all_companies_full.pop(t, None)
    if tickers_arg:
        # User provided tickers: filter and warn if any missing
        tickers = [t.strip().upper() for t in tickers_arg.split(",") if t.strip()]
        selected = {t: all_companies_full[t] for t in tickers if t in all_companies_full}
        missing = [t for t in tickers if t not in all_companies_full]
        if missing:
            logger.warning(
                f"Tickers not found in SEC cache and will be skipped: {missing}"
            )
        return selected
    else:
        # Random sample from all available companies
        sample = dict(
            random.sample(
                list(all_companies_full.items()), min(sample_n, len(all_companies_full))
            )
        )
        return sample


def can_compute_field(canonical_field, available_fields):
    """
    Check if a canonical field can be computed from available fields.
    
    Args:
        canonical_field (str): The canonical field name
        available_fields (set): Set of available field names for the company
        
    Returns:
        bool: True if the field can be computed, False otherwise
    """
    # Working capital can be computed if we have both current assets and current liabilities
    if canonical_field == "working_capital":
        return "AssetsCurrent" in available_fields and "LiabilitiesCurrent" in available_fields
    
    # Total liabilities can be computed in multiple ways
    if canonical_field == "total_liabilities":
        # Method 1: Current + Noncurrent liabilities
        if "LiabilitiesCurrent" in available_fields and "LiabilitiesNoncurrent" in available_fields:
            return True
        # Method 2: Balance sheet equation (Assets - Equity = Liabilities)
        if "LiabilitiesAndStockholdersEquity" in available_fields and "StockholdersEquity" in available_fields:
            return True
    
    # Add other computable fields as needed
    return False


def get_field_dependencies(canonical_field):
    """
    Get the fields that a canonical field depends on for computation.
    
    Args:
        canonical_field (str): The canonical field name
        
    Returns:
        list: List of field names that this field depends on, empty if not computable
    """
    dependencies = {
        "working_capital": ["current_assets", "current_liabilities"],
        "total_liabilities": [],  # Has multiple computation methods, no single dependency
    }
    return dependencies.get(canonical_field, [])


def should_report_as_missing(canonical_field, company_mappings, company_name):
    """
    Determine if a field should be reported as missing for a company.
    A field should only be reported as missing if:
    1. It's not directly mapped AND
    2. It cannot be computed from available fields AND  
    3. If it's a computed field, its dependencies are available
    
    Args:
        canonical_field (str): The canonical field name
        company_mappings (dict): Company mappings data
        company_name (str): Company ticker/name
        
    Returns:
        bool: True if field should be reported as missing
    """
    mapping = company_mappings[company_name]["mappings"].get(canonical_field)
    available_fields = set(company_mappings[company_name]["all_fields"])
    
    # If directly mapped, not missing
    if mapping:
        return False
    
    # If can be computed, not missing
    if can_compute_field(canonical_field, available_fields):
        return False
    
    # For computed fields like working_capital, don't report as missing if dependencies are also missing
    dependencies = get_field_dependencies(canonical_field)
    if dependencies:
        # Check if ALL dependencies are missing (mapped or computable)
        missing_dependencies = []
        for dep in dependencies:
            dep_mapping = company_mappings[company_name]["mappings"].get(dep)
            if not dep_mapping and not can_compute_field(dep, available_fields):
                missing_dependencies.append(dep)
        
        # If any dependency is missing, don't report the computed field as missing
        if missing_dependencies:
            return False
    
    # Field is truly missing and cannot be computed
    return True


def categorize_company_type(ticker, available_fields, company_title=""):
    """
    Categorize company type based on ticker patterns and available fields.
    
    Args:
        ticker (str): Company ticker symbol
        available_fields (set): Set of available field names
        company_title (str): Company title/name
        
    Returns:
        str: Company category ('bank', 'etf', 'reit', 'insurance', 'regular', 'limited_data')
    """
    ticker_upper = ticker.upper()
    title_upper = company_title.upper()
    
    # Very limited data companies
    if len(available_fields) < 50:
        return 'limited_data'
    
    # ETF/Fund patterns
    etf_patterns = ['SPDR', 'SPY', 'QQQ', 'VTI', 'IWM', 'EFA', 'EEM', 'TLT', 'GLD', 'SLV']
    fund_keywords = ['ETF', 'FUND', 'TRUST', 'INDEX', 'SPDR', 'ISHARES', 'VANGUARD', 'INVESCO']
    
    if (any(pattern in ticker_upper for pattern in etf_patterns) or
        any(keyword in title_upper for keyword in fund_keywords) or
        ticker_upper.endswith(('F', 'X')) and len(ticker) <= 5):
        return 'etf'
    
    # Bank/Financial patterns
    bank_tickers = ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'STT', 'BK', 'SCHW', 'USB', 'PNC', 'TFC', 'COF']
    bank_keywords = ['BANK', 'FINANCIAL', 'BANCORP', 'BANCSHARES', 'TRUST COMPANY']
    
    if (ticker_upper in bank_tickers or
        any(keyword in title_upper for keyword in bank_keywords)):
        return 'bank'
    
    # REIT patterns
    reit_tickers = ['O', 'REALTY', 'EXR', 'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'AVB']
    reit_keywords = ['REIT', 'REALTY', 'REAL ESTATE', 'PROPERTIES', 'STORAGE']
    preferred_patterns = ['-P', '-PR']
    
    if (ticker_upper in reit_tickers or
        any(keyword in title_upper for keyword in reit_keywords) or
        any(pattern in ticker_upper for pattern in preferred_patterns)):
        return 'reit'
    
    # Insurance patterns
    insurance_keywords = ['INSURANCE', 'LIFE', 'CASUALTY', 'MUTUAL', 'ASSURANCE']
    insurance_fields = ['PremiumsEarnedNet', 'PolicyholderFunds', 'InsuranceReserves']
    
    if (any(keyword in title_upper for keyword in insurance_keywords) or
        any(field in available_fields for field in insurance_fields)):
        return 'insurance'
    
    return 'regular'
