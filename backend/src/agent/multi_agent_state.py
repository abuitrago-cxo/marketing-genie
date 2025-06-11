"""
Multi-Agent State Management

Enhanced state schema for the 4-agent specialization system.
Manages complex workflows between Coordinator, Research, Code Engineer,
Project Manager, and QA Specialist agents.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated, Union
from datetime import datetime
from enum import Enum

from langchain_core.messages import BaseMessage


class TaskType(Enum):
    """Task classification types"""
    RESEARCH = "research"
    CODE_DEVELOPMENT = "code_development"
    PROJECT_MANAGEMENT = "project_management"
    QUALITY_ASSURANCE = "quality_assurance"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


class WorkflowStage(Enum):
    """Workflow execution stages"""
    COORDINATION = "coordination"
    RESEARCH = "research"
    CODE_ENGINEERING = "code_engineering"
    PROJECT_MANAGEMENT = "project_management"
    QUALITY_ASSURANCE = "quality_assurance"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"
    ERROR = "error"


class MultiAgentState(TypedDict):
    """
    Enhanced state schema for the multi-agent system.

    Tracks complex workflows across multiple specialized agents
    with comprehensive coordination and quality metrics.
    """

    # Core workflow data
    messages: Annotated[List[BaseMessage], "Conversation messages"]
    original_query: str
    task_type: TaskType
    task_classification: Optional[Dict[str, Any]]

    # Coordinator Agent data
    coordinator_data: Optional[Dict[str, Any]]
    task_breakdown: Optional[List[Dict[str, Any]]]
    agent_assignments: Optional[Dict[str, List[str]]]
    workflow_plan: Optional[Dict[str, Any]]
    coordinator_status: AgentStatus

    # Research Specialist data
    research_queries: Optional[List[str]]
    research_data: Optional[Dict[str, Any]]
    research_summary: Optional[str]
    research_confidence: Optional[float]
    research_status: AgentStatus

    # Code Engineer data
    code_analysis: Optional[Dict[str, Any]]
    code_generation: Optional[Dict[str, Any]]
    test_results: Optional[Dict[str, Any]]
    documentation: Optional[Dict[str, Any]]
    code_engineer_status: AgentStatus

    # Project Manager data
    project_plan: Optional[Dict[str, Any]]
    resource_allocation: Optional[Dict[str, Any]]
    timeline: Optional[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    project_manager_status: AgentStatus

    # QA Specialist data
    quality_assessment: Optional[Dict[str, Any]]
    test_coverage: Optional[Dict[str, Any]]
    security_analysis: Optional[Dict[str, Any]]
    performance_metrics: Optional[Dict[str, Any]]
    qa_specialist_status: AgentStatus

    # Synthesis data
    synthesis_data: Optional[Dict[str, Any]]
    final_answer: Optional[str]
    citations: Optional[List[Dict[str, Any]]]
    deliverables: Optional[List[Dict[str, Any]]]

    # Workflow control
    current_agent: Optional[str]
    workflow_stage: WorkflowStage
    active_tasks: Optional[List[Dict[str, Any]]]
    completed_tasks: Optional[List[Dict[str, Any]]]

    # Quality and performance metrics
    overall_quality_score: Optional[float]
    execution_metrics: Optional[Dict[str, Any]]
    agent_performance: Optional[Dict[str, Dict[str, Any]]]

    # Error handling and recovery
    errors: Optional[List[Dict[str, Any]]]
    fallback_used: Optional[bool]
    recovery_attempts: Optional[int]

    # Configuration
    reasoning_model: Optional[str]
    enable_tracing: Optional[bool]
    max_concurrent_agents: Optional[int]
    timeout_seconds: Optional[int]


def create_initial_state(
    messages: List[BaseMessage],
    query: str,
    reasoning_model: str = "gemini-1.5-pro",
    enable_tracing: bool = True,
    max_concurrent_agents: int = 3,
    timeout_seconds: int = 300
) -> MultiAgentState:
    """
    Create initial state for multi-agent workflow.

    Args:
        messages: Initial conversation messages
        query: User query to process
        reasoning_model: LLM model to use
        enable_tracing: Whether to enable LangSmith tracing
        max_concurrent_agents: Maximum agents running concurrently
        timeout_seconds: Timeout for agent execution

    Returns:
        Initial MultiAgentState with basic setup
    """
    return MultiAgentState(
        # Core data
        messages=messages,
        original_query=query,
        task_type=TaskType.UNKNOWN,
        task_classification=None,

        # Agent data initialization
        coordinator_data=None,
        task_breakdown=None,
        agent_assignments=None,
        workflow_plan=None,
        coordinator_status=AgentStatus.IDLE,

        research_queries=None,
        research_data=None,
        research_summary=None,
        research_confidence=None,
        research_status=AgentStatus.IDLE,

        code_analysis=None,
        code_generation=None,
        test_results=None,
        documentation=None,
        code_engineer_status=AgentStatus.IDLE,

        project_plan=None,
        resource_allocation=None,
        timeline=None,
        risk_assessment=None,
        project_manager_status=AgentStatus.IDLE,

        quality_assessment=None,
        test_coverage=None,
        security_analysis=None,
        performance_metrics=None,
        qa_specialist_status=AgentStatus.IDLE,

        # Synthesis data
        synthesis_data=None,
        final_answer=None,
        citations=None,
        deliverables=None,

        # Workflow control
        current_agent=None,
        workflow_stage=WorkflowStage.COORDINATION,
        active_tasks=[],
        completed_tasks=[],

        # Quality metrics
        overall_quality_score=None,
        execution_metrics={
            "start_time": datetime.now().isoformat(),
            "total_agents_used": 0,
            "coordinator_used": False,
            "research_used": False,
            "code_engineer_used": False,
            "project_manager_used": False,
            "qa_specialist_used": False,
            "error_count": 0,
            "recovery_count": 0
        },
        agent_performance={},

        # Error handling
        errors=[],
        fallback_used=False,
        recovery_attempts=0,

        # Configuration
        reasoning_model=reasoning_model,
        enable_tracing=enable_tracing,
        max_concurrent_agents=max_concurrent_agents,
        timeout_seconds=timeout_seconds
    )


def update_agent_status(
    state: MultiAgentState,
    agent_name: str,
    status: AgentStatus,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Update specific agent status and data"""
    updates = {}

    # Update agent status
    status_key = f"{agent_name}_status"
    updates[status_key] = status

    # Update agent data if provided
    if data:
        data_key = f"{agent_name}_data"
        if agent_name == "coordinator":
            updates["coordinator_data"] = data
        elif agent_name == "research":
            updates.update({
                "research_queries": data.get("queries"),
                "research_data": data.get("research_data"),
                "research_summary": data.get("summary"),
                "research_confidence": data.get("confidence")
            })
        elif agent_name == "code_engineer":
            updates.update({
                "code_analysis": data.get("analysis"),
                "code_generation": data.get("generation"),
                "test_results": data.get("tests"),
                "documentation": data.get("documentation")
            })
        elif agent_name == "project_manager":
            updates.update({
                "project_plan": data.get("plan"),
                "resource_allocation": data.get("resources"),
                "timeline": data.get("timeline"),
                "risk_assessment": data.get("risks")
            })
        elif agent_name == "qa_specialist":
            updates.update({
                "quality_assessment": data.get("quality"),
                "test_coverage": data.get("coverage"),
                "security_analysis": data.get("security"),
                "performance_metrics": data.get("performance")
            })

    # Update execution metrics
    execution_metrics = state.get("execution_metrics", {})
    if status == AgentStatus.ACTIVE:
        execution_metrics[f"{agent_name}_used"] = True
        execution_metrics["total_agents_used"] = execution_metrics.get("total_agents_used", 0) + 1

    updates["execution_metrics"] = execution_metrics
    updates["current_agent"] = agent_name

    return updates


def add_task_to_workflow(
    state: MultiAgentState,
    task: Dict[str, Any]
) -> Dict[str, Any]:
    """Add a new task to the active workflow"""
    active_tasks = state.get("active_tasks", [])
    active_tasks.append({
        **task,
        "id": f"task_{len(active_tasks) + 1}",
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    })

    return {"active_tasks": active_tasks}


def complete_task(
    state: MultiAgentState,
    task_id: str,
    result: Dict[str, Any]
) -> Dict[str, Any]:
    """Mark a task as completed and move to completed tasks"""
    active_tasks = state.get("active_tasks", [])
    completed_tasks = state.get("completed_tasks", [])

    # Find and remove task from active
    task_to_complete = None
    for i, task in enumerate(active_tasks):
        if task.get("id") == task_id:
            task_to_complete = active_tasks.pop(i)
            break

    if task_to_complete:
        # Add to completed with result
        task_to_complete.update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "result": result
        })
        completed_tasks.append(task_to_complete)

    return {
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks
    }


def calculate_overall_quality(state: MultiAgentState) -> float:
    """Calculate overall quality score based on all agent outputs"""
    quality_scores = []

    # Research quality
    if state.get("research_confidence"):
        quality_scores.append(state["research_confidence"])

    # Code quality (based on test results and documentation)
    code_quality = 0.0
    if state.get("test_results"):
        code_quality += 0.4  # Base score for having tests
        if state["test_results"].get("coverage", 0) > 0.8:
            code_quality += 0.3  # High coverage bonus
    if state.get("documentation"):
        code_quality += 0.3  # Documentation bonus
    if code_quality > 0:
        quality_scores.append(code_quality)

    # Project management quality
    if state.get("project_plan") and state.get("timeline"):
        pm_quality = 0.8  # Base score for having plan and timeline
        if state.get("risk_assessment"):
            pm_quality += 0.2  # Risk assessment bonus
        quality_scores.append(pm_quality)

    # QA quality
    if state.get("quality_assessment"):
        qa_score = state["quality_assessment"].get("score", 0.7)
        quality_scores.append(qa_score)

    return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0


def get_execution_metrics(state: MultiAgentState) -> Dict[str, Any]:
    """Get comprehensive execution metrics"""
    metrics = state.get("execution_metrics", {})

    # Calculate execution time if available
    start_time = metrics.get("start_time")
    if start_time:
        start_dt = datetime.fromisoformat(start_time)
        current_time = datetime.now()
        execution_time = (current_time - start_dt).total_seconds()
        metrics["current_execution_time"] = execution_time

    # Add quality score
    metrics["overall_quality"] = calculate_overall_quality(state)

    # Add workflow stage
    metrics["workflow_stage"] = state.get("workflow_stage", WorkflowStage.COORDINATION).value

    # Add task counts
    metrics["active_task_count"] = len(state.get("active_tasks", []))
    metrics["completed_task_count"] = len(state.get("completed_tasks", []))

    # Add agent status summary
    agent_statuses = {
        "coordinator": state.get("coordinator_status", AgentStatus.IDLE).value,
        "research": state.get("research_status", AgentStatus.IDLE).value,
        "code_engineer": state.get("code_engineer_status", AgentStatus.IDLE).value,
        "project_manager": state.get("project_manager_status", AgentStatus.IDLE).value,
        "qa_specialist": state.get("qa_specialist_status", AgentStatus.IDLE).value
    }
    metrics["agent_statuses"] = agent_statuses

    return metrics


def add_error_to_state(
    state: MultiAgentState,
    error: Exception,
    agent: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Add error information to state with recovery context"""
    error_info = {
        "agent": agent,
        "error": str(error),
        "timestamp": datetime.now().isoformat(),
        "type": type(error).__name__,
        "context": context or {}
    }

    errors = state.get("errors", [])
    errors.append(error_info)

    execution_metrics = state.get("execution_metrics", {})
    execution_metrics["error_count"] = execution_metrics.get("error_count", 0) + 1

    return {
        "errors": errors,
        "execution_metrics": execution_metrics,
        "workflow_stage": WorkflowStage.ERROR
    }


async def run_multi_agent_workflow(
    query: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute the multi-agent workflow.

    This is a placeholder function that will be implemented
    in the specialized_graph.py file.
    """
    from .specialized_graph import build_specialized_graph

    # Build and execute the graph
    graph = build_specialized_graph()

    # Create initial state
    from langchain_core.messages import HumanMessage
    messages = [HumanMessage(content=query)]
    initial_state = create_initial_state(messages, query)

    # Execute workflow
    result = await graph.ainvoke(initial_state, config=config)

    return {
        "final_answer": result.get("final_answer", ""),
        "citations": result.get("citations", []),
        "quality_score": calculate_overall_quality(result),
        "execution_metrics": get_execution_metrics(result),
        "workflow_complete": result.get("workflow_stage") == WorkflowStage.COMPLETE,
        "fallback_used": result.get("fallback_used", False)
    }
