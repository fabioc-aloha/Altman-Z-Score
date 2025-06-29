#!/usr/bin/env python3

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from altman_zscore.layers.ai_analysis.ai_orchestrator import AIAnalysisOrchestrator

# Test basic initialization
print("Testing AI Orchestrator...")
orchestrator = AIAnalysisOrchestrator()

# Check implementation status
status = orchestrator.get_implementation_status()
print("\nImplementation Status:")
for component, info in status.items():
    print(f"  {component}: {info['status']}")

print("\n✅ AI Orchestrator basic test passed!")
