import os
import requests

class AzureOpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        self.model = os.getenv("AZURE_OPENAI_MODEL")
        if not all([self.api_key, self.endpoint, self.deployment]):
            raise ValueError("Missing Azure OpenAI configuration in environment variables.")

    def chat_completion(self, messages, temperature=0.0, max_tokens=2500):
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
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
        """
        # Centralized synonyms for each canonical field
        FIELD_SYNONYMS = {
            "total_assets": ["Total Assets", "Assets", "TotalAssets", "Assets Total"],
            "current_assets": ["Current Assets", "Assets Current", "CurrentAssets"],
            "current_liabilities": ["Current Liabilities", "Liabilities Current", "CurrentLiabilities"],
            "retained_earnings": ["Retained Earnings", "Earnings Retained", "RetainedEarningsAccumulatedDeficit"],
            "ebit": ["EBIT", "Earnings Before Interest and Taxes", "Operating Income", "Income From Operations"],
            "market_value_equity": ["Market Value Equity", "Market Capitalization", "Market Cap", "MarketValueOfEquity"],
            "book_value_equity": ["Book Value Equity", "Total Equity", "Shareholders Equity", "Stockholders Equity", "Equity"],
            "total_liabilities": ["Total Liabilities", "Liabilities", "TotalLiabilities"],
            "sales": ["Total Revenue", "Revenue", "Sales Revenue Net", "Operating Revenue", "Sales"],
        }
        # --- Prompt Ingestion for Field Mapping ---
        # Try both new (src/prompts/) and legacy (src/altman_zscore/prompts/) locations for backward compatibility
        prompt_path_new = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "prompts", "prompt_field_mapping.md")
        prompt_path_legacy = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "prompt_field_mapping.md")
        if os.path.exists(prompt_path_new):
            prompt_path = prompt_path_new
        elif os.path.exists(prompt_path_legacy):
            prompt_path = prompt_path_legacy
        else:
            raise FileNotFoundError(f"Could not find prompt_field_mapping.md in either src/prompts/ or src/altman_zscore/prompts/. Checked: {prompt_path_new}, {prompt_path_legacy}")
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
            {"role": "user", "content": user_prompt}
        ]
        response = self.chat_completion(messages, temperature=0.0, max_tokens=2500)
        # Try to extract the mapping from the response
        try:
            content = response["choices"][0]["message"]["content"]
            import json
            # Strip code block markers if present
            if content.strip().startswith("```"):
                content = content.strip().split("\n", 1)[-1]
                if content.endswith("```"):
                    content = content.rsplit("```", 1)[0]
            mapping = json.loads(content)
            # --- CODE-LEVEL FALLBACK FOR ALL FIELDS ---
            for canonical in canonical_fields:
                # User-supplied override takes precedence
                if mapping_overrides and canonical in mapping_overrides:
                    override_field = mapping_overrides[canonical]
                    if override_field in raw_fields:
                        mapping[canonical] = {"FoundField": override_field, "Value": None}
                        continue
                # If missing/null, try synonyms
                if canonical not in mapping or mapping[canonical] is None or mapping[canonical].get("FoundField") in [None, "null"]:
                    for synonym in FIELD_SYNONYMS.get(canonical, []):
                        if synonym in raw_fields:
                            mapping[canonical] = {"FoundField": synonym, "Value": None}
                            break
            return mapping
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI field mapping: {e}\nResponse: {response}")

def get_llm_qualitative_commentary(prompt: str) -> str:
    """
    Generate a qualitative commentary for the Altman Z-Score report using Azure OpenAI LLM.
    Args:
        prompt (str): The full prompt to send to the LLM (should include context and instructions).
    Returns:
        str: The LLM-generated commentary as plain text.
    """
    client = AzureOpenAIClient()
    # Try both new (src/prompts/) and legacy (src/altman_zscore/prompts/) locations for backward compatibility
    prompt_path_new = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "prompts", "prompt_fin_analysis.md")
    prompt_path_legacy = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "prompt_fin_analysis.md")
    if os.path.exists(prompt_path_new):
        prompt_path = prompt_path_new
    elif os.path.exists(prompt_path_legacy):
        prompt_path = prompt_path_legacy
    else:
        raise FileNotFoundError(f"Could not find prompt_fin_analysis.md in either src/prompts/ or src/altman_zscore/prompts/. Checked: {prompt_path_new}, {prompt_path_legacy}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    response = client.chat_completion(messages, temperature=0.2, max_tokens=2500)
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
