# Legacy Code Archive

This directory contains archived legacy code from previous versions of the Altman Z-Score platform that has been migrated to the new architecture.

## Archived Components

### src_archived/ (Archived: v4.2.0 Development)
**Original Path**: `src/`
**Archive Date**: Version 4.2.0 Development Phase
**Status**: Fully migrated to new architecture

The complete legacy `src/` directory containing the original implementation. All functionality has been migrated to the new `altman_zscore/` architecture:

- **Data Models**: Migrated to `altman_zscore/models/data_models.py`
- **Core Logic**: Migrated to `altman_zscore/layers/`
- **API Clients**: Migrated to `altman_zscore/common/`
- **Configuration**: Migrated to `altman_zscore/common/config.py`

### Migration Notes

#### Data Models
- `ZScoreResult` and related models moved from `src.altman_zscore.models.financial_metrics` to `altman_zscore.models.data_models`
- Model signatures updated and enhanced with additional validation

#### Import Changes
```python
# Old imports (legacy)
from src.altman_zscore.models.financial_metrics import ZScoreResult
from src.altman_zscore.api import FinnhubClient

# New imports (v4.2.0+)
from altman_zscore.models.data_models import ZScoreResult
from altman_zscore.common.api_clients import FinnhubClient
```

#### Dependencies Removed
All tests and code have been updated to use the new architecture. The legacy `src/` directory is no longer required for any functionality.

## Restoration (If Needed)

If any legacy code needs to be referenced or restored:

1. Check `src_archived/` for the original implementation
2. Review migration mappings above
3. Adapt to new architecture patterns before integration

## Cleanup

This archive can be safely removed once v4.2.0 is stable and all stakeholders confirm no legacy code reference is needed.
