"""
Tool Registry

Central registry for managing all available tools in the system.
Provides discovery, registration, and execution coordination.
"""

from typing import Dict, List, Optional, Type, Any
from .base import BaseTool, ToolResult, ToolError
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for all agent tools.
    
    Manages tool registration, discovery, and execution coordination.
    Inspired by II-Agent's tool management but adapted for our system.
    """
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._categories: Dict[str, List[str]] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
    
    def register_tool(self, tool: BaseTool) -> bool:
        """Register a tool instance"""
        try:
            if tool.name in self._tools:
                logger.warning(f"Tool {tool.name} already registered, replacing...")
            
            self._tools[tool.name] = tool
            
            # Update category mapping
            if tool.category not in self._categories:
                self._categories[tool.category] = []
            
            if tool.name not in self._categories[tool.category]:
                self._categories[tool.category].append(tool.name)
            
            logger.info(f"Registered tool: {tool.name} (category: {tool.category})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tool {tool.name}: {e}")
            return False
    
    def register_tool_class(self, tool_class: Type[BaseTool], **kwargs) -> bool:
        """Register a tool class and instantiate it"""
        try:
            tool_instance = tool_class(**kwargs)
            return self.register_tool(tool_instance)
        except Exception as e:
            logger.error(f"Failed to register tool class {tool_class.__name__}: {e}")
            return False
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a specific category"""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(self._categories.keys())
    
    def search_tools(self, query: str) -> List[BaseTool]:
        """Search tools by name or description"""
        query_lower = query.lower()
        matching_tools = []
        
        for tool in self._tools.values():
            if (query_lower in tool.name.lower() or 
                query_lower in tool.description.lower()):
                matching_tools.append(tool)
        
        return matching_tools
    
    def get_tool_capabilities(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get capabilities for a specific tool or all tools"""
        if tool_name:
            tool = self.get_tool(tool_name)
            if tool:
                return {
                    "tool": tool.name,
                    "capabilities": [cap.dict() for cap in tool.get_capabilities()]
                }
            else:
                return {"error": f"Tool {tool_name} not found"}
        
        # Return all tool capabilities
        all_capabilities = {}
        for name, tool in self._tools.items():
            all_capabilities[name] = {
                "description": tool.description,
                "category": tool.category,
                "capabilities": [cap.dict() for cap in tool.get_capabilities()]
            }
        
        return all_capabilities
    
    async def execute_tool(self, tool_name: str, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool action"""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool {tool_name} not found",
                tool_name=tool_name
            )
        
        return await tool.safe_execute(action, parameters)
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get overall registry status"""
        tool_statuses = {}
        for name, tool in self._tools.items():
            tool_statuses[name] = tool.get_status()
        
        return {
            "total_tools": len(self._tools),
            "categories": self._categories,
            "tools": tool_statuses
        }
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool"""
        if name in self._tools:
            tool = self._tools[name]
            del self._tools[name]
            
            # Remove from category
            if tool.category in self._categories:
                if name in self._categories[tool.category]:
                    self._categories[tool.category].remove(name)
                
                # Remove empty categories
                if not self._categories[tool.category]:
                    del self._categories[tool.category]
            
            logger.info(f"Unregistered tool: {name}")
            return True
        
        return False


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
        _initialize_default_tools()
    return _global_registry


def _initialize_default_tools():
    """Initialize default tools in the registry"""
    registry = _global_registry
    
    try:
        # Import and register default tools
        from .file_operations import FileOperationsTool
        from .project_management import ProjectManagementTool
        from .web_operations import WebOperationsTool
        
        # Register tools
        registry.register_tool_class(FileOperationsTool)
        registry.register_tool_class(ProjectManagementTool)
        registry.register_tool_class(WebOperationsTool)
        
        logger.info("Default tools initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize default tools: {e}")


def reset_registry():
    """Reset the global registry (mainly for testing)"""
    global _global_registry
    _global_registry = None
