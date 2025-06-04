"""
Executive/officer data fetching and parsing utilities for financials module refactor.
"""
import os
import json
import logging
from typing import Any, Dict, Optional
import yfinance as yf
from altman_zscore.utils.paths import get_output_dir

def fetch_company_officers(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch company officers information using yfinance.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        dict or None: Company officers information if available, else None

    Notes:
        - Fetches officer information from yfinance info property
        - Returns None if no officer data is found
        - Logs any errors during fetch
    """
    logger = logging.getLogger("altman_zscore.fetch_company_officers")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            logger.warning(f"No company info found for {ticker}")
            return None

        # Extract officers if available
        officers = info.get('companyOfficers') or info.get('officers') or []

        # Format officer data
        formatted_officers = []
        for officer in officers:
            formatted_officer = {
                'name': officer.get('name'),
                'title': officer.get('title'),
                'yearBorn': officer.get('yearBorn'),
                'age': officer.get('age'),
                'totalPay': officer.get('totalPay'),
            }
            formatted_officers.append(formatted_officer)

        if not formatted_officers:
            logger.warning(f"No officer data found for {ticker}")
            return None

        # Save the data
        output_dir = get_output_dir(ticker)
        officers_file = os.path.join(output_dir, "company_officers.json")
        with open(officers_file, 'w', encoding='utf-8') as f:
            json.dump({'officers': formatted_officers}, f, indent=4, ensure_ascii=False)

        return {'officers': formatted_officers}

    except Exception as e:
        logger.error(f"Error fetching company officers for {ticker}: {e}")
        return None

def fetch_executive_data(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetch executive data from both yfinance (primary) and SEC EDGAR (supplementary).
    Merges data from both sources when available.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')

    Returns:
        dict or None: Executive data if available, else None

    Notes:
        - Uses yfinance as primary source for current officers
        - Uses SEC EDGAR DEF 14A filings for additional/historical data
        - Merges data when available from both sources
        - Returns None if no data is found from either source
    """
    logger = logging.getLogger("altman_zscore.fetch_executive_data")
    output_dir = get_output_dir(ticker)

    try:
        # 1. First try yfinance
        stock = yf.Ticker(ticker)
        info = stock.info
        yf_officers = []

        if info:
            # Extract officers if available
            officers = info.get('companyOfficers') or info.get('officers') or []
            for officer in officers:
                formatted_officer = {
                    'name': officer.get('name'),
                    'title': officer.get('title'),
                    'yearBorn': officer.get('yearBorn'),
                    'age': officer.get('age'),
                    'totalPay': officer.get('totalPay'),
                    'source': 'yfinance'
                }
                yf_officers.append(formatted_officer)

        # 2. Try SEC EDGAR
        sec_officers = []
        try:
            from altman_zscore.api.sec_client import SECClient
            from bs4 import BeautifulSoup, Tag  # Import Tag for type hints
            client = SECClient()
            
            # First get CIK
            cik = client.lookup_cik(ticker)
            if cik:
                # Get company submissions
                url = f"{SECClient.SUBMISSIONS_BASE_URL}CIK{cik.zfill(10)}.json"
                import requests
                response = requests.get(url, 
                    headers={'User-Agent': f'altman-zscore-analyzer ({os.getenv("SEC_API_EMAIL")})'})
                
                if response.ok:
                    data = response.json()
                    filings = data.get('filings', {}).get('recent', {})
                    
                    if filings:
                        form_types = filings.get('form', [])
                        accession_numbers = filings.get('accessionNumber', [])
                        primary_docs = filings.get('primaryDocument', [])
                        filing_dates = filings.get('filingDate', [])

                        # Find latest DEF 14A filing
                        def_14a_indices = [i for i, form in enumerate(form_types) if form == 'DEF 14A']
                        if def_14a_indices:
                            latest_def_14a_idx = def_14a_indices[0]
                            accession_number = accession_numbers[latest_def_14a_idx].replace('-', '')
                            primary_doc = primary_docs[latest_def_14a_idx]
                            filing_date = filing_dates[latest_def_14a_idx]

                            # Get the filing content
                            filing_url = f"{SECClient.ARCHIVES_BASE_URL}{cik}/{accession_number}/{primary_doc}"
                            response = requests.get(filing_url, 
                                headers={'User-Agent': f'altman-zscore-analyzer ({os.getenv("SEC_API_EMAIL")})'})
                            
                            if response.ok:
                                soup = BeautifulSoup(response.content, 'html.parser')
                                
                                # Find table with executive information
                                exec_keywords = ['executive', 'officer', 'compensation']
                                tables = soup.find_all('table')
                                
                                for table in tables:
                                    if not isinstance(table, Tag):
                                        continue
                                    
                                    # Check if this table has executive info
                                    table_text = table.get_text().lower()
                                    if not any(keyword in table_text for keyword in exec_keywords):
                                        continue
                                    
                                    rows = table.find_all('tr')
                                    if not rows or len(rows) < 2:  # Need at least header + one row
                                        continue

                                    # Check header row
                                    header = rows[0]
                                    if not isinstance(header, Tag):
                                        continue
                                    
                                    header_cells = header.find_all(['th', 'td'])
                                    header_text = ' '.join(cell.get_text().lower() for cell in header_cells if isinstance(cell, Tag))
                                    
                                    # Look for name/title columns
                                    if not ('name' in header_text and any(word in header_text for word in ['title', 'position'])):
                                        continue

                                    # Process data rows
                                    for row in rows[1:]:
                                        if not isinstance(row, Tag):
                                            continue
                                            
                                        cells = row.find_all(['td', 'th'])
                                        if len(cells) >= 2:
                                            name = cells[0].get_text().strip() if isinstance(cells[0], Tag) else ""
                                            title = cells[1].get_text().strip() if isinstance(cells[1], Tag) else ""
                                            
                                            # Try to find compensation in remaining cells
                                            compensation = None
                                            for cell in cells[2:]:
                                                if not isinstance(cell, Tag):
                                                    continue
                                                    
                                                text = cell.get_text().strip()
                                                if any(x in text.lower() for x in ['total', 'compensation', 'salary']):
                                                    try:
                                                        comp_str = ''.join(c for c in text if c.isdigit() or c == '.')
                                                        compensation = float(comp_str) if comp_str else None
                                                        break
                                                    except ValueError:
                                                        pass

                                            if name and title:
                                                officer = {
                                                    'name': name,
                                                    'title': title,
                                                    'totalPay': compensation,
                                                    'filingDate': filing_date,
                                                    'source': 'sec_edgar'
                                                }
                                                sec_officers.append(officer)

        except Exception as e:
            logger.warning(f"Error fetching SEC EDGAR executive data for {ticker}: {e}")

        # 3. Merge both sources
        all_officers = []
        seen_names = set()

        # Add yfinance officers first (they're usually more current)
        for officer in yf_officers:
            name = officer['name']
            if name not in seen_names:
                seen_names.add(name)
                all_officers.append(officer)

        # Add SEC officers if they don't exist in yfinance data
        for officer in sec_officers:
            name = officer['name']
            if name not in seen_names:
                seen_names.add(name)
                all_officers.append(officer)

        if not all_officers:
            logger.warning(f"No executive data found for {ticker} from either source")
            return None

        # Save the combined data
        result = {'officers': all_officers}
        officers_file = os.path.join(output_dir, "company_officers.json")
        with open(officers_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        return result

    except Exception as e:
        logger.error(f"Error fetching executive data for {ticker}: {e}")
        return None
