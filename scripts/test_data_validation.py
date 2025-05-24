"""Script to test financial data validation."""
import logging
from decimal import Decimal
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from altman_zscore.data_validation import FinancialDataValidator, ValidationLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tech_company_validation():
    """Test validation with tech company data."""
    validator = FinancialDataValidator()
    
    # Sample tech company data
    tech_data = {
        "total_assets": Decimal("1000000000"),  # $1B
        "current_assets": Decimal("500000000"),  # $500M
        "total_liabilities": Decimal("400000000"),  # $400M
        "current_liabilities": Decimal("200000000"),  # $200M
        "retained_earnings": Decimal("300000000"),  # $300M
        "ebit": Decimal("150000000"),  # $150M
        "revenue": Decimal("800000000"),  # $800M
        "research_and_development_expense": Decimal("20000000"),  # $20M (2.5% of revenue)
        "working_capital": Decimal("300000000"),  # $300M
        "equity_ratio": Decimal("0.6")  # 60% equity
    }
    
    # Validate the data
    issues = validator.validate_data(tech_data, industry="TECH")
    
    # Print validation results
    logger.info("\nTech Company Validation Results:")
    logger.info("-" * 60)
    
    if not issues:
        logger.info("No validation issues found")
    else:
        for issue in issues:
            level_marker = "❌" if issue.level == ValidationLevel.ERROR else "⚠️"
            logger.info(f"{level_marker} {issue.field}: {issue.issue}")
            if issue.value is not None:
                logger.info(f"   Value: {issue.value}")
            if issue.expected_range:
                logger.info(f"   Expected: {issue.expected_range}")
    
def test_manufacturing_company_validation():
    """Test validation with manufacturing company data."""
    validator = FinancialDataValidator()
    
    # Sample manufacturing company data
    mfg_data = {
        "total_assets": Decimal("2000000000"),  # $2B
        "current_assets": Decimal("800000000"),  # $800M
        "total_liabilities": Decimal("1200000000"),  # $1.2B
        "current_liabilities": Decimal("400000000"),  # $400M
        "retained_earnings": Decimal("500000000"),  # $500M
        "ebit": Decimal("250000000"),  # $250M
        "inventory": Decimal("150000000"),  # $150M (7.5% of total assets)
        "working_capital": Decimal("400000000"),  # $400M
        "equity_ratio": Decimal("0.4")  # 40% equity
    }
    
    # Validate the data
    issues = validator.validate_data(mfg_data, industry="MANUFACTURING")
    
    # Print validation results
    logger.info("\nManufacturing Company Validation Results:")
    logger.info("-" * 60)
    
    if not issues:
        logger.info("No validation issues found")
    else:
        for issue in issues:
            level_marker = "❌" if issue.level == ValidationLevel.ERROR else "⚠️"
            logger.info(f"{level_marker} {issue.field}: {issue.issue}")
            if issue.value is not None:
                logger.info(f"   Value: {issue.value}")
            if issue.expected_range:
                logger.info(f"   Expected: {issue.expected_range}")

def test_yahoo_industry_value():
    """Test that the industry value matches actual Yahoo Finance for AAPL."""
    import yfinance as yf
    yf_ticker = yf.Ticker("AAPL")
    yf_info = yf_ticker.info
    industry = yf_info.get("industry")
    assert industry == "Consumer Electronics", f"Expected 'Consumer Electronics', got {industry}"
    print(f"[PASS] Yahoo Finance industry for AAPL: {industry}")

def test_missing_required_field():
    """Test that missing required fields are handled gracefully."""
    validator = FinancialDataValidator()
    incomplete_data = {
        "total_assets": Decimal("1000000000"),
        # 'current_assets' is missing
        "current_liabilities": Decimal("200000000"),
        "retained_earnings": Decimal("300000000"),
        "ebit": Decimal("150000000"),
        "revenue": Decimal("800000000")
    }
    issues = validator.validate_data(incomplete_data, industry="TECH")
    if not issues:
        print("[WARN] No validation issues found for missing field (stub validator)")
    else:
        for issue in issues:
            print(f"[INFO] {issue.field}: {issue.issue}")

def main():
    """Run validation tests."""
    test_tech_company_validation()
    test_manufacturing_company_validation()
    test_yahoo_industry_value()
    test_missing_required_field()

if __name__ == "__main__":
    main()
