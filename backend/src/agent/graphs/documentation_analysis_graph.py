"""
Documentation Analysis Graph - Specialized Graph 2

This graph provides comprehensive documentation analysis using integrated tools,
memory system, and MCP dynamic tool loading. It analyzes README files, API docs,
code comments, and generates documentation recommendations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END

try:
    from langgraph.checkpoint.postgres import PostgresSaver
except ImportError:
    PostgresSaver = None

from src.agent.state import DocumentationAnalysisState
from agent.tools.registry import ToolRegistry
from memory.integration_pattern import IntegratedNodePattern
from memory import get_memory_manager

logger = logging.getLogger(__name__)

class DocumentationAnalysisGraph:
    """
    Specialized graph for comprehensive documentation analysis.

    This graph integrates:
    - File operations for reading documentation files
    - Web operations for checking external links and references
    - Dynamic MCP tools for documentation quality analysis
    - Long-term memory for documentation patterns and best practices
    - Short-term memory for caching analysis results
    """

    def __init__(self):
        self.graph = None
        self.tool_registry = ToolRegistry()
        self.memory_manager = None

    def create_graph(self) -> StateGraph:
        """Create the documentation analysis graph (synchronous version)"""

        # Create the graph
        workflow = StateGraph(DocumentationAnalysisState)

        # Add nodes with integrated pattern
        workflow.add_node("discover_docs", self._create_discover_docs_node())
        workflow.add_node("analyze_structure", self._create_analyze_structure_node())
        workflow.add_node("evaluate_quality", self._create_evaluate_quality_node())
        workflow.add_node("check_completeness", self._create_check_completeness_node())
        workflow.add_node("generate_recommendations", self._create_generate_recommendations_node())

        # Define the flow
        workflow.set_entry_point("discover_docs")

        workflow.add_edge("discover_docs", "analyze_structure")
        workflow.add_edge("analyze_structure", "evaluate_quality")
        workflow.add_edge("evaluate_quality", "check_completeness")
        workflow.add_edge("check_completeness", "generate_recommendations")
        workflow.add_edge("generate_recommendations", END)

        self.graph = workflow.compile(name="documentation-analysis-specialist")
        return self.graph

    async def initialize(self):
        """Initialize the graph with all components"""
        try:
            # Initialize memory manager
            self.memory_manager = await get_memory_manager()

            # Build the graph
            self.graph = await self._build_graph()

            logger.info("DocumentationAnalysisGraph initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DocumentationAnalysisGraph: {e}")
            raise

    async def _build_graph(self) -> StateGraph:
        """Build the LangGraph with integrated nodes"""

        # Create the graph
        workflow = StateGraph(DocumentationAnalysisState)

        # Add nodes with integrated pattern
        workflow.add_node("discover_docs", self._create_discover_docs_node())
        workflow.add_node("analyze_structure", self._create_analyze_structure_node())
        workflow.add_node("evaluate_quality", self._create_evaluate_quality_node())
        workflow.add_node("check_completeness", self._create_check_completeness_node())
        workflow.add_node("generate_recommendations", self._create_generate_recommendations_node())

        # Define the flow
        workflow.set_entry_point("discover_docs")

        workflow.add_edge("discover_docs", "analyze_structure")
        workflow.add_edge("analyze_structure", "evaluate_quality")
        workflow.add_edge("evaluate_quality", "check_completeness")
        workflow.add_edge("check_completeness", "generate_recommendations")
        workflow.add_edge("generate_recommendations", END)

        # Add checkpointer for state persistence
        pool = await get_database_pool()
        checkpointer = PostgresSaver(pool)

        return workflow.compile(checkpointer=checkpointer)

    def _create_discover_docs_node(self):
        """Create the documentation discovery node"""

        async def discover_docs_logic(state: DocumentationAnalysisState, context: Dict[str, Any]) -> DocumentationAnalysisState:
            """Discover and catalog all documentation files"""

            repo_path = state.get("repository_path", "")

            # Common documentation file patterns
            doc_patterns = [
                "README.md", "README.rst", "README.txt",
                "CHANGELOG.md", "CHANGELOG.rst",
                "CONTRIBUTING.md", "CONTRIBUTING.rst",
                "LICENSE", "LICENSE.md", "LICENSE.txt",
                "docs/", "documentation/", "wiki/",
                "API.md", "api.md", "api.rst",
                "INSTALL.md", "INSTALLATION.md",
                "USAGE.md", "EXAMPLES.md"
            ]

            discovered_docs = {
                "readme_files": [],
                "api_documentation": [],
                "user_guides": [],
                "developer_docs": [],
                "changelog": [],
                "license": [],
                "code_comments": {"total": 0, "documented_functions": 0},
                "missing_docs": []
            }

            # Mock discovery (in real implementation, would use file operations tool)
            discovered_docs["readme_files"] = ["README.md"]
            discovered_docs["api_documentation"] = ["docs/api.md", "docs/endpoints.md"]
            discovered_docs["user_guides"] = ["docs/user-guide.md", "docs/quickstart.md"]
            discovered_docs["developer_docs"] = ["CONTRIBUTING.md", "docs/development.md"]
            discovered_docs["changelog"] = ["CHANGELOG.md"]
            discovered_docs["license"] = ["LICENSE"]
            discovered_docs["code_comments"] = {"total": 150, "documented_functions": 120}

            state["discovered_documentation"] = discovered_docs
            state["analysis_stage"] = "discovery_complete"
            state["analysis_progress"] = 0.2

            logger.info(f"Discovered documentation: {len(discovered_docs)} categories")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="discover_docs",
            agent_id="documentation_analyzer",
            required_tools=["file_operations"],
            memory_types=["documentation_pattern", "file_structure"],
            cache_ttl=1800
        )

        async def integrated_discover_docs(state: DocumentationAnalysisState) -> DocumentationAnalysisState:
            await pattern.setup()

            cache_key = f"discover_{hash(state.get('repository_path', ''))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=discover_docs_logic,
                cache_key=cache_key,
                memory_content=f"Discovered documentation for {state.get('repository_path', 'unknown')}",
                memory_type="documentation_discovery",
                importance_score=0.6
            )

            return result or state

        return integrated_discover_docs

    def _create_analyze_structure_node(self):
        """Create the documentation structure analysis node"""

        async def analyze_structure_logic(state: DocumentationAnalysisState, context: Dict[str, Any]) -> DocumentationAnalysisState:
            """Analyze the structure and organization of documentation"""

            discovered_docs = state.get("discovered_documentation", {})

            structure_analysis = {
                "organization_score": 0,
                "navigation_clarity": 0,
                "hierarchy_depth": 0,
                "cross_references": 0,
                "structure_issues": [],
                "structure_strengths": []
            }

            # Analyze organization
            has_readme = len(discovered_docs.get("readme_files", [])) > 0
            has_api_docs = len(discovered_docs.get("api_documentation", [])) > 0
            has_user_guides = len(discovered_docs.get("user_guides", [])) > 0
            has_dev_docs = len(discovered_docs.get("developer_docs", [])) > 0

            organization_score = 0
            if has_readme:
                organization_score += 3
                structure_analysis["structure_strengths"].append("Has README file")
            else:
                structure_analysis["structure_issues"].append("Missing README file")

            if has_api_docs:
                organization_score += 2
                structure_analysis["structure_strengths"].append("Has API documentation")

            if has_user_guides:
                organization_score += 2
                structure_analysis["structure_strengths"].append("Has user guides")

            if has_dev_docs:
                organization_score += 2
                structure_analysis["structure_strengths"].append("Has developer documentation")

            structure_analysis["organization_score"] = min(organization_score, 10)
            structure_analysis["navigation_clarity"] = 7.5  # Mock score
            structure_analysis["hierarchy_depth"] = 3  # Mock depth
            structure_analysis["cross_references"] = 15  # Mock count

            state["structure_analysis"] = structure_analysis
            state["analysis_stage"] = "structure_complete"
            state["analysis_progress"] = 0.4

            logger.info(f"Structure analysis complete. Score: {structure_analysis['organization_score']}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="analyze_structure",
            agent_id="documentation_analyzer",
            required_tools=["file_operations"],
            memory_types=["structure_pattern", "organization_best_practice"],
            cache_ttl=1200
        )

        async def integrated_analyze_structure(state: DocumentationAnalysisState) -> DocumentationAnalysisState:
            await pattern.setup()

            cache_key = f"structure_{hash(str(state.get('discovered_documentation', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=analyze_structure_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed documentation structure with score {state.get('structure_analysis', {}).get('organization_score', 0)}",
                memory_type="structure_analysis",
                importance_score=0.7
            )

            return result or state

        return integrated_analyze_structure

    def _create_evaluate_quality_node(self):
        """Create the documentation quality evaluation node"""

        async def evaluate_quality_logic(state: DocumentationAnalysisState, context: Dict[str, Any]) -> DocumentationAnalysisState:
            """Evaluate the quality of documentation content"""

            discovered_docs = state.get("discovered_documentation", {})

            quality_metrics = {
                "readability_score": 8.2,
                "completeness_score": 7.5,
                "accuracy_score": 8.8,
                "up_to_date_score": 6.5,
                "examples_quality": 7.0,
                "language_clarity": 8.5,
                "quality_issues": [],
                "quality_strengths": []
            }

            # Evaluate based on discovered documentation
            code_comments = discovered_docs.get("code_comments", {})
            if code_comments.get("total", 0) > 0:
                comment_ratio = code_comments.get("documented_functions", 0) / code_comments.get("total", 1)
                if comment_ratio > 0.8:
                    quality_metrics["quality_strengths"].append("High code documentation coverage")
                elif comment_ratio < 0.5:
                    quality_metrics["quality_issues"].append("Low code documentation coverage")

            # Check for essential documentation
            if not discovered_docs.get("readme_files"):
                quality_metrics["quality_issues"].append("Missing README file")
                quality_metrics["completeness_score"] -= 2

            if not discovered_docs.get("api_documentation"):
                quality_metrics["quality_issues"].append("Missing API documentation")
                quality_metrics["completeness_score"] -= 1.5

            if discovered_docs.get("changelog"):
                quality_metrics["quality_strengths"].append("Has changelog for version tracking")
                quality_metrics["up_to_date_score"] += 1

            # Ensure scores are within bounds
            for key in ["readability_score", "completeness_score", "accuracy_score", "up_to_date_score", "examples_quality", "language_clarity"]:
                quality_metrics[key] = max(0, min(10, quality_metrics[key]))

            state["quality_metrics"] = quality_metrics
            state["analysis_stage"] = "quality_complete"
            state["analysis_progress"] = 0.6

            logger.info(f"Quality evaluation complete. Completeness: {quality_metrics['completeness_score']}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="evaluate_quality",
            agent_id="documentation_analyzer",
            required_tools=["file_operations", "web_operations"],
            memory_types=["quality_pattern", "documentation_best_practice"],
            cache_ttl=900
        )

        async def integrated_evaluate_quality(state: DocumentationAnalysisState) -> DocumentationAnalysisState:
            await pattern.setup()

            cache_key = f"quality_{hash(str(state.get('discovered_documentation', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=evaluate_quality_logic,
                cache_key=cache_key,
                memory_content=f"Evaluated documentation quality with completeness score {state.get('quality_metrics', {}).get('completeness_score', 0)}",
                memory_type="quality_evaluation",
                importance_score=0.8
            )

            return result or state

        return integrated_evaluate_quality

    def _create_check_completeness_node(self):
        """Create the completeness checking node"""

        async def check_completeness_logic(state: DocumentationAnalysisState, context: Dict[str, Any]) -> DocumentationAnalysisState:
            """Check completeness of documentation coverage"""

            discovered_docs = state.get("discovered_documentation", {})

            completeness_check = {
                "coverage_percentage": 0,
                "missing_sections": [],
                "recommended_additions": [],
                "critical_gaps": [],
                "coverage_by_category": {}
            }

            # Define required documentation categories
            required_categories = {
                "readme": {"weight": 20, "found": len(discovered_docs.get("readme_files", [])) > 0},
                "installation": {"weight": 15, "found": False},  # Would check content
                "usage_examples": {"weight": 15, "found": len(discovered_docs.get("user_guides", [])) > 0},
                "api_reference": {"weight": 20, "found": len(discovered_docs.get("api_documentation", [])) > 0},
                "contributing": {"weight": 10, "found": len(discovered_docs.get("developer_docs", [])) > 0},
                "changelog": {"weight": 10, "found": len(discovered_docs.get("changelog", [])) > 0},
                "license": {"weight": 5, "found": len(discovered_docs.get("license", [])) > 0},
                "code_comments": {"weight": 5, "found": discovered_docs.get("code_comments", {}).get("total", 0) > 0}
            }

            total_weight = 0
            achieved_weight = 0

            for category, info in required_categories.items():
                total_weight += info["weight"]
                if info["found"]:
                    achieved_weight += info["weight"]
                    completeness_check["coverage_by_category"][category] = "present"
                else:
                    completeness_check["coverage_by_category"][category] = "missing"
                    if info["weight"] >= 15:
                        completeness_check["critical_gaps"].append(category)
                    else:
                        completeness_check["missing_sections"].append(category)

            completeness_check["coverage_percentage"] = (achieved_weight / total_weight) * 100

            # Generate recommendations based on gaps
            if "readme" in completeness_check["critical_gaps"]:
                completeness_check["recommended_additions"].append("Create comprehensive README with project overview")

            if "api_reference" in completeness_check["critical_gaps"]:
                completeness_check["recommended_additions"].append("Add detailed API documentation")

            if "installation" in completeness_check["missing_sections"]:
                completeness_check["recommended_additions"].append("Add installation instructions")

            state["completeness_check"] = completeness_check
            state["analysis_stage"] = "completeness_complete"
            state["analysis_progress"] = 0.8

            logger.info(f"Completeness check complete. Coverage: {completeness_check['coverage_percentage']:.1f}%")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="check_completeness",
            agent_id="documentation_analyzer",
            required_tools=["file_operations"],
            memory_types=["completeness_pattern", "coverage_standard"],
            cache_ttl=600
        )

        async def integrated_check_completeness(state: DocumentationAnalysisState) -> DocumentationAnalysisState:
            await pattern.setup()

            cache_key = f"completeness_{hash(str(state.get('discovered_documentation', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=check_completeness_logic,
                cache_key=cache_key,
                memory_content=f"Checked documentation completeness: {state.get('completeness_check', {}).get('coverage_percentage', 0):.1f}% coverage",
                memory_type="completeness_check",
                importance_score=0.7
            )

            return result or state

        return integrated_check_completeness

    def _create_generate_recommendations_node(self):
        """Create the recommendations generation node"""

        async def generate_recommendations_logic(state: DocumentationAnalysisState, context: Dict[str, Any]) -> DocumentationAnalysisState:
            """Generate comprehensive documentation recommendations"""

            structure_analysis = state.get("structure_analysis", {})
            quality_metrics = state.get("quality_metrics", {})
            completeness_check = state.get("completeness_check", {})

            # Calculate overall documentation score
            structure_score = structure_analysis.get("organization_score", 0)
            quality_score = sum([
                quality_metrics.get("readability_score", 0),
                quality_metrics.get("completeness_score", 0),
                quality_metrics.get("accuracy_score", 0),
                quality_metrics.get("up_to_date_score", 0),
                quality_metrics.get("examples_quality", 0),
                quality_metrics.get("language_clarity", 0)
            ]) / 6
            completeness_score = completeness_check.get("coverage_percentage", 0) / 10

            overall_score = (structure_score * 0.3 + quality_score * 0.4 + completeness_score * 0.3)

            # Generate prioritized recommendations
            recommendations = {
                "overall_score": round(overall_score, 1),
                "priority_actions": [],
                "improvement_suggestions": [],
                "maintenance_tasks": [],
                "long_term_goals": [],
                "estimated_effort": {
                    "high_priority": "2-4 hours",
                    "medium_priority": "4-8 hours",
                    "low_priority": "1-2 hours"
                }
            }

            # High priority recommendations (critical gaps)
            critical_gaps = completeness_check.get("critical_gaps", [])
            for gap in critical_gaps:
                if gap == "readme":
                    recommendations["priority_actions"].append({
                        "action": "Create comprehensive README file",
                        "priority": "high",
                        "effort": "2-3 hours",
                        "impact": "high"
                    })
                elif gap == "api_reference":
                    recommendations["priority_actions"].append({
                        "action": "Develop detailed API documentation",
                        "priority": "high",
                        "effort": "4-6 hours",
                        "impact": "high"
                    })
                elif gap == "usage_examples":
                    recommendations["priority_actions"].append({
                        "action": "Add usage examples and tutorials",
                        "priority": "high",
                        "effort": "3-4 hours",
                        "impact": "high"
                    })

            # Medium priority recommendations (quality improvements)
            quality_issues = quality_metrics.get("quality_issues", [])
            for issue in quality_issues:
                if "code documentation" in issue:
                    recommendations["improvement_suggestions"].append({
                        "action": "Improve inline code documentation",
                        "priority": "medium",
                        "effort": "2-4 hours",
                        "impact": "medium"
                    })

            # Structure improvements
            structure_issues = structure_analysis.get("structure_issues", [])
            for issue in structure_issues:
                recommendations["improvement_suggestions"].append({
                    "action": f"Address structure issue: {issue}",
                    "priority": "medium",
                    "effort": "1-2 hours",
                    "impact": "medium"
                })

            # Maintenance tasks
            if quality_metrics.get("up_to_date_score", 0) < 7:
                recommendations["maintenance_tasks"].append({
                    "action": "Update outdated documentation sections",
                    "priority": "medium",
                    "effort": "2-3 hours",
                    "impact": "medium"
                })

            # Long-term goals
            if completeness_check.get("coverage_percentage", 0) < 80:
                recommendations["long_term_goals"].append({
                    "action": "Achieve 90%+ documentation coverage",
                    "priority": "low",
                    "effort": "8-12 hours",
                    "impact": "high"
                })

            recommendations["long_term_goals"].append({
                "action": "Implement automated documentation generation",
                "priority": "low",
                "effort": "6-10 hours",
                "impact": "high"
            })

            # Final results compilation
            final_results = {
                "overall_score": overall_score,
                "analysis_summary": {
                    "structure_score": structure_score,
                    "quality_score": quality_score,
                    "completeness_percentage": completeness_check.get("coverage_percentage", 0),
                    "total_documents_found": sum(len(docs) for docs in state.get("discovered_documentation", {}).values() if isinstance(docs, list))
                },
                "recommendations": recommendations,
                "detailed_findings": {
                    "structure_analysis": structure_analysis,
                    "quality_metrics": quality_metrics,
                    "completeness_check": completeness_check
                },
                "completion_time": datetime.now().isoformat()
            }

            state["final_results"] = final_results
            state["analysis_stage"] = "completed"
            state["analysis_progress"] = 1.0

            logger.info(f"Documentation analysis complete. Overall score: {overall_score:.1f}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="generate_recommendations",
            agent_id="documentation_analyzer",
            required_tools=[],
            memory_types=["recommendation_pattern", "documentation_best_practice"],
            cache_ttl=3600
        )

        async def integrated_generate_recommendations(state: DocumentationAnalysisState) -> DocumentationAnalysisState:
            await pattern.setup()

            cache_key = f"recommendations_{hash(str(state.get('completeness_check', {})) + str(state.get('quality_metrics', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=generate_recommendations_logic,
                cache_key=cache_key,
                memory_content=f"Generated documentation recommendations with overall score {state.get('final_results', {}).get('overall_score', 0):.1f}",
                memory_type="documentation_recommendations",
                importance_score=0.9
            )

            return result or state

        return integrated_generate_recommendations
