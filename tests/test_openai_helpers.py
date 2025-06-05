import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from altman_zscore.api import openai_helpers

def test_strip_code_block_markers():
    code = """```json\n{"foo": 1}\n```"""
    assert openai_helpers.strip_code_block_markers(code) == '{"foo": 1}'
    code2 = '{"foo": 2}'
    assert openai_helpers.strip_code_block_markers(code2) == '{"foo": 2}'

def test_parse_llm_json_response():
    code = """```json\n{"bar": 3}\n```"""
    result = openai_helpers.parse_llm_json_response(code)
    assert result == {"bar": 3}

def test_resolve_prompt_path_exists(tmp_path, monkeypatch):
    # Create a fake prompt file in a temp dir that matches the helper's search logic
    prompt_name = "prompt_test.md"
    # Simulate the src/prompts/ directory
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_path = prompts_dir / prompt_name
    prompt_path.write_text("test prompt")
    # Patch os.path.exists to recognize our test file
    orig_exists = openai_helpers.os.path.exists
    def fake_exists(p):
        return str(prompt_path) in p or orig_exists(p)
    monkeypatch.setattr(openai_helpers.os.path, "exists", fake_exists)
    # Patch the helper to look in our temp dir
    monkeypatch.setattr(openai_helpers.os.path, "join", lambda *args: str(prompt_path) if args[-1] == prompt_name else os.path.join(*args))
    assert openai_helpers.resolve_prompt_path(prompt_name) == str(prompt_path)

def test_load_prompt_file(tmp_path):
    prompt_path = tmp_path / "prompt_test.md"
    prompt_path.write_text("hello world")
    assert openai_helpers.load_prompt_file(str(prompt_path)) == "hello world"
