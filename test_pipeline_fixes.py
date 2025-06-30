#!/usr/bin/env python3
"""
Quick test to validate the report generator fixes
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from altman_zscore.layers.output_generation.report_generator import ReportGenerator
from altman_zscore.layers.ai_analysis.ai_orchestrator import ComprehensiveAIAnalysis
from datetime import datetime

# Test simplified AI analysis data structure
test_ai_analysis = ComprehensiveAIAnalysis(
    ticker="TEST",
    analysis_timestamp=datetime.now(),
    overall_ai_confidence=0.85,
    ai_recommendations=["Test recommendation"],
    llm_final_commentary="Test commentary"
)

print("✅ AI Analysis data structure created successfully")

# Test report generator initialization  
try:
    report_gen = ReportGenerator()
    print("✅ Report generator initialized successfully")
except Exception as e:
    print(f"❌ Report generator initialization failed: {e}")
    sys.exit(1)

print("🎉 All simplified pipeline components validated successfully!")
