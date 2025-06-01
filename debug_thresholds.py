#!/usr/bin/env python3
"""
Debug script to test threshold retrieval for different models
"""

print("Starting debug script...")

try:
    import sys
    sys.path.insert(0, 'src')
    print("Added src to path")
    
    from altman_zscore.computation.constants import Z_SCORE_THRESHOLDS
    print("Imported Z_SCORE_THRESHOLDS")
    
    print("=== Z_SCORE_THRESHOLDS from constants.py ===")
    for model, thresholds in Z_SCORE_THRESHOLDS.items():
        print(f"{model}: {thresholds}")
    
    from altman_zscore.plotting import get_zscore_thresholds
    print("Imported get_zscore_thresholds")
    
    print("\n=== Testing specific models ===")
    # Test the specific models mentioned in the issue
    original_result = get_zscore_thresholds("original")
    service_result = get_zscore_thresholds("service")
    
    print(f"Original model thresholds: {original_result}")
    print(f"Service model thresholds: {service_result}")
    
    print(f"\nOriginal - Distress: {original_result['distress_zone']}, Safe: {original_result['safe_zone']}")
    print(f"Service - Distress: {service_result['distress_zone']}, Safe: {service_result['safe_zone']}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
