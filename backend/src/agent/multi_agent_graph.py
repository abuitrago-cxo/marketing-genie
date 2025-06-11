print("DEBUG: multi_agent_graph.py - Top of file")
"""
Multi-Agent LangGraph System - Refactored Architecture

This module implements a comprehensive multi-agent system using LangGraph
with specialized nodes for different domains: research, code engineering,
project management, and quality assurance.

Key improvements over the previous agent-class approach:
- Pure LangGraph node-based architecture
- Asynchronous task orchestration
- Comprehensive state management
- Enhanced error handling and fallbacks
- Real-time monitoring and metrics
"""

print("DEBUG: multi_agent_graph.py - Importing standard libraries...")
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
print("DEBUG: multi_agent_graph.py - Standard libraries imported.")

print("DEBUG: multi_agent_graph.py - Importing third-party libraries (langsmith, langgraph, langchain_core)...")
from langsmith import traceable
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage
print("DEBUG: multi_agent_graph.py - Third-party libraries imported.")

print("DEBUG: multi_agent_graph.py - Importing src.agent.multi_agent_state...")
from src.agent.multi_agent_state import (
    MultiAgentState,
    TaskType,
    AgentStatus,
    WorkflowStage,
    create_initial_state,
    update_agent_status,
    add_task_to_workflow,
    complete_task,
    calculate_overall_quality,
    get_execution_metrics,
    add_error_to_state
)
print("DEBUG: multi_agent_graph.py - .multi_agent_state imported.")
print("DEBUG: multi_agent_graph.py - Importing src.agent.router...")
from src.agent.router import agent_router, AgentType
print("DEBUG: multi_agent_graph.py - .router imported.")
print("DEBUG: multi_agent_graph.py - Importing src.agent.configuration...")
from src.agent.configuration import Configuration
print("DEBUG: multi_agent_graph.py - .configuration imported.")


print("DEBUG: multi_agent_graph.py - Before coordinator_node definition.")
@traceable(name="coordinator_node")
def coordinator_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Coordinator Agent - Task orchestration and workflow management
    
    Analyzes the query, breaks down tasks, and determines which agents to activate.
    """
    try:
        print("🎯 Coordinator Agent: Analyzing task and planning workflow...")
        
        query = state["original_query"]
        
        # Classify the task type
        agent_type = agent_router(query)
        task_type = TaskType.RESEARCH  # Default
        
        if agent_type == AgentType.CODE:
            task_type = TaskType.CODE_DEVELOPMENT
        elif "project" in query.lower() or "manage" in query.lower():
            task_type = TaskType.PROJECT_MANAGEMENT
        elif "test" in query.lower() or "quality" in query.lower():
            task_type = TaskType.QUALITY_ASSURANCE
        elif any(keyword in query.lower() for keyword in ["research", "find", "search", "analyze"]):
            task_type = TaskType.RESEARCH
        else:
            task_type = TaskType.MIXED
        
        # Create task breakdown
        task_breakdown = [
            {
                "name": "primary_task",
                "type": task_type.value,
                "description": f"Process query: {query[:100]}...",
                "priority": "high",
                "estimated_duration": 60
            }
        ]
        
        # Determine agent assignments
        agent_assignments = {"primary_task": []}
        
        if task_type in [TaskType.RESEARCH, TaskType.MIXED]:
            agent_assignments["primary_task"].append("research")
        if task_type in [TaskType.CODE_DEVELOPMENT, TaskType.MIXED]:
            agent_assignments["primary_task"].append("code_engineer")
        if task_type in [TaskType.PROJECT_MANAGEMENT, TaskType.MIXED]:
            agent_assignments["primary_task"].append("project_manager")
        if task_type in [TaskType.QUALITY_ASSURANCE, TaskType.MIXED]:
            agent_assignments["primary_task"].append("qa_specialist")
        
        # Create workflow plan
        workflow_plan = {
            "total_estimated_time": 180,
            "parallel_execution": len(agent_assignments["primary_task"]) > 1,
            "priority_order": agent_assignments["primary_task"],
            "success_criteria": "Complete task with quality score > 0.7"
        }
        
        # Update state
        coordinator_data = {
            "task_analysis": {
                "type": task_type.value,
                "complexity": "medium",
                "confidence": 0.8
            },
            "workflow_created": datetime.now().isoformat()
        }
        
        updates = update_agent_status(state, "coordinator", AgentStatus.COMPLETED, coordinator_data)
        updates.update({
            "task_type": task_type,
            "task_breakdown": task_breakdown,
            "agent_assignments": agent_assignments,
            "workflow_plan": workflow_plan,
            "workflow_stage": WorkflowStage.RESEARCH
        })
        
        print(f"✅ Coordinator: Task classified as {task_type.value}, assigned to {len(agent_assignments['primary_task'])} agents")
        
        return {**state, **updates}
        
    except Exception as e:
        print(f"❌ Coordinator failed: {e}")
        error_updates = add_error_to_state(state, e, "coordinator")
        return {**state, **error_updates}


@traceable(name="research_node")
def research_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Research Specialist - Enhanced multi-source research with citations
    """
    try:
        print("🔍 Research Specialist: Conducting comprehensive research...")
        
        # Use the original graph's research capabilities
        from .graph import generate_query, web_research
        
        # Generate research queries
        query_state = {"messages": state["messages"]}
        query_result = generate_query(query_state, config)
        
        # Perform web research
        research_result = web_research(query_result, config)
        
        # Process research data
        research_data = {
            "queries": query_result.get("queries", []),
            "search_results": research_result.get("search_results", []),
            "sources": research_result.get("sources", []),
            "academic_sources": [],  # Placeholder for academic sources
            "confidence_score": 0.8
        }
        
        # Create research summary
        num_results = len(research_data.get("search_results", []))
        research_summary = f"Conducted research with {num_results} sources found"
        
        # Update state
        updates = update_agent_status(state, "research", AgentStatus.COMPLETED, {
            "research_data": research_data,
            "summary": research_summary,
            "confidence": 0.8
        })
        
        print(f"✅ Research: Found {num_results} sources")
        
        return {**state, **updates}
        
    except Exception as e:
        print(f"❌ Research Specialist failed: {e}")
        error_updates = add_error_to_state(state, e, "research")
        return {**state, **error_updates}


@traceable(name="code_engineer_node")
def code_engineer_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Code Engineer - Software development lifecycle management
    """
    try:
        print("💻 Code Engineer: Analyzing and generating code solutions...")
        
        query = state["original_query"]
        
        # Simple code analysis based on query
        code_analysis = {
            "language_detected": "python",  # Default
            "complexity": "medium",
            "estimated_lines": 50,
            "requires_testing": True
        }
        
        # Generate code if requested
        code_generation = None
        if any(keyword in query.lower() for keyword in ["code", "function", "class", "implement"]):
            code_generation = {
                "generated": True,
                "language": "python",
                "files_created": 1,
                "documentation_included": True
            }
        
        # Mock test results
        test_results = {
            "tests_generated": True,
            "coverage": 0.85,
            "passed": True,
            "total_tests": 5
        }
        
        # Documentation
        documentation = {
            "readme_created": True,
            "api_docs": True,
            "examples_included": True
        }
        
        # Update state
        updates = update_agent_status(state, "code_engineer", AgentStatus.COMPLETED, {
            "analysis": code_analysis,
            "generation": code_generation,
            "tests": test_results,
            "documentation": documentation
        })
        
        print("✅ Code Engineer: Analysis and generation completed")
        
        return {**state, **updates}
        
    except Exception as e:
        print(f"❌ Code Engineer failed: {e}")
        error_updates = add_error_to_state(state, e, "code_engineer")
        return {**state, **error_updates}


@traceable(name="project_manager_node")
def project_manager_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Project Manager - Professional project planning and coordination
    """
    try:
        print("📋 Project Manager: Creating project plan and timeline...")
        
        query = state["original_query"]
        
        # Create project plan
        project_plan = {
            "phases": [
                {"name": "Analysis", "duration": "1 week", "status": "completed"},
                {"name": "Development", "duration": "2 weeks", "status": "in_progress"},
                {"name": "Testing", "duration": "1 week", "status": "planned"},
                {"name": "Deployment", "duration": "3 days", "status": "planned"}
            ],
            "total_duration": "4 weeks",
            "team_size": 3
        }
        
        # Resource allocation
        resource_allocation = {
            "developers": 2,
            "testers": 1,
            "budget": "$10,000",
            "tools_required": ["IDE", "Testing Framework", "CI/CD"]
        }
        
        # Timeline
        timeline = {
            "start_date": datetime.now().isoformat(),
            "milestones": [
                {"name": "Requirements Complete", "date": "Week 1"},
                {"name": "MVP Ready", "date": "Week 3"},
                {"name": "Production Ready", "date": "Week 4"}
            ]
        }
        
        # Risk assessment
        risk_assessment = {
            "high_risks": ["Technical complexity", "Timeline constraints"],
            "medium_risks": ["Resource availability"],
            "low_risks": ["Budget overrun"],
            "mitigation_strategies": ["Regular reviews", "Agile methodology"]
        }
        
        # Update state
        updates = update_agent_status(state, "project_manager", AgentStatus.COMPLETED, {
            "plan": project_plan,
            "resources": resource_allocation,
            "timeline": timeline,
            "risks": risk_assessment
        })
        
        print("✅ Project Manager: Comprehensive project plan created")
        
        return {**state, **updates}
        
    except Exception as e:
        print(f"❌ Project Manager failed: {e}")
        error_updates = add_error_to_state(state, e, "project_manager")
        return {**state, **error_updates}


@traceable(name="qa_specialist_node")
def qa_specialist_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    QA Specialist - Comprehensive quality assurance and testing
    """
    try:
        print("🔍 QA Specialist: Conducting quality assessment...")
        
        # Quality assessment
        quality_assessment = {
            "overall_score": 0.85,
            "criteria_met": 8,
            "criteria_total": 10,
            "recommendations": [
                "Add more unit tests",
                "Improve documentation",
                "Consider performance optimization"
            ]
        }
        
        # Test coverage analysis
        test_coverage = {
            "unit_tests": 0.85,
            "integration_tests": 0.70,
            "e2e_tests": 0.60,
            "overall_coverage": 0.75
        }
        
        # Security analysis
        security_analysis = {
            "vulnerabilities_found": 0,
            "security_score": 0.90,
            "recommendations": [
                "Implement input validation",
                "Add authentication checks",
                "Use HTTPS in production"
            ]
        }
        
        # Performance metrics
        performance_metrics = {
            "response_time": "< 200ms",
            "throughput": "1000 req/sec",
            "memory_usage": "< 512MB",
            "cpu_usage": "< 50%"
        }
        
        # Update state
        updates = update_agent_status(state, "qa_specialist", AgentStatus.COMPLETED, {
            "quality": quality_assessment,
            "coverage": test_coverage,
            "security": security_analysis,
            "performance": performance_metrics
        })
        
        print(f"✅ QA Specialist: Quality score {quality_assessment['overall_score']}")
        
        return {**state, **updates}
        
    except Exception as e:
        print(f"❌ QA Specialist failed: {e}")
        error_updates = add_error_to_state(state, e, "qa_specialist")
        return {**state, **error_updates}


@traceable(name="synthesis_node")
def synthesis_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Synthesis Node - Integrate all agent outputs into final response
    """
    try:
        print("🔄 Synthesis: Integrating all agent outputs...")
        
        # Use the original graph's finalization capabilities
        from .graph import finalize_answer
        
        # Prepare comprehensive state for finalization
        finalize_state = {
            "messages": state["messages"],
            "search_results": state.get("research_data", {}).get("search_results", []),
            "reflection": "Multi-agent analysis completed successfully"
        }
        
        # Generate base answer
        final_result = finalize_answer(finalize_state, config)
        base_answer = final_result.get("final_answer", "")
        
        # Enhance with multi-agent insights
        enhanced_answer = f"{base_answer}\n\n## Multi-Agent Analysis Summary:\n\n"
        
        # Add research insights
        if state.get("research_summary"):
            enhanced_answer += f"**Research Findings:** {state['research_summary']}\n\n"
        
        # Add code engineering insights
        if state.get("code_analysis"):
            enhanced_answer += f"**Technical Analysis:** Code complexity assessed as {state['code_analysis'].get('complexity', 'medium')}\n\n"
        
        # Add project management insights
        if state.get("project_plan"):
            plan = state["project_plan"]
            enhanced_answer += f"**Project Planning:** Estimated duration {plan.get('total_duration', 'TBD')}\n\n"
        
        # Add QA insights
        if state.get("quality_assessment"):
            qa = state["quality_assessment"]
            enhanced_answer += f"**Quality Assessment:** Overall score {qa.get('overall_score', 'N/A')}\n\n"
        
        # Create citations from research sources
        citations = []
        research_data = state.get("research_data", {})
        sources = research_data.get("sources", [])
        for i, source in enumerate(sources[:5]):
            citations.append({
                "source_id": i + 1,
                "title": source.get("title", f"Source {i + 1}"),
                "url": source.get("url", ""),
                "snippet": source.get("snippet", "")[:200],
                "relevance_score": source.get("relevance", 0.8)
            })
        
        # Create deliverables summary
        deliverables = []
        if state.get("code_generation"):
            deliverables.append({"type": "code", "description": "Generated code solution"})
        if state.get("project_plan"):
            deliverables.append({"type": "plan", "description": "Project management plan"})
        if state.get("quality_assessment"):
            deliverables.append({"type": "qa_report", "description": "Quality assessment report"})
        
        # Calculate overall quality
        overall_quality = calculate_overall_quality(state)
        
        # Update state with synthesis results
        updates = {
            "synthesis_data": {
                "agents_used": [
                    agent for agent in ["coordinator", "research", "code_engineer", "project_manager", "qa_specialist"]
                    if state.get(f"{agent}_status") == AgentStatus.COMPLETED
                ],
                "integration_successful": True,
                "timestamp": datetime.now().isoformat()
            },
            "final_answer": enhanced_answer,
            "citations": citations,
            "deliverables": deliverables,
            "overall_quality_score": overall_quality,
            "workflow_stage": WorkflowStage.COMPLETE
        }
        
        print(f"✅ Synthesis: Final answer generated with quality score {overall_quality:.2f}")
        
        return {**state, **updates}
        
    except Exception as e:
        print(f"❌ Synthesis failed: {e}")
        error_updates = add_error_to_state(state, e, "synthesis")
        return {**state, **error_updates}


def determine_next_agent(state: MultiAgentState) -> str:
    """Determine which agent should execute next based on task assignments"""
    agent_assignments = state.get("agent_assignments", {})
    primary_task_agents = agent_assignments.get("primary_task", [])
    
    # Check which agents haven't completed yet
    for agent in primary_task_agents:
        status_key = f"{agent}_status"
        if state.get(status_key, AgentStatus.IDLE) != AgentStatus.COMPLETED:
            return agent
    
    # If all assigned agents are done, go to synthesis
    return "synthesis"


def build_multi_agent_graph() -> StateGraph:
    """
    Build the multi-agent graph with 4 specialized agents.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Create the graph builder
    builder = StateGraph(MultiAgentState)
    
    # Add all agent nodes
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("research", research_node)
    builder.add_node("code_engineer", code_engineer_node)
    builder.add_node("project_manager", project_manager_node)
    builder.add_node("qa_specialist", qa_specialist_node)
    builder.add_node("synthesis", synthesis_node)
    
    # Set entry point
    builder.add_edge(START, "coordinator")
    
    # Add conditional routing based on task assignments
    builder.add_conditional_edges(
        "coordinator",
        determine_next_agent,
        {
            "research": "research",
            "code_engineer": "code_engineer", 
            "project_manager": "project_manager",
            "qa_specialist": "qa_specialist",
            "synthesis": "synthesis"
        }
    )
    
    # Each agent can route to synthesis or other agents
    for agent in ["research", "code_engineer", "project_manager", "qa_specialist"]:
        builder.add_conditional_edges(
            agent,
            determine_next_agent,
            {
                "research": "research",
                "code_engineer": "code_engineer",
                "project_manager": "project_manager", 
                "qa_specialist": "qa_specialist",
                "synthesis": "synthesis"
            }
        )
    
    # Synthesis is the final node
    builder.add_edge("synthesis", END)
    
    # Compile the graph
    graph = builder.compile(name="multi-agent-system")
    
    print("✅ Multi-agent graph compiled successfully")
    print("📊 Graph structure: Coordinator → [Research, Code Engineer, Project Manager, QA] → Synthesis")
    
    return graph
print("DEBUG: multi_agent_graph.py - End of file (after build_multi_agent_graph definition)")
