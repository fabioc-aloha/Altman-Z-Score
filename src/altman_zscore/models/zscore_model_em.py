from .base import ZScoreModel, ModelType
from altman_zscore.computation.formulas import altman_zscore_em

class EmergingMarketsZScoreModel(ZScoreModel):
    """Z-Score model for Emerging Markets (Altman EM-Score)."""
    model_type = ModelType.EM

    def compute(self, metrics: dict):
        return altman_zscore_em(metrics)
