#!/usr/bin/env python3
"""
Bootstrap file for AI-powered processing in Altman Z-Score project.

This module provides a command-line interface to initialize and manage
the AI-powered financial data parsing pipeline, with options to toggle
between AI and traditional parsing approaches.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional, Union, List
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ai_bootstrap")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed. Environment variables should be set manually.")

def check_openai_credentials() -> bool:
    """
    Check if OpenAI credentials are properly configured.
    
    Returns:
        True if credentials are valid, False otherwise
    """
    # Check for Azure OpenAI credentials
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if azure_key and azure_endpoint:
        logger.info("Azure OpenAI credentials found.")
        return True
        
    # Check for standard OpenAI credentials as fallback
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        logger.info("OpenAI credentials found.")
        return True
        
    logger.warning("No OpenAI credentials found. AI features will not work.")
    return False

def initialize_ai_pipeline(force: bool = False) -> bool:
    """
    Initialize the AI pipeline by checking prerequisites
    and setting up necessary configurations.
    
    Args:
        force: Force initialization even if prerequisites are missing
        
    Returns:
        True if initialization was successful, False otherwise
    """
    # Check if OpenAI is installed
    try:
        import openai
        logger.info("OpenAI SDK installed.")
    except ImportError:
        logger.error("OpenAI SDK not installed. Run 'pip install openai'.")
        if not force:
            return False
            
    # Check OpenAI credentials
    credentials_valid = check_openai_credentials()
    if not credentials_valid and not force:
        return False
        
    # Check for prompt templates
    srcai_path = os.path.join(os.path.dirname(__file__), "srcai")
    prompt_dir = os.path.join(srcai_path, "altman_zscore", "config", "prompts")
    
    if not os.path.exists(prompt_dir):
        logger.error(f"Prompt directory not found: {prompt_dir}")
        if not force:
            return False
    else:
        prompt_files = list(Path(prompt_dir).glob("*.txt"))
        if not prompt_files:
            logger.warning("No prompt templates found.")
        else:
            logger.info(f"Found {len(prompt_files)} prompt templates.")
            
    # Create config file indicating AI pipeline is ready
    config_file = os.path.join(os.path.dirname(__file__), ".ai_config.json")
    with open(config_file, "w") as f:
        json.dump({
            "initialized": True,
            "timestamp": str(datetime.now()),
            "credentials_valid": credentials_valid,
            "api_type": "azure" if os.getenv("AZURE_OPENAI_API_KEY") else "openai",
            "prompt_templates": [os.path.basename(str(p)) for p in prompt_files] if 'prompt_files' in locals() else []
        }, f, indent=2)
    
    logger.info("AI pipeline initialized successfully.")
    return True

def toggle_ai_pipeline(enable: bool = True) -> None:
    """
    Toggle the AI pipeline on or off.
    
    Args:
        enable: True to enable AI pipeline, False to disable
    """
    config_file = os.path.join(os.path.dirname(__file__), ".ai_config.json")
    
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
    else:
        config = {}
        
    config["enabled"] = enable
    config["last_updated"] = str(datetime.now())
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
        
    status = "enabled" if enable else "disabled"
    logger.info(f"AI pipeline {status}.")

def is_ai_pipeline_enabled() -> bool:
    """
    Check if the AI pipeline is enabled.
    
    Returns:
        True if AI pipeline is enabled, False otherwise
    """
    config_file = os.path.join(os.path.dirname(__file__), ".ai_config.json")
    
    if not os.path.exists(config_file):
        return False
        
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config.get("enabled", False)
    except json.JSONDecodeError:
        return False

def run_test() -> None:
    """
    Run basic tests for the AI pipeline.
    """
    
    logger.info("Running AI pipeline test...")
    
    if not check_openai_credentials():
        logger.error("OpenAI credentials not found. Skipping test.")
        return
        
    try:
        # Import AI clients
        from srcai.altman_zscore.api.openai_client import OpenAIClient
        from srcai.altman_zscore.api.sec_ai_client import SECAIClient
        from srcai.altman_zscore.api.yahoo_ai_client import YahooFinanceAIClient
        from srcai.altman_zscore.config.prompt_config import PromptConfig
        
        logger.info("AI modules imported successfully.")
        
        # Test OpenAI client
        openai_client = OpenAIClient()
        logger.info("OpenAI client initialized.")
        
        # Test prompt config
        prompt_config = PromptConfig()
        try:
            sec_prompt = prompt_config.get_prompt("sec_edgar_parser")
            yahoo_prompt = prompt_config.get_prompt("yahoo_finance_parser")
            logger.info("Prompt templates loaded successfully.")
        except FileNotFoundError as e:
            logger.error(f"Failed to load prompt templates: {str(e)}")
            return
        
        # Test SEC AI client
        sec_client = SECAIClient(openai_client=openai_client, prompt_config=prompt_config)
        logger.info("SEC AI client initialized.")
        
        # Test Yahoo Finance AI client
        yahoo_client = YahooFinanceAIClient(openai_client=openai_client, prompt_config=prompt_config)
        logger.info("Yahoo Finance AI client initialized.")
        
        logger.info("All AI components initialized successfully. AI pipeline is ready.")
        
    except ImportError as e:
        logger.error(f"Failed to import AI modules: {str(e)}")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

def main():
    """
    Main entry point for AI bootstrap CLI.
    """
    parser = argparse.ArgumentParser(
        description="Bootstrap AI-powered processing for Altman Z-Score project."
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize AI pipeline"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force initialization even if prerequisites are missing"
    )
    
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Enable AI pipeline"
    )
    
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable AI pipeline"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Check AI pipeline status"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test AI pipeline"
    )
    
    args = parser.parse_args()
    
    if args.init:
        success = initialize_ai_pipeline(force=args.force)
        if success and args.enable:
            toggle_ai_pipeline(enable=True)
        sys.exit(0 if success else 1)
        
    if args.enable and args.disable:
        logger.error("Cannot both enable and disable AI pipeline.")
        sys.exit(1)
        
    if args.enable:
        toggle_ai_pipeline(enable=True)
        
    if args.disable:
        toggle_ai_pipeline(enable=False)
        
    if args.status:
        enabled = is_ai_pipeline_enabled()
        status = "enabled" if enabled else "disabled"
        print(f"AI pipeline is {status}.")
        
    if args.test:
        run_test()
        
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        
if __name__ == "__main__":
    main()