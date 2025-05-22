"""Response validation utilities."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar
from .base import BaseResponse, ResponseStatus, ValidationError, DataQualityMetrics

T = TypeVar('T', bound=BaseResponse)

class ResponseValidator:
    """Validates API responses against schemas."""
    
    @staticmethod
    def validate(data: Dict[str, Any], schema_class: Type[T]) -> T:
        """
        Validate response data against schema.
        
        Args:
            data: Response data to validate
            schema_class: Schema class to validate against
            
        Returns:
            Validated response object
            
        Raises:
            ValidationError if validation fails
        """
        errors: List[ValidationError] = []
        
        # Check required fields
        required_fields = [
            field.name for field in schema_class.__dataclass_fields__.values()
            if not field.default and not field.default_factory
        ]
        
        for field in required_fields:
            if field not in data:
                errors.append(ValidationError(
                    field=field,
                    message=f"Missing required field: {field}",
                    value=None,
                    code="missing_required_field"
                ))
        
        if errors:
            raise ValueError(
                f"Validation failed: {[e.message for e in errors]}"
            )
        
        # Create response object
        try:
            response = schema_class.from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to create response object: {e}")
        
        return response
    
    @staticmethod
    def validate_data_quality(response: BaseResponse, required_quality: float = 0.8) -> bool:
        """
        Validate data quality metrics.
        
        Args:
            response: Response to validate
            required_quality: Minimum required quality score (0-1)
            
        Returns:
            True if quality requirements are met
        """
        if not hasattr(response, 'data_quality'):
            return False
            
        quality = response.data_quality
        return all([
            quality.completeness >= required_quality,
            quality.accuracy >= required_quality,
            quality.timeliness >= required_quality,
            quality.consistency >= required_quality
        ])
    
    @staticmethod
    def normalize_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize response data to standard format."""
        # Add standard fields if missing
        if 'status' not in data:
            data['status'] = 'error' if data.get('errors') else 'success'
            
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
            
        if 'dataQuality' not in data:
            data['dataQuality'] = {
                'completeness': 1.0,
                'accuracy': 1.0,
                'timeliness': 1.0,
                'consistency': 1.0
            }
            
        if 'requestId' not in data:
            data['requestId'] = datetime.now().strftime('%Y%m%d%H%M%S')
        
        return data
