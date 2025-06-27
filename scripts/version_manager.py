#!/usr/bin/env python3
"""
Version Management Utility

This script helps manage version numbers across the Altman Z-Score project.
It provides utilities to:
- Update the version number in the centralized location
- Validate that all imports are working correctly
- Display current version information

Usage:
    python scripts/version_manager.py --version 4.3.0
    python scripts/version_manager.py --check
    python scripts/version_manager.py --info
"""

import argparse
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def update_version(new_version: str):
    """Update the version in _version.py"""
    version_file = project_root / "altman_zscore" / "_version.py"
    
    if not version_file.exists():
        print(f"Error: Version file not found at {version_file}")
        return False
    
    # Read current content
    with open(version_file, 'r') as f:
        content = f.read()
    
    # Update version
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('__version__ = '):
            updated_lines.append(f'__version__ = "{new_version}"')
        elif line.startswith('__version_info__ = '):
            # Parse version to create tuple
            parts = new_version.split('.')
            if len(parts) == 3:
                try:
                    major, minor, patch = map(int, parts)
                    updated_lines.append(f'__version_info__ = ({major}, {minor}, {patch})')
                except ValueError:
                    print(f"Error: Invalid version format: {new_version}")
                    return False
            else:
                print(f"Error: Version must be in format X.Y.Z: {new_version}")
                return False
        else:
            updated_lines.append(line)
    
    # Write updated content
    with open(version_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"✅ Version updated to {new_version}")
    return True

def check_version_imports():
    """Check that version imports are working correctly"""
    try:
        from altman_zscore import __version__
        print(f"✅ altman_zscore.__version__ = {__version__}")
        
        from altman_zscore._version import __version__, __version_info__
        print(f"✅ altman_zscore._version.__version__ = {__version__}")
        print(f"✅ altman_zscore._version.__version_info__ = {__version_info__}")
        
        # Check main.py can import it
        sys.path.insert(0, str(project_root))
        import main
        print(f"✅ main.__version__ = {main.__version__}")
        
        print("\n✅ All version imports working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Version import error: {e}")
        return False

def show_version_info():
    """Display comprehensive version information"""
    try:
        from altman_zscore._version import __version__, __version_info__, RELEASE_DATE, RELEASE_NAME
        
        print("📋 VERSION INFORMATION")
        print("=" * 50)
        print(f"Version: {__version__}")
        print(f"Version Info: {__version_info__}")
        print(f"Release Date: {RELEASE_DATE}")
        print(f"Release Name: {RELEASE_NAME}")
        print()
        
        # Show where version is used
        print("📍 VERSION USAGE LOCATIONS:")
        print("- altman_zscore/_version.py (source of truth)")
        print("- altman_zscore/__init__.py (imports from _version)")
        print("- main.py (imports from _version)")
        print("- altman_zscore/main_pipeline.py (imports from _version)")
        print("- altman_zscore/models/data_models.py (imports from _version)")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting version info: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Version Management Utility for Altman Z-Score Project",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version",
        type=str,
        help="Update version number (format: X.Y.Z)"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that all version imports are working"
    )
    
    parser.add_argument(
        "--info",
        action="store_true", 
        help="Display current version information"
    )
    
    args = parser.parse_args()
    
    if args.version:
        success = update_version(args.version)
        if success:
            print("\n🔍 Checking imports after update...")
            check_version_imports()
        return success
    
    elif args.check:
        return check_version_imports()
    
    elif args.info:
        return show_version_info()
    
    else:
        parser.print_help()
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
