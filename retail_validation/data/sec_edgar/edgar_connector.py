# SEC EDGAR Connector for Delisted Companies
# This file provides functionality to retrieve historical financial data
# for delisted companies from the SEC EDGAR database.

import json
import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class EdgarConnector:
    """Connector for retrieving historical financial data from SEC EDGAR"""
    
    def __init__(self, cache_dir: str = None):
        """Initialize the Edgar connector
        
        Args:
            cache_dir: Directory to store cached SEC data
        """
        self.headers = {
            # Using proper User-Agent header as required by SEC
            'User-Agent': 'RetailModelValidator/1.0 (research@altmanzscore.org)'
        }
        self.base_url = "https://www.sec.gov/Archives"
        self.edgar_search_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        
        # Set up caching for SEC data
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "cache" / "sec_edgar"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load CIK mapping
        self.cik_map = self._load_cik_mapping()
        
        # Request throttling to comply with SEC rate limits
        self.request_delay = 0.1  # seconds between requests
        self.last_request_time = 0
    
    def _load_cik_mapping(self) -> Dict[str, str]:
        """Load the mapping of tickers to CIK numbers"""
        cik_file = Path(__file__).parent / "cik_ticker_map.json"
        
        if cik_file.exists():
            with open(cik_file, 'r') as f:
                return json.load(f)
        else:
            # Create a minimal mapping with our bankrupt companies
            bankruptcy_ciks = {
                "NMRCQ": "0001398666",  # Neiman Marcus
                "JCPNQ": "0001166126",  # JCPenney
                "SHLDQ": "0001310067",  # Sears Holdings
                "BRKSQ": "0000078890",  # Brooks Brothers
                "PIRRQ": "0000278130",  # Pier 1 Imports
                "TOY": "0001005414",    # Toys R Us
                "BONTQ": "0000878765",  # Bon-Ton Stores
                "RSHCQ": "0000096289",  # RadioShack
                "TSAQ": "0001022442",   # Sports Authority
                "PSDSQ": "0000808292",  # Payless ShoeSource
                "F21Q": "0000930337",   # Forever 21
                "GYMQ": "0001059212",   # Gymboree
            }
            
            # Write the mapping to file for future use
            with open(cik_file, 'w') as f:
                json.dump(bankruptcy_ciks, f, indent=4)
            
            return bankruptcy_ciks
    
    async def _throttled_request(self, url: str) -> Optional[str]:
        """Make a throttled request to SEC EDGAR"""
        # Ensure we don't exceed rate limits
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last)
        
        self.last_request_time = datetime.now().timestamp()
        
        # Make the request
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"Error fetching {url}: Status {response.status}")
                        return None
        except Exception as e:
            print(f"Error making request to {url}: {str(e)}")
            return None
    
    async def get_cik_for_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK for a ticker symbol"""
        # First check our mapping
        if ticker in self.cik_map:
            return self.cik_map[ticker]
        
        # If not in our mapping, try to look it up from SEC
        # This is a simplified implementation
        search_url = f"{self.edgar_search_url}?CIK={ticker}&Find=Search&owner=exclude&action=getcompany"
        
        html_content = await self._throttled_request(search_url)
        if not html_content:
            return None
        
        # Parse the CIK from the response
        soup = BeautifulSoup(html_content, 'html.parser')
        cik_match = re.search(r'CIK=(\d+)', html_content)
        
        if cik_match:
            cik = cik_match.group(1).zfill(10)
            
            # Update our mapping
            self.cik_map[ticker] = cik
            cik_file = Path(__file__).parent / "cik_ticker_map.json"
            with open(cik_file, 'w') as f:
                json.dump(self.cik_map, f, indent=4)
            
            return cik
        
        return None
    
    async def get_recent_filings(self, ticker: str, filing_type: str = "10-K",
                              years_before_bankruptcy: int = 3) -> List[Dict]:
        """Get recent filings before bankruptcy
        
        Args:
            ticker: Company ticker symbol
            filing_type: Filing type (10-K or 10-Q)
            years_before_bankruptcy: Number of years before bankruptcy to retrieve
            
        Returns:
            List of filing information dictionaries
        """
        # Get the CIK for this ticker
        cik = await self.get_cik_for_ticker(ticker)
        if not cik:
            print(f"Could not find CIK for {ticker}")
            return []
        
        # Get the bankruptcy date
        from retail_validation.config.validation_config import BANKRUPTCY_DATES
        if ticker not in BANKRUPTCY_DATES:
            print(f"No bankruptcy date found for {ticker}")
            return []
        
        bankruptcy_date = datetime.strptime(BANKRUPTCY_DATES[ticker], "%Y-%m-%d")
        start_date = bankruptcy_date - timedelta(days=365 * years_before_bankruptcy)
        
        # Check cache first
        cache_file = self.cache_dir / f"{ticker}_{filing_type}_filings.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                filings = json.load(f)
                # Filter by date
                return [f for f in filings if datetime.strptime(f['filing_date'], "%Y-%m-%d") >= start_date]
        
        # Build the search URL
        search_url = (
            f"{self.edgar_search_url}?action=getcompany&CIK={cik}&type={filing_type}"
            f"&dateb={bankruptcy_date.strftime('%Y%m%d')}&datea={start_date.strftime('%Y%m%d')}"
            f"&owner=exclude&count=100"
        )
        
        html_content = await self._throttled_request(search_url)
        if not html_content:
            return []
        
        # Parse filing information
        soup = BeautifulSoup(html_content, 'html.parser')
        filing_tables = soup.select('table.tableFile2')
        
        if not filing_tables:
            print(f"No filing tables found for {ticker}")
            return []
        
        filings = []
        for table in filing_tables:
            rows = table.select('tr')
            for row in rows[1:]:  # Skip header row
                cells = row.select('td')
                if len(cells) >= 4:
                    filing_info = {
                        'filing_type': cells[0].get_text().strip(),
                        'filing_date': datetime.strptime(cells[3].get_text().strip(), "%Y-%m-%d").strftime("%Y-%m-%d"),
                        'filing_link': 'https://www.sec.gov' + cells[1].select_one('a')['href'] if cells[1].select_one('a') else None,
                        'filing_desc': cells[2].get_text().strip() if len(cells) > 2 else ''
                    }
                    filings.append(filing_info)
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(filings, f, indent=4)
        
        return filings
    
    async def extract_financial_data(self, filing_url: str) -> Dict:
        """Extract financial data from filing HTML
        
        Args:
            filing_url: URL to the SEC filing
            
        Returns:
            Dictionary of extracted financial data
        """
        # Use the specialized filing parser
        from retail_validation.data.sec_edgar.filing_parser import FilingParser
        
        parser = FilingParser()
        return await parser.extract_financial_data_from_filing(filing_url)
    
    async def get_financial_data(self, ticker: str, 
                           quarters_before_bankruptcy: int = 4) -> Optional[Dict]:
        """Get financial data for calculating Z-Score
        
        Args:
            ticker: Company ticker symbol
            quarters_before_bankruptcy: Number of quarters before bankruptcy to analyze
            
        Returns:
            Dictionary of financial data suitable for Z-Score calculation
        """
        # Find bankruptcy date
        from retail_validation.config.validation_config import BANKRUPTCY_DATES
        if ticker not in BANKRUPTCY_DATES:
            print(f"No bankruptcy date found for {ticker}")
            return None
        
        bankruptcy_date = BANKRUPTCY_DATES[ticker]
        
        # Get annual and quarterly filings before bankruptcy
        annual_filings = await self.get_recent_filings(ticker, "10-K", 3)
        if not annual_filings:
            print(f"No annual filings found for {ticker}")
        else:
            print(f"Found {len(annual_filings)} annual filings for {ticker}")
        
        quarterly_filings = await self.get_recent_filings(ticker, "10-Q", max(3, quarters_before_bankruptcy // 4 + 1))
        if not quarterly_filings:
            print(f"No quarterly filings found for {ticker}")
        else:
            print(f"Found {len(quarterly_filings)} quarterly filings for {ticker}")
        
        if not annual_filings and not quarterly_filings:
            print(f"No filings found for {ticker}")
            return None
        
        # Choose the most recent filing before bankruptcy
        all_filings = sorted(
            annual_filings + quarterly_filings,
            key=lambda f: f['filing_date'],
            reverse=True
        )
        
        if not all_filings:
            return None
        
        # Get the most recent filing that has a filing_link
        filing = None
        for f in all_filings:
            if f.get('filing_link'):
                filing = f
                break
        
        if not filing:
            print(f"No filing with link found for {ticker}")
            return None
        
        print(f"Using {filing['filing_type']} from {filing['filing_date']} for {ticker}")
        
        # Extract financial data from the filing
        financial_data = await self.extract_financial_data(filing['filing_link'])
        if not financial_data:
            print(f"Failed to extract financial data for {ticker}")
            return None
        
        # Add metadata
        financial_data['filing_date'] = filing['filing_date']
        financial_data['filing_type'] = filing['filing_type']
        financial_data['ticker'] = ticker
        
        # Calculate quarters before bankruptcy
        filing_date = datetime.strptime(filing['filing_date'], "%Y-%m-%d")
        bankruptcy_date_obj = datetime.strptime(bankruptcy_date, "%Y-%m-%d")
        days_before = (bankruptcy_date_obj - filing_date).days
        financial_data['quarters_before_bankruptcy'] = days_before // 91  # ~91 days per quarter
        
        return financial_data
    
    async def transform_to_zscore_input(self, financial_data: Dict) -> Dict:
        """Transform SEC financial data to Z-Score input format
        
        Args:
            financial_data: Raw financial data extracted from SEC filings
            
        Returns:
            Financial data formatted for Z-Score calculation
        """
        from retail_validation.data.sec_edgar.filing_parser import FilingParser
        
        parser = FilingParser()
        transformed = parser.transform_to_zscore_input(
            financial_data,
            ticker=financial_data['ticker'],
            filing_date=financial_data['filing_date'],
            filing_type=financial_data['filing_type']
        )
        
        if transformed:
            # Add bankruptcy-specific metadata
            transformed['metadata']['quarters_before_bankruptcy'] = financial_data['quarters_before_bankruptcy']
            
            # Create Z-Score compatible object
            from altman_zscore.models.data_models import MergedFinancialData
            return MergedFinancialData(**transformed)
        
        return None

# Create an initialization file
if __name__ == "__main__":
    print("SEC EDGAR Connector for Retail Validation Framework")
    print("This module provides functionality to retrieve historical financial data")
    print("for delisted companies from the SEC EDGAR database.")
    
    # Example usage
    async def test():
        connector = EdgarConnector()
        ticker = "SHLDQ"  # Sears Holdings
        print(f"Testing with {ticker}")
        
        cik = await connector.get_cik_for_ticker(ticker)
        print(f"CIK: {cik}")
        
        filings = await connector.get_recent_filings(ticker)
        print(f"Found {len(filings)} filings")
        
        data = await connector.get_financial_data(ticker)
        if data:
            print(f"Financial data retrieved for {ticker}")
            print(json.dumps(data, indent=2))
    
    # asyncio.run(test())  # Uncomment to test
