"""
Real Specialized State Management

State schema for the real specialized agent architecture.
Manages data flow between Research, Analysis, and Synthesis agents.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime

from langchain_core.messages import BaseMessage


class SpecializedState(TypedDict):
    """
    State schema for the specialized 3-agent system.

    This state tracks the complete workflow from initial query through
    research, analysis, and final synthesis with full traceability.
    """

    # Core workflow data
    messages: Annotated[List[BaseMessage], "Conversation messages"]
    original_query: str
    agent_type: str
    task_classification: Optional[Dict[str, Any]]

    # Research Agent data
    research_queries: Optional[List[str]]
    research_data: Optional[Dict[str, Any]]
    research_summary: Optional[str]
    research_confidence: Optional[float]
    research_timestamp: Optional[str]

    # Analysis Agent data
    analysis_data: Optional[Dict[str, Any]]
    knowledge_gaps: Optional[List[str]]
    follow_up_queries: Optional[List[str]]
    should_continue_research: Optional[bool]
    analysis_confidence: Optional[float]
    analysis_timestamp: Optional[str]

    # Synthesis Agent data
    synthesis_data: Optional[Dict[str, Any]]
    final_answer: Optional[str]
    citations: Optional[List[Dict[str, Any]]]
    synthesis_confidence: Optional[float]
    synthesis_timestamp: Optional[str]

    # Workflow control
    current_agent: Optional[str]
    workflow_stage: Optional[str]  # "research", "analysis", "synthesis", "complete"
    research_iteration: Optional[int]
    max_research_iterations: Optional[int]

    # Quality metrics
    overall_quality_score: Optional[float]
    execution_metrics: Optional[Dict[str, Any]]

    # Error handling
    errors: Optional[List[Dict[str, Any]]]
    fallback_used: Optional[bool]

    # Configuration
    reasoning_model: Optional[str]
    enable_tracing: Optional[bool]


class WorkflowStage:
    """Workflow stage constants"""
    ROUTING = "routing"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"
    ERROR = "error"


def create_initial_state(
    messages: List[BaseMessage],
    query: str,
    max_iterations: int = 3,
    reasoning_model: str = "gemini-1.5-pro",
    enable_tracing: bool = True
) -> SpecializedState:
    """
    Create initial state for specialized workflow.

    Args:
        messages: Initial conversation messages
        query: User query to process
        max_iterations: Maximum research iterations
        reasoning_model: LLM model to use
        enable_tracing: Whether to enable LangSmith tracing

    Returns:
        Initial SpecializedState with basic setup
    """
    return SpecializedState(
        # Core data
        messages=messages,
        original_query=query,
        agent_type="",
        task_classification=None,

        # Research data
        research_queries=None,
        research_data=None,
        research_summary=None,
        research_confidence=None,
        research_timestamp=None,

        # Analysis data
        analysis_data=None,
        knowledge_gaps=None,
        follow_up_queries=None,
        should_continue_research=None,
        analysis_confidence=None,
        analysis_timestamp=None,

        # Synthesis data
        synthesis_data=None,
        final_answer=None,
        citations=None,
        synthesis_confidence=None,
        synthesis_timestamp=None,

        # Workflow control
        current_agent=None,
        workflow_stage=WorkflowStage.ROUTING,
        research_iteration=0,
        max_research_iterations=max_iterations,

        # Quality metrics
        overall_quality_score=None,
        execution_metrics={
            "start_time": datetime.now().isoformat(),
            "total_agents_used": 0,
            "has_research": False,
            "has_analysis": False,
            "has_synthesis": False,
            "error_count": 0
        },

        # Error handling
        errors=[],
        fallback_used=False,

        # Configuration
        reasoning_model=reasoning_model,
        enable_tracing=enable_tracing
    )


def update_state_with_research(
    state: SpecializedState,
    queries: List[str],
    research_data: Dict[str, Any],
    summary: str,
    confidence: float
) -> Dict[str, Any]:
    """Update state with research results"""
    return {
        "research_queries": queries,
        "research_data": research_data,
        "research_summary": summary,
        "research_confidence": confidence,
        "research_timestamp": datetime.now().isoformat(),
        "current_agent": "research",
        "workflow_stage": WorkflowStage.RESEARCH,
        "execution_metrics": {
            **state.get("execution_metrics", {}),
            "has_research": True,
            "total_agents_used": state.get("execution_metrics", {}).get("total_agents_used", 0) + 1
        }
    }


def update_state_with_analysis(
    state: SpecializedState,
    analysis_data: Dict[str, Any],
    knowledge_gaps: List[str],
    follow_up_queries: List[str],
    should_continue: bool,
    confidence: float
) -> Dict[str, Any]:
    """Update state with analysis results"""
    return {
        "analysis_data": analysis_data,
        "knowledge_gaps": knowledge_gaps,
        "follow_up_queries": follow_up_queries,
        "should_continue_research": should_continue,
        "analysis_confidence": confidence,
        "analysis_timestamp": datetime.now().isoformat(),
        "current_agent": "analysis",
        "workflow_stage": WorkflowStage.ANALYSIS,
        "execution_metrics": {
            **state.get("execution_metrics", {}),
            "has_analysis": True,
            "total_agents_used": state.get("execution_metrics", {}).get("total_agents_used", 0) + 1
        }
    }


def update_state_with_synthesis(
    state: SpecializedState,
    synthesis_data: Dict[str, Any],
    final_answer: str,
    citations: List[Dict[str, Any]],
    confidence: float
) -> Dict[str, Any]:
    """Update state with synthesis results"""
    return {
        "synthesis_data": synthesis_data,
        "final_answer": final_answer,
        "citations": citations,
        "synthesis_confidence": confidence,
        "synthesis_timestamp": datetime.now().isoformat(),
        "current_agent": "synthesis",
        "workflow_stage": WorkflowStage.COMPLETE,
        "execution_metrics": {
            **state.get("execution_metrics", {}),
            "has_synthesis": True,
            "total_agents_used": state.get("execution_metrics", {}).get("total_agents_used", 0) + 1,
            "end_time": datetime.now().isoformat()
        }
    }


def calculate_overall_quality(state: SpecializedState) -> float:
    """Calculate overall quality score based on agent confidences"""
    confidences = []

    if state.get("research_confidence"):
        confidences.append(state["research_confidence"])
    if state.get("analysis_confidence"):
        confidences.append(state["analysis_confidence"])
    if state.get("synthesis_confidence"):
        confidences.append(state["synthesis_confidence"])

    if not confidences:
        return 0.0

    return sum(confidences) / len(confidences)


def get_execution_metrics(state: SpecializedState) -> Dict[str, Any]:
    """Get comprehensive execution metrics"""
    metrics = state.get("execution_metrics", {})

    # Calculate execution time if available
    start_time = metrics.get("start_time")
    end_time = metrics.get("end_time")

    if start_time and end_time:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        execution_time = (end_dt - start_dt).total_seconds()
        metrics["total_execution_time"] = execution_time

    # Add quality score
    metrics["overall_quality"] = calculate_overall_quality(state)

    # Add workflow stage
    metrics["workflow_stage"] = state.get("workflow_stage", "unknown")

    # Add research iterations
    metrics["research_iterations"] = state.get("research_iteration", 0)

    # Add fallback status
    metrics["fallback_used"] = state.get("fallback_used", False)

    return metrics


def add_error_to_state(state: SpecializedState, error: Exception, agent: str) -> Dict[str, Any]:
    """Add error information to state"""
    error_info = {
        "agent": agent,
        "error": str(error),
        "timestamp": datetime.now().isoformat(),
        "type": type(error).__name__
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


def should_continue_research_iteration(state: SpecializedState) -> bool:
    """Determine if research should continue based on analysis"""
    current_iteration = state.get("research_iteration", 0)
    max_iterations = state.get("max_research_iterations", 3)
    should_continue = state.get("should_continue_research", False)

    return should_continue and current_iteration < max_iterations


def prepare_research_continuation(state: SpecializedState) -> Dict[str, Any]:
    """Prepare state for research continuation"""
    return {
        "research_iteration": state.get("research_iteration", 0) + 1,
        "workflow_stage": WorkflowStage.RESEARCH
    }
