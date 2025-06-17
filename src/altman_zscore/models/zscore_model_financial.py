"""
zscore_model_financial.py
------------------------
Z-Score model implementation for financial institutions.

This module implements the Altman Z-Score model specifically designed for financial
institutions, using modified ratios and coefficients appropriate for banks and
financial companies.

Key differences from the original model:
1. Uses equity-to-debt ratio instead of working capital ratios
2. Different treatment of market value due to leverage considerations
3. Modified coefficients to account for financial sector characteristics
"""

from decimal import Decimal
from typing import Dict

from .zscore_model_base import ZScoreModel

class FinancialInstitutionZScoreModel(ZScoreModel):
    """
    Altman Z-Score model for financial institutions.
    
    This model uses the following ratios:
    X1 = (Equity - Intangible Assets) / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Book Value of Equity / Total Liabilities
    
    Z-Score = 3.25 + 6.56X₁ + 3.26X₂ + 6.72X₃ + 1.05X₄
    
    Interpretation:
    Z > 2.6: Safe Zone
    1.1 < Z < 2.6: Grey Zone
    Z < 1.1: Distress Zone
    """

    def __init__(self):
        self.COEFFICIENT_X1 = Decimal('6.56')  # Working Capital / Total Assets
        self.COEFFICIENT_X2 = Decimal('3.26')  # Retained Earnings / Total Assets
        self.COEFFICIENT_X3 = Decimal('6.72')  # EBIT / Total Assets
        self.COEFFICIENT_X4 = Decimal('1.05')  # Book Value of Equity / Total Liabilities
        self.CONSTANT = Decimal('3.25')        # Constant term
        
        # Thresholds for financial institutions
        self.DISTRESS_THRESHOLD = Decimal('1.1')
        self.SAFE_THRESHOLD = Decimal('2.6')

    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """
        Calculate Z-Score for financial institutions using modified ratios.
        
        Args:
            financial_data: Dictionary containing required financial metrics:
                - total_assets
                - total_equity
                - intangible_assets
                - retained_earnings
                - ebit
                - total_liabilities
        
        Returns:
            Decimal: Calculated Z-Score
        """
        try:
            # X1 = (Equity - Intangible Assets) / Total Assets
            x1 = (Decimal(str(financial_data['total_equity'])) - 
                  Decimal(str(financial_data.get('intangible_assets', 0)))) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X2 = Retained Earnings / Total Assets
            x2 = Decimal(str(financial_data['retained_earnings'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X3 = EBIT / Total Assets
            x3 = Decimal(str(financial_data['ebit'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X4 = Book Value of Equity / Total Liabilities
            x4 = Decimal(str(financial_data['total_equity'])) / \
                 Decimal(str(financial_data['total_liabilities']))
            
            # Calculate Z-Score
            zscore = self.CONSTANT + \
                    (self.COEFFICIENT_X1 * x1) + \
                    (self.COEFFICIENT_X2 * x2) + \
                    (self.COEFFICIENT_X3 * x3) + \
                    (self.COEFFICIENT_X4 * x4)
            
            return zscore.quantize(Decimal('0.01'))
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e)}")
        except (ValueError, ArithmeticError) as e:
            raise ValueError(f"Error calculating Z-Score: {str(e)}")

    def interpret_score(self, score: Decimal) -> str:
        """
        Interpret the Z-Score for financial institutions.
        
        Args:
            score: Calculated Z-Score
            
        Returns:
            str: Interpretation of the Z-Score
        """
        if score >= self.SAFE_THRESHOLD:
            return "Safe Zone: Low probability of financial distress"
        elif score >= self.DISTRESS_THRESHOLD:
            return "Grey Zone: Moderate risk of financial distress"
        else:
            return "Distress Zone: High risk of financial distress"

    def get_thresholds(self) -> Dict[str, Decimal]:
        """Get the threshold values for this model."""
        return {
            'safe_zone': self.SAFE_THRESHOLD,
            'distress_zone': self.DISTRESS_THRESHOLD
        }
