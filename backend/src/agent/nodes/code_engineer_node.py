"""
Code Engineer Node - Advanced Software Development and Engineering

This node handles all software development tasks including code generation,
review, optimization, testing, and documentation.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langsmith import traceable

from ..multi_agent_state import MultiAgentState, CodeArtifact, QualityMetrics, AgentExecution
from ..utils.llm_utils import get_llm
from ..utils.code_utils import analyze_code_quality, generate_tests, create_documentation
from ..utils.prompt_templates import CODE_ENGINEER_PROMPTS


@traceable(name="code_engineer")
async def code_engineer_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Code Engineer node for comprehensive software development
    
    Capabilities:
    - Code generation and development
    - Code review and optimization
    - Test generation
    - Documentation creation
    - Architecture design
    - Dependency management
    """
    
    print("💻 Code Engineer: Starting software development tasks...")
    
    start_time = datetime.now()
    
    try:
        llm = get_llm(config)
        
        # Find code engineering tasks
        code_tasks = [task for task in state["tasks"] if task.agent_type == "code_engineer" and task.status == "pending"]
        
        if not code_tasks:
            print("ℹ️ No code engineering tasks found")
            return state
        
        # Execute code engineering for each task
        code_artifacts = []
        project_structure = {}
        dependencies = []
        
        for task in code_tasks:
            print(f"⚙️ Executing code task: {task.title}")
            
            # Analyze requirements from research data
            requirements = await analyze_coding_requirements(
                state["original_query"],
                state["research_data"],
                task.description,
                llm
            )
            
            # Generate code solution
            code_solution = await generate_code_solution(
                requirements,
                state["original_query"],
                llm
            )
            
            # Create code artifacts
            artifacts = await create_code_artifacts(code_solution, requirements)
            code_artifacts.extend(artifacts)
            
            # Generate tests
            test_artifacts = await generate_test_artifacts(artifacts, llm)
            code_artifacts.extend(test_artifacts)
            
            # Create documentation
            doc_artifacts = await generate_documentation_artifacts(artifacts, requirements, llm)
            code_artifacts.extend(doc_artifacts)
            
            # Update project structure
            project_structure.update(code_solution.get("project_structure", {}))
            dependencies.extend(code_solution.get("dependencies", []))
            
            # Mark task as completed
            task.status = "completed"
            task.result = {
                "artifacts_created": len(artifacts),
                "tests_generated": len(test_artifacts),
                "documentation_created": len(doc_artifacts)
            }
            task.updated_at = datetime.now()
        
        # Perform code quality analysis
        quality_analysis = await perform_code_quality_analysis(code_artifacts, llm)
        
        # Calculate quality metrics
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        quality_metrics = QualityMetrics(
            overall_score=calculate_code_quality_score(code_artifacts, quality_analysis),
            completeness=assess_code_completeness(code_artifacts),
            accuracy=assess_code_accuracy(code_artifacts),
            relevance=assess_code_relevance(code_artifacts, state["original_query"]),
            clarity=assess_code_clarity(code_artifacts),
            execution_time=execution_time,
            token_usage=estimate_code_token_usage(code_artifacts),
            error_count=0
        )
        
        # Update state
        updated_state = state.copy()
        updated_state["code_artifacts"].extend(code_artifacts)
        updated_state["project_structure"] = project_structure
        updated_state["dependencies_required"] = list(set(dependencies))
        updated_state["workflow_stage"] = "code_engineering_complete"
        
        # Add execution record
        execution = AgentExecution(
            agent_type="code_engineer",
            task_id=code_tasks[0].id if code_tasks else "code_general",
            start_time=start_time,
            end_time=end_time,
            status="completed",
            output={
                "artifacts_created": len(code_artifacts),
                "project_structure": project_structure,
                "dependencies": dependencies,
                "quality_analysis": quality_analysis
            },
            metrics=quality_metrics
        )
        updated_state["agent_executions"].append(execution)
        
        # Add performance data
        updated_state["performance_data"]["code_engineer"].append(quality_metrics)
        
        # Create code engineering summary message
        code_message = create_code_engineering_summary(code_artifacts, project_structure, quality_analysis)
        updated_state["messages"].append(AIMessage(content=code_message))
        
        print(f"✅ Code engineering completed: {len(code_artifacts)} artifacts created")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ Code engineering error: {e}")
        
        # Add error to state
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "code_engineer",
            "error": str(e),
            "context": "code_development"
        }
        
        updated_state = state.copy()
        updated_state["error_log"].append(error_entry)
        updated_state["workflow_stage"] = "code_engineering_error"
        
        # Mark code tasks as failed
        for task in state["tasks"]:
            if task.agent_type == "code_engineer" and task.status == "pending":
                task.status = "failed"
                task.error_message = str(e)
        
        return updated_state


async def analyze_coding_requirements(
    original_query: str,
    research_data: List[Dict[str, Any]],
    task_description: str,
    llm
) -> Dict[str, Any]:
    """Analyze coding requirements from query and research data"""
    
    # Combine research insights
    research_summary = ""
    for data in research_data:
        research_summary += data.get("analysis", "") + "\n\n"
    
    requirements_prompt = CODE_ENGINEER_PROMPTS["requirements_analysis"].format(
        original_query=original_query,
        task_description=task_description,
        research_summary=research_summary[:2000]  # Limit length
    )
    
    response = await llm.ainvoke(requirements_prompt)
    
    # Parse requirements (simplified)
    return {
        "functional_requirements": extract_functional_requirements(response.content),
        "technical_requirements": extract_technical_requirements(response.content),
        "programming_language": determine_programming_language(original_query),
        "architecture_pattern": determine_architecture_pattern(original_query),
        "complexity_level": assess_code_complexity(original_query)
    }


async def generate_code_solution(
    requirements: Dict[str, Any],
    original_query: str,
    llm
) -> Dict[str, Any]:
    """Generate comprehensive code solution"""
    
    solution_prompt = CODE_ENGINEER_PROMPTS["code_generation"].format(
        requirements=requirements,
        original_query=original_query,
        programming_language=requirements.get("programming_language", "python"),
        architecture_pattern=requirements.get("architecture_pattern", "modular")
    )
    
    response = await llm.ainvoke(solution_prompt)
    
    # Parse code solution
    return {
        "main_code": extract_main_code(response.content),
        "supporting_files": extract_supporting_files(response.content),
        "project_structure": extract_project_structure(response.content),
        "dependencies": extract_dependencies(response.content),
        "setup_instructions": extract_setup_instructions(response.content)
    }


async def create_code_artifacts(
    code_solution: Dict[str, Any],
    requirements: Dict[str, Any]
) -> List[CodeArtifact]:
    """Create code artifacts from the solution"""
    
    artifacts = []
    
    # Main code artifact
    main_code = code_solution.get("main_code", "")
    if main_code:
        artifact = CodeArtifact(
            id=f"main_{uuid.uuid4().hex[:8]}",
            filename=determine_main_filename(requirements.get("programming_language", "python")),
            content=main_code,
            language=requirements.get("programming_language", "python"),
            description="Main application code",
            author="code_engineer"
        )
        artifacts.append(artifact)
    
    # Supporting files
    supporting_files = code_solution.get("supporting_files", {})
    for filename, content in supporting_files.items():
        artifact = CodeArtifact(
            id=f"support_{uuid.uuid4().hex[:8]}",
            filename=filename,
            content=content,
            language=detect_language_from_filename(filename),
            description=f"Supporting file: {filename}",
            author="code_engineer"
        )
        artifacts.append(artifact)
    
    return artifacts


async def generate_test_artifacts(artifacts: List[CodeArtifact], llm) -> List[CodeArtifact]:
    """Generate test artifacts for code"""
    
    test_artifacts = []
    
    for artifact in artifacts:
        if artifact.language in ["python", "javascript", "java", "go"]:
            test_prompt = CODE_ENGINEER_PROMPTS["test_generation"].format(
                filename=artifact.filename,
                code_content=artifact.content,
                language=artifact.language
            )
            
            response = await llm.ainvoke(test_prompt)
            
            test_artifact = CodeArtifact(
                id=f"test_{uuid.uuid4().hex[:8]}",
                filename=generate_test_filename(artifact.filename, artifact.language),
                content=response.content,
                language=artifact.language,
                description=f"Tests for {artifact.filename}",
                author="code_engineer",
                tests_included=True
            )
            test_artifacts.append(test_artifact)
    
    return test_artifacts


async def generate_documentation_artifacts(
    artifacts: List[CodeArtifact],
    requirements: Dict[str, Any],
    llm
) -> List[CodeArtifact]:
    """Generate documentation artifacts"""
    
    doc_artifacts = []
    
    # README documentation
    readme_prompt = CODE_ENGINEER_PROMPTS["documentation_generation"].format(
        project_description=requirements.get("functional_requirements", ""),
        code_files=[a.filename for a in artifacts],
        setup_instructions=requirements.get("setup_instructions", "")
    )
    
    response = await llm.ainvoke(readme_prompt)
    
    readme_artifact = CodeArtifact(
        id=f"doc_{uuid.uuid4().hex[:8]}",
        filename="README.md",
        content=response.content,
        language="markdown",
        description="Project documentation",
        author="code_engineer",
        documentation=response.content
    )
    doc_artifacts.append(readme_artifact)
    
    return doc_artifacts


async def perform_code_quality_analysis(artifacts: List[CodeArtifact], llm) -> Dict[str, Any]:
    """Perform comprehensive code quality analysis"""
    
    quality_issues = []
    suggestions = []
    
    for artifact in artifacts:
        if artifact.language in ["python", "javascript", "java", "go"]:
            analysis_prompt = CODE_ENGINEER_PROMPTS["quality_analysis"].format(
                filename=artifact.filename,
                code_content=artifact.content,
                language=artifact.language
            )
            
            response = await llm.ainvoke(analysis_prompt)
            
            # Parse quality analysis
            issues = extract_quality_issues(response.content)
            quality_issues.extend(issues)
            
            improvements = extract_improvement_suggestions(response.content)
            suggestions.extend(improvements)
    
    return {
        "quality_issues": quality_issues,
        "improvement_suggestions": suggestions,
        "overall_quality": "high" if len(quality_issues) < 3 else "medium",
        "code_coverage": estimate_code_coverage(artifacts)
    }


# Helper functions for code processing

def extract_functional_requirements(content: str) -> List[str]:
    """Extract functional requirements from LLM response"""
    # Simplified extraction
    lines = content.split('\n')
    requirements = []
    for line in lines:
        if 'requirement' in line.lower() or 'function' in line.lower():
            requirements.append(line.strip())
    return requirements[:5]  # Limit to 5


def extract_technical_requirements(content: str) -> List[str]:
    """Extract technical requirements from LLM response"""
    # Simplified extraction
    return ["Modern architecture", "Clean code", "Error handling", "Documentation"]


def determine_programming_language(query: str) -> str:
    """Determine programming language from query"""
    query_lower = query.lower()
    
    if any(lang in query_lower for lang in ["python", "py"]):
        return "python"
    elif any(lang in query_lower for lang in ["javascript", "js", "node"]):
        return "javascript"
    elif "java" in query_lower:
        return "java"
    elif any(lang in query_lower for lang in ["go", "golang"]):
        return "go"
    elif any(lang in query_lower for lang in ["rust", "rs"]):
        return "rust"
    else:
        return "python"  # Default


def determine_architecture_pattern(query: str) -> str:
    """Determine architecture pattern from query"""
    query_lower = query.lower()
    
    if "microservice" in query_lower:
        return "microservices"
    elif "mvc" in query_lower:
        return "mvc"
    elif "api" in query_lower:
        return "api"
    else:
        return "modular"


def assess_code_complexity(query: str) -> str:
    """Assess code complexity from query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["simple", "basic", "quick"]):
        return "low"
    elif any(word in query_lower for word in ["complex", "advanced", "enterprise"]):
        return "high"
    else:
        return "medium"


def extract_main_code(content: str) -> str:
    """Extract main code from LLM response"""
    # Look for code blocks
    lines = content.split('\n')
    in_code_block = False
    code_lines = []
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            code_lines.append(line)
    
    return '\n'.join(code_lines) if code_lines else content


def extract_supporting_files(content: str) -> Dict[str, str]:
    """Extract supporting files from LLM response"""
    # Simplified - would be more sophisticated in real implementation
    return {}


def extract_project_structure(content: str) -> Dict[str, Any]:
    """Extract project structure from LLM response"""
    return {
        "type": "application",
        "structure": "modular",
        "entry_point": "main.py"
    }


def extract_dependencies(content: str) -> List[str]:
    """Extract dependencies from LLM response"""
    dependencies = []
    lines = content.split('\n')
    
    for line in lines:
        if 'import' in line or 'require' in line:
            # Extract dependency name (simplified)
            parts = line.split()
            if len(parts) > 1:
                dependencies.append(parts[1])
    
    return dependencies


def extract_setup_instructions(content: str) -> str:
    """Extract setup instructions from LLM response"""
    return "1. Install dependencies\n2. Run the application\n3. Follow usage instructions"


def determine_main_filename(language: str) -> str:
    """Determine main filename based on language"""
    filename_map = {
        "python": "main.py",
        "javascript": "index.js",
        "java": "Main.java",
        "go": "main.go",
        "rust": "main.rs"
    }
    return filename_map.get(language, "main.py")


def detect_language_from_filename(filename: str) -> str:
    """Detect programming language from filename"""
    extension = Path(filename).suffix.lower()
    
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".md": "markdown",
        ".txt": "text"
    }
    
    return extension_map.get(extension, "text")


def generate_test_filename(original_filename: str, language: str) -> str:
    """Generate test filename for a given file"""
    name = Path(original_filename).stem
    
    if language == "python":
        return f"test_{name}.py"
    elif language == "javascript":
        return f"{name}.test.js"
    elif language == "java":
        return f"{name}Test.java"
    elif language == "go":
        return f"{name}_test.go"
    else:
        return f"test_{name}.{Path(original_filename).suffix}"


def extract_quality_issues(content: str) -> List[str]:
    """Extract quality issues from analysis"""
    # Simplified extraction
    return ["Minor style issues", "Consider adding error handling"]


def extract_improvement_suggestions(content: str) -> List[str]:
    """Extract improvement suggestions from analysis"""
    return ["Add type hints", "Improve documentation", "Add logging"]


def estimate_code_coverage(artifacts: List[CodeArtifact]) -> float:
    """Estimate code coverage based on tests"""
    code_files = [a for a in artifacts if not a.tests_included and a.language != "markdown"]
    test_files = [a for a in artifacts if a.tests_included]
    
    if not code_files:
        return 0.0
    
    coverage = min(1.0, len(test_files) / len(code_files))
    return coverage


def calculate_code_quality_score(artifacts: List[CodeArtifact], quality_analysis: Dict[str, Any]) -> float:
    """Calculate overall code quality score"""
    base_score = 4.0
    
    # Adjust based on quality analysis
    issues_count = len(quality_analysis.get("quality_issues", []))
    if issues_count > 5:
        base_score -= 1.0
    elif issues_count > 2:
        base_score -= 0.5
    
    # Adjust based on test coverage
    coverage = quality_analysis.get("code_coverage", 0.0)
    base_score += coverage * 0.5
    
    return min(5.0, max(1.0, base_score))


def assess_code_completeness(artifacts: List[CodeArtifact]) -> float:
    """Assess code completeness"""
    has_main = any(a.filename.startswith("main") for a in artifacts)
    has_tests = any(a.tests_included for a in artifacts)
    has_docs = any(a.language == "markdown" for a in artifacts)
    
    completeness = 0.4  # Base
    if has_main:
        completeness += 0.3
    if has_tests:
        completeness += 0.2
    if has_docs:
        completeness += 0.1
    
    return completeness


def assess_code_accuracy(artifacts: List[CodeArtifact]) -> float:
    """Assess code accuracy (simplified)"""
    return 0.9  # Placeholder


def assess_code_relevance(artifacts: List[CodeArtifact], query: str) -> float:
    """Assess code relevance to query"""
    return 0.85  # Placeholder


def assess_code_clarity(artifacts: List[CodeArtifact]) -> float:
    """Assess code clarity"""
    return 0.8  # Placeholder


def estimate_code_token_usage(artifacts: List[CodeArtifact]) -> int:
    """Estimate token usage for code generation"""
    total_content = sum(len(a.content) for a in artifacts)
    return int(total_content / 4)


def create_code_engineering_summary(
    artifacts: List[CodeArtifact],
    project_structure: Dict[str, Any],
    quality_analysis: Dict[str, Any]
) -> str:
    """Create code engineering summary"""
    
    message = f"""💻 **Code Engineer Report**

**Development Completed:**
- Files created: {len(artifacts)}
- Languages used: {', '.join(set(a.language for a in artifacts))}
- Tests included: {sum(1 for a in artifacts if a.tests_included)}
- Documentation: {sum(1 for a in artifacts if a.language == 'markdown')}

**Project Structure:**
- Type: {project_structure.get('type', 'Application')}
- Architecture: {project_structure.get('structure', 'Modular')}
- Entry point: {project_structure.get('entry_point', 'main file')}

**Code Quality:**
- Overall quality: {quality_analysis.get('overall_quality', 'High')}
- Issues identified: {len(quality_analysis.get('quality_issues', []))}
- Test coverage: {quality_analysis.get('code_coverage', 0.0):.1%}

**Files Created:**
"""
    
    for artifact in artifacts:
        message += f"- `{artifact.filename}` ({artifact.language}) - {artifact.description}\n"
    
    message += """
**Next Steps:**
Code artifacts are ready for quality assurance review and testing.
"""
    
    return message
