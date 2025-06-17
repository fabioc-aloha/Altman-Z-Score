"""
zscore_model_zeta.py
-------------------
Implementation of the Zeta® Model (1977 public domain version).

This is the public domain version of the Zeta® model developed by Altman,
Haldeman, and Narayanan. The proprietary version includes additional
variables and different coefficients.
"""

from decimal import Decimal
from typing import Dict

from .zscore_model_base import ZScoreModel

class ZetaZScoreModel(ZScoreModel):
    """
    Zeta® Model (1977 public domain version).
    
    This model uses seven variables:
    X1 = Return on Assets (EBIT / Total Assets)
    X2 = Stability of Earnings (Standard deviation of ROA over 5-10 years)
    X3 = Debt Service (EBIT / Total Interest Payments)
    X4 = Cumulative Profitability (Retained Earnings / Total Assets)
    X5 = Liquidity (Current Assets / Current Liabilities)
    X6 = Capitalization (Common Equity / Total Capital)
    X7 = Size (Log of Total Assets)
    
    Note: Actual coefficients are modified from the proprietary model.
    """

    def __init__(self):
        # Public domain approximation of coefficients
        self.COEFFICIENT_X1 = Decimal('3.25')  # ROA
        self.COEFFICIENT_X2 = Decimal('2.50')  # Earnings stability
        self.COEFFICIENT_X3 = Decimal('2.00')  # Debt service
        self.COEFFICIENT_X4 = Decimal('3.50')  # Cumulative profitability
        self.COEFFICIENT_X5 = Decimal('1.00')  # Liquidity
        self.COEFFICIENT_X6 = Decimal('1.50')  # Capitalization
        self.COEFFICIENT_X7 = Decimal('0.75')  # Size
        
        # Thresholds (public domain approximation)
        self.DISTRESS_THRESHOLD = Decimal('1.45')
        self.SAFE_THRESHOLD = Decimal('2.60')

    def _calculate_zscore_impl(self, financial_data: Dict) -> Decimal:
        """Calculate Zeta® Score using the seven variables."""
        try:
            # X1 = Return on Assets
            x1 = Decimal(str(financial_data['ebit'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X2 = Stability of Earnings (requires historical data)
            x2 = Decimal(str(financial_data.get('earnings_stability', 0)))
            
            # X3 = Debt Service
            x3 = Decimal(str(financial_data['ebit'])) / \
                 Decimal(str(financial_data.get('interest_payments', 1)))
            
            # X4 = Cumulative Profitability
            x4 = Decimal(str(financial_data['retained_earnings'])) / \
                 Decimal(str(financial_data['total_assets']))
            
            # X5 = Liquidity
            x5 = Decimal(str(financial_data['current_assets'])) / \
                 Decimal(str(financial_data['current_liabilities']))
            
            # X6 = Capitalization
            x6 = Decimal(str(financial_data['common_equity'])) / \
                 Decimal(str(financial_data['total_capital']))
            
            # X7 = Size (log of total assets)
            import math
            x7 = Decimal(str(math.log(float(financial_data['total_assets']))))
            
            # Calculate Zeta® Score
            zscore = (self.COEFFICIENT_X1 * x1) + \
                    (self.COEFFICIENT_X2 * x2) + \
                    (self.COEFFICIENT_X3 * x3) + \
                    (self.COEFFICIENT_X4 * x4) + \
                    (self.COEFFICIENT_X5 * x5) + \
                    (self.COEFFICIENT_X6 * x6) + \
                    (self.COEFFICIENT_X7 * x7)
            
            return zscore.quantize(Decimal('0.01'))
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {str(e)}")
        except (ValueError, ArithmeticError) as e:
            raise ValueError(f"Error calculating Zeta® Score: {str(e)}")

    def interpret_score(self, score: Decimal) -> str:
        """Interpret the Zeta® Score result."""
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
