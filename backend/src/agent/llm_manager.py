"""
Multi-LLM Provider Manager
Based on II-Agent patterns for provider abstraction and management.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass
import logging
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_anthropic import ChatAnthropic  # Removed - using only Gemini
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    GOOGLE_GEMINI = "google_gemini"
    # ANTHROPIC_CLAUDE = "anthropic_claude"  # TODO: Re-enable when langchain_anthropic is available
    OPENAI_GPT = "openai_gpt"
    VERTEX_AI = "vertex_ai"
    LOCAL_OLLAMA = "local_ollama"

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7  # Default temperature for more creative and diverse responses
    max_tokens: Optional[int] = None
    max_retries: int = 2
    timeout: int = 60
    additional_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client: Optional[BaseChatModel] = None
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self) -> None:
        """Initialize the LLM client"""
        pass

    @abstractmethod
    def generate_response(
        self,
        messages: List[BaseMessage],
        **kwargs
    ) -> AIMessage:
        """Generate a response from the LLM"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available"""
        pass

    def get_token_count(self, text: str) -> int:
        """Estimate token count for the given text"""
        # Simple estimation - can be improved with actual tokenizers
        return len(text.split()) * 1.3  # Rough approximation

class GoogleGeminiProvider(BaseLLMProvider):
    """Google Gemini provider implementation"""

    def _initialize_client(self) -> None:
        try:
            api_key = self.config.api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found")

            self.client = ChatGoogleGenerativeAI(
                model=self.config.model_name,
                google_api_key=api_key,
                temperature=self.config.temperature,
                max_retries=self.config.max_retries,
                **self.config.additional_params
            )
            logger.info(f"Initialized Google Gemini client with model: {self.config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Google Gemini client: {e}")
            self.client = None

    def generate_response(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        if not self.client:
            raise RuntimeError("Google Gemini client not initialized")

        try:
            response = self.client.invoke(messages, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Google Gemini generation failed: {e}")
            raise

    def is_available(self) -> bool:
        return self.client is not None

# TODO: Re-enable when langchain_anthropic is available
# class AnthropicClaudeProvider(BaseLLMProvider):
#     """Anthropic Claude provider implementation"""
#
#     def _initialize_client(self) -> None:
#         try:
#             api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
#             if not api_key:
#                 raise ValueError("ANTHROPIC_API_KEY not found")
#
#             self.client = ChatAnthropic(
#                 model=self.config.model_name,
#                 anthropic_api_key=api_key,
#                 temperature=self.config.temperature,
#                 max_retries=self.config.max_retries,
#                 **self.config.additional_params
#             )
#             logger.info(f"Initialized Anthropic Claude client with model: {self.config.model_name}")
#         except Exception as e:
#             logger.error(f"Failed to initialize Anthropic Claude client: {e}")
#             self.client = None
#
#     def generate_response(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
#         if not self.client:
#             raise RuntimeError("Anthropic Claude client not initialized")
#
#         try:
#             response = self.client.invoke(messages, **kwargs)
#             return response
#         except Exception as e:
#             logger.error(f"Anthropic Claude generation failed: {e}")
#             raise
#
#     def is_available(self) -> bool:
#         return self.client is not None

class OpenAIGPTProvider(BaseLLMProvider):
    """OpenAI GPT provider implementation"""

    def _initialize_client(self) -> None:
        try:
            api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")

            self.client = ChatOpenAI(
                model=self.config.model_name,
                openai_api_key=api_key,
                temperature=self.config.temperature,
                max_retries=self.config.max_retries,
                **self.config.additional_params
            )
            logger.info(f"Initialized OpenAI GPT client with model: {self.config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI GPT client: {e}")
            self.client = None

    def generate_response(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        if not self.client:
            raise RuntimeError("OpenAI GPT client not initialized")

        try:
            response = self.client.invoke(messages, **kwargs)
            return response
        except Exception as e:
            logger.error(f"OpenAI GPT generation failed: {e}")
            raise

    def is_available(self) -> bool:
        return self.client is not None

class LLMManager:
    """
    Central manager for multiple LLM providers
    Inspired by II-Agent's provider management patterns
    """

    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.primary_provider: Optional[str] = None
        self.fallback_providers: List[str] = []
        self._load_default_providers()

    def _load_default_providers(self) -> None:
        """Load default provider configurations"""
        default_configs = [
            LLMConfig(
                provider=LLMProvider.GOOGLE_GEMINI,
                model_name="gemini-2.0-flash",
                temperature=0.7
            ),
            # TODO: Re-enable when langchain_anthropic is available
            # LLMConfig(
            #     provider=LLMProvider.ANTHROPIC_CLAUDE,
            #     model_name="claude-3-5-sonnet-20241022",
            #     temperature=0.7
            # ),
            LLMConfig(
                provider=LLMProvider.OPENAI_GPT,
                model_name="gpt-4o",
                temperature=0.7
            )
        ]

        for config in default_configs:
            self.add_provider(config)

    def add_provider(self, config: LLMConfig, provider_id: Optional[str] = None) -> str:
        """Add a new LLM provider"""
        if provider_id is None:
            provider_id = f"{config.provider.value}_{config.model_name}"

        try:
            if config.provider == LLMProvider.GOOGLE_GEMINI:
                provider = GoogleGeminiProvider(config)
            # TODO: Re-enable when langchain_anthropic is available
            # elif config.provider == LLMProvider.ANTHROPIC_CLAUDE:
            #     provider = AnthropicClaudeProvider(config)
            elif config.provider == LLMProvider.OPENAI_GPT:
                provider = OpenAIGPTProvider(config)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")

            if provider.is_available():
                self.providers[provider_id] = provider
                if self.primary_provider is None:
                    self.primary_provider = provider_id
                logger.info(f"Added provider: {provider_id}")
                return provider_id
            else:
                logger.warning(f"Provider {provider_id} is not available")
                return ""
        except Exception as e:
            logger.error(f"Failed to add provider {provider_id}: {e}")
            return ""

    def set_primary_provider(self, provider_id: str) -> bool:
        """Set the primary provider"""
        if provider_id in self.providers:
            self.primary_provider = provider_id
            logger.info(f"Set primary provider to: {provider_id}")
            return True
        return False

    def set_fallback_providers(self, provider_ids: List[str]) -> None:
        """Set fallback providers in order of preference"""
        valid_providers = [pid for pid in provider_ids if pid in self.providers]
        self.fallback_providers = valid_providers
        logger.info(f"Set fallback providers: {valid_providers}")

    def generate_response(
        self,
        messages: List[BaseMessage],
        provider_id: Optional[str] = None,
        **kwargs
    ) -> AIMessage:
        """Generate response with fallback support"""
        providers_to_try = []

        if provider_id and provider_id in self.providers:
            providers_to_try.append(provider_id)
        elif self.primary_provider:
            providers_to_try.append(self.primary_provider)

        providers_to_try.extend(self.fallback_providers)

        # Remove duplicates while preserving order
        providers_to_try = list(dict.fromkeys(providers_to_try))

        last_error = None
        for pid in providers_to_try:
            if pid not in self.providers:
                continue

            try:
                logger.info(f"Attempting generation with provider: {pid}")
                response = self.providers[pid].generate_response(messages, **kwargs)
                logger.info(f"Successfully generated response with provider: {pid}")
                return response
            except Exception as e:
                logger.warning(f"Provider {pid} failed: {e}")
                last_error = e
                continue

        if last_error:
            raise last_error
        else:
            raise RuntimeError("No available providers")

    def get_available_providers(self) -> List[str]:
        """Get list of available provider IDs"""
        return [pid for pid, provider in self.providers.items() if provider.is_available()]

    def get_provider_info(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific provider"""
        if provider_id not in self.providers:
            return None

        provider = self.providers[provider_id]
        return {
            "provider_id": provider_id,
            "provider_type": provider.config.provider.value,
            "model_name": provider.config.model_name,
            "is_available": provider.is_available(),
            "is_primary": provider_id == self.primary_provider,
            "is_fallback": provider_id in self.fallback_providers
        }

# Global LLM manager instance (deprecated). Use get_llm_manager() instead.
_llm_manager: Optional[LLMManager] = None

def get_llm_manager() -> LLMManager:
    """Lazy singleton accessor for the global LLMManager.

    This avoids side-effects at import time (e.g., initializing clients when
    running Alembic migrations or other CLI tools) and encourages explicit
    dependency injection.
    """
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager

# Backwards compatibility: keep original name but reference the new singleton
llm_manager = get_llm_manager()
