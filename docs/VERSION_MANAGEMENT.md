# Version Management

## Centralized Version Control

The Altman Z-Score project uses a centralized version management system to ensure consistency across all components.

### Single Source of Truth

**File: `altman_zscore/_version.py`**
- Contains the authoritative version number
- Includes version metadata (release date, name, etc.)
- All other files import from this location

### Version Usage

The version is automatically imported in:
- `altman_zscore/__init__.py` - Package version
- `main.py` - Script version  
- `altman_zscore/main_pipeline.py` - Pipeline version
- `altman_zscore/models/data_models.py` - Data model version

### Updating Versions

#### Manual Update
Edit `altman_zscore/_version.py`:
```python
__version__ = "4.3.0"
__version_info__ = (4, 3, 0)
RELEASE_DATE = "2025-06-27"
RELEASE_NAME = "New Feature Release"
```

#### Using Version Manager Script
```bash
# Update version
python scripts/version_manager.py --version 4.3.0

# Check all imports work
python scripts/version_manager.py --check

# Show version info
python scripts/version_manager.py --info
```

### Benefits

1. **Single Update Point**: Change version in one file only
2. **Consistency**: All components use the same version automatically
3. **Validation**: Version manager script validates imports
4. **Documentation**: Clear version metadata in one place

### Migration from Old System

Previously, version numbers were scattered across:
- `altman_zscore/__init__.py`
- `main.py` 
- `altman_zscore/main_pipeline.py`
- `altman_zscore/models/data_models.py`
- `altman_zscore/layers/__init__.py`
- `altman_zscore/layers/analysis/__init__.py`
- `altman_zscore/layers/zscore_calculation/__init__.py`

Now all import from the centralized `_version.py` file.
