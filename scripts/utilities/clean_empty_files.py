"""
Empty File Cleanup Script
Removes empty files that may reappear after VS Code restarts
"""

import os
import glob
from pathlib import Path


def find_empty_files(directory=".", exclude_patterns=None):
    """Find all empty files in the directory tree."""
    if exclude_patterns is None:
        exclude_patterns = [
            ".venv",
            ".git", 
            "__pycache__",
            ".cache",
            ".pytest_cache",
            "node_modules"
        ]
    
    empty_files = []
    
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from dirs list (modifies in-place)
        dirs[:] = [d for d in dirs if d not in exclude_patterns]
        
        # Skip if we're in an excluded directory
        if any(excl in root for excl in exclude_patterns):
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if file is empty
            try:
                if os.path.getsize(file_path) == 0:
                    empty_files.append(file_path)
            except (OSError, IOError):
                # Skip files we can't read
                continue
    
    return empty_files


def clean_empty_files(directory=".", dry_run=True, exclude_patterns=None):
    """Clean up empty files."""
    empty_files = find_empty_files(directory, exclude_patterns)
    
    if not empty_files:
        print("✅ No empty files found!")
        return
    
    print(f"Found {len(empty_files)} empty files:")
    print("=" * 50)
    
    removed_count = 0
    for file_path in empty_files:
        rel_path = os.path.relpath(file_path, directory)
        
        if dry_run:
            print(f"Would remove: {rel_path}")
        else:
            try:
                os.remove(file_path)
                print(f"✅ Removed: {rel_path}")
                removed_count += 1
            except (OSError, IOError) as e:
                print(f"❌ Failed to remove {rel_path}: {e}")
    
    print("=" * 50)
    if dry_run:
        print(f"Dry run complete. Found {len(empty_files)} empty files.")
        print("Run with --clean to actually remove them.")
    else:
        print(f"Cleanup complete. Removed {removed_count}/{len(empty_files)} files.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Find and clean empty files")
    parser.add_argument("--clean", action="store_true", 
                       help="Actually remove empty files (default is dry run)")
    parser.add_argument("--directory", default=".", 
                       help="Directory to scan (default: current)")
    
    args = parser.parse_args()
    
    print("🧹 Empty File Cleanup Tool")
    print("=" * 50)
    
    if args.clean:
        print("⚠️  CLEANUP MODE: Empty files will be REMOVED")
    else:
        print("🔍 DRY RUN MODE: No files will be removed")
    
    print(f"📁 Scanning directory: {os.path.abspath(args.directory)}")
    print()
    
    clean_empty_files(args.directory, dry_run=not args.clean)


if __name__ == "__main__":
    main()
