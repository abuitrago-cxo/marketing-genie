"""
Project Orchestrator & Coordination Graph

This graph specializes in coordinating and orchestrating all other specialized graphs.
It manages dependencies, resource allocation, conflict resolution, and optimization
of the overall project management workflow.

Integrated with:
- All available tools for comprehensive coordination
- Memory system for orchestration patterns and optimization strategies
- MCP tools for advanced project management capabilities
"""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from src.agent.state import ProjectOrchestratorState
from memory.integration_pattern import IntegratedNodePattern
from agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ProjectOrchestratorGraph:
    """
    Specialized graph for project orchestration and coordination.

    This graph follows the established pattern with 5 integrated nodes:
    1. route_orchestration - Analyze project context and determine coordination strategy
    2. analyze_dependencies - Map dependencies between graphs and tasks
    3. allocate_resources - Optimize resource allocation across graphs
    4. resolve_conflicts - Handle conflicts and bottlenecks
    5. optimize_coordination - Generate final coordination recommendations
    """

    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the project orchestrator graph"""

        # Create the graph
        workflow = StateGraph(ProjectOrchestratorState)

        # Add nodes
        workflow.add_node("route_orchestration", self._create_route_orchestration_node())
        workflow.add_node("analyze_dependencies", self._create_analyze_dependencies_node())
        workflow.add_node("allocate_resources", self._create_allocate_resources_node())
        workflow.add_node("resolve_conflicts", self._create_resolve_conflicts_node())
        workflow.add_node("optimize_coordination", self._create_optimize_coordination_node())

        # Define the flow
        workflow.set_entry_point("route_orchestration")
        workflow.add_edge("route_orchestration", "analyze_dependencies")
        workflow.add_edge("analyze_dependencies", "allocate_resources")
        workflow.add_edge("allocate_resources", "resolve_conflicts")
        workflow.add_edge("resolve_conflicts", "optimize_coordination")
        workflow.add_edge("optimize_coordination", END)

        self.graph = workflow.compile(name="project-orchestrator-specialist")
        return self.graph

    def _create_route_orchestration_node(self):
        """Create the orchestration routing node with integrated pattern"""

        async def route_orchestration_logic(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            """Analyze project context and determine coordination strategy"""

            project_context = state.get("project_context", {})

            # Analyze project complexity and scope
            project_size = project_context.get("size", "medium")  # small, medium, large, enterprise
            team_size = project_context.get("team_size", 5)
            timeline_weeks = project_context.get("timeline_weeks", 12)

            # Determine available graphs based on project needs
            available_graphs = [
                "codebase_analysis",
                "documentation_analysis",
                "task_planning",
                "research_analysis",
                "qa_testing"
            ]

            # Determine coordination strategy based on complexity
            if project_size == "enterprise" or team_size > 10 or timeline_weeks > 24:
                coordination_strategy = "hierarchical_coordination"
                orchestration_approach = "centralized_control"
            elif project_size == "large" or team_size > 5 or timeline_weeks > 12:
                coordination_strategy = "matrix_coordination"
                orchestration_approach = "distributed_control"
            else:
                coordination_strategy = "simple_coordination"
                orchestration_approach = "autonomous_execution"

            # Set initial execution status for all graphs
            execution_status = {}
            for graph in available_graphs:
                execution_status[graph] = {
                    "status": "pending",
                    "priority": "medium",
                    "estimated_duration": "1-2 weeks",
                    "dependencies": [],
                    "resource_requirements": {"cpu": "medium", "memory": "medium", "team": 1}
                }

            # Set priorities based on typical project flow
            execution_status["task_planning"]["priority"] = "high"
            execution_status["task_planning"]["dependencies"] = []

            execution_status["codebase_analysis"]["priority"] = "high"
            execution_status["codebase_analysis"]["dependencies"] = ["task_planning"]

            execution_status["documentation_analysis"]["priority"] = "medium"
            execution_status["documentation_analysis"]["dependencies"] = ["codebase_analysis"]

            execution_status["research_analysis"]["priority"] = "medium"
            execution_status["research_analysis"]["dependencies"] = []

            execution_status["qa_testing"]["priority"] = "high"
            execution_status["qa_testing"]["dependencies"] = ["codebase_analysis", "documentation_analysis"]

            # Generate coordination plan
            coordination_plan = {
                "strategy": coordination_strategy,
                "approach": orchestration_approach,
                "total_graphs": len(available_graphs),
                "parallel_execution_capacity": min(team_size // 2, 3),
                "estimated_total_duration": f"{timeline_weeks} weeks",
                "coordination_overhead": "15%" if coordination_strategy == "hierarchical_coordination" else "10%"
            }

            state["active_graphs"] = available_graphs
            state["coordination_plan"] = coordination_plan
            state["execution_status"] = execution_status
            state["orchestration_strategy"] = coordination_strategy
            state["orchestration_stage"] = "routing_complete"
            state["orchestration_progress"] = 0.2

            logger.info(f"Orchestration routing complete. Strategy: {coordination_strategy}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="route_orchestration",
            agent_id="project_orchestrator",
            required_tools=["project_management"],
            memory_types=["orchestration_pattern", "coordination_strategy"],
            cache_ttl=1800
        )

        async def integrated_route_orchestration(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            await pattern.setup()

            cache_key = f"route_orchestration_{hash(str(state.get('project_context', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=route_orchestration_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed orchestration for project: {state.get('project_context', {}).get('name', 'unknown')}",
                memory_type="orchestration_routing",
                importance_score=0.8
            )

            return result or state

        return integrated_route_orchestration

    def _create_analyze_dependencies_node(self):
        """Create the dependency analysis node with integrated pattern"""

        async def analyze_dependencies_logic(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            """Map dependencies between graphs and tasks"""

            active_graphs = state.get("active_graphs", [])
            execution_status = state.get("execution_status", {})

            # Analyze dependencies between graphs
            dependency_matrix = {}

            for graph in active_graphs:
                dependencies = execution_status.get(graph, {}).get("dependencies", [])
                dependency_matrix[graph] = {
                    "direct_dependencies": dependencies,
                    "dependent_graphs": [],
                    "dependency_level": 0,
                    "can_start_immediately": len(dependencies) == 0
                }

            # Calculate which graphs depend on each graph
            for graph in active_graphs:
                for other_graph in active_graphs:
                    if graph in execution_status.get(other_graph, {}).get("dependencies", []):
                        dependency_matrix[graph]["dependent_graphs"].append(other_graph)

            # Calculate dependency levels (topological ordering)
            def calculate_dependency_level(graph, visited=None):
                if visited is None:
                    visited = set()

                if graph in visited:
                    return 0  # Circular dependency, treat as level 0

                visited.add(graph)
                dependencies = dependency_matrix[graph]["direct_dependencies"]

                if not dependencies:
                    return 0

                max_level = 0
                for dep in dependencies:
                    if dep in dependency_matrix:
                        dep_level = calculate_dependency_level(dep, visited.copy())
                        max_level = max(max_level, dep_level + 1)

                return max_level

            for graph in active_graphs:
                dependency_matrix[graph]["dependency_level"] = calculate_dependency_level(graph)

            # Identify critical path
            critical_path = []
            current_level = 0
            max_level = max(dep["dependency_level"] for dep in dependency_matrix.values())

            while current_level <= max_level:
                level_graphs = [graph for graph, dep in dependency_matrix.items()
                              if dep["dependency_level"] == current_level]
                if level_graphs:
                    # Choose the graph with most dependents as critical
                    critical_graph = max(level_graphs,
                                       key=lambda g: len(dependency_matrix[g]["dependent_graphs"]))
                    critical_path.append(critical_graph)
                current_level += 1

            # Calculate execution phases
            execution_phases = {}
            for level in range(max_level + 1):
                phase_graphs = [graph for graph, dep in dependency_matrix.items()
                              if dep["dependency_level"] == level]
                if phase_graphs:
                    execution_phases[f"phase_{level + 1}"] = {
                        "graphs": phase_graphs,
                        "can_run_parallel": len(phase_graphs) > 1,
                        "estimated_duration": "1-2 weeks",
                        "resource_requirements": sum(
                            execution_status.get(g, {}).get("resource_requirements", {}).get("team", 1)
                            for g in phase_graphs
                        )
                    }

            dependency_analysis = {
                "dependency_matrix": dependency_matrix,
                "critical_path": critical_path,
                "execution_phases": execution_phases,
                "total_phases": len(execution_phases),
                "max_parallel_graphs": max(len(phase["graphs"]) for phase in execution_phases.values()),
                "dependency_complexity": "high" if max_level > 2 else "medium" if max_level > 1 else "low"
            }

            state["graph_dependencies"] = dependency_analysis
            state["orchestration_stage"] = "dependencies_analyzed"
            state["orchestration_progress"] = 0.4

            logger.info(f"Dependency analysis complete. Critical path: {len(critical_path)} graphs")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="analyze_dependencies",
            agent_id="project_orchestrator",
            required_tools=["project_management"],
            memory_types=["dependency_pattern", "execution_template"],
            cache_ttl=1200
        )

        async def integrated_analyze_dependencies(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            await pattern.setup()

            cache_key = f"dependencies_{hash(str(state.get('active_graphs', [])))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=analyze_dependencies_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed dependencies for {len(state.get('active_graphs', []))} graphs",
                memory_type="dependency_analysis",
                importance_score=0.9
            )

            return result or state

        return integrated_analyze_dependencies

    def _create_allocate_resources_node(self):
        """Create the resource allocation node with integrated pattern"""

        async def allocate_resources_logic(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            """Optimize resource allocation across graphs"""

            project_context = state.get("project_context", {})
            graph_dependencies = state.get("graph_dependencies", {})
            execution_status = state.get("execution_status", {})

            # Available resources
            total_team_size = project_context.get("team_size", 5)
            available_compute = project_context.get("compute_resources", "medium")
            budget_constraints = project_context.get("budget_level", "standard")

            # Calculate resource requirements
            execution_phases = graph_dependencies.get("execution_phases", {})

            resource_allocation = {}

            for phase_name, phase_info in execution_phases.items():
                phase_graphs = phase_info["graphs"]
                total_team_needed = phase_info["resource_requirements"]

                # Allocate team members
                if total_team_needed <= total_team_size:
                    # Can run all graphs in parallel
                    team_per_graph = max(1, total_team_size // len(phase_graphs))
                    allocation_strategy = "parallel_execution"
                else:
                    # Need to serialize some graphs
                    team_per_graph = 1
                    allocation_strategy = "sequential_execution"

                phase_allocation = {
                    "allocation_strategy": allocation_strategy,
                    "total_team_allocated": min(total_team_needed, total_team_size),
                    "graphs": {}
                }

                for graph in phase_graphs:
                    graph_status = execution_status.get(graph, {})
                    priority = graph_status.get("priority", "medium")

                    # Allocate based on priority
                    if priority == "high":
                        allocated_team = min(team_per_graph + 1, total_team_size // 2)
                    elif priority == "medium":
                        allocated_team = team_per_graph
                    else:
                        allocated_team = max(1, team_per_graph - 1)

                    phase_allocation["graphs"][graph] = {
                        "team_members": allocated_team,
                        "compute_level": available_compute,
                        "priority_level": priority,
                        "estimated_start": f"Week {list(execution_phases.keys()).index(phase_name) * 2 + 1}",
                        "estimated_duration": graph_status.get("estimated_duration", "1-2 weeks")
                    }

                resource_allocation[phase_name] = phase_allocation

            # Calculate resource utilization
            total_allocated_team = sum(
                phase["total_team_allocated"] for phase in resource_allocation.values()
            )
            avg_utilization = (total_allocated_team / len(resource_allocation)) / total_team_size * 100

            # Resource optimization recommendations
            optimization_recommendations = []

            if avg_utilization > 90:
                optimization_recommendations.append({
                    "category": "overallocation",
                    "priority": "high",
                    "recommendation": "Consider extending timeline or adding team members",
                    "rationale": f"Resource utilization at {avg_utilization:.1f}% may cause bottlenecks"
                })
            elif avg_utilization < 60:
                optimization_recommendations.append({
                    "category": "underutilization",
                    "priority": "medium",
                    "recommendation": "Consider parallel execution or additional tasks",
                    "rationale": f"Resource utilization at {avg_utilization:.1f}% indicates capacity for more work"
                })

            # Budget optimization
            if budget_constraints == "limited":
                optimization_recommendations.append({
                    "category": "budget",
                    "priority": "medium",
                    "recommendation": "Prioritize high-impact graphs and defer nice-to-have analyses",
                    "rationale": "Limited budget requires focus on essential deliverables"
                })

            resource_allocation_result = {
                "resource_allocation": resource_allocation,
                "utilization_metrics": {
                    "avg_team_utilization": round(avg_utilization, 1),
                    "peak_team_requirement": max(phase["total_team_allocated"] for phase in resource_allocation.values()),
                    "total_phases": len(resource_allocation),
                    "parallel_capacity": total_team_size
                },
                "optimization_recommendations": optimization_recommendations,
                "allocation_efficiency": round(min(avg_utilization / 80 * 10, 10), 1)  # Optimal around 80%
            }

            state["resource_allocation"] = resource_allocation_result
            state["orchestration_stage"] = "resources_allocated"
            state["orchestration_progress"] = 0.6

            logger.info(f"Resource allocation complete. Utilization: {avg_utilization:.1f}%")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="allocate_resources",
            agent_id="project_orchestrator",
            required_tools=["project_management"],
            memory_types=["resource_pattern", "allocation_strategy"],
            cache_ttl=900
        )

        async def integrated_allocate_resources(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            await pattern.setup()

            cache_key = f"resources_{hash(str(state.get('graph_dependencies', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=allocate_resources_logic,
                cache_key=cache_key,
                memory_content=f"Allocated resources with {state.get('resource_allocation', {}).get('utilization_metrics', {}).get('avg_team_utilization', 0):.1f}% utilization",
                memory_type="resource_allocation",
                importance_score=0.8
            )

            return result or state

        return integrated_allocate_resources

    def _create_resolve_conflicts_node(self):
        """Create the conflict resolution node with integrated pattern"""

        async def resolve_conflicts_logic(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            """Handle conflicts and bottlenecks"""

            resource_allocation = state.get("resource_allocation", {})
            graph_dependencies = state.get("graph_dependencies", {})

            # Identify potential conflicts
            conflicts = []

            # Resource conflicts
            utilization_metrics = resource_allocation.get("utilization_metrics", {})
            if utilization_metrics.get("avg_team_utilization", 0) > 90:
                conflicts.append({
                    "type": "resource_overallocation",
                    "severity": "high",
                    "description": "Team utilization exceeds 90%, risk of burnout and delays",
                    "affected_graphs": list(graph_dependencies.get("dependency_matrix", {}).keys()),
                    "impact": "timeline_delay"
                })

            # Dependency conflicts
            dependency_matrix = graph_dependencies.get("dependency_matrix", {})
            for graph, deps in dependency_matrix.items():
                if len(deps["direct_dependencies"]) > 2:
                    conflicts.append({
                        "type": "dependency_bottleneck",
                        "severity": "medium",
                        "description": f"{graph} has multiple dependencies, potential bottleneck",
                        "affected_graphs": [graph] + deps["direct_dependencies"],
                        "impact": "coordination_complexity"
                    })

            # Timeline conflicts
            execution_phases = graph_dependencies.get("execution_phases", {})
            if len(execution_phases) > 4:
                conflicts.append({
                    "type": "timeline_complexity",
                    "severity": "medium",
                    "description": "Multiple execution phases may complicate coordination",
                    "affected_graphs": list(dependency_matrix.keys()),
                    "impact": "management_overhead"
                })

            # Generate conflict resolution strategies
            resolution_strategies = {}

            for conflict in conflicts:
                conflict_type = conflict["type"]

                if conflict_type == "resource_overallocation":
                    resolution_strategies[conflict_type] = {
                        "strategy": "timeline_extension",
                        "actions": [
                            "Extend project timeline by 20-30%",
                            "Implement staggered start dates for non-critical graphs",
                            "Consider hiring additional team members",
                            "Reduce scope of lower-priority analyses"
                        ],
                        "estimated_impact": "Reduces utilization to 70-80%",
                        "implementation_effort": "medium"
                    }

                elif conflict_type == "dependency_bottleneck":
                    resolution_strategies[conflict_type] = {
                        "strategy": "dependency_optimization",
                        "actions": [
                            "Parallelize independent components of dependent graphs",
                            "Create intermediate deliverables to unblock dependencies",
                            "Assign senior team members to critical path items",
                            "Implement daily coordination meetings"
                        ],
                        "estimated_impact": "Reduces dependency wait time by 30-50%",
                        "implementation_effort": "low"
                    }

                elif conflict_type == "timeline_complexity":
                    resolution_strategies[conflict_type] = {
                        "strategy": "coordination_simplification",
                        "actions": [
                            "Combine compatible graphs into single execution phases",
                            "Implement automated status tracking and reporting",
                            "Designate phase coordinators for each execution phase",
                            "Create clear handoff procedures between phases"
                        ],
                        "estimated_impact": "Reduces coordination overhead by 40%",
                        "implementation_effort": "medium"
                    }

            # Calculate conflict resolution score
            total_conflicts = len(conflicts)
            high_severity_conflicts = len([c for c in conflicts if c["severity"] == "high"])

            if total_conflicts == 0:
                resolution_score = 10.0
            elif high_severity_conflicts == 0:
                resolution_score = max(8.0 - total_conflicts * 0.5, 5.0)
            else:
                resolution_score = max(6.0 - high_severity_conflicts * 1.0 - (total_conflicts - high_severity_conflicts) * 0.5, 2.0)

            conflict_resolution = {
                "identified_conflicts": conflicts,
                "resolution_strategies": resolution_strategies,
                "total_conflicts": total_conflicts,
                "high_severity_conflicts": high_severity_conflicts,
                "resolution_score": round(resolution_score, 1),
                "resolution_complexity": "high" if total_conflicts > 3 else "medium" if total_conflicts > 1 else "low"
            }

            state["conflict_resolution"] = conflict_resolution
            state["orchestration_stage"] = "conflicts_resolved"
            state["orchestration_progress"] = 0.8

            logger.info(f"Conflict resolution complete. {total_conflicts} conflicts identified")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="resolve_conflicts",
            agent_id="project_orchestrator",
            required_tools=[],
            memory_types=["conflict_pattern", "resolution_strategy"],
            cache_ttl=600
        )

        async def integrated_resolve_conflicts(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            await pattern.setup()

            cache_key = f"conflicts_{hash(str(state.get('resource_allocation', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=resolve_conflicts_logic,
                cache_key=cache_key,
                memory_content=f"Resolved {len(state.get('conflict_resolution', {}).get('identified_conflicts', []))} conflicts",
                memory_type="conflict_resolution",
                importance_score=0.8
            )

            return result or state

        return integrated_resolve_conflicts

    def _create_optimize_coordination_node(self):
        """Create the coordination optimization node with integrated pattern"""

        async def optimize_coordination_logic(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            """Generate final coordination recommendations"""

            coordination_plan = state.get("coordination_plan", {})
            resource_allocation = state.get("resource_allocation", {})
            conflict_resolution = state.get("conflict_resolution", {})
            graph_dependencies = state.get("graph_dependencies", {})

            # Generate optimization recommendations
            optimization_recommendations = []

            # Resource optimization
            utilization = resource_allocation.get("utilization_metrics", {}).get("avg_team_utilization", 0)
            if utilization < 70:
                optimization_recommendations.append({
                    "category": "resource_optimization",
                    "priority": "medium",
                    "recommendation": "Increase parallel execution to improve resource utilization",
                    "rationale": f"Current utilization at {utilization:.1f}% indicates unused capacity",
                    "expected_benefit": "15-25% faster completion"
                })

            # Coordination efficiency
            total_phases = graph_dependencies.get("total_phases", 1)
            if total_phases > 3:
                optimization_recommendations.append({
                    "category": "coordination_efficiency",
                    "priority": "medium",
                    "recommendation": "Implement automated coordination tools and dashboards",
                    "rationale": f"{total_phases} execution phases require enhanced coordination",
                    "expected_benefit": "30% reduction in coordination overhead"
                })

            # Conflict prevention
            if conflict_resolution.get("total_conflicts", 0) > 2:
                optimization_recommendations.append({
                    "category": "conflict_prevention",
                    "priority": "high",
                    "recommendation": "Implement proactive conflict detection and early warning systems",
                    "rationale": "Multiple conflicts detected suggest need for preventive measures",
                    "expected_benefit": "50% reduction in future conflicts"
                })

            # Communication optimization
            team_size = len(state.get("active_graphs", [])) * 2  # Estimate team size
            if team_size > 8:
                optimization_recommendations.append({
                    "category": "communication",
                    "priority": "medium",
                    "recommendation": "Establish structured communication protocols and regular sync meetings",
                    "rationale": f"Large team size ({team_size}) requires formal communication structure",
                    "expected_benefit": "25% improvement in coordination efficiency"
                })

            # Technology optimization
            optimization_recommendations.append({
                "category": "technology",
                "priority": "low",
                "recommendation": "Implement project management tools with real-time tracking",
                "rationale": "Technology can automate routine coordination tasks",
                "expected_benefit": "20% reduction in manual coordination effort"
            })

            # Calculate overall coordination efficiency
            base_efficiency = 10.0

            # Deduct for conflicts
            conflict_penalty = conflict_resolution.get("total_conflicts", 0) * 0.5
            base_efficiency -= conflict_penalty

            # Deduct for resource inefficiency
            if utilization > 90:
                base_efficiency -= 1.5  # Overutilization penalty
            elif utilization < 60:
                base_efficiency -= 1.0  # Underutilization penalty

            # Deduct for complexity
            complexity_penalty = max(0, (total_phases - 2) * 0.3)
            base_efficiency -= complexity_penalty

            # Ensure minimum score
            efficiency_score = max(base_efficiency, 3.0)

            # Generate coordination summary
            coordination_summary = {
                "orchestration_strategy": coordination_plan.get("strategy", "unknown"),
                "total_graphs": len(state.get("active_graphs", [])),
                "execution_phases": total_phases,
                "resource_utilization": utilization,
                "conflict_count": conflict_resolution.get("total_conflicts", 0),
                "efficiency_score": round(efficiency_score, 1),
                "coordination_complexity": "high" if total_phases > 3 else "medium" if total_phases > 1 else "low"
            }

            # Generate final optimization suggestions
            optimization_suggestions = []

            # Priority-based suggestions
            high_priority_recs = [r for r in optimization_recommendations if r["priority"] == "high"]
            if high_priority_recs:
                optimization_suggestions.extend(high_priority_recs[:3])  # Top 3 high priority

            medium_priority_recs = [r for r in optimization_recommendations if r["priority"] == "medium"]
            optimization_suggestions.extend(medium_priority_recs[:2])  # Top 2 medium priority

            low_priority_recs = [r for r in optimization_recommendations if r["priority"] == "low"]
            optimization_suggestions.extend(low_priority_recs[:1])  # Top 1 low priority

            final_coordination = {
                "coordination_summary": coordination_summary,
                "optimization_recommendations": optimization_recommendations,
                "optimization_suggestions": optimization_suggestions,
                "efficiency_score": round(efficiency_score, 1),
                "confidence_level": "high" if efficiency_score >= 8 else "medium" if efficiency_score >= 6 else "low",
                "next_steps": [
                    "Review and approve coordination plan",
                    "Implement high-priority optimization recommendations",
                    "Set up monitoring and tracking systems",
                    "Schedule regular coordination review meetings"
                ]
            }

            state["coordination_recommendations"] = optimization_recommendations
            state["optimization_suggestions"] = optimization_suggestions
            state["final_coordination"] = final_coordination
            state["efficiency_score"] = efficiency_score
            state["resource_utilization"] = utilization
            state["orchestration_stage"] = "complete"
            state["orchestration_progress"] = 1.0

            logger.info(f"Coordination optimization complete. Efficiency score: {efficiency_score}/10")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="optimize_coordination",
            agent_id="project_orchestrator",
            required_tools=[],
            memory_types=["optimization_pattern", "coordination_best_practice"],
            cache_ttl=300
        )

        async def integrated_optimize_coordination(state: ProjectOrchestratorState) -> ProjectOrchestratorState:
            await pattern.setup()

            cache_key = f"optimize_{hash(str(state.get('coordination_plan', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=optimize_coordination_logic,
                cache_key=cache_key,
                memory_content=f"Optimized coordination with efficiency score {state.get('efficiency_score', 0)}",
                memory_type="coordination_optimization",
                importance_score=1.0
            )

            return result or state

        return integrated_optimize_coordination
