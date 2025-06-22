# Prompts Module for Altman Z-Score Analysis

"""
LLM Prompts for AI-Enhanced Financial Analysis

This module contains structured prompts for AI analysis tasks in the modern pipeline:
- Financial analysis report generation with AI insights
- Data reconciliation and validation
- Executive summary and strategic recommendations

These prompts are used by the LLM client (altman_zscore.layers.data_fetch.llm_client)
for generating AI-enhanced insights in the output generation layer.

Note: Field mapping prompts have been removed as the modern pipeline uses 
FMP pre-calculated ratios, eliminating the need for complex field mapping.
"""

from pathlib import Path

# Get the directory containing this file
PROMPTS_DIR = Path(__file__).parent

def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the prompts directory.
    
    Args:
        prompt_name: Name of the prompt file (without .md extension)
        
    Returns:
        The prompt content as a string
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    return prompt_file.read_text(encoding='utf-8')

def get_available_prompts() -> list[str]:
    """
    Get a list of available prompt templates.
    
    Returns:
        List of prompt names (without .md extension)
    """
    return [f.stem for f in PROMPTS_DIR.glob("*.md")]

# Available prompt templates
FINANCIAL_ANALYSIS_PROMPT = "prompt_fin_analysis"
