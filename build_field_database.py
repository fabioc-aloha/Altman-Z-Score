#!/usr/bin/env python3
"""
Field Mapping Database Builder CLI

This script serves as a minimal bootstrapper for building the SEC field mapping database.
The main logic is located in src/altman_zscore/data_fetching/field_mapping_builder.py
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Configure logging to ERROR level
logging.basicConfig(level=logging.ERROR)

# Check if SEC cache exists before importing
SEC_CACHE_PATH = "src/altman_zscore/api/cache/sec_company_tickers_cache.json"
if not os.path.exists(SEC_CACHE_PATH):
    print(f"ERROR: SEC company cache not found at {SEC_CACHE_PATH}. Please generate or download it before running this script.")
    sys.exit(1)

# Import the main functionality from the data_fetching module
from src.altman_zscore.data_fetching.field_mapping_builder import (
    build_field_database,
    test_field_lookup,
    get_companies_for_run
)

# Import SEC cache functions
from src.altman_zscore.company.cik_cache import get_cache_stats, refresh_cache


def check_and_update_sec_cache():
    """
    Check the status of the SEC cache and update it if needed.
    
    Returns:
        bool: True if cache is ready for use, False if there are issues
    """
    try:
        print("Checking SEC company cache status...")
        cache_stats = get_cache_stats()
        
        # Check if cache exists
        if not cache_stats.get('cache_file_exists', False):
            print("❌ SEC cache file does not exist. Attempting to download...")
            if refresh_cache():
                print("✅ Successfully downloaded SEC company cache.")
                return True
            else:
                print("❌ Failed to download SEC cache. Cannot proceed.")
                return False
        
        # Check cache freshness
        is_fresh = cache_stats.get('is_fresh', False)
        total_entries = cache_stats.get('total_entries', 0)
        last_updated = cache_stats.get('metadata', {}).get('last_updated', 'unknown')
        
        if is_fresh:
            print(f"✅ SEC cache is fresh with {total_entries:,} companies (last updated: {last_updated}).")
            return True
        else:
            print(f"⚠️  SEC cache is stale with {total_entries:,} companies (last updated: {last_updated}).")
            print("Attempting to update cache...")
            
            if refresh_cache():
                print("✅ Successfully updated SEC company cache.")
                # Get updated stats
                updated_stats = get_cache_stats()
                updated_entries = updated_stats.get('total_entries', 0)
                updated_time = updated_stats.get('metadata', {}).get('last_updated', 'unknown')
                print(f"   New cache has {updated_entries:,} companies (updated: {updated_time}).")
                return True
            else:
                print("⚠️  Failed to update cache, but will continue with stale cache.")
                print(f"   Using existing cache with {total_entries:,} companies.")
                return True  # Still usable, just stale
                
    except Exception as e:
        print(f"❌ Error checking/updating SEC cache: {e}")
        print("Will attempt to proceed with existing cache...")
        return True  # Try to continue anyway


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Build SEC field mapping database")
    parser.add_argument("--test", action="store_true", help="Test the field lookup functionality")
    parser.add_argument("--sample", metavar="N", type=int, help="Sample N random companies from SEC cache (alternative to providing tickers)")
    parser.add_argument("--deterministic", action="store_true", default=True, help="Use deterministic (rule-based) mapping [default]")
    parser.add_argument("--LLM", action="store_true", help="Use LLM-based mapping instead of deterministic")
    parser.add_argument("--force-cache-update", action="store_true", help="Force update of SEC company cache before building database")
    parser.add_argument("tickers", nargs="*", help="List of tickers to process (positional arguments)")
    
    # If no arguments provided, show help and exit
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()

    try:
        if args.test:
            test_field_lookup()
        else:            # Force cache update if requested
            if args.force_cache_update:
                print("Force updating SEC company cache...")
                if refresh_cache():
                    print("✅ Successfully updated SEC company cache.")
                    # Get updated stats to show results
                    updated_stats = get_cache_stats()
                    updated_entries = updated_stats.get('total_entries', 0)
                    updated_time = updated_stats.get('metadata', {}).get('last_updated', 'unknown')
                    print(f"   Cache now has {updated_entries:,} companies (updated: {updated_time}).")
                    print("✅ Cache refresh complete.")
                    sys.exit(0)
                else:
                    print("❌ Failed to force update SEC cache.")
                    sys.exit(1)
            
            # Check and update SEC cache if needed before proceeding
            if not check_and_update_sec_cache():
                print("❌ SEC cache is not available. Cannot proceed with field database building.")
                sys.exit(1)
            
            print()  # Add spacing after cache check
            
            # Determine companies for this run
            tickers_arg = ",".join(args.tickers) if args.tickers else None
            sample_n = args.sample or 50  # Default to 50 companies
            exclude_tickers = []
            
            companies_input = get_companies_for_run(tickers_arg, sample_n, exclude_tickers)
            requested_n = len(companies_input)
            
            print(f"Building field mapping database with {requested_n} companies...")
            build_field_database(
                use_llm=args.LLM, 
                companies_input=companies_input, 
                requested_n=requested_n
            )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
