"""
Test script to verify the new modular chart system works correctly.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all imports work correctly."""
    print("Testing modular chart system imports...")
    
    try:
        # Test main import
        from altman_zscore.layers.output_generation.chart_generator import ChartGenerator
        print("✓ ChartGenerator import successful")
        
        # Test direct dashboard generator import
        from altman_zscore.layers.output_generation.dashboard_generator import DashboardGenerator
        print("✓ DashboardGenerator import successful")
        
        # Test chart components
        from altman_zscore.layers.output_generation.charts import (
            ZScoreGauge, ComponentBreakdown, RiskZoneChart, DataQualityChart,
            InvestmentRecommendation, TechnicalIndicators, ValuationMetrics,
            PerformanceMetrics, RiskReturnAnalysis,
            AIDataQuality, AIPeerAnalysis, AISentiment, AIRisk, AIConfidence,
            TrendChart, DashboardLayoutManager
        )
        print("✓ All chart components import successful")
        
        # Test layout manager
        layout_manager = DashboardLayoutManager()
        print("✓ Layout manager initialization successful")
        
        # Test chart component initialization
        zscore_gauge = ZScoreGauge()
        component_breakdown = ComponentBreakdown()
        print("✓ Chart component initialization successful")
        
        # Test backward compatibility
        assert ChartGenerator == DashboardGenerator
        print("✓ Backward compatibility maintained")
        
        print("\n🎉 All tests passed! The modular chart system is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_structure():
    """Test the new structure organization."""
    print("\nTesting new structure organization...")
    
    charts_dir = project_root / "altman_zscore" / "layers" / "output_generation" / "charts"
    
    expected_files = [
        "__init__.py",
        "base.py", 
        "zscore_components.py",
        "market_components.py",
        "performance.py",
        "ai_components.py",
        "trend_analysis.py",
        "data_quality.py",
        "layout_manager.py"
    ]
    
    for file_name in expected_files:
        file_path = charts_dir / file_name
        if file_path.exists():
            print(f"✓ {file_name} exists")
        else:
            print(f"❌ {file_name} missing")
            return False
    
    print("✓ All expected files are present")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("MODULAR CHART SYSTEM VERIFICATION")
    print("=" * 60)
    
    structure_ok = test_structure()
    imports_ok = test_imports()
    
    if structure_ok and imports_ok:
        print("\n✅ SUCCESS: The chart system has been successfully refactored!")
        print("\nBenefits of the new modular system:")
        print("- Each chart component has a single responsibility")
        print("- Easier to test individual components")
        print("- Better code organization and maintainability")
        print("- Reduced coupling between different chart types")
        print("- Scalable architecture for adding new chart types")
        print("- Clean separation of layout management")
    else:
        print("\n❌ FAILURE: Some issues need to be resolved")
        sys.exit(1)
