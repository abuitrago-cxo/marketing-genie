"""
Configuration module for agent system.
This module provides configuration classes and utilities for the AI agent system.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import os

class AgentType(Enum):
    """Types of agents in the system."""
    CODEBASE_ANALYSIS = "codebase-analysis"
    DOCUMENTATION_ANALYSIS = "documentation-analysis"
    TASK_PLANNING = "task-planning"
    RESEARCH_ANALYSIS = "research-analysis"
    QA_TESTING = "qa-testing"
    PROJECT_ORCHESTRATOR = "project-orchestrator"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    COORDINATOR = "coordinator"

class WorkflowType(Enum):
    """Types of workflows supported."""
    SPECIALIZED = "specialized"
    MULTI_AGENT = "multi_agent"
    TRUE_SPECIALIZED = "true_specialized"
    BASIC = "basic"

@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[str]
    max_iterations: int = 3
    timeout_seconds: int = 300
    enable_tracing: bool = True
    model_name: str = "gemini-1.5-pro"
    temperature: float = 0.1
    max_tokens: int = 4000
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""
    workflow_id: str
    workflow_type: WorkflowType
    name: str
    description: str
    agents: List[str]  # List of agent IDs
    max_execution_time: int = 600
    enable_parallel_execution: bool = False
    retry_attempts: int = 2
    quality_threshold: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemConfig:
    """System-wide configuration."""
    # Core API Keys
    gemini_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None

    # Basic Configuration
    api_host: str = "localhost"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Gemini Configuration
    gemini_model: str = "gemini-1.5-pro"

    # LangSmith Configuration
    langsmith_project: str = "ai-agent-assistant"

class ConfigManager:
    """Manages system configuration."""

    def __init__(self):
        self.system_config = SystemConfig()
        self.agent_configs: Dict[str, AgentConfig] = {}
        self.workflow_configs: Dict[str, WorkflowConfig] = {}
        self._load_from_environment()
        self._initialize_default_configs()

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Core API Keys
        self.system_config.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.system_config.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

    def _initialize_default_configs(self):
        """Initialize default agent and workflow configurations."""
        # Default agent configurations
        default_agents = [
            {
                "agent_id": "codebase-analysis",
                "agent_type": AgentType.CODEBASE_ANALYSIS,
                "name": "Code Analysis Specialist",
                "description": "Analyzes codebase structure, dependencies, and quality",
                "capabilities": ["Code Analysis", "Dependency Mapping", "Quality Assessment", "Architecture Review"]
            },
            {
                "agent_id": "documentation-analysis",
                "agent_type": AgentType.DOCUMENTATION_ANALYSIS,
                "name": "Documentation Specialist",
                "description": "Analyzes and improves project documentation",
                "capabilities": ["Documentation Review", "Content Analysis", "Structure Optimization", "Clarity Assessment"]
            },
            {
                "agent_id": "task-planning",
                "agent_type": AgentType.TASK_PLANNING,
                "name": "Task Planning Specialist",
                "description": "Creates and manages project task plans",
                "capabilities": ["Task Breakdown", "Timeline Planning", "Resource Allocation", "Priority Management"]
            },
            {
                "agent_id": "research-analysis",
                "agent_type": AgentType.RESEARCH_ANALYSIS,
                "name": "Research Specialist",
                "description": "Conducts research and knowledge analysis",
                "capabilities": ["Web Research", "Knowledge Synthesis", "Trend Analysis", "Information Validation"]
            },
            {
                "agent_id": "qa-testing",
                "agent_type": AgentType.QA_TESTING,
                "name": "QA Testing Specialist",
                "description": "Manages quality assurance and testing processes",
                "capabilities": ["Test Planning", "Quality Assessment", "Bug Detection", "Performance Testing"]
            },
            {
                "agent_id": "project-orchestrator",
                "agent_type": AgentType.PROJECT_ORCHESTRATOR,
                "name": "Project Orchestrator",
                "description": "Coordinates and manages overall project workflow",
                "capabilities": ["Project Coordination", "Workflow Management", "Team Communication", "Progress Tracking"]
            }
        ]

        for agent_data in default_agents:
            config = AgentConfig(**agent_data)
            self.agent_configs[config.agent_id] = config

        # Default workflow configurations
        default_workflows = [
            {
                "workflow_id": "codebase-analysis-workflow",
                "workflow_type": WorkflowType.SPECIALIZED,
                "name": "Codebase Analysis Workflow",
                "description": "Comprehensive codebase analysis and review",
                "agents": ["codebase-analysis"]
            },
            {
                "workflow_id": "documentation-workflow",
                "workflow_type": WorkflowType.SPECIALIZED,
                "name": "Documentation Analysis Workflow",
                "description": "Documentation review and improvement",
                "agents": ["documentation-analysis"]
            },
            {
                "workflow_id": "project-planning-workflow",
                "workflow_type": WorkflowType.MULTI_AGENT,
                "name": "Project Planning Workflow",
                "description": "Comprehensive project planning and coordination",
                "agents": ["task-planning", "project-orchestrator"]
            },
            {
                "workflow_id": "research-workflow",
                "workflow_type": WorkflowType.SPECIALIZED,
                "name": "Research Analysis Workflow",
                "description": "Research and knowledge analysis",
                "agents": ["research-analysis"]
            },
            {
                "workflow_id": "qa-workflow",
                "workflow_type": WorkflowType.SPECIALIZED,
                "name": "QA Testing Workflow",
                "description": "Quality assurance and testing",
                "agents": ["qa-testing"]
            }
        ]

        for workflow_data in default_workflows:
            config = WorkflowConfig(**workflow_data)
            self.workflow_configs[config.workflow_id] = config

    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent."""
        return self.agent_configs.get(agent_id)

    def get_workflow_config(self, workflow_id: str) -> Optional[WorkflowConfig]:
        """Get configuration for a specific workflow."""
        return self.workflow_configs.get(workflow_id)

    def get_all_agent_configs(self) -> Dict[str, AgentConfig]:
        """Get all agent configurations."""
        return self.agent_configs.copy()

    def get_all_workflow_configs(self) -> Dict[str, WorkflowConfig]:
        """Get all workflow configurations."""
        return self.workflow_configs.copy()

    def add_agent_config(self, config: AgentConfig) -> None:
        """Add a new agent configuration."""
        self.agent_configs[config.agent_id] = config

    def add_workflow_config(self, config: WorkflowConfig) -> None:
        """Add a new workflow configuration."""
        self.workflow_configs[config.workflow_id] = config

    def update_system_config(self, **kwargs) -> None:
        """Update system configuration."""
        for key, value in kwargs.items():
            if hasattr(self.system_config, key):
                setattr(self.system_config, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "system": self.system_config.__dict__,
            "agents": {k: v.__dict__ for k, v in self.agent_configs.items()},
            "workflows": {k: v.__dict__ for k, v in self.workflow_configs.items()}
        }

# Global configuration manager
config_manager = ConfigManager()

# Convenience functions
def get_system_config() -> SystemConfig:
    """Get system configuration."""
    return config_manager.system_config

def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """Get agent configuration."""
    return config_manager.get_agent_config(agent_id)

def get_workflow_config(workflow_id: str) -> Optional[WorkflowConfig]:
    """Get workflow configuration."""
    return config_manager.get_workflow_config(workflow_id)

def get_all_agents() -> Dict[str, AgentConfig]:
    """Get all agent configurations."""
    return config_manager.get_all_agent_configs()

def get_all_workflows() -> Dict[str, WorkflowConfig]:
    """Get all workflow configurations."""
    return config_manager.get_all_workflow_configs()
