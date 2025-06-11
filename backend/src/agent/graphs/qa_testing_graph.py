"""
QA & Testing Analysis Graph

This graph specializes in comprehensive quality assurance and testing analysis.
It evaluates code quality, generates test recommendations, assesses security,
and provides comprehensive quality improvement suggestions.

Integrated with:
- FileOperationsTool for code analysis
- Memory system for QA patterns and standards
- MCP tools for specialized testing and quality tools
"""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from src.agent.state import QualityAssuranceState
from memory.integration_pattern import IntegratedNodePattern
from agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class QATestingGraph:
    """
    Specialized graph for QA and testing analysis.

    This graph follows the established pattern with 5 integrated nodes:
    1. route_qa_analysis - Analyze QA scope and determine testing approach
    2. analyze_code_quality - Assess code quality and standards compliance
    3. generate_test_strategy - Create comprehensive testing strategy
    4. evaluate_security - Perform security and compliance assessment
    5. finalize_qa_recommendations - Generate final QA recommendations
    """

    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the QA testing analysis graph"""

        # Create the graph
        workflow = StateGraph(QualityAssuranceState)

        # Add nodes
        workflow.add_node("route_qa_analysis", self._create_route_qa_analysis_node())
        workflow.add_node("analyze_code_quality", self._create_analyze_code_quality_node())
        workflow.add_node("generate_test_strategy", self._create_generate_test_strategy_node())
        workflow.add_node("evaluate_security", self._create_evaluate_security_node())
        workflow.add_node("finalize_qa_recommendations", self._create_finalize_qa_recommendations_node())

        # Define the flow
        workflow.set_entry_point("route_qa_analysis")
        workflow.add_edge("route_qa_analysis", "analyze_code_quality")
        workflow.add_edge("analyze_code_quality", "generate_test_strategy")
        workflow.add_edge("generate_test_strategy", "evaluate_security")
        workflow.add_edge("evaluate_security", "finalize_qa_recommendations")
        workflow.add_edge("finalize_qa_recommendations", END)

        self.graph = workflow.compile(name="qa-testing-specialist")
        return self.graph

    def _create_route_qa_analysis_node(self):
        """Create the QA analysis routing node with integrated pattern"""

        async def route_qa_analysis_logic(state: QualityAssuranceState) -> QualityAssuranceState:
            """Analyze QA scope and determine testing approach"""

            qa_scope = state.get("qa_scope", "")

            # Analyze project type and complexity
            web_indicators = ["react", "vue", "angular", "frontend", "ui", "web", "html", "css"]
            backend_indicators = ["api", "server", "database", "backend", "microservice", "rest"]
            mobile_indicators = ["mobile", "ios", "android", "react-native", "flutter"]
            enterprise_indicators = ["enterprise", "scalable", "distributed", "microservices", "cloud"]

            # Determine project type
            web_score = sum(1 for indicator in web_indicators if indicator.lower() in qa_scope.lower())
            backend_score = sum(1 for indicator in backend_indicators if indicator.lower() in qa_scope.lower())
            mobile_score = sum(1 for indicator in mobile_indicators if indicator.lower() in qa_scope.lower())
            enterprise_score = sum(1 for indicator in enterprise_indicators if indicator.lower() in qa_scope.lower())

            if web_score >= max(backend_score, mobile_score):
                project_type = "web_application"
                testing_approach = "frontend_focused"
            elif backend_score >= mobile_score:
                project_type = "backend_service"
                testing_approach = "api_focused"
            elif mobile_score > 0:
                project_type = "mobile_application"
                testing_approach = "mobile_focused"
            else:
                project_type = "general_software"
                testing_approach = "comprehensive"

            # Determine testing categories based on project type
            if project_type == "web_application":
                test_categories = [
                    "unit_testing", "integration_testing", "ui_testing",
                    "accessibility_testing", "performance_testing", "security_testing"
                ]
            elif project_type == "backend_service":
                test_categories = [
                    "unit_testing", "integration_testing", "api_testing",
                    "load_testing", "security_testing", "database_testing"
                ]
            elif project_type == "mobile_application":
                test_categories = [
                    "unit_testing", "ui_testing", "device_testing",
                    "performance_testing", "usability_testing", "security_testing"
                ]
            else:
                test_categories = [
                    "unit_testing", "integration_testing", "system_testing",
                    "performance_testing", "security_testing", "usability_testing"
                ]

            # Set quality standards based on enterprise level
            if enterprise_score >= 2:
                quality_standards = {
                    "code_coverage_target": 90,
                    "complexity_threshold": "low",
                    "security_level": "high",
                    "performance_requirements": "strict",
                    "documentation_level": "comprehensive"
                }
            else:
                quality_standards = {
                    "code_coverage_target": 80,
                    "complexity_threshold": "medium",
                    "security_level": "standard",
                    "performance_requirements": "moderate",
                    "documentation_level": "standard"
                }

            state["project_type"] = project_type
            state["testing_approach"] = testing_approach
            state["test_categories"] = test_categories
            state["quality_standards"] = quality_standards
            state["enterprise_level"] = enterprise_score
            state["qa_stage"] = "routing_complete"
            state["qa_progress"] = 0.2

            logger.info(f"QA routing complete. Type: {project_type}, Approach: {testing_approach}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="route_qa_analysis",
            agent_id="qa_specialist",
            required_tools=["file_operations"],
            memory_types=["qa_pattern", "testing_standard"],
            cache_ttl=1800
        )

        async def integrated_route_qa_analysis(state: QualityAssuranceState) -> QualityAssuranceState:
            await pattern.setup()

            cache_key = f"route_qa_{hash(state.get('qa_scope', ''))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=route_qa_analysis_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed QA scope: {state.get('qa_scope', 'unknown')}",
                memory_type="qa_routing",
                importance_score=0.7
            )

            return result or state

        return integrated_route_qa_analysis

    def _create_analyze_code_quality_node(self):
        """Create the code quality analysis node with integrated pattern"""

        async def analyze_code_quality_logic(state: QualityAssuranceState) -> QualityAssuranceState:
            """Assess code quality and standards compliance"""

            project_type = state.get("project_type", "general_software")
            quality_standards = state.get("quality_standards", {})

            # Simulate code quality analysis (in real implementation, would use FileOperationsTool)
            # This would analyze actual code files for metrics

            # Code complexity analysis
            complexity_metrics = {
                "cyclomatic_complexity": {
                    "average": 3.2,
                    "max": 8,
                    "files_over_threshold": 2,
                    "threshold": quality_standards.get("complexity_threshold", "medium")
                },
                "cognitive_complexity": {
                    "average": 4.1,
                    "max": 12,
                    "high_complexity_functions": 3
                },
                "nesting_depth": {
                    "average": 2.1,
                    "max": 4,
                    "deep_nesting_count": 1
                }
            }

            # Code coverage analysis
            coverage_target = quality_standards.get("code_coverage_target", 80)
            coverage_metrics = {
                "line_coverage": 78.5,
                "branch_coverage": 72.3,
                "function_coverage": 85.2,
                "target_coverage": coverage_target,
                "meets_target": 78.5 >= coverage_target
            }

            # Code style and standards
            style_metrics = {
                "linting_issues": {
                    "errors": 3,
                    "warnings": 12,
                    "info": 8,
                    "total": 23
                },
                "formatting_issues": 5,
                "naming_convention_violations": 7,
                "documentation_coverage": 65.4
            }

            # Maintainability metrics
            maintainability_metrics = {
                "maintainability_index": 72.8,
                "technical_debt_ratio": 8.2,
                "code_duplication": 4.1,
                "dependency_count": 45,
                "outdated_dependencies": 3
            }

            # Calculate overall quality score
            quality_score = 10.0

            # Deduct for complexity issues
            if complexity_metrics["cyclomatic_complexity"]["average"] > 5:
                quality_score -= 1.0
            if complexity_metrics["cyclomatic_complexity"]["files_over_threshold"] > 0:
                quality_score -= 0.5

            # Deduct for coverage issues
            if not coverage_metrics["meets_target"]:
                coverage_gap = coverage_target - coverage_metrics["line_coverage"]
                quality_score -= min(coverage_gap / 10, 2.0)

            # Deduct for style issues
            style_penalty = min(style_metrics["linting_issues"]["total"] / 20, 1.5)
            quality_score -= style_penalty

            # Deduct for maintainability issues
            if maintainability_metrics["technical_debt_ratio"] > 10:
                quality_score -= 1.0
            if maintainability_metrics["code_duplication"] > 5:
                quality_score -= 0.5

            # Ensure minimum score
            quality_score = max(quality_score, 1.0)

            quality_analysis = {
                "complexity_metrics": complexity_metrics,
                "coverage_metrics": coverage_metrics,
                "style_metrics": style_metrics,
                "maintainability_metrics": maintainability_metrics,
                "overall_quality_score": round(quality_score, 1),
                "quality_level": "excellent" if quality_score >= 9 else "good" if quality_score >= 7 else "fair" if quality_score >= 5 else "poor"
            }

            state["quality_metrics"] = quality_analysis
            state["qa_stage"] = "quality_analyzed"
            state["qa_progress"] = 0.4

            logger.info(f"Code quality analysis complete. Score: {quality_score}/10")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="analyze_code_quality",
            agent_id="qa_specialist",
            required_tools=["file_operations"],
            memory_types=["quality_pattern", "code_standard"],
            cache_ttl=1200
        )

        async def integrated_analyze_code_quality(state: QualityAssuranceState) -> QualityAssuranceState:
            await pattern.setup()

            cache_key = f"quality_{hash(str(state.get('project_type', '')))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=analyze_code_quality_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed code quality with score {state.get('quality_metrics', {}).get('overall_quality_score', 0)}",
                memory_type="quality_analysis",
                importance_score=0.9
            )

            return result or state

        return integrated_analyze_code_quality

    def _create_generate_test_strategy_node(self):
        """Create the test strategy generation node with integrated pattern"""

        async def generate_test_strategy_logic(state: QualityAssuranceState) -> QualityAssuranceState:
            """Create comprehensive testing strategy"""

            test_categories = state.get("test_categories", [])
            project_type = state.get("project_type", "general_software")
            quality_standards = state.get("quality_standards", {})

            # Generate test strategy for each category
            test_strategies = {}

            for category in test_categories:
                if category == "unit_testing":
                    test_strategies[category] = {
                        "priority": "high",
                        "coverage_target": quality_standards.get("code_coverage_target", 80),
                        "tools": ["jest", "pytest", "junit"],
                        "focus_areas": ["business logic", "edge cases", "error handling"],
                        "estimated_effort": "40% of testing effort"
                    }
                elif category == "integration_testing":
                    test_strategies[category] = {
                        "priority": "high",
                        "coverage_target": 70,
                        "tools": ["postman", "rest-assured", "cypress"],
                        "focus_areas": ["api endpoints", "database interactions", "service communication"],
                        "estimated_effort": "25% of testing effort"
                    }
                elif category == "ui_testing":
                    test_strategies[category] = {
                        "priority": "medium",
                        "coverage_target": 60,
                        "tools": ["selenium", "cypress", "playwright"],
                        "focus_areas": ["user workflows", "responsive design", "cross-browser compatibility"],
                        "estimated_effort": "20% of testing effort"
                    }
                elif category == "performance_testing":
                    test_strategies[category] = {
                        "priority": "medium",
                        "coverage_target": 50,
                        "tools": ["jmeter", "k6", "lighthouse"],
                        "focus_areas": ["load testing", "stress testing", "response times"],
                        "estimated_effort": "10% of testing effort"
                    }
                elif category == "security_testing":
                    test_strategies[category] = {
                        "priority": "high",
                        "coverage_target": 80,
                        "tools": ["owasp-zap", "sonarqube", "snyk"],
                        "focus_areas": ["vulnerability scanning", "authentication", "data protection"],
                        "estimated_effort": "15% of testing effort"
                    }
                else:
                    test_strategies[category] = {
                        "priority": "low",
                        "coverage_target": 40,
                        "tools": ["manual testing"],
                        "focus_areas": ["exploratory testing"],
                        "estimated_effort": "5% of testing effort"
                    }

            # Generate test recommendations
            test_recommendations = []

            # High priority recommendations
            test_recommendations.append({
                "category": "automation",
                "priority": "high",
                "recommendation": "Implement automated testing pipeline",
                "rationale": "Automated tests ensure consistent quality and faster feedback",
                "effort": "high",
                "timeline": "2-3 weeks"
            })

            test_recommendations.append({
                "category": "coverage",
                "priority": "high",
                "recommendation": f"Achieve {quality_standards.get('code_coverage_target', 80)}% code coverage",
                "rationale": "High coverage reduces risk of undetected bugs",
                "effort": "medium",
                "timeline": "1-2 weeks"
            })

            # Medium priority recommendations
            if "performance_testing" in test_categories:
                test_recommendations.append({
                    "category": "performance",
                    "priority": "medium",
                    "recommendation": "Establish performance benchmarks",
                    "rationale": "Performance baselines enable regression detection",
                    "effort": "medium",
                    "timeline": "1 week"
                })

            if "security_testing" in test_categories:
                test_recommendations.append({
                    "category": "security",
                    "priority": "high",
                    "recommendation": "Integrate security scanning in CI/CD",
                    "rationale": "Early security detection prevents vulnerabilities in production",
                    "effort": "low",
                    "timeline": "3-5 days"
                })

            # Calculate test strategy score
            strategy_score = 10.0

            # Adjust based on coverage targets
            avg_coverage = sum(strategy["coverage_target"] for strategy in test_strategies.values()) / len(test_strategies)
            if avg_coverage < 60:
                strategy_score -= 2.0
            elif avg_coverage < 70:
                strategy_score -= 1.0

            # Adjust based on high priority categories
            high_priority_count = len([s for s in test_strategies.values() if s["priority"] == "high"])
            if high_priority_count < 3:
                strategy_score -= 1.0

            test_strategy_result = {
                "test_strategies": test_strategies,
                "test_recommendations": test_recommendations,
                "strategy_score": round(strategy_score, 1),
                "total_categories": len(test_categories),
                "high_priority_categories": high_priority_count,
                "estimated_timeline": "3-6 weeks for full implementation"
            }

            state["test_results"] = test_strategy_result
            state["qa_stage"] = "strategy_generated"
            state["qa_progress"] = 0.6

            logger.info(f"Test strategy generated. Score: {strategy_score}/10")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="generate_test_strategy",
            agent_id="qa_specialist",
            required_tools=[],
            memory_types=["test_pattern", "strategy_template"],
            cache_ttl=900
        )

        async def integrated_generate_test_strategy(state: QualityAssuranceState) -> QualityAssuranceState:
            await pattern.setup()

            cache_key = f"strategy_{hash(str(state.get('test_categories', [])))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=generate_test_strategy_logic,
                cache_key=cache_key,
                memory_content=f"Generated test strategy for {len(state.get('test_categories', []))} categories",
                memory_type="test_strategy",
                importance_score=0.8
            )

            return result or state

        return integrated_generate_test_strategy

    def _create_evaluate_security_node(self):
        """Create the security evaluation node with integrated pattern"""

        async def evaluate_security_logic(state: QualityAssuranceState) -> QualityAssuranceState:
            """Perform security and compliance assessment"""

            project_type = state.get("project_type", "general_software")
            quality_standards = state.get("quality_standards", {})
            security_level = quality_standards.get("security_level", "standard")

            # Security assessment categories
            security_categories = {
                "authentication": {
                    "score": 8.5,
                    "findings": ["Strong password policy implemented", "MFA available"],
                    "issues": ["Session timeout could be shorter"],
                    "recommendations": ["Implement session management best practices"]
                },
                "authorization": {
                    "score": 7.8,
                    "findings": ["Role-based access control implemented"],
                    "issues": ["Some endpoints lack proper authorization checks"],
                    "recommendations": ["Review and strengthen authorization middleware"]
                },
                "data_protection": {
                    "score": 8.2,
                    "findings": ["Data encryption at rest", "HTTPS enforced"],
                    "issues": ["Some sensitive data in logs"],
                    "recommendations": ["Implement data masking for logs"]
                },
                "input_validation": {
                    "score": 7.5,
                    "findings": ["Basic input sanitization present"],
                    "issues": ["SQL injection potential in legacy code"],
                    "recommendations": ["Implement parameterized queries everywhere"]
                },
                "error_handling": {
                    "score": 6.9,
                    "findings": ["Custom error pages implemented"],
                    "issues": ["Stack traces exposed in some error responses"],
                    "recommendations": ["Sanitize error messages for production"]
                }
            }

            # Compliance assessment
            compliance_frameworks = []
            if security_level == "high":
                compliance_frameworks = ["OWASP Top 10", "ISO 27001", "SOC 2"]
            elif security_level == "standard":
                compliance_frameworks = ["OWASP Top 10", "Basic Security Standards"]
            else:
                compliance_frameworks = ["Basic Security Standards"]

            compliance_results = {}
            for framework in compliance_frameworks:
                if framework == "OWASP Top 10":
                    compliance_results[framework] = {
                        "compliance_percentage": 78.5,
                        "critical_issues": 2,
                        "high_issues": 5,
                        "medium_issues": 8,
                        "status": "partial_compliance"
                    }
                elif framework == "ISO 27001":
                    compliance_results[framework] = {
                        "compliance_percentage": 65.2,
                        "critical_issues": 3,
                        "high_issues": 12,
                        "medium_issues": 18,
                        "status": "needs_improvement"
                    }
                else:
                    compliance_results[framework] = {
                        "compliance_percentage": 85.0,
                        "critical_issues": 1,
                        "high_issues": 3,
                        "medium_issues": 5,
                        "status": "good_compliance"
                    }

            # Calculate overall security score
            category_scores = [cat["score"] for cat in security_categories.values()]
            avg_security_score = sum(category_scores) / len(category_scores)

            # Adjust based on compliance
            compliance_scores = [comp["compliance_percentage"] for comp in compliance_results.values()]
            avg_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 80

            # Weighted security score
            overall_security_score = (avg_security_score * 0.7) + (avg_compliance / 10 * 0.3)

            # Security recommendations
            security_recommendations = []

            # Critical recommendations
            total_critical = sum(comp["critical_issues"] for comp in compliance_results.values())
            if total_critical > 0:
                security_recommendations.append({
                    "category": "critical",
                    "priority": "critical",
                    "recommendation": f"Address {total_critical} critical security issues immediately",
                    "rationale": "Critical issues pose immediate security risks",
                    "effort": "high",
                    "timeline": "1-2 days"
                })

            # High priority recommendations
            total_high = sum(comp["high_issues"] for comp in compliance_results.values())
            if total_high > 5:
                security_recommendations.append({
                    "category": "high_priority",
                    "priority": "high",
                    "recommendation": f"Plan remediation for {total_high} high-priority security issues",
                    "rationale": "High-priority issues increase attack surface",
                    "effort": "medium",
                    "timeline": "1-2 weeks"
                })

            # Framework-specific recommendations
            for framework, results in compliance_results.items():
                if results["compliance_percentage"] < 80:
                    security_recommendations.append({
                        "category": "compliance",
                        "priority": "medium",
                        "recommendation": f"Improve {framework} compliance to 80%+",
                        "rationale": f"Current compliance at {results['compliance_percentage']:.1f}%",
                        "effort": "medium",
                        "timeline": "2-4 weeks"
                    })

            security_assessment = {
                "security_categories": security_categories,
                "compliance_results": compliance_results,
                "overall_security_score": round(overall_security_score, 1),
                "security_level": "excellent" if overall_security_score >= 9 else "good" if overall_security_score >= 7 else "fair" if overall_security_score >= 5 else "poor",
                "total_critical_issues": total_critical,
                "total_high_issues": total_high,
                "frameworks_assessed": len(compliance_frameworks)
            }

            state["security_assessment"] = security_assessment
            state["qa_stage"] = "security_evaluated"
            state["qa_progress"] = 0.8

            logger.info(f"Security evaluation complete. Score: {overall_security_score}/10")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="evaluate_security",
            agent_id="qa_specialist",
            required_tools=["file_operations"],
            memory_types=["security_pattern", "compliance_standard"],
            cache_ttl=600
        )

        async def integrated_evaluate_security(state: QualityAssuranceState) -> QualityAssuranceState:
            await pattern.setup()

            cache_key = f"security_{hash(str(state.get('quality_standards', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=evaluate_security_logic,
                cache_key=cache_key,
                memory_content=f"Evaluated security with score {state.get('security_assessment', {}).get('overall_security_score', 0)}",
                memory_type="security_evaluation",
                importance_score=0.9
            )

            return result or state

        return integrated_evaluate_security

    def _create_finalize_qa_recommendations_node(self):
        """Create the QA recommendations finalization node with integrated pattern"""

        async def finalize_qa_recommendations_logic(state: QualityAssuranceState) -> QualityAssuranceState:
            """Generate final QA recommendations"""

            quality_metrics = state.get("quality_metrics", {})
            test_results = state.get("test_results", {})
            security_assessment = state.get("security_assessment", {})

            # Consolidate all recommendations
            all_recommendations = []

            # Quality recommendations
            quality_score = quality_metrics.get("overall_quality_score", 5.0)
            if quality_score < 7.0:
                all_recommendations.append({
                    "category": "code_quality",
                    "priority": "high",
                    "recommendation": "Improve code quality through refactoring and standards enforcement",
                    "rationale": f"Current quality score: {quality_score}/10",
                    "effort": "high",
                    "timeline": "2-4 weeks",
                    "impact": "high"
                })

            # Coverage recommendations
            coverage_metrics = quality_metrics.get("coverage_metrics", {})
            if not coverage_metrics.get("meets_target", True):
                coverage_gap = coverage_metrics.get("target_coverage", 80) - coverage_metrics.get("line_coverage", 0)
                all_recommendations.append({
                    "category": "test_coverage",
                    "priority": "medium",
                    "recommendation": f"Increase test coverage by {coverage_gap:.1f}%",
                    "rationale": "Insufficient test coverage increases risk",
                    "effort": "medium",
                    "timeline": "1-2 weeks",
                    "impact": "medium"
                })

            # Test strategy recommendations
            test_recommendations = test_results.get("test_recommendations", [])
            all_recommendations.extend(test_recommendations)

            # Security recommendations
            security_recommendations = security_assessment.get("security_recommendations", [])
            all_recommendations.extend(security_recommendations)

            # Performance recommendations
            maintainability = quality_metrics.get("maintainability_metrics", {})
            if maintainability.get("technical_debt_ratio", 0) > 10:
                all_recommendations.append({
                    "category": "technical_debt",
                    "priority": "medium",
                    "recommendation": "Address technical debt to improve maintainability",
                    "rationale": f"Technical debt ratio: {maintainability.get('technical_debt_ratio', 0):.1f}%",
                    "effort": "high",
                    "timeline": "3-6 weeks",
                    "impact": "high"
                })

            # Prioritize recommendations
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            all_recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

            # Generate quality improvements
            quality_improvements = []

            # Immediate improvements (1-2 weeks)
            immediate_improvements = [rec for rec in all_recommendations
                                   if rec.get("priority") in ["critical", "high"] and "1-2" in rec.get("timeline", "")]

            # Short-term improvements (2-4 weeks)
            short_term_improvements = [rec for rec in all_recommendations
                                     if rec.get("timeline", "").startswith("2-") or rec.get("timeline", "").startswith("3-")]

            # Long-term improvements (1+ months)
            long_term_improvements = [rec for rec in all_recommendations
                                    if "month" in rec.get("timeline", "") or "6 week" in rec.get("timeline", "")]

            quality_improvements = {
                "immediate": immediate_improvements[:5],  # Top 5 immediate
                "short_term": short_term_improvements[:8],  # Top 8 short-term
                "long_term": long_term_improvements[:5]  # Top 5 long-term
            }

            # Calculate overall QA score
            qa_score = 10.0

            # Weight different aspects
            quality_weight = 0.4
            security_weight = 0.3
            testing_weight = 0.3

            quality_contribution = quality_score * quality_weight
            security_contribution = security_assessment.get("overall_security_score", 5.0) * security_weight
            testing_contribution = test_results.get("strategy_score", 5.0) * testing_weight

            qa_score = quality_contribution + security_contribution + testing_contribution

            # Generate final summary
            qa_summary = {
                "overall_qa_score": round(qa_score, 1),
                "quality_level": "excellent" if qa_score >= 9 else "good" if qa_score >= 7 else "fair" if qa_score >= 5 else "poor",
                "total_recommendations": len(all_recommendations),
                "critical_issues": len([r for r in all_recommendations if r.get("priority") == "critical"]),
                "high_priority_issues": len([r for r in all_recommendations if r.get("priority") == "high"]),
                "estimated_effort": "4-8 weeks for full implementation",
                "confidence_level": "high" if qa_score >= 7 else "medium" if qa_score >= 5 else "low"
            }

            final_qa_results = {
                "qa_summary": qa_summary,
                "all_recommendations": all_recommendations,
                "quality_improvements": quality_improvements,
                "next_steps": [
                    "Prioritize critical and high-priority recommendations",
                    "Create implementation timeline",
                    "Assign team members to specific improvements",
                    "Set up monitoring and tracking for progress"
                ]
            }

            state["test_recommendations"] = all_recommendations
            state["quality_improvements"] = quality_improvements
            state["final_qa_results"] = final_qa_results
            state["qa_stage"] = "complete"
            state["qa_progress"] = 1.0

            logger.info(f"QA recommendations finalized. Overall score: {qa_score}/10")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="finalize_qa_recommendations",
            agent_id="qa_specialist",
            required_tools=[],
            memory_types=["qa_best_practice", "improvement_template"],
            cache_ttl=300
        )

        async def integrated_finalize_qa_recommendations(state: QualityAssuranceState) -> QualityAssuranceState:
            await pattern.setup()

            cache_key = f"finalize_qa_{hash(str(state.get('quality_metrics', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=finalize_qa_recommendations_logic,
                cache_key=cache_key,
                memory_content=f"Finalized QA with score {state.get('final_qa_results', {}).get('qa_summary', {}).get('overall_qa_score', 0)}",
                memory_type="qa_finalization",
                importance_score=1.0
            )

            return result or state

        return integrated_finalize_qa_recommendations
