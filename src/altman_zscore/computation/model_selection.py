from typing import Optional

from .constants import MODEL_COEFFICIENTS


def determine_zscore_model(profile):
    """
    Select the correct Altman Z-Score model based on company profile (industry, SIC, maturity, public/private, region).
    Args:
        profile: CompanyProfile object with industry, sic, is_public, is_emerging_market, maturity, etc.
    Returns:
        model_key (str): Key for MODEL_COEFFICIENTS/Z_SCORE_THRESHOLDS
    """
    # Prefer SIC-based override if available
    sic = getattr(profile, "sic", None) or None
    if sic:
        sic_key = f"sic_{sic}"
        if sic_key in MODEL_COEFFICIENTS:
            return sic_key
    # Use region
    if getattr(profile, "is_emerging_market", False):
        return "em"
    # Use maturity if available
    maturity = getattr(profile, "maturity", None)
    is_public = getattr(profile, "is_public", True)
    industry = (getattr(profile, "industry", "") or "").lower()
    # Map industry to model
    if industry in ["manufacturing", "hardware", "industrial"]:
        return "original" if is_public else "private"
    if industry in ["service", "software", "tech", "technology"]:
        return "service" if is_public else "private"
    # Use maturity for override
    if maturity:
        if maturity == "early-stage":
            return "private"
        if maturity == "growth":
            return "private" if not is_public else "original"
        if maturity == "mature":
            return "original" if is_public else "private"
    # Fallback
    return "original"


def select_zscore_model_by_sic(sic_code: str, is_public: bool = True, maturity: Optional[str] = None) -> str:
    """
    Map SIC code to the correct Altman Z-Score model type, using constants.py for overrides.
    Args:
        sic_code (str): SIC code as string or int
        is_public (bool): Whether the company is public
        maturity (Optional[str]): Optional maturity string (e.g., 'private', 'emerging')
    Returns:
        str: Model type key for constants.py
    """
    try:
        sic = int(str(sic_code))
    except Exception:
        return "original"  # fallback to original if SIC is invalid
    sic_key = f"sic_{sic}"
    if sic_key in MODEL_COEFFICIENTS:
        return sic_key
    if maturity and str(maturity).lower() in ["private", "emerging", "early-stage", "growth"]:
        return "private"
    if 2000 <= sic <= 3999:
        return "original" if is_public else "private"
    if (3570 <= sic <= 3579) or (3670 <= sic <= 3679) or (7370 <= sic <= 7379):
        return "service" if is_public else "private"
    if 6000 <= sic <= 6999:
        return "service" if is_public else "private"
    if 7000 <= sic <= 8999:
        return "service" if is_public else "private"
    return "original"  # fallback
