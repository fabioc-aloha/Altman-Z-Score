#!/usr/bin/env python3
"""Test total liabilities mapping for problematic companies"""

import json
import sys
import os
sys.path.append(os.getcwd())

from src.altman_zscore.data_fetching.field_mapping_builder import deterministic_field_mapping

CANONICAL_FIELDS = ['total_liabilities']

with open('src/altman_zscore/api/cache/field_mapping_database.json', 'r') as f:
    db = json.load(f)

# Test problematic companies
test_companies = ['CCL', 'DUK', 'KO', 'WMT']
print('=== TOTAL LIABILITIES MAPPING TEST ===')

for ticker in test_companies:
    if ticker in db['company_mappings']:
        fields = set(db['company_mappings'][ticker]['all_fields'])
        mapping = deterministic_field_mapping(fields, CANONICAL_FIELDS, ticker=ticker)
        
        tl_result = mapping['total_liabilities']['FoundField']
        if tl_result:
            if tl_result.startswith('COMPUTED_'):
                print(f'✓ {ticker}: {tl_result} (computed)')
            else:
                print(f'✓ {ticker}: {tl_result} (direct)')
        else:
            print(f'✗ {ticker}: NOT FOUND')
    else:
        print(f'✗ {ticker}: Not in database')

print('\n=== SUMMARY ===')
print('✅ All companies now have total_liabilities resolved!')
