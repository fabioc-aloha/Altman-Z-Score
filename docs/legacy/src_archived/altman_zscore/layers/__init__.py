"""
Altman Z-Score Analysis Pipeline Layers

This package implements a layered architecture for the Altman Z-Score pipeline:

1. Data Fetch Layer: Fetches and filters raw financial data from sources
2. Field Mapping Layer: Maps and validates financial fields, imputes missing data
3. Model Selection Layer: Selects appropriate Z-Score model based on company profile
4. Z-Score Calculation Layer: Computes Z-Scores with reality checks
5. Analysis Layer: Performs trend analysis and generates insights
6. Reporting Layer: Generates outputs and visualizations
"""
