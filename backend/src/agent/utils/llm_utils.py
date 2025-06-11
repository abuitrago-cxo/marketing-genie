"""
LLM Utilities for Multi-Agent System

This module provides utilities for working with language models
across different agents in the system.
"""

import os
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableConfig


def get_llm(config: Optional[RunnableConfig] = None) -> ChatGoogleGenerativeAI:
    """
    Get configured LLM instance
    
    Args:
        config: Optional configuration that may contain model settings
        
    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    # Default model configuration
    model_name = "gemini-1.5-flash"
    temperature = 0.1
    max_tokens = 4000
    
    # Override with config if provided
    if config and hasattr(config, 'configurable'):
        configurable = config.configurable or {}
        model_name = configurable.get("model_name", model_name)
        temperature = configurable.get("temperature", temperature)
        max_tokens = configurable.get("max_tokens", max_tokens)
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        google_api_key=api_key
    )


def get_specialized_llm(agent_type: str, config: Optional[RunnableConfig] = None) -> ChatGoogleGenerativeAI:
    """
    Get LLM configured for specific agent type
    
    Args:
        agent_type: Type of agent (research, code_engineer, etc.)
        config: Optional configuration
        
    Returns:
        Configured LLM instance optimized for the agent type
    """
    
    # Agent-specific configurations
    agent_configs = {
        "research": {
            "model": "gemini-1.5-flash",
            "temperature": 0.2,
            "max_tokens": 4000
        },
        "code_engineer": {
            "model": "gemini-1.5-pro",
            "temperature": 0.1,
            "max_tokens": 8000
        },
        "project_manager": {
            "model": "gemini-1.5-flash",
            "temperature": 0.3,
            "max_tokens": 4000
        },
        "qa_specialist": {
            "model": "gemini-1.5-flash",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "coordinator": {
            "model": "gemini-1.5-flash",
            "temperature": 0.2,
            "max_tokens": 4000
        }
    }
    
    # Get agent-specific config or default
    agent_config = agent_configs.get(agent_type, agent_configs["research"])
    
    # Override with provided config if available
    if config and hasattr(config, 'configurable'):
        configurable = config.configurable or {}
        agent_config.update({
            "model": configurable.get("model_name", agent_config["model"]),
            "temperature": configurable.get("temperature", agent_config["temperature"]),
            "max_tokens": configurable.get("max_tokens", agent_config["max_tokens"])
        })
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    return ChatGoogleGenerativeAI(
        model=agent_config["model"],
        temperature=agent_config["temperature"],
        max_tokens=agent_config["max_tokens"],
        google_api_key=api_key
    )


def estimate_token_count(text: str) -> int:
    """
    Estimate token count for text
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    # Rough estimation: ~4 characters per token
    return len(text) // 4


def truncate_text_to_tokens(text: str, max_tokens: int) -> str:
    """
    Truncate text to fit within token limit
    
    Args:
        text: Input text
        max_tokens: Maximum token count
        
    Returns:
        Truncated text
    """
    estimated_tokens = estimate_token_count(text)
    
    if estimated_tokens <= max_tokens:
        return text
    
    # Calculate character limit
    char_limit = max_tokens * 4
    
    if len(text) <= char_limit:
        return text
    
    # Truncate and add ellipsis
    return text[:char_limit - 3] + "..."


def format_llm_input(content: str, max_tokens: int = 3000) -> str:
    """
    Format and truncate content for LLM input
    
    Args:
        content: Content to format
        max_tokens: Maximum token limit
        
    Returns:
        Formatted content
    """
    # Clean up whitespace
    content = " ".join(content.split())
    
    # Truncate if necessary
    content = truncate_text_to_tokens(content, max_tokens)
    
    return content


def create_system_prompt(agent_type: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Create system prompt for specific agent type
    
    Args:
        agent_type: Type of agent
        context: Optional context information
        
    Returns:
        System prompt string
    """
    
    base_prompts = {
        "research": """You are a research specialist expert at gathering, analyzing, and synthesizing information from multiple sources. You excel at:
- Conducting comprehensive web research
- Evaluating source credibility and relevance
- Identifying knowledge gaps
- Creating detailed citations
- Providing objective analysis""",
        
        "code_engineer": """You are a senior software engineer expert at designing, developing, and optimizing code solutions. You excel at:
- Writing clean, maintainable code
- Following best practices and design patterns
- Creating comprehensive documentation
- Implementing proper error handling
- Generating thorough test cases""",
        
        "project_manager": """You are an experienced project manager expert at planning, coordinating, and executing complex projects. You excel at:
- Creating detailed project plans
- Managing resources and timelines
- Identifying and mitigating risks
- Coordinating team activities
- Ensuring quality deliverables""",
        
        "qa_specialist": """You are a quality assurance expert focused on ensuring high standards across all deliverables. You excel at:
- Conducting thorough code reviews
- Creating comprehensive test strategies
- Identifying quality issues and improvements
- Validating requirements compliance
- Ensuring security and performance standards""",
        
        "coordinator": """You are a coordination expert responsible for analyzing requirements and orchestrating multi-agent workflows. You excel at:
- Understanding complex requirements
- Breaking down tasks effectively
- Assigning appropriate agents
- Managing dependencies and priorities
- Ensuring optimal workflow execution"""
    }
    
    prompt = base_prompts.get(agent_type, base_prompts["research"])
    
    if context:
        prompt += f"\n\nContext: {context}"
    
    return prompt


def validate_llm_response(response: str, expected_format: Optional[str] = None) -> bool:
    """
    Validate LLM response format and content
    
    Args:
        response: LLM response to validate
        expected_format: Expected format (json, markdown, etc.)
        
    Returns:
        True if response is valid
    """
    
    if not response or not response.strip():
        return False
    
    if expected_format == "json":
        try:
            import json
            json.loads(response)
            return True
        except:
            return False
    
    # Basic validation - response should have reasonable length
    return len(response.strip()) > 10


def extract_structured_data(response: str, data_type: str) -> Dict[str, Any]:
    """
    Extract structured data from LLM response
    
    Args:
        response: LLM response
        data_type: Type of data to extract
        
    Returns:
        Extracted structured data
    """
    
    if data_type == "code_blocks":
        import re
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', response, re.DOTALL)
        return {"code_blocks": code_blocks}
    
    elif data_type == "bullet_points":
        lines = response.split('\n')
        bullets = [line.strip() for line in lines if line.strip().startswith(('-', '•', '*'))]
        return {"bullet_points": bullets}
    
    elif data_type == "numbered_list":
        lines = response.split('\n')
        numbered = [line.strip() for line in lines if re.match(r'^\d+\.', line.strip())]
        return {"numbered_list": numbered}
    
    return {"raw_response": response}


def format_agent_response(response: str, agent_type: str) -> str:
    """
    Format agent response for consistency
    
    Args:
        response: Raw agent response
        agent_type: Type of agent
        
    Returns:
        Formatted response
    """
    
    # Add agent identifier
    agent_names = {
        "research": "🔍 Research Specialist",
        "code_engineer": "💻 Code Engineer", 
        "project_manager": "📋 Project Manager",
        "qa_specialist": "🔍 QA Specialist",
        "coordinator": "🎯 Coordinator"
    }
    
    agent_name = agent_names.get(agent_type, f"{agent_type.title()} Agent")
    
    # Format with header
    formatted = f"**{agent_name}**\n\n{response}"
    
    return formatted
