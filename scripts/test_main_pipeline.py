#!/usr/bin/env python3
"""Test script to verify main analysis pipeline functionality."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import the main function from the entry point
from main import main

def test_main_pipeline():
    """Test the main analysis pipeline with a sample ticker."""
    print("Testing main analysis pipeline with ticker MSFT...")
    
    # Set up sys.argv with the ticker
    sys.argv = ["main.py", "MSFT"]
    
    try:
        # Run the main function
        main()
        print("\nAnalysis pipeline completed successfully!")
        return True
    except Exception as e:
        print(f"\nError in analysis pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_pipeline()
    if not success:
        sys.exit(1)
