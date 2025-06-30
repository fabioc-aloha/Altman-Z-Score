"""
Markdown Utilities

Utility functions for converting markdown to HTML and other text formatting operations.
"""

import markdown
from typing import Optional


def markdown_to_html(markdown_text: Optional[str]) -> Optional[str]:
    """
    Convert markdown text to HTML with enhanced formatting.
    
    Args:
        markdown_text: The markdown text to convert
        
    Returns:
        HTML string or None if input is None
    """
    if not markdown_text:
        return None
    
    # Configure markdown extensions for better formatting
    md = markdown.Markdown(extensions=[
        'extra',      # Adds tables, footnotes, etc.
        'codehilite', # Syntax highlighting for code blocks
        'toc',        # Table of contents
        'nl2br',      # Convert newlines to <br> tags
        'sane_lists'  # Better list handling
    ])
    
    # Convert markdown to HTML
    html = md.convert(markdown_text)
    
    return html


def sanitize_html_for_display(html_text: Optional[str]) -> Optional[str]:
    """
    Sanitize HTML for safe display (basic cleanup).
    
    Args:
        html_text: The HTML text to sanitize
        
    Returns:
        Sanitized HTML string or None if input is None
    """
    if not html_text:
        return None
    
    # Basic cleanup - remove potentially harmful tags
    # This is a simple implementation; for production use, consider using bleach library
    dangerous_tags = ['<script', '</script>', '<iframe', '</iframe>']
    cleaned_html = html_text
    
    for tag in dangerous_tags:
        cleaned_html = cleaned_html.replace(tag, '')
    
    return cleaned_html


def format_ai_insights_for_html(ai_insights: Optional[str]) -> Optional[str]:
    """
    Format AI insights markdown for HTML display in reports.
    
    Args:
        ai_insights: AI-generated insights in markdown format
        
    Returns:
        HTML-formatted insights ready for display
    """
    if not ai_insights:
        return None
    
    # Convert markdown to HTML
    html_content = markdown_to_html(ai_insights)
    
    if not html_content:
        return None
    
    # Sanitize for safety
    sanitized_html = sanitize_html_for_display(html_content)
    
    # Add some basic styling classes for better integration
    if sanitized_html:
        # Add a wrapper div with styling class
        styled_html = f'<div class="ai-insights-content">{sanitized_html}</div>'
        return styled_html
    
    return sanitized_html
