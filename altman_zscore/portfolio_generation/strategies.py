"""
Portfolio Generation Strategies

Implements specific strategies for different types of investment portfolios.
Each strategy defines filtering criteria and ranking logic for its portfolio type.
"""

from typing import List
from .base import PortfolioStrategy, CompanyData, PortfolioConfig, InvestmentRating


class StrongBuyStrategy(PortfolioStrategy):
    """Strategy for identifying strong buy opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies with strong buy recommendations and good fundamentals."""
        # Must have STRONG_BUY rating from at least one profile
        has_strong_buy = any(
            rating == "STRONG_BUY" 
            for rating in company.investment_ratings.values()
        )
        
        # Z-Score should be reasonable (not in deep distress)
        has_decent_zscore = company.z_score >= 1.5
        
        return has_strong_buy and has_decent_zscore
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by Z-Score primarily, with AI confidence as tiebreaker."""
        base_score = company.z_score
        
        # Bonus for AI confidence
        ai_confidence = company.ai_insights.get('confidence_level', 50) / 100
        confidence_bonus = ai_confidence * 0.5
        
        # Bonus for multiple strong buy ratings
        strong_buy_count = sum(
            1 for rating in company.investment_ratings.values() 
            if rating == "STRONG_BUY"
        )
        multiple_rating_bonus = (strong_buy_count - 1) * 0.2
        
        return base_score + confidence_bonus + multiple_rating_bonus


class BuyStrategy(PortfolioStrategy):
    """Strategy for identifying buy opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies with buy or strong buy recommendations."""
        buy_ratings = {"BUY", "STRONG_BUY"}
        has_buy_rating = any(
            rating in buy_ratings 
            for rating in company.investment_ratings.values()
        )
        
        # Z-Score should indicate some stability
        has_stable_zscore = company.z_score >= 1.2
        
        return has_buy_rating and has_stable_zscore
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by combination of Z-Score and number of buy ratings."""
        base_score = company.z_score
        
        buy_ratings = {"BUY", "STRONG_BUY"}
        buy_count = sum(
            1 for rating in company.investment_ratings.values() 
            if rating in buy_ratings
        )
        
        return base_score + (buy_count * 0.3)


class SellStrategy(PortfolioStrategy):
    """Strategy for identifying sell opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies with sell or strong sell recommendations."""
        sell_ratings = {"SELL", "STRONG_SELL"}
        has_sell_rating = any(
            rating in sell_ratings 
            for rating in company.investment_ratings.values()
        )
        
        return has_sell_rating
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by inverse Z-Score (lower Z-Score = higher risk = higher in sell list)."""
        # Invert Z-Score so lowest scores rank highest
        base_score = 10.0 - company.z_score
        
        sell_ratings = {"SELL", "STRONG_SELL"}
        sell_count = sum(
            1 for rating in company.investment_ratings.values() 
            if rating in sell_ratings
        )
        
        return base_score + (sell_count * 0.5)


class StrongSellStrategy(PortfolioStrategy):
    """Strategy for identifying strong sell opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies with strong sell recommendations or severe distress."""
        # Must have STRONG_SELL rating OR be in deep distress
        has_strong_sell = any(
            rating == "STRONG_SELL" 
            for rating in company.investment_ratings.values()
        )
        
        in_severe_distress = company.z_score < 1.0
        
        return has_strong_sell or in_severe_distress
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by severity of distress (lowest Z-Score first)."""
        # Severely invert Z-Score for distress ranking
        base_score = 15.0 - company.z_score
        
        strong_sell_count = sum(
            1 for rating in company.investment_ratings.values() 
            if rating == "STRONG_SELL"
        )
        
        return base_score + (strong_sell_count * 1.0)


class ValueStrategy(PortfolioStrategy):
    """Strategy for value investing opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies with value characteristics."""
        # Look for value profile buy recommendation
        value_rating = company.investment_ratings.get('value_investor', '')
        has_value_buy = value_rating in {"BUY", "STRONG_BUY"}
        
        # Or low P/E ratio with decent Z-Score
        pe_ratio = company.key_metrics.get('pe_ratio', 999)
        has_low_pe = isinstance(pe_ratio, (int, float)) and pe_ratio < 20
        decent_zscore = company.z_score >= 1.5
        
        return has_value_buy or (has_low_pe and decent_zscore)
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by value metrics (P/E, P/B ratios) and Z-Score."""
        base_score = company.z_score
        
        # Bonus for low P/E ratio
        pe_ratio = company.key_metrics.get('pe_ratio', 999)
        if isinstance(pe_ratio, (int, float)) and pe_ratio > 0:
            pe_bonus = max(0, (20 - pe_ratio) / 20)  # Better score for lower P/E
        else:
            pe_bonus = 0
        
        # Bonus for low P/B ratio
        pb_ratio = company.key_metrics.get('pb_ratio', 999)
        if isinstance(pb_ratio, (int, float)) and pb_ratio > 0:
            pb_bonus = max(0, (3 - pb_ratio) / 3)  # Better score for lower P/B
        else:
            pb_bonus = 0
        
        return base_score + pe_bonus + pb_bonus


class GrowthStrategy(PortfolioStrategy):
    """Strategy for growth investing opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies with growth characteristics."""
        # Look for growth profile buy recommendation
        growth_rating = company.investment_ratings.get('growth_investor', '')
        has_growth_buy = growth_rating in {"BUY", "STRONG_BUY"}
        
        # Or high revenue growth with decent Z-Score
        revenue_growth = company.key_metrics.get('revenue_growth', 0)
        has_high_growth = isinstance(revenue_growth, (int, float)) and revenue_growth > 10
        decent_zscore = company.z_score >= 1.8
        
        return has_growth_buy or (has_high_growth and decent_zscore)
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by growth metrics and Z-Score."""
        base_score = company.z_score
        
        # Bonus for high revenue growth
        revenue_growth = company.key_metrics.get('revenue_growth', 0)
        if isinstance(revenue_growth, (int, float)):
            growth_bonus = min(2.0, revenue_growth / 20)  # Cap bonus at 2.0
        else:
            growth_bonus = 0
        
        return base_score + growth_bonus


class DividendStrategy(PortfolioStrategy):
    """Strategy for dividend investing opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies with dividend characteristics."""
        # Look for dividend profile buy recommendation
        dividend_rating = company.investment_ratings.get('dividend_investor', '')
        has_dividend_buy = dividend_rating in {"BUY", "STRONG_BUY"}
        
        # Should have stable Z-Score for dividend reliability
        stable_zscore = company.z_score >= 2.0
        
        return has_dividend_buy and stable_zscore
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by financial stability (Z-Score primarily)."""
        return company.z_score


class ConservativeStrategy(PortfolioStrategy):
    """Strategy for conservative investing opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies suitable for conservative investors."""
        # Look for conservative profile buy recommendation
        conservative_rating = company.investment_ratings.get('conservative_investor', '')
        has_conservative_buy = conservative_rating in {"BUY", "STRONG_BUY"}
        
        # Must have high Z-Score for safety
        safe_zscore = company.z_score >= 2.5
        
        return has_conservative_buy and safe_zscore
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by safety metrics (highest Z-Score first)."""
        return company.z_score


class AggressiveStrategy(PortfolioStrategy):
    """Strategy for aggressive investing opportunities."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies suitable for aggressive investors."""
        # Look for aggressive profile buy recommendation
        aggressive_rating = company.investment_ratings.get('aggressive_investor', '')
        has_aggressive_buy = aggressive_rating in {"BUY", "STRONG_BUY"}
        
        # Can accept lower Z-Scores for higher potential returns
        acceptable_zscore = company.z_score >= 1.0
        
        return has_aggressive_buy and acceptable_zscore
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by potential upside and AI confidence."""
        base_score = company.z_score
        
        # Bonus for AI confidence in aggressive picks
        ai_confidence = company.ai_insights.get('confidence_level', 50) / 100
        confidence_bonus = ai_confidence * 1.0
        
        return base_score + confidence_bonus


class ModelPortfolioStrategy(PortfolioStrategy):
    """Strategy for creating balanced model portfolios."""
    
    def should_include(self, company: CompanyData) -> bool:
        """Include companies suitable for model portfolios."""
        # Must have at least one buy recommendation
        buy_ratings = {"BUY", "STRONG_BUY"}
        has_buy_rating = any(
            rating in buy_ratings 
            for rating in company.investment_ratings.values()
        )
        
        # Must have reasonable Z-Score
        reasonable_zscore = company.z_score >= 1.8
        
        return has_buy_rating and reasonable_zscore
    
    def get_ranking_score(self, company: CompanyData) -> float:
        """Rank by overall quality and diversification potential."""
        base_score = company.z_score
        
        # Bonus for multiple buy ratings (indicates broad appeal)
        buy_ratings = {"BUY", "STRONG_BUY"}
        buy_count = sum(
            1 for rating in company.investment_ratings.values() 
            if rating in buy_ratings
        )
        diversity_bonus = buy_count * 0.3
        
        return base_score + diversity_bonus
