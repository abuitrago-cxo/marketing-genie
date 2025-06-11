"""
Enhanced Graph with Tool Integration

Extends the existing LangGraph workflow with tool capabilities while preserving
the original Gemini-based research flow:

1. Route Task -> Determine if tools are needed
2. Generate Initial Queries -> Same as original
3. Web Research -> Same as original
4. Tool Execution -> NEW: Execute tools if needed
5. Reflection & Knowledge Gap Analysis -> Enhanced with tool results
6. Iterative Refinement -> Same as original
7. Finalize Answer -> Enhanced with tool outputs

This maintains the existing Google Gemini integration and chat functionality.
"""

import os
from typing import Dict, Any, List, Optional, Literal
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig

# Import existing components (DO NOT MODIFY)
from agent.graph import (
    generate_query, web_research, reflection, finalize_answer,
    continue_to_web_research, evaluate_research
)
from src.agent.state import OverallState
from agent.configuration import Configuration, get_model
from agent.router import agent_router, AgentType
from agent.prompts import get_current_date

# Import new tool system
from agent.tools import get_tool_registry, ToolResult
from agent.tools.base import ToolError

import logging

logger = logging.getLogger(__name__)


def enhanced_route_task(state: OverallState, config: RunnableConfig) -> OverallState:
    """
    Enhanced task routing that determines if tools are needed.

    Extends the original routing logic to identify tool requirements
    while maintaining compatibility with existing research flow.
    """
    if not state.get("messages"):
        return {"agent_type": AgentType.RESEARCH.value, "requires_tools": False}

    # Get the latest user message
    user_message = ""
    for msg in reversed(state["messages"]):
        if hasattr(msg, 'type') and msg.type == "human":
            user_message = msg.content
            break

    if not user_message:
        return {"agent_type": AgentType.RESEARCH.value, "requires_tools": False}

    # Route the task using existing router
    selected_agent, classification = agent_router.route_task(user_message)

    # Determine if tools are needed based on task content
    requires_tools = _analyze_tool_requirements(user_message, classification)

    # Update agent load
    agent_router.update_agent_load(selected_agent, 1)

    return {
        "agent_type": selected_agent.value,
        "task_classification": {
            "task_type": classification.task_type,
            "complexity": classification.complexity.value,
            "confidence": classification.confidence,
            "reasoning": classification.reasoning
        },
        "requires_tools": requires_tools,
        "tool_requirements": _identify_required_tools(user_message) if requires_tools else []
    }


def _analyze_tool_requirements(message: str, classification) -> bool:
    """Analyze if the message requires tool execution"""
    tool_keywords = [
        # File operations
        "create file", "write file", "read file", "delete file", "list files",
        "save to file", "load from file", "file content",

        # Project management
        "create task", "list tasks", "project status", "task management",
        "milestone", "deadline", "assign task", "project analysis",

        # Web operations
        "download", "fetch url", "api call", "http request", "web scraping",
        "check website", "url status"
    ]

    message_lower = message.lower()
    return any(keyword in message_lower for keyword in tool_keywords)


def _identify_required_tools(message: str) -> List[str]:
    """Identify which specific tools are needed"""
    required_tools = []
    message_lower = message.lower()

    # File operations
    file_keywords = ["file", "create file", "write file", "read file", "save", "load"]
    if any(keyword in message_lower for keyword in file_keywords):
        required_tools.append("file_operations")

    # Project management
    pm_keywords = ["task", "project", "milestone", "deadline", "assign"]
    if any(keyword in message_lower for keyword in pm_keywords):
        required_tools.append("project_management")

    # Web operations
    web_keywords = ["download", "fetch", "api", "http", "url", "website"]
    if any(keyword in message_lower for keyword in web_keywords):
        required_tools.append("web_operations")

    return required_tools


async def execute_tools(state: OverallState, config: RunnableConfig) -> OverallState:
    """
    Execute required tools based on the user's request.

    This is a NEW node that executes tools while maintaining
    compatibility with the existing LangGraph state.
    """
    tool_requirements = state.get("tool_requirements", [])

    if not tool_requirements:
        return {"tool_results": [], "tool_execution_complete": True}

    tool_registry = get_tool_registry()
    tool_results = []

    # Get the latest user message for tool execution
    user_message = ""
    for msg in reversed(state["messages"]):
        if hasattr(msg, 'type') and msg.type == "human":
            user_message = msg.content
            break

    # Execute each required tool
    for tool_name in tool_requirements:
        try:
            # Parse tool action and parameters from user message
            action, parameters = _parse_tool_request(user_message, tool_name)

            if action and parameters:
                result = await tool_registry.execute_tool(tool_name, action, parameters)
                tool_results.append({
                    "tool_name": tool_name,
                    "action": action,
                    "result": result.dict(),
                    "success": result.success
                })

                logger.info(f"Executed tool {tool_name}.{action}: {'success' if result.success else 'failed'}")

        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            tool_results.append({
                "tool_name": tool_name,
                "action": "unknown",
                "result": {"success": False, "error": str(e)},
                "success": False
            })

    return {
        "tool_results": tool_results,
        "tool_execution_complete": True
    }


def _parse_tool_request(message: str, tool_name: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Parse tool action and parameters from user message.

    This is a simplified parser - in production, you'd use LLM to parse this.
    """
    message_lower = message.lower()

    if tool_name == "file_operations":
        if "create file" in message_lower or "write file" in message_lower:
            # Extract file path and content (simplified)
            return "write_file", {
                "file_path": "example.txt",
                "content": "Generated content based on user request"
            }
        elif "read file" in message_lower:
            return "read_file", {"file_path": "example.txt"}
        elif "list files" in message_lower:
            return "list_directory", {"directory_path": "."}

    elif tool_name == "project_management":
        if "create task" in message_lower:
            return "create_task", {
                "title": "Task from user request",
                "description": message
            }
        elif "list tasks" in message_lower:
            return "list_tasks", {}
        elif "project analysis" in message_lower:
            return "analyze_project", {"project_id": "default"}

    elif tool_name == "web_operations":
        if "download" in message_lower or "fetch" in message_lower:
            return "fetch_webpage", {"url": "https://example.com"}
        elif "check" in message_lower and "url" in message_lower:
            return "check_url_status", {"url": "https://example.com"}

    return None, None


def enhanced_reflection(state: OverallState, config: RunnableConfig) -> OverallState:
    """
    Enhanced reflection that considers both web research and tool results.

    Extends the original reflection logic to incorporate tool execution results.
    """
    # First, run the original reflection
    original_result = reflection(state, config)

    # If tools were executed, incorporate their results into the reflection
    tool_results = state.get("tool_results", [])

    if tool_results:
        # Analyze tool results and adjust reflection accordingly
        successful_tools = [r for r in tool_results if r.get("success", False)]
        failed_tools = [r for r in tool_results if not r.get("success", False)]

        # If tools provided useful information, we might be more satisfied
        if successful_tools:
            # Tool results might provide additional context
            original_result["tool_context"] = {
                "successful_tools": len(successful_tools),
                "failed_tools": len(failed_tools),
                "tool_data_available": True
            }

        # If tools failed, we might need more research
        if failed_tools and not successful_tools:
            original_result["is_sufficient"] = False
            original_result["knowledge_gap"] = (
                original_result.get("knowledge_gap", "") +
                " Tool execution failed, need alternative approaches."
            )

    return original_result


def enhanced_finalize_answer(state: OverallState, config: RunnableConfig) -> OverallState:
    """
    Enhanced answer finalization that incorporates tool results.

    Extends the original finalization to include tool outputs in the final answer.
    """
    # First, run the original finalization
    original_result = finalize_answer(state, config)

    # Incorporate tool results if available
    tool_results = state.get("tool_results", [])

    if tool_results:
        # Extract the AI message content
        ai_message = original_result["messages"][0]
        original_content = ai_message.content

        # Add tool results section
        tool_summary = "\n\n## Tool Execution Results\n\n"

        for tool_result in tool_results:
            tool_name = tool_result.get("tool_name", "Unknown")
            action = tool_result.get("action", "unknown")
            success = tool_result.get("success", False)
            result_data = tool_result.get("result", {})

            tool_summary += f"**{tool_name}.{action}**: "
            if success:
                tool_summary += "✅ Success\n"
                if result_data.get("data"):
                    tool_summary += f"- Result: {result_data.get('message', 'Completed successfully')}\n"
            else:
                tool_summary += "❌ Failed\n"
                tool_summary += f"- Error: {result_data.get('error', 'Unknown error')}\n"
            tool_summary += "\n"

        # Combine original content with tool results
        enhanced_content = original_content + tool_summary

        # Create new AI message with enhanced content
        enhanced_message = AIMessage(content=enhanced_content)

        return {
            "messages": [enhanced_message],
            "sources_gathered": original_result.get("sources_gathered", [])
        }

    return original_result


def should_execute_tools(state: OverallState) -> Literal["execute_tools", "generate_query"]:
    """Conditional edge to determine if tools should be executed"""
    requires_tools = state.get("requires_tools", False)

    if requires_tools:
        return "execute_tools"
    else:
        return "generate_query"


def continue_after_tools(state: OverallState) -> Literal["generate_query", "enhanced_finalize_answer"]:
    """Conditional edge after tool execution"""
    tool_results = state.get("tool_results", [])

    # If tools provided sufficient information, we might skip research
    successful_tools = [r for r in tool_results if r.get("success", False)]

    # For now, always continue to research to maintain original behavior
    # In future versions, this could be made smarter
    return "generate_query"


def build_enhanced_graph() -> StateGraph:
    """
    Build the enhanced graph that integrates tools with the existing workflow.

    The enhanced flow:
    1. enhanced_route_task -> Determine agent type and tool requirements
    2. Conditional: execute_tools OR generate_query
    3. If tools executed: continue to generate_query
    4. generate_query -> Same as original (Gemini-based)
    5. web_research -> Same as original (Gemini + Google Search)
    6. enhanced_reflection -> Original reflection + tool context
    7. Conditional: continue research OR finalize
    8. enhanced_finalize_answer -> Original finalization + tool results
    """

    # Create the enhanced graph with the same state schema
    builder = StateGraph(OverallState, config_schema=Configuration)

    # Add all nodes
    builder.add_node("enhanced_route_task", enhanced_route_task)
    builder.add_node("execute_tools", execute_tools)
    builder.add_node("generate_query", generate_query)  # Original node
    builder.add_node("web_research", web_research)      # Original node
    builder.add_node("enhanced_reflection", enhanced_reflection)
    builder.add_node("enhanced_finalize_answer", enhanced_finalize_answer)

    # Set the entrypoint
    builder.add_edge(START, "enhanced_route_task")

    # Conditional edge: tools or direct to query generation
    builder.add_conditional_edges(
        "enhanced_route_task",
        should_execute_tools,
        ["execute_tools", "generate_query"]
    )

    # After tool execution, continue to query generation
    builder.add_conditional_edges(
        "execute_tools",
        continue_after_tools,
        ["generate_query", "enhanced_finalize_answer"]
    )

    # Continue with original flow
    builder.add_conditional_edges(
        "generate_query",
        continue_to_web_research,  # Original function
        ["web_research"]
    )

    # Web research to enhanced reflection
    builder.add_edge("web_research", "enhanced_reflection")

    # Enhanced reflection with original evaluation logic
    builder.add_conditional_edges(
        "enhanced_reflection",
        evaluate_research,  # Original function
        ["web_research", "enhanced_finalize_answer"]
    )

    # Finalize and end
    builder.add_edge("enhanced_finalize_answer", END)

    return builder.compile(name="enhanced-agent-with-tools")


# Create the enhanced graph instance
enhanced_graph = build_enhanced_graph()


def get_enhanced_graph():
    """Get the enhanced graph instance"""
    return enhanced_graph


def get_original_graph():
    """Get the original graph for backward compatibility"""
    from agent.graph import graph
    return graph
