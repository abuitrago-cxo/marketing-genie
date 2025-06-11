"""
Agent Tools Module

This module provides a comprehensive toolkit for the AI Agent Assistant,
inspired by II-Agent's tool ecosystem but built specifically for our LangGraph-based system.

The tools are designed to work seamlessly with the existing Google Gemini integration
and LangGraph workflow without modifying the core chat functionality.
"""

from .base import BaseTool, ToolResult, ToolError
from .registry import ToolRegistry, get_tool_registry
from .file_operations import FileOperationsTool
from .project_management import ProjectManagementTool
from .web_operations import WebOperationsTool

__all__ = [
    'BaseTool',
    'ToolResult', 
    'ToolError',
    'ToolRegistry',
    'get_tool_registry',
    'FileOperationsTool',
    'ProjectManagementTool',
    'WebOperationsTool'
]
