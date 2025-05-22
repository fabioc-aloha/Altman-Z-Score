"""
Industry comparison module for analyzing Z-Score trends and peer comparisons.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import statistics

from .industry_classifier import CompanyProfile, IndustryGroup, TechSubsector

@dataclass
class IndustryMetrics:
    """Container for industry-level Z-Score metrics."""
    mean_zscore: Decimal
    median_zscore: Decimal
    percentile_25: Decimal
    percentile_75: Decimal
    std_dev: Decimal
    sample_size: int
    
    @property
    def interquartile_range(self) -> Decimal:
        """Calculate the interquartile range of Z-Scores."""
        return self.percentile_75 - self.percentile_25
    
    def relative_position(self, zscore: Decimal) -> str:
        """
        Determine the relative position of a Z-Score within the industry.
        
        Args:
            zscore: Z-Score to compare
            
        Returns:
            str: Description of relative position
        """
        if zscore > self.percentile_75:
            return "Top Quartile"
        elif zscore > self.median_zscore:
            return "Above Median"
        elif zscore > self.percentile_25:
            return "Below Median"
        else:
            return "Bottom Quartile"
    
    def zscore_percentile(self, zscore: Decimal) -> Optional[int]:
        """
        Estimate the percentile of a Z-Score within the industry.
        Uses a normal distribution approximation.
        
        Args:
            zscore: Z-Score to evaluate
            
        Returns:
            Optional[int]: Estimated percentile (0-100)
        """
        try:
            from scipy import stats
            z = float((zscore - self.median_zscore) / self.std_dev)
            percentile = float(stats.norm.cdf(z) * 100)
            return round(percentile)
        except ImportError:
            return None

@dataclass
class TrendAnalysis:
    """Analysis of Z-Score trends over time."""
    time_periods: List[str]
    zscores: List[Decimal]
    industry_medians: List[Decimal]
    
    @property
    def trend_direction(self) -> str:
        """Determine the overall trend direction."""
        if len(self.zscores) < 2:
            return "Insufficient Data"
            
        changes = [self.zscores[i] - self.zscores[i-1] 
                  for i in range(1, len(self.zscores))]
        
        if all(change > Decimal('0') for change in changes):
            return "Improving"
        elif all(change < Decimal('0') for change in changes):
            return "Declining"
        else:
            return "Mixed"
    
    @property
    def relative_trend(self) -> str:
        """Compare trend to industry median trend."""
        if len(self.zscores) < 2:
            return "Insufficient Data"
            
        company_change = self.zscores[-1] - self.zscores[0]
        industry_change = self.industry_medians[-1] - self.industry_medians[0]
        
        if company_change > industry_change:
            return "Outperforming Industry"
        elif company_change < industry_change:
            return "Underperforming Industry"
        else:
            return "Tracking Industry"

class IndustryComparison:
    """Handles industry peer comparison and trend analysis."""
    
    def __init__(self, peer_data: Dict[str, Dict]):
        """
        Initialize with peer company data.
        
        Args:
            peer_data: Dictionary of company data (key: company_id)
        """
        self.peer_data = peer_data
    
    def get_industry_metrics(self, profile: CompanyProfile) -> IndustryMetrics:
        """
        Calculate industry-level Z-Score metrics.
        
        Args:
            profile: Company profile for filtering peers
            
        Returns:
            IndustryMetrics: Calculated industry metrics
        """
        # Filter peers by industry group and subsector
        peers = self._filter_peers(profile)
        
        if not peers:
            raise ValueError("Insufficient peer data for analysis")
        
        # Extract Z-Scores
        zscores = [Decimal(str(peer['zscore'])) for peer in peers]
        
        return IndustryMetrics(
            mean_zscore=Decimal(str(statistics.mean(zscores))),
            median_zscore=Decimal(str(statistics.median(zscores))),
            percentile_25=Decimal(str(statistics.quantiles(zscores, n=4)[0])),
            percentile_75=Decimal(str(statistics.quantiles(zscores, n=4)[2])),
            std_dev=Decimal(str(statistics.stdev(zscores))) if len(zscores) > 1 else Decimal('0'),
            sample_size=len(zscores)
        )
    
    def analyze_trends(self, company_id: str, profile: CompanyProfile,
                      periods: List[str]) -> TrendAnalysis:
        """
        Analyze Z-Score trends over time.
        
        Args:
            company_id: ID of the company to analyze
            profile: Company profile for peer filtering
            periods: List of time periods to analyze
            
        Returns:
            TrendAnalysis: Trend analysis results
        """
        company_scores = []
        industry_medians = []
        
        for period in periods:
            # Get company score for period
            company_score = self._get_company_score(company_id, period)
            if company_score is None:
                continue
                
            # Get industry median for period
            industry_median = self._get_industry_median(profile, period)
            if industry_median is None:
                continue
                
            company_scores.append(company_score)
            industry_medians.append(industry_median)
        
        if not company_scores or not industry_medians:
            raise ValueError("Insufficient data for trend analysis")
            
        return TrendAnalysis(
            time_periods=periods[:len(company_scores)],
            zscores=company_scores,
            industry_medians=industry_medians
        )
    
    def get_peer_group(self, profile: CompanyProfile,
                      limit: int = 5) -> List[Tuple[str, Decimal]]:
        """
        Get the closest peer companies by Z-Score.
        
        Args:
            profile: Company profile for filtering peers
            limit: Maximum number of peers to return
            
        Returns:
            List[Tuple[str, Decimal]]: List of (company_id, zscore) tuples
        """
        peers = self._filter_peers(profile)
        
        # Sort by Z-Score
        sorted_peers = sorted(peers, key=lambda x: x['zscore'])
        
        # Return top matches
        return [(peer['company_id'], Decimal(str(peer['zscore']))) 
                for peer in sorted_peers[:limit]]
    
    def _filter_peers(self, profile: CompanyProfile) -> List[Dict]:
        """Filter peer companies by industry classification."""
        return [
            peer for peer in self.peer_data.values()
            if (peer.get('industry_group') == profile.industry_group and
                (profile.tech_subsector is None or 
                 peer.get('tech_subsector') == profile.tech_subsector))
        ]
    
    def _get_company_score(self, company_id: str, period: str) -> Optional[Decimal]:
        """Get a company's Z-Score for a specific period."""
        company = self.peer_data.get(company_id)
        if not company or period not in company.get('historical_scores', {}):
            return None
        return Decimal(str(company['historical_scores'][period]))
    
    def _get_industry_median(self, profile: CompanyProfile,
                           period: str) -> Optional[Decimal]:
        """Calculate industry median Z-Score for a specific period."""
        peers = self._filter_peers(profile)
        period_scores = []
        
        for peer in peers:
            score = peer.get('historical_scores', {}).get(period)
            if score is not None:
                period_scores.append(Decimal(str(score)))
        
        if not period_scores:
            return None
            
        return Decimal(str(statistics.median(period_scores)))
