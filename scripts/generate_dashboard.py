#!/usr/bin/env python3
"""
Dashboard Generator for Altman Z-Score Analysis
Handles data processing and HTML generation with proper templating
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import re
from typing import List, Optional
import webbrowser

from jinja2 import Environment, FileSystemLoader

@dataclass
class StockData:
    symbol: str
    name: str
    z_score: float
    sector: str
    recommendation: str
    risk_category: str = "Unknown"
    data_quality: float = 0.0
    confidence: float = 0.0
    model_used: str = "Unknown"
    portfolio: str = "Main"
    logo: str = "default_logo.png"
    
    # Market data (when available)
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    
    # Component analysis
    working_capital_ratio: Optional[float] = None
    retained_earnings_ratio: Optional[float] = None
    ebit_ratio: Optional[float] = None
    market_equity_ratio: Optional[float] = None
    book_equity_ratio: Optional[float] = None
    asset_turnover: Optional[float] = None
    
    # Additional financial ratios (from FMP data)
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    
    # Analysis metadata
    analysis_date: Optional[str] = None
    calculation_timestamp: Optional[str] = None
    executive_summary: Optional[str] = None

    @classmethod
    def from_summary_file(cls, summary_path: Path) -> 'StockData':
        """Create StockData from a summary file"""
        content = summary_path.read_text(encoding='utf-8')
        symbol = summary_path.stem.replace('_summary', '')
        
        # Extract basic Z-Score data
        z_score = 0.0
        if match := re.search(r'Z-SCORE:\s*([\d.]+)', content):
            z_score = float(match.group(1))
        
        # Extract analysis date
        analysis_date = None
        if match := re.search(r'Analysis Date:\s*([^\r\n]+)', content):
            analysis_date = match.group(1).strip()
        
        # Extract company name from the dedicated Company Name line
        name = f"{symbol} Inc."  # Default fallback
        if match := re.search(r'Company Name:\s*([^\r\n]+)', content):
            name = match.group(1).strip()
        # Fallback: try to extract from AI analysis section if Company Name line not found
        elif match := re.search(r'\*\*Company:\*\*\s*([^(]+)', content):
            name = match.group(1).strip()
            
        # Get risk category
        risk_category = "Unknown"
        if match := re.search(r'Risk Category:\s*([^\r\n]+)', content):
            risk_category = match.group(1).strip()
            
        # Get model used
        model_used = "Unknown"
        if match := re.search(r'Model Used:\s*([^\r\n]+)', content):
            model_used = match.group(1).strip()
            
        # Get data quality
        data_quality = 0.0
        if match := re.search(r'Data Quality:\s*([\d.]+)', content):
            data_quality = float(match.group(1))
            
        # Extract executive summary from AI analysis section
        executive_summary = None
        if match := re.search(r'## 1\. Executive Intelligence Summary\s*\n\s*(.+?)(?=\s*\[Full analysis available|\s*##|\s*$)', content, re.DOTALL):
            executive_summary = match.group(1).strip()
            # Clean up the summary - remove extra whitespace and markdown formatting
            executive_summary = re.sub(r'\s+', ' ', executive_summary)
            executive_summary = re.sub(r'\*\*(.*?)\*\*', r'\1', executive_summary)  # Remove bold markdown
            
        # Get component analysis ratios
        component_data = {
            'working_capital_ratio': r'Working Capital Ratio:\s*([-\d.]+)',
            'retained_earnings_ratio': r'Retained Earnings Ratio:\s*([-\d.]+)',
            'ebit_ratio': r'Ebit Ratio:\s*([-\d.]+)',
            'market_equity_ratio': r'Market Equity Ratio:\s*([-\d.]+)',
            'book_equity_ratio': r'Book Equity Ratio:\s*([-\d.]+)',
            'asset_turnover': r'Asset Turnover:\s*([-\d.]+)'
        }
        
        components = {}
        for key, pattern in component_data.items():
            if match := re.search(pattern, content):
                components[key] = float(match.group(1))
            else:
                components[key] = None
                
        # Try to extract additional financial ratios if they exist
        additional_ratios = {
            'current_ratio': r'Current Ratio:\s*([-\d.]+)',
            'debt_to_equity': r'Debt to Equity:\s*([-\d.]+)',
        }
        
        for key, pattern in additional_ratios.items():
            if match := re.search(pattern, content):
                components[key] = float(match.group(1))
            else:
                components[key] = None
                
        # Try to extract market data if available
        current_price = None
        if match := re.search(r'Current Price:\s*\$?([\d.]+)', content):
            current_price = float(match.group(1))
            
        market_cap = None
        if match := re.search(r'Market Cap:\s*([^\r\n]+)', content):
            market_cap_str = match.group(1).strip()
            # Parse market cap (could be in format like "$1.2B" or "1200000000")
            if market_cap_str != "N/A":
                market_cap = market_cap_str
                
        # Get recommendation and confidence
        recommendation = "Unknown"
        confidence = 0.0
        if match := re.search(r'Action:\s*([^\r\n]+).*?Confidence:\s*([\d.]+)', content, re.DOTALL):
            recommendation = match.group(1).strip()
            confidence = float(match.group(2))
        elif z_score >= 3.0:
            recommendation = "Strong Buy"
            confidence = 70.0
        elif z_score >= 1.8:
            recommendation = "Hold"
            confidence = 50.0
        else:
            recommendation = "Sell"
            confidence = 60.0
            
        return cls(
            symbol=symbol,
            name=name,
            z_score=z_score,
            sector="Unknown",  # We'll determine sector from a different source
            recommendation=recommendation,
            risk_category=risk_category,
            data_quality=data_quality,
            confidence=confidence,
            model_used=model_used,
            current_price=current_price,
            market_cap=market_cap,
            analysis_date=analysis_date,
            executive_summary=executive_summary,
            logo=f"output/{symbol}/{symbol}_logo.png",
            **components  # Unpack all the component ratios
        )

def process_stock_data(output_dir: Path, verbose: bool = False) -> List[StockData]:
    """Process all stock summary files in the output directory"""
    if verbose:
        logging.info("Processing stock data...")
    
    stocks = []
    if not output_dir.exists():
        if verbose:
            logging.warning(f"Output directory not found: {output_dir}")
            logging.info("Using sample data for demonstration")
        return get_sample_data()
    
    for company_dir in output_dir.iterdir():
        if not company_dir.is_dir():
            continue
            
        summary_file = company_dir / f"{company_dir.name}_summary.txt"
        if summary_file.exists():
            try:
                if verbose:
                    logging.debug(f"Processing {company_dir.name} summary...")
                stock = StockData.from_summary_file(summary_file)
                stocks.append(stock)
                if verbose:
                    logging.info(f"Successfully processed {stock.symbol}")
            except Exception as e:
                logging.warning(f"Error processing {summary_file}: {e}")
        else:
            logging.warning(f"No summary file found for {company_dir.name}")
    
    if not stocks:
        logging.warning("No company data found, using sample data")
        return get_sample_data()
        
    return stocks

def get_sample_data() -> List[StockData]:
    """Return sample stock data for demonstration"""
    return [
        StockData(
            symbol="AAPL",
            name="Apple Inc.",
            z_score=3.85,
            sector="Technology",
            recommendation="Strong Buy",
        ),
        StockData(
            symbol="MSFT",
            name="Microsoft Corporation",
            z_score=4.2,
            sector="Technology",
            recommendation="Strong Buy",
        )
    ]

def generate_dashboard(stocks: List[StockData], template_dir: Path, output_file: Path) -> None:
    """Generate HTML dashboard using Jinja2 templating"""
    env = Environment(loader=FileSystemLoader(template_dir, encoding='utf-8'))
    template = env.get_template('dashboard.template.html')
    
    # Convert stock data to dict for JSON serialization with the exact keys JavaScript expects
    stock_data = []
    for s in stocks:
        stock = {
            'Symbol': s.symbol,
            'Name': s.name,
            'ZScore': s.z_score,
            'Risk': s.risk_category,
            'Recommendation': s.recommendation,
            'Confidence': f"{s.confidence:.1f}%",
            'Model': s.model_used,
            'Price': s.current_price if s.current_price is not None else 'N/A',
            'MarketCap': s.market_cap if s.market_cap is not None else 'N/A',
            'AnalysisDate': s.analysis_date if s.analysis_date is not None else 'N/A',
            'ExecutiveSummary': s.executive_summary if s.executive_summary is not None else '',
            'Portfolio': s.portfolio,
            'Logo': s.logo
        }
        stock_data.append(stock)
    
    # Render template with stock data
    html_content = template.render(
        stock_data_json=json.dumps(stock_data)
    )
    
    # Save the dashboard
    output_file.write_text(html_content, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description='Generate Altman Z-Score Dashboard')
    parser.add_argument('--output-dir', type=Path, default=Path('web'),
                      help='Output directory for the dashboard')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s] %(message)s'
    )
    
    try:
        # Process stock data
        stock_data = process_stock_data(
            args.output_dir / 'output',
            verbose=args.verbose
        )
        
        if args.verbose:
            logging.info(f"Processed {len(stock_data)} stocks")
        
        # Generate dashboard
        template_dir = Path('scripts')
        output_file = args.output_dir / 'dashboard.html'
        
        generate_dashboard(stock_data, template_dir, output_file)
        
        if args.verbose:
            logging.info(f"Dashboard generated: {output_file}")
            
    except Exception as e:
        logging.error(f"Error generating dashboard: {e}")
        raise

if __name__ == '__main__':
    main()
