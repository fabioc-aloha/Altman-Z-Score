#!/usr/bin/env python3
"""Final verification of field mapping improvements"""

import json
import sys
import os
sys.path.append(os.getcwd())

from src.altman_zscore.data_fetching.field_mapping_builder import deterministic_field_mapping

CANONICAL_FIELDS = ['sales', 'total_assets', 'current_assets', 'current_liabilities', 'total_liabilities', 'retained_earnings', 'ebit', 'market_value_equity', 'book_value_equity', 'working_capital']

with open('src/altman_zscore/api/cache/field_mapping_database.json', 'r') as f:
    db = json.load(f)

print("=== FIELD MAPPING IMPROVEMENT VERIFICATION ===\n")

# The companies that were problematic before
problematic_companies = ['CCL', 'AFRM', 'O', 'GS', 'DUK', 'KO', 'WMT', 'JPM']

print("Companies that had incomplete mappings BEFORE improvements:")
original_issues = {
    'CCL': ['total_liabilities'],
    'AFRM': ['current_liabilities'], 
    'O': ['current_liabilities', 'retained_earnings'],
    'GS': ['current_assets', 'current_liabilities'],
    'DUK': ['total_liabilities'],
    'KO': ['total_liabilities'], 
    'WMT': ['total_liabilities'],
    'JPM': ['current_assets', 'current_liabilities']
}

total_issues_before = sum(len(issues) for issues in original_issues.values())
total_companies = len(problematic_companies)

print(f"- {total_companies} companies with issues")
print(f"- {total_issues_before} total missing field mappings")

print(f"\nResults AFTER improvements:")
issues_resolved = 0
companies_available = 0

for ticker in problematic_companies:
    if ticker in db['company_mappings']:
        companies_available += 1
        fields = set(db['company_mappings'][ticker]['all_fields'])
        mapping = deterministic_field_mapping(fields, CANONICAL_FIELDS, ticker=ticker)
        
        was_missing = original_issues[ticker]
        now_resolved = []
        
        for field in was_missing:
            found = mapping[field].get('FoundField')
            if found:
                now_resolved.append(field)
                issues_resolved += 1
        
        if now_resolved:
            print(f"✓ {ticker}: Fixed {len(now_resolved)}/{len(was_missing)} issues - {now_resolved}")

print(f"\n=== SUMMARY ===")
print(f"- Companies tested: {companies_available}/{total_companies}")
print(f"- Issues resolved: {issues_resolved}/{total_issues_before} ({issues_resolved/total_issues_before*100:.1f}%)")

if issues_resolved == total_issues_before:
    print("🎉 ALL ISSUES RESOLVED!")
else:
    remaining = total_issues_before - issues_resolved
    print(f"- Remaining issues: {remaining}")

print(f"\nImprovements made:")
print(f"- Enhanced field alternatives for current_liabilities")
print(f"- Added computed fields for total_liabilities")
print(f"- Special handling for financial companies (banks)")
print(f"- Special handling for REITs")
print(f"- Smart fallback patterns for edge cases")
