"""
model_validation.py
------------------
Validation logic for Z-Score model selection and appropriateness.
"""

from typing import Dict, Tuple

from ..models.base import ModelType

# Industry classification for validation
INDUSTRY_MODEL_MATRIX = {
    'Banks': {
        'appropriate': [ModelType.FINANCIAL],
        'potentially_suitable': [ModelType.EMERGING],
        'not_recommended': [ModelType.RETAIL, ModelType.ORIGINAL, ModelType.PRIVATE]
    },
    'Capital Markets': {
        'appropriate': [ModelType.FINANCIAL],
        'potentially_suitable': [ModelType.EMERGING],
        'not_recommended': [ModelType.RETAIL, ModelType.ORIGINAL, ModelType.PRIVATE]
    },
    'Insurance': {
        'appropriate': [ModelType.FINANCIAL],
        'potentially_suitable': [ModelType.EMERGING],
        'not_recommended': [ModelType.RETAIL, ModelType.ORIGINAL, ModelType.PRIVATE]
    },
    'Retail': {
        'appropriate': [ModelType.RETAIL],
        'potentially_suitable': [ModelType.ORIGINAL, ModelType.PRIVATE],
        'not_recommended': [ModelType.FINANCIAL]
    },
    'Technology': {
        'appropriate': [ModelType.EMERGING],
        'potentially_suitable': [ModelType.ZETA],
        'not_recommended': [ModelType.RETAIL, ModelType.FINANCIAL]
    },
    'Manufacturing': {
        'appropriate': [ModelType.ORIGINAL, ModelType.PRIVATE],
        'potentially_suitable': [ModelType.ZETA],
        'not_recommended': [ModelType.FINANCIAL, ModelType.RETAIL]
    },
    'Services': {
        'appropriate': [ModelType.EMERGING],
        'potentially_suitable': [ModelType.ZETA],
        'not_recommended': [ModelType.RETAIL, ModelType.FINANCIAL]
    }
}

def validate_model_appropriateness(
    company_data: Dict,
    model_type: ModelType
) -> Tuple[bool, str, str]:
    """
    Validate the appropriateness of a Z-Score model for a given company.
    
    Args:
        company_data: Dictionary containing company information
        model_type: The ModelType to validate
        
    Returns:
        Tuple[bool, str, str]: (is_appropriate, warning_level, message)
        where warning_level is one of: 'none', 'caution', 'warning'
    """
    sector = company_data.get('sector', '').strip()
    age = company_data.get('age', 0)
    company_data.get('market_cap', 0)
    
    # Match sector to industry category
    industry = _map_sector_to_industry(sector)
    if not industry:
        return True, 'caution', f"Unknown industry for sector '{sector}'. Model appropriateness cannot be fully validated."
    
    # Get appropriateness levels for the industry
    matrix = INDUSTRY_MODEL_MATRIX.get(industry, {})
    
    # Check appropriateness
    if model_type in matrix.get('appropriate', []):
        return True, 'none', "Model is appropriate for this company type."
    
    if model_type in matrix.get('potentially_suitable', []):
        return True, 'caution', f"Model is potentially suitable but not optimal for {industry} companies."
    
    if model_type in matrix.get('not_recommended', []):
        return False, 'warning', f"Model is not recommended for {industry} companies. Consider using {', '.join([m.value for m in matrix['appropriate']])} instead."
    
    # Special cases
    if model_type == ModelType.ZETA and age < 5:
        return False, 'warning', "Zeta model requires 5+ years of history. Consider using another model."
    
    return True, 'caution', "Model appropriateness could not be definitively determined."

def _map_sector_to_industry(sector: str) -> str:
    """Map a specific sector to a general industry category."""
    sector = sector.lower()
    
    if any(x in sector for x in ['bank', 'capital market', 'financial', 'insurance']):
        return 'Banks'
    if any(x in sector for x in ['retail', 'store', 'merchandise']):
        return 'Retail'
    if any(x in sector for x in ['technology', 'software', 'internet']):
        return 'Technology'
    if any(x in sector for x in ['manufact', 'industrial', 'auto', 'aerospace']):
        return 'Manufacturing'
    if any(x in sector for x in ['service', 'consulting', 'healthcare']):
        return 'Services'
    
    return None
