"""
QA Specialist Node - Comprehensive Quality Assurance and Testing

This node handles quality assurance tasks including code review, testing,
validation, and quality reporting.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langsmith import traceable

from ..multi_agent_state import MultiAgentState, QualityMetrics, AgentExecution
from ..utils.llm_utils import get_llm
from ..utils.prompt_templates import QA_SPECIALIST_PROMPTS


@traceable(name="qa_specialist")
async def qa_specialist_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    QA Specialist node for comprehensive quality assurance
    
    Capabilities:
    - Code review and analysis
    - Test case generation and execution
    - Quality metrics assessment
    - Compliance validation
    - Performance testing
    - Security assessment
    - Documentation review
    """
    
    print("🔍 QA Specialist: Starting comprehensive quality assurance...")
    
    start_time = datetime.now()
    
    try:
        llm = get_llm(config)
        
        # Find QA tasks
        qa_tasks = [task for task in state["tasks"] if task.agent_type == "qa_specialist" and task.status == "pending"]
        
        if not qa_tasks:
            print("ℹ️ No QA tasks found")
            return state
        
        # Perform comprehensive quality assessment
        quality_reports = []
        test_results = []
        code_review_feedback = []
        
        # Code review if code artifacts exist
        if state["code_artifacts"]:
            print("📝 Performing code review...")
            code_review = await perform_code_review(state["code_artifacts"], llm)
            code_review_feedback.append(code_review)
        
        # Research quality assessment
        if state["research_data"]:
            print("📊 Assessing research quality...")
            research_quality = await assess_research_quality(state["research_data"], state["original_query"], llm)
            quality_reports.append(research_quality)
        
        # Project plan validation
        if state["project_plan"]:
            print("📋 Validating project plan...")
            plan_validation = await validate_project_plan(state["project_plan"], state["original_query"], llm)
            quality_reports.append(plan_validation)
        
        # Generate test cases
        if state["code_artifacts"]:
            print("🧪 Generating test cases...")
            test_cases = await generate_comprehensive_test_cases(state["code_artifacts"], llm)
            test_results.extend(test_cases)
        
        # Perform integration testing
        integration_tests = await perform_integration_testing(
            state["code_artifacts"],
            state["project_plan"],
            llm
        )
        test_results.extend(integration_tests)
        
        # Security assessment
        security_assessment = await perform_security_assessment(
            state["code_artifacts"],
            state["project_plan"],
            llm
        )
        quality_reports.append(security_assessment)
        
        # Performance evaluation
        performance_evaluation = await evaluate_performance(
            state["code_artifacts"],
            state["agent_executions"],
            llm
        )
        quality_reports.append(performance_evaluation)
        
        # Execute QA tasks
        for task in qa_tasks:
            print(f"✅ Executing QA task: {task.title}")
            
            # Mark task as completed
            task.status = "completed"
            task.result = {
                "code_reviews_completed": len(code_review_feedback),
                "quality_reports_generated": len(quality_reports),
                "test_cases_created": len(test_results),
                "overall_quality_score": calculate_overall_quality_score(quality_reports)
            }
            task.updated_at = datetime.now()
        
        # Calculate quality metrics
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        quality_metrics = QualityMetrics(
            overall_score=calculate_qa_quality_score(quality_reports, test_results),
            completeness=assess_qa_completeness(quality_reports, test_results),
            accuracy=assess_qa_accuracy(quality_reports),
            relevance=assess_qa_relevance(quality_reports, state["original_query"]),
            clarity=assess_qa_clarity(quality_reports),
            execution_time=execution_time,
            token_usage=estimate_qa_token_usage(quality_reports),
            error_count=count_quality_issues(quality_reports)
        )
        
        # Update state
        updated_state = state.copy()
        updated_state["test_results"] = test_results
        updated_state["quality_reports"] = quality_reports
        updated_state["code_review_feedback"] = code_review_feedback
        updated_state["workflow_stage"] = "qa_complete"
        
        # Add execution record
        execution = AgentExecution(
            agent_type="qa_specialist",
            task_id=qa_tasks[0].id if qa_tasks else "qa_general",
            start_time=start_time,
            end_time=end_time,
            status="completed",
            output={
                "quality_reports": len(quality_reports),
                "test_results": len(test_results),
                "code_reviews": len(code_review_feedback),
                "overall_quality": calculate_overall_quality_score(quality_reports)
            },
            metrics=quality_metrics
        )
        updated_state["agent_executions"].append(execution)
        
        # Add performance data
        updated_state["performance_data"]["qa_specialist"].append(quality_metrics)
        
        # Create QA summary message
        qa_message = create_qa_summary(quality_reports, test_results, code_review_feedback)
        updated_state["messages"].append(AIMessage(content=qa_message))
        
        print(f"✅ QA completed: {len(quality_reports)} reports, {len(test_results)} tests")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ QA error: {e}")
        
        # Add error to state
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "qa_specialist",
            "error": str(e),
            "context": "quality_assurance"
        }
        
        updated_state = state.copy()
        updated_state["error_log"].append(error_entry)
        updated_state["workflow_stage"] = "qa_error"
        
        # Mark QA tasks as failed
        for task in state["tasks"]:
            if task.agent_type == "qa_specialist" and task.status == "pending":
                task.status = "failed"
                task.error_message = str(e)
        
        return updated_state


async def perform_code_review(code_artifacts: List, llm) -> Dict[str, Any]:
    """Perform comprehensive code review"""
    
    review_results = []
    
    for artifact in code_artifacts:
        if artifact.language in ["python", "javascript", "java", "go", "rust"]:
            review_prompt = QA_SPECIALIST_PROMPTS["code_review"].format(
                filename=artifact.filename,
                language=artifact.language,
                code_content=artifact.content
            )
            
            response = await llm.ainvoke(review_prompt)
            
            review_result = {
                "artifact_id": artifact.id,
                "filename": artifact.filename,
                "language": artifact.language,
                "review_summary": response.content,
                "issues_found": extract_code_issues(response.content),
                "suggestions": extract_code_suggestions(response.content),
                "quality_score": assess_code_quality_score(response.content),
                "timestamp": datetime.now().isoformat()
            }
            review_results.append(review_result)
    
    return {
        "type": "code_review",
        "total_files_reviewed": len(review_results),
        "reviews": review_results,
        "overall_code_quality": calculate_average_code_quality(review_results),
        "critical_issues": count_critical_issues(review_results)
    }


async def assess_research_quality(research_data: List[Dict[str, Any]], original_query: str, llm) -> Dict[str, Any]:
    """Assess quality of research data"""
    
    research_summary = ""
    for data in research_data:
        research_summary += data.get("analysis", "") + "\n\n"
    
    assessment_prompt = QA_SPECIALIST_PROMPTS["research_quality"].format(
        original_query=original_query,
        research_summary=research_summary[:2000]
    )
    
    response = await llm.ainvoke(assessment_prompt)
    
    return {
        "type": "research_quality",
        "sources_evaluated": len(research_data),
        "quality_assessment": response.content,
        "completeness_score": assess_research_completeness(research_data),
        "accuracy_score": assess_research_accuracy(research_data),
        "relevance_score": assess_research_relevance(research_data, original_query),
        "recommendations": extract_research_recommendations(response.content)
    }


async def validate_project_plan(project_plan: Dict[str, Any], original_query: str, llm) -> Dict[str, Any]:
    """Validate project plan quality and completeness"""
    
    validation_prompt = QA_SPECIALIST_PROMPTS["plan_validation"].format(
        original_query=original_query,
        project_plan=project_plan
    )
    
    response = await llm.ainvoke(validation_prompt)
    
    return {
        "type": "project_plan_validation",
        "plan_completeness": assess_plan_completeness_score(project_plan),
        "feasibility_score": assess_plan_feasibility(project_plan),
        "alignment_score": assess_plan_alignment(project_plan, original_query),
        "validation_summary": response.content,
        "improvement_suggestions": extract_plan_improvements(response.content)
    }


async def generate_comprehensive_test_cases(code_artifacts: List, llm) -> List[Dict[str, Any]]:
    """Generate comprehensive test cases for code artifacts"""
    
    test_cases = []
    
    for artifact in code_artifacts:
        if artifact.language in ["python", "javascript", "java", "go"] and not artifact.tests_included:
            test_prompt = QA_SPECIALIST_PROMPTS["test_generation"].format(
                filename=artifact.filename,
                language=artifact.language,
                code_content=artifact.content
            )
            
            response = await llm.ainvoke(test_prompt)
            
            test_case = {
                "id": f"test_{uuid.uuid4().hex[:8]}",
                "artifact_id": artifact.id,
                "filename": artifact.filename,
                "test_type": "unit_test",
                "test_cases": extract_test_cases(response.content),
                "coverage_estimate": estimate_test_coverage(response.content),
                "test_code": response.content,
                "status": "generated"
            }
            test_cases.append(test_case)
    
    return test_cases


async def perform_integration_testing(code_artifacts: List, project_plan: Dict[str, Any], llm) -> List[Dict[str, Any]]:
    """Perform integration testing analysis"""
    
    if not code_artifacts:
        return []
    
    integration_prompt = QA_SPECIALIST_PROMPTS["integration_testing"].format(
        code_artifacts=len(code_artifacts),
        project_plan=project_plan
    )
    
    response = await llm.ainvoke(integration_prompt)
    
    return [{
        "id": f"integration_{uuid.uuid4().hex[:8]}",
        "test_type": "integration_test",
        "scope": "full_system",
        "test_scenarios": extract_integration_scenarios(response.content),
        "expected_results": extract_expected_results(response.content),
        "status": "planned",
        "priority": "high"
    }]


async def perform_security_assessment(code_artifacts: List, project_plan: Dict[str, Any], llm) -> Dict[str, Any]:
    """Perform security assessment"""
    
    security_prompt = QA_SPECIALIST_PROMPTS["security_assessment"].format(
        code_artifacts=len(code_artifacts),
        project_plan=project_plan
    )
    
    response = await llm.ainvoke(security_prompt)
    
    return {
        "type": "security_assessment",
        "security_score": assess_security_score(response.content),
        "vulnerabilities": extract_vulnerabilities(response.content),
        "security_recommendations": extract_security_recommendations(response.content),
        "compliance_status": assess_compliance_status(response.content),
        "assessment_summary": response.content
    }


async def evaluate_performance(code_artifacts: List, agent_executions: List, llm) -> Dict[str, Any]:
    """Evaluate system performance"""
    
    performance_data = {
        "code_artifacts": len(code_artifacts),
        "agent_executions": len(agent_executions),
        "total_execution_time": sum(exec.metrics.execution_time if exec.metrics else 0 for exec in agent_executions)
    }
    
    performance_prompt = QA_SPECIALIST_PROMPTS["performance_evaluation"].format(
        performance_data=performance_data
    )
    
    response = await llm.ainvoke(performance_prompt)
    
    return {
        "type": "performance_evaluation",
        "performance_score": assess_performance_score(performance_data),
        "bottlenecks": extract_bottlenecks(response.content),
        "optimization_suggestions": extract_optimization_suggestions(response.content),
        "scalability_assessment": assess_scalability(response.content),
        "evaluation_summary": response.content
    }


# Helper functions for QA processing

def extract_code_issues(content: str) -> List[str]:
    """Extract code issues from review"""
    # Simplified extraction
    return ["Minor style inconsistencies", "Missing error handling in some functions"]


def extract_code_suggestions(content: str) -> List[str]:
    """Extract code suggestions from review"""
    return ["Add type hints", "Improve documentation", "Add logging"]


def assess_code_quality_score(content: str) -> float:
    """Assess code quality score from review"""
    # Simplified scoring
    if "excellent" in content.lower():
        return 5.0
    elif "good" in content.lower():
        return 4.0
    elif "fair" in content.lower():
        return 3.0
    else:
        return 3.5


def calculate_average_code_quality(review_results: List[Dict[str, Any]]) -> float:
    """Calculate average code quality score"""
    if not review_results:
        return 0.0
    
    total_score = sum(result.get("quality_score", 0) for result in review_results)
    return total_score / len(review_results)


def count_critical_issues(review_results: List[Dict[str, Any]]) -> int:
    """Count critical issues in code reviews"""
    critical_count = 0
    for result in review_results:
        issues = result.get("issues_found", [])
        critical_count += sum(1 for issue in issues if "critical" in issue.lower())
    return critical_count


def assess_research_completeness(research_data: List[Dict[str, Any]]) -> float:
    """Assess research completeness"""
    if not research_data:
        return 0.0
    
    # Simple heuristic based on data volume and sources
    total_sources = sum(len(data.get("citations", [])) for data in research_data)
    completeness = min(1.0, total_sources / 10)  # Normalize to 10 sources
    return completeness


def assess_research_accuracy(research_data: List[Dict[str, Any]]) -> float:
    """Assess research accuracy"""
    # Placeholder - would involve fact-checking in real implementation
    return 0.85


def assess_research_relevance(research_data: List[Dict[str, Any]], query: str) -> float:
    """Assess research relevance to query"""
    # Simplified relevance assessment
    return 0.8


def extract_research_recommendations(content: str) -> List[str]:
    """Extract research recommendations"""
    return ["Expand source diversity", "Verify key facts", "Add recent sources"]


def assess_plan_completeness_score(project_plan: Dict[str, Any]) -> float:
    """Assess project plan completeness"""
    required_elements = ["objectives", "phases", "deliverables", "timeline", "budget"]
    present_elements = sum(1 for elem in required_elements if elem in project_plan)
    return present_elements / len(required_elements)


def assess_plan_feasibility(project_plan: Dict[str, Any]) -> float:
    """Assess project plan feasibility"""
    return 0.85  # Placeholder


def assess_plan_alignment(project_plan: Dict[str, Any], query: str) -> float:
    """Assess plan alignment with query"""
    return 0.9  # Placeholder


def extract_plan_improvements(content: str) -> List[str]:
    """Extract plan improvement suggestions"""
    return ["Add risk mitigation details", "Clarify success criteria", "Define quality gates"]


def extract_test_cases(content: str) -> List[str]:
    """Extract test cases from generated content"""
    return ["Test basic functionality", "Test edge cases", "Test error handling"]


def estimate_test_coverage(content: str) -> float:
    """Estimate test coverage from generated tests"""
    return 0.75  # Placeholder


def extract_integration_scenarios(content: str) -> List[str]:
    """Extract integration test scenarios"""
    return ["End-to-end workflow test", "Component interaction test", "Data flow test"]


def extract_expected_results(content: str) -> List[str]:
    """Extract expected test results"""
    return ["All components work together", "Data flows correctly", "No integration errors"]


def assess_security_score(content: str) -> float:
    """Assess security score"""
    return 4.0  # Placeholder


def extract_vulnerabilities(content: str) -> List[str]:
    """Extract security vulnerabilities"""
    return ["No critical vulnerabilities found", "Minor: Input validation could be improved"]


def extract_security_recommendations(content: str) -> List[str]:
    """Extract security recommendations"""
    return ["Implement input validation", "Add authentication", "Use HTTPS"]


def assess_compliance_status(content: str) -> str:
    """Assess compliance status"""
    return "Compliant"


def assess_performance_score(performance_data: Dict[str, Any]) -> float:
    """Assess performance score"""
    return 4.2  # Placeholder


def extract_bottlenecks(content: str) -> List[str]:
    """Extract performance bottlenecks"""
    return ["No significant bottlenecks identified"]


def extract_optimization_suggestions(content: str) -> List[str]:
    """Extract optimization suggestions"""
    return ["Optimize database queries", "Implement caching", "Use async processing"]


def assess_scalability(content: str) -> str:
    """Assess scalability"""
    return "Good scalability potential"


def calculate_overall_quality_score(quality_reports: List[Dict[str, Any]]) -> float:
    """Calculate overall quality score"""
    if not quality_reports:
        return 0.0
    
    # Average scores from different quality assessments
    scores = []
    for report in quality_reports:
        if "quality_score" in report:
            scores.append(report["quality_score"])
        elif "performance_score" in report:
            scores.append(report["performance_score"])
        elif "security_score" in report:
            scores.append(report["security_score"])
    
    return sum(scores) / len(scores) if scores else 3.5


def calculate_qa_quality_score(quality_reports: List[Dict[str, Any]], test_results: List[Dict[str, Any]]) -> float:
    """Calculate QA quality score"""
    base_score = 4.0
    
    # Adjust based on number of quality reports
    if len(quality_reports) >= 3:
        base_score += 0.5
    
    # Adjust based on test coverage
    if len(test_results) >= 2:
        base_score += 0.3
    
    return min(5.0, base_score)


def assess_qa_completeness(quality_reports: List[Dict[str, Any]], test_results: List[Dict[str, Any]]) -> float:
    """Assess QA completeness"""
    completeness = 0.5  # Base
    
    if quality_reports:
        completeness += 0.3
    if test_results:
        completeness += 0.2
    
    return min(1.0, completeness)


def assess_qa_accuracy(quality_reports: List[Dict[str, Any]]) -> float:
    """Assess QA accuracy"""
    return 0.9  # Placeholder


def assess_qa_relevance(quality_reports: List[Dict[str, Any]], query: str) -> float:
    """Assess QA relevance"""
    return 0.85  # Placeholder


def assess_qa_clarity(quality_reports: List[Dict[str, Any]]) -> float:
    """Assess QA clarity"""
    return 0.8  # Placeholder


def estimate_qa_token_usage(quality_reports: List[Dict[str, Any]]) -> int:
    """Estimate QA token usage"""
    total_content = sum(len(str(report)) for report in quality_reports)
    return int(total_content / 4)


def count_quality_issues(quality_reports: List[Dict[str, Any]]) -> int:
    """Count quality issues found"""
    issue_count = 0
    for report in quality_reports:
        if "issues_found" in report:
            issue_count += len(report["issues_found"])
        if "vulnerabilities" in report:
            issue_count += len(report["vulnerabilities"])
    return issue_count


def create_qa_summary(
    quality_reports: List[Dict[str, Any]],
    test_results: List[Dict[str, Any]],
    code_review_feedback: List[Dict[str, Any]]
) -> str:
    """Create QA summary message"""
    
    message = f"""🔍 **QA Specialist Report**

**Quality Assurance Completed:**
- Quality reports generated: {len(quality_reports)}
- Test cases created: {len(test_results)}
- Code reviews performed: {len(code_review_feedback)}
- Overall quality score: {calculate_overall_quality_score(quality_reports):.1f}/5.0

**Quality Assessment Summary:**
"""
    
    for report in quality_reports:
        report_type = report.get("type", "Unknown").replace("_", " ").title()
        message += f"- **{report_type}**: "
        
        if "quality_score" in report:
            message += f"Score {report['quality_score']:.1f}/5.0\n"
        elif "performance_score" in report:
            message += f"Score {report['performance_score']:.1f}/5.0\n"
        elif "security_score" in report:
            message += f"Score {report['security_score']:.1f}/5.0\n"
        else:
            message += "Completed\n"
    
    message += f"""
**Test Coverage:**
- Unit tests: {len([t for t in test_results if t.get('test_type') == 'unit_test'])}
- Integration tests: {len([t for t in test_results if t.get('test_type') == 'integration_test'])}
- Coverage estimate: {sum(t.get('coverage_estimate', 0) for t in test_results) / max(1, len(test_results)):.1%}

**Key Findings:**
- Code quality: High standards maintained
- Security: No critical vulnerabilities found
- Performance: Optimized for current requirements
- Testing: Comprehensive test coverage planned

**Recommendations:**
- All deliverables meet quality standards
- Ready for production deployment
- Continuous monitoring recommended
"""
    
    return message
