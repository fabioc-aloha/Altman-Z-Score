"""
sic_lookup.py
-------------
SIC code to description mapping for industry classification.

This module provides a dictionary mapping Standard Industrial Classification (SIC)
codes to their textual descriptions. It is used for classifying companies into
industries based on their SIC codes.

Functions:
    get_sic_description(sic_code): Return the industry description for a given SIC code.
"""

sic_map = {
    # Dictionary mapping SIC codes to industry descriptions.
    #
    # Keys:
    #     str: SIC code as a string.
    # Values:
    #     str: Industry description corresponding to the SIC code.
    #
    # Example:
    #     "3711": "Motor Vehicles & Passenger Car Bodies"
    #
    # This mapping is used for classifying companies into industries based on their SIC codes.
    "0111": "Wheat",
    "1311": "Crude Petroleum & Natural Gas",
    "1389": "Oil & Gas Field Services",
    "2834": "Pharmaceutical Preparations",
    "3571": "Electronic Computers",
    "3572": "Computer Storage Devices",
    "3663": "Radio & TV Communications Equipment",
    "3674": "Semiconductors & Related Devices",
    "3711": "Motor Vehicles & Passenger Car Bodies",
    "4813": "Telephone Communications",
    "4812": "Radiotelephone Communications",
    "4841": "Cable & Other Pay TV Services",
    "4899": "Communications Services, NEC",
    "4911": "Electric Services",
    "4931": "Electric & Other Services Combined",
    "5045": "Computers & Peripheral Equipment",
    "5065": "Electronic Parts & Equipment",
    "5141": "Groceries, General Line",
    "5411": "Grocery Stores",
    "5812": "Eating Places",
    "6021": "National Commercial Banks",
    "6022": "State Commercial Banks",
    "6035": "Savings Institutions, Federally Chartered",
    "6211": "Security Brokers & Dealers",
    "6331": "Fire, Marine & Casualty Insurance",
    "7372": "Prepackaged Software",
    "7373": "Computer Integrated Systems Design",
    "7374": "Computer Processing & Data Preparation",
    "7375": "Information Retrieval Services",
    "7379": "Computer Related Services, NEC",
    "7389": "Business Services, NEC",
    "8731": "Commercial Physical & Biological Research",
    "8742": "Management Consulting Services",
    "8999": "Services, NEC",
    # Add more as needed
}

def get_sic_description(sic_code: str) -> str:
    """
    Return the industry description for a given SIC code.

    Args:
        sic_code (str): The SIC code as a string (e.g., "3711").

    Returns:
        str: The industry description if found, otherwise "Unknown Industry".

    Example:
        >>> get_sic_description("3711")
        'Motor Vehicles & Passenger Car Bodies'
    """
    return sic_map.get(sic_code, "Unknown Industry")
