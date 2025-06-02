import os
import json
import requests
from typing import Optional


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
        # --- Prompt Ingestion for Field Mapping ---
        # Try both new (src/prompts/) and legacy (src/altman_zscore/prompts/) locations for backward compatibility
        prompt_path_new = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "..", "prompts", "prompt_field_mapping.md"
        )
        prompt_path_legacy = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts", "prompt_field_mapping.md"
        )
        if os.path.exists(prompt_path_new):
            prompt_path = prompt_path_new
        elif os.path.exists(prompt_path_legacy):
            prompt_path = prompt_path_legacy
        else:
            raise FileNotFoundError(
                f"Could not find prompt_field_mapping.md in either src/prompts/ or src/altman_zscore/prompts/. Checked: {prompt_path_new}, {prompt_path_legacy}"
            )
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
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
        # --- Use LLM for all language/synonym mapping ---
        # The LLM prompt is now responsible for robust, multilingual, and semantic field mapping.
        # The Python code will only apply user-supplied mapping overrides if present, and otherwise trust the LLM output.
        response = self.chat_completion(messages, temperature=0.0, max_tokens=4096)
        try:
            content = response["choices"][0]["message"]["content"]
            import json

            # Strip code block markers if present
            if content.strip().startswith("```"):
                content = content.strip().split("\n", 1)[-1]
                if content.endswith("```"):
                    content = content.rsplit("```", 1)[0]
            mapping = json.loads(content)
            # Apply user-supplied mapping overrides if present
            if mapping_overrides:
                for canonical, override_field in mapping_overrides.items():
                    if override_field in raw_fields:
                        mapping[canonical] = {"FoundField": override_field, "Value": None}
            return mapping
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI field mapping: {e}\nResponse: {response}")


def _extract_trimmed_sec_info(sec_info: dict) -> dict:
    """
    Extract only the most relevant fields from SEC EDGAR company info for prompt injection.
    Exclude the 'filings' field entirely.
    """
    return {
        "name": sec_info.get("name"),
        "cik": sec_info.get("cik"),
        "sic": sec_info.get("sic"),
        "sicDescription": sec_info.get("sicDescription"),
        "stateOfIncorporation": sec_info.get("stateOfIncorporation"),
        "fiscalYearEnd": sec_info.get("fiscalYearEnd"),
        "category": sec_info.get("category"),
        "business_address": sec_info.get("addresses", {}).get("business", {}),
        "phone": sec_info.get("phone"),
        "tickers": sec_info.get("tickers"),
        "exchanges": sec_info.get("exchanges"),
        "ein": sec_info.get("ein"),
        "website": sec_info.get("website"),
    }


def _extract_trimmed_company_info(company_info: dict) -> dict:
    """
    Extract only the most relevant fields from Yahoo Finance company info for prompt injection.
    Exclude the 'filings' field entirely and remove None values.
    """
    # Remove specific fields we don't want
    filtered = {k: v for k, v in company_info.items() if k != "filings" and v is not None}

    # Process nested dictionaries
    for k, v in list(filtered.items()):
        if isinstance(v, dict):
            # Recursively clean nested dictionaries
            filtered[k] = {sk: sv for sk, sv in v.items() if sv is not None}
            if not filtered[k]:  # Remove if empty
                del filtered[k]
        elif isinstance(v, list):
            # Clean up lists to remove None values and empty dicts
            filtered[k] = [x for x in v if x is not None and (not isinstance(x, dict) or any(x.values()))]
            if not filtered[k]:  # Remove if empty
                del filtered[k]

    return filtered


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
    # Try both new (src/prompts/) and legacy (src/altman_zscore/prompts/) locations for backward compatibility
    prompt_path_new = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..", "prompts", "prompt_fin_analysis.md"
    )
    prompt_path_legacy = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "prompt_fin_analysis.md")
    if os.path.exists(prompt_path_new):
        prompt_path = prompt_path_new
    elif os.path.exists(prompt_path_legacy):
        prompt_path = prompt_path_legacy
    else:
        raise FileNotFoundError(
            f"Could not find prompt_fin_analysis.md in either src/prompts/ or src/altman_zscore/prompts/. Checked: {prompt_path_new}, {prompt_path_legacy}"
        )
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    # Inject company_info.json content if ticker is provided
    company_info_str = ""
    sec_info_str = ""
    if ticker:
        from altman_zscore.utils.paths import get_output_dir
        company_info_path = get_output_dir("company_info.json", ticker=ticker)
        sec_info_path = get_output_dir("sec_edgar_company_info.json", ticker=ticker)
        if os.path.exists(company_info_path):
            try:
                with open(company_info_path, "r", encoding="utf-8") as info_file:
                    company_info = json.load(info_file)
                # First extract the trimmed info
                trimmed_company = _extract_trimmed_company_info(company_info)
                import io
                import pprint
                buf = io.StringIO()
                pprint.pprint(trimmed_company, stream=buf, compact=True, width=120)
                company_info_str = f"\n\n# Company Profile (from Yahoo Finance)\n{buf.getvalue()}\n"
            except Exception as e:
                company_info_str = f"\n[Could not load company_info.json: {e}]\n"
        if os.path.exists(sec_info_path):
            try:
                with open(sec_info_path, "r", encoding="utf-8") as sec_file:
                    sec_info = json.load(sec_file)
                    # First extract the trimmed info
                    trimmed = _extract_trimmed_sec_info(sec_info)
                    # Remove any None values to reduce noise
                    trimmed = {k: v for k, v in trimmed.items() if v is not None}
                    # Also filter out None values from nested dictionaries like business_address
                    if "business_address" in trimmed:
                        trimmed["business_address"] = {k: v for k, v in trimmed["business_address"].items() if v is not None}
                        if not trimmed["business_address"]:  # Remove if empty
                            del trimmed["business_address"]
                    import io
                    import pprint
                    buf = io.StringIO()
                    pprint.pprint(trimmed, stream=buf, compact=True, width=120)
                    sec_info_str = f"\n\n# Key SEC EDGAR Company Info (trimmed)\n{buf.getvalue()}\n"
            except Exception as e:
                sec_info_str = f"\n[Could not load sec_edgar_company_info.json: {e}]\n"
    # Prepend the company info and trimmed SEC info to the user prompt
    full_prompt = f"{company_info_str}{sec_info_str}\n{prompt}"
    # Save the prompt to a file for traceability if ticker is provided
    if ticker:
        try:
            from altman_zscore.utils.paths import get_output_dir
            prompt_path = get_output_dir("llm_commentary_prompt.txt", ticker=ticker)
            os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
            with open(prompt_path, "w", encoding="utf-8") as pf:
                pf.write(full_prompt)
        except Exception as e:
            print(f"[WARN] Could not save LLM prompt to file for ticker {ticker}: {e}")
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": full_prompt}]
    response = client.chat_completion(messages, temperature=0.2, max_tokens=4096)
    try:
        content = response["choices"][0]["message"]["content"]
        # Remove code block markers if present
        if content.strip().startswith("```"):
            content = content.strip().split("\n", 1)[-1]
            if content.endswith("```"):
                content = content.rsplit("```", 1)[0]
        return content.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to parse LLM commentary: {e}\nResponse: {response}")
