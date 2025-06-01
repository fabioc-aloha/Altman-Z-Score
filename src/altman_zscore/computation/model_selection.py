# model_selection.py

from typing import Optional
from .constants import MODEL_COEFFICIENTS, MODEL_ALIASES


def select_zscore_model(
    sic_code: Optional[int],
    is_public: bool = True,
    is_emerging: bool = False
) -> str:
    """
    Select and return one of the canonical Altman Z-Score model keys:
      - "original"         : Public manufacturing (SIC 2000–3999)
      - "private"          : Private manufacturing (SIC 2000–3999)
      - "service"          : Public non-manufacturing/service/transport (SIC 4000–4999,
                             6000–6999, 7000–8999, tech subranges)
      - "service_private"  : Private non-manufacturing/service/transport
      - "tech"             : Alias for public non-manufacturing ("service")
      - "em"               : Emerging Market (any SIC, if flagged)
    If a specific SIC override (e.g. "sic_4512") exists in MODEL_COEFFICIENTS, it is returned directly.
    """
    # 1) Emerging market override
    if is_emerging:
        return "em"

    # 2) Check for explicit SIC override entry (e.g. MODEL_COEFFICIENTS["sic_4512"])
    if isinstance(sic_code, int):
        sic_key = f"sic_{sic_code}"
        if sic_key in MODEL_COEFFICIENTS:
            return sic_key

    # 3) Manufacturing (SIC 2000–3999)
    if isinstance(sic_code, int) and 2000 <= sic_code <= 3999:
        return "original" if is_public else "private"

    # 4) Non-manufacturing / Service / Transport / Utilities / Tech
    if isinstance(sic_code, int) and (
        4000 <= sic_code <= 4999   # Transport / Service / Utilities
        or 6000 <= sic_code <= 6999  # Finance / Insurance
        or 7000 <= sic_code <= 8999  # Services / Retail / Tech
        or 3570 <= sic_code <= 3579  # Tech subrange 1
        or 3670 <= sic_code <= 3679  # Tech subrange 2
        or 7370 <= sic_code <= 7379  # Tech subrange 3
    ):
        return "service" if is_public else "service_private"

    # 5) Tech fallback: treat "tech" as alias to "service"
    #    (If industry metadata is available, you could detect "tech" here and return "tech".)
    #    Otherwise, default to "original" if nothing else matches.
    return "original"


def canonicalize_model_key(key: str) -> str:
    """
    Given a potentially legacy or aliased model key (e.g. "public_service", "private_mfg", "emerging"),
    return the canonical key by checking MODEL_ALIASES. If no alias exists, return the key itself.
    """
    return MODEL_ALIASES.get(key, key)


def determine_zscore_model(profile) -> str:
    """
    Legacy compatibility function: Select Z-Score model based on company profile.
    Maps to select_zscore_model() with profile attributes.
    """
    sic_code = getattr(profile, 'sic_code', None)
    is_public = getattr(profile, 'is_public', True)
    is_emerging = getattr(profile, 'is_emerging_market', False)
    
    # Convert string SIC to int if needed
    if isinstance(sic_code, str) and sic_code.isdigit():
        sic_code = int(sic_code)
    elif not isinstance(sic_code, int):
        sic_code = None
        
    return select_zscore_model(sic_code, is_public, is_emerging)


def select_zscore_model_by_sic(sic_code: str, is_public: bool = True, maturity: Optional[str] = None) -> str:
    """
    Legacy compatibility function: Select Z-Score model based on SIC code string.
    Maps to select_zscore_model() with converted SIC code.
    """
    # Convert string SIC to int if possible
    if sic_code and sic_code.isdigit():
        sic_int = int(sic_code)
    else:
        sic_int = None
    
    # Map maturity to is_emerging flag
    is_emerging = (maturity == "emerging") if maturity else False
    
    return select_zscore_model(sic_int, is_public, is_emerging)
