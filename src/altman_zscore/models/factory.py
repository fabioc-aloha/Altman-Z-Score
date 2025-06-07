"""
Factory for creating and managing Z-score models in Altman Z-Score analysis.

Provides a registry and factory methods for registering, retrieving, and instantiating Z-score model classes.
"""

from typing import Dict, Type

from .base import ModelType, ZScoreModel
from .original import OriginalZScoreModel


class ModelRegistry:
    """Registry of available Z-score models.

    Methods:
        register(model_type):
            Decorator to register a model class.
        get_model_class(model_type):
            Get model class by type.
        create_model(model_type):
            Create and return a new model instance.
    """

    _models: Dict[ModelType, Type[ZScoreModel]] = {}

    @classmethod
    def register(cls, model_type: ModelType):
        """Decorator to register a model class.

        Args:
            model_type: Type of model to register

        Returns:
            Decorator function
        """

        def decorator(model_class: Type[ZScoreModel]) -> Type[ZScoreModel]:
            cls._models[model_type] = model_class
            return model_class

        return decorator

    @classmethod
    def get_model_class(cls, model_type: ModelType) -> Type[ZScoreModel]:
        """Get model class by type.

        Args:
            model_type: Type of model to get

        Returns:
            The model class for the given type

        Raises:
            KeyError: If model type not found in registry
        """
        if model_type not in cls._models:
            raise KeyError(f"No model registered for type {model_type}")
        return cls._models[model_type]

    @classmethod
    def create_model(cls, model_type: ModelType) -> ZScoreModel:
        """Create and return a new model instance.

        Args:
            model_type: Type of model to create

        Returns:
            A new instance of the requested model type

        Raises:
            KeyError: If model type not found in registry
        """
        model_class = cls.get_model_class(model_type)
        return model_class(model_type)  # Pass model_type to constructor


# Register available models
@ModelRegistry.register(ModelType.ORIGINAL)
class _OriginalModel(OriginalZScoreModel):
    pass
