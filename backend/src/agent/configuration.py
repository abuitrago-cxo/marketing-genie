import os
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict

from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

# Import the new LLM manager
from .llm_manager import llm_manager, LLMProvider, LLMConfig


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="gemini-2.0-flash",
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    reflection_model: str = Field(
        default="gemini-2.5-flash-preview-04-17",
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    answer_model: str = Field(
        default="gemini-2.5-pro-preview-05-06",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)


def get_model(model_name: str, provider: Optional[str] = None) -> BaseChatModel:
    """
    Get a language model instance.

    Args:
        model_name: Name of the model to use
        provider: Optional provider ID to use specific provider

    Returns:
        BaseChatModel instance
    """
    if provider:
        # Use specific provider
        if provider in llm_manager.providers:
            return llm_manager.providers[provider].client
        else:
            raise ValueError(f"Provider {provider} not available")
    else:
        # Use primary provider or fallback
        if llm_manager.primary_provider:
            return llm_manager.providers[llm_manager.primary_provider].client
        else:
            # Fallback to original Gemini implementation
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")

            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.7,
            )


def configure_llm_providers() -> Dict[str, Any]:
    """
    Configure and initialize LLM providers based on available API keys.

    Returns:
        Dict with configuration status
    """
    config_status = {
        "providers_configured": [],
        "providers_failed": [],
        "primary_provider": None
    }

    # Try to configure Google Gemini
    if os.getenv("GEMINI_API_KEY"):
        try:
            gemini_config = LLMConfig(
                provider=LLMProvider.GOOGLE_GEMINI,
                model_name="gemini-2.0-flash",
                temperature=0.7
            )
            provider_id = llm_manager.add_provider(gemini_config)
            if provider_id:
                config_status["providers_configured"].append("google_gemini")
                if not config_status["primary_provider"]:
                    config_status["primary_provider"] = provider_id
                    llm_manager.set_primary_provider(provider_id)
        except Exception as e:
            config_status["providers_failed"].append(f"google_gemini: {str(e)}")

    # Try to configure Anthropic Claude
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            claude_config = LLMConfig(
                provider=LLMProvider.ANTHROPIC_CLAUDE,
                model_name="claude-3-5-sonnet-20241022",
                temperature=0.7
            )
            provider_id = llm_manager.add_provider(claude_config)
            if provider_id:
                config_status["providers_configured"].append("anthropic_claude")
                if not config_status["primary_provider"]:
                    config_status["primary_provider"] = provider_id
                    llm_manager.set_primary_provider(provider_id)
        except Exception as e:
            config_status["providers_failed"].append(f"anthropic_claude: {str(e)}")

    # Try to configure OpenAI GPT
    if os.getenv("OPENAI_API_KEY"):
        try:
            openai_config = LLMConfig(
                provider=LLMProvider.OPENAI_GPT,
                model_name="gpt-4o",
                temperature=0.7
            )
            provider_id = llm_manager.add_provider(openai_config)
            if provider_id:
                config_status["providers_configured"].append("openai_gpt")
                if not config_status["primary_provider"]:
                    config_status["primary_provider"] = provider_id
                    llm_manager.set_primary_provider(provider_id)
        except Exception as e:
            config_status["providers_failed"].append(f"openai_gpt: {str(e)}")

    # Set up fallback providers
    available_providers = llm_manager.get_available_providers()
    if len(available_providers) > 1:
        # Set all providers except primary as fallbacks
        primary = config_status["primary_provider"]
        fallbacks = [p for p in available_providers if p != primary]
        llm_manager.set_fallback_providers(fallbacks)

    return config_status


def get_llm_status() -> Dict[str, Any]:
    """Get current status of all LLM providers"""
    return {
        "available_providers": llm_manager.get_available_providers(),
        "primary_provider": llm_manager.primary_provider,
        "fallback_providers": llm_manager.fallback_providers,
        "provider_details": {
            pid: llm_manager.get_provider_info(pid)
            for pid in llm_manager.get_available_providers()
        }
    }
