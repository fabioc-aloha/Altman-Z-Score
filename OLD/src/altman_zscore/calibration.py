"""
Calibration module for handling industry-specific Z-Score model adjustments.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

from .industry_classifier import CompanyProfile, IndustryGroup, TechSubsector
from .models import ModelCoefficients, ModelThresholds

@dataclass
class ModelCalibration:
    """Container for model calibration parameters."""
    coefficients: ModelCoefficients
    thresholds: ModelThresholds
    adjustment_factors: Dict[str, Decimal]

class CalibrationManager:
    """Manages Z-Score model calibrations for different industries and company types."""
    
    def get_calibration(self, profile: CompanyProfile, 
                       financial_metrics: Optional[Dict] = None) -> ModelCalibration:
        """
        Get appropriate model calibration based on company profile.
        
        Args:
            profile: Company classification profile
            financial_metrics: Optional financial metrics for fine-tuning
            
        Returns:
            ModelCalibration: Calibrated model parameters
        """
        # Start with base calibration based on company type
        if not profile.is_public:
            base_calibration = self._get_private_company_base()
        elif profile.is_emerging_market:
            base_calibration = self._get_emerging_market_base()
        elif profile.industry_group == IndustryGroup.MANUFACTURING:
            base_calibration = self._get_manufacturing_base()
        else:
            base_calibration = self._get_non_manufacturing_base()
        
        # Apply industry-specific adjustments
        if profile.is_tech_or_ai:
            return self._apply_tech_calibration(base_calibration, profile, financial_metrics)
            
        return base_calibration
    
    def _get_manufacturing_base(self) -> ModelCalibration:
        """Get base calibration for manufacturing companies."""
        return ModelCalibration(
            coefficients=ModelCoefficients.original(),
            thresholds=ModelThresholds.original(),
            adjustment_factors={
                'working_capital': Decimal('1.0'),
                'profitability': Decimal('1.0'),
                'leverage': Decimal('1.0')
            }
        )
    
    def _get_private_company_base(self) -> ModelCalibration:
        """Get base calibration for private companies."""
        return ModelCalibration(
            coefficients=ModelCoefficients.private_company(),
            thresholds=ModelThresholds.private_company(),
            adjustment_factors={
                'working_capital': Decimal('1.0'),
                'profitability': Decimal('1.0'),
                'leverage': Decimal('1.0')
            }
        )
    
    def _get_emerging_market_base(self) -> ModelCalibration:
        """Get base calibration for emerging market companies."""
        return ModelCalibration(
            coefficients=ModelCoefficients.non_manufacturing(),
            thresholds=ModelThresholds.non_manufacturing(),
            adjustment_factors={
                'working_capital': Decimal('1.2'),  # Higher WC needs
                'profitability': Decimal('0.9'),   # Lower profit expectations
                'leverage': Decimal('1.1')        # Higher leverage tolerance
            }
        )
    
    def _get_non_manufacturing_base(self) -> ModelCalibration:
        """Get base calibration for non-manufacturing companies."""
        return ModelCalibration(
            coefficients=ModelCoefficients.non_manufacturing(),
            thresholds=ModelThresholds.non_manufacturing(),
            adjustment_factors={
                'working_capital': Decimal('1.0'),
                'profitability': Decimal('1.0'),
                'leverage': Decimal('1.0')
            }
        )
    
    def _apply_tech_calibration(self, base: ModelCalibration, 
                              profile: CompanyProfile,
                              financial_metrics: Optional[Dict]) -> ModelCalibration:
        """
        Apply tech-specific calibration adjustments.
        
        Args:
            base: Base calibration to adjust
            profile: Company profile with tech classification
            financial_metrics: Optional financial metrics for fine-tuning
            
        Returns:
            ModelCalibration: Adjusted calibration for tech company
        """
        if not financial_metrics:
            financial_metrics = {}
        
        # Start with tech base adjustments
        calibration = ModelCalibration(
            coefficients=base.coefficients,
            thresholds=base.thresholds,
            adjustment_factors=base.adjustment_factors.copy()
        )
        
        # Get R&D intensity
        rd_intensity = Decimal(str(profile.rd_intensity or 0))
        
        # Apply subsector-specific adjustments
        if profile.tech_subsector == TechSubsector.AI_ML:
            self._apply_ai_calibration(calibration, rd_intensity, financial_metrics)
        elif profile.tech_subsector == TechSubsector.SAAS:
            self._apply_saas_calibration(calibration, rd_intensity, financial_metrics)
        elif profile.tech_subsector == TechSubsector.HARDWARE:
            self._apply_hardware_calibration(calibration, rd_intensity, financial_metrics)
        
        return calibration
    
    def _apply_ai_calibration(self, calibration: ModelCalibration,
                            rd_intensity: Decimal,
                            financial_metrics: Dict) -> None:
        """Apply AI/ML company specific calibration adjustments."""
        # Adjust for R&D intensity
        if rd_intensity > Decimal('0.2'):
            calibration.adjustment_factors['profitability'] *= Decimal('1.2')
        
        # Adjust for growth rate
        revenue_growth = Decimal(str(financial_metrics.get('revenue_growth', 0)))
        if revenue_growth > Decimal('1.0'):  # >100% growth
            calibration.thresholds.safe_zone = Decimal('2.2')
            calibration.thresholds.distress_zone = Decimal('1.4')
        elif revenue_growth > Decimal('0.3'):  # >30% growth
            calibration.thresholds.safe_zone = Decimal('2.4')
            calibration.thresholds.distress_zone = Decimal('1.45')
        else:
            calibration.thresholds.safe_zone = Decimal('2.6')
            calibration.thresholds.distress_zone = Decimal('1.5')
    
    def _apply_saas_calibration(self, calibration: ModelCalibration,
                              rd_intensity: Decimal,
                              financial_metrics: Dict) -> None:
        """Apply SaaS company specific calibration adjustments."""
        # Adjust for subscription revenue
        subscription_pct = Decimal(str(financial_metrics.get('subscription_revenue_pct', 0)))
        if subscription_pct > Decimal('0.8'):
            calibration.adjustment_factors['working_capital'] *= Decimal('0.9')
            calibration.adjustment_factors['leverage'] *= Decimal('1.1')
        
        # Adjust thresholds based on unit economics
        ltv_cac = Decimal(str(financial_metrics.get('ltv_cac_ratio', 0)))
        if ltv_cac > Decimal('3.0'):
            calibration.thresholds.safe_zone = Decimal('2.5')
            calibration.thresholds.distress_zone = Decimal('1.5')
        else:
            calibration.thresholds.safe_zone = Decimal('2.3')
            calibration.thresholds.distress_zone = Decimal('1.4')
    
    def _apply_hardware_calibration(self, calibration: ModelCalibration,
                                 rd_intensity: Decimal,
                                 financial_metrics: Dict) -> None:
        """Apply hardware tech company specific calibration adjustments."""
        # Hardware companies are more similar to manufacturing
        calibration.coefficients = ModelCoefficients.original()
        calibration.thresholds = ModelThresholds.original()
        
        # But adjust for tech characteristics
        if rd_intensity > Decimal('0.15'):
            calibration.adjustment_factors['profitability'] *= Decimal('1.1')
        
        # Adjust for inventory needs
        calibration.adjustment_factors['working_capital'] *= Decimal('1.1')
