import os
import json
import requests
from typing import Optional
from .openai_helpers import (
    resolve_prompt_path,
    load_prompt_file,
    strip_code_block_markers,
    parse_llm_json_response,
    inject_company_context,
    extract_trimmed_sec_info,
    extract_trimmed_company_info,
)


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
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        self.model = os.getenv("AZURE_OPENAI_MODEL")
        if not all([self.api_key, self.endpoint, self.deployment]):
            raise ValueError("Missing Azure OpenAI configuration in environment variables.")

    def chat_completion(self, messages, temperature=0.0, max_tokens=4096):
        """
        Generate a chat completion using Azure OpenAI.

        Args:
            messages (list): List of message dicts for the chat (system/user roles).
            temperature (float): Sampling temperature for response randomness.
            max_tokens (int): Maximum number of tokens in the response.
        Returns:
            dict: The full response from the OpenAI API.
        Raises:
            requests.HTTPError: If the API call fails.
        """
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        payload = {"messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def suggest_field_mapping(self, raw_fields, canonical_fields, sample_values=None, mapping_overrides=None):
        """
        Use Azure OpenAI to suggest a mapping from canonical fields to raw fields.

        Args:
            raw_fields (list[str]): List of raw field names (from XBRL/EDGAR)
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
        user_prompt = f"""
Raw fields: {raw_fields}\n
Canonical fields: {canonical_fields}\n
"""
        if sample_values:
            user_prompt += f"Sample values: {sample_values}\n"
        user_prompt += "Return a JSON object mapping each canonical field to an object with 'FoundField' (the best-matching raw field name or null) and 'Value' (the value for that field, or null)."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.chat_completion(messages, temperature=0.0, max_tokens=4096)
        try:
            content = response["choices"][0]["message"]["content"]
            mapping = parse_llm_json_response(content)
            if mapping_overrides:
                for canonical, override_field in mapping_overrides.items():
                    if override_field in raw_fields:
                        mapping[canonical] = {"FoundField": override_field, "Value": None}
            return mapping
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI field mapping: {e}\nResponse: {response}")


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
    Raises:
        RuntimeError: If the LLM response cannot be parsed as text.
    """
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
        financials_raw_str,
        yf_info_str,
    ) = _inject_company_context(ticker)
    # Compose the full prompt with clear section headers for each data file
    full_prompt = (
        f"{company_officers_str}{company_info_str}{sec_info_str}{analyst_recs_str}"
        f"{holders_str}{dividends_str}{splits_str}{weekly_prices_str}{financials_raw_str}{yf_info_str}\n{prompt}"
    )
    if ticker:
        try:
            from altman_zscore.utils.paths import get_output_dir
            prompt_save_path = get_output_dir("llm_commentary_prompt.txt", ticker=ticker)
            with open(prompt_save_path, "w", encoding="utf-8") as f:
                f.write(full_prompt)
        except Exception:
            pass
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_prompt},
    ]
    response = client.chat_completion(messages, temperature=0.0, max_tokens=4096)
    try:
        content = response["choices"][0]["message"]["content"]
        return content.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to parse LLM commentary: {e}\nResponse: {response}")


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
    """Return context strings for company officers, info, SEC info, analyst recommendations, and all relevant data for a ticker. Trims large keys like 'filings'."""
    company_officers_str = ""
    company_info_str = ""
    sec_info_str = ""
    analyst_recs_str = ""
    holders_str = ""
    dividends_str = ""
    splits_str = ""
    weekly_prices_str = ""
    financials_raw_str = ""
    yf_info_str = ""
    if not ticker:
        return (company_officers_str, company_info_str, sec_info_str, analyst_recs_str, holders_str, dividends_str, splits_str, weekly_prices_str, financials_raw_str, yf_info_str)
    from altman_zscore.utils.paths import get_output_dir
    base_dir = get_output_dir(ticker=ticker)
    # Existing context injections
    company_officers_path = os.path.join(base_dir, "company_officers.json")
    company_info_path = os.path.join(base_dir, "company_info.json")
    sec_info_path = os.path.join(base_dir, "sec_edgar_company_info.json")
    analyst_recs_path = os.path.join(base_dir, "recommendations.json")
    institutional_holders_path = os.path.join(base_dir, "institutional_holders.json")
    major_holders_path = os.path.join(base_dir, "major_holders.json")
    dividends_path = os.path.join(base_dir, "dividends.csv")
    splits_path = os.path.join(base_dir, "splits.csv")
    weekly_prices_path = os.path.join(base_dir, "weekly_prices.csv")
    weekly_prices_json_path = os.path.join(base_dir, "weekly_prices.json")
    financials_raw_path = os.path.join(base_dir, "financials_raw.json")
    yf_info_path = os.path.join(base_dir, "yf_info.json")
    # Officers
    if os.path.exists(company_officers_path):
        try:
            with open(company_officers_path, "r", encoding="utf-8") as officers_file:
                officers_json = json.load(officers_file)
            company_officers_str = f"\n\n# company_officers.json\n{json.dumps(officers_json, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            company_officers_str = f"\n[Could not load company_officers.json: {e}]\n"
    # Company info (trim 'filings')
    if os.path.exists(company_info_path):
        try:
            with open(company_info_path, "r", encoding="utf-8") as info_file:
                company_info = json.load(info_file)
            if isinstance(company_info, dict) and "filings" in company_info:
                company_info = {k: v for k, v in company_info.items() if k != "filings"}
            company_info_str = f"\n\n# company_info.json\n{json.dumps(company_info, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            company_info_str = f"\n[Could not load company_info.json: {e}]\n"
    # SEC info (trim 'filings')
    if os.path.exists(sec_info_path):
        try:
            with open(sec_info_path, "r", encoding="utf-8") as sec_file:
                sec_info = json.load(sec_file)
            if isinstance(sec_info, dict) and "filings" in sec_info:
                sec_info = {k: v for k, v in sec_info.items() if k != "filings"}
            sec_info_str = f"\n\n# sec_edgar_company_info.json\n{json.dumps(sec_info, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            sec_info_str = f"\n[Could not load sec_edgar_company_info.json: {e}]\n"
    # Analyst recommendations
    if os.path.exists(analyst_recs_path):
        try:
            with open(analyst_recs_path, "r", encoding="utf-8") as rec_file:
                rec_data = json.load(rec_file)
            analyst_recs_str = f"\n\n# recommendations.json\n{json.dumps(rec_data, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            analyst_recs_str = f"\n[Could not load recommendations.json: {e}]\n"
    # Institutional and major holders
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
    # Dividends
    if os.path.exists(dividends_path):
        try:
            with open(dividends_path, "r", encoding="utf-8") as f:
                dividends_str = f"\n# dividends.csv\n{f.read()}\n"
        except Exception as e:
            dividends_str = f"\n[Could not load dividends.csv: {e}]\n"
    # Splits
    if os.path.exists(splits_path):
        try:
            with open(splits_path, "r", encoding="utf-8") as f:
                splits_str = f"\n# splits.csv\n{f.read()}\n"
        except Exception as e:
            splits_str = f"\n[Could not load splits.csv: {e}]\n"
    # Weekly prices (CSV and JSON)
    if os.path.exists(weekly_prices_path):
        try:
            with open(weekly_prices_path, "r", encoding="utf-8") as f:
                weekly_prices_str = f"\n# weekly_prices.csv\n{f.read()}\n"
        except Exception as e:
            weekly_prices_str = f"\n[Could not load weekly_prices.csv: {e}]\n"
    elif os.path.exists(weekly_prices_json_path):
        try:
            with open(weekly_prices_json_path, "r", encoding="utf-8") as f:
                import io, pprint
                data = json.load(f)
                buf = io.StringIO()
                # pprint.pprint(data, stream=buf, compact=True, width=120)
                # All pprint output is suppressed to avoid printing input data
                weekly_prices_str = f"\n# weekly_prices.json\n{buf.getvalue()}\n"
        except Exception as e:
            weekly_prices_str = f"\n[Could not load weekly_prices.json: {e}]\n"
    # Financials raw
    if os.path.exists(financials_raw_path):
        try:
            with open(financials_raw_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            financials_raw_str = f"\n# financials_raw.json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            financials_raw_str = f"\n[Could not load financials_raw.json: {e}]\n"
    # yf_info
    if os.path.exists(yf_info_path):
        try:
            with open(yf_info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            yf_info_str = f"\n# yf_info.json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n"
        except Exception as e:
            yf_info_str = f"\n[Could not load yf_info.json: {e}]\n"
    return (company_officers_str, company_info_str, sec_info_str, analyst_recs_str, holders_str, dividends_str, splits_str, weekly_prices_str, financials_raw_str, yf_info_str)
