import pytest
from unittest.mock import patch, MagicMock

# Import the node function and relevant classes
from agent.graph import generate_query
from agent.configuration import Configuration, LLMProvider
from agent.tools_and_schemas import SearchQueryList # For structured_llm mock

# Mock initial state for the node
mock_initial_state = {
    "messages": [{"role": "user", "content": "Test question"}],
    "initial_search_query_count": None, # To let the default from config apply
}

# Mock RunnableConfig (though Configuration.from_runnable_config will be patched)
mock_runnable_config = {"configurable": {}}


@patch("agent.graph.ChatGoogleGenerativeAI")
@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_gemini_provider(mock_from_config, mock_chat_google):
    """Test generate_query uses ChatGoogleGenerativeAI when provider is GEMINI."""
    # Setup mock Configuration returned by from_runnable_config
    mock_config_instance = Configuration(
        llm_provider=LLMProvider.GEMINI,
        query_generator_model="gemini-test-model",
        # other fields will use defaults from Configuration class
    )
    mock_from_config.return_value = mock_config_instance

    # Mock the structured_llm chain
    mock_structured_llm = MagicMock()
    mock_chat_google.return_value.with_structured_output.return_value = mock_structured_llm
    mock_structured_llm.invoke.return_value = SearchQueryList(query=["Test query 1"])

    # Call the node
    result_state = generate_query(mock_initial_state.copy(), mock_runnable_config)

    # Assertions
    mock_from_config.assert_called_once_with(mock_runnable_config)
    mock_chat_google.assert_called_once_with(
        model="gemini-test-model",
        temperature=1.0,
        max_retries=2,
        api_key=None, # os.getenv("GEMINI_API_KEY") would be used, but it's None in tests unless set
    )
    mock_chat_google.return_value.with_structured_output.assert_called_once_with(SearchQueryList)
    mock_structured_llm.invoke.assert_called_once()
    assert result_state["query_list"] == ["Test query 1"]


@patch("agent.graph.ChatOllama")
@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_ollama_provider(mock_from_config, mock_chat_ollama):
    """Test generate_query uses ChatOllama when provider is OLLAMA."""
    mock_config_instance = Configuration(
        llm_provider=LLMProvider.OLLAMA,
        ollama_base_url="http://ollama:11434",
        ollama_model_name="ollama-test-model",
    )
    mock_from_config.return_value = mock_config_instance

    mock_structured_llm = MagicMock()
    mock_chat_ollama.return_value.with_structured_output.return_value = mock_structured_llm
    mock_structured_llm.invoke.return_value = SearchQueryList(query=["Ollama query"])

    result_state = generate_query(mock_initial_state.copy(), mock_runnable_config)

    mock_chat_ollama.assert_called_once_with(
        base_url="http://ollama:11434",
        model="ollama-test-model",
        temperature=1.0,
    )
    mock_chat_ollama.return_value.with_structured_output.assert_called_once_with(SearchQueryList)
    assert result_state["query_list"] == ["Ollama query"]


@patch("agent.graph.ChatOpenAI")
@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_lmstudio_provider(mock_from_config, mock_chat_openai):
    """Test generate_query uses ChatOpenAI when provider is LMSTUDIO."""
    mock_config_instance = Configuration(
        llm_provider=LLMProvider.LMSTUDIO,
        lmstudio_base_url="http://lmstudio:1234/v1",
        lmstudio_model_name="lmstudio-test-model",
    )
    mock_from_config.return_value = mock_config_instance

    mock_structured_llm = MagicMock()
    mock_chat_openai.return_value.with_structured_output.return_value = mock_structured_llm
    mock_structured_llm.invoke.return_value = SearchQueryList(query=["LMStudio query"])

    result_state = generate_query(mock_initial_state.copy(), mock_runnable_config)

    mock_chat_openai.assert_called_once_with(
        base_url="http://lmstudio:1234/v1",
        model_name="lmstudio-test-model",
        api_key="not-needed",
        temperature=1.0,
        max_retries=2,
    )
    mock_chat_openai.return_value.with_structured_output.assert_called_once_with(SearchQueryList)
    assert result_state["query_list"] == ["LMStudio query"]


@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_ollama_missing_url_raises_error(mock_from_config):
    """Test ValueError is raised if Ollama URL is missing."""
    mock_config_instance = Configuration(
        llm_provider=LLMProvider.OLLAMA,
        ollama_model_name="ollama-model", # URL is missing
    )
    mock_from_config.return_value = mock_config_instance

    with pytest.raises(ValueError, match="Ollama base URL or model name not configured"):
        generate_query(mock_initial_state.copy(), mock_runnable_config)


@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_ollama_missing_model_raises_error(mock_from_config):
    """Test ValueError is raised if Ollama model name is missing."""
    mock_config_instance = Configuration(
        llm_provider=LLMProvider.OLLAMA,
        ollama_base_url="http://ollama:11434", # Model name is missing
    )
    mock_from_config.return_value = mock_config_instance

    with pytest.raises(ValueError, match="Ollama base URL or model name not configured"):
        generate_query(mock_initial_state.copy(), mock_runnable_config)


@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_lmstudio_missing_url_raises_error(mock_from_config):
    """Test ValueError is raised if LMStudio URL is missing."""
    mock_config_instance = Configuration(
        llm_provider=LLMProvider.LMSTUDIO,
        lmstudio_model_name="lm-model", # URL is missing
    )
    mock_from_config.return_value = mock_config_instance

    with pytest.raises(ValueError, match="LM Studio base URL or model name not configured"):
        generate_query(mock_initial_state.copy(), mock_runnable_config)

@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_lmstudio_missing_model_raises_error(mock_from_config):
    """Test ValueError is raised if LMStudio model name is missing."""
    mock_config_instance = Configuration(
        llm_provider=LLMProvider.LMSTUDIO,
        lmstudio_base_url="http://lmstudio:1234/v1", # Model name is missing
    )
    mock_from_config.return_value = mock_config_instance

    with pytest.raises(ValueError, match="LM Studio base URL or model name not configured"):
        generate_query(mock_initial_state.copy(), mock_runnable_config)

@patch("agent.graph.Configuration.from_runnable_config")
def test_generate_query_unsupported_provider_raises_error(mock_from_config):
    """Test ValueError is raised for an unsupported LLM provider."""
    mock_config_instance = MagicMock(spec=Configuration)
    mock_config_instance.llm_provider = "unsupported_provider"
    # To make Pydantic validation pass for the mock, if direct instantiation was used.
    # But since we are mocking from_runnable_config's return, this is simpler.
    mock_from_config.return_value = mock_config_instance

    # Patching __str__ on the mock_config_instance.llm_provider if it's a MagicMock itself
    if isinstance(mock_config_instance.llm_provider, MagicMock):
      mock_config_instance.llm_provider.__str__.return_value = "unsupported_provider"


    with pytest.raises(ValueError, match="Unsupported LLM provider: unsupported_provider"):
        generate_query(mock_initial_state.copy(), mock_runnable_config)

# To run these tests, you would typically use `pytest` in the terminal
# Ensure that pytest and pytest-mock are installed in your environment.
# These tests assume that os.getenv("GEMINI_API_KEY") returns None during tests.
# If it's set globally, the Gemini test might behave differently regarding api_key.
# The fixture in test_configuration.py clears common env vars, which is good practice.
# For test_graph.py, if GEMINI_API_KEY is needed for some setup, it should be mocked too.
# Here, api_key=None in ChatGoogleGenerativeAI call is expected if env var is not set.
