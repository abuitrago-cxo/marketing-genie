print("DEBUG: specialized_endpoints.py - Top of file")
"""
Real Specialized Agent API Endpoints

Provides API endpoints for the real specialized agent system with monitoring.
"""

# Standard library imports
print("DEBUG: specialized_endpoints.py - Importing standard library types...")
import importlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
print("DEBUG: specialized_endpoints.py - Standard library types imported: Dict, List, Optional, Any, Union, Tuple")

# Third-party library imports
print("DEBUG: specialized_endpoints.py - Importing FastAPI and Pydantic...")
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
print("DEBUG: specialized_endpoints.py - FastAPI, Pydantic, Langchain_core imported.")



# Internal module imports
print("DEBUG: specialized_endpoints.py - Importing agent, monitoring, and memory modules...")

print("DEBUG: specialized_endpoints.py - Importing agent.multi_agent_graph...")

from agent.multi_agent_graph import build_multi_agent_graph
from agent.multi_agent_state import create_initial_state as create_initial_multi, calculate_overall_quality, get_execution_metrics
from memory.long_term_memory_manager import get_long_memory_manager
from memory.short_term_memory_manager import get_short_memory_manager
from agent.specialized_graph import build_specialized_graph
from agent.true_specialized_graph import build_true_specialized_graph
from agent.specialized_state import create_initial_state as create_specialized_state
from monitoring.workflow_logging import log_workflow_execution
from agent.graphs.graph_registry import get_graph_registry, get_specialized_graph, list_available_graphs
from monitoring.langsmith_metrics import langsmith_monitor
from agent.configuration import Configuration

# Extraemos las funciones necesarias de los módulos importados
build_multi_agent_graph = build_multi_agent_graph
create_initial_state = create_initial_multi
calculate_overall_quality = calculate_overall_quality
get_execution_metrics = get_execution_metrics
get_long_memory_manager = get_long_memory_manager
get_short_memory_manager = get_short_memory_manager
build_specialized_graph = build_specialized_graph
create_specialized_state = create_specialized_state
build_true_specialized_graph = build_true_specialized_graph
log_workflow_execution = log_workflow_execution
get_graph_registry = get_graph_registry
get_specialized_graph = get_specialized_graph
list_available_graphs = list_available_graphs
langsmith_monitor = langsmith_monitor
Configuration = Configuration

# Las importaciones anteriores ya son robustas, no necesitamos importaciones directas duplicadas
print("DEBUG: specialized_endpoints.py - Agent, monitoring, and memory modules import attempt finished.")


print("DEBUG: specialized_endpoints.py - Before APIRouter instantiation.")
router = APIRouter(prefix="/api/v1/specialized", tags=["specialized-agents"])
print("DEBUG: specialized_endpoints.py - After APIRouter instantiation.")


class SpecializedQuery(BaseModel):
    """Request model for specialized agent queries"""
    query: str
    max_research_iterations: Optional[int] = 3
    enable_tracing: Optional[bool] = True
    user_id: Optional[str] = None
    session_id: Optional[str] = None  # For memory integration
    project_id: Optional[int] = None  # For project context
    use_multi_agent: Optional[bool] = False
    use_real_agents: Optional[bool] = True  # Use REAL specialized agents by default
    use_memory: Optional[bool] = True  # Enable memory integration


class SpecializedResponse(BaseModel):
    """Response model for specialized agent queries"""
    final_answer: str
    citations: list
    quality_score: float
    execution_metrics: Dict[str, Any]
    workflow_complete: bool
    fallback_used: bool
    trace_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    trace_id: str
    rating: int  # 1-5 scale
    comment: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/query", response_model=SpecializedResponse)
async def process_specialized_query(
    request: SpecializedQuery,
    background_tasks: BackgroundTasks
):
    """
    Process a query using the specialized agent system.
    """
    return await specialized_query(request, background_tasks)


@router.post("/chat", response_model=SpecializedResponse)
async def process_chat_query(
    request: SpecializedQuery,
    background_tasks: BackgroundTasks
):
    """
    Process a chat query with memory integration and project context.
    This endpoint is optimized for conversational AI with system-wide memory access.
    """
    return await chat_query_with_memory(request, background_tasks)
print("DEBUG: specialized_endpoints.py - End of file")

async def specialized_query(
    request: SpecializedQuery,
    background_tasks: BackgroundTasks
):
    """
    Process a query using the specialized agent system.

    This endpoint coordinates Research, Analysis, and Synthesis agents
    to provide comprehensive responses with full traceability.
    """
    try:
        # Create configuration
        config = {
            "configurable": {
                "max_research_loops": request.max_research_iterations,
                "enable_tracing": request.enable_tracing
            }
        }

        # Choose which system to use
        if request.use_multi_agent:
            # Use the 4-agent multi-agent system
            result = await run_multi_agent_workflow(request.query, config)
        elif request.use_real_agents:
            # Use the REAL 3-agent specialized system with ii-agent logic
            result = await run_true_specialized_workflow(request.query, config)
        else:
            # Use the basic 3-agent specialized system (legacy)
            result = await run_specialized_workflow(request.query, config)

        # Log workflow execution in background
        if request.enable_tracing:
            background_tasks.add_task(
                log_workflow_execution,
                request.query,
                result,
                request.user_id
            )

        return SpecializedResponse(
            final_answer=result["final_answer"],
            citations=result["citations"],
            quality_score=result["quality_score"],
            execution_metrics=result["execution_metrics"],
            workflow_complete=result["workflow_complete"],
            fallback_used=result["fallback_used"],
            trace_id=result.get("trace_id")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


async def chat_query_with_memory(
    request: SpecializedQuery,
    background_tasks: BackgroundTasks
) -> SpecializedResponse:
    """
    Process a chat query with integrated memory access and project context.

    This function:
    1. Retrieves relevant memories from long-term storage
    2. Checks short-term cache for recent context
    3. Integrates project information if available
    4. Processes the query with enhanced context
    5. Stores new memories for future reference
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"chat_{datetime.now().timestamp()}"

        # Initialize memory managers
        long_memory = await get_long_memory_manager()
        short_memory = await get_short_memory_manager()

        # Retrieve relevant memories
        relevant_memories = []
        if long_memory and request.use_memory:
            try:
                memories = await long_memory.retrieve_memories(
                    agent_id="chat_agent",
                    query_text=request.query,
                    user_id=request.user_id,
                    project_id=request.project_id,
                    limit=5,
                    min_importance=0.3
                )
                relevant_memories = [
                    f"Memory: {m.content} (importance: {m.importance_score})"
                    for m in memories
                ]
            except Exception as e:
                print(f"⚠️ Memory retrieval failed: {e}")

        # Get project context if available
        project_context = ""
        if request.project_id:
            # TODO: Retrieve project information from database
            project_context = f"Project context for project ID: {request.project_id}"

        # Enhance query with context
        enhanced_query = request.query
        if relevant_memories or project_context:
            context_parts = []
            if project_context:
                context_parts.append(f"Project Context: {project_context}")
            if relevant_memories:
                context_parts.append("Relevant Memories:")
                context_parts.extend(relevant_memories)

            enhanced_query = f"""
Context Information:
{chr(10).join(context_parts)}

User Query: {request.query}

Please provide a comprehensive response considering the above context and any relevant information about managed projects.
"""

        # Create enhanced request
        enhanced_request = SpecializedQuery(
            query=enhanced_query,
            max_research_iterations=request.max_research_iterations,
            enable_tracing=request.enable_tracing,
            user_id=request.user_id,
            session_id=session_id,
            project_id=request.project_id,
            use_multi_agent=request.use_multi_agent,
            use_real_agents=request.use_real_agents,
            use_memory=request.use_memory
        )

        # Process the enhanced query
        result = await specialized_query(enhanced_request, background_tasks)

        # Store new memory if enabled
        if long_memory and request.use_memory and result.final_answer:
            try:
                await long_memory.store_memory(
                    agent_id="chat_agent",
                    content=f"Q: {request.query}\nA: {result.final_answer}",
                    memory_type="conversation",
                    user_id=request.user_id,
                    session_id=session_id,
                    project_id=request.project_id,
                    importance_score=min(result.quality_score, 1.0),
                    metadata={
                        "query_type": "chat",
                        "has_context": bool(relevant_memories or project_context),
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                print(f"⚠️ Memory storage failed: {e}")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat query with memory failed: {str(e)}")


async def run_true_specialized_workflow(query: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the TRUE specialized workflow using REAL agent classes"""
    try:
        # Build the TRUE specialized graph with REAL agents
        graph = build_true_specialized_graph()

        # Create initial state
        messages = [HumanMessage(content=query)]
        initial_state = create_specialized_state(
            messages=messages,
            query=query,
            max_iterations=config.get("configurable", {}).get("max_research_loops", 3),
            enable_tracing=config.get("configurable", {}).get("enable_tracing", True)
        )

        # Execute the workflow with REAL agents
        result = await graph.ainvoke(initial_state, config=config)

        return {
            "final_answer": result.get("final_answer", ""),
            "citations": result.get("citations", []),
            "quality_score": result.get("overall_quality_score", 0.0),
            "execution_metrics": result.get("execution_metrics", {}),
            "workflow_complete": result.get("workflow_stage") == "complete",
            "fallback_used": result.get("fallback_used", False),
            "agent_system": "true_specialized_agents"  # Identifier
        }

    except Exception as e:
        print(f"❌ TRUE Specialized workflow failed: {e}")
        return {
            "final_answer": f"I encountered an error processing your query with the specialized agents: {str(e)}",
            "citations": [],
            "quality_score": 0.1,
            "execution_metrics": {"error": str(e)},
            "workflow_complete": False,
            "fallback_used": True,
            "agent_system": "true_specialized_agents_error"
        }


async def run_specialized_workflow(query: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the basic 3-agent specialized workflow (legacy)"""
    try:
        # Build the basic specialized graph
        graph = build_specialized_graph()

        # Create initial state
        messages = [HumanMessage(content=query)]
        initial_state = create_specialized_state(
            messages=messages,
            query=query,
            max_iterations=config.get("configurable", {}).get("max_research_loops", 3),
            enable_tracing=config.get("configurable", {}).get("enable_tracing", True)
        )

        # Execute the workflow
        result = await graph.ainvoke(initial_state, config=config)

        return {
            "final_answer": result.get("final_answer", ""),
            "citations": result.get("citations", []),
            "quality_score": result.get("overall_quality_score", 0.0),
            "execution_metrics": result.get("execution_metrics", {}),
            "workflow_complete": result.get("workflow_stage") == "complete",
            "fallback_used": result.get("fallback_used", False),
            "agent_system": "basic_specialized_agents"  # Identifier
        }

    except Exception as e:
        print(f"❌ Basic Specialized workflow failed: {e}")
        return {
            "final_answer": f"I encountered an error processing your query: {str(e)}",
            "citations": [],
            "quality_score": 0.1,
            "execution_metrics": {"error": str(e)},
            "workflow_complete": False,
            "fallback_used": True,
            "agent_system": "basic_specialized_agents_error"
        }


async def run_multi_agent_workflow(query: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the 4-agent multi-agent workflow"""
    try:
        # Build the multi-agent graph
        graph = build_multi_agent_graph()

        # Create initial state
        messages = [HumanMessage(content=query)]
        initial_state = create_initial_state(
            messages=messages,
            query=query,
            enable_tracing=config.get("configurable", {}).get("enable_tracing", True)
        )

        # Execute the workflow
        result = await graph.ainvoke(initial_state, config=config)

        return {
            "final_answer": result.get("final_answer", ""),
            "citations": result.get("citations", []),
            "quality_score": calculate_overall_quality(result),
            "execution_metrics": get_execution_metrics(result),
            "workflow_complete": result.get("workflow_stage").value == "complete" if result.get("workflow_stage") else False,
            "fallback_used": result.get("fallback_used", False)
        }

    except Exception as e:
        print(f"❌ Multi-agent workflow failed: {e}")
        return {
            "final_answer": f"I encountered an error processing your query: {str(e)}",
            "citations": [],
            "quality_score": 0.1,
            "execution_metrics": {"error": str(e)},
            "workflow_complete": False,
            "fallback_used": True
        }


# ===== NEW SPECIALIZED GRAPH ENDPOINTS =====

@router.get("/graphs/available")
async def get_available_graphs():
    """Get list of all available specialized graphs"""
    try:
        registry = get_graph_registry()
        graphs = registry.get_all_metadata()

        return {
            "success": True,
            "graphs": graphs,
            "total_count": len(graphs),
            "execution_order": registry.get_execution_order(),
            "health_status": registry.get_health_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available graphs: {str(e)}")


# Ensure Any type is recognized in all class definitions
AnyType = Any  # Create an alias to ensure type is accessible

class SpecializedGraphRequest(BaseModel):
    graph_id: str
    input_data: Dict[str, Any]
    enable_tracing: bool = True
    max_iterations: int = 3


@router.post("/graphs/execute/{graph_id}")
async def execute_specialized_graph(graph_id: str, request: SpecializedGraphRequest):
    """Execute a specific specialized graph"""
    try:
        # Get the graph from registry
        graph = get_specialized_graph(graph_id)
        if not graph:
            raise HTTPException(status_code=404, detail=f"Graph '{graph_id}' not found")

        # Get graph metadata
        registry = get_graph_registry()
        metadata = registry.get_graph_metadata(graph_id)

        # Create initial state based on graph type
        state_class = metadata["state_class"]
        initial_state = {
            **request.input_data,
            "messages": [HumanMessage(content=request.input_data.get("query", ""))],
            "agent_type": graph_id,
            "max_research_loops": request.max_iterations
        }

        # Execute the graph
        config = {
            "configurable": {
                "enable_tracing": request.enable_tracing,
                "max_iterations": request.max_iterations
            }
        }

        result = await graph.ainvoke(initial_state, config=config)

        return {
            "success": True,
            "graph_id": graph_id,
            "result": result,
            "metadata": metadata,
            "execution_complete": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph execution failed: {str(e)}")


@router.post("/graphs/orchestrate")
async def orchestrate_multiple_graphs(request: Dict[str, Any]):
    """Execute multiple graphs in coordinated fashion using Project Orchestrator"""
    try:
        # Get the orchestrator graph
        orchestrator = get_specialized_graph("project_orchestrator")
        if not orchestrator:
            raise HTTPException(status_code=404, detail="Project Orchestrator not available")

        # Create orchestration state
        initial_state = {
            "project_context": request.get("project_context", {}),
            "messages": [HumanMessage(content=request.get("query", ""))],
            "agent_type": "project_orchestrator"
        }

        # Execute orchestration
        config = {
            "configurable": {
                "enable_tracing": request.get("enable_tracing", True),
                "max_iterations": request.get("max_iterations", 3)
            }
        }

        orchestration_result = await orchestrator.ainvoke(initial_state, config=config)

        # Execute individual graphs based on orchestration plan
        execution_results = {}
        coordination_plan = orchestration_result.get("coordination_plan", {})
        active_graphs = orchestration_result.get("active_graphs", [])

        for graph_id in active_graphs:
            try:
                graph = get_specialized_graph(graph_id)
                if graph:
                    graph_state = {
                        **request.get("graph_inputs", {}).get(graph_id, {}),
                        "messages": [HumanMessage(content=request.get("query", ""))],
                        "agent_type": graph_id
                    }

                    graph_result = await graph.ainvoke(graph_state, config=config)
                    execution_results[graph_id] = {
                        "success": True,
                        "result": graph_result
                    }
                else:
                    execution_results[graph_id] = {
                        "success": False,
                        "error": f"Graph '{graph_id}' not available"
                    }
            except Exception as e:
                execution_results[graph_id] = {
                    "success": False,
                    "error": str(e)
                }

        return {
            "success": True,
            "orchestration_result": orchestration_result,
            "coordination_plan": coordination_plan,
            "graph_results": execution_results,
            "total_graphs_executed": len(execution_results),
            "successful_executions": len([r for r in execution_results.values() if r["success"]])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")


@router.get("/graphs/{graph_id}/metadata")
async def get_graph_metadata(graph_id: str):
    """Get metadata for a specific graph"""
    try:
        registry = get_graph_registry()
        metadata = registry.get_graph_metadata(graph_id)

        if not metadata:
            raise HTTPException(status_code=404, detail=f"Graph '{graph_id}' not found")

        return {
            "success": True,
            "graph_id": graph_id,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")


@router.get("/graphs/health")
async def get_graphs_health():
    """Get health status of all specialized graphs"""
    try:
        registry = get_graph_registry()
        health_status = registry.get_health_status()

        return {
            "success": True,
            "health_status": health_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/health")
async def specialized_health():
    """Get health status of the specialized agent system"""
    try:
        health_data = await langsmith_monitor.get_system_health()

        return {
            "status": health_data.get("status", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "agents": health_data.get("agents", {}),
            "workflow": health_data.get("workflow", {}),
            "langsmith_connected": health_data.get("langsmith_connected", False)
        }

    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/metrics/agents")
async def get_agent_metrics(time_range_hours: int = 24):
    """Get performance metrics for all specialized agents"""
    try:
        metrics = {}

        # Mock metrics for now - in production, these would come from LangSmith
        agents = ["research_agent", "analysis_agent", "synthesis_agent"]

        for agent in agents:
            metrics[agent] = {
                "total_executions": 150,
                "success_rate": 95.5,
                "avg_execution_time": 12.3,
                "avg_quality_score": 4.2,
                "last_execution": datetime.now().isoformat()
            }

        return {
            "metrics": metrics,
            "time_range_hours": time_range_hours,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent metrics: {str(e)}")


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for a specific workflow execution"""
    try:
        # In production, this would store feedback in a database
        # and potentially trigger model retraining

        feedback_data = {
            "trace_id": request.trace_id,
            "rating": request.rating,
            "comment": request.comment,
            "user_id": request.user_id,
            "timestamp": datetime.now().isoformat()
        }

        # Log feedback (in production, save to database)
        print(f"📝 Feedback received: {feedback_data}")

        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": f"fb_{datetime.now().timestamp()}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Check agent initialization status
        agents_status = {
            "research_agent": True,  # Mock status
            "analysis_agent": True,
            "synthesis_agent": True,
            "coordinator_agent": True,
            "code_engineer": True,
            "project_manager": True,
            "qa_specialist": True
        }

        # Get recent workflow metrics
        recent_metrics = await langsmith_monitor.get_workflow_metrics(1)  # Last hour

        return {
            "system_status": "operational" if all(agents_status.values()) else "initializing",
            "agents_initialized": agents_status,
            "langsmith_connected": langsmith_monitor.client is not None,
            "recent_activity": {
                "workflows_last_hour": recent_metrics.get("total_workflows", 0),
                "success_rate": recent_metrics.get("success_rate", 0),
                "avg_quality": recent_metrics.get("avg_quality_score", 0)
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "system_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/test")
async def test_specialized_system():
    """Test the basic specialized agent system with a simple query"""
    try:
        test_query = "What is artificial intelligence?"

        # Run a simple test using the basic 3-agent system
        result = await run_specialized_workflow(test_query, {})

        return {
            "test_status": "success",
            "test_query": test_query,
            "agent_system": result.get("agent_system", "basic"),
            "response_length": len(result["final_answer"]),
            "quality_score": result["quality_score"],
            "workflow_complete": result["workflow_complete"],
            "execution_time": result["execution_metrics"].get("total_execution_time", 0),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "test_status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/test-real-agents")
async def test_real_specialized_system():
    """Test the REAL specialized agent system with ii-agent logic"""
    try:
        test_query = "What are the latest developments in artificial intelligence and machine learning?"

        # Run a test using the REAL specialized agent system
        result = await run_true_specialized_workflow(test_query, {})

        return {
            "test_status": "success",
            "test_query": test_query,
            "agent_system": result.get("agent_system", "true_specialized"),
            "response_length": len(result["final_answer"]),
            "quality_score": result["quality_score"],
            "workflow_complete": result["workflow_complete"],
            "citations_count": len(result.get("citations", [])),
            "execution_time": result["execution_metrics"].get("total_execution_time", 0),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "test_status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/test-multi-agent")
async def test_multi_agent_system():
    """Test the multi-agent system with a complex query"""
    try:
        test_query = "Create a project plan for developing a web application with quality assurance"

        # Run a test using the 4-agent system
        result = await run_multi_agent_workflow(test_query, {})

        return {
            "test_status": "success",
            "test_query": test_query,
            "response_length": len(result["final_answer"]),
            "quality_score": result["quality_score"],
            "workflow_complete": result["workflow_complete"],
            "agents_used": result["execution_metrics"].get("total_agents_used", 0),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "test_status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def log_workflow_execution(query: str, result: Dict[str, Any], user_id: Optional[str]):
    """Log workflow execution for monitoring and analytics"""
    try:
        log_data = {
            "query": query,
            "user_id": user_id,
            "quality_score": result.get("quality_score", 0),
            "execution_time": result.get("execution_metrics", {}).get("total_execution_time", 0),
            "workflow_complete": result.get("workflow_complete", False),
            "fallback_used": result.get("fallback_used", False),
            "timestamp": datetime.now().isoformat()
        }

        # In production, this would be sent to a logging service
        print(f"📊 Workflow logged: {log_data}")

    except Exception as e:
        print(f"❌ Failed to log workflow: {e}")
