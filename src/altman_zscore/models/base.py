"""
Base classes for Z-score models in Altman Z-Score analysis.

Defines abstract base classes and shared data structures for all Z-score model implementations, providing a common interface for model creation, validation, and computation.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Enumeration of Z-score model types available."""

    ORIGINAL = "original"
    PRIVATE = "private"
    SERVICE = "service"
    EMERGING = "emerging"


@dataclass
class ModelMetrics:
    """Model performance and validation metrics.

    Attributes:
        accuracy (float): Model accuracy.
        precision (float): Model precision.
        recall (float): Model recall.
        f1_score (float): Model F1 score.
        sample_size (int): Number of samples used for validation.
        last_validation (datetime): Date of last validation.
        validation_period (str): Period covered by validation.
    """

    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    sample_size: int = 0
    last_validation: datetime = datetime.now()
    validation_period: str = ""


@dataclass
class ModelVersion:
    """Model version information.

    Attributes:
        version (str): Version string.
        release_date (datetime): Release date of the version.
        changes (list): List of changes in this version.
        validation_metrics (ModelMetrics): Validation metrics for this version.
        min_data_requirements (list): Minimum required data fields for this version.
    """

    version: str
    release_date: datetime
    changes: List[str]
    validation_metrics: ModelMetrics
    min_data_requirements: List[str]


class ZScoreModel(ABC):
    """Abstract base class for Z-score models.

    Methods:
        calculate_zscore(financial_data):
            Calculate Z-score from financial data.
        validate_input(financial_data):
            Validate input data requirements.
        get_required_metrics():
            Get list of required financial metrics.
        update_metrics(metrics):
            Update model performance metrics.
        add_version(version):
            Add new model version.
        get_latest_version():
            Get latest model version.
    """

    def __init__(self, model_type: ModelType):
        """Initialize Z-score model.

        Args:
            model_type: Type of Z-score model
        """
        self.model_type = model_type
        self.metrics = ModelMetrics()
        self.versions: List[ModelVersion] = []
        self._validate_model_configuration()

    @abstractmethod
    def calculate_zscore(self, financial_data: Dict[str, Decimal]) -> float:
        """Calculate Z-score from financial data.

        Args:
            financial_data: Dictionary of financial metrics

        Returns:
            Calculated Z-score value
        """

    @abstractmethod
    def validate_input(self, financial_data: Dict[str, Decimal]) -> List[str]:
        """Validate input data requirements.

        Args:
            financial_data: Dictionary of financial metrics

        Returns:
            List of validation error messages, empty if valid
        """

    @abstractmethod
    def get_required_metrics(self) -> List[str]:
        """Get list of required financial metrics.

        Returns:
            List of required metric names
        """

    def _validate_model_configuration(self) -> None:
        """Validate model configuration and coefficients.

        Raises:
            ValueError: If required metrics are not defined.
        """
        if not self.get_required_metrics():
            raise ValueError(f"Model {self.model_type} has no required metrics defined")

    def update_metrics(self, metrics: ModelMetrics) -> None:
        """Update model performance metrics.

        Args:
            metrics (ModelMetrics): New model metrics.
        """
        self.metrics = metrics
        logger.info(
            f"Updated metrics for model {self.model_type}: "
            f"accuracy={metrics.accuracy:.3f}, "
            f"precision={metrics.precision:.3f}, "
            f"recall={metrics.recall:.3f}"
        )

    def add_version(self, version: ModelVersion) -> None:
        """Add new model version.

        Args:
            version (ModelVersion): New version information.
        """
        self.versions.append(version)
        logger.info(f"Added version {version.version} to model {self.model_type}")

    def get_latest_version(self) -> Optional[ModelVersion]:
        """Get latest model version.

        Returns:
            ModelVersion or None: Latest version information or None if no versions.
        """
        return self.versions[-1] if self.versions else None
