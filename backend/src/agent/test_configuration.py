import os
import pytest
from unittest.mock import patch

from agent.configuration import Configuration, LLMProvider


@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear relevant environment variables before each test."""
    vars_to_clear = [
        "LLM_PROVIDER",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL_NAME",
        "LMSTUDIO_BASE_URL",
        "LMSTUDIO_MODEL_NAME",
        "QUERY_GENERATOR_MODEL", # Clear others to ensure defaults are tested
        "REFLECTION_MODEL",
        "ANSWER_MODEL",
        "NUMBER_OF_INITIAL_QUERIES",
        "MAX_RESEARCH_LOOPS",
    ]
    original_values = {var: os.environ.get(var) for var in vars_to_clear}
    for var in vars_to_clear:
        if os.environ.get(var) is not None:
            del os.environ[var]
    yield
    for var, val in original_values.items():
        if val is not None:
            os.environ[var] = val
        elif os.environ.get(var) is not None: # if it was set during test but not before
            del os.environ[var]


def test_from_runnable_config_defaults():
    """Test that default values are loaded when no env vars are set."""
    config = Configuration.from_runnable_config()

    assert config.llm_provider == LLMProvider.GEMINI
    assert config.ollama_base_url is None
    assert config.ollama_model_name is None
    assert config.lmstudio_base_url is None
    assert config.lmstudio_model_name is None
    assert config.query_generator_model == "gemini-2.0-flash" # Default from class
    assert config.number_of_initial_queries == 3 # Default from class


@patch.dict(os.environ, {
    "LLM_PROVIDER": "ollama",
    "OLLAMA_BASE_URL": "http://ollama:11434",
    "OLLAMA_MODEL_NAME": "test-ollama-model",
})
def test_from_runnable_config_ollama_provider():
    """Test loading Ollama provider configuration from environment variables."""
    config = Configuration.from_runnable_config()

    assert config.llm_provider == LLMProvider.OLLAMA
    assert config.ollama_base_url == "http://ollama:11434"
    assert config.ollama_model_name == "test-ollama-model"
    assert config.lmstudio_base_url is None
    assert config.lmstudio_model_name is None


@patch.dict(os.environ, {
    "LLM_PROVIDER": "lmstudio",
    "LMSTUDIO_BASE_URL": "http://lmstudio:1234/v1",
    "LMSTUDIO_MODEL_NAME": "test-lmstudio-model",
})
def test_from_runnable_config_lmstudio_provider():
    """Test loading LM Studio provider configuration from environment variables."""
    config = Configuration.from_runnable_config()

    assert config.llm_provider == LLMProvider.LMSTUDIO
    assert config.lmstudio_base_url == "http://lmstudio:1234/v1"
    assert config.lmstudio_model_name == "test-lmstudio-model"
    assert config.ollama_base_url is None
    assert config.ollama_model_name is None


@patch.dict(os.environ, {"LLM_PROVIDER": "invalid_provider"})
def test_from_runnable_config_invalid_provider():
    """Test handling of an invalid LLM provider value."""
    # Pydantic should raise a ValidationError
    with pytest.raises(ValueError): # Adjusted to ValueError based on Pydantic v2 behavior for Enums
        Configuration.from_runnable_config()


def test_from_runnable_config_gemini_defaults_explicit():
    """Test that Gemini is default even if other LLM vars are partially set."""
    # GEMINI is default, so no need to set LLM_PROVIDER
    # Test that ollama/lmstudio fields are not populated if provider is gemini
    with patch.dict(os.environ, {
        "OLLAMA_BASE_URL": "http://shouldnotbeused:11434",
        "LMSTUDIO_MODEL_NAME": "shouldnotbeusedeither",
    }):
        config = Configuration.from_runnable_config()
        assert config.llm_provider == LLMProvider.GEMINI
        assert config.ollama_base_url == "http://shouldnotbeused:11434" # Field will be set if env var is present
        assert config.ollama_model_name is None
        assert config.lmstudio_base_url is None
        assert config.lmstudio_model_name == "shouldnotbeusedeither" # Field will be set


def test_from_runnable_config_partial_ollama_still_loads_what_is_there():
    """Test that if provider is ollama, but model name is missing, base_url is still loaded."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "ollama",
        "OLLAMA_BASE_URL": "http://partialollama:11434",
    }):
        config = Configuration.from_runnable_config()
        assert config.llm_provider == LLMProvider.OLLAMA
        assert config.ollama_base_url == "http://partialollama:11434"
        assert config.ollama_model_name is None # Defaults to None


def test_runnable_config_override():
    """Test that runnable config values override environment variables."""
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "gemini",
        "OLLAMA_BASE_URL": "http://env_ollama:11434",
        "OLLAMA_MODEL_NAME": "env_ollama_model",
    }):
        runnable_config_values = {
            "llm_provider": "ollama",
            "ollama_base_url": "http://runnable_ollama:11434",
            "ollama_model_name": "runnable_ollama_model",
            "lmstudio_base_url": "http://runnable_lmstudio:1234/v1",
        }
        config_input = {"configurable": runnable_config_values}

        config = Configuration.from_runnable_config(config_input)

        assert config.llm_provider == LLMProvider.OLLAMA
        assert config.ollama_base_url == "http://runnable_ollama:11434"
        assert config.ollama_model_name == "runnable_ollama_model"
        assert config.lmstudio_base_url == "http://runnable_lmstudio:1234/v1"
        assert config.lmstudio_model_name is None # Not in runnable_config_values, not in env
