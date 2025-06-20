"""
zscore_model_retail.py
---------------------
Implementation of the retail-specific Z-Score model.

This model modifies the original Z-Score to account for retail industry
characteristics, particularly regarding inventory and asset utilization.
"""

from decimal import Decimal
from typing import Dict

from .zscore_model_base import ZScoreModel

class RetailZScoreModel(ZScoreModel):
    """
    Retail Industry Z-Score Model.
    
    Modified version with retail-specific adjustments:
    X1 = (Current Assets - Inventory) / Total Assets
    X2 = Retained Earnings / Total Assets
    X3 = EBIT / Total Assets
    X4 = Market Value of Equity / Total Liabilities
    X5 = Sales / Total Assets
    X6 = Inventory Turnover
    
    Note: Coefficients are adjusted for retail industry characteristics.
    """

    def __init__(self):
        self.COEFFICIENT_X1 = Decimal('1.10')  # Quick ratio weight
        self.COEFFICIENT_X2 = Decimal('1.40')  # Retained earnings weight
        self.COEFFICIENT_X3 = Decimal('3.30')  # Profitability weight
        self.COEFFICIENT_X4 = Decimal('0.60')  # Market value weight
        self.COEFFICIENT_X5 = Decimal('1.20')  # Asset turnover weight
        self.COEFFICIENT_X6 = Decimal('0.30')  # Inventory turnover weight
        
        # Thresholds adjusted for retail
        self.DISTRESS_THRESHOLD = Decimal('1.90')
        self.SAFE_THRESHOLD = Decimal('3.10')

    def _calculate_zscore_impl(self, financial_data: Dict) -> Decimal:
        """Calculate Retail Z-Score using modified ratios."""
        try:
            # X1 = Quick Ratio Component
            x1 = (Decimal(str(financial_data['current_assets'])) - 
                  Decimal(str(financial_data['inventory']))) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X2 = Retained Earnings to Total Assets
            x2 = Decimal(str(financial_data['retained_earnings'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X3 = EBIT to Total Assets
            x3 = Decimal(str(financial_data['ebit'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X4 = Market Value of Equity to Total Liabilities
            x4 = Decimal(str(financial_data['market_value_equity'])) / \
                 Decimal(str(financial_data['total_liabilities']))
            
            # X5 = Sales to Total Assets
            x5 = Decimal(str(financial_data['sales'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X6 = Inventory Turnover
            x6 = Decimal(str(financial_data['cost_of_goods_sold'])) / \
                 Decimal(str(financial_data['average_inventory']))
            
            # Calculate Retail Z-Score
            zscore = (self.COEFFICIENT_X1 * x1) + \
                    (self.COEFFICIENT_X2 * x2) + \
                    (self.COEFFICIENT_X3 * x3) + \
                    (self.COEFFICIENT_X4 * x4) + \
                    (self.COEFFICIENT_X5 * x5) + \
                    (self.COEFFICIENT_X6 * x6)
            
            return zscore.quantize(Decimal('0.01'))
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e)}")
        except (ValueError, ArithmeticError) as e:
            raise ValueError(f"Error calculating Retail Z-Score: {str(e)}")

    def calculate_zscore(self, financial_data: Dict) -> Decimal:
        """Calculate the Retail Z-Score for given financial data."""
        return self._calculate_zscore_impl(financial_data)

    def interpret_score(self, score: Decimal) -> str:
        """Interpret the Retail Z-Score result."""
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
