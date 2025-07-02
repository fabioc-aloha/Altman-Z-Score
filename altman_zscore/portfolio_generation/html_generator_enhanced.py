"""
Enhanced HTML Portfolio Generator - Modern template-based HTML generation

This enhanced version provides improved logo handling, modern styling,
and better fallback mechanisms for portfolio dashboards.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from string import Template

from ..common.logging_config import get_logger
from .._version import __version__

logger = get_logger(__name__)


class EnhancedHTMLPortfolioGenerator:
    """Enhanced HTML generator with modern styling and better logo handling."""
    
    def __init__(self, base_dir: str = "."):
        """
        Initialize enhanced HTML generator.
        
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
            # Load enhanced templates
            main_template_path = self.templates_dir / "portfolio_enhanced.html"
            if main_template_path.exists():
                with open(main_template_path, 'r', encoding='utf-8') as f:
                    self.main_template = Template(f.read())
            else:
                self._create_fallback_main_template()
                
            # Load enhanced company card template
            card_template_path = self.templates_dir / "company_card_enhanced.html"
            if card_template_path.exists():
                with open(card_template_path, 'r', encoding='utf-8') as f:
                    self.card_template = Template(f.read())
            else:
                self._create_fallback_card_template()
                
            # Load enhanced CSS
            css_path = Path(self.base_dir) / "web" / "assets" / "dashboard_enhanced.css"
            if css_path.exists():
                with open(css_path, 'r', encoding='utf-8') as f:
                    self.css_content = f.read()
            else:
                self._create_fallback_css()
                
            self.logger.info("Enhanced templates loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load enhanced templates: {e}")
            self._create_fallback_templates()
    
    def _generate_enhanced_logo_html(self, ticker: str, company_name: str) -> str:
        """
        Generate enhanced logo HTML with better fallback handling.
        
        Args:
            ticker: Company ticker symbol
            company_name: Company name for alt text
            
        Returns:
            HTML string for company logo with enhanced styling
        """
        # Multiple logo path possibilities
        logo_paths = [
            f"output/{ticker}/{ticker}_logo.png",
            f"output/{ticker}/logo.png",
            f"output/{ticker.lower()}/{ticker.lower()}_logo.png",
            f"output/{ticker.lower()}/logo.png"
        ]
        
        default_logo_path = "assets/default_logo.png"
        
        # Check which logo exists
        logo_exists = False
        chosen_logo_path = None
        
        for logo_path in logo_paths:
            # Check in both base directory and parent directory
            check_paths = [
                os.path.join(self.base_dir, logo_path),
                os.path.join(os.path.dirname(self.base_dir), logo_path)
            ]
            
            for check_path in check_paths:
                if os.path.exists(check_path):
                    logo_exists = True
                    chosen_logo_path = logo_path
                    break
            
            if logo_exists:
                break
        
        # Generate enhanced logo HTML
        if logo_exists and chosen_logo_path:
            logo_html = f'''<img src="{chosen_logo_path}" 
                           alt="{company_name} ({ticker})" 
                           class="company-logo" 
                           title="{company_name}"
                           loading="lazy"
                           onerror="this.src='{default_logo_path}'; this.onerror=null;">'''
        else:
            # Use default logo with company initials as fallback
            initials = self._get_company_initials(company_name)
            logo_html = f'''<img src="{default_logo_path}" 
                           alt="{company_name} ({ticker})" 
                           class="company-logo" 
                           title="{company_name}"
                           loading="lazy"
                           data-initials="{initials}">'''
        
        return logo_html
    
    def _get_company_initials(self, company_name: str) -> str:
        """
        Extract company initials for fallback display.
        
        Args:
            company_name: Full company name
            
        Returns:
            Company initials (up to 3 characters)
        """
        if not company_name:
            return "??"
        
        # Remove common corporate suffixes
        cleaned_name = company_name.replace(" Inc.", "").replace(" Corp.", "").replace(" LLC", "")
        cleaned_name = cleaned_name.replace(" Ltd.", "").replace(" Co.", "").replace(" Company", "")
        
        # Split into words and get initials
        words = [word.strip() for word in cleaned_name.split() if word.strip()]
        if not words:
            return "??"
        
        # Take first letter of first 3 significant words
        initials = ""
        for word in words[:3]:
            if word.upper() not in ["THE", "A", "AN", "AND", "OR", "OF", "FOR", "TO", "IN", "ON", "AT"]:
                initials += word[0].upper()
        
        return initials[:3] if initials else company_name[:2].upper()
    
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
        Generate enhanced HTML portfolio dashboard.
        
        Args:
            companies: List of company data dictionaries
            portfolio_type: Type of portfolio (e.g., 'strong_buy', 'value', 'growth')
            title: Page title
            description: Portfolio description
            output_filename: Output HTML filename
            color_scheme: Optional custom color scheme
            
        Returns:
            Generated HTML content
        """
        if not companies:
            self.logger.warning(f"No companies provided for {portfolio_type} portfolio")
            return self._generate_empty_portfolio_html(title, description)
        
        current_date = datetime.now().strftime("%B %d, %Y")
        company_count = len(companies)
        
        # Calculate enhanced statistics
        safe_count = len([c for c in companies if c.get('z_score', 0) > 2.99])
        gray_zone_count = len([c for c in companies if 1.8 <= c.get('z_score', 0) <= 2.99])
        distress_count = len([c for c in companies if c.get('z_score', 0) < 1.8])
        avg_zscore = sum(c.get('z_score', 0) for c in companies) / len(companies) if companies else 0
        
        # Get top companies for summary
        top_companies = companies[:5]
        
        # Generate enhanced summary text
        summary_text = self._generate_enhanced_summary_text(companies, portfolio_type, top_companies)
        
        # Generate enhanced company cards
        company_cards = self._generate_enhanced_company_cards(companies)
        
        # Prepare template variables
        template_vars = {
            'title': title,
            'description': description,
            'current_date': current_date,
            'company_count': company_count,
            'safe_count': safe_count,
            'gray_zone_count': gray_zone_count,
            'distress_count': distress_count,
            'avg_zscore': f"{avg_zscore:.2f}",
            'summary_text': summary_text,
            'company_cards': company_cards,
            'embedded_css': f"<style>\n{self.css_content}\n</style>",
            'version': __version__,
            'portfolio_type': portfolio_type
        }
        
        # Generate final HTML
        try:
            html_content = self.main_template.substitute(template_vars)
            self.logger.info(f"Successfully generated enhanced HTML for {portfolio_type} portfolio")
            return html_content
        except Exception as e:
            self.logger.error(f"Error generating HTML template: {e}")
            return self._generate_fallback_html(title, description, companies)
    
    def _generate_enhanced_company_cards(self, companies: List[Dict[str, Any]]) -> str:
        """Generate enhanced HTML for company cards using template."""
        cards_html = []
        
        for i, company in enumerate(companies, 1):
            ticker = company.get('ticker', 'N/A')
            name = company.get('name', ticker)
            z_score = company.get('z_score', 0)
            
            # Clean the company name to remove ** and (ticker) patterns
            cleaned_name = self._clean_company_name(name, ticker)
            
            # Generate enhanced logo HTML
            logo_html = self._generate_enhanced_logo_html(ticker, cleaned_name)
            
            # Get additional metrics
            market_cap = self._format_market_cap(company.get('market_cap', 'N/A'))
            industry = company.get('industry', 'N/A')
            price = self._format_price(company.get('price', 'N/A'))
            revenue_growth = self._format_percentage(company.get('revenue_growth', 'N/A'))
            debt_equity = self._format_ratio(company.get('debt_equity', 'N/A'))
            
            # Determine risk category and label
            risk_category, risk_label = self._get_risk_category_and_label(z_score)
            
            # Prepare template variables
            card_vars = {
                'logo_html': logo_html,
                'company_name': cleaned_name,
                'ticker': ticker,
                'z_score': f"{z_score:.2f}",
                'market_cap': market_cap,
                'industry': industry,
                'price': price,
                'revenue_growth': revenue_growth,
                'debt_equity': debt_equity,
                'risk_category': risk_category,
                'risk_label': risk_label
            }
            
            # Generate card HTML
            try:
                card_html = self.card_template.substitute(card_vars)
                cards_html.append(card_html)
            except Exception as e:
                self.logger.error(f"Error generating card for {ticker}: {e}")
                # Generate fallback card
                cards_html.append(self._generate_fallback_card(ticker, name, z_score))
        
        return '\n'.join(cards_html)
    
    def _format_market_cap(self, market_cap) -> str:
        """Format market cap for display."""
        if market_cap == 'N/A' or market_cap is None:
            return 'N/A'
        
        try:
            cap = float(market_cap)
            if cap >= 1e12:
                return f"${cap/1e12:.1f}T"
            elif cap >= 1e9:
                return f"${cap/1e9:.1f}B"
            elif cap >= 1e6:
                return f"${cap/1e6:.1f}M"
            else:
                return f"${cap:,.0f}"
        except (ValueError, TypeError):
            return str(market_cap)
    
    def _format_price(self, price) -> str:
        """Format price for display."""
        if price == 'N/A' or price is None:
            return 'N/A'
        
        try:
            return f"${float(price):.2f}"
        except (ValueError, TypeError):
            return str(price)
    
    def _format_percentage(self, value) -> str:
        """Format percentage for display."""
        if value == 'N/A' or value is None:
            return 'N/A'
        
        try:
            return f"{float(value):.1f}%"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_ratio(self, value) -> str:
        """Format ratio for display."""
        if value == 'N/A' or value is None:
            return 'N/A'
        
        try:
            return f"{float(value):.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _get_risk_category_and_label(self, z_score: float) -> tuple:
        """Get risk category and label based on Z-Score."""
        if z_score > 2.99:
            return "safe", "Safe Zone"
        elif z_score >= 1.8:
            return "gray", "Gray Zone"
        else:
            return "distress", "Distress Zone"
    
    def _generate_enhanced_summary_text(self, companies: List[Dict[str, Any]], portfolio_type: str, top_companies: List[Dict[str, Any]]) -> str:
        """Generate enhanced summary text with more insights."""
        if not companies:
            return "No companies found for this portfolio."
        
        avg_z = sum(c.get('z_score', 0) for c in companies) / len(companies)
        top_names = [c.get('name', c.get('ticker', 'N/A')) for c in top_companies[:3]]
        
        summary = f"""
        <p>This {portfolio_type} portfolio contains <strong>{len(companies)} companies</strong> 
        with an average Z-Score of <strong>{avg_z:.2f}</strong>.</p>
        
        <p>Top holdings include <strong>{', '.join(top_names)}</strong>, representing 
        companies with strong financial fundamentals and attractive investment characteristics.</p>
        
        <p>The portfolio is designed to align with {portfolio_type} investment strategies, 
        focusing on companies that demonstrate solid financial health according to the Altman Z-Score model.</p>
        """
        
        return summary
    
    def _create_fallback_main_template(self):
        """Create fallback main template if file doesn't exist."""
        template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title</title>
    $embedded_css
</head>
<body>
    <div class="container">
        <header class="header-container">
            <h1>$title</h1>
            <p class="subtitle">$description</p>
            <p class="date">Generated: $current_date</p>
        </header>
        
        <section class="summary-section">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">$company_count</div>
                    <div class="stat-label">Companies</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">$avg_zscore</div>
                    <div class="stat-label">Avg Z-Score</div>
                </div>
            </div>
            <div class="summary-text">$summary_text</div>
        </section>
        
        <section class="companies-section">
            <h2>Company Analysis</h2>
            <div class="company-grid">$company_cards</div>
        </section>
    </div>
</body>
</html>"""
        self.main_template = Template(template_content)
    
    def _create_fallback_card_template(self):
        """Create fallback card template if file doesn't exist."""
        template_content = """<div class="company-card">
    <div class="company-header">
        <div class="company-logo-container">$logo_html</div>
        <div class="company-name">
            <h3>$company_name</h3>
            <span class="company-ticker">$ticker</span>
        </div>
    </div>
    <div class="company-metrics">
        <div class="metric">
            <span class="metric-name">Z-Score</span>
            <span class="metric-value">$z_score</span>
        </div>
    </div>
    <div class="z-score $risk_category">
        <strong>$risk_label</strong>
    </div>
</div>"""
        self.card_template = Template(template_content)
    
    def _create_fallback_css(self):
        """Create fallback CSS if file doesn't exist."""
        self.css_content = """
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .company-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .company-card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: white; }
        .company-logo { width: 60px; height: 60px; object-fit: contain; }
        """
    
    def _generate_empty_portfolio_html(self, title: str, description: str) -> str:
        """Generate HTML for empty portfolio."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>{description}</p>
    <p>No companies found for this portfolio.</p>
</body>
</html>"""
    
    def _generate_fallback_html(self, title: str, description: str, companies: List[Dict[str, Any]]) -> str:
        """Generate fallback HTML if template fails."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p>{description}</p>
    <ul>"""
        
        for company in companies:
            html += f"<li>{company.get('name', company.get('ticker', 'N/A'))} - Z-Score: {company.get('z_score', 'N/A')}</li>"
        
        html += "</ul></body></html>"
        return html
    
    def _generate_fallback_card(self, ticker: str, name: str, z_score: float) -> str:
        """Generate fallback card HTML."""
        return f"""<div class="company-card">
    <h3>{name} ({ticker})</h3>
    <p>Z-Score: {z_score:.2f}</p>
</div>"""
    
    def _clean_company_name(self, name: str, ticker: str = None) -> str:
        """
        Clean company name by removing formatting artifacts and ticker symbols.
        
        Args:
            name: Original company name
            ticker: Company ticker (optional, for specific ticker removal)
            
        Returns:
            Cleaned company name
        """
        if not name:
            return ""
        
        # Remove ** from the beginning of company names
        cleaned_name = name.lstrip('*').strip()
        
        # Remove (TICKER) patterns - first try with specific ticker if provided
        if ticker:
            # Remove (TICKER) or (ticker) patterns
            import re
            pattern = rf'\s*\({re.escape(ticker.upper())}\)\s*'
            cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
            pattern = rf'\s*\({re.escape(ticker.lower())}\)\s*'
            cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
        
        # Remove any remaining (XXXX) patterns at the end (likely tickers)
        import re
        cleaned_name = re.sub(r'\s*\([A-Z]{1,5}\)\s*$', '', cleaned_name)
        
        # Clean up extra whitespace
        cleaned_name = ' '.join(cleaned_name.split())
        
        return cleaned_name
