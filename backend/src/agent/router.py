"""
Agent Router System
Based on AgenticSeek patterns for intelligent agent selection and task distribution.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from langchain_core.messages import BaseMessage, HumanMessage

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Available agent types"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    PROJECT_MANAGEMENT = "project_management"
    DEVOPS = "devops"
    COMMUNICATION = "communication"
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"
    CODE_ENGINEER = "code_engineer"

class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class AgentCapability:
    """Defines what an agent can do"""
    agent_type: AgentType
    name: str
    description: str
    keywords: List[str]
    complexity_level: TaskComplexity
    tools: List[str]
    priority: int = 1  # Higher number = higher priority

@dataclass
class TaskClassification:
    """Result of task classification"""
    task_type: str
    complexity: TaskComplexity
    keywords_found: List[str]
    confidence: float
    suggested_agent: AgentType
    reasoning: str

class BaseTaskClassifier(ABC):
    """Abstract base class for task classifiers"""
    
    @abstractmethod
    def classify_task(self, message: str) -> TaskClassification:
        """Classify a task based on the input message"""
        pass

class KeywordBasedClassifier(BaseTaskClassifier):
    """Keyword-based task classifier"""
    
    def __init__(self):
        self.agent_patterns = {
            AgentType.RESEARCH: {
                "keywords": [
                    "research", "search", "find", "investigate", "analyze data",
                    "market analysis", "competitor", "trends", "information",
                    "study", "explore", "discover", "web search", "gather"
                ],
                "patterns": [
                    r"research\s+(?:about|on|into)",
                    r"find\s+(?:information|data|details)",
                    r"what\s+(?:is|are|do|does)",
                    r"search\s+for",
                    r"investigate\s+(?:the|this|how)"
                ]
            },
            AgentType.ANALYSIS: {
                "keywords": [
                    "analyze", "analysis", "evaluate", "assess", "review",
                    "performance", "metrics", "statistics", "data analysis",
                    "compare", "benchmark", "insights", "patterns", "trends"
                ],
                "patterns": [
                    r"analyze\s+(?:the|this|my)",
                    r"performance\s+(?:analysis|review)",
                    r"what\s+(?:are\s+the\s+)?(?:metrics|statistics)",
                    r"compare\s+(?:with|to|against)"
                ]
            },
            AgentType.PROJECT_MANAGEMENT: {
                "keywords": [
                    "project", "task", "sprint", "milestone", "deadline",
                    "schedule", "planning", "roadmap", "timeline", "progress",
                    "status", "tracking", "management", "organize", "coordinate"
                ],
                "patterns": [
                    r"project\s+(?:status|progress|plan)",
                    r"create\s+(?:task|milestone|sprint)",
                    r"schedule\s+(?:meeting|task|deadline)",
                    r"track\s+(?:progress|tasks|issues)"
                ]
            },
            AgentType.DEVOPS: {
                "keywords": [
                    "deploy", "deployment", "ci/cd", "pipeline", "build",
                    "docker", "kubernetes", "infrastructure", "server",
                    "monitoring", "logs", "performance", "scaling", "automation"
                ],
                "patterns": [
                    r"deploy\s+(?:to|on|the)",
                    r"build\s+(?:and\s+)?deploy",
                    r"ci/cd\s+pipeline",
                    r"docker\s+(?:build|run|deploy)",
                    r"infrastructure\s+(?:setup|management)"
                ]
            },
            AgentType.CODE_REVIEW: {
                "keywords": [
                    "code", "review", "quality", "security", "vulnerability",
                    "bug", "error", "refactor", "optimize", "test", "testing",
                    "lint", "format", "style", "best practices"
                ],
                "patterns": [
                    r"code\s+(?:review|quality|analysis)",
                    r"security\s+(?:scan|review|audit)",
                    r"find\s+(?:bugs|errors|issues)",
                    r"test\s+(?:coverage|quality)"
                ]
            },
            AgentType.COMMUNICATION: {
                "keywords": [
                    "email", "message", "notification", "report", "summary",
                    "update", "communicate", "inform", "notify", "document",
                    "meeting", "presentation", "stakeholder"
                ],
                "patterns": [
                    r"send\s+(?:email|message|notification)",
                    r"create\s+(?:report|summary|update)",
                    r"notify\s+(?:team|stakeholders)",
                    r"schedule\s+meeting"
                ]
            },
            AgentType.DOCUMENTATION: {
                "keywords": [
                    "documentation", "docs", "readme", "api", "guide",
                    "tutorial", "manual", "specification", "wiki", "help",
                    "instructions", "how-to", "examples"
                ],
                "patterns": [
                    r"create\s+(?:documentation|docs|readme)",
                    r"update\s+(?:documentation|docs)",
                    r"api\s+(?:documentation|docs)",
                    r"write\s+(?:guide|tutorial|manual)"
                ]
            },
            AgentType.CODE_ENGINEER: {
                "keywords": [
                    "code engineer", "improve code", "refactor", "optimize",
                    "codebase", "project structure", "apply patterns", "enhance code",
                    "technical debt", "best practices", "project_id"
                ],
                "patterns": [
                    r"improve\s+(?:code|codebase|project)",
                    r"refactor\s+(?:code|project)",
                    r"optimize\s+(?:codebase|performance)",
                    r"apply\s+(?:best\s+practices|design\s+patterns)",
                    r"code\s+engineer\s+task",
                    r"fix\s+bug\s+in\s+project",
                    r"add\s+feature\s+to\s+project"
                ]
            }
        }
    
    def classify_task(self, message: str) -> TaskClassification:
        """Classify task based on keywords and patterns"""
        message_lower = message.lower()
        
        best_match = None
        best_score = 0.0
        best_keywords = []
        
        for agent_type, config in self.agent_patterns.items():
            score = 0.0
            found_keywords = []
            
            # Check keywords
            for keyword in config["keywords"]:
                if keyword in message_lower:
                    score += 1.0
                    found_keywords.append(keyword)
            
            # Check patterns (weighted higher)
            for pattern in config["patterns"]:
                if re.search(pattern, message_lower):
                    score += 2.0
            
            # Normalize score
            total_possible = len(config["keywords"]) + len(config["patterns"]) * 2
            normalized_score = score / total_possible if total_possible > 0 else 0.0
            
            if normalized_score > best_score:
                best_score = normalized_score
                best_match = agent_type
                best_keywords = found_keywords
        
        # Determine complexity based on message length and keywords
        complexity = self._determine_complexity(message, best_keywords)
        
        # Generate reasoning
        reasoning = f"Matched {len(best_keywords)} keywords: {', '.join(best_keywords[:3])}"
        if best_score > 0.3:
            reasoning += f" with {best_score:.2f} confidence"
        
        return TaskClassification(
            task_type=best_match.value if best_match else "general",
            complexity=complexity,
            keywords_found=best_keywords,
            confidence=best_score,
            suggested_agent=best_match or AgentType.RESEARCH,
            reasoning=reasoning
        )
    
    def _determine_complexity(self, message: str, keywords: List[str]) -> TaskComplexity:
        """Determine task complexity based on various factors"""
        # Simple heuristics for complexity
        word_count = len(message.split())
        keyword_count = len(keywords)
        
        complexity_indicators = [
            "complex", "advanced", "detailed", "comprehensive",
            "multiple", "integrate", "coordinate", "enterprise"
        ]
        
        has_complexity_indicators = any(
            indicator in message.lower() 
            for indicator in complexity_indicators
        )
        
        if word_count > 50 or keyword_count > 5 or has_complexity_indicators:
            return TaskComplexity.COMPLEX
        elif word_count > 20 or keyword_count > 2:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE

class AgentRouter:
    """
    Main agent router for intelligent task distribution
    Inspired by AgenticSeek's agent routing patterns
    """
    
    def __init__(self):
        self.classifiers: List[BaseTaskClassifier] = []
        self.agent_capabilities: Dict[AgentType, AgentCapability] = {}
        self.agent_load: Dict[AgentType, int] = {}
        self._initialize_default_setup()
    
    def _initialize_default_setup(self):
        """Initialize default classifiers and agent capabilities"""
        # Add default classifier
        self.classifiers.append(KeywordBasedClassifier())
        
        # Define agent capabilities
        capabilities = [
            AgentCapability(
                agent_type=AgentType.RESEARCH,
                name="Research Agent",
                description="Specialized in web research, data gathering, and information analysis",
                keywords=["research", "search", "investigate", "analyze"],
                complexity_level=TaskComplexity.MODERATE,
                tools=["web_search", "data_analysis", "summarization"],
                priority=2
            ),
            AgentCapability(
                agent_type=AgentType.PROJECT_MANAGEMENT,
                name="Project Management Agent",
                description="Handles project planning, task management, and progress tracking",
                keywords=["project", "task", "planning", "schedule"],
                complexity_level=TaskComplexity.COMPLEX,
                tools=["task_management", "scheduling", "progress_tracking"],
                priority=3
            ),
            AgentCapability(
                agent_type=AgentType.DEVOPS,
                name="DevOps Agent",
                description="Manages deployments, infrastructure, and CI/CD pipelines",
                keywords=["deploy", "infrastructure", "pipeline", "monitoring"],
                complexity_level=TaskComplexity.EXPERT,
                tools=["deployment", "monitoring", "infrastructure_management"],
                priority=1
            ),
            AgentCapability(
                agent_type=AgentType.CODE_REVIEW,
                name="Code Review Agent",
                description="Performs code analysis, security scans, and quality assessments",
                keywords=["code", "review", "security", "quality"],
                complexity_level=TaskComplexity.MODERATE,
                tools=["code_analysis", "security_scan", "quality_check"],
                priority=2
            ),
            AgentCapability(
                agent_type=AgentType.CODE_ENGINEER,
                name="Code Engineer Agent",
                description="Performs codebase improvements, refactoring, and applies best practices.",
                keywords=["code engineer", "improve code", "refactor", "optimize codebase", "project structure", "apply patterns"],
                complexity_level=TaskComplexity.COMPLEX,
                tools=["file_system_access", "code_analysis", "code_generation", "project_management_api"], # Placeholder tools
                priority=3 # High priority for direct engineering tasks
            )
        ]
        
        for capability in capabilities:
            self.agent_capabilities[capability.agent_type] = capability
            self.agent_load[capability.agent_type] = 0
    
    def route_task(self, message: str, context: Optional[Dict[str, Any]] = None) -> Tuple[AgentType, TaskClassification]:
        """Route a task to the most appropriate agent"""
        # Classify the task
        classification = self._classify_task(message)
        
        # Select the best agent based on classification and current load
        selected_agent = self._select_agent(classification, context)
        
        logger.info(
            f"Routed task to {selected_agent.value} agent "
            f"(confidence: {classification.confidence:.2f})"
        )
        
        return selected_agent, classification
    
    def _classify_task(self, message: str) -> TaskClassification:
        """Classify task using available classifiers"""
        if not self.classifiers:
            # Fallback to research agent
            return TaskClassification(
                task_type="general",
                complexity=TaskComplexity.SIMPLE,
                keywords_found=[],
                confidence=0.5,
                suggested_agent=AgentType.RESEARCH,
                reasoning="No classifiers available, defaulting to research"
            )
        
        # Use the first classifier for now (can be enhanced to use multiple)
        return self.classifiers[0].classify_task(message)
    
    def _select_agent(self, classification: TaskClassification, context: Optional[Dict[str, Any]]) -> AgentType:
        """Select the best agent based on classification and current state"""
        suggested_agent = classification.suggested_agent
        
        # Check if suggested agent is available and not overloaded
        if (suggested_agent in self.agent_capabilities and 
            self.agent_load.get(suggested_agent, 0) < 5):  # Max 5 concurrent tasks
            return suggested_agent
        
        # Find alternative agent based on priority and load
        available_agents = [
            (agent_type, capability) 
            for agent_type, capability in self.agent_capabilities.items()
            if self.agent_load.get(agent_type, 0) < 5
        ]
        
        if not available_agents:
            # All agents are busy, return the suggested one anyway
            return suggested_agent
        
        # Sort by priority and current load
        available_agents.sort(
            key=lambda x: (x[1].priority, -self.agent_load.get(x[0], 0)),
            reverse=True
        )
        
        return available_agents[0][0]
    
    def update_agent_load(self, agent_type: AgentType, delta: int):
        """Update the current load for an agent"""
        current_load = self.agent_load.get(agent_type, 0)
        self.agent_load[agent_type] = max(0, current_load + delta)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        return {
            "agents": {
                agent_type.value: {
                    "name": capability.name,
                    "current_load": self.agent_load.get(agent_type, 0),
                    "max_load": 5,
                    "status": "busy" if self.agent_load.get(agent_type, 0) >= 5 else "available"
                }
                for agent_type, capability in self.agent_capabilities.items()
            },
            "total_active_tasks": sum(self.agent_load.values())
        }


    def dispatch_direct_task(self, agent_type: AgentType, task_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Dispatch a task directly to a specified agent type without classification."""
        if agent_type not in self.agent_capabilities:
            logger.error(f"Cannot dispatch task: AgentType '{agent_type.value}' not found.")
            return None

        import uuid
        task_id = str(uuid.uuid4())
        logger.info(
            f"Dispatching direct task {task_id} to agent {agent_type.value}. "
            f"Task Data: {task_data}, Context: {context}"
        )
        # TODO: integrate with actual agent execution framework
        self.update_agent_load(agent_type, 1)
        return task_id

# Global agent router instance
agent_router = AgentRouter()
