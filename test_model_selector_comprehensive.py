"""
Test Model Selector - Comprehensive Validation

This test validates that the model selector can reliably pick the correct
Z-Score model for a wide variety of ticker symbols across different industries.

Test Categories:
1. Financial Companies (should use 'financial' model)
2. Technology Companies (should use 'original' model)
3. Manufacturing Companies (should use 'original' model)
4. Service Companies (should use 'service' model)
5. Retail Companies (should use 'retail' model)
6. Emerging Market Companies (should use 'emerging' model)
7. Private/No Market Data Companies (should use 'private' model)
"""

import json
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

# Import the model selector and required types
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from altman_zscore.models.data_models import MergedFinancialData
from altman_zscore.layers.zscore_calculation.model_selector import ModelSelector, CompanyType


@dataclass
class TestCase:
    """Test case for model selector validation."""
    ticker: str
    company_name: str
    sector: str
    industry: str
    expected_model: str
    expected_company_type: CompanyType
    description: str
    country: str = "US"
    market_cap: float = 1000000000  # Default 1B market cap
    
    
def create_test_data(test_case: TestCase) -> MergedFinancialData:
    """Create MergedFinancialData for testing based on test case."""
    
    # Create company profile data
    profile_data = {
        'companyName': test_case.company_name,
        'sector': test_case.sector,
        'industry': test_case.industry,
        'country': test_case.country,
        'description': f"{test_case.company_name} is a leading company in {test_case.industry}"
    }
    
    raw_fmp_data = {
        'profile': [profile_data]
    }
    
    # Set market data based on expected model
    market_cap = None if test_case.expected_model == 'private' else test_case.market_cap
    
    return MergedFinancialData(
        ticker=test_case.ticker,
        timestamp="2024-01-01",
        market_cap=market_cap,
        raw_fmp_data=raw_fmp_data,
        current_price=100.0 if market_cap else None,
        shares_outstanding=market_cap / 100.0 if market_cap else None
    )


def get_test_cases() -> List[TestCase]:
    """Get comprehensive test cases covering all model types."""
    
    return [
        # Financial Companies (should use 'financial' model)
        TestCase("JPM", "JPMorgan Chase & Co", "Financial Services", "Banks", 
                "financial", CompanyType.PUBLIC_FINANCIAL, "Major US bank"),
        TestCase("BAC", "Bank of America Corp", "Financial Services", "Banks", 
                "financial", CompanyType.PUBLIC_FINANCIAL, "Major US bank"),
        TestCase("WFC", "Wells Fargo & Company", "Financial Services", "Banks", 
                "financial", CompanyType.PUBLIC_FINANCIAL, "Major US bank"),
        TestCase("SCHW", "Charles Schwab Corp", "Financial Services", "Investment Banking", 
                "financial", CompanyType.PUBLIC_FINANCIAL, "Investment services"),
        TestCase("AIG", "American International Group", "Financial Services", "Insurance", 
                "financial", CompanyType.PUBLIC_FINANCIAL, "Insurance company"),
        TestCase("BRK-A", "Berkshire Hathaway Inc", "Financial Services", "Insurance", 
                "financial", CompanyType.PUBLIC_FINANCIAL, "Insurance/Investment company"),
        
        # Technology Companies (should use 'original' model)
        TestCase("MSFT", "Microsoft Corporation", "Technology", "Software", 
                "original", CompanyType.PUBLIC_TECH, "Software technology company"),
        TestCase("AAPL", "Apple Inc", "Technology", "Consumer Electronics", 
                "original", CompanyType.PUBLIC_TECH, "Technology hardware company"),
        TestCase("GOOGL", "Alphabet Inc", "Technology", "Internet Services", 
                "original", CompanyType.PUBLIC_TECH, "Internet technology company"),
        TestCase("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors", 
                "original", CompanyType.PUBLIC_TECH, "Semiconductor technology company"),
        TestCase("CRM", "Salesforce Inc", "Technology", "Software", 
                "original", CompanyType.PUBLIC_TECH, "Cloud software company"),
        TestCase("ADBE", "Adobe Inc", "Technology", "Software", 
                "original", CompanyType.PUBLIC_TECH, "Software technology company"),
        
        # Manufacturing Companies (should use 'original' model)
        TestCase("GE", "General Electric Company", "Industrials", "Industrial Equipment", 
                "original", CompanyType.PUBLIC_MANUFACTURING, "Industrial manufacturing"),
        TestCase("CAT", "Caterpillar Inc", "Industrials", "Heavy Machinery", 
                "original", CompanyType.PUBLIC_MANUFACTURING, "Heavy equipment manufacturer"),
        TestCase("BA", "Boeing Company", "Industrials", "Aerospace & Defense", 
                "original", CompanyType.PUBLIC_MANUFACTURING, "Aerospace manufacturer"),
        TestCase("F", "Ford Motor Company", "Consumer Cyclical", "Auto Manufacturers", 
                "original", CompanyType.PUBLIC_MANUFACTURING, "Automotive manufacturer"),
        TestCase("MMM", "3M Company", "Industrials", "Diversified Manufacturing", 
                "original", CompanyType.PUBLIC_MANUFACTURING, "Diversified manufacturer"),
        TestCase("HON", "Honeywell International", "Industrials", "Industrial Equipment", 
                "original", CompanyType.PUBLIC_MANUFACTURING, "Industrial technology"),
        
        # Service Companies (should use 'service' model)
        TestCase("UNH", "UnitedHealth Group", "Healthcare", "Healthcare Services", 
                "service", CompanyType.PUBLIC_SERVICE, "Healthcare services company"),
        TestCase("JNJ", "Johnson & Johnson", "Healthcare", "Drug Manufacturers", 
                "service", CompanyType.PUBLIC_SERVICE, "Healthcare and pharmaceutical services"),
        TestCase("VZ", "Verizon Communications", "Communication Services", "Telecom Services", 
                "service", CompanyType.PUBLIC_SERVICE, "Telecommunications services"),
        TestCase("T", "AT&T Inc", "Communication Services", "Telecom Services", 
                "service", CompanyType.PUBLIC_SERVICE, "Telecommunications services"),
        TestCase("NEE", "NextEra Energy", "Utilities", "Electric Utilities", 
                "service", CompanyType.PUBLIC_SERVICE, "Utility services company"),
        TestCase("SO", "Southern Company", "Utilities", "Electric Utilities", 
                "service", CompanyType.PUBLIC_SERVICE, "Electric utility services"),
        
        # Retail Companies (should use 'retail' model)
        TestCase("AMZN", "Amazon.com Inc", "Consumer Cyclical", "Internet Retail", 
                "retail", CompanyType.PUBLIC_RETAIL, "E-commerce retail company"),
        TestCase("WMT", "Walmart Inc", "Consumer Defensive", "Discount Stores", 
                "retail", CompanyType.PUBLIC_RETAIL, "Retail discount stores"),
        TestCase("TGT", "Target Corporation", "Consumer Cyclical", "Discount Stores", 
                "retail", CompanyType.PUBLIC_RETAIL, "Retail discount stores"),
        TestCase("HD", "Home Depot Inc", "Consumer Cyclical", "Home Improvement Retail", 
                "retail", CompanyType.PUBLIC_RETAIL, "Home improvement retail"),
        TestCase("COST", "Costco Wholesale Corp", "Consumer Defensive", "Discount Stores", 
                "retail", CompanyType.PUBLIC_RETAIL, "Warehouse retail stores"),
        TestCase("NKE", "Nike Inc", "Consumer Cyclical", "Footwear & Accessories", 
                "retail", CompanyType.PUBLIC_RETAIL, "Athletic retail and apparel"),
        
        # Emerging Market Companies (should use 'emerging' model)
        TestCase("BABA", "Alibaba Group", "Technology", "Internet Services", 
                "emerging", CompanyType.EMERGING_MARKET, "Chinese e-commerce company", "CHINA"),
        TestCase("TSM", "Taiwan Semiconductor", "Technology", "Semiconductors", 
                "emerging", CompanyType.EMERGING_MARKET, "Taiwanese semiconductor company", "TAIWAN"),
        TestCase("VALE", "Vale SA", "Basic Materials", "Iron & Steel", 
                "emerging", CompanyType.EMERGING_MARKET, "Brazilian mining company", "BRAZIL"),
        TestCase("TENCENT", "Tencent Holdings", "Technology", "Internet Services", 
                "emerging", CompanyType.EMERGING_MARKET, "Chinese technology company", "CHINA"),
        
        # Financial companies from emerging markets (should still use 'financial' model)
        TestCase("ITUB", "Itau Unibanco", "Financial Services", "Banks", 
                "financial", CompanyType.PUBLIC_FINANCIAL, "Brazilian bank (financial priority over geographic)", "BRAZIL"),
        
        # Developed Market Companies (that might be confused with emerging)
        TestCase("ASML", "ASML Holding", "Technology", "Semiconductor Equipment", 
                "original", CompanyType.PUBLIC_MANUFACTURING, "Dutch semiconductor equipment manufacturer", "NETHERLANDS"),
        TestCase("UL", "Unilever PLC", "Consumer Defensive", "Consumer Goods", 
                "retail", CompanyType.PUBLIC_RETAIL, "UK/Dutch consumer goods", "NETHERLANDS"),
        
        # Private/No Market Data Companies (should use 'private' model)
        TestCase("PRIVATE1", "Private Manufacturing Co", "Industrials", "Manufacturing", 
                "private", CompanyType.PRIVATE_COMPANY, "Private manufacturing company", market_cap=None),
        TestCase("PRIVATE2", "Private Service Co", "Healthcare", "Healthcare Services", 
                "private", CompanyType.PRIVATE_COMPANY, "Private service company", market_cap=None),
        TestCase("PRIVATE3", "Private Tech Co", "Technology", "Software", 
                "private", CompanyType.PRIVATE_COMPANY, "Private technology company", market_cap=None),
    ]


def run_model_selector_tests():
    """Run comprehensive model selector tests."""
    print("="*80)
    print("MODEL SELECTOR COMPREHENSIVE VALIDATION TEST")
    print("="*80)
    print()
    
    # Initialize model selector
    selector = ModelSelector()
    test_cases = get_test_cases()
    
    # Track results
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = []
    
    print(f"Running {total_tests} test cases...")
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i:2d}/{total_tests}: {test_case.ticker:8s} ({test_case.description})")
        
        try:
            # Create test data
            test_data = create_test_data(test_case)
            
            # Run model selection
            result = selector.select_model(test_data)
            
            # Check results
            model_correct = result.model_name == test_case.expected_model
            type_correct = result.company_type == test_case.expected_company_type
            
            if model_correct and type_correct:
                print(f"         ✓ PASS: Selected '{result.model_name}' model, {result.company_type.value}")
                print(f"           Confidence: {result.confidence:.2f}, Rationale: {result.selection_rationale}")
                passed_tests += 1
            else:
                print(f"         ✗ FAIL:")
                print(f"           Expected: '{test_case.expected_model}' model, {test_case.expected_company_type.value}")
                print(f"           Actual:   '{result.model_name}' model, {result.company_type.value}")
                print(f"           Confidence: {result.confidence:.2f}")
                print(f"           Rationale: {result.selection_rationale}")
                failed_tests.append({
                    'test_case': test_case,
                    'result': result,
                    'model_correct': model_correct,
                    'type_correct': type_correct
                })
                
        except Exception as e:
            print(f"         ✗ ERROR: {str(e)}")
            failed_tests.append({
                'test_case': test_case,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {passed_tests}")
    print(f"Failed:       {len(failed_tests)}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    print()
    
    # Failed test details
    if failed_tests:
        print("FAILED TESTS:")
        print("-" * 40)
        for i, failure in enumerate(failed_tests, 1):
            test_case = failure['test_case']
            print(f"{i}. {test_case.ticker} - {test_case.description}")
            
            if 'error' in failure:
                print(f"   Error: {failure['error']}")
            else:
                result = failure['result']
                print(f"   Expected: {test_case.expected_model} model")
                print(f"   Actual:   {result.model_name} model")
                print(f"   Rationale: {result.selection_rationale}")
            print()
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_model_selector_tests()
    exit(0 if success else 1)
