"""
Factory for creating and managing Z-score models in Altman Z-Score analysis.

Provides a registry and factory methods for registering, retrieving, and instantiating Z-score model classes.
"""

from typing import Dict, Type, Tuple

from .base import ModelType, ZScoreModel
from .original import OriginalZScoreModel
from .zscore_model_private import PrivateManufacturingZScoreModel
from .zscore_model_financial import FinancialInstitutionZScoreModel
from .zscore_model_retail import RetailZScoreModel
from .zscore_model_em import EmergingMarketsZScoreModel


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

    _models: Dict[ModelType, Type[ZScoreModel]] = {
        ModelType.ORIGINAL: OriginalZScoreModel,
        ModelType.PRIVATE: PrivateManufacturingZScoreModel,
        ModelType.FINANCIAL: FinancialInstitutionZScoreModel,
        ModelType.RETAIL: RetailZScoreModel,
        ModelType.EM: EmergingMarketsZScoreModel,  # Register EM model
    }

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
        try:
            return model_class(model_type)
        except TypeError:
            return model_class()

    @classmethod
    def select_model_type(cls, company_data: Dict) -> Tuple[ModelType, str]:
        """
        Select the appropriate model type based on company characteristics.

        Args:
            company_data: Dictionary containing company information

        Returns:
            Tuple[ModelType, str]: Selected model type and reason for selection
        """
        from .industry_classifier import determine_model_type

        return determine_model_type(company_data)

    @classmethod
    def create_model_for_company(cls, company_data: Dict) -> Tuple[ZScoreModel, str]:
        """
        Create appropriate Z-Score model instance based on company characteristics.

        Args:
            company_data: Dictionary containing company information

        Returns:
            Tuple[ZScoreModel, str]: Model instance and reason for selection
        """
        model_type, reason = cls.select_model_type(company_data)
        model = cls.create_model(model_type)
        return model, reason


# Register available models
@ModelRegistry.register(ModelType.ORIGINAL)
class _OriginalModel(OriginalZScoreModel):
    pass


@ModelRegistry.register(ModelType.PRIVATE)
class _PrivateModel(PrivateManufacturingZScoreModel):
    pass


@ModelRegistry.register(ModelType.FINANCIAL)
class _FinancialModel(FinancialInstitutionZScoreModel):
    pass


@ModelRegistry.register(ModelType.RETAIL)
class _RetailModel(RetailZScoreModel):
    pass


@ModelRegistry.register(ModelType.EM)
class _EmergingMarketsModel(EmergingMarketsZScoreModel):
    pass
