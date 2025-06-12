import os
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class LLMProvider(str, Enum):
    """The available LLM providers."""

    GEMINI = "gemini"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"


class Configuration(BaseModel):
    """The configuration for the agent."""

    gemini_api_key: Optional[str] = Field(
        default=None,
        metadata={"description": "The API key for Google Gemini services."},
    )

    llm_provider: LLMProvider = Field(
        default=LLMProvider.GEMINI,
        metadata={"description": "The LLM provider to use."},
    )

    ollama_base_url: Optional[str] = Field(
        default=None,
        metadata={"description": "The base URL for the Ollama API."},
    )

    ollama_model_name: Optional[str] = Field(
        default=None,
        metadata={"description": "The model name to use with Ollama."},
    )

    lmstudio_base_url: Optional[str] = Field(
        default=None,
        metadata={"description": "The base URL for the LM Studio API."},
    )

    lmstudio_model_name: Optional[str] = Field(
        default=None,
        metadata={"description": "The model name to use with LM Studio."},
    )

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

        raw_values: dict[str, Any] = {}
        for name, field_info in cls.model_fields.items():
            # 1. Try to get value from 'configurable' (e.g., frontend request)
            configurable_value = configurable.get(name)

            if configurable_value is not None:
                raw_values[name] = configurable_value
            else:
                # 2. If not in 'configurable' or None, try to get from environment variables
                #    The environment variable name is assumed to be the uppercase field name.
                env_value = os.environ.get(name.upper())
                if env_value is not None:
                    raw_values[name] = env_value
                # 3. If neither 'configurable' nor environment variable is set (or both are None),
                #    the key is not added to raw_values. Pydantic will then use the
                #    `default` value specified in `Field()` when `cls(**raw_values)` is called.

        # Pydantic will handle type conversion for basic types.
        # If a field is not present in raw_values, Pydantic uses its default.
        return cls(**raw_values)
