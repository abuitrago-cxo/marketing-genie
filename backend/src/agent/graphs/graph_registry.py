print("DEBUG: graph_registry.py - Top of file")
"""
Graph Registry for Specialized LangGraph Implementations

This module provides a centralized registry for all specialized graphs,
following the original Google Gemini repository pattern with 6 specialized
agent workflows.

Each graph follows the established 5-node pattern:
1. Route Task → Determine approach and strategy
2. Generate Queries → Create comprehensive queries  
3. Execute Research/Analysis → Conduct specialized work
4. Reflection & Gap Analysis → Evaluate and identify gaps
5. Finalize Results → Generate final recommendations

All graphs integrate:
- Tool Registry for dynamic tool access
- Memory systems for pattern storage and retrieval
- MCP service discovery for specialized tools
- LangSmith tracing for monitoring
"""

print("DEBUG: graph_registry.py - Importing standard libraries (logging, typing)...")
import logging
from typing import Dict, Type, Optional, List
print("DEBUG: graph_registry.py - Standard libraries imported.")
print("DEBUG: graph_registry.py - Importing third-party libraries (langgraph.graph)...")
from langgraph.graph import StateGraph
print("DEBUG: graph_registry.py - Third-party libraries imported.")

# Import all specialized graph classes
print("DEBUG: graph_registry.py - Importing src.agent.graphs.codebase_analysis_graph...")
from src.agent.graphs.codebase_analysis_graph import CodebaseAnalysisGraph
print("DEBUG: graph_registry.py - Importing src.agent.graphs.documentation_analysis_graph...")
from src.agent.graphs.documentation_analysis_graph import DocumentationAnalysisGraph
print("DEBUG: graph_registry.py - Importing src.agent.graphs.task_planning_graph...")
from src.agent.graphs.task_planning_graph import TaskPlanningGraph
print("DEBUG: graph_registry.py - Importing src.agent.graphs.research_analysis_graph...")
from src.agent.graphs.research_analysis_graph import ResearchAnalysisGraph
print("DEBUG: graph_registry.py - Importing src.agent.graphs.qa_testing_graph...")
from src.agent.graphs.qa_testing_graph import QATestingGraph
print("DEBUG: graph_registry.py - Importing src.agent.graphs.project_orchestrator_graph...")
from src.agent.graphs.project_orchestrator_graph import ProjectOrchestratorGraph
print("DEBUG: graph_registry.py - All specialized graph classes imported.")

# Import state classes
print("DEBUG: graph_registry.py - Importing src.agent.state (state classes)...")
from src.agent.state import (
    CodebaseAnalysisState,
    DocumentationAnalysisState, 
    TaskPlanningState,
    ResearchAnalysisState,
    QualityAssuranceState,
    ProjectOrchestratorState
)
print("DEBUG: graph_registry.py - State classes imported.")

logger = logging.getLogger(__name__)


print("DEBUG: graph_registry.py - Before class GraphRegistry definition")
class GraphRegistry:
    """
    Centralized registry for all specialized LangGraph implementations.
    
    Provides unified access to all 6 specialized graphs with proper
    initialization, configuration, and lifecycle management.
    """
    
    def __init__(self):
        print("DEBUG: GraphRegistry.__init__ called")
        self._graph_classes: Dict[str, Type] = {}
        self._graph_instances: Dict[str, StateGraph] = {}
        self._graph_metadata: Dict[str, dict] = {}
        self._initialized = False
        
    def initialize(self):
        """Initialize the graph registry with all specialized graphs"""
        print("DEBUG: GraphRegistry.initialize called")
        if self._initialized:
            return
            
        logger.info("🔧 Initializing Graph Registry...")
        
        # Register all specialized graph classes
        self._register_graph_classes()
        
        # Initialize metadata for each graph
        self._initialize_metadata()
        
        self._initialized = True
        logger.info("✅ Graph Registry initialized successfully")
        logger.info(f"📊 Registered {len(self._graph_classes)} specialized graphs")
        print("DEBUG: GraphRegistry.initialize finished")
        
    def _register_graph_classes(self):
        """Register all specialized graph classes"""
        
        # Core analysis graphs
        self._graph_classes["codebase_analysis"] = CodebaseAnalysisGraph
        self._graph_classes["documentation_analysis"] = DocumentationAnalysisGraph
        
        # Planning and coordination graphs  
        self._graph_classes["task_planning"] = TaskPlanningGraph
        self._graph_classes["project_orchestrator"] = ProjectOrchestratorGraph
        
        # Research and quality graphs
        self._graph_classes["research_analysis"] = ResearchAnalysisGraph
        self._graph_classes["qa_testing"] = QATestingGraph
        print("DEBUG: GraphRegistry._register_graph_classes finished")
        
        logger.info(f"Registered {len(self._graph_classes)} graph classes")
        
    def _initialize_metadata(self):
        """Initialize metadata for each graph"""
        
        self._graph_metadata = {
            "codebase_analysis": {
                "name": "Codebase Analysis Specialist",
                "description": "Analyzes code architecture, quality, and patterns",
                "state_class": CodebaseAnalysisState,
                "category": "analysis",
                "priority": "high",
                "dependencies": [],
                "estimated_duration": "1-2 hours",
                "required_tools": ["file_operations", "code_analysis"],
                "memory_types": ["code_pattern", "architecture_insight"],
                "workflow_pattern": "route_analysis → generate_queries → execute_analysis → reflection_gaps → finalize_analysis"
            },
            "documentation_analysis": {
                "name": "Documentation Analysis Specialist", 
                "description": "Evaluates documentation quality and completeness",
                "state_class": DocumentationAnalysisState,
                "category": "analysis",
                "priority": "medium",
                "dependencies": ["codebase_analysis"],
                "estimated_duration": "30-60 minutes",
                "required_tools": ["file_operations", "web_operations"],
                "memory_types": ["doc_pattern", "quality_standard"],
                "workflow_pattern": "discover_docs → analyze_structure → evaluate_quality → check_completeness → generate_recommendations"
            },
            "task_planning": {
                "name": "Task Planning Specialist",
                "description": "Creates comprehensive project plans and task breakdowns",
                "state_class": TaskPlanningState,
                "category": "planning",
                "priority": "high", 
                "dependencies": [],
                "estimated_duration": "1-3 hours",
                "required_tools": ["project_management"],
                "memory_types": ["planning_pattern", "methodology_template"],
                "workflow_pattern": "route_planning → analyze_requirements → generate_task_breakdown → estimate_resources → finalize_planning"
            },
            "research_analysis": {
                "name": "Research & Knowledge Specialist",
                "description": "Conducts comprehensive research and knowledge synthesis",
                "state_class": ResearchAnalysisState,
                "category": "research",
                "priority": "medium",
                "dependencies": [],
                "estimated_duration": "2-4 hours", 
                "required_tools": ["web_operations"],
                "memory_types": ["research_pattern", "source_credibility"],
                "workflow_pattern": "route_research → generate_research_queries → execute_research → evaluate_sources → synthesize_knowledge"
            },
            "qa_testing": {
                "name": "QA & Testing Specialist",
                "description": "Performs quality assurance and testing analysis",
                "state_class": QualityAssuranceState,
                "category": "quality",
                "priority": "high",
                "dependencies": ["codebase_analysis", "documentation_analysis"],
                "estimated_duration": "2-3 hours",
                "required_tools": ["file_operations", "testing_tools"],
                "memory_types": ["qa_pattern", "test_standard"],
                "workflow_pattern": "route_qa_analysis → analyze_code_quality → generate_test_strategy → evaluate_security → finalize_qa_recommendations"
            },
            "project_orchestrator": {
                "name": "Project Orchestrator & Coordinator",
                "description": "Coordinates and optimizes multi-graph execution",
                "state_class": ProjectOrchestratorState,
                "category": "coordination",
                "priority": "critical",
                "dependencies": ["task_planning"],
                "estimated_duration": "30-60 minutes",
                "required_tools": ["project_management"],
                "memory_types": ["orchestration_pattern", "coordination_strategy"],
                "workflow_pattern": "route_orchestration → analyze_dependencies → allocate_resources → resolve_conflicts → optimize_coordination"
            }
        }
        print("DEBUG: GraphRegistry._initialize_metadata finished")
        
    def get_graph(self, graph_id: str) -> Optional[StateGraph]:
        """Get a compiled graph instance by ID"""
        if not self._initialized:
            self.initialize()
            
        if graph_id not in self._graph_classes:
            logger.error(f"Graph '{graph_id}' not found in registry")
            return None
            
        # Create and compile graph if not already cached
        if graph_id not in self._graph_instances:
            try:
                graph_class = self._graph_classes[graph_id]
                graph_instance = graph_class()
                compiled_graph = graph_instance.create_graph()
                
                self._graph_instances[graph_id] = compiled_graph
                logger.info(f"✅ Compiled and cached graph: {graph_id}")
                
            except Exception as e:
                logger.error(f"Failed to compile graph '{graph_id}': {e}")
                return None
                
        return self._graph_instances[graph_id]
        
    def get_all_graphs(self) -> Dict[str, StateGraph]:
        """Get all compiled graph instances"""
        if not self._initialized:
            self.initialize()
            
        graphs = {}
        for graph_id in self._graph_classes.keys():
            graph = self.get_graph(graph_id)
            if graph:
                graphs[graph_id] = graph
                
        return graphs
        
    def get_graph_metadata(self, graph_id: str) -> Optional[dict]:
        print(f"DEBUG: GraphRegistry.get_graph_metadata called for {graph_id}")
        """Get metadata for a specific graph"""
        if not self._initialized:
            self.initialize()
            
        return self._graph_metadata.get(graph_id)
        
    def get_all_metadata(self) -> Dict[str, dict]:
        """Get metadata for all graphs"""
        if not self._initialized:
            self.initialize()
            
        return self._graph_metadata.copy()
        
    def list_graphs(self) -> List[str]:
        """List all available graph IDs"""
        if not self._initialized:
            self.initialize()
            
        return list(self._graph_classes.keys())
        
    def get_graphs_by_category(self, category: str) -> List[str]:
        """Get graph IDs filtered by category"""
        if not self._initialized:
            self.initialize()
            
        return [
            graph_id for graph_id, metadata in self._graph_metadata.items()
            if metadata.get("category") == category
        ]
        
    def get_execution_order(self) -> List[str]:
        """Get recommended execution order based on dependencies"""
        if not self._initialized:
            self.initialize()
            
        # Simple topological sort based on dependencies
        ordered = []
        remaining = set(self._graph_classes.keys())
        
        while remaining:
            # Find graphs with no unresolved dependencies
            ready = []
            for graph_id in remaining:
                deps = self._graph_metadata[graph_id].get("dependencies", [])
                if all(dep in ordered for dep in deps):
                    ready.append(graph_id)
                    
            if not ready:
                # Handle circular dependencies by adding remaining graphs
                ready = list(remaining)
                
            # Sort by priority within ready graphs
            ready.sort(key=lambda x: {
                "critical": 0, "high": 1, "medium": 2, "low": 3
            }.get(self._graph_metadata[x].get("priority", "medium"), 2))
            
            ordered.extend(ready)
            remaining -= set(ready)
            
        return ordered
        
    def validate_graph(self, graph_id: str) -> bool:
        """Validate that a graph can be compiled successfully"""
        try:
            graph = self.get_graph(graph_id)
            return graph is not None
        except Exception as e:
            logger.error(f"Graph validation failed for '{graph_id}': {e}")
            return False
            
    def get_health_status(self) -> dict:
        """Get health status of all graphs"""
        if not self._initialized:
            self.initialize()
            
        status = {
            "total_graphs": len(self._graph_classes),
            "compiled_graphs": len(self._graph_instances),
            "healthy_graphs": 0,
            "failed_graphs": [],
            "graph_status": {}
        }
        
        for graph_id in self._graph_classes.keys():
            is_healthy = self.validate_graph(graph_id)
            status["graph_status"][graph_id] = "healthy" if is_healthy else "failed"
            
            if is_healthy:
                status["healthy_graphs"] += 1
            else:
                status["failed_graphs"].append(graph_id)
                
        return status


# Global instance of the registry
print("DEBUG: graph_registry.py - Before creating global graph_registry_instance")
graph_registry_instance = GraphRegistry()
print("DEBUG: graph_registry.py - After creating global graph_registry_instance")

def get_graph_registry():
    print("DEBUG: graph_registry.py - get_graph_registry() called")
    if not graph_registry_instance._initialized:
        graph_registry_instance.initialize()
    return graph_registry_instance

def get_specialized_graph(graph_id: str) -> Optional[StateGraph]:
    print(f"DEBUG: graph_registry.py - get_specialized_graph() called for {graph_id}")
    """Convenience function to get a specialized graph"""
    registry = get_graph_registry()
    return registry.get_graph(graph_id)

def list_available_graphs():
    print("DEBUG: GraphRegistry.list_available_graphs called")
    print("DEBUG: graph_registry.py - list_available_graphs() function called")
    """Convenience function to list all available graphs"""
    registry = get_graph_registry()
    return registry.list_graphs()

print("DEBUG: graph_registry.py - End of file")

def get_graph_execution_order() -> List[str]:
    """Convenience function to get recommended execution order"""
    registry = get_graph_registry()
    return registry.get_execution_order()
