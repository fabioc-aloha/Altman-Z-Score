"""Portfolio configuration for Altman Z-Score analysis."""
from datetime import datetime, timedelta

# Analysis Period Configuration
# Change these dates to analyze different quarters
#
# Examples:
#   For Q1 analysis: PERIOD_END = "2025-03-31", PRICE_START = "2025-01-01"
#   For Q2 analysis: PERIOD_END = "2025-06-30", PRICE_START = "2025-04-01"
#   For Q3 analysis: PERIOD_END = "2025-09-30", PRICE_START = "2025-07-01"
#   For Q4 analysis: PERIOD_END = "2025-12-31", PRICE_START = "2025-10-01"

PERIOD_END = "2025-03-31"     # Last day of the quarter to analyze
PRICE_START = "2025-01-01"    # First day for price comparison
PRICE_END = "2025-03-31"      # Last day for price comparison

# Portfolio Configuration
# Add or remove tickers as needed. Comments indicate company name and recommended model.
PORTFOLIO: list[str] = [
    # Technology/Software Companies (Service Model)
    "MSFT",   # Microsoft Corporation
    "ORCL",   # Oracle Corporation
    "CRM",    # Salesforce, Inc.
    "ADBE",   # Adobe Inc.
    "NOW",    # ServiceNow, Inc.
    "SNOW",   # Snowflake Inc.
    
    # Manufacturing Companies (Original Model)
    "F",      # Ford Motor Company
    "GM",     # General Motors Company
    "CAT",    # Caterpillar Inc.
    "BA",     # Boeing Company
    "MMM",    # 3M Company
    "HON",    # Honeywell International Inc.
    
    # Mixed Hardware/Software (Original/Service Model)
    "AAPL",   # Apple Inc.
    "IBM",    # International Business Machines
    "NVDA",   # NVIDIA Corporation
    "AMD",    # Advanced Micro Devices
    
    # Emerging Market ADRs (EM Model)
    "BABA",   # Alibaba Group Holding Ltd.
    "TSM",    # Taiwan Semiconductor Manufacturing
    "TCEHY",  # Tencent Holdings Ltd.
    "NIO",    # NIO Inc.
    "PDD",    # PDD Holdings Inc.
    
    # Recent IPOs/SPACs (Private Model)
    "LCID",   # Lucid Group Inc.
    "AI",     # C3.ai, Inc.
    "PLTR",   # Palantir Technologies Inc.
    
    # Pure Service Companies (Service Model)
    "UBER",   # Uber Technologies Inc.
    "ABNB",   # Airbnb, Inc.
    "DIS",    # The Walt Disney Company
    "NFLX",   # Netflix, Inc.
    "MA"      # Mastercard Incorporated
    
    # Distressed/Turnaround Companies (Various Models)
    "RIVN",   # Rivian Automotive - EV maker with cash burn concerns
    "MAT",    # Mattel Inc. - Historical restructuring case
    "BBBY",   # Bed Bath & Beyond - Recent bankruptcy case
    "AMC",    # AMC Entertainment - Theater chain restructuring
    "CVNA",   # Carvana - Car retailer with debt concerns
    "HOOD",   # Robinhood - Fintech with regulatory challenges
    "BYND",   # Beyond Meat - Food tech with market challenges
    "WISH",   # ContextLogic (Wish) - E-commerce turnaround attempt
    "VYGR",   # Voyager Digital - Crypto bankruptcy case
    "PRTY"    # Party City - Retail restructuring case
]
