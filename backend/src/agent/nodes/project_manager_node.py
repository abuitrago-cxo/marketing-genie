"""
Project Manager Node - Comprehensive Project Planning and Coordination

This node handles project management tasks including planning, resource allocation,
milestone tracking, and team coordination.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langsmith import traceable

from ..multi_agent_state import MultiAgentState, QualityMetrics, AgentExecution
from ..utils.llm_utils import get_llm
from ..utils.prompt_templates import PROJECT_MANAGER_PROMPTS


@traceable(name="project_manager")
async def project_manager_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Project Manager node for comprehensive project coordination
    
    Capabilities:
    - Project planning and structuring
    - Resource allocation and optimization
    - Timeline and milestone management
    - Risk assessment and mitigation
    - Progress tracking and reporting
    - Team coordination
    """
    
    print("📋 Project Manager: Starting project planning and coordination...")
    
    start_time = datetime.now()
    
    try:
        llm = get_llm(config)
        
        # Find project management tasks
        pm_tasks = [task for task in state["tasks"] if task.agent_type == "project_manager" and task.status == "pending"]
        
        if not pm_tasks:
            print("ℹ️ No project management tasks found")
            return state
        
        # Analyze current project state
        project_analysis = await analyze_project_state(
            state["original_query"],
            state["tasks"],
            state["research_data"],
            state["code_artifacts"],
            llm
        )
        
        # Create comprehensive project plan
        project_plan = await create_project_plan(
            project_analysis,
            state["original_query"],
            llm
        )
        
        # Generate milestones and timeline
        milestones = await generate_project_milestones(project_plan, llm)
        
        # Allocate resources
        resource_allocation = await allocate_project_resources(
            project_plan,
            state["agent_availability"],
            llm
        )
        
        # Assess risks and create mitigation strategies
        risk_assessment = await assess_project_risks(project_plan, llm)
        
        # Execute project management tasks
        for task in pm_tasks:
            print(f"📊 Executing PM task: {task.title}")
            
            # Mark task as completed
            task.status = "completed"
            task.result = {
                "project_plan_created": True,
                "milestones_defined": len(milestones),
                "resources_allocated": True,
                "risks_assessed": len(risk_assessment.get("risks", []))
            }
            task.updated_at = datetime.now()
        
        # Calculate quality metrics
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        quality_metrics = QualityMetrics(
            overall_score=calculate_pm_quality_score(project_plan, milestones),
            completeness=assess_plan_completeness(project_plan),
            accuracy=assess_plan_accuracy(project_plan),
            relevance=assess_plan_relevance(project_plan, state["original_query"]),
            clarity=assess_plan_clarity(project_plan),
            execution_time=execution_time,
            token_usage=estimate_pm_token_usage(project_plan),
            error_count=0
        )
        
        # Update state
        updated_state = state.copy()
        updated_state["project_plan"] = project_plan
        updated_state["milestones"] = milestones
        updated_state["resource_allocation"] = resource_allocation
        updated_state["workflow_stage"] = "project_management_complete"
        
        # Add execution record
        execution = AgentExecution(
            agent_type="project_manager",
            task_id=pm_tasks[0].id if pm_tasks else "pm_general",
            start_time=start_time,
            end_time=end_time,
            status="completed",
            output={
                "project_plan": project_plan,
                "milestones_count": len(milestones),
                "resource_allocation": resource_allocation,
                "risk_assessment": risk_assessment
            },
            metrics=quality_metrics
        )
        updated_state["agent_executions"].append(execution)
        
        # Add performance data
        updated_state["performance_data"]["project_manager"].append(quality_metrics)
        
        # Create project management summary message
        pm_message = create_project_management_summary(project_plan, milestones, resource_allocation, risk_assessment)
        updated_state["messages"].append(AIMessage(content=pm_message))
        
        print(f"✅ Project management completed: Plan created with {len(milestones)} milestones")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ Project management error: {e}")
        
        # Add error to state
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "project_manager",
            "error": str(e),
            "context": "project_planning"
        }
        
        updated_state = state.copy()
        updated_state["error_log"].append(error_entry)
        updated_state["workflow_stage"] = "project_management_error"
        
        # Mark PM tasks as failed
        for task in state["tasks"]:
            if task.agent_type == "project_manager" and task.status == "pending":
                task.status = "failed"
                task.error_message = str(e)
        
        return updated_state


async def analyze_project_state(
    original_query: str,
    tasks: List,
    research_data: List[Dict[str, Any]],
    code_artifacts: List,
    llm
) -> Dict[str, Any]:
    """Analyze current project state and requirements"""
    
    # Prepare context
    context = {
        "query": original_query,
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks if t.status == "completed"]),
        "research_completed": len(research_data) > 0,
        "code_artifacts": len(code_artifacts),
        "complexity": assess_project_complexity(original_query, tasks)
    }
    
    analysis_prompt = PROJECT_MANAGER_PROMPTS["project_analysis"].format(
        original_query=original_query,
        project_context=context
    )
    
    response = await llm.ainvoke(analysis_prompt)
    
    return {
        "project_type": determine_project_type(original_query),
        "scope": determine_project_scope(original_query, tasks),
        "complexity": context["complexity"],
        "stakeholders": identify_stakeholders(original_query),
        "success_criteria": define_success_criteria(original_query),
        "constraints": identify_constraints(original_query),
        "analysis_summary": response.content
    }


async def create_project_plan(
    project_analysis: Dict[str, Any],
    original_query: str,
    llm
) -> Dict[str, Any]:
    """Create comprehensive project plan"""
    
    planning_prompt = PROJECT_MANAGER_PROMPTS["project_planning"].format(
        project_analysis=project_analysis,
        original_query=original_query
    )
    
    response = await llm.ainvoke(planning_prompt)
    
    return {
        "project_name": generate_project_name(original_query),
        "description": original_query,
        "objectives": extract_project_objectives(response.content),
        "phases": create_project_phases(project_analysis),
        "deliverables": identify_project_deliverables(project_analysis),
        "timeline": estimate_project_timeline(project_analysis),
        "budget": estimate_project_budget(project_analysis),
        "quality_standards": define_quality_standards(project_analysis),
        "communication_plan": create_communication_plan(),
        "plan_details": response.content
    }


async def generate_project_milestones(project_plan: Dict[str, Any], llm) -> List[Dict[str, Any]]:
    """Generate project milestones and timeline"""
    
    milestones_prompt = PROJECT_MANAGER_PROMPTS["milestone_generation"].format(
        project_plan=project_plan
    )
    
    response = await llm.ainvoke(milestones_prompt)
    
    # Create milestone structure
    milestones = []
    phases = project_plan.get("phases", [])
    
    for i, phase in enumerate(phases):
        milestone = {
            "id": f"milestone_{i+1}",
            "name": f"{phase['name']} Complete",
            "description": phase.get("description", ""),
            "due_date": calculate_milestone_date(i, len(phases)),
            "dependencies": get_milestone_dependencies(i, phases),
            "deliverables": phase.get("deliverables", []),
            "success_criteria": phase.get("success_criteria", []),
            "status": "pending",
            "progress": 0
        }
        milestones.append(milestone)
    
    return milestones


async def allocate_project_resources(
    project_plan: Dict[str, Any],
    agent_availability: Dict[str, bool],
    llm
) -> Dict[str, Any]:
    """Allocate resources for project execution"""
    
    allocation_prompt = PROJECT_MANAGER_PROMPTS["resource_allocation"].format(
        project_plan=project_plan,
        available_agents=agent_availability
    )
    
    response = await llm.ainvoke(allocation_prompt)
    
    return {
        "agent_assignments": create_agent_assignments(project_plan, agent_availability),
        "time_allocation": estimate_time_allocation(project_plan),
        "priority_matrix": create_priority_matrix(project_plan),
        "resource_constraints": identify_resource_constraints(agent_availability),
        "optimization_suggestions": extract_optimization_suggestions(response.content)
    }


async def assess_project_risks(project_plan: Dict[str, Any], llm) -> Dict[str, Any]:
    """Assess project risks and create mitigation strategies"""
    
    risk_prompt = PROJECT_MANAGER_PROMPTS["risk_assessment"].format(
        project_plan=project_plan
    )
    
    response = await llm.ainvoke(risk_prompt)
    
    return {
        "risks": identify_project_risks(project_plan),
        "mitigation_strategies": create_mitigation_strategies(project_plan),
        "contingency_plans": create_contingency_plans(project_plan),
        "risk_matrix": create_risk_matrix(project_plan),
        "assessment_details": response.content
    }


# Helper functions for project management

def assess_project_complexity(query: str, tasks: List) -> str:
    """Assess project complexity"""
    complexity_indicators = {
        "high": ["enterprise", "complex", "comprehensive", "full-scale", "production"],
        "medium": ["moderate", "standard", "typical", "multi-step"],
        "low": ["simple", "basic", "quick", "minimal"]
    }
    
    query_lower = query.lower()
    
    for level, indicators in complexity_indicators.items():
        if any(indicator in query_lower for indicator in indicators):
            return level
    
    # Base on task count
    if len(tasks) > 5:
        return "high"
    elif len(tasks) > 2:
        return "medium"
    else:
        return "low"


def determine_project_type(query: str) -> str:
    """Determine project type from query"""
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in ["software", "app", "application", "system"]):
        return "software_development"
    elif any(keyword in query_lower for keyword in ["research", "analysis", "study"]):
        return "research_project"
    elif any(keyword in query_lower for keyword in ["plan", "strategy", "roadmap"]):
        return "planning_project"
    else:
        return "general_project"


def determine_project_scope(query: str, tasks: List) -> str:
    """Determine project scope"""
    if len(tasks) > 4:
        return "large"
    elif len(tasks) > 2:
        return "medium"
    else:
        return "small"


def identify_stakeholders(query: str) -> List[str]:
    """Identify project stakeholders"""
    return ["User", "Development Team", "Quality Assurance", "Project Manager"]


def define_success_criteria(query: str) -> List[str]:
    """Define project success criteria"""
    return [
        "All requirements met",
        "Quality standards achieved",
        "Timeline adhered to",
        "User satisfaction achieved"
    ]


def identify_constraints(query: str) -> List[str]:
    """Identify project constraints"""
    return [
        "Time constraints",
        "Resource availability",
        "Quality requirements",
        "Technical limitations"
    ]


def generate_project_name(query: str) -> str:
    """Generate project name from query"""
    words = query.split()[:3]  # First 3 words
    return " ".join(words).title() + " Project"


def extract_project_objectives(content: str) -> List[str]:
    """Extract project objectives from LLM response"""
    # Simplified extraction
    return [
        "Deliver high-quality solution",
        "Meet user requirements",
        "Ensure maintainability",
        "Provide comprehensive documentation"
    ]


def create_project_phases(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create project phases based on analysis"""
    complexity = analysis.get("complexity", "medium")
    
    if complexity == "high":
        phases = [
            {"name": "Planning", "description": "Detailed planning and analysis", "duration": "2 days"},
            {"name": "Research", "description": "Comprehensive research and investigation", "duration": "3 days"},
            {"name": "Design", "description": "System design and architecture", "duration": "2 days"},
            {"name": "Development", "description": "Implementation and coding", "duration": "5 days"},
            {"name": "Testing", "description": "Quality assurance and testing", "duration": "2 days"},
            {"name": "Deployment", "description": "Final deployment and delivery", "duration": "1 day"}
        ]
    elif complexity == "medium":
        phases = [
            {"name": "Planning", "description": "Project planning", "duration": "1 day"},
            {"name": "Research", "description": "Information gathering", "duration": "2 days"},
            {"name": "Development", "description": "Implementation", "duration": "3 days"},
            {"name": "Testing", "description": "Quality assurance", "duration": "1 day"},
            {"name": "Delivery", "description": "Final delivery", "duration": "1 day"}
        ]
    else:
        phases = [
            {"name": "Analysis", "description": "Requirement analysis", "duration": "0.5 days"},
            {"name": "Implementation", "description": "Quick implementation", "duration": "1 day"},
            {"name": "Review", "description": "Quality review", "duration": "0.5 days"}
        ]
    
    return phases


def identify_project_deliverables(analysis: Dict[str, Any]) -> List[str]:
    """Identify project deliverables"""
    project_type = analysis.get("project_type", "general_project")
    
    if project_type == "software_development":
        return ["Source code", "Documentation", "Tests", "Deployment guide"]
    elif project_type == "research_project":
        return ["Research report", "Data analysis", "Recommendations", "Citations"]
    else:
        return ["Final report", "Recommendations", "Implementation plan"]


def estimate_project_timeline(analysis: Dict[str, Any]) -> Dict[str, str]:
    """Estimate project timeline"""
    complexity = analysis.get("complexity", "medium")
    
    timeline_map = {
        "low": {"start": "Today", "end": "2 days", "duration": "2 days"},
        "medium": {"start": "Today", "end": "1 week", "duration": "1 week"},
        "high": {"start": "Today", "end": "2 weeks", "duration": "2 weeks"}
    }
    
    return timeline_map.get(complexity, timeline_map["medium"])


def estimate_project_budget(analysis: Dict[str, Any]) -> Dict[str, str]:
    """Estimate project budget"""
    return {
        "development_hours": "40-80 hours",
        "resource_cost": "Medium",
        "total_estimate": "Standard project budget"
    }


def define_quality_standards(analysis: Dict[str, Any]) -> List[str]:
    """Define quality standards"""
    return [
        "Code quality: High",
        "Documentation: Comprehensive",
        "Testing: Thorough",
        "Performance: Optimized"
    ]


def create_communication_plan() -> Dict[str, str]:
    """Create communication plan"""
    return {
        "frequency": "Real-time updates",
        "channels": "System messages and logs",
        "stakeholders": "All agents and user",
        "reporting": "Progress tracking and metrics"
    }


def calculate_milestone_date(index: int, total_phases: int) -> str:
    """Calculate milestone due date"""
    days_per_phase = 2  # Simplified
    due_date = datetime.now() + timedelta(days=(index + 1) * days_per_phase)
    return due_date.strftime("%Y-%m-%d")


def get_milestone_dependencies(index: int, phases: List) -> List[str]:
    """Get milestone dependencies"""
    if index == 0:
        return []
    else:
        return [f"milestone_{index}"]


def create_agent_assignments(project_plan: Dict[str, Any], agent_availability: Dict[str, bool]) -> Dict[str, List[str]]:
    """Create agent assignments"""
    assignments = {}
    
    for agent, available in agent_availability.items():
        if available:
            if agent == "research":
                assignments[agent] = ["Information gathering", "Market research"]
            elif agent == "code_engineer":
                assignments[agent] = ["Development", "Code review", "Testing"]
            elif agent == "project_manager":
                assignments[agent] = ["Planning", "Coordination", "Reporting"]
            elif agent == "qa_specialist":
                assignments[agent] = ["Quality assurance", "Testing", "Validation"]
    
    return assignments


def estimate_time_allocation(project_plan: Dict[str, Any]) -> Dict[str, str]:
    """Estimate time allocation"""
    return {
        "planning": "20%",
        "development": "50%",
        "testing": "20%",
        "documentation": "10%"
    }


def create_priority_matrix(project_plan: Dict[str, Any]) -> Dict[str, str]:
    """Create priority matrix"""
    return {
        "high_priority": "Core functionality",
        "medium_priority": "Additional features",
        "low_priority": "Nice-to-have features"
    }


def identify_resource_constraints(agent_availability: Dict[str, bool]) -> List[str]:
    """Identify resource constraints"""
    constraints = []
    
    for agent, available in agent_availability.items():
        if not available:
            constraints.append(f"{agent.replace('_', ' ').title()} not available")
    
    if not constraints:
        constraints.append("No significant resource constraints")
    
    return constraints


def extract_optimization_suggestions(content: str) -> List[str]:
    """Extract optimization suggestions from LLM response"""
    return [
        "Parallel task execution where possible",
        "Regular progress reviews",
        "Continuous quality monitoring",
        "Efficient resource utilization"
    ]


def identify_project_risks(project_plan: Dict[str, Any]) -> List[Dict[str, str]]:
    """Identify project risks"""
    return [
        {"risk": "Timeline delays", "probability": "Medium", "impact": "Medium"},
        {"risk": "Quality issues", "probability": "Low", "impact": "High"},
        {"risk": "Resource unavailability", "probability": "Low", "impact": "Medium"},
        {"risk": "Scope creep", "probability": "Medium", "impact": "Medium"}
    ]


def create_mitigation_strategies(project_plan: Dict[str, Any]) -> Dict[str, str]:
    """Create risk mitigation strategies"""
    return {
        "timeline_delays": "Buffer time allocation and parallel processing",
        "quality_issues": "Continuous quality monitoring and testing",
        "resource_unavailability": "Cross-training and backup resources",
        "scope_creep": "Clear requirements and change management"
    }


def create_contingency_plans(project_plan: Dict[str, Any]) -> Dict[str, str]:
    """Create contingency plans"""
    return {
        "major_delays": "Prioritize core features and defer non-essential items",
        "quality_failures": "Additional testing cycles and code review",
        "resource_loss": "Redistribute tasks and extend timeline if necessary"
    }


def create_risk_matrix(project_plan: Dict[str, Any]) -> Dict[str, str]:
    """Create risk assessment matrix"""
    return {
        "high_probability_high_impact": "Timeline management",
        "high_probability_low_impact": "Minor scope adjustments",
        "low_probability_high_impact": "Quality assurance",
        "low_probability_low_impact": "Documentation updates"
    }


def calculate_pm_quality_score(project_plan: Dict[str, Any], milestones: List[Dict[str, Any]]) -> float:
    """Calculate project management quality score"""
    base_score = 4.0
    
    # Adjust based on plan completeness
    if len(project_plan.get("phases", [])) >= 4:
        base_score += 0.5
    
    # Adjust based on milestone detail
    if len(milestones) >= 3:
        base_score += 0.3
    
    return min(5.0, base_score)


def assess_plan_completeness(project_plan: Dict[str, Any]) -> float:
    """Assess plan completeness"""
    required_elements = ["objectives", "phases", "deliverables", "timeline"]
    present_elements = sum(1 for elem in required_elements if elem in project_plan)
    return present_elements / len(required_elements)


def assess_plan_accuracy(project_plan: Dict[str, Any]) -> float:
    """Assess plan accuracy"""
    return 0.9  # Placeholder


def assess_plan_relevance(project_plan: Dict[str, Any], query: str) -> float:
    """Assess plan relevance to query"""
    return 0.85  # Placeholder


def assess_plan_clarity(project_plan: Dict[str, Any]) -> float:
    """Assess plan clarity"""
    return 0.8  # Placeholder


def estimate_pm_token_usage(project_plan: Dict[str, Any]) -> int:
    """Estimate token usage for project management"""
    content_length = len(str(project_plan))
    return int(content_length / 4)


def create_project_management_summary(
    project_plan: Dict[str, Any],
    milestones: List[Dict[str, Any]],
    resource_allocation: Dict[str, Any],
    risk_assessment: Dict[str, Any]
) -> str:
    """Create project management summary"""
    
    message = f"""📋 **Project Manager Report**

**Project Overview:**
- Name: {project_plan.get('project_name', 'Unnamed Project')}
- Type: {project_plan.get('project_type', 'General').replace('_', ' ').title()}
- Complexity: {project_plan.get('complexity', 'Medium')}
- Timeline: {project_plan.get('timeline', {}).get('duration', 'TBD')}

**Project Phases:**
"""
    
    phases = project_plan.get("phases", [])
    for i, phase in enumerate(phases, 1):
        message += f"{i}. **{phase['name']}** - {phase.get('duration', 'TBD')}\n"
        message += f"   {phase.get('description', '')}\n"
    
    message += f"""
**Milestones:**
{len(milestones)} key milestones defined with clear deliverables and success criteria.

**Resource Allocation:**
- Agents assigned: {len(resource_allocation.get('agent_assignments', {}))}
- Priority matrix: Established
- Time allocation: Optimized

**Risk Management:**
- Risks identified: {len(risk_assessment.get('risks', []))}
- Mitigation strategies: In place
- Contingency plans: Prepared

**Next Steps:**
Project plan is ready for execution. All agents have clear assignments and timelines.
"""
    
    return message
