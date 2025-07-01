#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix HTML CSS References

This script scans web/*.html files and fixes any references to CSS files
that aren't in web/assets/ by updating them to use assets/dashboard_common.css.
"""

import os
import sys
import re
from pathlib import Path

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
sys.path.append(PROJECT_ROOT)

# Import from utility modules if needed
from assets_manager import ensure_assets_folder

def main():
    """Main execution function"""
    # Ensure we have the assets folder with all required CSS/HTML files
    ensure_assets_folder()
    
    # Define paths
    web_dir = os.path.join(PROJECT_ROOT, "web")
    assets_dir = os.path.join(web_dir, "assets")
    
    # Find all HTML files in the web directory
    html_files = [f for f in os.listdir(web_dir) if f.endswith('.html')]
    
    fixed_count = 0
    for html_file in html_files:
        html_path = os.path.join(web_dir, html_file)
        
        # Read the file content
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file references a CSS file that's not in assets/
        css_pattern = r'<link\s+rel="stylesheet"\s+href="([^"]+\.css)"'
        css_matches = re.findall(css_pattern, content)
        
        needs_fix = False
        for css_match in css_matches:
            if not css_match.startswith('assets/'):
                print(f"Found invalid CSS reference in {html_file}: {css_match}")
                needs_fix = True
                break
        
        if needs_fix:
            # Replace CSS references with standardized reference to assets/dashboard_common.css
            updated_content = re.sub(
                r'<link\s+rel="stylesheet"\s+href="([^"]+\.css)"',
                r'<link rel="stylesheet" href="assets/dashboard_common.css"',
                content
            )
            
            # Write the updated content back
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            fixed_count += 1
            print(f"Fixed CSS reference in {html_file}")
    
    if fixed_count > 0:
        print(f"\nFixed CSS references in {fixed_count} HTML files")
    else:
        print("\nAll HTML files already using correct CSS references")

if __name__ == "__main__":
    main()
