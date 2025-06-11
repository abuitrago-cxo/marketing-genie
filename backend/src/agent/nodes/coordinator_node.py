"""
Coordinator Node - Multi-Agent Task Orchestration

This node acts as the central coordinator for the multi-agent system,
responsible for task analysis, agent selection, and workflow orchestration.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langsmith import traceable

from ..multi_agent_state import MultiAgentState, Task, AgentExecution, AgentType
from ..utils.llm_utils import get_llm
from ..utils.prompt_templates import COORDINATOR_PROMPTS


@traceable(name="coordinator_analysis")
async def coordinator_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Coordinator node that analyzes the query and creates a comprehensive task plan
    
    Responsibilities:
    - Analyze user query and determine required agents
    - Create task breakdown and dependencies
    - Assign priorities and resource allocation
    - Set up workflow orchestration
    """
    
    print("🎯 Coordinator: Analyzing query and creating task plan...")
    
    try:
        llm = get_llm(config)
        
        # Analyze the query to determine required agents and tasks
        analysis_result = await analyze_query_and_create_plan(
            state["original_query"], 
            llm,
            state.get("user_preferences", {})
        )
        
        # Create tasks based on analysis
        tasks = create_tasks_from_analysis(analysis_result)
        
        # Update state with tasks and plan
        updated_state = state.copy()
        updated_state["tasks"] = tasks
        updated_state["project_plan"] = analysis_result.get("project_plan")
        updated_state["workflow_stage"] = "planning_complete"
        updated_state["current_agent"] = "coordinator"
        
        # Add coordinator execution record
        execution = AgentExecution(
            agent_type="coordinator",
            task_id="coordination",
            start_time=datetime.now(),
            end_time=datetime.now(),
            status="completed",
            output=analysis_result
        )
        updated_state["agent_executions"].append(execution)
        
        # Determine next agent based on task priorities
        next_agent = determine_next_agent(tasks)
        if next_agent:
            updated_state["current_agent"] = next_agent
            updated_state["workflow_stage"] = f"{next_agent}_ready"
        
        # Add coordination message
        coordination_message = create_coordination_message(analysis_result, tasks)
        updated_state["messages"].append(AIMessage(content=coordination_message))
        
        print(f"✅ Coordinator: Created {len(tasks)} tasks, next agent: {next_agent}")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ Coordinator error: {e}")
        
        # Add error to state
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "coordinator",
            "error": str(e),
            "context": "query_analysis"
        }
        
        updated_state = state.copy()
        updated_state["error_log"].append(error_entry)
        updated_state["workflow_stage"] = "coordinator_error"
        
        return updated_state


async def analyze_query_and_create_plan(query: str, llm, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze query and create comprehensive execution plan"""
    
    analysis_prompt = COORDINATOR_PROMPTS["query_analysis"].format(
        query=query,
        user_preferences=user_preferences
    )
    
    response = await llm.ainvoke(analysis_prompt)
    
    # Parse the LLM response to extract structured plan
    # This would typically involve more sophisticated parsing
    plan = {
        "query_type": determine_query_type(query),
        "required_agents": determine_required_agents(query),
        "complexity_level": assess_complexity(query),
        "estimated_duration": estimate_duration(query),
        "deliverables": identify_deliverables(query),
        "project_plan": {
            "phases": create_project_phases(query),
            "dependencies": identify_dependencies(query),
            "success_criteria": define_success_criteria(query)
        }
    }
    
    return plan


def create_tasks_from_analysis(analysis: Dict[str, Any]) -> List[Task]:
    """Create specific tasks based on the analysis"""
    tasks = []
    
    required_agents = analysis.get("required_agents", [])
    query_type = analysis.get("query_type", "general")
    
    # Create tasks based on required agents and query type
    if "research" in required_agents:
        research_task = Task(
            id=f"research_{uuid.uuid4().hex[:8]}",
            title="Research and Information Gathering",
            description="Conduct comprehensive research on the topic",
            agent_type="research",
            priority="high" if query_type in ["research", "analysis"] else "medium"
        )
        tasks.append(research_task)
    
    if "code_engineer" in required_agents:
        code_task = Task(
            id=f"code_{uuid.uuid4().hex[:8]}",
            title="Code Development and Engineering",
            description="Develop, review, and optimize code solutions",
            agent_type="code_engineer",
            priority="high" if query_type in ["coding", "development"] else "medium"
        )
        tasks.append(code_task)
    
    if "project_manager" in required_agents:
        pm_task = Task(
            id=f"pm_{uuid.uuid4().hex[:8]}",
            title="Project Planning and Management",
            description="Create project structure and manage execution",
            agent_type="project_manager",
            priority="high" if query_type in ["planning", "management"] else "medium"
        )
        tasks.append(pm_task)
    
    if "qa_specialist" in required_agents:
        qa_task = Task(
            id=f"qa_{uuid.uuid4().hex[:8]}",
            title="Quality Assurance and Testing",
            description="Ensure quality and test deliverables",
            agent_type="qa_specialist",
            priority="medium"
        )
        tasks.append(qa_task)
    
    # Set up task dependencies
    setup_task_dependencies(tasks, query_type)
    
    return tasks


def determine_query_type(query: str) -> str:
    """Determine the type of query to optimize task creation"""
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in ["code", "program", "develop", "build", "implement"]):
        return "coding"
    elif any(keyword in query_lower for keyword in ["research", "find", "search", "analyze", "study"]):
        return "research"
    elif any(keyword in query_lower for keyword in ["plan", "manage", "organize", "schedule", "project"]):
        return "planning"
    elif any(keyword in query_lower for keyword in ["test", "quality", "review", "validate"]):
        return "testing"
    else:
        return "general"


def determine_required_agents(query: str) -> List[AgentType]:
    """Determine which agents are needed based on the query"""
    agents = []
    query_lower = query.lower()
    
    # Always include coordinator
    agents.append("coordinator")
    
    # Research agent for information gathering
    if any(keyword in query_lower for keyword in ["research", "find", "search", "information", "data", "analyze"]):
        agents.append("research")
    
    # Code engineer for development tasks
    if any(keyword in query_lower for keyword in ["code", "program", "develop", "build", "implement", "software", "app"]):
        agents.append("code_engineer")
    
    # Project manager for complex tasks
    if any(keyword in query_lower for keyword in ["plan", "manage", "organize", "project", "schedule", "coordinate"]):
        agents.append("project_manager")
    
    # QA specialist for quality tasks
    if any(keyword in query_lower for keyword in ["test", "quality", "review", "validate", "check"]):
        agents.append("qa_specialist")
    
    # Default to research if no specific agents identified
    if len(agents) == 1:  # Only coordinator
        agents.append("research")
    
    return agents


def assess_complexity(query: str) -> str:
    """Assess the complexity level of the query"""
    complexity_indicators = {
        "high": ["complex", "comprehensive", "detailed", "full", "complete", "enterprise", "production"],
        "medium": ["moderate", "standard", "typical", "normal", "basic"],
        "low": ["simple", "quick", "easy", "basic", "minimal"]
    }
    
    query_lower = query.lower()
    
    for level, indicators in complexity_indicators.items():
        if any(indicator in query_lower for indicator in indicators):
            return level
    
    # Default complexity based on query length and structure
    if len(query.split()) > 20:
        return "high"
    elif len(query.split()) > 10:
        return "medium"
    else:
        return "low"


def estimate_duration(query: str) -> str:
    """Estimate execution duration based on query complexity"""
    complexity = assess_complexity(query)
    required_agents = determine_required_agents(query)
    
    base_time = {
        "low": 5,
        "medium": 15,
        "high": 30
    }
    
    # Add time for each additional agent
    agent_multiplier = len(required_agents) * 0.5
    
    estimated_minutes = base_time[complexity] * (1 + agent_multiplier)
    
    if estimated_minutes < 10:
        return "5-10 minutes"
    elif estimated_minutes < 30:
        return "15-30 minutes"
    else:
        return "30+ minutes"


def identify_deliverables(query: str) -> List[str]:
    """Identify expected deliverables from the query"""
    deliverables = []
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in ["code", "program", "script", "application"]):
        deliverables.append("Source code")
        deliverables.append("Documentation")
    
    if any(keyword in query_lower for keyword in ["research", "analysis", "report"]):
        deliverables.append("Research report")
        deliverables.append("Citations and sources")
    
    if any(keyword in query_lower for keyword in ["plan", "strategy", "roadmap"]):
        deliverables.append("Project plan")
        deliverables.append("Timeline and milestones")
    
    if any(keyword in query_lower for keyword in ["test", "quality"]):
        deliverables.append("Test results")
        deliverables.append("Quality report")
    
    # Default deliverable
    if not deliverables:
        deliverables.append("Comprehensive response")
    
    return deliverables


def create_project_phases(query: str) -> List[Dict[str, Any]]:
    """Create project phases based on query analysis"""
    phases = [
        {"name": "Analysis", "description": "Analyze requirements and plan approach"},
        {"name": "Execution", "description": "Execute main tasks using specialized agents"},
        {"name": "Integration", "description": "Integrate results from different agents"},
        {"name": "Quality Assurance", "description": "Review and validate outputs"},
        {"name": "Delivery", "description": "Finalize and present results"}
    ]
    return phases


def identify_dependencies(query: str) -> List[Dict[str, str]]:
    """Identify task dependencies"""
    # This would be more sophisticated in a real implementation
    return [
        {"from": "research", "to": "code_engineer", "type": "information"},
        {"from": "code_engineer", "to": "qa_specialist", "type": "artifacts"},
        {"from": "project_manager", "to": "all", "type": "coordination"}
    ]


def define_success_criteria(query: str) -> List[str]:
    """Define success criteria for the project"""
    return [
        "All tasks completed successfully",
        "Quality standards met",
        "User requirements satisfied",
        "Deliverables provided"
    ]


def setup_task_dependencies(tasks: List[Task], query_type: str) -> None:
    """Set up dependencies between tasks"""
    # Simple dependency setup - research before coding, coding before QA
    task_by_type = {task.agent_type: task for task in tasks}
    
    if "research" in task_by_type and "code_engineer" in task_by_type:
        task_by_type["code_engineer"].dependencies.append(task_by_type["research"].id)
    
    if "code_engineer" in task_by_type and "qa_specialist" in task_by_type:
        task_by_type["qa_specialist"].dependencies.append(task_by_type["code_engineer"].id)


def determine_next_agent(tasks: List[Task]) -> Optional[AgentType]:
    """Determine which agent should execute next"""
    # Find highest priority task without dependencies
    available_tasks = [task for task in tasks if not task.dependencies and task.status == "pending"]
    
    if not available_tasks:
        return None
    
    # Sort by priority
    priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    available_tasks.sort(key=lambda t: priority_order.get(t.priority, 0), reverse=True)
    
    return available_tasks[0].agent_type


def create_coordination_message(analysis: Dict[str, Any], tasks: List[Task]) -> str:
    """Create a message explaining the coordination plan"""
    message = f"""🎯 **Multi-Agent Coordination Plan**

**Query Analysis:**
- Type: {analysis.get('query_type', 'general').title()}
- Complexity: {analysis.get('complexity_level', 'medium').title()}
- Estimated Duration: {analysis.get('estimated_duration', 'Unknown')}

**Task Breakdown:**
"""
    
    for i, task in enumerate(tasks, 1):
        message += f"{i}. **{task.title}** ({task.agent_type.replace('_', ' ').title()})\n"
        message += f"   - Priority: {task.priority.title()}\n"
        message += f"   - Status: {task.status.title()}\n\n"
    
    message += f"""**Expected Deliverables:**
{chr(10).join(f"- {d}" for d in analysis.get('deliverables', []))}

**Next Steps:**
The specialized agents will now execute their tasks in the optimal sequence. You'll see real-time updates as each agent completes their work.
"""
    
    return message
