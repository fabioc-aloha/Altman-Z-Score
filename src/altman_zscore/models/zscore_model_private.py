"""
zscore_model_private.py
----------------------
Z'-Score model implementation for private manufacturing companies.

This module implements the Altman Z'-Score model designed for private companies,
which replaces the market value of equity with book value of equity.
"""

from decimal import Decimal
from typing import Dict

from .zscore_model_base import ZScoreModel

class PrivateManufacturingZScoreModel(ZScoreModel):
    """
    Altman Z'-Score model for private manufacturing companies.
    
    This model uses the following ratios:
    X1 = Working Capital / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Book Value of Equity / Total Liabilities
    X5 = Sales / Total Assets
    
    Z' = 0.717X₁ + 0.847X₂ + 3.107X₃ + 0.420X₄ + 0.998X₅
    
    Interpretation:
    Z' > 2.9: Safe Zone
    1.23 < Z' < 2.9: Grey Zone
    Z' < 1.23: Distress Zone
    """

    def __init__(self):
        self.COEFFICIENT_X1 = Decimal('0.717')  # Working Capital / Total Assets
        self.COEFFICIENT_X2 = Decimal('0.847')  # Retained Earnings / Total Assets
        self.COEFFICIENT_X3 = Decimal('3.107')  # EBIT / Total Assets
        self.COEFFICIENT_X4 = Decimal('0.420')  # Book Value of Equity / Total Liabilities
        self.COEFFICIENT_X5 = Decimal('0.998')  # Sales / Total Assets
        
        # Thresholds for private companies
        self.DISTRESS_THRESHOLD = Decimal('1.23')
        self.SAFE_THRESHOLD = Decimal('2.90')

    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """
        Calculate Z'-Score using book values instead of market values.
        
        Args:
            financial_data: Dictionary containing required financial metrics:
                - working_capital
                - total_assets
                - retained_earnings
                - ebit
                - total_equity (book value)
                - total_liabilities
                - sales
        
        Returns:
            Decimal: Calculated Z'-Score
        """
        try:
            # X1 = Working Capital / Total Assets
            x1 = Decimal(str(financial_data['working_capital'])) / \
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
            
            # X5 = Sales / Total Assets
            x5 = Decimal(str(financial_data['sales'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # Calculate Z'-Score
            zscore = (self.COEFFICIENT_X1 * x1) + \
                    (self.COEFFICIENT_X2 * x2) + \
                    (self.COEFFICIENT_X3 * x3) + \
                    (self.COEFFICIENT_X4 * x4) + \
                    (self.COEFFICIENT_X5 * x5)
            
            return zscore.quantize(Decimal('0.01'))
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e)}")
        except (ValueError, ArithmeticError) as e:
            raise ValueError(f"Error calculating Z'-Score: {str(e)}")

    def interpret_score(self, score: Decimal) -> str:
        """
        Interpret the Z'-Score result.
        
        Args:
            score: Calculated Z'-Score
            
        Returns:
            str: Interpretation of the Z'-Score
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
