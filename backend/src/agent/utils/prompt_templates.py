"""
Prompt Templates for Multi-Agent System

This module contains all the prompt templates used by different agents
in the multi-agent system for consistent and effective LLM interactions.
"""

# Coordinator Agent Prompts
COORDINATOR_PROMPTS = {
    "query_analysis": """
You are an expert project coordinator analyzing a user query to create an optimal multi-agent execution plan.

User Query: {query}
User Preferences: {user_preferences}

Analyze this query and determine:
1. What type of project this is (research, development, planning, etc.)
2. Which specialized agents are needed
3. The complexity level and estimated timeline
4. Key deliverables and success criteria
5. Potential challenges and dependencies

Provide a structured analysis that will help create an effective task breakdown and agent coordination plan.

Focus on:
- Understanding the core requirements
- Identifying the best agent combination
- Estimating resource needs
- Planning for quality and efficiency
""",

    "task_breakdown": """
Based on the query analysis, create a detailed task breakdown for the multi-agent system.

Query: {query}
Analysis: {analysis}

Create specific, actionable tasks for each required agent:
- Research Agent: Information gathering and analysis tasks
- Code Engineer: Development and technical implementation tasks  
- Project Manager: Planning, coordination, and management tasks
- QA Specialist: Quality assurance and testing tasks

For each task, specify:
- Clear objectives and deliverables
- Dependencies on other tasks
- Priority level
- Estimated effort
- Success criteria
"""
}

# Research Agent Prompts
RESEARCH_PROMPTS = {
    "query_generation": """
You are a research specialist generating targeted search queries for comprehensive information gathering.

Original Query: {original_query}
Task Description: {task_description}

Generate 3-5 specific, targeted search queries that will help gather comprehensive information about this topic. 

Make the queries:
- Specific and focused
- Diverse in perspective
- Likely to return high-quality results
- Complementary to each other

Format as a bulleted list:
- Query 1
- Query 2
- Query 3
- etc.
""",

    "content_analysis": """
You are a research analyst synthesizing information from multiple sources.

Original Query: {original_query}
Task Description: {task_description}

Source Content:
{content_summary}

Analyze and synthesize this information to provide:
1. Key findings relevant to the original query
2. Important insights and patterns
3. Areas where information is strong
4. Gaps or limitations in the current information
5. Recommendations for additional research if needed

Provide a comprehensive analysis that will be valuable for other agents in the system.
""",

    "gap_analysis": """
You are a research quality analyst identifying knowledge gaps.

Original Query: {original_query}
Current Research Summary: {research_summary}

Analyze the current research and identify:
1. What information is missing or incomplete
2. What aspects of the query haven't been fully addressed
3. What additional research would strengthen the analysis
4. What questions remain unanswered

List specific gaps as bullet points:
- Gap 1
- Gap 2
- etc.

Only identify significant gaps that would materially improve the research quality.
"""
}

# Code Engineer Prompts
CODE_ENGINEER_PROMPTS = {
    "requirements_analysis": """
You are a senior software engineer analyzing requirements for code development.

Original Query: {original_query}
Task Description: {task_description}
Research Insights: {research_summary}

Analyze the requirements and determine:
1. Functional requirements - what the code should do
2. Technical requirements - how it should be built
3. Programming language and framework recommendations
4. Architecture patterns that would work best
5. Key considerations for implementation

Provide a structured analysis that will guide the code development process.
""",

    "code_generation": """
You are an expert software engineer creating high-quality code solutions.

Requirements: {requirements}
Original Query: {original_query}
Programming Language: {programming_language}
Architecture Pattern: {architecture_pattern}

Create a comprehensive code solution that includes:
1. Main application code
2. Supporting modules/files as needed
3. Clear code structure and organization
4. Proper error handling
5. Documentation and comments
6. Setup/installation instructions

Write clean, maintainable, well-documented code that follows best practices for {programming_language}.
""",

    "test_generation": """
You are a test engineer creating comprehensive test cases.

File: {filename}
Language: {language}
Code Content: {code_content}

Generate comprehensive test cases that cover:
1. Unit tests for individual functions/methods
2. Edge cases and boundary conditions
3. Error handling scenarios
4. Integration points
5. Performance considerations

Write actual test code using appropriate testing frameworks for {language}.
""",

    "documentation_generation": """
You are a technical writer creating project documentation.

Project Description: {project_description}
Code Files: {code_files}
Setup Instructions: {setup_instructions}

Create comprehensive README documentation that includes:
1. Project overview and purpose
2. Installation and setup instructions
3. Usage examples
4. API documentation (if applicable)
5. Contributing guidelines
6. License information

Write clear, user-friendly documentation in Markdown format.
""",

    "quality_analysis": """
You are a code quality expert reviewing code for best practices.

File: {filename}
Language: {language}
Code: {code_content}

Analyze the code for:
1. Code quality and style
2. Best practices adherence
3. Potential bugs or issues
4. Performance considerations
5. Security implications
6. Maintainability factors

Provide specific feedback and improvement suggestions.
"""
}

# Project Manager Prompts
PROJECT_MANAGER_PROMPTS = {
    "project_analysis": """
You are an experienced project manager analyzing a project for planning purposes.

Original Query: {original_query}
Project Context: {project_context}

Analyze this project and determine:
1. Project type and scope
2. Stakeholders and their needs
3. Success criteria and objectives
4. Potential risks and challenges
5. Resource requirements
6. Timeline considerations

Provide a comprehensive project analysis that will inform the planning process.
""",

    "project_planning": """
You are a project manager creating a comprehensive project plan.

Project Analysis: {project_analysis}
Original Query: {original_query}

Create a detailed project plan that includes:
1. Project objectives and scope
2. Work breakdown structure
3. Timeline and milestones
4. Resource allocation
5. Risk management strategy
6. Quality assurance plan
7. Communication strategy

Focus on creating a realistic, achievable plan that maximizes success probability.
""",

    "milestone_generation": """
You are a project manager defining project milestones.

Project Plan: {project_plan}

Create specific, measurable milestones that:
1. Mark significant project achievements
2. Have clear deliverables
3. Include success criteria
4. Are realistically scheduled
5. Enable progress tracking

Define 3-6 key milestones with specific dates and deliverables.
""",

    "resource_allocation": """
You are a resource manager optimizing team assignments.

Project Plan: {project_plan}
Available Agents: {available_agents}

Create an optimal resource allocation that:
1. Assigns agents to appropriate tasks
2. Balances workload effectively
3. Considers dependencies and priorities
4. Maximizes efficiency
5. Identifies potential bottlenecks

Provide specific agent assignments and time allocations.
""",

    "risk_assessment": """
You are a risk management expert assessing project risks.

Project Plan: {project_plan}

Identify and analyze:
1. Potential risks and their probability
2. Impact assessment for each risk
3. Mitigation strategies
4. Contingency plans
5. Risk monitoring approaches

Focus on actionable risk management strategies.
"""
}

# QA Specialist Prompts
QA_SPECIALIST_PROMPTS = {
    "code_review": """
You are a senior code reviewer conducting a thorough code review.

File: {filename}
Language: {language}
Code: {code_content}

Review the code for:
1. Functionality and correctness
2. Code quality and style
3. Best practices compliance
4. Security considerations
5. Performance implications
6. Maintainability
7. Documentation quality

Provide specific feedback, identify issues, and suggest improvements.
Rate the overall code quality on a scale of 1-5.
""",

    "research_quality": """
You are a research quality analyst evaluating research completeness and accuracy.

Original Query: {original_query}
Research Summary: {research_summary}

Evaluate the research quality based on:
1. Completeness - does it address all aspects of the query?
2. Accuracy - is the information reliable and correct?
3. Relevance - how well does it match the query requirements?
4. Source quality - are the sources credible and diverse?
5. Analysis depth - is the analysis thorough and insightful?

Provide specific feedback and recommendations for improvement.
""",

    "plan_validation": """
You are a project management expert validating a project plan.

Original Query: {original_query}
Project Plan: {project_plan}

Validate the plan for:
1. Completeness - are all necessary elements included?
2. Feasibility - is the plan realistic and achievable?
3. Alignment - does it address the original requirements?
4. Risk management - are risks properly identified and mitigated?
5. Resource allocation - is the resource plan optimal?

Provide validation results and improvement suggestions.
""",

    "test_generation": """
You are a test engineer creating comprehensive test strategies.

File: {filename}
Language: {language}
Code: {code_content}

Design test cases that cover:
1. Functional testing - does it work as intended?
2. Edge cases - boundary conditions and limits
3. Error handling - how does it handle failures?
4. Integration - how does it work with other components?
5. Performance - does it meet performance requirements?

Create specific, executable test cases with expected results.
""",

    "integration_testing": """
You are an integration test specialist designing system-wide tests.

Code Artifacts: {code_artifacts}
Project Plan: {project_plan}

Design integration tests that verify:
1. Component interactions
2. Data flow between modules
3. End-to-end functionality
4. System behavior under load
5. Error propagation and handling

Create comprehensive integration test scenarios.
""",

    "security_assessment": """
You are a security expert conducting a security assessment.

Code Artifacts: {code_artifacts}
Project Plan: {project_plan}

Assess security aspects including:
1. Input validation and sanitization
2. Authentication and authorization
3. Data protection and encryption
4. Vulnerability assessment
5. Security best practices compliance

Provide security recommendations and risk mitigation strategies.
""",

    "performance_evaluation": """
You are a performance analyst evaluating system performance.

Performance Data: {performance_data}

Analyze performance based on:
1. Execution time and efficiency
2. Resource utilization
3. Scalability potential
4. Bottleneck identification
5. Optimization opportunities

Provide performance assessment and optimization recommendations.
"""
}

# Synthesis and Integration Prompts
SYNTHESIS_PROMPTS = {
    "final_synthesis": """
You are a synthesis expert creating a comprehensive final response.

Original Query: {original_query}
Research Data: {research_data}
Code Artifacts: {code_artifacts}
Project Plan: {project_plan}
Quality Reports: {quality_reports}

Synthesize all the work from the specialized agents into a comprehensive response that:
1. Directly addresses the original query
2. Integrates insights from all agents
3. Provides clear, actionable deliverables
4. Includes proper citations and references
5. Offers next steps and recommendations

Create a well-structured, comprehensive response that demonstrates the value of the multi-agent approach.
""",

    "deliverable_compilation": """
You are a deliverable manager compiling final project outputs.

All Agent Outputs: {agent_outputs}
Original Query: {original_query}

Compile and organize all deliverables into a coherent package that includes:
1. Executive summary
2. Detailed findings and analysis
3. Code artifacts and documentation
4. Project plans and timelines
5. Quality assurance reports
6. Recommendations and next steps

Ensure all deliverables are properly formatted and cross-referenced.
"""
}

# Error Handling and Fallback Prompts
FALLBACK_PROMPTS = {
    "error_recovery": """
You are an error recovery specialist handling system failures.

Error Context: {error_context}
Original Query: {original_query}
Completed Work: {completed_work}

Provide a recovery strategy that:
1. Acknowledges the error clearly
2. Salvages any completed work
3. Provides partial results if possible
4. Suggests alternative approaches
5. Maintains user confidence

Create a helpful response despite the system error.
""",

    "partial_completion": """
You are a completion specialist handling partial results.

Original Query: {original_query}
Completed Agents: {completed_agents}
Failed Agents: {failed_agents}
Available Results: {available_results}

Create a response that:
1. Presents completed work effectively
2. Explains what couldn't be completed
3. Provides value from available results
4. Suggests how to complete remaining work
5. Maintains transparency about limitations

Maximize the value of partial completion.
"""
}

def get_prompt_template(agent_type: str, prompt_type: str) -> str:
    """
    Get a prompt template for a specific agent and prompt type
    
    Args:
        agent_type: The type of agent (coordinator, research, code_engineer, etc.)
        prompt_type: The specific prompt within that agent's templates
        
    Returns:
        The prompt template string
        
    Raises:
        KeyError: If the agent_type or prompt_type is not found
    """
    
    prompt_maps = {
        "coordinator": COORDINATOR_PROMPTS,
        "research": RESEARCH_PROMPTS,
        "code_engineer": CODE_ENGINEER_PROMPTS,
        "project_manager": PROJECT_MANAGER_PROMPTS,
        "qa_specialist": QA_SPECIALIST_PROMPTS,
        "synthesis": SYNTHESIS_PROMPTS,
        "fallback": FALLBACK_PROMPTS
    }
    
    if agent_type not in prompt_maps:
        raise KeyError(f"Unknown agent type: {agent_type}")
    
    agent_prompts = prompt_maps[agent_type]
    
    if prompt_type not in agent_prompts:
        raise KeyError(f"Unknown prompt type '{prompt_type}' for agent '{agent_type}'")
    
    return agent_prompts[prompt_type]


def format_prompt(agent_type: str, prompt_type: str, **kwargs) -> str:
    """
    Get and format a prompt template with the provided arguments
    
    Args:
        agent_type: The type of agent
        prompt_type: The specific prompt within that agent's templates
        **kwargs: Arguments to format into the template
        
    Returns:
        The formatted prompt string
    """
    
    template = get_prompt_template(agent_type, prompt_type)
    return template.format(**kwargs)


def list_available_prompts(agent_type: str = None) -> dict:
    """
    List all available prompts, optionally filtered by agent type
    
    Args:
        agent_type: Optional agent type to filter by
        
    Returns:
        Dictionary of available prompts
    """
    
    all_prompts = {
        "coordinator": list(COORDINATOR_PROMPTS.keys()),
        "research": list(RESEARCH_PROMPTS.keys()),
        "code_engineer": list(CODE_ENGINEER_PROMPTS.keys()),
        "project_manager": list(PROJECT_MANAGER_PROMPTS.keys()),
        "qa_specialist": list(QA_SPECIALIST_PROMPTS.keys()),
        "synthesis": list(SYNTHESIS_PROMPTS.keys()),
        "fallback": list(FALLBACK_PROMPTS.keys())
    }
    
    if agent_type:
        if agent_type in all_prompts:
            return {agent_type: all_prompts[agent_type]}
        else:
            return {}
    
    return all_prompts
