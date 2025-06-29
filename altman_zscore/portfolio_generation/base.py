"""
Base Portfolio Generation Classes

Provides abstract base classes and common functionality for portfolio generation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os

from ..common.logging_config import get_logger

logger = get_logger(__name__)


class InvestmentRating(Enum):
    """Investment rating categories."""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY" 
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class CompanyData:
    """Data structure for company information extracted from reports."""
    ticker: str
    company_name: str
    z_score: float
    risk_category: str
    investment_ratings: Dict[str, str]  # profile -> rating
    key_metrics: Dict[str, Any]
    ai_insights: Dict[str, Any]
    market_analysis: Dict[str, Any]
    summary_content: str
    report_path: Optional[str] = None
    

@dataclass 
class PortfolioConfig:
    """Configuration for portfolio generation."""
    name: str
    title: str
    description: str
    output_filename: str
    min_companies: int = 10
    max_companies: int = 50
    sort_by: str = "z_score"
    sort_descending: bool = True
    

class PortfolioStrategy(ABC):
    """
    Abstract base class for portfolio generation strategies.
    
    Each strategy defines how to filter and rank companies
    for a specific type of investment portfolio.
    """
    
    def __init__(self, config: PortfolioConfig):
        """Initialize strategy with configuration."""
        self.config = config
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def should_include(self, company: CompanyData) -> bool:
        """
        Determine if a company should be included in this portfolio.
        
        Args:
            company: Company data to evaluate
            
        Returns:
            True if company meets portfolio criteria
        """
        pass
    
    @abstractmethod
    def get_ranking_score(self, company: CompanyData) -> float:
        """
        Get ranking score for company within this portfolio type.
        
        Args:
            company: Company data to score
            
        Returns:
            Numeric score for ranking (higher = better)
        """
        pass
    
    def get_portfolio_description(self) -> str:
        """Get description text for this portfolio type."""
        return self.config.description
    
    def get_additional_notes(self, companies: List[CompanyData]) -> List[str]:
        """
        Get additional notes or warnings for this portfolio.
        
        Args:
            companies: Final list of companies in portfolio
            
        Returns:
            List of note strings
        """
        return []


class PortfolioGenerator:
    """
    Main portfolio generator that coordinates data extraction,
    strategy application, and output generation.
    """
    
    def __init__(self, output_base_dir: str = "."):
        """
        Initialize portfolio generator.
        
        Args:
            output_base_dir: Base directory for output files
        """
        self.output_base_dir = output_base_dir
        self.logger = get_logger(self.__class__.__name__)
        
        # Import here to avoid circular imports
        from .data_extractor import CompanyDataExtractor
        from .html_generator import HTMLPortfolioGenerator
        
        self.data_extractor = CompanyDataExtractor(os.path.join(output_base_dir, "output"))
        self.html_generator = HTMLPortfolioGenerator(os.path.join(output_base_dir, "web"))
    
    def generate_portfolio(self, strategy: PortfolioStrategy) -> str:
        """
        Generate a portfolio using the specified strategy.
        
        Args:
            strategy: Portfolio strategy to apply
            
        Returns:
            Path to generated HTML file
        """
        self.logger.info(f"Generating {strategy.config.name} portfolio")
        
        # Extract all company data
        all_companies = self.data_extractor.extract_all_companies()
        self.logger.info(f"Found {len(all_companies)} companies to evaluate")
        
        # Apply strategy filtering
        filtered_companies = [
            company for company in all_companies 
            if strategy.should_include(company)
        ]
        self.logger.info(f"{len(filtered_companies)} companies match {strategy.config.name} criteria")
        
        if len(filtered_companies) < strategy.config.min_companies:
            self.logger.warning(
                f"Only {len(filtered_companies)} companies found for {strategy.config.name}, "
                f"minimum is {strategy.config.min_companies}"
            )
        
        # Apply strategy ranking
        ranked_companies = sorted(
            filtered_companies,
            key=strategy.get_ranking_score,
            reverse=strategy.config.sort_descending
        )
        
        # Limit to max companies
        final_companies = ranked_companies[:strategy.config.max_companies]
        
        # Convert to HTML generator format
        html_companies = []
        for company in final_companies:
            html_companies.append({
                'ticker': company.ticker,
                'name': company.company_name,
                'z_score': company.z_score,
                'risk_category': company.risk_category,
                'recommendation': self._get_primary_recommendation(company)
            })
        
        # Determine portfolio type for styling
        portfolio_type = strategy.config.name.lower().replace(' ', '_')
        
        # Generate HTML output
        output_path = self.html_generator.generate_portfolio_html(
            companies=html_companies,
            portfolio_type=portfolio_type,
            title=strategy.config.title,
            description=strategy.config.description,
            output_filename=strategy.config.output_filename
        )
        
        self.logger.info(
            f"Generated {strategy.config.name} portfolio with {len(final_companies)} companies: {output_path}"
        )
        
        return output_path
    
    def _get_primary_recommendation(self, company: CompanyData) -> str:
        """Get the primary investment recommendation for a company."""
        # Look for the most common recommendation across profiles
        recommendations = list(company.investment_ratings.values())
        if not recommendations:
            return "HOLD"
        
        # Return the first non-hold recommendation, or HOLD if all are HOLD
        for rec in recommendations:
            if rec != "HOLD":
                return rec
        return "HOLD"
