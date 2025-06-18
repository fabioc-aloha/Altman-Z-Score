#!/usr/bin/env python3
"""
Run Ford analysis with debug logging
"""
import logging
import sys
import os

# Set up debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import and run main
sys.path.insert(0, os.path.dirname(__file__))
import main

if __name__ == "__main__":
    main.main()
