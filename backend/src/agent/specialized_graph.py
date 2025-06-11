"""
Real Specialized Graph Implementation

Implements the real specialized agent architecture with LangSmith tracing.
Coordinates Research, Analysis, and Synthesis agents with proper handoffs.
"""

import os
from typing import Dict, Any, Literal
from datetime import datetime

from langsmith import traceable
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

from .specialized_state import (
    SpecializedState,
    WorkflowStage,
    create_initial_state,
    update_state_with_research,
    update_state_with_analysis,
    update_state_with_synthesis,
    calculate_overall_quality,
    get_execution_metrics,
    add_error_to_state,
    should_continue_research_iteration,
    prepare_research_continuation
)
from .multi_agent_state import MultiAgentState, run_multi_agent_workflow
from .router import agent_router, AgentType
from .configuration import Configuration


# Global agent instances (initialized once)
research_agent = None
analysis_agent = None
synthesis_agent = None


def initialize_agents(config: RunnableConfig = None):
    """Initialize specialized agents with configuration"""
    global research_agent, analysis_agent, synthesis_agent

    if research_agent is None:
        from .specialized_agents.research_agent import ResearchAgent
        research_agent = ResearchAgent(config)
        print("✅ Research Agent initialized")

    if analysis_agent is None:
        from .specialized_agents.analysis_agent import AnalysisAgent
        analysis_agent = AnalysisAgent(config)
        print("✅ Analysis Agent initialized")

    if synthesis_agent is None:
        from .specialized_agents.synthesis_agent import SynthesisAgent
        synthesis_agent = SynthesisAgent(config)
        print("✅ Synthesis Agent initialized")


@traceable(name="route_specialized_task")
def route_specialized_task(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Route the initial task and classify the query type.

    This node determines the workflow path and initializes agents.
    """
    try:
        print(f"🎯 Routing task: {state['original_query'][:100]}...")

        # Initialize agents if needed
        initialize_agents(config)

        # Use the existing router to classify the task
        agent_type = agent_router(state["original_query"])

        # Update state with routing information
        task_classification = {
            "agent_type": agent_type.value,
            "confidence": 0.9,  # High confidence in routing
            "timestamp": datetime.now().isoformat()
        }

        return {
            **state,
            "agent_type": agent_type.value,
            "task_classification": task_classification,
            "workflow_stage": WorkflowStage.RESEARCH,
            "current_agent": "router"
        }

    except Exception as e:
        print(f"❌ Routing failed: {e}")
        error_updates = add_error_to_state(state, e, "router")
        return {**state, **error_updates}


@traceable(name="research_agent_node")
def research_agent_node(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Execute research phase with web search and data gathering.

    This agent performs comprehensive research based on the query.
    """
    try:
        print(f"🔍 Research Agent processing query...")

        # Initialize agents if needed
        initialize_agents(config)

        # Use the original graph's research capabilities
        from .graph import generate_query, web_research

        # Generate research queries
        query_state = {"messages": state["messages"]}
        query_result = generate_query(query_state, config)

        # Perform web research
        research_result = web_research(query_result, config)

        # Extract research data
        research_queries = query_result.get("queries", [state["original_query"]])
        research_data = {
            "search_results": research_result.get("search_results", []),
            "sources": research_result.get("sources", []),
            "raw_data": research_result.get("raw_content", "")
        }

        # Create research summary
        research_summary = f"Conducted research on: {', '.join(research_queries[:3])}"
        if len(research_queries) > 3:
            research_summary += f" and {len(research_queries) - 3} more topics"

        # Calculate confidence based on results
        confidence = min(0.9, len(research_data.get("search_results", [])) * 0.1 + 0.3)

        # Update state with research results
        research_updates = update_state_with_research(
            state, research_queries, research_data, research_summary, confidence
        )

        print(f"✅ Research completed with {len(research_data.get('search_results', []))} results")

        return {**state, **research_updates}

    except Exception as e:
        print(f"❌ Research agent failed: {e}")
        error_updates = add_error_to_state(state, e, "research_agent")
        error_updates["fallback_used"] = True
        return {**state, **error_updates}


@traceable(name="analysis_agent_node")
def analysis_agent_node(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Execute analysis phase with knowledge gap identification.

    This agent analyzes research results and determines if more research is needed.
    """
    try:
        print(f"📊 Analysis Agent evaluating research quality...")

        # Initialize agents if needed
        initialize_agents(config)

        # Use the original graph's reflection capabilities
        from .graph import reflection

        # Prepare state for reflection
        reflection_state = {
            "messages": state["messages"],
            "search_results": state.get("research_data", {}).get("search_results", [])
        }

        # Perform reflection/analysis
        reflection_result = reflection(reflection_state, config)

        # Extract analysis data
        analysis_data = {
            "reflection_summary": reflection_result.get("reflection", ""),
            "search_quality": reflection_result.get("search_quality", "good"),
            "information_gaps": reflection_result.get("information_gaps", [])
        }

        # Determine knowledge gaps and follow-up queries
        knowledge_gaps = analysis_data.get("information_gaps", [])
        follow_up_queries = []

        # Simple logic to determine if more research is needed
        current_iteration = state.get("research_iteration", 0)
        max_iterations = state.get("max_research_iterations", 3)
        search_quality = analysis_data.get("search_quality", "good")

        should_continue = (
            current_iteration < max_iterations and
            search_quality in ["poor", "needs_improvement"] and
            len(knowledge_gaps) > 0
        )

        if should_continue:
            follow_up_queries = knowledge_gaps[:2]  # Limit follow-up queries

        # Calculate confidence
        confidence = 0.8 if search_quality == "good" else 0.6

        # Update state with analysis results
        analysis_updates = update_state_with_analysis(
            state, analysis_data, knowledge_gaps, follow_up_queries, should_continue, confidence
        )

        print(f"✅ Analysis completed - Continue research: {should_continue}")

        return {**state, **analysis_updates}

    except Exception as e:
        print(f"❌ Analysis agent failed: {e}")
        error_updates = add_error_to_state(state, e, "analysis_agent")
        error_updates["fallback_used"] = True
        return {**state, **error_updates}


@traceable(name="synthesis_agent_node")
def synthesis_agent_node(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Execute synthesis phase with final answer generation.

    This agent creates the final comprehensive response with citations.
    """
    try:
        print(f"🔄 Synthesis Agent generating final answer...")

        # Initialize agents if needed
        initialize_agents(config)

        # Use the original graph's finalization capabilities
        from .graph import finalize_answer

        # Prepare state for finalization
        finalize_state = {
            "messages": state["messages"],
            "search_results": state.get("research_data", {}).get("search_results", []),
            "reflection": state.get("analysis_data", {}).get("reflection_summary", "")
        }

        # Generate final answer
        final_result = finalize_answer(finalize_state, config)

        # Extract synthesis data
        synthesis_data = {
            "final_response": final_result.get("final_answer", ""),
            "reasoning": final_result.get("reasoning", ""),
            "sources_used": final_result.get("sources", [])
        }

        # Create citations from sources
        citations = []
        sources = synthesis_data.get("sources_used", [])
        for i, source in enumerate(sources[:5]):  # Limit to 5 citations
            citations.append({
                "source_id": i + 1,
                "title": source.get("title", f"Source {i + 1}"),
                "url": source.get("url", ""),
                "snippet": source.get("snippet", "")[:200],
                "relevance_score": source.get("relevance", 0.8)
            })

        final_answer = synthesis_data.get("final_response", "")
        confidence = 0.9  # High confidence in synthesis

        # Update state with synthesis results
        synthesis_updates = update_state_with_synthesis(
            state, synthesis_data, final_answer, citations, confidence
        )

        # Calculate overall quality
        overall_quality = calculate_overall_quality({**state, **synthesis_updates})
        synthesis_updates["overall_quality_score"] = overall_quality

        print(f"✅ Synthesis completed with quality score: {overall_quality:.2f}")

        return {**state, **synthesis_updates}

    except Exception as e:
        print(f"❌ Synthesis agent failed: {e}")
        error_updates = add_error_to_state(state, e, "synthesis_agent")
        error_updates["fallback_used"] = True
        return {**state, **error_updates}


@traceable(name="evaluate_research_continuation")
def evaluate_research_continuation(state: SpecializedState, config: RunnableConfig) -> Literal["research_agent", "synthesis_agent"]:
    """
    Determine whether to continue research or proceed to synthesis.

    This is the key decision point in the specialized workflow.
    """
    # Check if we should continue research
    if should_continue_research_iteration(state):
        print(f"🔄 Continuing research - iteration {state.get('research_iteration', 0) + 1}")
        return "research_agent"
    else:
        print(f"➡️ Proceeding to synthesis")
        return "synthesis_agent"


@traceable(name="handle_specialized_error")
def handle_specialized_error(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Handle errors in the specialized workflow with fallback responses.
    """
    try:
        print("⚠️ Handling workflow error...")

        # Create a fallback response
        fallback_answer = f"""I encountered an issue while processing your query: "{state['original_query']}"

I was able to gather some information, but the full specialized workflow couldn't complete. Here's what I found:

"""

        # Add any research data we have
        if state.get("research_summary"):
            fallback_answer += f"Research Summary: {state['research_summary']}\n\n"

        # Add any analysis insights
        if state.get("analysis_data"):
            analysis = state["analysis_data"]
            if analysis.get("reflection_summary"):
                fallback_answer += f"Analysis: {analysis['reflection_summary']}\n\n"

        fallback_answer += "Please try rephrasing your question or contact support if the issue persists."

        # Create minimal citations from any sources we have
        citations = []
        research_data = state.get("research_data", {})
        sources = research_data.get("sources", [])
        for i, source in enumerate(sources[:3]):
            citations.append({
                "source_id": i + 1,
                "title": source.get("title", f"Source {i + 1}"),
                "url": source.get("url", ""),
                "snippet": source.get("snippet", "")[:150],
                "relevance_score": 0.5
            })

        return {
            **state,
            "final_answer": fallback_answer,
            "citations": citations,
            "workflow_stage": WorkflowStage.COMPLETE,
            "fallback_used": True,
            "overall_quality_score": 0.3  # Low quality due to error
        }

    except Exception as e:
        print(f"❌ Error handler failed: {e}")
        return {
            **state,
            "final_answer": "I'm sorry, but I encountered a technical error and cannot process your request at this time.",
            "citations": [],
            "workflow_stage": WorkflowStage.ERROR,
            "fallback_used": True,
            "overall_quality_score": 0.1
        }


def build_specialized_graph() -> StateGraph:
    """
    Build the specialized 3-agent graph with LangSmith tracing.

    Workflow:
    1. Route Task -> Determine workflow type
    2. Research Agent -> Gather information
    3. Analysis Agent -> Evaluate and identify gaps
    4. Decision Point -> Continue research or proceed to synthesis
    5. Synthesis Agent -> Generate final answer
    6. Error Handling -> Fallback responses

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph builder
    builder = StateGraph(SpecializedState)

    # Add nodes
    builder.add_node("route_task", route_specialized_task)
    builder.add_node("research_agent", research_agent_node)
    builder.add_node("analysis_agent", analysis_agent_node)
    builder.add_node("synthesis_agent", synthesis_agent_node)
    builder.add_node("handle_error", handle_specialized_error)

    # Set entry point
    builder.add_edge(START, "route_task")

    # Main workflow edges
    builder.add_edge("route_task", "research_agent")
    builder.add_edge("research_agent", "analysis_agent")

    # Conditional edge for research continuation
    builder.add_conditional_edges(
        "analysis_agent",
        evaluate_research_continuation,
        {
            "research_agent": "research_agent",
            "synthesis_agent": "synthesis_agent"
        }
    )

    # Final edges
    builder.add_edge("synthesis_agent", END)
    builder.add_edge("handle_error", END)

    # Compile the graph
    graph = builder.compile(name="specialized-3-agent-system")

    print("✅ Specialized 3-agent graph compiled successfully")
    print("📊 Graph structure:")
    print("   Route Task → Research Agent → Analysis Agent")
    print("                     ↑              ↓")
    print("                     └── Continue? ──┘")
    print("                                    ↓")
    print("                              Synthesis Agent")

    return graph
