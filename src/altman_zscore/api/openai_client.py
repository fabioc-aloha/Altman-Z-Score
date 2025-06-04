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

    This function injects the content of company_info.json for the ticker (if available)
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
    company_officers_str, company_info_str, sec_info_str = inject_company_context(ticker)
    full_prompt = f"{company_officers_str}{company_info_str}{sec_info_str}\n{prompt}"
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
    """Return context strings for company officers, info, and SEC info for a ticker."""
    company_officers_str = ""
    company_info_str = ""
    sec_info_str = ""
    if not ticker:
        return company_officers_str, company_info_str, sec_info_str
    from altman_zscore.utils.paths import get_output_dir
    company_officers_path = get_output_dir("company_officers.json", ticker=ticker)
    company_info_path = get_output_dir("company_info.json", ticker=ticker)
    sec_info_path = get_output_dir("sec_edgar_company_info.json", ticker=ticker)
    if os.path.exists(company_officers_path):
        try:
            with open(company_officers_path, "r", encoding="utf-8") as officers_file:
                officers_json = json.load(officers_file)
            import io, pprint
            buf = io.StringIO()
            pprint.pprint(officers_json, stream=buf, compact=True, width=120)
            company_officers_str = f"\n\n# Key Executives and Officers (from Yahoo Finance)\n{buf.getvalue()}\n"
        except Exception as e:
            company_officers_str = f"\n[Could not load company_officers.json: {e}]\n"
    if os.path.exists(company_info_path):
        try:
            with open(company_info_path, "r", encoding="utf-8") as info_file:
                company_info = json.load(info_file)
            trimmed_company = extract_trimmed_company_info(company_info)
            import io, pprint
            buf = io.StringIO()
            pprint.pprint(trimmed_company, stream=buf, compact=True, width=120)
            company_info_str = f"\n\n# Company Profile (from Yahoo Finance)\n{buf.getvalue()}\n"
        except Exception as e:
            company_info_str = f"\n[Could not load company_info.json: {e}]\n"
    if os.path.exists(sec_info_path):
        try:
            with open(sec_info_path, "r", encoding="utf-8") as sec_file:
                sec_info = json.load(sec_file)
                trimmed = extract_trimmed_sec_info(sec_info)
                trimmed = {k: v for k, v in trimmed.items() if v is not None}
                if "business_address" in trimmed:
                    trimmed["business_address"] = {k: v for k, v in trimmed["business_address"].items() if v is not None}
                    if not trimmed["business_address"]:
                        del trimmed["business_address"]
                import io, pprint
                buf = io.StringIO()
                pprint.pprint(trimmed, stream=buf, compact=True, width=120)
                sec_info_str = f"\n\n# Key SEC EDGAR Company Info (trimmed)\n{buf.getvalue()}\n"
        except Exception as e:
            sec_info_str = f"\n[Could not load sec_edgar_company_info.json: {e}]\n"
    return company_officers_str, company_info_str, sec_info_str
