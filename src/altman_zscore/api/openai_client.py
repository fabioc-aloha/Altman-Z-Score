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

    def chat_completion(self, messages, temperature=0.0, max_tokens=512):
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

    def suggest_field_mapping(self, raw_fields, canonical_fields, sample_values=None):
        """
        Use Azure OpenAI to suggest a mapping from canonical fields to raw fields.
        Args:
            raw_fields (list[str]): List of raw field names (from XBRL/EDGAR)
            canonical_fields (list[str]): List of canonical fields (e.g., total_assets, retained_earnings)
            sample_values (dict, optional): Optional dict of {raw_field: value} for context
        Returns:
            dict: {canonical_field: {"FoundField": matched_raw_field, "Value": value}}
        """
        system_prompt = (
            "You are a financial data expert. Given a list of raw field names from an SEC XBRL filing, "
            "map each canonical Altman Z-Score field to the most likely raw field name. "
            "If no good match exists, return null for that field. "
            "For the canonical field 'sales', you must always map it to the best available revenue field (such as 'Total Revenue', 'Revenue', 'Sales Revenue Net', or 'Operating Revenue') if any of these are present in the raw fields. "
            "Never leave 'sales' as null if any revenue field is present. If multiple revenue fields are present, prefer 'Total Revenue', then 'Revenue', then 'Sales Revenue Net', then 'Operating Revenue'. "
            "Always return a JSON object where the keys are the canonical field names (e.g., 'sales'), and the values are objects with two keys: 'FoundField' (the best-matching raw field name or null) and 'Value' (the value for that field, or null). "
            "Even if the best match for 'sales' is 'Total Revenue', the output key must still be 'sales', with the value set to {\"FoundField\": \"Total Revenue\", \"Value\": <value>}. "
            "The output must always include all canonical field names as keys, even if the matched raw field is different. "
        )
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
        response = self.chat_completion(messages, temperature=0.0, max_tokens=512)
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
            # --- CODE-LEVEL FALLBACK FOR 'sales' ---
            if ("sales" not in mapping or mapping["sales"] is None or mapping["sales"].get("FoundField") in [None, "null"]):
                # Fallback: pick the best available revenue field
                revenue_priority = ["Total Revenue", "Revenue", "Sales Revenue Net", "Operating Revenue"]
                for field in revenue_priority:
                    if field in raw_fields:
                        mapping["sales"] = {"FoundField": field, "Value": None}
                        break
            return mapping
        except Exception as e:
            raise RuntimeError(f"Failed to parse AI field mapping: {e}\nResponse: {response}")
