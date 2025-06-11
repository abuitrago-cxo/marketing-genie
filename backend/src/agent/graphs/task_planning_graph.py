"""
Task Planning Analysis Graph

This graph specializes in intelligent task planning and project breakdown.
It analyzes project requirements, creates task breakdowns, estimates resources,
and generates comprehensive project plans with dependencies and timelines.

Integrated with:
- ProjectManagementTool for task creation and management
- Memory system for planning patterns and best practices
- MCP tools for advanced planning and estimation
"""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from src.agent.state import TaskPlanningState
from memory.integration_pattern import IntegratedNodePattern
from agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class TaskPlanningGraph:
    """
    Specialized graph for task planning and project breakdown analysis.

    This graph follows the established pattern with 5 integrated nodes:
    1. route_planning - Analyze project scope and determine planning approach
    2. analyze_requirements - Break down and analyze project requirements
    3. generate_task_breakdown - Create detailed task breakdown structure
    4. estimate_resources - Estimate resources, timelines, and dependencies
    5. finalize_planning - Generate final planning recommendations
    """

    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the task planning analysis graph"""

        # Create the graph
        workflow = StateGraph(TaskPlanningState)

        # Add nodes
        workflow.add_node("route_planning", self._create_route_planning_node())
        workflow.add_node("analyze_requirements", self._create_analyze_requirements_node())
        workflow.add_node("generate_task_breakdown", self._create_generate_task_breakdown_node())
        workflow.add_node("estimate_resources", self._create_estimate_resources_node())
        workflow.add_node("finalize_planning", self._create_finalize_planning_node())

        # Define the flow
        workflow.set_entry_point("route_planning")
        workflow.add_edge("route_planning", "analyze_requirements")
        workflow.add_edge("analyze_requirements", "generate_task_breakdown")
        workflow.add_edge("generate_task_breakdown", "estimate_resources")
        workflow.add_edge("estimate_resources", "finalize_planning")
        workflow.add_edge("finalize_planning", END)

        self.graph = workflow.compile(name="task-planning-specialist")
        return self.graph

    def _create_route_planning_node(self):
        """Create the planning routing node with integrated pattern"""

        async def route_planning_logic(state: TaskPlanningState) -> TaskPlanningState:
            """Analyze project scope and determine planning approach"""

            project_scope = state.get("project_scope", "")

            # Analyze project complexity and type
            complexity_indicators = [
                "microservice", "distributed", "enterprise", "scalable",
                "multi-platform", "integration", "migration", "legacy"
            ]

            complexity_score = sum(1 for indicator in complexity_indicators
                                 if indicator.lower() in project_scope.lower())

            # Determine planning approach based on complexity
            if complexity_score >= 4:
                planning_approach = "enterprise"
                methodology = "hybrid_agile_waterfall"
            elif complexity_score >= 2:
                planning_approach = "standard"
                methodology = "agile_scrum"
            else:
                planning_approach = "simple"
                methodology = "kanban"

            # Set planning context
            state["planning_approach"] = planning_approach
            state["methodology"] = methodology
            state["complexity_score"] = complexity_score
            state["planning_stage"] = "routing_complete"
            state["planning_progress"] = 0.2

            logger.info(f"Planning routing complete. Approach: {planning_approach}, Methodology: {methodology}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="route_planning",
            agent_id="task_planner",
            required_tools=["project_management"],
            memory_types=["planning_pattern", "methodology_best_practice"],
            cache_ttl=1800
        )

        async def integrated_route_planning(state: TaskPlanningState) -> TaskPlanningState:
            await pattern.setup()

            cache_key = f"route_planning_{hash(state.get('project_scope', ''))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=route_planning_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed project scope: {state.get('project_scope', 'unknown')}",
                memory_type="planning_routing",
                importance_score=0.7
            )

            return result or state

        return integrated_route_planning

    def _create_analyze_requirements_node(self):
        """Create the requirements analysis node with integrated pattern"""

        async def analyze_requirements_logic(state: TaskPlanningState) -> TaskPlanningState:
            """Break down and analyze project requirements"""

            project_scope = state.get("project_scope", "")
            planning_approach = state.get("planning_approach", "standard")

            # Extract functional requirements
            functional_keywords = [
                "user authentication", "data processing", "api integration",
                "user interface", "database", "reporting", "notification",
                "search", "analytics", "security", "performance"
            ]

            functional_requirements = []
            for keyword in functional_keywords:
                if keyword.lower() in project_scope.lower():
                    functional_requirements.append({
                        "type": "functional",
                        "category": keyword,
                        "priority": "high" if keyword in ["security", "authentication"] else "medium",
                        "complexity": "high" if keyword in ["api integration", "analytics"] else "medium"
                    })

            # Extract non-functional requirements
            non_functional_requirements = [
                {"type": "performance", "requirement": "Response time < 2s", "priority": "high"},
                {"type": "scalability", "requirement": "Support 1000+ concurrent users", "priority": "medium"},
                {"type": "security", "requirement": "Data encryption and secure authentication", "priority": "high"},
                {"type": "availability", "requirement": "99.9% uptime", "priority": "high"},
                {"type": "maintainability", "requirement": "Modular and documented code", "priority": "medium"}
            ]

            # Combine requirements
            all_requirements = functional_requirements + non_functional_requirements

            # Categorize by priority
            high_priority = [req for req in all_requirements if req.get("priority") == "high"]
            medium_priority = [req for req in all_requirements if req.get("priority") == "medium"]
            low_priority = [req for req in all_requirements if req.get("priority") == "low"]

            requirements_analysis = {
                "total_requirements": len(all_requirements),
                "functional_count": len(functional_requirements),
                "non_functional_count": len(non_functional_requirements),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority),
                "low_priority_count": len(low_priority),
                "complexity_distribution": {
                    "high": len([req for req in all_requirements if req.get("complexity") == "high"]),
                    "medium": len([req for req in all_requirements if req.get("complexity") == "medium"]),
                    "low": len([req for req in all_requirements if req.get("complexity") == "low"])
                }
            }

            state["requirements"] = all_requirements
            state["requirements_analysis"] = requirements_analysis
            state["planning_stage"] = "requirements_complete"
            state["planning_progress"] = 0.4

            logger.info(f"Requirements analysis complete. Total: {len(all_requirements)} requirements")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="analyze_requirements",
            agent_id="task_planner",
            required_tools=["project_management"],
            memory_types=["requirements_pattern", "analysis_template"],
            cache_ttl=1200
        )

        async def integrated_analyze_requirements(state: TaskPlanningState) -> TaskPlanningState:
            await pattern.setup()

            cache_key = f"requirements_{hash(str(state.get('project_scope', '')))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=analyze_requirements_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed {len(state.get('requirements', []))} requirements",
                memory_type="requirements_analysis",
                importance_score=0.8
            )

            return result or state

        return integrated_analyze_requirements

    def _create_generate_task_breakdown_node(self):
        """Create the task breakdown generation node with integrated pattern"""

        async def generate_task_breakdown_logic(state: TaskPlanningState) -> TaskPlanningState:
            """Create detailed task breakdown structure"""

            requirements = state.get("requirements", [])
            methodology = state.get("methodology", "agile_scrum")

            # Generate tasks based on requirements
            tasks = []
            task_id = 1

            # Planning and setup phase
            planning_tasks = [
                {"id": task_id, "name": "Project Setup", "category": "setup", "effort": 8, "priority": "high"},
                {"id": task_id + 1, "name": "Environment Configuration", "category": "setup", "effort": 16, "priority": "high"},
                {"id": task_id + 2, "name": "Team Onboarding", "category": "setup", "effort": 12, "priority": "medium"}
            ]
            tasks.extend(planning_tasks)
            task_id += len(planning_tasks)

            # Development tasks based on requirements
            for req in requirements:
                if req.get("type") == "functional":
                    category = req.get("category", "development")
                    complexity = req.get("complexity", "medium")

                    effort_mapping = {"low": 8, "medium": 16, "high": 32}
                    effort = effort_mapping.get(complexity, 16)

                    task = {
                        "id": task_id,
                        "name": f"Implement {category.title()}",
                        "category": "development",
                        "effort": effort,
                        "priority": req.get("priority", "medium"),
                        "requirement_id": req.get("category")
                    }
                    tasks.append(task)
                    task_id += 1

            # Testing and QA tasks
            testing_tasks = [
                {"id": task_id, "name": "Unit Testing", "category": "testing", "effort": 24, "priority": "high"},
                {"id": task_id + 1, "name": "Integration Testing", "category": "testing", "effort": 16, "priority": "high"},
                {"id": task_id + 2, "name": "Performance Testing", "category": "testing", "effort": 12, "priority": "medium"},
                {"id": task_id + 3, "name": "Security Testing", "category": "testing", "effort": 8, "priority": "high"}
            ]
            tasks.extend(testing_tasks)
            task_id += len(testing_tasks)

            # Deployment and documentation
            final_tasks = [
                {"id": task_id, "name": "Documentation", "category": "documentation", "effort": 16, "priority": "medium"},
                {"id": task_id + 1, "name": "Deployment Setup", "category": "deployment", "effort": 12, "priority": "high"},
                {"id": task_id + 2, "name": "Production Deployment", "category": "deployment", "effort": 8, "priority": "high"}
            ]
            tasks.extend(final_tasks)

            # Generate dependencies
            dependencies = []
            for i, task in enumerate(tasks):
                if task["category"] == "development" and i > 0:
                    # Development tasks depend on setup
                    setup_tasks = [t for t in tasks if t["category"] == "setup"]
                    if setup_tasks:
                        dependencies.append({
                            "task_id": task["id"],
                            "depends_on": setup_tasks[0]["id"],
                            "type": "finish_to_start"
                        })
                elif task["category"] == "testing":
                    # Testing depends on development
                    dev_tasks = [t for t in tasks if t["category"] == "development"]
                    if dev_tasks:
                        dependencies.append({
                            "task_id": task["id"],
                            "depends_on": dev_tasks[-1]["id"],
                            "type": "finish_to_start"
                        })

            task_breakdown = {
                "total_tasks": len(tasks),
                "total_effort_hours": sum(task["effort"] for task in tasks),
                "categories": list(set(task["category"] for task in tasks)),
                "high_priority_tasks": len([t for t in tasks if t["priority"] == "high"]),
                "critical_path_length": len([t for t in tasks if t["priority"] == "high"])
            }

            state["generated_tasks"] = tasks
            state["dependencies"] = dependencies
            state["task_breakdown"] = task_breakdown
            state["planning_stage"] = "breakdown_complete"
            state["planning_progress"] = 0.6

            logger.info(f"Task breakdown complete. Generated {len(tasks)} tasks")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="generate_task_breakdown",
            agent_id="task_planner",
            required_tools=["project_management"],
            memory_types=["task_pattern", "breakdown_template"],
            cache_ttl=900
        )

        async def integrated_generate_task_breakdown(state: TaskPlanningState) -> TaskPlanningState:
            await pattern.setup()

            cache_key = f"breakdown_{hash(str(state.get('requirements', [])))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=generate_task_breakdown_logic,
                cache_key=cache_key,
                memory_content=f"Generated {len(state.get('generated_tasks', []))} tasks",
                memory_type="task_breakdown",
                importance_score=0.9
            )

            return result or state

        return integrated_generate_task_breakdown

    def _create_estimate_resources_node(self):
        """Create the resource estimation node with integrated pattern"""

        async def estimate_resources_logic(state: TaskPlanningState) -> TaskPlanningState:
            """Estimate resources, timelines, and dependencies"""

            tasks = state.get("generated_tasks", [])
            methodology = state.get("methodology", "agile_scrum")

            # Calculate resource estimates
            total_effort_hours = sum(task["effort"] for task in tasks)

            # Assume team of 3-5 developers working 6 hours/day on development
            team_size = 4
            productive_hours_per_day = 6
            working_days_per_week = 5

            # Add overhead for meetings, planning, etc.
            overhead_factor = 1.3 if methodology == "agile_scrum" else 1.2

            estimated_weeks = (total_effort_hours * overhead_factor) / (team_size * productive_hours_per_day * working_days_per_week)

            # Generate milestones
            milestones = [
                {
                    "id": 1,
                    "name": "Project Setup Complete",
                    "week": 1,
                    "deliverables": ["Environment setup", "Team onboarding"],
                    "criteria": "All team members can access development environment"
                },
                {
                    "id": 2,
                    "name": "Core Features Complete",
                    "week": int(estimated_weeks * 0.6),
                    "deliverables": ["Core functionality", "Basic UI"],
                    "criteria": "Main user workflows functional"
                },
                {
                    "id": 3,
                    "name": "Testing Complete",
                    "week": int(estimated_weeks * 0.8),
                    "deliverables": ["All tests passing", "Performance validated"],
                    "criteria": "Quality gates met"
                },
                {
                    "id": 4,
                    "name": "Production Ready",
                    "week": int(estimated_weeks),
                    "deliverables": ["Documentation", "Deployment"],
                    "criteria": "Ready for production deployment"
                }
            ]

            # Resource allocation
            resource_allocation = {
                "developers": team_size,
                "qa_engineers": 1,
                "devops_engineer": 0.5,
                "project_manager": 0.5,
                "total_team_size": team_size + 2
            }

            # Timeline analysis
            timeline_analysis = {
                "total_effort_hours": total_effort_hours,
                "estimated_weeks": int(estimated_weeks),
                "estimated_months": round(estimated_weeks / 4, 1),
                "team_size": team_size,
                "overhead_factor": overhead_factor,
                "critical_path_weeks": int(estimated_weeks * 0.8),
                "buffer_weeks": int(estimated_weeks * 0.2)
            }

            # Risk assessment
            risk_factors = []
            if total_effort_hours > 500:
                risk_factors.append({"risk": "Large project complexity", "impact": "high", "probability": "medium"})
            if len(tasks) > 20:
                risk_factors.append({"risk": "Task management overhead", "impact": "medium", "probability": "high"})
            if estimated_weeks > 12:
                risk_factors.append({"risk": "Long timeline risks", "impact": "high", "probability": "medium"})

            risk_assessment = {
                "total_risks": len(risk_factors),
                "high_impact_risks": len([r for r in risk_factors if r["impact"] == "high"]),
                "risk_factors": risk_factors,
                "overall_risk_level": "high" if len(risk_factors) >= 3 else "medium" if len(risk_factors) >= 1 else "low"
            }

            state["resource_estimates"] = resource_allocation
            state["timeline_analysis"] = timeline_analysis
            state["milestones"] = milestones
            state["risk_assessment"] = risk_assessment
            state["planning_stage"] = "estimation_complete"
            state["planning_progress"] = 0.8

            logger.info(f"Resource estimation complete. Timeline: {int(estimated_weeks)} weeks")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="estimate_resources",
            agent_id="task_planner",
            required_tools=["project_management"],
            memory_types=["estimation_pattern", "resource_template"],
            cache_ttl=600
        )

        async def integrated_estimate_resources(state: TaskPlanningState) -> TaskPlanningState:
            await pattern.setup()

            cache_key = f"estimation_{hash(str(state.get('generated_tasks', [])))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=estimate_resources_logic,
                cache_key=cache_key,
                memory_content=f"Estimated resources for {len(state.get('generated_tasks', []))} tasks",
                memory_type="resource_estimation",
                importance_score=0.8
            )

            return result or state

        return integrated_estimate_resources

    def _create_finalize_planning_node(self):
        """Create the planning finalization node with integrated pattern"""

        async def finalize_planning_logic(state: TaskPlanningState) -> TaskPlanningState:
            """Generate final planning recommendations"""

            task_breakdown = state.get("task_breakdown", {})
            timeline_analysis = state.get("timeline_analysis", {})
            risk_assessment = state.get("risk_assessment", {})
            milestones = state.get("milestones", [])

            # Generate planning summary
            planning_summary = {
                "project_complexity": state.get("complexity_score", 0),
                "methodology": state.get("methodology", "agile_scrum"),
                "total_tasks": task_breakdown.get("total_tasks", 0),
                "estimated_duration": timeline_analysis.get("estimated_weeks", 0),
                "team_size": timeline_analysis.get("team_size", 4),
                "risk_level": risk_assessment.get("overall_risk_level", "medium"),
                "milestone_count": len(milestones)
            }

            # Generate recommendations
            recommendations = []

            # Methodology recommendations
            if state.get("complexity_score", 0) >= 4:
                recommendations.append({
                    "category": "methodology",
                    "priority": "high",
                    "recommendation": "Consider hybrid Agile-Waterfall approach for complex enterprise project",
                    "rationale": "High complexity requires structured planning with iterative development"
                })

            # Timeline recommendations
            if timeline_analysis.get("estimated_weeks", 0) > 16:
                recommendations.append({
                    "category": "timeline",
                    "priority": "medium",
                    "recommendation": "Break project into smaller releases",
                    "rationale": "Long timelines increase risk and reduce agility"
                })

            # Risk mitigation recommendations
            if risk_assessment.get("overall_risk_level") == "high":
                recommendations.append({
                    "category": "risk",
                    "priority": "high",
                    "recommendation": "Implement weekly risk review meetings",
                    "rationale": "High-risk projects require proactive risk management"
                })

            # Resource recommendations
            if task_breakdown.get("total_effort_hours", 0) > 800:
                recommendations.append({
                    "category": "resources",
                    "priority": "medium",
                    "recommendation": "Consider adding senior developer to team",
                    "rationale": "Large projects benefit from additional expertise"
                })

            # Quality recommendations
            recommendations.append({
                "category": "quality",
                "priority": "high",
                "recommendation": "Implement continuous integration and automated testing",
                "rationale": "Essential for maintaining quality in multi-developer projects"
            })

            # Calculate overall planning score
            planning_score = 10.0

            # Deduct points for risks
            if risk_assessment.get("overall_risk_level") == "high":
                planning_score -= 2.0
            elif risk_assessment.get("overall_risk_level") == "medium":
                planning_score -= 1.0

            # Deduct points for complexity
            complexity_penalty = min(state.get("complexity_score", 0) * 0.3, 2.0)
            planning_score -= complexity_penalty

            # Ensure minimum score
            planning_score = max(planning_score, 5.0)

            final_planning = {
                "planning_summary": planning_summary,
                "recommendations": recommendations,
                "planning_score": round(planning_score, 1),
                "confidence_level": "high" if planning_score >= 8.0 else "medium" if planning_score >= 6.0 else "low",
                "next_steps": [
                    "Review and approve project plan",
                    "Set up development environment",
                    "Begin sprint 0 activities",
                    "Schedule regular team meetings"
                ]
            }

            state["final_planning"] = final_planning
            state["planning_stage"] = "complete"
            state["planning_progress"] = 1.0

            logger.info(f"Planning finalization complete. Score: {planning_score}/10")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="finalize_planning",
            agent_id="task_planner",
            required_tools=["project_management"],
            memory_types=["planning_best_practice", "recommendation_template"],
            cache_ttl=300
        )

        async def integrated_finalize_planning(state: TaskPlanningState) -> TaskPlanningState:
            await pattern.setup()

            cache_key = f"finalize_{hash(str(state.get('task_breakdown', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=finalize_planning_logic,
                cache_key=cache_key,
                memory_content=f"Finalized planning with score {state.get('final_planning', {}).get('planning_score', 0)}",
                memory_type="planning_finalization",
                importance_score=1.0
            )

            return result or state

        return integrated_finalize_planning
