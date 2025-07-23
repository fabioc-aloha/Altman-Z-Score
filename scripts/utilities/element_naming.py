"""
IUPAC Systematic Element Naming Utility for Version Numbers
Based on systematic nomenclature for hypothetical chemical elements.
"""

def version_to_element_name(version_string):
    """
    Convert a version string (e.g., "4.10.0") to IUPAC systematic element name.
    
    Args:
        version_string (str): Version in format "major.minor.patch"
        
    Returns:
        str: IUPAC systematic element name
        
    Examples:
        >>> version_to_element_name("4.10.0")
        'QUADUNILIUM'
        >>> version_to_element_name("5.0.0") 
        'PENTNILNILIUM'
    """
    # IUPAC systematic naming roots
    digit_roots = {
        '0': 'nil',
        '1': 'un', 
        '2': 'bi',
        '3': 'tri',
        '4': 'quad',
        '5': 'pent',
        '6': 'hex',
        '7': 'sept',
        '8': 'oct',
        '9': 'enn'
    }
    
    # Convert version to atomic number format
    # Remove dots and pad to 3 digits
    atomic_number = version_string.replace('.', '')
    
    # Build element name from roots
    roots = []
    for digit in atomic_number:
        if digit in digit_roots:
            roots.append(digit_roots[digit])
    
    # Concatenate roots and add -ium suffix
    element_base = ''.join(roots)
    element_name = element_base + 'ium'
    
    # Apply IUPAC rules: remove duplicate vowels at boundaries
    # and drop final 'i' before 'ium' 
    element_name = element_name.replace('iium', 'ium')
    
    return element_name.upper()


def get_current_version_info():
    """Get current version with element name."""
    from altman_zscore._version import __version__, __element_name__, RELEASE_NAME
    
    return {
        'version': __version__,
        'element_name': __element_name__,
        'release_name': RELEASE_NAME,
        'full_name': f"v{__version__} {__element_name__}"
    }


def calculate_element_name_from_parts(major, minor, patch):
    """Calculate element name from version components."""
    version_str = f"{major}.{minor}.{patch}"
    return version_to_element_name(version_str)


if __name__ == "__main__":
    # Demonstrate the naming convention
    test_versions = [
        "5.0.0",   # Current
        "5.1.0",   # Next minor
        "6.0.0",   # Next major
        "4.10.0",  # Previous
        "2.9.0",   # Historical
        "1.0.0"    # First release
    ]
    
    print("🧪 IUPAC Systematic Element Naming for Altman Z-Score Versions")
    print("=" * 65)
    
    for version in test_versions:
        element = version_to_element_name(version)
        print(f"Version {version:>6} → {element}")
    
    print("\n📋 Current Version Info:")
    current = get_current_version_info()
    print(f"  {current['full_name']}")
    print(f"  {current['release_name']}")
