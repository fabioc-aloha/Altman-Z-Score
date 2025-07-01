"""
HTML Portfolio Generator - Template-based HTML generation for portfolio dashboards

This module provides template-based HTML generation for various portfolio types,
eliminating code duplication across the generate_*.py scripts.

Key Features:
- Reusable HTML templates with consistent styling
- Dynamic company card generation
- Risk category color coding
- Responsive grid layouts
- Customizable themes for different portfolio types
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from string import Template

from ..common.logging_config import get_logger
from .._version import __version__

logger = get_logger(__name__)


class HTMLPortfolioGenerator:
    """Generate HTML dashboards for different portfolio types."""
    
    def __init__(self, base_dir: str = "."):
        """
        Initialize HTML generator.
        
        Args:
            base_dir: Base directory for output files
        """
        self.base_dir = Path(base_dir)
        self.logger = get_logger(self.__class__.__name__)
        self.templates_dir = Path(__file__).parent / "templates"
        
        # Ensure output directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Load templates
        self._load_templates()
        
    def _load_templates(self):
        """Load HTML and CSS templates from files."""
        try:
            # Load main HTML template
            main_template_path = self.templates_dir / "portfolio_template.html"
            with open(main_template_path, 'r', encoding='utf-8') as f:
                self.main_template = Template(f.read())
                
            # Load company card template
            card_template_path = self.templates_dir / "company_card_template.html"
            with open(card_template_path, 'r', encoding='utf-8') as f:
                self.card_template = Template(f.read())
                
            # Load CSS template
            css_template_path = self.templates_dir / "portfolio_styles.css"
            with open(css_template_path, 'r', encoding='utf-8') as f:
                self.css_template = Template(f.read())
                
            self.logger.info("Templates loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load templates: {e}")
            # Fallback to inline templates if files don't exist
            self._create_fallback_templates()
        
    def generate_portfolio_html(
        self,
        companies: List[Dict[str, Any]], 
        portfolio_type: str,
        title: str,
        description: str,
        output_filename: str,
        color_scheme: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate HTML portfolio dashboard.
        
        Args:
            companies: List of company data dictionaries
            portfolio_type: Type of portfolio (e.g., 'strong_buy', 'value', 'growth')
            title: Page title
            description: Portfolio description
            output_filename: Output HTML filename
            color_scheme: Optional custom color scheme
            
        Returns:
            str: Path to generated HTML file
        """
        if not companies:
            self.logger.error(f"No company data to generate HTML for {portfolio_type}")
            return ""
            
        # Use default color scheme if none provided
        if color_scheme is None:
            color_scheme = self._get_default_color_scheme(portfolio_type)
            
        current_date = datetime.now().strftime("%B %d, %Y")
        company_count = len(companies)
        
        # Get top companies for highlighting
        top_companies = companies[:3] if len(companies) >= 3 else companies
        
        # Generate HTML content
        html_content = self._generate_html_template(
            companies=companies,
            portfolio_type=portfolio_type,
            title=title,
            description=description,
            current_date=current_date,
            company_count=company_count,
            top_companies=top_companies,
            color_scheme=color_scheme
        )
        
        # Write HTML file
        output_path = self.base_dir / output_filename
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"Generated {portfolio_type} portfolio HTML: {output_path}")
            return str(output_path)
        except Exception as e:
            self.logger.error(f"Failed to write HTML file {output_path}: {e}")
            return ""
    
    def _generate_html_template(
        self,
        companies: List[Dict[str, Any]],
        portfolio_type: str,
        title: str,
        description: str,
        current_date: str,
        company_count: int,
        top_companies: List[Dict[str, Any]],
        color_scheme: Dict[str, str]
    ) -> str:
        """Generate the complete HTML template using external template files."""
        
        # Generate CSS content with color scheme
        css_content = self._generate_css_content(color_scheme)
        
        # Save CSS to a temporary file for the template
        css_filename = f"portfolio_{portfolio_type}_styles.css"
        css_path = self.base_dir / css_filename
        
        try:
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
        except Exception as e:
            self.logger.warning(f"Failed to write CSS file: {e}")
            css_filename = ""  # Fallback to inline styles
        
        # Calculate statistics
        safe_count = len([c for c in companies if c.get('z_score', 0) > 2.99])
        avg_zscore = sum(c.get('z_score', 0) for c in companies) / len(companies) if companies else 0
        
        # Generate summary text
        summary_text = self._generate_summary_text(top_companies, portfolio_type)
        
        # Generate company cards
        company_cards = self._generate_company_cards(companies)
        
        # Prepare template variables
        template_vars = {
            'title': title,
            'description': description,
            'current_date': current_date,
            'company_count': company_count,
            'safe_count': safe_count,
            'avg_zscore': f"{avg_zscore:.2f}",
            'summary_text': summary_text,
            'company_cards': company_cards,
            'css_file': css_filename,
            'version': __version__
        }
        
        # Generate final HTML
        return self.main_template.substitute(template_vars)
        
    def _generate_company_cards(self, companies: List[Dict[str, Any]]) -> str:
        """Generate HTML for company cards using template."""
        cards_html = []
        
        for i, company in enumerate(companies, 1):
            ticker = company.get('ticker', 'N/A')
            name = company.get('name', ticker)
            z_score = company.get('z_score', 0)
            risk_category = company.get('risk_category', 'Unknown')
            recommendation = company.get('recommendation', 'N/A')
            
            # Determine risk class for styling
            risk_class = self._get_risk_class(z_score)
            
            # Generate logo path and check existence
            logo_path = f"output/{ticker}/logo.png"
            logo_exists = os.path.exists(os.path.join(self.base_dir, logo_path))
            
            # Build logo HTML
            logo_html = ""
            if logo_exists:
                logo_html = f'<img src="{logo_path}" alt="{ticker}" class="company-logo" onerror="this.style.display=\'none\'">'
            
            # Build recommendation class
            rec_class = recommendation.lower().replace(' ', '-')
            
            # Prepare template variables
            card_vars = {
                'logo_html': logo_html,
                'name': name,
                'ticker': ticker,
                'rank': i,
                'z_score': f"{z_score:.2f}",
                'risk_class': risk_class,
                'risk_category': risk_category,
                'recommendation': recommendation,
                'rec_class': rec_class
            }
            
            # Generate card HTML using template
            try:
                card_html = self.card_template.substitute(card_vars)
                cards_html.append(card_html)
            except Exception as e:
                self.logger.error(f"Failed to generate card for {ticker}: {e}")
                continue
            
        return '\n'.join(cards_html)
    
    def _generate_css_content(self, color_scheme: Dict[str, str]) -> str:
        """Generate CSS content with color scheme applied."""
        try:
            css_vars = {
                'primary_color': color_scheme['primary'],
                'secondary_color': color_scheme['secondary'],
                'accent_color': color_scheme['accent']
            }
            return self.css_template.substitute(css_vars)
        except Exception as e:
            self.logger.error(f"Failed to generate CSS content: {e}")
            return self._get_fallback_css(color_scheme)
            
    def _create_fallback_templates(self):
        """Create fallback templates if external files are not available."""
        self.logger.warning("Using fallback inline templates")
        
        # Simple fallback main template
        self.main_template = Template('''<!DOCTYPE html>
<html>
<head>
    <title>$title</title>
    <style>$css_content</style>
</head>
<body>
    <h1>$title</h1>
    <p>$description</p>
    <div>$company_cards</div>
</body>
</html>''')
        
        # Simple fallback card template  
        self.card_template = Template('''
<div class="company-card">
    <h3>$name ($ticker)</h3>
    <p>Z-Score: $z_score</p>
    <p>Risk: $risk_category</p>
    <p>Recommendation: $recommendation</p>
</div>''')
        
        # Simple fallback CSS template
        self.css_template = Template('''
body { font-family: Arial, sans-serif; }
.company-card { border: 1px solid #ccc; margin: 10px; padding: 15px; }
h1 { color: $primary_color; }
''')
    
    def _get_fallback_css(self, color_scheme: Dict[str, str]) -> str:
        """Generate fallback CSS if template fails."""
        return f'''
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .company-card {{ 
            background: white; 
            border: 1px solid #ddd; 
            margin: 10px; 
            padding: 20px; 
            border-radius: 8px;
        }}
        h1 {{ color: {color_scheme['primary']}; }}
        .risk-safe {{ color: #27ae60; }}
        .risk-moderate {{ color: #f39c12; }}
        .risk-high {{ color: #e74c3c; }}
        '''
    
    def _get_default_color_scheme(self, portfolio_type: str) -> Dict[str, str]:
        """Get default color scheme for portfolio type."""
        schemes = {
            'strong_buy': {
                'primary': '#1e8449',
                'secondary': '#27ae60', 
                'accent': '#58d68d'
            },
            'buy': {
                'primary': '#229954',
                'secondary': '#2ecc71',
                'accent': '#6bcf7f'
            },
            'value': {
                'primary': '#1f618d',
                'secondary': '#3498db',
                'accent': '#85c1e9'
            },
            'growth': {
                'primary': '#7d3c98',
                'secondary': '#9b59b6',
                'accent': '#bb8fce'
            },
            'dividend': {
                'primary': '#ca6f1e',
                'secondary': '#e67e22',
                'accent': '#f8c471'
            },
            'conservative': {
                'primary': '#566573',
                'secondary': '#6c7b7f',
                'accent': '#a6acaf'
            },
            'aggressive': {
                'primary': '#c0392b',
                'secondary': '#e74c3c',
                'accent': '#f1948a'
            },
            'sell': {
                'primary': '#e67e22',
                'secondary': '#f39c12',
                'accent': '#f8c471'
            },
            'strong_sell': {
                'primary': '#c0392b',
                'secondary': '#e74c3c',
                'accent': '#f1948a'
            }
        }
        
        return schemes.get(portfolio_type, {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#5d6d7e'
        })
    
    def _get_risk_class(self, z_score: float) -> str:
        """Get CSS risk class based on Z-Score."""
        if z_score > 2.99:
            return "risk-safe"
        elif z_score > 1.8:
            return "risk-moderate"
        else:
            return "risk-high"
    
    def _generate_summary_text(self, top_companies: List[Dict[str, Any]], portfolio_type: str) -> str:
        """Generate portfolio summary text."""
        if not top_companies:
            return "No companies found matching the criteria."
            
        portfolio_descriptions = {
            'strong_buy': 'companies with exceptional financial strength and Strong Buy recommendations',
            'buy': 'companies with strong financial metrics and Buy recommendations', 
            'value': 'undervalued companies with solid fundamentals',
            'growth': 'companies showing strong growth potential',
            'dividend': 'reliable dividend-paying companies',
            'conservative': 'low-risk companies for conservative investors',
            'aggressive': 'high-growth potential companies for aggressive investors',
            'sell': 'companies requiring careful consideration for sell decisions',
            'strong_sell': 'companies with concerning financial metrics'
        }
        
        description = portfolio_descriptions.get(portfolio_type, 'companies meeting specific criteria')
        
        top_company = top_companies[0]
        summary = f"""
        <p>This portfolio presents <strong>{description}</strong> based on comprehensive Altman Z-Score analysis. 
        The selection emphasizes financial stability, market position, and investment potential.</p>
        
        <p><strong>Top Pick:</strong> {top_company['name']} ({top_company['ticker']}) leads with a Z-Score of 
        {top_company['z_score']:.2f}, indicating {top_company['risk_category'].lower()} risk levels.</p>
        """
        
        if len(top_companies) >= 2:
            summary += f"""
            <p><strong>Notable Mentions:</strong> {top_companies[1]['name']} ({top_companies[1]['ticker']}) 
            and {top_companies[2]['name']} ({top_companies[2]['ticker']}) also demonstrate strong fundamentals 
            with Z-Scores of {top_companies[1]['z_score']:.2f} and {top_companies[2]['z_score']:.2f} respectively.</p>
            """
            
        return summary
