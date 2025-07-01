#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create a default company logo placeholder for missing logos
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_default_logo(output_path):
    """Create a default company logo placeholder."""
    
    # Create a 128x128 image with white background
    img = Image.new('RGBA', (128, 128), (240, 240, 240, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw a rectangle frame
    draw.rectangle([(10, 10), (118, 118)], outline=(100, 100, 100), width=3)
    
    # Add "LOGO" text - using simple approach without custom font
    # Draw "LOGO" text manually
    # L
    draw.rectangle([(30, 40), (40, 80)], fill=(100, 100, 100))
    draw.rectangle([(40, 70), (60, 80)], fill=(100, 100, 100))
    
    # O
    draw.ellipse([(60, 40), (90, 80)], outline=(100, 100, 100), width=6)
    
    # G
    draw.arc([(90, 40), (120, 80)], 180, 0, fill=(100, 100, 100), width=6)
    draw.line([(105, 60), (120, 60)], fill=(100, 100, 100), width=6)
    draw.line([(120, 60), (120, 80)], fill=(100, 100, 100), width=6)
    
    # O
    #draw.ellipse([(120, 40), (150, 80)], outline=(100, 100, 100), width=6)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the image
    img.save(output_path)
    
    print(f"Default logo created at {output_path}")

if __name__ == "__main__":
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_path = os.path.join(project_root, "web", "assets", "default_logo.png")
    
    create_default_logo(output_path)
