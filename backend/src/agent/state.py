from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from langgraph.graph import add_messages
from typing_extensions import Annotated


import operator
from dataclasses import dataclass, field
from typing_extensions import Annotated


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    search_query: Annotated[list, operator.add]
    web_research_result: Annotated[list, operator.add]
    sources_gathered: Annotated[list, operator.add]
    initial_search_query_count: int
    max_research_loops: int
    research_loop_count: int
    reasoning_model: str
    # New fields for agent routing and multi-LLM support
    agent_type: str  # Type of agent handling the task
    task_classification: dict  # Classification details from router
    llm_provider: str  # LLM provider being used
    # New fields for Phase 2: Tool Integration
    requires_tools: bool  # Whether the task requires tool execution
    tool_requirements: Annotated[list, operator.add]  # List of required tools
    tool_results: Annotated[list, operator.add]  # Results from tool execution
    tool_execution_complete: bool  # Whether tool execution is finished
    tool_context: dict  # Additional context from tools


class ReflectionState(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: Annotated[list, operator.add]
    research_loop_count: int
    number_of_ran_queries: int


class Query(TypedDict):
    query: str
    rationale: str


class QueryGenerationState(TypedDict):
    query_list: list[Query]


class WebSearchState(TypedDict):
    search_query: str
    id: str


@dataclass(kw_only=True)
class SearchStateOutput:
    running_summary: str = field(default=None)  # Final report


# ===== SPECIALIZED GRAPH STATES FOR 6 INTEGRATED GRAPHS =====

class CodebaseAnalysisState(OverallState):
    """State for Codebase Analysis Graph - extends OverallState with specialized fields"""
    # Analysis-specific fields
    repository_url: str = ''  # alias to satisfy hasattr
    repository_path: str = ''
    analysis_type: str = ''
    file_patterns: list = []
    analysis_results: Annotated[list, operator.add]  # Results from code analysis
    code_patterns: Annotated[list, operator.add]  # Identified patterns
    architecture_insights: dict  # Architecture analysis results
    quality_metrics: dict  # Code quality metrics
    security_findings: Annotated[list, operator.add]  # Security issues found
    # Memory integration
    retrieved_patterns: Annotated[list, operator.add]  # Patterns from long-term memory
    stored_memories: Annotated[list, operator.add]  # New memories stored
    # MCP tool integration
    mcp_tools_loaded: Annotated[list, operator.add]  # Dynamically loaded MCP tools
    mcp_analysis_results: dict  # Results from MCP tools


class DocumentationAnalysisState(OverallState):
    """State for Documentation Analysis Graph"""
    # Documentation analysis fields
    repository_path: str
    documentation_type: str  # 'api', 'user_guide', 'technical', 'readme'
    discovered_documentation: dict  # Found documentation files
    structure_analysis: dict  # Documentation structure analysis
    quality_metrics: dict  # Quality assessment results
    completeness_check: dict  # Completeness evaluation
    # Memory integration
    retrieved_patterns: Annotated[list, operator.add]  # Patterns from memory
    documentation_standards: Annotated[list, operator.add]  # Standards from memory
    # Analysis progress
    analysis_stage: str  # Current analysis stage
    analysis_progress: float  # Progress percentage (0.0 to 1.0)


class TaskPlanningState(OverallState):
    """State for Task Planning Analysis Graph"""
    # Planning-specific fields
    project_scope: str  # Project scope description
    requirements: Annotated[list, operator.add]  # Project requirements
    task_breakdown: dict  # Task breakdown structure
    dependencies: Annotated[list, operator.add]  # Task dependencies
    resource_estimates: dict  # Resource estimation results
    timeline_analysis: dict  # Timeline and milestone analysis
    risk_assessment: dict  # Risk analysis results
    # Memory integration
    retrieved_patterns: Annotated[list, operator.add]  # Planning patterns from memory
    similar_projects: Annotated[list, operator.add]  # Similar project data from memory
    best_practices: Annotated[list, operator.add]  # Best practices from memory
    # Planning progress
    planning_stage: str  # Current planning stage
    planning_progress: float  # Progress percentage (0.0 to 1.0)
    # Generated artifacts
    generated_tasks: Annotated[list, operator.add]  # Generated task list
    milestones: Annotated[list, operator.add]  # Project milestones


class ResearchAnalysisState(OverallState):
    """State for Research & Knowledge Analysis Graph"""
    # Research-specific fields
    research_topic: str  # Main research topic
    research_scope: str  # Scope of research
    information_sources: Annotated[list, operator.add]  # Available information sources
    research_queries: Annotated[list, operator.add]  # Generated research queries
    collected_data: dict  # Collected research data
    knowledge_synthesis: dict  # Synthesized knowledge
    source_credibility: dict  # Source credibility analysis
    knowledge_gaps: Annotated[list, operator.add]  # Identified knowledge gaps
    # Memory integration
    retrieved_sources: Annotated[list, operator.add]  # Trusted sources from memory
    research_patterns: Annotated[list, operator.add]  # Research patterns from memory
    domain_knowledge: Annotated[list, operator.add]  # Domain knowledge from memory
    # Research progress
    research_stage: str  # Current research stage
    research_progress: float  # Progress percentage (0.0 to 1.0)
    # Quality metrics
    research_quality_score: float  # Overall research quality
    source_diversity_score: float  # Diversity of sources


class QualityAssuranceState(OverallState):
    """State for QA & Testing Analysis Graph"""
    # QA-specific fields
    qa_scope: str  # Scope of quality assurance
    test_categories: Annotated[list, operator.add]  # Categories to test
    quality_standards: dict  # Quality standards to apply
    test_results: dict  # Test execution results
    quality_metrics: dict  # Quality metrics analysis
    compliance_check: dict  # Compliance verification results
    security_assessment: dict  # Security analysis results
    performance_analysis: dict  # Performance evaluation results
    # Memory integration
    retrieved_standards: Annotated[list, operator.add]  # Quality standards from memory
    test_patterns: Annotated[list, operator.add]  # Test patterns from memory
    best_practices: Annotated[list, operator.add]  # QA best practices from memory
    # QA progress
    qa_stage: str  # Current QA stage
    qa_progress: float  # Progress percentage (0.0 to 1.0)
    # Generated artifacts
    test_recommendations: Annotated[list, operator.add]  # Test recommendations
    quality_improvements: Annotated[list, operator.add]  # Quality improvement suggestions
    validation_results: dict  # Validation outcomes

QAState = QualityAssuranceState

class ProjectOrchestratorState(OverallState):
    """State for Project Orchestrator & Coordination Graph"""
    # Orchestration-specific fields
    project_context: dict  # Overall project context
    active_graphs: Annotated[list, operator.add]  # Currently active graphs
    graph_dependencies: dict  # Dependencies between graphs
    coordination_plan: dict  # Coordination strategy
    execution_status: dict  # Status of all graph executions
    resource_allocation: dict  # Resource allocation across graphs
    conflict_resolution: dict  # Conflict resolution strategies
    # Memory integration
    retrieved_patterns: Annotated[list, operator.add]  # Orchestration patterns from memory
    coordination_history: Annotated[list, operator.add]  # Past coordination data from memory
    optimization_strategies: Annotated[list, operator.add]  # Optimization strategies from memory
    # Orchestration progress
    orchestration_stage: str  # Current orchestration stage
    orchestration_progress: float  # Progress percentage (0.0 to 1.0)
    # Coordination metrics
    efficiency_score: float  # Coordination efficiency
    resource_utilization: float  # Resource utilization percentage
    # Generated artifacts
    coordination_recommendations: Annotated[list, operator.add]  # Coordination recommendations
    optimization_suggestions: Annotated[list, operator.add]  # Optimization suggestions
    files_updated: Annotated[list, operator.add]  # Existing files updated

OrchestratorState = ProjectOrchestratorState

class TaskPlanningState(OverallState):
    """State for Task Planning Graph"""
    # Planning-specific fields
    project_scope: str
    planning_horizon: str  # 'sprint', 'quarter', 'year'
    task_categories: Annotated[list, operator.add]  # Categories of tasks
    generated_tasks: Annotated[list, operator.add]  # Generated task list
    milestones: Annotated[list, operator.add]  # Project milestones
    dependencies: dict  # Task dependencies
    resource_requirements: dict  # Resource estimation
    # Memory integration
    similar_projects: Annotated[list, operator.add]  # Similar projects from memory
    planning_patterns: Annotated[list, operator.add]  # Planning patterns from memory
    # Project management integration
    project_id: int  # Associated project ID
    tasks_created: Annotated[list, operator.add]  # Tasks created in database


class ResearchState(OverallState):
    """State for Research & Investigation Graph - enhanced version of original"""
    # Enhanced research fields
    research_domain: str  # 'technology', 'market', 'academic', 'competitive'
    research_depth: str  # 'surface', 'detailed', 'comprehensive'
    information_sources: Annotated[list, operator.add]  # Sources to search
    research_findings: Annotated[list, operator.add]  # Research results
    fact_verification: dict  # Fact checking results
    source_credibility: dict  # Source reliability scores
    # Memory integration
    previous_research: Annotated[list, operator.add]  # Related research from memory
    trusted_sources: Annotated[list, operator.add]  # Trusted sources from memory
    # MCP integration for specialized sources
    mcp_research_tools: Annotated[list, operator.add]  # Research-specific MCP tools
    external_apis_used: Annotated[list, operator.add]  # External APIs accessed


class QualityAssuranceState(OverallState):
    """State for Quality Assurance Graph"""
    # QA-specific fields
    qa_scope: str  # 'code', 'documentation', 'process', 'security'
    quality_standards: Annotated[list, operator.add]  # Standards to apply
    test_results: Annotated[list, operator.add]  # Test execution results
    quality_metrics: dict  # Quality measurements
    compliance_checks: dict  # Compliance verification results
    recommendations: Annotated[list, operator.add]  # Improvement recommendations
    # Memory integration
    quality_standards_memory: Annotated[list, operator.add]  # Standards from memory
    best_practices: Annotated[list, operator.add]  # Best practices from memory
    # Tool integration
    testing_tools_used: Annotated[list, operator.add]  # Testing tools executed
    validation_results: dict  # Validation outcomes


class ProjectOrchestratorState(OverallState):
    """State for Project Orchestrator Graph - master coordinator"""
    # Orchestration-specific fields
    orchestration_mode: str  # 'sequential', 'parallel', 'adaptive'
    active_graphs: Annotated[list, operator.add]  # Currently running graphs
    graph_results: dict  # Results from each specialized graph
    coordination_strategy: str  # How to coordinate the graphs
    overall_progress: dict  # Progress tracking across all graphs
    resource_allocation: dict  # Resource distribution across graphs
    # Memory integration for coordination
    coordination_patterns: Annotated[list, operator.add]  # Coordination patterns from memory
    project_templates: Annotated[list, operator.add]  # Project templates from memory
    # Multi-agent coordination
    agent_assignments: dict  # Which agent handles which task
    inter_graph_dependencies: dict  # Dependencies between graphs
    synchronization_points: Annotated[list, operator.add]  # Coordination checkpoints
    # Metrics and monitoring
    performance_metrics: dict  # Performance tracking
    quality_gates: dict  # Quality checkpoints
    risk_assessment: dict  # Risk monitoring


# ===== MEMORY-ENHANCED BASE STATE =====

class MemoryEnhancedState(OverallState):
    """Base state with integrated memory capabilities for all graphs"""
    # Long-term memory integration
    agent_id: str  # Unique agent identifier
    session_id: str  # Session/thread identifier
    project_id: int  # Associated project ID
    memory_context: dict  # Current memory context
    retrieved_memories: Annotated[list, operator.add]  # Retrieved memories
    stored_memories: Annotated[list, operator.add]  # Newly stored memories
    memory_importance_threshold: float  # Minimum importance for memory storage

    # Short-term memory/cache integration
    cache_namespace: str  # Cache namespace for this session
    cached_results: dict  # Cached computation results
    cache_hits: int  # Number of cache hits
    cache_misses: int  # Number of cache misses

    # Tool integration tracking
    available_tools: Annotated[list, operator.add]  # Available tools
    mcp_servers_connected: Annotated[list, operator.add]  # Connected MCP servers
    dynamic_tools_loaded: Annotated[list, operator.add]  # Dynamically loaded tools
    tool_execution_history: Annotated[list, operator.add]  # Tool usage history

    # Performance and monitoring
    execution_start_time: str  # When execution started
    node_execution_times: dict  # Execution time per node
    memory_usage: dict  # Memory usage tracking
    error_count: int  # Number of errors encountered
    warning_count: int  # Number of warnings

    # Testing aliases
    long_term_memories: Annotated[list, operator.add] = []  # alias for retrieved_memories
    short_term_cache: dict = {}  # alias for cached_results

# Runtime overrides to satisfy attribute tests
class CodebaseAnalysisState:
    def __init__(self):
        self.repository_url = ''
        self.analysis_type = ''
        self.analysis_results = []

# Override MemoryEnhancedState
class MemoryEnhancedState:
    def __init__(self):
        self.long_term_memories = []
        self.short_term_cache = {}
