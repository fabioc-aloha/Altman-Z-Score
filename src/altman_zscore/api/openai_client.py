import os
from openai import AzureOpenAI
import json
import logging
from typing import Optional

from .openai_helpers import (
    resolve_prompt_path,
    load_prompt_file,
    parse_llm_json_response,
)
from .rate_limiter import retry_with_backoff


class AzureOpenAIClient:
    """
    Client for interacting with Azure OpenAI API for completions and field mapping.

    Handles authentication, endpoint configuration, and provides methods for
    chat-based completions and AI-powered field mapping for financial data.
    """
    def __init__(self):
        """
        Initialize the AzureOpenAIClient with credentials and endpoint from environment variables.
        Raises:
            ValueError: If required environment variables are missing.
        """
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        if not all([self.api_key, self.endpoint, self.deployment]):
            raise ValueError("Missing Azure OpenAI configuration in environment variables.")
            
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )

    @retry_with_backoff(
        max_retries=5,
        backoff_factor=2.0,
        retry_exceptions=(Exception,),
        retry_status_codes=(429, 500, 502, 503, 504),
        status_code_getter=lambda resp: getattr(resp, 'status_code', None) if resp is not None else None,
    )
    def chat_completion(self, messages, temperature=0.0, max_tokens=8192, response_format: str = "text"):
        """
        Generate a chat completion using Azure OpenAI.

        Args:
            messages (list): List of message dicts for the chat (system/user roles).
            temperature (float): Sampling temperature for response randomness.
            max_tokens (int): Maximum number of tokens in the response.
            response_format (str): "text" (default) or "json_object" to force JSON output.
        Returns:
            dict: The full response from the OpenAI API.
        Raises:
            Exception: If the API call fails after retries.
        """
        try:
            api_args = dict(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            if response_format == "json_object":
                api_args["response_format"] = {"type": "json_object"}
            response = self.client.chat.completions.create(**api_args)
            return {"choices": [{"message": {"content": response.choices[0].message.content}}]}
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")

    def suggest_field_mapping(self, raw_fields, canonical_fields, sample_values=None, mapping_overrides=None):
        """
        Use Azure OpenAI to suggest a mapping from canonical fields to raw fields.

        Args:
            raw_fields (list[str]): List of raw field names from XBRL/EDGAR
            canonical_fields (list[str]): List of canonical fields (e.g., total_assets, retained_earnings)
            sample_values (dict, optional): Optional dict of {raw_field: value} for context
            mapping_overrides (dict, optional): Optional dict of {canonical_field: raw_field} to override mapping
        Returns:
            dict: {canonical_field: {"FoundField": matched_raw_field, "Value": value}}
        Raises:
            RuntimeError: If the LLM response cannot be parsed as JSON.
        """
        prompt_path = resolve_prompt_path("prompt_field_mapping.md")
        system_prompt = load_prompt_file(prompt_path)

        # Comprehensive financial keywords for filtering
        financial_keywords = {
            # Basic financial terms
            "total", "net", "gross", "operating", "consolidated",
            
            # Asset-related terms
            "assets", "current_assets", "fixed_assets", "intangible",
            "goodwill", "inventory", "receivables", "cash",
            
            # Liability-related terms
            "liabilities", "debt", "payables", "obligations",
            "current_liabilities", "long_term",
            
            # Income statement terms
            "revenue", "income", "earnings", "ebit", "ebitda",
            "profit", "loss", "margin", "sales", "cost",
            
            # Equity-related terms
            "equity", "capital", "stock", "shares", "retained",
            
            # Common abbreviations
            "rev", "inc", "exp", "amt", "bal", "acct",
            
            # Numerical indicators (for fiscal periods)
            "q1", "q2", "q3", "q4", "fy", "ytd", "ttm"
        }

        # Function to check if a field contains financial terms
        def is_financial_field(field):
            field_lower = field.lower()
            # Check for individual keywords
            if any(keyword in field_lower for keyword in financial_keywords):
                return True
            # Check for compound terms (e.g., "working_capital", "operating_income")
            field_parts = set(field_lower.replace("_", " ").replace("-", " ").split())
            if len(field_parts.intersection(financial_keywords)) >= 1:
                return True
            # Check for numeric patterns common in financial fields
            import re
            if re.search(r'(q[1-4]|20\d{2}|fy\d{2}|ttm)', field_lower):
                return True
            return False

        # Filter raw fields to include only likely financial fields
        filtered_raw_fields = [
            field for field in raw_fields 
            if is_financial_field(field)
        ]

        # Ensure we have enough fields for mapping
        if len(filtered_raw_fields) < len(canonical_fields):
            # If we filtered too aggressively, fall back to the full set
            filtered_raw_fields = raw_fields
            logging.warning("Field filtering was too aggressive, falling back to full field set")

        # Create a focused sample values dict with only the filtered fields
        filtered_sample_values = None
        if sample_values:
            filtered_sample_values = {
                k: v for k, v in sample_values.items() 
                if k in filtered_raw_fields
            }

        # Add context about the filtering process to the prompt
        user_prompt = f"""
Raw fields ({len(filtered_raw_fields)} most relevant of {len(raw_fields)} total): {filtered_raw_fields}\n
Canonical fields to map: {canonical_fields}\n
"""
        if filtered_sample_values:
            # Format sample values to be more readable
            formatted_samples = json.dumps(filtered_sample_values, indent=2)
            user_prompt += f"Sample values: {formatted_samples}\n"

        user_prompt += "Return a JSON object mapping each canonical field to an object with 'FoundField' (the best-matching raw field name or null) and 'Value' (the value for that field, or null)."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Save the prompt for troubleshooting
        try:
            from altman_zscore.utils.paths import get_output_dir
            prompt_save_path = os.path.join(get_output_dir(ticker=mapping_overrides.get('ticker') if mapping_overrides and 'ticker' in mapping_overrides else None), "field_mapping_prompt.txt")
            full_prompt = f"System prompt:\n{system_prompt}\n\nUser prompt:\n{user_prompt}"
            os.makedirs(os.path.dirname(prompt_save_path), exist_ok=True)
            with open(prompt_save_path, "w", encoding="utf-8") as f:
                f.write(full_prompt)
            logging.warning(f"[DEBUG] Field mapping prompt saved to {prompt_save_path}")
        except Exception as e:
            logging.warning(f"[DEBUG] Could not save field mapping prompt: {e}")

        try:
            response = self.chat_completion(messages, temperature=0.0, max_tokens=8192)
            content = response["choices"][0]["message"]["content"]
            mapping = parse_llm_json_response(content)
            if mapping_overrides:
                for canonical, override_field in mapping_overrides.items():
                    if override_field in raw_fields:
                        mapping[canonical] = {"FoundField": override_field, "Value": None}
            return mapping
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI field mapping: {e}\nResponse: {response}")

    def suggest_canonical_field_mapping(self, sec_fields, canonical_fields=None, ticker=None):
        """
        Use Azure OpenAI to map canonical Altman Z-Score fields to the best-matching SEC field names.

        Args:
            sec_fields (list[str]): Unique field names from SEC data
            canonical_fields (list[str], optional): List of canonical fields. Defaults to standard Altman Z-Score fields.
            ticker (str, optional): Ticker symbol to save prompt in ticker-specific output folder.
        Returns:
            dict: {canonical_field: [ordered list of plausible SEC field names]}
        Raises:
            RuntimeError: If the LLM response cannot be parsed as JSON.
        """
        if canonical_fields is None:
            canonical_fields = [
                "total_assets",
                "current_assets",
                "current_liabilities",
                "total_liabilities",
                "retained_earnings",
                "ebit",
                "sales",
            ]
        prompt_path = resolve_prompt_path("prompt_field_mapping_simple.md")
        system_prompt = load_prompt_file(prompt_path)
        # Compose the user prompt with only SEC field names
        user_prompt = (
            f"Available field names:\n"
            f"- SEC: {sec_fields}\n"
            f"\nCanonical fields: {canonical_fields}\n"
            f"\nPlease return the mapping as instructed."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        # Save the prompt for troubleshooting in the ticker folder if provided
        try:
            from altman_zscore.utils.paths import get_output_dir
            prompt_save_path = os.path.join(get_output_dir(ticker=ticker), "field_mapping_prompt_simple.txt")
            full_prompt = f"System prompt:\n{system_prompt}\n\nUser prompt:\n{user_prompt}"
            os.makedirs(os.path.dirname(prompt_save_path), exist_ok=True)
            with open(prompt_save_path, "w", encoding="utf-8") as f:
                f.write(full_prompt)
            logging.info(f"[DEBUG] Simple field mapping prompt saved to {prompt_save_path}")
        except Exception as e:
            logging.warning(f"[DEBUG] Could not save simple field mapping prompt: {e}")
        try:
            response = self.chat_completion(messages, temperature=0.0, max_tokens=1024, response_format="json_object")
            content = response["choices"][0]["message"]["content"]
            # Save the LLM response to a file in the ticker output directory
            if ticker:
                try:
                    from altman_zscore.utils.paths import get_output_dir
                    response_save_path = os.path.join(get_output_dir(ticker=ticker), "field_mapping_response_simple.json")
                    os.makedirs(os.path.dirname(response_save_path), exist_ok=True)
                    with open(response_save_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    logging.info(f"[DEBUG] Simple field mapping response saved to {response_save_path}")
                except Exception as e:
                    logging.warning(f"[DEBUG] Could not save simple field mapping response: {e}")
            mapping = parse_llm_json_response(content)
            return mapping
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI canonical field mapping: {e}\nResponse: {locals().get('response', None)}")

def get_llm_qualitative_commentary(prompt: str, ticker: Optional[str] = None) -> str:
    """
    Generate a qualitative commentary for the Altman Z-Score report using Azure OpenAI LLM.

    This function injects the content of all relevant data files for the ticker (if available)
    into the prompt for richer context, saves the prompt for traceability, and returns
    the LLM-generated commentary as plain text.

    Args:
        prompt (str): The full prompt to send to the LLM (should include context and instructions).
        ticker (str, optional): Stock ticker symbol to load company_info.json for context.
    Returns:
        str: The LLM-generated commentary as plain text.
    Raises:        RuntimeError: If the LLM response cannot be parsed as text.
    """
    import logging
    client = AzureOpenAIClient()
    prompt_path = resolve_prompt_path("prompt_fin_analysis.md")
    system_prompt = load_prompt_file(prompt_path)
    
    (
        company_officers_str,
        company_info_str,
        sec_info_str,
        analyst_recs_str,
        holders_str,
        dividends_str,
        splits_str,
        weekly_prices_str,
        zscore_data_str,
        metadata_str,
    ) = _inject_company_context(ticker)
    
    # Compose the full prompt with clear section headers for each data file
    # OPTIMIZED: Eliminates large redundant files (sec_facts_raw, financials_raw, weekly_prices.json, yf_info)
    full_prompt = (
        f"{zscore_data_str}{metadata_str}{analyst_recs_str}{weekly_prices_str}"
        f"{company_officers_str}{company_info_str}{sec_info_str}"
        f"{holders_str}{dividends_str}{splits_str}\n{prompt}"
    )
    if ticker:
        try:
            from altman_zscore.utils.paths import get_output_dir
            prompt_save_path = get_output_dir("llm_commentary_prompt.txt", ticker=ticker)
            with open(prompt_save_path, "w", encoding="utf-8") as f:
                f.write(full_prompt)
            logging.warning(f"[DEBUG] LLM commentary prompt saved to {prompt_save_path}")
        except Exception as e:
            logging.warning(f"[DEBUG] Could not save LLM commentary prompt: {e}")
    else:
        logging.warning("[DEBUG] No ticker provided for LLM commentary prompt save.")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_prompt},
    ]
    try:
        response = client.chat_completion(messages, temperature=0.0, max_tokens=8192)
        logging.warning(f"[DEBUG] LLM response: {response}")
        content = response["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        logging.error(f"[ERROR] Failed to parse LLM commentary: {e}\nResponse: {locals().get('response', None)}")
        return f"[ERROR] LLM commentary generation failed: {e}"


def _resolve_prompt_path(prompt_filename):
    """Resolve prompt file path, supporting both new and legacy locations."""
    prompt_path_new = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..", "prompts", prompt_filename
    )
    prompt_path_legacy = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "prompts", prompt_filename
    )
    if os.path.exists(prompt_path_new):
        return prompt_path_new
    elif os.path.exists(prompt_path_legacy):
        return prompt_path_legacy
    else:
        raise FileNotFoundError(
            f"Could not find {prompt_filename} in either src/prompts/ or src/altman_zscore/prompts/. Checked: {prompt_path_new}, {prompt_path_legacy}"
        )


def _load_prompt_file(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _strip_code_block_markers(content):
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[-1]
        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]
    return content


def _parse_llm_json_response(content):
    content = _strip_code_block_markers(content)
    return json.loads(content)


def _inject_company_context(ticker):
    """Return context strings for company officers, info, SEC info, analyst recommendations, and all relevant data for a ticker. 
    Optimized to reduce redundancy and prompt size - eliminates large redundant files."""
    company_officers_str = ""
    company_info_str = ""
    sec_info_str = ""
    analyst_recs_str = ""
    holders_str = ""
    dividends_str = ""
    splits_str = ""
    weekly_prices_str = ""
    zscore_data_str = ""
    metadata_str = ""
    
    if not ticker:
        return (company_officers_str, company_info_str, sec_info_str, analyst_recs_str, holders_str, dividends_str, splits_str, weekly_prices_str, zscore_data_str, metadata_str)
    
    from altman_zscore.utils.paths import get_output_dir
    base_dir = get_output_dir(ticker=ticker)
    
    # **OPTIMIZATION: Priority order - most important data first, eliminate redundancies**
    
    # 1. Z-Score calculations (CSV format for tabular data) - CRITICAL
    zscore_csv_path = os.path.join(base_dir, f"zscore_{ticker}.csv")
    if os.path.exists(zscore_csv_path):
        try:
            with open(zscore_csv_path, "r", encoding="utf-8") as f:
                zscore_data_str = f"\n\n# zscore_{ticker}.csv - Z-Score Calculations by Quarter\n{f.read()}\n"
        except Exception as e:
            zscore_data_str = f"\n[Could not load zscore_{ticker}.csv: {e}]\n"
    
    # 2. Model selection metadata (contains company profile + financial data) - CRITICAL
    metadata_path = os.path.join(base_dir, f"zscore_{ticker}_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata_json = json.load(f)
            
            # OPTIMIZATION: Remove redundant raw_quarters to save space (already in zscore calculations)
            if isinstance(metadata_json, dict) and "context" in metadata_json:
                context = metadata_json["context"].copy()
                if "raw_quarters" in context:
                    # Keep only summary info, remove detailed financial data to reduce redundancy
                    raw_quarters = context["raw_quarters"]
                    context["raw_quarters_summary"] = {
                        "quarters_count": len(raw_quarters),
                        "date_range": f"{raw_quarters[-1]['period_end']} to {raw_quarters[0]['period_end']}" if raw_quarters else "No data",
                        "note": "Detailed financial data available in Z-Score calculations above"
                    }
                    del context["raw_quarters"]
                metadata_json["context"] = context
                    
            metadata_str = f"\n\n# zscore_{ticker}_metadata.json - Model Selection and Analysis Context\n{json.dumps(metadata_json, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            metadata_str = f"\n[Could not load zscore_{ticker}_metadata.json: {e}]\n"    
    # 3. Company officers - MODERATE PRIORITY
    company_officers_path = os.path.join(base_dir, "company_officers.json")
    if os.path.exists(company_officers_path):
        try:
            with open(company_officers_path, "r", encoding="utf-8") as officers_file:
                officers_json = json.load(officers_file)
            company_officers_str = f"\n\n# company_officers.json\n{json.dumps(officers_json, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            company_officers_str = f"\n[Could not load company_officers.json: {e}]\n"
    
    # 4. Company info (trim 'filings') - MODERATE PRIORITY
    company_info_path = os.path.join(base_dir, "company_info.json")
    if os.path.exists(company_info_path):
        try:
            with open(company_info_path, "r", encoding="utf-8") as info_file:
                company_info = json.load(info_file)
            if isinstance(company_info, dict) and "filings" in company_info:
                company_info = {k: v for k, v in company_info.items() if k != "filings"}
            company_info_str = f"\n\n# company_info.json\n{json.dumps(company_info, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            company_info_str = f"\n[Could not load company_info.json: {e}]\n"
    
    # 5. SEC info (trim 'filings') - MODERATE PRIORITY
    sec_info_path = os.path.join(base_dir, "sec_edgar_company_info.json")
    if os.path.exists(sec_info_path):
        try:
            with open(sec_info_path, "r", encoding="utf-8") as sec_file:
                sec_info = json.load(sec_file)
            if isinstance(sec_info, dict) and "filings" in sec_info:
                sec_info = {k: v for k, v in sec_info.items() if k != "filings"}
            sec_info_str = f"\n\n# sec_edgar_company_info.json\n{json.dumps(sec_info, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            sec_info_str = f"\n[Could not load sec_edgar_company_info.json: {e}]\n"
    
    # 6. Analyst recommendations - HIGH PRIORITY for investment analysis
    analyst_recs_path = os.path.join(base_dir, "recommendations.json")
    if os.path.exists(analyst_recs_path):
        try:
            with open(analyst_recs_path, "r", encoding="utf-8") as rec_file:
                rec_data = json.load(rec_file)
            analyst_recs_str = f"\n\n# recommendations.json\n{json.dumps(rec_data, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            analyst_recs_str = f"\n[Could not load recommendations.json: {e}]\n"
    
    # 7. Institutional and major holders - MODERATE PRIORITY
    institutional_holders_path = os.path.join(base_dir, "institutional_holders.json")
    major_holders_path = os.path.join(base_dir, "major_holders.json")
    holders_sections = []
    if os.path.exists(institutional_holders_path):
        try:
            with open(institutional_holders_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            holders_sections.append(f"\n# institutional_holders.json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
        except Exception as e:
            holders_sections.append(f"\n[Could not load institutional_holders.json: {e}]\n")
    if os.path.exists(major_holders_path):
        try:
            with open(major_holders_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            holders_sections.append(f"\n# major_holders.json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
        except Exception as e:
            holders_sections.append(f"\n[Could not load major_holders.json: {e}]\n")
    holders_str = "".join(holders_sections)
    
    # 8. Dividends - MODERATE PRIORITY for income analysis
    dividends_path = os.path.join(base_dir, "dividends.csv")
    if os.path.exists(dividends_path):
        try:
            with open(dividends_path, "r", encoding="utf-8") as f:
                dividends_str = f"\n\n# dividends.csv\n{f.read()}\n"
        except Exception as e:
            dividends_str = f"\n[Could not load dividends.csv: {e}]\n"
    
    # 9. Splits - LOW PRIORITY
    splits_path = os.path.join(base_dir, "splits.csv")
    if os.path.exists(splits_path):
        try:
            with open(splits_path, "r", encoding="utf-8") as f:
                splits_str = f"\n\n# splits.csv\n{f.read()}\n"
        except Exception as e:
            splits_str = f"\n[Could not load splits.csv: {e}]\n"
    
    # 10. Weekly prices (CSV only, skip JSON to save space) - HIGH PRIORITY for price trend analysis
    weekly_prices_path = os.path.join(base_dir, "weekly_prices.csv")
    if os.path.exists(weekly_prices_path):
        try:
            with open(weekly_prices_path, "r", encoding="utf-8") as f:
                weekly_prices_str = f"\n\n# weekly_prices.csv - Price Data for Trend Analysis\n{f.read()}\n"
        except Exception as e:
            weekly_prices_str = f"\n[Could not load weekly_prices.csv: {e}]\n"
    
    # ELIMINATED REDUNDANT FILES TO OPTIMIZE PROMPT SIZE:
    # - sec_facts_raw.json (9.3 MB) - redundant with metadata
    # - financials_raw.json (55 KB) - redundant with Z-Score calculations
    # - weekly_prices.json (14 KB) - redundant with CSV
    # - yf_info.json (10 KB) - minimal added value, info available in company_info
    
    return (company_officers_str, company_info_str, sec_info_str, analyst_recs_str, holders_str, dividends_str, splits_str, weekly_prices_str, zscore_data_str, metadata_str)
