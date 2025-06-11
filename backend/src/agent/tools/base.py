"""
Base Tool Classes

Provides the foundation for all agent tools, inspired by II-Agent's architecture
but designed specifically for our LangGraph-based system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class ToolStatus(str, Enum):
    """Tool execution status"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


class ToolResult(BaseModel):
    """Result of tool execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    tool_name: str = ""
    tool_id: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolError(Exception):
    """Custom exception for tool errors"""
    def __init__(self, message: str, tool_name: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.details = details or {}


class ToolCapability(BaseModel):
    """Describes what a tool can do"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    examples: List[str] = Field(default_factory=list)
    category: str = "general"


class BaseTool(ABC):
    """
    Base class for all agent tools.
    
    Inspired by II-Agent's tool architecture but adapted for our LangGraph system.
    All tools should inherit from this class and implement the required methods.
    """
    
    def __init__(self, name: str, description: str, category: str = "general"):
        self.name = name
        self.description = description
        self.category = category
        self.tool_id = str(uuid.uuid4())
        self.status = ToolStatus.IDLE
        self.created_at = time.time()
        self.last_used = None
        self.usage_count = 0
        
    @abstractmethod
    def get_capabilities(self) -> List[ToolCapability]:
        """Return list of capabilities this tool provides"""
        pass
    
    @abstractmethod
    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool action with given parameters"""
        pass
    
    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Validate parameters for a specific action"""
        capabilities = self.get_capabilities()
        for capability in capabilities:
            if capability.name == action:
                # Basic validation - can be extended
                required_params = capability.parameters.get('required', [])
                for param in required_params:
                    if param not in parameters:
                        raise ToolError(
                            f"Missing required parameter: {param}",
                            tool_name=self.name,
                            details={"action": action, "required": required_params}
                        )
                return True
        
        raise ToolError(
            f"Unknown action: {action}",
            tool_name=self.name,
            details={"available_actions": [c.name for c in capabilities]}
        )
    
    async def safe_execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """Safely execute tool action with error handling and timing"""
        start_time = time.time()
        self.status = ToolStatus.RUNNING
        
        try:
            # Validate parameters
            self.validate_parameters(action, parameters)
            
            # Execute the action
            result = await self.execute(action, parameters)
            
            # Update timing and usage
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.tool_name = self.name
            result.tool_id = self.tool_id
            
            self.status = ToolStatus.SUCCESS if result.success else ToolStatus.ERROR
            self.last_used = time.time()
            self.usage_count += 1
            
            logger.info(f"Tool {self.name} executed action '{action}' in {execution_time:.2f}s")
            return result
            
        except ToolError as e:
            execution_time = time.time() - start_time
            self.status = ToolStatus.ERROR
            
            result = ToolResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                tool_name=self.name,
                tool_id=self.tool_id,
                metadata={"error_details": e.details}
            )
            
            logger.error(f"Tool {self.name} failed: {e}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.status = ToolStatus.ERROR
            
            result = ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                execution_time=execution_time,
                tool_name=self.name,
                tool_id=self.tool_id
            )
            
            logger.error(f"Tool {self.name} unexpected error: {e}", exc_info=True)
            return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current tool status and metrics"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tool_id": self.tool_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "usage_count": self.usage_count,
            "capabilities": [cap.dict() for cap in self.get_capabilities()]
        }
    
    def reset_status(self):
        """Reset tool status to idle"""
        self.status = ToolStatus.IDLE
