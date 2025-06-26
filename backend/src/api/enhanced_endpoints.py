"""
Enhanced API endpoints for the AI Agent Assistant
Provides endpoints for agent status, LLM provider management, and system monitoring.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from agent.configuration import Configuration
from agent.router import agent_router
from agent.llm_manager import llm_manager, LLMConfig, LLMProvider
from agent.tools import get_tool_registry

logger = logging.getLogger(__name__)

# Create router for enhanced endpoints
enhanced_router = APIRouter(prefix="/api/v1/enhanced", tags=["enhanced"])

# --- Simple in-memory task registry (prototype) ---
# In production this should be replaced by persistent task tracking (DB or queue)
_task_registry: Dict[str, Dict[str, Any]] = {}

# Helper function to get LLM status
def get_llm_status():
    """Get LLM status using the llm_manager"""
    available_providers = llm_manager.get_available_providers()
    primary_provider = llm_manager.primary_provider
    fallback_providers = llm_manager.fallback_providers

    provider_details = {}
    for provider_id in llm_manager.providers.keys():
        info = llm_manager.get_provider_info(provider_id)
        if info:
            provider_details[provider_id] = info

    return {
        "available_providers": available_providers,
        "primary_provider": primary_provider,
        "fallback_providers": fallback_providers,
        "provider_details": provider_details
    }

# Pydantic models for request/response
class AgentStatusResponse(BaseModel):
    agents: Dict[str, Dict[str, Any]]
    total_active_tasks: int

class LLMStatusResponse(BaseModel):
    available_providers: List[str]
    primary_provider: Optional[str]
    fallback_providers: List[str]
    provider_details: Dict[str, Dict[str, Any]]

class LLMProviderRequest(BaseModel):
    provider: str
    model_name: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class SystemStatusResponse(BaseModel):
    agent_status: AgentStatusResponse
    llm_status: LLMStatusResponse
    system_health: str
    uptime: str

@enhanced_router.get("/agents/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """Get current status of all agents"""
    try:
        status = agent_router.get_agent_status()
        return AgentStatusResponse(**status)
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent status")

@enhanced_router.get("/llm/status", response_model=LLMStatusResponse)
async def get_llm_status_endpoint():
    """Get current status of all LLM providers"""
    try:
        status = get_llm_status()
        return LLMStatusResponse(**status)
    except Exception as e:
        logger.error(f"Failed to get LLM status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get LLM status")

@enhanced_router.post("/llm/providers")
async def add_llm_provider(request: LLMProviderRequest):
    """Add a new LLM provider"""
    try:
        # Map string to enum
        provider_enum = LLMProvider(request.provider.lower())

        config = LLMConfig(
            provider=provider_enum,
            model_name=request.model_name,
            api_key=request.api_key,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        provider_id = llm_manager.add_provider(config)

        if provider_id:
            return {
                "success": True,
                "provider_id": provider_id,
                "message": f"Provider {provider_id} added successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to add provider - check API key and configuration"
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {e}")
    except Exception as e:
        logger.error(f"Failed to add LLM provider: {e}")
        raise HTTPException(status_code=500, detail="Failed to add LLM provider")

@enhanced_router.put("/llm/primary/{provider_id}")
async def set_primary_provider(provider_id: str):
    """Set the primary LLM provider"""
    try:
        success = llm_manager.set_primary_provider(provider_id)
        if success:
            return {
                "success": True,
                "message": f"Primary provider set to {provider_id}"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Provider {provider_id} not found"
            )
    except Exception as e:
        logger.error(f"Failed to set primary provider: {e}")
        raise HTTPException(status_code=500, detail="Failed to set primary provider")

@enhanced_router.put("/llm/fallbacks")
async def set_fallback_providers(provider_ids: List[str]):
    """Set fallback LLM providers"""
    try:
        llm_manager.set_fallback_providers(provider_ids)
        return {
            "success": True,
            "message": f"Fallback providers set to {provider_ids}"
        }
    except Exception as e:
        logger.error(f"Failed to set fallback providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to set fallback providers")

@enhanced_router.post("/llm/reconfigure")
async def reconfigure_llm_providers():
    """Reconfigure LLM providers based on available API keys"""
    try:
        # Reload default providers
        llm_manager._load_default_providers()

        available_providers = llm_manager.get_available_providers()
        config_status = {
            "providers_loaded": len(llm_manager.providers),
            "available_providers": available_providers,
            "primary_provider": llm_manager.primary_provider
        }

        return {
            "success": True,
            "configuration_status": config_status
        }
    except Exception as e:
        logger.error(f"Failed to reconfigure LLM providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to reconfigure LLM providers")

@enhanced_router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get comprehensive system status"""
    try:
        agent_status = agent_router.get_agent_status()
        llm_status = get_llm_status()

        # Determine system health
        system_health = "healthy"
        if not llm_status["available_providers"]:
            system_health = "error"
        elif agent_status["total_active_tasks"] > 20:
            system_health = "warning"

        return SystemStatusResponse(
            agent_status=AgentStatusResponse(**agent_status),
            llm_status=LLMStatusResponse(**llm_status),
            system_health=system_health,
            uptime="N/A"  # Could be implemented with actual uptime tracking
        )
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@enhanced_router.get("/agents/{agent_type}/tasks")
async def get_agent_tasks(agent_type: str):
    """Get current tasks for a specific agent type"""
    try:
        # This would be implemented with actual task tracking
        # For now, return mock data
        return {
            "agent_type": agent_type,
            "active_tasks": [],
            "completed_tasks": [],
            "failed_tasks": []
        }
    except Exception as e:
        logger.error(f"Failed to get agent tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent tasks")

@enhanced_router.post("/agents/{agent_type}/tasks")
async def create_agent_task(agent_type: str, task_data: Dict[str, Any]):
    """Create a new task for a specific agent using direct dispatch"""
    try:
        from agent.router import AgentType  # Enum of agents

        # Validate and convert agent_type string to AgentType enum
        try:
            enum_agent_type = AgentType(agent_type)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Unknown agent type '{agent_type}'")

        task_id = agent_router.dispatch_direct_task(enum_agent_type, task_data)
        if task_id:
            # Store task entry in registry with mock pending status
            _task_registry[task_id] = {
                "agent_type": agent_type,
                "status": "pending",
                "input": task_data,
                "result": None
            }
        if task_id:
            return {
                "success": True,
                "task_id": task_id,
                "agent_type": agent_type,
                "message": "Task created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create task for {agent_type}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create task for {agent_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create agent task")

# ---------------- Task status endpoint ----------------
@enhanced_router.get("/agents/tasks/{task_id}")
async def get_agent_task_status(task_id: str):
    """Return status/result for a previously created agent task."""
    try:
        task = _task_registry.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # For demo, after first read mark completed with mock result
        if task["status"] == "pending":
            task["status"] = "completed"
            task["result"] = {"message": "Code engineer task finished successfully"}

        return {"success": True, **task, "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task status")

@enhanced_router.get("/metrics/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        # This would be implemented with actual metrics collection
        return {
            "response_times": {
                "average": 1.2,
                "p95": 2.5,
                "p99": 5.0
            },
            "throughput": {
                "requests_per_minute": 45,
                "tasks_completed": 123
            },
            "resource_usage": {
                "cpu_percent": 25.5,
                "memory_percent": 45.2,
                "disk_usage": 67.8
            },
            "error_rates": {
                "total_errors": 3,
                "error_rate_percent": 0.5
            }
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance metrics")

@enhanced_router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    try:
        llm_status = get_llm_status()
        agent_status = agent_router.get_agent_status()

        return {
            "status": "healthy",
            "timestamp": "2025-01-03T00:00:00Z",
            "services": {
                "llm_providers": len(llm_status["available_providers"]) > 0,
                "agent_router": True,
                "database": True  # Would check actual database connection
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Tool Management Endpoints (Phase 2)

class ToolExecutionRequest(BaseModel):
    tool_name: str
    action: str
    parameters: Dict[str, Any]

class ToolExecutionResponse(BaseModel):
    success: bool
    tool_name: str
    action: str
    result: Dict[str, Any]
    execution_time: float

@enhanced_router.get("/tools/registry")
async def get_tools_registry():
    """Get all available tools and their capabilities"""
    try:
        registry = get_tool_registry()
        return {
            "success": True,
            "data": registry.get_registry_status()
        }
    except Exception as e:
        logger.error(f"Failed to get tools registry: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tools registry")

@enhanced_router.get("/tools/{tool_name}/capabilities")
async def get_tool_capabilities(tool_name: str):
    """Get capabilities for a specific tool"""
    try:
        registry = get_tool_registry()
        capabilities = registry.get_tool_capabilities(tool_name)

        if "error" in capabilities:
            raise HTTPException(status_code=404, detail=capabilities["error"])

        return {
            "success": True,
            "data": capabilities
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tool capabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tool capabilities")

@enhanced_router.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute a tool action"""
    try:
        registry = get_tool_registry()
        result = await registry.execute_tool(
            request.tool_name,
            request.action,
            request.parameters
        )

        return ToolExecutionResponse(
            success=result.success,
            tool_name=result.tool_name,
            action=request.action,
            result=result.dict(),
            execution_time=result.execution_time
        )
    except Exception as e:
        logger.error(f"Failed to execute tool: {e}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@enhanced_router.get("/tools/search")
async def search_tools(query: str):
    """Search for tools by name or description"""
    try:
        registry = get_tool_registry()
        matching_tools = registry.search_tools(query)

        return {
            "success": True,
            "query": query,
            "data": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "capabilities": [cap.dict() for cap in tool.get_capabilities()]
                }
                for tool in matching_tools
            ]
        }
    except Exception as e:
        logger.error(f"Failed to search tools: {e}")
        raise HTTPException(status_code=500, detail="Failed to search tools")


# Enhanced Graph Endpoints

@enhanced_router.get("/graph/status")
async def get_graph_status():
    """Get status of available graphs (original vs enhanced)"""
    try:
        from agent.enhanced_graph import get_enhanced_graph, get_original_graph

        return {
            "success": True,
            "data": {
                "original_graph_available": True,
                "enhanced_graph_available": True,
                "default_graph": "enhanced",
                "features": {
                    "original": ["web_research", "reflection", "gemini_integration"],
                    "enhanced": ["web_research", "reflection", "gemini_integration", "tool_execution", "file_operations", "project_management"]
                }
            }
        }
    except Exception as e:
        logger.error(f"Failed to get graph status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get graph status")
