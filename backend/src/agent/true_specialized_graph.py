"""
True Specialized Graph Implementation

This module implements the REAL specialized agent system using the actual
ResearchAgent, AnalysisAgent, and SynthesisAgent classes with logic extracted
from ii-agent and deepseekai.

This is the correct implementation that uses the specialized agent classes
instead of simple LangGraph nodes.
"""

import os
from typing import Dict, Any, Literal
from datetime import datetime

from langsmith import traceable
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

from .specialized_state import (
    SpecializedState, 
    create_initial_state,
    update_state_with_research,
    update_state_with_analysis, 
    update_state_with_synthesis,
    calculate_overall_quality,
    should_continue_research_iteration,
    add_error_to_state
)

# Global agent instances
research_agent = None
analysis_agent = None
synthesis_agent = None


def initialize_specialized_agents(config: RunnableConfig = None):
    """Initialize the real specialized agent classes"""
    global research_agent, analysis_agent, synthesis_agent
    
    if research_agent is None:
        from .specialized_agents.research_agent import ResearchAgent
        research_agent = ResearchAgent(config)
        print("✅ ResearchAgent (Real) initialized")
    
    if analysis_agent is None:
        from .specialized_agents.analysis_agent import AnalysisAgent
        analysis_agent = AnalysisAgent(config)
        print("✅ AnalysisAgent (Real) initialized")
    
    if synthesis_agent is None:
        from .specialized_agents.synthesis_agent import SynthesisAgent
        synthesis_agent = SynthesisAgent(config)
        print("✅ SynthesisAgent (Real) initialized")


@traceable(name="route_specialized_task")
def route_specialized_task(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """Route the task to the specialized workflow"""
    print(f"🎯 Routing task to specialized 3-agent system...")
    
    updated_state = state.copy()
    updated_state.update({
        "workflow_stage": "routing",
        "current_agent": "router",
        "research_iteration": 0
    })
    
    return updated_state


@traceable(name="true_research_agent_node")
async def true_research_agent_node(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Research Agent Node - Uses the REAL ResearchAgent class with ii-agent logic
    """
    try:
        print(f"🔍 ResearchAgent (Real) processing query...")
        
        # Initialize the real specialized agents
        initialize_specialized_agents(config)
        
        # Use the REAL ResearchAgent class
        result = await research_agent.execute(state)
        
        # Update state with research results
        updated_state = state.copy()
        updated_state.update(result)
        updated_state.update({
            "current_agent": "research_agent",
            "workflow_stage": "research"
        })
        
        confidence = result.get('research_confidence', 0)
        print(f"✅ ResearchAgent (Real) completed - confidence: {confidence:.2f}")
        return updated_state
        
    except Exception as e:
        print(f"❌ ResearchAgent (Real) failed: {e}")
        error_updates = add_error_to_state(state, e, "research_agent")
        error_updates["fallback_used"] = True
        return {**state, **error_updates}


@traceable(name="true_analysis_agent_node")
async def true_analysis_agent_node(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Analysis Agent Node - Uses the REAL AnalysisAgent class with gap analysis logic
    """
    try:
        print(f"📊 AnalysisAgent (Real) evaluating research quality...")
        
        # Initialize the real specialized agents
        initialize_specialized_agents(config)
        
        # Use the REAL AnalysisAgent class
        result = await analysis_agent.execute(state)
        
        # Update state with analysis results
        updated_state = state.copy()
        updated_state.update(result)
        updated_state.update({
            "current_agent": "analysis_agent",
            "workflow_stage": "analysis"
        })
        
        should_continue = result.get('should_continue_research', False)
        print(f"✅ AnalysisAgent (Real) completed - Continue research: {should_continue}")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ AnalysisAgent (Real) failed: {e}")
        error_updates = add_error_to_state(state, e, "analysis_agent")
        error_updates["fallback_used"] = True
        return {**state, **error_updates}


@traceable(name="true_synthesis_agent_node")
async def true_synthesis_agent_node(state: SpecializedState, config: RunnableConfig) -> SpecializedState:
    """
    Synthesis Agent Node - Uses the REAL SynthesisAgent class with citation logic
    """
    try:
        print(f"🔄 SynthesisAgent (Real) generating final answer...")
        
        # Initialize the real specialized agents
        initialize_specialized_agents(config)
        
        # Use the REAL SynthesisAgent class
        result = await synthesis_agent.execute(state)
        
        # Update state with synthesis results
        updated_state = state.copy()
        updated_state.update(result)
        updated_state.update({
            "current_agent": "synthesis_agent",
            "workflow_stage": "complete"
        })
        
        # Calculate overall quality
        overall_quality = calculate_overall_quality(updated_state)
        updated_state["overall_quality_score"] = overall_quality
        
        print(f"✅ SynthesisAgent (Real) completed with quality score: {overall_quality:.2f}")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ SynthesisAgent (Real) failed: {e}")
        error_updates = add_error_to_state(state, e, "synthesis_agent")
        error_updates["fallback_used"] = True
        return {**state, **error_updates}


@traceable(name="evaluate_true_research_continuation")
def evaluate_true_research_continuation(state: SpecializedState, config: RunnableConfig) -> Literal["true_research_agent", "true_synthesis_agent"]:
    """
    Determine whether to continue research or proceed to synthesis using real agent logic
    """
    # Use the real logic from the AnalysisAgent
    if should_continue_research_iteration(state):
        print(f"🔄 Continuing research - iteration {state.get('research_iteration', 0) + 1}")
        return "true_research_agent"
    else:
        print(f"➡️ Proceeding to synthesis")
        return "true_synthesis_agent"


def build_true_specialized_graph() -> StateGraph:
    """
    Build the TRUE specialized 3-agent graph using REAL agent classes.
    
    This uses the actual ResearchAgent, AnalysisAgent, and SynthesisAgent classes
    with logic extracted from ii-agent and deepseekai.
    
    Workflow:
    1. Route Task -> Initialize workflow
    2. ResearchAgent (Real) -> ii-agent logic for research
    3. AnalysisAgent (Real) -> Gap analysis and quality evaluation
    4. Decision Point -> Continue research or proceed to synthesis
    5. SynthesisAgent (Real) -> Final answer with citations
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph builder
    builder = StateGraph(SpecializedState)
    
    # Add nodes with REAL agent implementations
    builder.add_node("route_task", route_specialized_task)
    builder.add_node("true_research_agent", true_research_agent_node)
    builder.add_node("true_analysis_agent", true_analysis_agent_node)
    builder.add_node("true_synthesis_agent", true_synthesis_agent_node)
    
    # Set entry point
    builder.add_edge(START, "route_task")
    
    # Main workflow edges
    builder.add_edge("route_task", "true_research_agent")
    builder.add_edge("true_research_agent", "true_analysis_agent")
    
    # Conditional edge for research continuation
    builder.add_conditional_edges(
        "true_analysis_agent",
        evaluate_true_research_continuation,
        {
            "true_research_agent": "true_research_agent",
            "true_synthesis_agent": "true_synthesis_agent"
        }
    )
    
    # Final edge
    builder.add_edge("true_synthesis_agent", END)
    
    # Compile the graph
    graph = builder.compile(name="true-specialized-3-agent-system")
    
    print("✅ TRUE Specialized 3-agent graph compiled successfully")
    print("📊 Graph structure (REAL Agents):")
    print("   Route Task → ResearchAgent (Real) → AnalysisAgent (Real)")
    print("                        ↑                      ↓")
    print("                        └── Continue? ──────────┘")
    print("                                              ↓")
    print("                                    SynthesisAgent (Real)")
    
    return graph
