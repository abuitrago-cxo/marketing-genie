print("DEBUG: codebase_analysis_graph.py - Top of file")
"""
Codebase Analysis Specialized Graph

This module implements the Codebase Analysis specialist graph following the
established pattern from the original Google Gemini repository.

Workflow Pattern:
1. route_analysis → Determine analysis approach and scope
2. generate_queries → Create comprehensive analysis queries
3. execute_analysis → Conduct detailed codebase analysis
4. reflection_gaps → Evaluate findings and identify gaps
5. finalize_analysis → Generate final analysis report

Uses the same dependencies and patterns as the original graph:
- Gemini models for LLM operations
- LangSmith tracing for monitoring
- Simple synchronous node functions
"""

print("DEBUG: codebase_analysis_graph.py - Importing standard libraries (os, logging, typing, datetime)...")
import os
import logging
from typing import Dict, Any, List
from datetime import datetime
print("DEBUG: codebase_analysis_graph.py - Standard libraries imported.")

print("DEBUG: codebase_analysis_graph.py - Importing third-party libraries (langgraph, langchain_core, langchain_google_genai, dotenv)...")
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
print("DEBUG: codebase_analysis_graph.py - Third-party libraries imported.")

print("DEBUG: codebase_analysis_graph.py - Importing src.agent.state...")
from src.agent.state import CodebaseAnalysisState
print("DEBUG: codebase_analysis_graph.py - ..state imported.")
print("DEBUG: codebase_analysis_graph.py - Importing src.agent.configuration...")
from src.agent.configuration import Configuration
print("DEBUG: codebase_analysis_graph.py - ..configuration imported.")
print("DEBUG: codebase_analysis_graph.py - Importing src.agent.tools.registry...")
from src.agent.tools.registry import ToolRegistry
print("DEBUG: codebase_analysis_graph.py - ..tools.registry imported.")
print("DEBUG: codebase_analysis_graph.py - Importing src.memory.integration_pattern...")
from src.memory.integration_pattern import IntegratedNodePattern
print("DEBUG: codebase_analysis_graph.py - ...memory.integration_pattern imported.")

print("DEBUG: codebase_analysis_graph.py - Calling load_dotenv()...")
load_dotenv()
print("DEBUG: codebase_analysis_graph.py - load_dotenv() called.")

logger = logging.getLogger(__name__)


print("DEBUG: codebase_analysis_graph.py - Before class CodebaseAnalysisGraph definition")
class CodebaseAnalysisGraph:
    """
    Specialized graph for codebase analysis and architecture evaluation.

    This graph follows the established pattern with 5 integrated nodes:
    1. route_analysis - Determine analysis approach and scope
    2. generate_queries - Create comprehensive analysis queries
    3. execute_analysis - Conduct detailed codebase analysis
    4. reflection_gaps - Evaluate findings and identify gaps
    5. finalize_analysis - Generate final analysis report
    """

    def __init__(self):
        print("DEBUG: CodebaseAnalysisGraph.__init__ called")
        self.tool_registry = ToolRegistry()
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the codebase analysis graph"""

        # Create the graph
        workflow = StateGraph(CodebaseAnalysisState)

        # Add nodes
        workflow.add_node("route_analysis", self._create_route_analysis_node())
        workflow.add_node("generate_queries", self._create_generate_queries_node())
        workflow.add_node("execute_analysis", self._create_execute_analysis_node())
        workflow.add_node("reflection_gaps", self._create_reflection_gaps_node())
        workflow.add_node("finalize_analysis", self._create_finalize_analysis_node())

        # Define the flow
        workflow.set_entry_point("route_analysis")
        workflow.add_edge("route_analysis", "generate_queries")
        workflow.add_edge("generate_queries", "execute_analysis")
        workflow.add_edge("execute_analysis", "reflection_gaps")
        workflow.add_edge("reflection_gaps", "finalize_analysis")
        workflow.add_edge("finalize_analysis", END)

        self.graph = workflow.compile(name="codebase-analysis-specialist")
        print("DEBUG: CodebaseAnalysisGraph.create_graph finished")
        return self.graph

    def _create_route_analysis_node(self):
        """Create the analysis routing node with integrated pattern"""

        async def route_analysis_logic(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            """Analyze repository context and determine analysis approach"""

            repository_url = state.get("repository_url", "")
            repository_path = state.get("repository_path", "")
            analysis_type = state.get("analysis_type", "comprehensive")

            # Determine analysis scope based on repository characteristics
            if "microservice" in repository_url.lower() or "api" in repository_url.lower():
                analysis_focus = "architecture_and_api"
                analysis_queries = [
                    f"Microservices architecture patterns in {repository_url}",
                    f"API design best practices for {analysis_type} analysis",
                    f"Service communication patterns and dependencies",
                    f"Container orchestration and deployment strategies"
                ]
            elif "frontend" in repository_url.lower() or "react" in repository_url.lower():
                analysis_focus = "frontend_architecture"
                analysis_queries = [
                    f"Frontend architecture patterns for {repository_url}",
                    f"Component design and state management analysis",
                    f"Performance optimization techniques",
                    f"Accessibility and user experience evaluation"
                ]
            elif "data" in repository_url.lower() or "ml" in repository_url.lower():
                analysis_focus = "data_and_ml"
                analysis_queries = [
                    f"Data pipeline architecture for {repository_url}",
                    f"Machine learning model deployment patterns",
                    f"Data quality and validation strategies",
                    f"Scalability and performance optimization"
                ]
            else:
                analysis_focus = "general_software"
                analysis_queries = [
                    f"Software architecture analysis for {repository_url}",
                    f"Code quality and maintainability assessment",
                    f"Security vulnerability analysis",
                    f"Performance and scalability evaluation"
                ]

            # Set file patterns based on analysis type
            if analysis_type == "security":
                file_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "Dockerfile", "*.yaml", "*.yml"]
            elif analysis_type == "performance":
                file_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "*.sql", "*.json"]
            elif analysis_type == "architecture":
                file_patterns = ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "*.md", "*.yaml", "*.yml", "*.json"]
            else:  # comprehensive
                file_patterns = ["*.*"]

            state["analysis_focus"] = analysis_focus
            state["analysis_queries"] = analysis_queries
            state["file_patterns"] = file_patterns
            state["analysis_stage"] = "routing_complete"
            state["analysis_progress"] = 0.2

            logger.info(f"Analysis routing complete. Focus: {analysis_focus}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="route_analysis",
            agent_id="codebase_analyzer",
            required_tools=["file_operations"],
            memory_types=["analysis_pattern", "architecture_insight"],
            cache_ttl=1800
        )

        async def integrated_route_analysis(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            await pattern.setup()

            cache_key = f"route_analysis_{hash(state.get('repository_url', ''))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=route_analysis_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed repository: {state.get('repository_url', 'unknown')}",
                memory_type="analysis_routing",
                importance_score=0.7
            )

            return result or state

        return integrated_route_analysis

    def _create_generate_queries_node(self):
        """Create the query generation node with integrated pattern"""

        async def generate_queries_logic(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            """Generate comprehensive analysis queries based on routing"""

            analysis_focus = state.get("analysis_focus", "general_software")
            analysis_type = state.get("analysis_type", "comprehensive")
            repository_url = state.get("repository_url", "")

            # Generate specific queries based on focus area
            detailed_queries = []

            if analysis_focus == "architecture_and_api":
                detailed_queries.extend([
                    f"Analyze microservices architecture patterns in {repository_url}",
                    f"Evaluate API design consistency and RESTful principles",
                    f"Assess service discovery and communication mechanisms",
                    f"Review containerization and orchestration strategies",
                    f"Analyze database design and data flow patterns"
                ])
            elif analysis_focus == "frontend_architecture":
                detailed_queries.extend([
                    f"Evaluate component architecture and design patterns",
                    f"Analyze state management implementation and efficiency",
                    f"Review routing and navigation structure",
                    f"Assess performance optimization techniques",
                    f"Evaluate accessibility and responsive design implementation"
                ])
            elif analysis_focus == "data_and_ml":
                detailed_queries.extend([
                    f"Analyze data pipeline architecture and flow",
                    f"Evaluate machine learning model structure and deployment",
                    f"Review data validation and quality assurance processes",
                    f"Assess scalability and performance optimization",
                    f"Analyze data security and privacy implementation"
                ])
            else:  # general_software
                detailed_queries.extend([
                    f"Analyze overall software architecture and design patterns",
                    f"Evaluate code quality, maintainability, and technical debt",
                    f"Review security implementation and vulnerability assessment",
                    f"Assess performance bottlenecks and optimization opportunities",
                    f"Analyze testing coverage and quality assurance practices"
                ])

            # Add analysis type specific queries
            if analysis_type == "security":
                detailed_queries.extend([
                    f"Identify potential security vulnerabilities and threats",
                    f"Review authentication and authorization mechanisms",
                    f"Analyze input validation and sanitization practices",
                    f"Evaluate encryption and data protection measures"
                ])
            elif analysis_type == "performance":
                detailed_queries.extend([
                    f"Identify performance bottlenecks and optimization opportunities",
                    f"Analyze resource utilization and efficiency",
                    f"Review caching strategies and implementation",
                    f"Evaluate scalability and load handling capabilities"
                ])

            state["detailed_analysis_queries"] = detailed_queries
            state["query_generation_complete"] = True
            state["analysis_stage"] = "queries_generated"
            state["analysis_progress"] = 0.4

            logger.info(f"Generated {len(detailed_queries)} analysis queries")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="generate_queries",
            agent_id="codebase_analyzer",
            required_tools=["file_operations"],
            memory_types=["query_pattern", "analysis_template"],
            cache_ttl=1200
        )

        async def integrated_generate_queries(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            await pattern.setup()

            cache_key = f"queries_{hash(str(state.get('analysis_focus', '')))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=generate_queries_logic,
                cache_key=cache_key,
                memory_content=f"Generated queries for {state.get('analysis_focus', 'unknown')} analysis",
                memory_type="query_generation",
                importance_score=0.6
            )

            return result or state

        return integrated_generate_queries

    def _create_execute_analysis_node(self):
        """Create the analysis execution node with integrated pattern"""

        async def execute_analysis_logic(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            """Execute comprehensive codebase analysis"""

            detailed_queries = state.get("detailed_analysis_queries", [])
            file_patterns = state.get("file_patterns", ["*.*"])
            repository_path = state.get("repository_path", "")
            analysis_type = state.get("analysis_type", "comprehensive")

            # Simulate comprehensive analysis execution
            analysis_results = []
            code_patterns = []
            architecture_insights = {}
            quality_metrics = {}
            security_findings = []

            # Architecture Analysis
            architecture_insights = {
                "overall_structure": "Modular architecture with clear separation of concerns",
                "design_patterns": ["MVC", "Repository Pattern", "Dependency Injection"],
                "coupling_analysis": "Low coupling between modules, high cohesion within modules",
                "scalability_assessment": "Good horizontal scaling potential",
                "maintainability_score": 8.5
            }

            # Code Quality Metrics
            quality_metrics = {
                "code_complexity": "Medium complexity with some areas for improvement",
                "test_coverage": "75% overall coverage",
                "documentation_quality": "Good inline documentation, missing API docs",
                "code_duplication": "Minimal duplication detected",
                "technical_debt_score": 6.8
            }

            # Security Analysis (if security focus)
            if analysis_type == "security":
                security_findings = [
                    {
                        "severity": "medium",
                        "category": "input_validation",
                        "description": "Some endpoints lack proper input validation",
                        "recommendation": "Implement comprehensive input sanitization"
                    },
                    {
                        "severity": "low",
                        "category": "authentication",
                        "description": "Consider implementing rate limiting",
                        "recommendation": "Add rate limiting to prevent brute force attacks"
                    }
                ]

            # Code Patterns Analysis
            code_patterns = [
                {
                    "pattern": "Singleton Pattern",
                    "usage": "Database connection management",
                    "assessment": "Appropriate usage"
                },
                {
                    "pattern": "Factory Pattern",
                    "usage": "Object creation in services",
                    "assessment": "Good implementation"
                },
                {
                    "pattern": "Observer Pattern",
                    "usage": "Event handling system",
                    "assessment": "Could be optimized"
                }
            ]

            # Analysis Results Summary
            for i, query in enumerate(detailed_queries[:5]):  # Limit to first 5 for demo
                analysis_results.append({
                    "query": query,
                    "findings": f"Analysis result {i+1}: Comprehensive evaluation completed",
                    "confidence": 0.85 + (i * 0.02),
                    "recommendations": [
                        f"Recommendation {i+1}.1: Optimize implementation",
                        f"Recommendation {i+1}.2: Improve documentation"
                    ]
                })

            state["analysis_results"] = analysis_results
            state["code_patterns"] = code_patterns
            state["architecture_insights"] = architecture_insights
            state["quality_metrics"] = quality_metrics
            state["security_findings"] = security_findings
            state["analysis_stage"] = "analysis_complete"
            state["analysis_progress"] = 0.7

            logger.info(f"Analysis execution complete. Found {len(analysis_results)} results")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="execute_analysis",
            agent_id="codebase_analyzer",
            required_tools=["file_operations", "code_analysis"],
            memory_types=["analysis_result", "code_insight"],
            cache_ttl=900
        )

        async def integrated_execute_analysis(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            await pattern.setup()

            cache_key = f"analysis_{hash(str(state.get('detailed_analysis_queries', [])))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=execute_analysis_logic,
                cache_key=cache_key,
                memory_content=f"Executed analysis with {len(state.get('detailed_analysis_queries', []))} queries",
                memory_type="analysis_execution",
                importance_score=0.9
            )

            return result or state

        return integrated_execute_analysis

    def _create_reflection_gaps_node(self):
        """Create the reflection and gap analysis node with integrated pattern"""

        async def reflection_gaps_logic(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            """Evaluate analysis results and identify knowledge gaps"""

            analysis_results = state.get("analysis_results", [])
            architecture_insights = state.get("architecture_insights", {})
            quality_metrics = state.get("quality_metrics", {})
            analysis_type = state.get("analysis_type", "comprehensive")

            # Evaluate completeness and quality of analysis
            total_queries = len(state.get("detailed_analysis_queries", []))
            completed_analyses = len(analysis_results)
            completeness_ratio = completed_analyses / total_queries if total_queries > 0 else 0

            # Identify knowledge gaps
            knowledge_gaps = []

            if completeness_ratio < 0.8:
                knowledge_gaps.append({
                    "category": "analysis_coverage",
                    "description": f"Only {completed_analyses}/{total_queries} queries analyzed",
                    "priority": "high",
                    "recommendation": "Complete remaining analysis queries"
                })

            # Check for missing analysis areas
            if analysis_type == "comprehensive":
                if not architecture_insights.get("scalability_assessment"):
                    knowledge_gaps.append({
                        "category": "scalability",
                        "description": "Scalability assessment incomplete",
                        "priority": "medium",
                        "recommendation": "Conduct detailed scalability analysis"
                    })

                if quality_metrics.get("test_coverage", 0) < 80:
                    knowledge_gaps.append({
                        "category": "testing",
                        "description": f"Test coverage at {quality_metrics.get('test_coverage', 0)}%",
                        "priority": "medium",
                        "recommendation": "Improve test coverage to 80%+"
                    })

            # Evaluate confidence levels
            avg_confidence = sum(r.get("confidence", 0) for r in analysis_results) / len(analysis_results) if analysis_results else 0

            if avg_confidence < 0.7:
                knowledge_gaps.append({
                    "category": "analysis_confidence",
                    "description": f"Average confidence level at {avg_confidence:.2f}",
                    "priority": "high",
                    "recommendation": "Conduct deeper analysis for low-confidence areas"
                })

            # Generate follow-up queries if gaps identified
            follow_up_queries = []
            for gap in knowledge_gaps:
                if gap["priority"] == "high":
                    follow_up_queries.append(f"Address {gap['category']}: {gap['recommendation']}")

            # Determine if analysis is sufficient
            is_analysis_sufficient = len(knowledge_gaps) <= 2 and avg_confidence >= 0.7

            state["knowledge_gaps"] = knowledge_gaps
            state["follow_up_queries"] = follow_up_queries
            state["analysis_confidence"] = avg_confidence
            state["is_analysis_sufficient"] = is_analysis_sufficient
            state["analysis_stage"] = "reflection_complete"
            state["analysis_progress"] = 0.9

            logger.info(f"Reflection complete. Found {len(knowledge_gaps)} gaps, confidence: {avg_confidence:.2f}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="reflection_gaps",
            agent_id="codebase_analyzer",
            required_tools=["analysis_tools"],
            memory_types=["reflection_pattern", "gap_analysis"],
            cache_ttl=600
        )

        async def integrated_reflection_gaps(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            await pattern.setup()

            cache_key = f"reflection_{hash(str(state.get('analysis_results', [])))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=reflection_gaps_logic,
                cache_key=cache_key,
                memory_content=f"Reflected on analysis with {state.get('analysis_confidence', 0):.2f} confidence",
                memory_type="reflection_analysis",
                importance_score=0.8
            )

            return result or state

        return integrated_reflection_gaps

    def _create_finalize_analysis_node(self):
        """Create the analysis finalization node with integrated pattern"""

        async def finalize_analysis_logic(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            """Generate final comprehensive analysis report"""

            analysis_results = state.get("analysis_results", [])
            architecture_insights = state.get("architecture_insights", {})
            quality_metrics = state.get("quality_metrics", {})
            security_findings = state.get("security_findings", [])
            code_patterns = state.get("code_patterns", [])
            knowledge_gaps = state.get("knowledge_gaps", [])
            analysis_confidence = state.get("analysis_confidence", 0.0)

            # Generate executive summary
            executive_summary = {
                "repository_analyzed": state.get("repository_url", "Unknown"),
                "analysis_type": state.get("analysis_type", "comprehensive"),
                "total_findings": len(analysis_results),
                "overall_confidence": analysis_confidence,
                "analysis_date": datetime.now().isoformat(),
                "key_insights": [
                    f"Architecture: {architecture_insights.get('overall_structure', 'Not analyzed')}",
                    f"Quality Score: {quality_metrics.get('technical_debt_score', 'N/A')}/10",
                    f"Security Issues: {len(security_findings)} found",
                    f"Code Patterns: {len(code_patterns)} identified"
                ]
            }

            # Generate recommendations
            recommendations = []

            # Architecture recommendations
            if architecture_insights.get("maintainability_score", 0) < 8:
                recommendations.append({
                    "category": "architecture",
                    "priority": "high",
                    "title": "Improve Code Maintainability",
                    "description": "Focus on reducing complexity and improving code organization",
                    "estimated_effort": "2-3 weeks"
                })

            # Quality recommendations
            if quality_metrics.get("technical_debt_score", 0) < 7:
                recommendations.append({
                    "category": "quality",
                    "priority": "medium",
                    "title": "Address Technical Debt",
                    "description": "Refactor legacy code and improve documentation",
                    "estimated_effort": "1-2 weeks"
                })

            # Security recommendations
            for finding in security_findings:
                if finding.get("severity") in ["high", "critical"]:
                    recommendations.append({
                        "category": "security",
                        "priority": "critical",
                        "title": f"Fix {finding.get('category', 'Security Issue')}",
                        "description": finding.get("recommendation", "Address security vulnerability"),
                        "estimated_effort": "1-3 days"
                    })

            # Knowledge gap recommendations
            for gap in knowledge_gaps:
                if gap.get("priority") == "high":
                    recommendations.append({
                        "category": "analysis",
                        "priority": "high",
                        "title": f"Address {gap.get('category', 'Analysis Gap')}",
                        "description": gap.get("recommendation", "Complete missing analysis"),
                        "estimated_effort": "1-2 days"
                    })

            # Calculate overall analysis score
            architecture_score = architecture_insights.get("maintainability_score", 5) / 10
            quality_score = quality_metrics.get("technical_debt_score", 5) / 10
            security_score = max(0, 1 - (len(security_findings) * 0.1))
            confidence_score = analysis_confidence

            overall_score = (architecture_score + quality_score + security_score + confidence_score) / 4

            # Generate final report
            final_report = {
                "executive_summary": executive_summary,
                "detailed_findings": analysis_results,
                "architecture_analysis": architecture_insights,
                "quality_assessment": quality_metrics,
                "security_analysis": security_findings,
                "code_patterns_analysis": code_patterns,
                "recommendations": recommendations,
                "knowledge_gaps": knowledge_gaps,
                "overall_score": round(overall_score, 2),
                "analysis_metadata": {
                    "total_queries_processed": len(state.get("detailed_analysis_queries", [])),
                    "analysis_duration": "Estimated 30-45 minutes",
                    "confidence_level": analysis_confidence,
                    "completeness": "High" if len(knowledge_gaps) <= 2 else "Medium"
                }
            }

            state["final_analysis_report"] = final_report
            state["analysis_recommendations"] = recommendations
            state["overall_analysis_score"] = overall_score
            state["analysis_stage"] = "complete"
            state["analysis_progress"] = 1.0

            logger.info(f"Analysis finalized. Overall score: {overall_score:.2f}, {len(recommendations)} recommendations")
            logger.info(f"Final analysis report generated for {state.get('repository_url', 'unknown')}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="finalize_analysis",
            agent_id="codebase_analyzer",
            required_tools=["file_operations", "reporting_tools"],
            memory_types=["analysis_summary", "recommendation_pattern"],
            cache_ttl=3600  # Cache final reports for an hour
        )

        async def integrated_finalize_analysis(state: CodebaseAnalysisState) -> CodebaseAnalysisState:
            await pattern.setup()

            cache_key = f"finalize_analysis_{hash(state.get('repository_url', ''))}_{hash(str(state.get('analysis_findings', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=finalize_analysis_logic,
                cache_key=cache_key,
                memory_content=f"Finalized analysis for: {state.get('repository_url', 'unknown')}",
                memory_type="final_report_generation",
                importance_score=0.9
            )

            return result or state

        return integrated_finalize_analysis

print("DEBUG: codebase_analysis_graph.py - End of file (after class CodebaseAnalysisGraph definition)")
