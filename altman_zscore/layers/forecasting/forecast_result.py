"""
Forecast Result - Data structures for Z-Score forecasting results

Contains data classes and result structures for forecast Z-Score calculations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class ForecastScenario:
    """Single forecast scenario (base, optimistic, pessimistic)."""
    scenario_name: str
    z_score: float
    risk_category: str
    confidence_level: float
    forecast_period: str  # e.g., "2025 Q4", "2026 Annual"
    component_values: Dict[str, float] = field(default_factory=dict)
    assumptions: Dict[str, str] = field(default_factory=dict)
    

@dataclass
class ForecastResult:
    """Complete Z-Score forecast result for a ticker."""
    ticker: str
    company_name: str
    base_z_score: float  # Current/baseline Z-Score
    forecast_scenarios: List[ForecastScenario] = field(default_factory=list)
    forecast_metadata: Dict[str, Any] = field(default_factory=dict)
    model_used: str = "original"
    data_quality_score: float = 0.0
    analyst_coverage_quality: float = 0.0
    forecast_timestamp: datetime = field(default_factory=datetime.now)
    warnings: List[str] = field(default_factory=list)
    
    def get_scenario(self, scenario_name: str) -> Optional[ForecastScenario]:
        """Get specific forecast scenario by name."""
        for scenario in self.forecast_scenarios:
            if scenario.scenario_name.lower() == scenario_name.lower():
                return scenario
        return None
    
    def get_base_scenario(self) -> Optional[ForecastScenario]:
        """Get the base/most likely forecast scenario."""
        # Try exact matches first
        for scenario in self.forecast_scenarios:
            if scenario.scenario_name.lower() in ["base case", "base", "consensus"]:
                return scenario
        
        # If no exact match, return the first scenario with "base" in the name
        for scenario in self.forecast_scenarios:
            if "base" in scenario.scenario_name.lower():
                return scenario
        
        # Fallback: return first scenario if available
        return self.forecast_scenarios[0] if self.forecast_scenarios else None
    
    def get_forecast_range(self) -> Dict[str, float]:
        """Get Z-Score range across all scenarios."""
        if not self.forecast_scenarios:
            return {"min": 0.0, "max": 0.0, "range": 0.0}
        
        z_scores = [scenario.z_score for scenario in self.forecast_scenarios]
        min_z = min(z_scores)
        max_z = max(z_scores)
        
        return {
            "min": min_z,
            "max": max_z,
            "range": max_z - min_z
        }
    
    def get_forecast_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the forecast."""
        if not self.forecast_scenarios:
            return {}
        
        z_scores = [scenario.z_score for scenario in self.forecast_scenarios]
        confidence_levels = [scenario.confidence_level for scenario in self.forecast_scenarios]
        
        return {
            "scenarios_count": len(self.forecast_scenarios),
            "z_score_range": self.get_forecast_range(),
            "avg_z_score": sum(z_scores) / len(z_scores),
            "avg_confidence": sum(confidence_levels) / len(confidence_levels),
            "forecast_periods": [s.forecast_period for s in self.forecast_scenarios],
            "risk_categories": list(set(s.risk_category for s in self.forecast_scenarios))
        }
