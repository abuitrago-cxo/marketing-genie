"""
Base Specialized Agent

Base class for all specialized agents with common functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from langsmith import traceable


class BaseSpecializedAgent(ABC):
    """
    Base class for specialized agents.
    
    Provides common functionality for LangSmith tracing, error handling,
    and configuration management.
    """
    
    def __init__(self, config: Optional[RunnableConfig] = None):
        """Initialize the base agent with configuration"""
        self.config = config or {}
        self.agent_name = self.__class__.__name__
        self.initialized_at = datetime.now().isoformat()
        
    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with agent's results
        """
        pass
    
    @traceable
    async def safe_execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely execute the agent with error handling.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with results or error information
        """
        try:
            print(f"🚀 {self.agent_name}: Starting execution...")
            start_time = datetime.now()
            
            result = await self.execute(state)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Add execution metadata
            result["execution_metadata"] = {
                "agent": self.agent_name,
                "execution_time": execution_time,
                "timestamp": end_time.isoformat(),
                "success": True
            }
            
            print(f"✅ {self.agent_name}: Completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"❌ {self.agent_name}: Failed with error: {e}")
            
            # Return error state
            return {
                **state,
                "error": {
                    "agent": self.agent_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "timestamp": datetime.now().isoformat()
                },
                "execution_metadata": {
                    "agent": self.agent_name,
                    "success": False,
                    "error": str(e)
                }
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": self.agent_name,
            "initialized_at": self.initialized_at,
            "config": self.config
        }
