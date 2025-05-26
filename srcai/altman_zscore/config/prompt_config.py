"""
Configuration loader for OpenAI prompt templates.

This module provides utilities for loading and managing prompt templates
used by the AI-powered parsing functions for financial data.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptConfig:
    """
    Manager for OpenAI prompt templates.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize prompt configuration manager.
        
        Args:
            config_dir: Directory containing prompt templates (defaults to project's config directory)
        """
        # Default to the project's config directory if not provided
        if not config_dir:
            # Get the module directory
            module_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_dir = os.path.join(module_dir, "prompts")
        else:
            self.config_dir = config_dir
            
        # Cache for loaded templates
        self._prompt_cache: Dict[str, str] = {}
        
    def get_prompt(self, name: str) -> str:
        """
        Get a prompt template by name.
        
        Args:
            name: Name of the prompt template (without extension)
            
        Returns:
            Prompt template string
            
        Raises:
            FileNotFoundError: If prompt template file does not exist
        """
        if name in self._prompt_cache:
            return self._prompt_cache[name]
            
        # Try to load the prompt from file
        file_path = os.path.join(self.config_dir, f"{name}.txt")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt template not found: {file_path}")
            
        with open(file_path, "r") as f:
            prompt = f.read()
            
        # Cache the prompt for future use
        self._prompt_cache[name] = prompt
        return prompt
        
    def get_all_prompts(self) -> Dict[str, str]:
        """
        Get all available prompt templates.
        
        Returns:
            Dictionary of prompt templates keyed by name (without extension)
        """
        prompts = {}
        
        # List all .txt files in the prompts directory
        prompt_files = Path(self.config_dir).glob("*.txt")
        
        for file_path in prompt_files:
            name = file_path.stem
            with open(file_path, "r") as f:
                prompts[name] = f.read()
                
        # Update cache
        self._prompt_cache.update(prompts)
        return prompts
        
    def add_prompt(self, name: str, prompt: str) -> None:
        """
        Add or update a prompt template.
        
        Args:
            name: Name of the prompt template (without extension)
            prompt: Prompt template string
        """
        file_path = os.path.join(self.config_dir, f"{name}.txt")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w") as f:
            f.write(prompt)
            
        # Update cache
        self._prompt_cache[name] = prompt