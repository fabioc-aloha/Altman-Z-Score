"""
FMP Statement Mapper - Maps raw financial statements to Z-Score components.

This module transforms raw FMP financial statement data into standardized
component values needed for Altman Z-Score calculations, enabling better
compatibility with the free tier of the FMP API.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from ...common.logging_config import get_logger

logger = get_logger(__name__)


class FMPStatementMapper:
    """Maps FMP financial statement fields to Z-Score components."""
    
    def map_statements_to_zscore_inputs(
        self, 
        ticker: str,
        income_statement: List[Dict[str, Any]], 
        balance_sheet: List[Dict[str, Any]],
        profile: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Map financial statements to Z-Score input components.
        
        Args:
            ticker: Stock ticker symbol
            income_statement: Income statement data from FMP
            balance_sheet: Balance sheet data from FMP
            profile: Company profile data from FMP (for market cap)
            
        Returns:
            List of period data with mapped Z-Score component values
        """
        results = []
        
        # Match statements by date
        for bs_entry in balance_sheet:
            # Extract date from balance sheet
            period_date = bs_entry.get('date', '')
            if not period_date:
                continue
                
            # Find matching income statement
            is_entry = next((is_data for is_data in income_statement 
                            if is_data.get('date') == period_date), None)
            if not is_entry:
                logger.warning(f"No matching income statement for {ticker} on {period_date}")
                continue
                
            # Extract required values with fallbacks
            total_assets = self._get_value(bs_entry, ["totalAssets"])
            if not total_assets or total_assets == 0:
                logger.warning(f"Total assets missing or zero for {ticker} on {period_date}")
                continue
                
            # Calculate Working Capital
            current_assets = self._get_value(bs_entry, ["totalCurrentAssets"])
            current_liabilities = self._get_value(bs_entry, ["totalCurrentLiabilities"])
            working_capital = current_assets - current_liabilities
                
            # Get Retained Earnings
            retained_earnings = self._get_value(bs_entry, ["retainedEarnings"])
            
            # Get EBIT (Operating Income)
            ebit = self._get_value(is_entry, ["operatingIncome", "ebit"])
            
            # Get Total Liabilities
            total_liabilities = self._get_value(bs_entry, ["totalLiabilities"])
            
            # Get Sales/Revenue
            sales = self._get_value(is_entry, ["revenue", "totalRevenue"])
            
            # Get Market Value of Equity (from profile)
            market_value = 0
            if profile and isinstance(profile, list) and len(profile) > 0:
                market_value = self._get_value(profile[0], ["mktCap", "marketCap"])
            elif profile and isinstance(profile, dict):
                market_value = self._get_value(profile, ["mktCap", "marketCap"])
            
            # Calculate ratios needed for Z-Score
            period_data = {
                "date": period_date,
                "fiscal_year": bs_entry.get("calendarYear", ""),
                "fiscal_period": bs_entry.get("period", ""),
                "working_capital_ratio": working_capital / total_assets,
                "retained_earnings_ratio": retained_earnings / total_assets,
                "ebit_ratio": ebit / total_assets,
                "market_value_ratio": market_value / total_liabilities if total_liabilities else 0,
                "sales_ratio": sales / total_assets,
                # Store raw values for debugging/reporting
                "total_assets": total_assets,
                "working_capital": working_capital,
                "retained_earnings": retained_earnings,
                "ebit": ebit,
                "total_liabilities": total_liabilities,
                "sales": sales,
                "market_value": market_value
            }
            results.append(period_data)
            
        return results
    
    def _get_value(self, data: Dict[str, Any], possible_keys: List[str]) -> float:
        """
        Extract value from data using a list of possible keys.
        
        Args:
            data: Dictionary containing financial data
            possible_keys: List of possible field names for the value
            
        Returns:
            Extracted value or 0 if not found
        """
        for key in possible_keys:
            if key in data and data[key] is not None:
                try:
                    return float(data[key])
                except (ValueError, TypeError):
                    continue
        
        # Log missing field but return 0 to allow calculation to proceed
        logger.debug(f"Could not find any of these fields in data: {possible_keys}")
        return 0.0
    
    def calculate_current_ratio(self, balance_sheet: Dict[str, Any]) -> Optional[float]:
        """
        Calculate current ratio (current assets / current liabilities).
        
        Args:
            balance_sheet: Balance sheet data
            
        Returns:
            Current ratio or None if data is missing
        """
        current_assets = self._get_value(balance_sheet, ['totalCurrentAssets'])
        current_liabilities = self._get_value(balance_sheet, ['totalCurrentLiabilities'])
        
        if current_assets > 0 and current_liabilities > 0:
            return current_assets / current_liabilities
        return None
    
    def calculate_debt_to_equity(self, balance_sheet: Dict[str, Any]) -> Optional[float]:
        """
        Calculate debt-to-equity ratio (total debt / total equity).
        
        Args:
            balance_sheet: Balance sheet data
            
        Returns:
            Debt-to-equity ratio or None if data is missing
        """
        total_debt = self._get_value(balance_sheet, ['totalDebt', 'totalLiabilities'])
        total_equity = self._get_value(balance_sheet, ['totalStockholdersEquity', 'totalEquity'])
        
        if total_debt > 0 and total_equity > 0:
            return total_debt / total_equity
        return None
