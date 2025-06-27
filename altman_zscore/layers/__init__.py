"""
Layers Package - Altman Z-Score Pipeline

This package contains the simplified layered architecture implementation for the 
Altman Z-Score analysis pipeline.

Simplified Layer Structure (FMP-First Architecture):
- Layer 1: Data Fetch (altman_zscore.layers.data_fetch) - FMP + Yahoo data fetching
- Layer 2: Z-Score Calculation (altman_zscore.layers.zscore_calculation) - Direct calculation
- Layer 3: AI Analysis (altman_zscore.layers.ai_analysis) - Insights generation
- Layer 4: Output Generation (altman_zscore.layers.output_generation) - Reports & charts

Key Architectural Benefits:
- No field mapping complexity (FMP provides standardized data)
- Direct data flow from integration to Z-Score calculation
- Simplified testing and maintenance
- Performance optimized pipeline

Each layer has a single responsibility and clear interfaces.
"""

# Layer components for easy access