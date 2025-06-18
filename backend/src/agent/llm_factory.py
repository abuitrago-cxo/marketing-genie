import os
from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI


class LLMFactory:
    """Factory class for creating different LLM instances based on provider."""
    
    @staticmethod
    def create_llm(
        provider: str,
        model_name: str,
        temperature: float = 1.0,
        max_retries: int = 2
    ) -> BaseChatModel:
        """
        Create an LLM instance based on the provider.
        
        Args:
            provider: The AI model provider (gemini, deepseek, ollama, openai)
            model_name: The specific model name
            temperature: The temperature for generation
            max_retries: Maximum number of retries
            
        Returns:
            BaseChatModel: The configured LLM instance
        """
        
        if provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                max_retries=max_retries,
                api_key=os.getenv("GEMINI_API_KEY"),
            )
        elif provider == "deepseek":
            return ChatDeepSeek(
                model=model_name,
                temperature=temperature,
                max_retries=max_retries,
                api_key=os.getenv("DEEPSEEK_API_KEY"),
            )
        elif provider == "ollama":
            return Ollama(
                model=model_name,
                temperature=temperature,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            )
        elif provider == "openai":
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_retries=max_retries,
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),  # 可选，用于自定义端点
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def get_default_model(provider: str, model_type: str = "general") -> str:
        """
        Get the default model name for a given provider and type.
        
        Args:
            provider: The AI model provider
            model_type: The type of model (general, coding, etc.)
            
        Returns:
            str: The default model name
        """
        
        defaults = {
            "gemini": {
                "general": "gemini-2.0-flash",
                "advanced": "gemini-2.5-flash-preview-04-17",
                "pro": "gemini-2.5-pro-preview-05-06"
            },
            "deepseek": {
                "general": "deepseek-chat",
                "coding": "deepseek-coder"
            },
            "ollama": {
                "general": "qwen3:8b",
                "coding": "qwen3:8b",
            },
            "openai": {
                "general": "gpt-4.1",
                "fast": "gpt-4.1-mini",
            }
        }
        
        return defaults.get(provider, {}).get(model_type, defaults[provider]["general"]) 