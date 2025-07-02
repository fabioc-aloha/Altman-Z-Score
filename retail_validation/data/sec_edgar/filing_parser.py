"""
SEC EDGAR Financial Statement Parser
===================================

This module extracts financial data from SEC EDGAR filings for use in the
retail validation framework. It handles both modern XBRL filings and older
HTML-formatted filings.

It focuses on extracting key metrics needed for Z-Score calculation:
- Current Assets
- Total Assets
- Current Liabilities
- Total Liabilities
- Retained Earnings
- EBIT (Earnings Before Interest and Taxes)
- Sales/Revenue
- Inventory (for retail model)
- COGS (for retail model inventory turnover)
"""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
import aiohttp
from typing import Dict, List, Optional, Union, Any
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilingParser:
    """Parser for SEC EDGAR financial statements"""
    
    def __init__(self, cache_dir: str = None):
        """Initialize the filing parser
        
        Args:
            cache_dir: Directory to cache parsed financial data
        """
        self.headers = {
            # Using proper User-Agent header as required by SEC
            'User-Agent': 'RetailModelValidator/1.0 (research@altmanzscore.org)'
        }
        
        # Set up caching for parsed data
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / "cache" / "parsed_filings"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Define key financial terms to search for
        self.metric_patterns = {
            'current_assets': [
                r'current\s+assets?',
                r'total\s+current\s+assets'
            ],
            'total_assets': [
                r'total\s+assets',
                r'assets?\s+\-\s+total',
                r'consolidated\s+assets'
            ],
            'current_liabilities': [
                r'current\s+liabilit(y|ies)',
                r'total\s+current\s+liabilit(y|ies)'
            ],
            'total_liabilities': [
                r'total\s+liabilit(y|ies)',
                r'liabilit(y|ies)\s+\-\s+total',
                r'consolidated\s+liabilit(y|ies)'
            ],
            'retained_earnings': [
                r'retained\s+earnings',
                r'accumulated\s+(deficit|earnings)',
                r'accumulated\s+retained\s+earnings'
            ],
            'ebit': [
                r'earnings\s+before\s+interest\s+(and|&)\s+tax(es)?',
                r'operating\s+income\s+\(loss\)',
                r'income\s+from\s+operations',
                r'operating\s+profit'
            ],
            'sales': [
                r'net\s+sales',
                r'revenue',
                r'total\s+revenue',
                r'sales\s+and\s+revenue',
                r'consolidated\s+sales'
            ],
            'inventory': [
                r'inventory',
                r'inventories',
                r'merchandise\s+inventory'
            ],
            'cogs': [
                r'cost\s+of\s+(goods\s+sold|sales)',
                r'cost\s+of\s+revenue',
                r'cost\s+of\s+merchandise\s+sold'
            ]
        }
    
    async def extract_financial_data_from_filing(self, filing_url: str) -> Dict:
        """Extract financial data from an SEC filing
        
        Args:
            filing_url: URL to the SEC filing
            
        Returns:
            Dictionary of extracted financial data
        """
        # Check cache first
        cache_key = filing_url.split('/')[-1]
        cache_file = self.cache_dir / f"{cache_key}_data.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Fetch the filing content
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(filing_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch filing: {response.status}")
                        return {}
                    
                    content = await response.text()
            except Exception as e:
                logger.error(f"Error fetching filing: {str(e)}")
                return {}
        
        # First try XBRL extraction for modern filings
        financial_data = await self._extract_from_xbrl(filing_url, content)
        
        # If XBRL extraction fails, try HTML table parsing for older filings
        if not financial_data or all(v is None for v in financial_data.values()):
            logger.info("XBRL extraction failed or incomplete, trying HTML tables")
            financial_data = self._extract_from_html_tables(content)
        
        # Cache the results
        if financial_data:
            with open(cache_file, 'w') as f:
                json.dump(financial_data, f, indent=4)
        
        return financial_data
    
    async def _extract_from_xbrl(self, filing_url: str, content: str) -> Dict:
        """Extract financial data from XBRL in filing
        
        Args:
            filing_url: URL to the SEC filing
            content: HTML content of the filing
            
        Returns:
            Dictionary of financial data from XBRL
        """
        # Try to locate embedded XBRL data or link to XBRL file
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check for embedded XBRL
        xbrl_elements = soup.select('*[contextref]')
        if xbrl_elements:
            return self._parse_embedded_xbrl(soup)
        
        # Check for XBRL instance document link
        xbrl_links = [a['href'] for a in soup.find_all('a') 
                    if a.get('href') and '.xml' in a.get('href').lower()]
        
        if xbrl_links:
            # Fetch XBRL file
            xbrl_url = f"https://www.sec.gov{xbrl_links[0]}" if xbrl_links[0].startswith('/') else xbrl_links[0]
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(xbrl_url, headers=self.headers) as response:
                        if response.status == 200:
                            xbrl_content = await response.text()
                            return self._parse_xbrl_file(xbrl_content)
            except Exception as e:
                logger.error(f"Error fetching XBRL file: {str(e)}")
        
        return {}
    
    def _parse_embedded_xbrl(self, soup: BeautifulSoup) -> Dict:
        """Parse embedded XBRL in filing
        
        Args:
            soup: BeautifulSoup object of the filing HTML
            
        Returns:
            Dictionary of financial data
        """
        data = {
            'current_assets': None,
            'total_assets': None,
            'current_liabilities': None, 
            'total_liabilities': None,
            'retained_earnings': None,
            'ebit': None,
            'sales': None,
            'inventory': None,
            'cogs': None
        }
        
        # Common XBRL tag mappings for financial metrics
        tag_mappings = {
            'current_assets': ['us-gaap:AssetsCurrent', 'us-gaap:CurrentAssets'],
            'total_assets': ['us-gaap:Assets', 'us-gaap:AssetsTotal'],
            'current_liabilities': ['us-gaap:LiabilitiesCurrent', 'us-gaap:CurrentLiabilities'],
            'total_liabilities': ['us-gaap:Liabilities', 'us-gaap:LiabilitiesTotal'],
            'retained_earnings': ['us-gaap:RetainedEarnings', 'us-gaap:AccumulatedDeficit', 
                                'us-gaap:RetainedEarningsAccumulatedDeficit'],
            'ebit': ['us-gaap:OperatingIncomeLoss', 'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes'],
            'sales': ['us-gaap:Revenues', 'us-gaap:SalesRevenueNet', 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax'],
            'inventory': ['us-gaap:InventoryNet', 'us-gaap:Inventories'],
            'cogs': ['us-gaap:CostOfGoodsAndServicesSold', 'us-gaap:CostOfRevenue', 'us-gaap:CostOfGoodsSold']
        }
        
        # Extract the most recent period
        contexts = {}
        for ctx in soup.find_all(attrs={"id": re.compile(r'^(i_|ctx_|c_)')}):
            if ctx.find('instant'):
                contexts[ctx['id']] = ctx.find('instant').text
            elif ctx.find('enddate'):
                contexts[ctx['id']] = ctx.find('enddate').text
        
        # Sort contexts by date
        sorted_contexts = sorted(contexts.items(), key=lambda x: x[1], reverse=True)
        
        # For each metric, try to find its value
        for metric, tags in tag_mappings.items():
            for tag in tags:
                for element in soup.find_all(tag.lower().replace('-', ':'), recursive=True):
                    if element.get('contextref') in contexts:
                        try:
                            data[metric] = float(element.text.replace(',', '').strip())
                            break
                        except (ValueError, TypeError):
                            continue
            
        return data
    
    def _parse_xbrl_file(self, xbrl_content: str) -> Dict:
        """Parse XBRL file content
        
        Args:
            xbrl_content: XML content of XBRL file
            
        Returns:
            Dictionary of financial data
        """
        # Similar to _parse_embedded_xbrl but for standalone XBRL file
        soup = BeautifulSoup(xbrl_content, 'lxml-xml')
        
        data = {
            'current_assets': None,
            'total_assets': None,
            'current_liabilities': None, 
            'total_liabilities': None,
            'retained_earnings': None,
            'ebit': None,
            'sales': None,
            'inventory': None,
            'cogs': None
        }
        
        # Common XBRL tag mappings (same as in _parse_embedded_xbrl)
        tag_mappings = {
            'current_assets': ['us-gaap:AssetsCurrent', 'us-gaap:CurrentAssets'],
            'total_assets': ['us-gaap:Assets', 'us-gaap:AssetsTotal'],
            'current_liabilities': ['us-gaap:LiabilitiesCurrent', 'us-gaap:CurrentLiabilities'],
            'total_liabilities': ['us-gaap:Liabilities', 'us-gaap:LiabilitiesTotal'],
            'retained_earnings': ['us-gaap:RetainedEarnings', 'us-gaap:AccumulatedDeficit', 
                                'us-gaap:RetainedEarningsAccumulatedDeficit'],
            'ebit': ['us-gaap:OperatingIncomeLoss', 'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes'],
            'sales': ['us-gaap:Revenues', 'us-gaap:SalesRevenueNet', 'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax'],
            'inventory': ['us-gaap:InventoryNet', 'us-gaap:Inventories'],
            'cogs': ['us-gaap:CostOfGoodsAndServicesSold', 'us-gaap:CostOfRevenue', 'us-gaap:CostOfGoodsSold']
        }
        
        # Find context elements to determine time periods
        contexts = {}
        for ctx in soup.find_all('context'):
            ctx_id = ctx.get('id')
            if ctx.find('instant'):
                contexts[ctx_id] = ctx.find('instant').text
            elif ctx.find('enddate'):
                contexts[ctx_id] = ctx.find('enddate').text
        
        # Sort contexts by date (most recent first)
        sorted_contexts = sorted(contexts.items(), key=lambda x: x[1], reverse=True)
        recent_contexts = [ctx_id for ctx_id, _ in sorted_contexts[:5]]  # Take 5 most recent contexts
        
        # For each metric, try to find its value
        for metric, tags in tag_mappings.items():
            for tag in tags:
                tag_without_namespace = tag.split(':')[1].lower()
                
                # Try with various namespace prefixes
                for prefix in ['us-gaap', 'gaap', '']:
                    tag_to_search = f"{prefix}:{tag_without_namespace}" if prefix else tag_without_namespace
                    
                    for element in soup.find_all(tag_to_search, recursive=True):
                        ctx_ref = element.get('contextref')
                        
                        # Try to use a recent context
                        if ctx_ref in recent_contexts:
                            try:
                                data[metric] = float(element.text.replace(',', '').strip())
                                break
                            except (ValueError, TypeError):
                                continue
                    
                    # If we found the metric, break out of prefix loop
                    if data[metric] is not None:
                        break
                
                # If we found the metric, break out of tag loop
                if data[metric] is not None:
                    break
        
        return data
    
    def _extract_from_html_tables(self, content: str) -> Dict:
        """Extract financial data from HTML tables in filing
        
        Args:
            content: HTML content of the filing
            
        Returns:
            Dictionary of financial data
        """
        soup = BeautifulSoup(content, 'html.parser')
        data = {
            'current_assets': None,
            'total_assets': None,
            'current_liabilities': None, 
            'total_liabilities': None,
            'retained_earnings': None,
            'ebit': None,
            'sales': None,
            'inventory': None,
            'cogs': None
        }
        
        # Look for tables with financial data
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text().lower()
            
            # Look for balance sheet tables
            if ('balance sheet' in table_text or 'financial position' in table_text or 
                'statement of financial condition' in table_text or 'assets and liabilities' in table_text):
                self._parse_balance_sheet_table(table, data)
            
            # Look for income statement tables
            if ('statement of operations' in table_text or 'income statement' in table_text or 
                'statement of income' in table_text or 'statement of earnings' in table_text or
                'profit and loss' in table_text or 'revenues and expenses' in table_text):
                self._parse_income_statement_table(table, data)
        
        return data
    
    def _parse_balance_sheet_table(self, table, data: Dict) -> None:
        """Parse balance sheet table for relevant metrics
        
        Args:
            table: BeautifulSoup table element
            data: Dictionary to update with extracted values
        """
        rows = table.find_all('tr')
        
        # Find rows with financial metrics
        for row in rows:
            row_text = row.get_text().lower().strip()
            
            # Extract cells (look for the last numeric cell as the value)
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # Try to get numeric value from the last cell or second-to-last cell
            value = None
            for cell_idx in range(len(cells)-1, 0, -1):
                cell_text = cells[cell_idx].get_text().strip()
                # Check for numeric content
                num_match = re.search(r'[\d,\.]+', cell_text)
                if num_match:
                    try:
                        # Remove common prefixes and convert to float
                        cleaned_text = re.sub(r'^\$|\(|\)|\$', '', num_match.group())
                        value = float(cleaned_text.replace(',', ''))
                        # Handle negative values in parentheses
                        if '(' in cell_text and ')' in cell_text:
                            value = -value
                        break
                    except (ValueError, TypeError):
                        continue
            
            if value is None:
                continue
            
            # Match row text against metric patterns
            for metric, patterns in self.metric_patterns.items():
                if metric in ['current_assets', 'total_assets', 'current_liabilities', 
                             'total_liabilities', 'retained_earnings', 'inventory']:
                    for pattern in patterns:
                        if re.search(pattern, row_text, re.IGNORECASE):
                            data[metric] = value
                            break
    
    def _parse_income_statement_table(self, table, data: Dict) -> None:
        """Parse income statement table for relevant metrics
        
        Args:
            table: BeautifulSoup table element
            data: Dictionary to update with extracted values
        """
        rows = table.find_all('tr')
        
        # Find rows with financial metrics
        for row in rows:
            row_text = row.get_text().lower().strip()
            
            # Extract cells (look for the last numeric cell as the value)
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # Try to get numeric value from the last cell or second-to-last cell
            value = None
            for cell_idx in range(len(cells)-1, 0, -1):
                cell_text = cells[cell_idx].get_text().strip()
                # Check for numeric content
                num_match = re.search(r'[\d,\.]+', cell_text)
                if num_match:
                    try:
                        # Remove common prefixes and convert to float
                        cleaned_text = re.sub(r'^\$|\(|\)|\$', '', num_match.group())
                        value = float(cleaned_text.replace(',', ''))
                        # Handle negative values in parentheses
                        if '(' in cell_text and ')' in cell_text:
                            value = -value
                        break
                    except (ValueError, TypeError):
                        continue
            
            if value is None:
                continue
            
            # Match row text against metric patterns
            for metric, patterns in self.metric_patterns.items():
                if metric in ['ebit', 'sales', 'cogs']:
                    for pattern in patterns:
                        if re.search(pattern, row_text, re.IGNORECASE):
                            data[metric] = value
                            break
    
    def transform_to_zscore_input(self, financial_data: Dict, ticker: str,
                               filing_date: str, filing_type: str) -> Dict:
        """Transform extracted financial data to Z-Score input format
        
        Args:
            financial_data: Dictionary of extracted financial data
            ticker: Company ticker symbol
            filing_date: Date of the filing
            filing_type: Type of filing (10-K or 10-Q)
            
        Returns:
            Dictionary with financial data formatted for Z-Score calculation
        """
        # Check for required fields
        required_fields = ['current_assets', 'total_assets', 'current_liabilities', 
                         'total_liabilities', 'retained_earnings', 'ebit', 'sales']
        
        missing_fields = [f for f in required_fields if f not in financial_data or financial_data[f] is None]
        if missing_fields:
            logger.warning(f"Missing required fields for Z-Score calculation: {missing_fields}")
            
            # Fill in missing fields with reasonable estimates where possible
            if 'current_assets' in missing_fields and 'total_assets' in financial_data and financial_data['total_assets']:
                # Estimate current assets as 40% of total assets (common for retailers)
                financial_data['current_assets'] = financial_data['total_assets'] * 0.4
                logger.info(f"Estimated missing current_assets as {financial_data['current_assets']}")
            
            if 'current_liabilities' in missing_fields and 'total_liabilities' in financial_data and financial_data['total_liabilities']:
                # Estimate current liabilities as 60% of total liabilities (common for retailers)
                financial_data['current_liabilities'] = financial_data['total_liabilities'] * 0.6
                logger.info(f"Estimated missing current_liabilities as {financial_data['current_liabilities']}")
                
            # Re-check after estimation
            missing_fields = [f for f in required_fields if f not in financial_data or financial_data[f] is None]
            if missing_fields:
                logger.error(f"Still missing required fields after estimation: {missing_fields}")
                return None
        
        # Create a structured format for Z-Score calculation
        return {
            'symbol': ticker,
            'period': 'quarter' if filing_type == '10-Q' else 'annual',
            'date': filing_date,
            'metrics': {
                'total_current_assets': financial_data['current_assets'],
                'total_assets': financial_data['total_assets'],
                'total_current_liabilities': financial_data['current_liabilities'],
                'total_liabilities': financial_data['total_liabilities'],
                'retained_earnings': financial_data['retained_earnings'],
                'ebit': financial_data['ebit'],
                'revenue': financial_data['sales'],
                # Add inventory and other metrics if available
                'inventory': financial_data.get('inventory', 0),
                'cost_of_revenue': financial_data.get('cogs', 0),
            },
            'metadata': {
                'source': 'sec_edgar',
                'filing_type': filing_type,
                'filing_date': filing_date,
                'data_quality': self._assess_data_quality(financial_data)
            }
        }
    
    def _assess_data_quality(self, data: Dict) -> Dict:
        """Assess the quality and completeness of extracted financial data
        
        Args:
            data: Dictionary of financial data
            
        Returns:
            Dictionary with data quality metrics
        """
        # Calculate how many fields were successfully extracted
        total_fields = len(data)
        extracted_fields = sum(1 for v in data.values() if v is not None)
        completion_rate = extracted_fields / total_fields if total_fields > 0 else 0
        
        # Check for consistency in the data
        consistency_issues = []
        
        # Current assets should be less than total assets
        if (data.get('current_assets') and data.get('total_assets') and 
            data['current_assets'] > data['total_assets']):
            consistency_issues.append("Current assets exceed total assets")
        
        # Current liabilities should be less than total liabilities
        if (data.get('current_liabilities') and data.get('total_liabilities') and 
            data['current_liabilities'] > data['total_liabilities']):
            consistency_issues.append("Current liabilities exceed total liabilities")
        
        # COGS should be less than sales
        if data.get('cogs') and data.get('sales') and data['cogs'] > data['sales']:
            consistency_issues.append("COGS exceed sales")
        
        return {
            'completion_rate': completion_rate,
            'consistency_issues': consistency_issues,
            'estimated_fields': [],  # Would be populated in transform_to_zscore_input
            'overall_quality': 'high' if completion_rate > 0.8 and not consistency_issues else 
                            'medium' if completion_rate > 0.6 and len(consistency_issues) <= 2 else 
                            'low'
        }

# For testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        parser = FilingParser()
        # Example filing URL
        filing_url = "https://www.sec.gov/Archives/edgar/data/1310067/000131006717000013/shld-20170128x10k.htm"
        
        print(f"Extracting financial data from {filing_url}")
        financial_data = await parser.extract_financial_data_from_filing(filing_url)
        
        print("Extracted financial data:")
        print(json.dumps(financial_data, indent=2))
        
        transformed = parser.transform_to_zscore_input(
            financial_data, 
            ticker="SHLDQ", 
            filing_date="2017-01-28", 
            filing_type="10-K"
        )
        
        if transformed:
            print("\nTransformed to Z-Score input:")
            print(json.dumps(transformed, indent=2))
        else:
            print("\nFailed to transform data for Z-Score calculation")
    
    # asyncio.run(test())  # Uncomment to test
