from typing import Optional

def determine_zscore_model(profile):
    """
    Select the correct Altman Z-Score model based on company profile (industry, maturity, public/private).
    Args:
        profile: Company profile object with at least 'industry' and 'is_public' attributes.
    Returns:
        Model string: 'original', 'private', 'service', 'public', or 'em'
    """
    industry = getattr(profile, 'industry', '').lower() if hasattr(profile, 'industry') else ''
    is_public = getattr(profile, 'is_public', True) if hasattr(profile, 'is_public') else True
    is_emerging = getattr(profile, 'is_emerging_market', False) if hasattr(profile, 'is_emerging_market') else False

    if is_emerging:
        return 'em'
    if industry in ['manufacturing', 'hardware', 'industrial']:
        return 'original' if is_public else 'private'
    if industry in ['service', 'software', 'tech', 'technology']:
        return 'public' if is_public else 'private'
    # Default fallback
    return 'original'

def select_zscore_model_by_sic(sic_code: str, is_public: bool = True, maturity: Optional[str] = None) -> str:
    """
    Map SIC code to the correct Altman Z-Score model type.
    Args:
        sic_code (str): SIC code as string or int
        is_public (bool): Whether the company is public
        maturity (Optional[str]): Optional maturity string (e.g., 'private', 'emerging')
    Returns:
        str: Model type ('original', 'private', 'service', 'public', 'tech', 'em')
    """
    try:
        sic = int(str(sic_code))
    except Exception:
        return 'original'  # fallback to original if SIC is invalid
    # Explicit maturity override
    if maturity and str(maturity).lower() in ['private', 'emerging']:
        return 'private'
    # Manufacturing (Original/Private): 2000-3999
    if 2000 <= sic <= 3999:
        return 'original' if is_public else 'private'
    # Tech: 3570-3579, 3670-3679, 7370-7379
    if (3570 <= sic <= 3579) or (3670 <= sic <= 3679) or (7370 <= sic <= 7379):
        return 'tech' if is_public else 'private'
    # Financial Services: 6000-6999
    if 6000 <= sic <= 6999:
        return 'service' if is_public else 'private'
    # General Services: 7000-8999
    if 7000 <= sic <= 8999:
        return 'service' if is_public else 'private'
    # Emerging markets (if flagged elsewhere)
    # Add more rules as needed
    return 'original'  # fallback
