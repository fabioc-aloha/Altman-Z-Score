import os
import requests
from bs4 import BeautifulSoup, Tag # Import Tag
import json
from datetime import datetime
import time
import logging
import argparse
from dotenv import load_dotenv # Add this import
from urllib.parse import urljoin

# Basic configuration (should align with your project's settings if possible)
EDGAR_BASE = "https://www.sec.gov"
DATA_EDGAR_BASE = "https://data.sec.gov"
REQUEST_INTERVAL = 0.11 # Seconds (to be safe with SEC 10 requests/sec limit)
LAST_REQUEST_TIME = 0

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_user_agent():
    user_agent = os.getenv('SEC_USER_AGENT') or os.getenv('SEC_EDGAR_USER_AGENT')
    if not user_agent:
        logging.error("SEC_USER_AGENT or SEC_EDGAR_USER_AGENT environment variable is not set.")
        raise ValueError("SEC User-Agent not set.")
    return user_agent

def make_sec_request_debug(url: str, base_url_for_host_header: str = EDGAR_BASE) -> requests.Response:
    global LAST_REQUEST_TIME
    current_time = time.time()
    time_since_last = current_time - LAST_REQUEST_TIME
    if time_since_last < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - time_since_last)
    
    headers = {
        "User-Agent": get_user_agent(),
        "Accept": "application/json, text/html, */*",
        "Host": base_url_for_host_header.replace("https://", "").replace("http://", ""), # Extract host
        "Connection": "close" 
    }
    logging.info(f"Requesting URL: {url} with host: {headers['Host']}")
    response = requests.get(url, headers=headers, timeout=20)
    LAST_REQUEST_TIME = time.time()
    response.raise_for_status() # Raise an exception for HTTP errors

    # Validate response headers - similar to main script but simplified for debug
    content_type = response.headers.get('Content-Type', '').lower()
    if not any(ct in content_type for ct in ['application/json', 'text/html', 'application/xml', 'text/xml']):
        if url.lower().endswith('.xml') and 'xml' in content_type:
            pass # OK for XML file
        else:
            # Allow text/plain for directory listings if they don't set HTML type
            if not (url.endswith('/') and 'text/plain' in content_type):
                 logging.warning(f"Unexpected content type: {content_type} for URL: {url} in debug script")
                 # Not raising error here to allow flexibility in debug, but logging it.
    return response

def _make_absolute_url_debug(base_for_relative: str, path_or_url: str) -> str:
    """
    Helper to construct absolute URLs, adapted for debug_xbrl.py.
    Ensures that the base for relative paths is correctly used.
    """
    if path_or_url.startswith('http://') or path_or_url.startswith('https://'):
        return path_or_url
    
    # If path_or_url starts with '/', it's an absolute path from the server root.
    # Use EDGAR_BASE as the true base for such paths.
    if path_or_url.startswith('/'):
        return urljoin(EDGAR_BASE, path_or_url)
    
    # Otherwise, it's a relative path. Join it with base_for_relative.
    # base_for_relative should be the URL of the page/directory from which path_or_url was extracted.
    return urljoin(base_for_relative, path_or_url)


def find_latest_filing_debug(filings_json: dict, before_date_str: str, filing_types_to_check: list[str]) -> dict | None:
    target_date = datetime.strptime(before_date_str, "%Y-%m-%d")
    recent_filings = filings_json.get("filings", {}).get("recent", {})
    
    if not recent_filings:
        logging.warning("No 'recent' filings found in JSON.")
        return None

    forms = recent_filings.get("form", [])
    filing_dates = recent_filings.get("filingDate", [])
    accession_numbers = recent_filings.get("accessionNumber", [])
    primary_documents = recent_filings.get("primaryDocument", [])
    
    latest_filing_found = None
    latest_date_found = datetime.min

    for i in range(len(forms)):
        form_type = forms[i]
        date_str = filing_dates[i]
        
        if form_type in filing_types_to_check:
            try:
                filing_date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if latest_date_found < filing_date_obj <= target_date:
                    latest_date_found = filing_date_obj
                    latest_filing_found = {
                        "form": form_type,
                        "filingDate": date_str,
                        "accessionNumber": accession_numbers[i],
                        "primaryDocument": primary_documents[i]
                    }
            except ValueError:
                logging.warning(f"Could not parse date: {date_str}")
                continue
    
    if latest_filing_found:
        logging.info(f"Found latest filing: {latest_filing_found['form']} on {latest_filing_found['filingDate']}")
    else:
        logging.warning(f"No suitable filing found from types {filing_types_to_check} before {before_date_str}")
    return latest_filing_found

def fetch_xbrl_snippet(cik: str, filing_type: str, period_end_date: str, lines: int = 200):
    logging.info(f"--- Debugging XBRL for CIK: {cik}, Filing Type: {filing_type}, Before: {period_end_date} ---")
    try:
        cik_padded = cik.zfill(10)
        submissions_url = f"{DATA_EDGAR_BASE}/submissions/CIK{cik_padded}.json"
        
        logging.info(f"Fetching submissions from: {submissions_url}")
        response = make_sec_request_debug(submissions_url, DATA_EDGAR_BASE)
        filings_json = response.json()

        latest_filing_doc = find_latest_filing_debug(filings_json, period_end_date, [filing_type])

        if not latest_filing_doc:
            logging.error(f"No {filing_type} found for CIK {cik_padded} before {period_end_date}.")
            return

        acc_no_raw = latest_filing_doc["accessionNumber"]
        acc_no_clean = acc_no_raw.replace("-", "")
        primary_doc_name = latest_filing_doc["primaryDocument"]
        
        filing_dir_url = f"{EDGAR_BASE}/Archives/edgar/data/{int(cik_padded)}/{acc_no_clean}/"
        logging.info(f"Filing directory URL: {filing_dir_url}")

        xbrl_instance_url = None

        # Strategy 1: Primary document is XML and suitable (align with fetch_financials.py)
        if primary_doc_name.endswith('.xml') and not any(x.lower() in primary_doc_name.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml']):
            logging.info(f"Primary document {primary_doc_name} is an XML file, considering it as XBRL instance.")
            xbrl_instance_url = _make_absolute_url_debug(filing_dir_url, primary_doc_name)

        # Strategy 2: Scan the filing directory (align with fetch_financials.py)
        if not xbrl_instance_url:
            logging.info(f"Primary doc not XML or not suitable. Scanning directory: {filing_dir_url}")
            try:
                dir_response = make_sec_request_debug(filing_dir_url)
                dir_soup = BeautifulSoup(dir_response.text, 'html.parser')
                
                potential_xbrl_hrefs: list[str] = []
                for link_tag in dir_soup.find_all('a', href=True):
                    if not isinstance(link_tag, Tag): continue
                    href_attr = link_tag.get('href')
                    actual_href = href_attr[0] if isinstance(href_attr, list) else href_attr
                    if (isinstance(actual_href, str) and actual_href.endswith('.xml') and
                        not any(x.lower() in actual_href.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml'])): # Case-insensitive exclusion
                        potential_xbrl_hrefs.append(actual_href)

                if potential_xbrl_hrefs:
                    if len(potential_xbrl_hrefs) == 1:
                        chosen_href = potential_xbrl_hrefs[0]
                        logging.info(f"Found single potential XBRL file in directory: {chosen_href}")
                        xbrl_instance_url = _make_absolute_url_debug(filing_dir_url, chosen_href)
                    else:
                        # Refined heuristic matching fetch_financials.py
                        filtered_list = [h for h in potential_xbrl_hrefs if not any(kwd.lower() in h.lower() for kwd in ['schema', 'xsd', 'cal', 'def', 'lab', 'pre'])] # 'filingsummary.xml' already excluded
                        if not filtered_list:
                            logging.debug("Filtering (schema, etc.) removed all potential XBRL files, reverting to full list for choice.")
                            filtered_list = potential_xbrl_hrefs # Already excludes FilingSummary

                        preferred_candidates = []
                        primary_doc_name_base = primary_doc_name.split('.')[0]
                        for h_pref in filtered_list:
                            if acc_no_clean in h_pref or cik_padded in h_pref or primary_doc_name_base in h_pref:
                                preferred_candidates.append(h_pref)
                        
                        if preferred_candidates:
                            chosen_href = min(preferred_candidates, key=len)
                            logging.info(f"Multiple potential XBRL files. Preferred heuristic choice: {chosen_href} from list: {preferred_candidates}")
                        elif filtered_list:
                            chosen_href = min(filtered_list, key=len) 
                            logging.info(f"Multiple potential XBRL files. Fallback heuristic choice (shortest): {chosen_href} from list: {filtered_list}")
                        else: # Should not happen if potential_xbrl_hrefs was not empty
                            logging.warning(f"XBRL selection logic failed to choose from {potential_xbrl_hrefs} for {cik_padded}, acc {acc_no_raw}")
                            chosen_href = None

                        if chosen_href:
                            xbrl_instance_url = _make_absolute_url_debug(filing_dir_url, chosen_href)
            except Exception as e:
                logging.warning(f"Failed to fetch or parse directory listing {filing_dir_url} for debug: {e}")

        # Strategy 3: Primary document is HTML, parse it (align with fetch_financials.py)
        if not xbrl_instance_url and primary_doc_name.endswith(('.htm', '.html')):
            logging.info(f"Primary document {primary_doc_name} is HTML. Parsing for XBRL link...")
            primary_doc_full_url = _make_absolute_url_debug(filing_dir_url, primary_doc_name)
            try:
                primary_doc_response = make_sec_request_debug(primary_doc_full_url)
                primary_soup = BeautifulSoup(primary_doc_response.text, 'html.parser')
                
                for a_tag in primary_soup.find_all('a', href=True):
                    if not isinstance(a_tag, Tag): continue
                    href_attr = a_tag.get('href')
                    actual_href_from_html = href_attr[0] if isinstance(href_attr, list) else href_attr

                    if (isinstance(actual_href_from_html, str) and actual_href_from_html.endswith('.xml') and
                        not any(x.lower() in actual_href_from_html.lower() for x in ['_lab.xml', '_pre.xml', '_cal.xml', '_def.xml', 'filingsummary.xml'])): # Case-insensitive exclusion
                        tag_text_element = getattr(a_tag, 'string', None)
                        tag_text = str(tag_text_element).strip() if tag_text_element else ""
                        
                        if "INSTANCE" in tag_text.upper() or "XBRL" in tag_text.upper() or not tag_text:
                            logging.info(f"Found XBRL link in HTML primary document: {actual_href_from_html} (Text: \'{tag_text}\')")
                            xbrl_instance_url = _make_absolute_url_debug(primary_doc_full_url, actual_href_from_html)
                            break 
            except Exception as e:
                logging.warning(f"Failed to fetch or parse HTML primary document {primary_doc_full_url} for debug: {e}")

        if xbrl_instance_url:
            logging.info(f"Attempting to fetch XBRL content from: {xbrl_instance_url}")
            
            # Fetch the determined XBRL URL
            xbrl_response = make_sec_request_debug(xbrl_instance_url) # Host header will be derived from xbrl_instance_url
            content_type_final = xbrl_response.headers.get('Content-Type', '').lower()

            # Handle cases where the direct URL gives HTML, which might link to the actual XML (similar to main fetch_financials)
            if 'xml' not in content_type_final:
                if 'html' in content_type_final:
                    logging.warning(f"URL {xbrl_instance_url} returned HTML. Parsing for XML link (debug)...")
                    temp_soup = BeautifulSoup(xbrl_response.text, 'html.parser')
                    found_link_in_html_debug = False
                    for link_tag_html_debug in temp_soup.find_all('a', href=True):
                        if not isinstance(link_tag_html_debug, Tag): continue
                        href_attr_html_debug = link_tag_html_debug.get('href')
                        actual_href_html_debug = href_attr_html_debug[0] if isinstance(href_attr_html_debug, list) else href_attr_html_debug
                        if isinstance(actual_href_html_debug, str) and actual_href_html_debug.endswith('.xml'):
                            linked_xbrl_url_debug = _make_absolute_url_debug(xbrl_instance_url, actual_href_html_debug)
                            logging.info(f"Found XML link in HTML page (debug): {linked_xbrl_url_debug}. Fetching...")
                            xbrl_response = make_sec_request_debug(linked_xbrl_url_debug)
                            new_content_type_debug = xbrl_response.headers.get('Content-Type', '').lower()
                            if 'xml' not in new_content_type_debug:
                                logging.error(f"Linked document {linked_xbrl_url_debug} from HTML page is not XML: {new_content_type_debug}")
                                return # Stop if linked doc is also not XML
                            found_link_in_html_debug = True
                            logging.info(f"Successfully fetched XML from linked URL (debug): {linked_xbrl_url_debug}")
                            break 
                    
                    if not found_link_in_html_debug and ('xml' not in xbrl_response.headers.get('Content-Type', '').lower()):
                        logging.error(f"XBRL URL {xbrl_instance_url} returned HTML, and no valid XML link found within (debug).")
                        return
                else: # Not XML and not HTML
                    logging.error(f"Unexpected content type for XBRL from {xbrl_instance_url}: {content_type_final} (debug)")
                    return
            
            # Final check if xbrl_response is XML
            if 'xml' not in xbrl_response.headers.get('Content-Type', '').lower():
                logging.error(f"Final check: content from {xbrl_instance_url} (or linked) is not XML. Last content type: {xbrl_response.headers.get('Content-Type', '')} (debug)")
                return

            xbrl_content = xbrl_response.text
            
            print(f"\\n--- Start of XBRL Content (first {lines} lines) for CIK {cik} from {xbrl_instance_url} ---")
            for i, line_content in enumerate(xbrl_content.splitlines()):
                if i < lines:
                    print(line_content)
                else:
                    break
            print("--- End of XBRL Snippet ---")
        else:
            logging.error(f"Could not find or determine the XBRL instance document for CIK {cik} in filing {acc_no_raw}.")

    except ValueError as ve: # Catch SEC User-Agent not set
        logging.error(f"Configuration error: {ve}")
    except requests.exceptions.HTTPError as he:
        logging.error(f"HTTP error fetching data for CIK {cik}: {he} (URL: {he.request.url})")
        if he.response is not None:
            logging.error(f"Response content: {he.response.text[:500]}") # Log first 500 chars of error response
    except Exception as e:
        logging.error(f"An unexpected error occurred during XBRL debug fetch for CIK {cik}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_dotenv() # Load .env file
    parser = argparse.ArgumentParser(description="Fetch and display a snippet of an XBRL document from SEC EDGAR.")
    parser.add_argument("cik", help="Company CIK number.")
    parser.add_argument("--filing_type", default="20-F", help="Type of filing (e.g., 20-F, 10-K).")
    parser.add_argument("--date", default="2025-03-31", help="Latest filing date to consider (YYYY-MM-DD).")
    parser.add_argument("--lines", type=int, default=200, help="Number of lines of the XBRL to print.")
    
    args = parser.parse_args()
    
    # Ensure SEC_USER_AGENT is set, e.g. from .env file if your main project uses python-dotenv
    # For direct execution, you might need to set it manually if not already in environment:
    # os.environ['SEC_USER_AGENT'] = "Your Name Your.Email@example.com" 
    # os.environ['SEC_EDGAR_USER_AGENT'] = "Your Name Your.Email@example.com" 

    if not (os.getenv('SEC_USER_AGENT') or os.getenv('SEC_EDGAR_USER_AGENT')):
        print("ERROR: Please set the SEC_USER_AGENT or SEC_EDGAR_USER_AGENT environment variable.")
        print("Example: export SEC_USER_AGENT=\"Your Name Your.Email@example.com\"")
    else:
        fetch_xbrl_snippet(args.cik, args.filing_type, args.date, args.lines)
