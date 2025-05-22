"""Financial metrics and ratio calculations."""
from decimal import Decimal
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FinancialMetricsCalculator:
    """Calculator for financial metrics and ratios."""
    
    @staticmethod
    def safe_divide(numerator: Decimal, denominator: Decimal) -> Optional[Decimal]:
        """Safely perform division handling zero denominator.
        
        Args:
            numerator: Division numerator
            denominator: Division denominator
            
        Returns:
            Division result or None if invalid
        """
        try:
            if denominator == 0:
                return None
            return numerator / denominator
        except (TypeError, ValueError, ZeroDivisionError) as e:
            logger.warning(f"Division error: {str(e)}")
            return None
            
    def calculate_working_capital_ratio(
        self,
        current_assets: Decimal,
        current_liabilities: Decimal
    ) -> Optional[Decimal]:
        """Calculate working capital to total assets ratio.
        
        Args:
            current_assets: Current assets value
            current_liabilities: Current liabilities value
            
        Returns:
            Ratio value or None if invalid
        """
        working_capital = current_assets - current_liabilities
        total_assets = current_assets  # Assuming total_assets provided
        return self.safe_divide(working_capital, total_assets)
        
    def calculate_retained_earnings_ratio(
        self,
        retained_earnings: Decimal,
        total_assets: Decimal
    ) -> Optional[Decimal]:
        """Calculate retained earnings to total assets ratio.
        
        Args:
            retained_earnings: Retained earnings value
            total_assets: Total assets value
            
        Returns:
            Ratio value or None if invalid
        """
        return self.safe_divide(retained_earnings, total_assets)
        
    def calculate_ebit_ratio(
        self,
        ebit: Decimal,
        total_assets: Decimal
    ) -> Optional[Decimal]:
        """Calculate EBIT to total assets ratio.
        
        Args:
            ebit: EBIT (Earnings Before Interest and Taxes) value
            total_assets: Total assets value
            
        Returns:
            Ratio value or None if invalid
        """
        return self.safe_divide(ebit, total_assets)
        
    def calculate_equity_ratio(
        self,
        market_value_equity: Decimal,
        total_liabilities: Decimal
    ) -> Optional[Decimal]:
        """Calculate market value of equity to total liabilities ratio.
        
        Args:
            market_value_equity: Market value of equity
            total_liabilities: Total liabilities value
            
        Returns:
            Ratio value or None if invalid
        """
        return self.safe_divide(market_value_equity, total_liabilities)
        
    def calculate_sales_ratio(
        self,
        sales: Decimal,
        total_assets: Decimal
    ) -> Optional[Decimal]:
        """Calculate sales to total assets ratio.
        
        Args:
            sales: Sales value
            total_assets: Total assets value
            
        Returns:
            Ratio value or None if invalid
        """
        return self.safe_divide(sales, total_assets)
        
    def calculate_all_ratios(self, financial_data: Dict[str, Decimal]) -> Dict[str, Optional[Decimal]]:
        """Calculate all Z-score ratios from financial data.
        
        Args:
            financial_data: Dictionary of financial values
            
        Returns:
            Dictionary of calculated ratios
        """
        required_fields = {
            'current_assets',
            'current_liabilities',
            'retained_earnings',
            'total_assets',
            'ebit',
            'market_value_equity',
            'total_liabilities',
            'sales'
        }
        
        # Validate required fields
        missing_fields = required_fields - set(financial_data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
            
        return {
            'working_capital_to_total_assets': self.calculate_working_capital_ratio(
                financial_data['current_assets'],
                financial_data['current_liabilities']
            ),
            'retained_earnings_to_total_assets': self.calculate_retained_earnings_ratio(
                financial_data['retained_earnings'],
                financial_data['total_assets']
            ),
            'ebit_to_total_assets': self.calculate_ebit_ratio(
                financial_data['ebit'],
                financial_data['total_assets']
            ),
            'market_value_equity_to_total_liabilities': self.calculate_equity_ratio(
                financial_data['market_value_equity'],
                financial_data['total_liabilities']
            ),
            'sales_to_total_assets': self.calculate_sales_ratio(
                financial_data['sales'],
                financial_data['total_assets']
            )
        }
