"""
Enhanced API endpoints for the AI Agent Assistant
Provides endpoints for agent status, LLM provider management, and system monitoring.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from agent.configuration import get_llm_status, configure_llm_providers
from agent.router import agent_router
from agent.llm_manager import llm_manager, LLMConfig, LLMProvider

logger = logging.getLogger(__name__)

# Create router for enhanced endpoints
enhanced_router = APIRouter(prefix="/api/v1/enhanced", tags=["enhanced"])

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
        config_status = configure_llm_providers()
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
    """Create a new task for a specific agent"""
    try:
        # This would be implemented with actual task creation
        # For now, return mock response
        return {
            "success": True,
            "task_id": "mock_task_id",
            "agent_type": agent_type,
            "message": "Task created successfully"
        }
    except Exception as e:
        logger.error(f"Failed to create agent task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create agent task")

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
