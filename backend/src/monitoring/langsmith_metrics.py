print("DEBUG: langsmith_metrics.py - Top of file")
"""
LangSmith Metrics Collection

Provides comprehensive metrics collection and monitoring for the specialized agent system.
Integrates with LangSmith for observability and performance tracking.
"""

print("DEBUG: langsmith_metrics.py - Importing standard libraries (os, asyncio, typing, datetime, dataclasses)...")
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
print("DEBUG: langsmith_metrics.py - Standard libraries imported.")

print("DEBUG: langsmith_metrics.py - Importing third-party libraries (langsmith, pydantic)...")
from langsmith import Client as LangSmithClient, traceable
from pydantic import BaseModel
print("DEBUG: langsmith_metrics.py - Third-party libraries imported.")


print("DEBUG: langsmith_metrics.py - Before @dataclass AgentPerformanceMetrics")
@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for individual agents"""
    agent_type: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    avg_execution_time: float
    avg_quality_score: float
    success_rate: float
    last_execution: str


@dataclass
class WorkflowMetrics:
    """Metrics for complete workflow execution"""
    workflow_id: str
    total_time: float
    agents_used: List[str]
    handoff_times: List[float]
    overall_quality: float
    user_satisfaction: Optional[float]
    completion_status: str


print("DEBUG: langsmith_metrics.py - Before class LangSmithMonitor definition")
class LangSmithMonitor:
    """
    Main monitoring class for LangSmith integration.
    
    Provides comprehensive monitoring capabilities for the specialized agent system.
    """
    
    def __init__(self, project_name: str = "ai-agent-3-specialization"):
        print(f"DEBUG: LangSmithMonitor.__init__ called for project: {project_name}")
        self.project_name = project_name
        self.client = None
        self.metrics_cache = {}
        
        # Initialize LangSmith client
        print("DEBUG: LangSmithMonitor.__init__ - Checking LANGSMITH_API_KEY...")
        if os.getenv("LANGSMITH_API_KEY"):
            try:
                print("DEBUG: LangSmithMonitor.__init__ - LANGSMITH_API_KEY found. Attempting to instantiate LangSmithClient()...")
                self.client = LangSmithClient()
                print(f"✅ LangSmith Monitor initialized for project: {project_name}")
            except Exception as e:
                print(f"⚠️ LangSmith Monitor initialization failed: {e}")
        else:
            print("DEBUG: LangSmithMonitor.__init__ - LANGSMITH_API_KEY not found. Client will not be initialized.")
    
    @traceable(name="log_agent_execution")
    async def log_agent_execution(
        self, 
        agent_type: str, 
        input_data: Dict[str, Any], 
        output_data: Dict[str, Any],
        execution_time: float,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log individual agent execution to LangSmith"""
        
        if not self.client:
            return
        
        try:
            run_data = {
                "name": f"{agent_type}_execution",
                "run_type": "chain",
                "inputs": input_data,
                "outputs": output_data if success else {"error": error_message},
                "tags": [agent_type, "specialized-agent", "success" if success else "error"],
                "extra": {
                    "execution_time": execution_time,
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat(),
                    "success": success
                }
            }
            
            if "quality_score" in output_data:
                run_data["extra"]["quality_score"] = output_data["quality_score"]
            
            await self.client.acreate_run(**run_data)
            
        except Exception as e:
            print(f"⚠️ Failed to log agent execution to LangSmith: {e}")
    
    @traceable(name="log_workflow_execution")
    async def log_workflow_execution(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any],
        agents_used: List[str],
        total_time: float,
        success: bool = True
    ):
        """Log complete workflow execution to LangSmith"""
        
        if not self.client:
            return
        
        try:
            await self.client.acreate_run(
                name="specialized_workflow_execution",
                run_type="chain",
                inputs={
                    "workflow_id": workflow_id,
                    "query": workflow_data.get("original_query", ""),
                    "agents_requested": agents_used
                },
                outputs={
                    "final_answer": workflow_data.get("final_answer", ""),
                    "quality_score": workflow_data.get("overall_quality_score", 0.0),
                    "citations_count": len(workflow_data.get("citations", [])),
                    "success": success
                },
                tags=["workflow", "3-agent-specialization", "complete"],
                extra={
                    "total_execution_time": total_time,
                    "agents_used": agents_used,
                    "research_iterations": workflow_data.get("execution_metrics", {}).get("research_iterations", 0),
                    "fallback_used": workflow_data.get("fallback_used", False),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            print(f"⚠️ Failed to log workflow execution to LangSmith: {e}")
    
    @traceable(name="log_agent_handoff")
    async def log_agent_handoff(
        self,
        from_agent: str,
        to_agent: str,
        handoff_data: Dict[str, Any],
        handoff_time: float,
        quality_score: Optional[float] = None
    ):
        """Log agent handoff to LangSmith"""
        
        if not self.client:
            return
        
        try:
            await self.client.acreate_run(
                name="agent_handoff",
                run_type="tool",
                inputs={
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "data_size": len(str(handoff_data))
                },
                outputs={
                    "handoff_time": handoff_time,
                    "quality_score": quality_score,
                    "success": True
                },
                tags=["handoff", from_agent, to_agent],
                extra={
                    "handoff_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            print(f"⚠️ Failed to log agent handoff to LangSmith: {e}")
    
    async def get_agent_performance_metrics(
        self, 
        agent_type: str, 
        time_range_hours: int = 24
    ) -> Optional[AgentPerformanceMetrics]:
        """Get performance metrics for a specific agent"""
        
        if not self.client:
            return None
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            # Query runs for the agent
            runs = await self.client.alist_runs(
                project_name=self.project_name,
                filter={
                    "tags": [agent_type],
                    "start_time": {"gte": start_time.isoformat()},
                    "end_time": {"lte": end_time.isoformat()}
                }
            )
            
            if not runs:
                return AgentPerformanceMetrics(
                    agent_type=agent_type,
                    total_executions=0,
                    successful_executions=0,
                    failed_executions=0,
                    avg_execution_time=0.0,
                    avg_quality_score=0.0,
                    success_rate=0.0,
                    last_execution="Never"
                )
            
            # Calculate metrics
            total_executions = len(runs)
            successful_runs = [r for r in runs if r.extra.get("success", True)]
            failed_runs = [r for r in runs if not r.extra.get("success", True)]
            
            successful_executions = len(successful_runs)
            failed_executions = len(failed_runs)
            success_rate = (successful_executions / total_executions) * 100 if total_executions > 0 else 0
            
            # Calculate average execution time
            execution_times = [r.extra.get("execution_time", 0) for r in successful_runs if r.extra.get("execution_time")]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            # Calculate average quality score
            quality_scores = [r.extra.get("quality_score", 0) for r in successful_runs if r.extra.get("quality_score")]
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Get last execution time
            last_execution = max([r.start_time for r in runs]).isoformat() if runs else "Never"
            
            return AgentPerformanceMetrics(
                agent_type=agent_type,
                total_executions=total_executions,
                successful_executions=successful_executions,
                failed_executions=failed_executions,
                avg_execution_time=avg_execution_time,
                avg_quality_score=avg_quality_score,
                success_rate=success_rate,
                last_execution=last_execution
            )
            
        except Exception as e:
            print(f"⚠️ Failed to get agent performance metrics: {e}")
            return None
    
    async def get_workflow_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive workflow metrics"""
        
        if not self.client:
            return {}
        
        try:
            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            # Query workflow runs
            workflow_runs = await self.client.alist_runs(
                project_name=self.project_name,
                filter={
                    "tags": ["workflow", "3-agent-specialization"],
                    "start_time": {"gte": start_time.isoformat()},
                    "end_time": {"lte": end_time.isoformat()}
                }
            )
            
            if not workflow_runs:
                return {
                    "total_workflows": 0,
                    "successful_workflows": 0,
                    "failed_workflows": 0,
                    "avg_execution_time": 0.0,
                    "avg_quality_score": 0.0,
                    "success_rate": 0.0
                }
            
            # Calculate workflow metrics
            total_workflows = len(workflow_runs)
            successful_workflows = len([r for r in workflow_runs if r.outputs.get("success", True)])
            failed_workflows = total_workflows - successful_workflows
            success_rate = (successful_workflows / total_workflows) * 100 if total_workflows > 0 else 0
            
            # Calculate averages
            execution_times = [r.extra.get("total_execution_time", 0) for r in workflow_runs if r.extra.get("total_execution_time")]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
            
            quality_scores = [r.outputs.get("quality_score", 0) for r in workflow_runs if r.outputs.get("quality_score")]
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                "total_workflows": total_workflows,
                "successful_workflows": successful_workflows,
                "failed_workflows": failed_workflows,
                "avg_execution_time": avg_execution_time,
                "avg_quality_score": avg_quality_score,
                "success_rate": success_rate,
                "time_range_hours": time_range_hours
            }
            
        except Exception as e:
            print(f"⚠️ Failed to get workflow metrics: {e}")
            return {}
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        
        health_data = {
            "langsmith_connected": self.client is not None,
            "timestamp": datetime.now().isoformat(),
            "status": "healthy"
        }
        
        if self.client:
            try:
                # Get recent metrics for all agents
                research_metrics = await self.get_agent_performance_metrics("research_agent", 1)
                analysis_metrics = await self.get_agent_performance_metrics("analysis_agent", 1)
                synthesis_metrics = await self.get_agent_performance_metrics("synthesis_agent", 1)
                workflow_metrics = await self.get_workflow_metrics(1)
                
                health_data.update({
                    "agents": {
                        "research_agent": {
                            "operational": research_metrics.success_rate > 80 if research_metrics else True,
                            "last_execution": research_metrics.last_execution if research_metrics else "Never"
                        },
                        "analysis_agent": {
                            "operational": analysis_metrics.success_rate > 80 if analysis_metrics else True,
                            "last_execution": analysis_metrics.last_execution if analysis_metrics else "Never"
                        },
                        "synthesis_agent": {
                            "operational": synthesis_metrics.success_rate > 80 if synthesis_metrics else True,
                            "last_execution": synthesis_metrics.last_execution if synthesis_metrics else "Never"
                        }
                    },
                    "workflow": {
                        "success_rate": workflow_metrics.get("success_rate", 100),
                        "avg_quality": workflow_metrics.get("avg_quality_score", 0),
                        "total_executions": workflow_metrics.get("total_workflows", 0)
                    }
                })
                
                # Determine overall status
                agent_operational = all(
                    agent_data["operational"] 
                    for agent_data in health_data["agents"].values()
                )
                workflow_healthy = workflow_metrics.get("success_rate", 100) > 70
                
                if agent_operational and workflow_healthy:
                    health_data["status"] = "healthy"
                elif workflow_metrics.get("success_rate", 100) > 50:
                    health_data["status"] = "degraded"
                else:
                    health_data["status"] = "unhealthy"
                
            except Exception as e:
                health_data.update({
                    "status": "error",
                    "error": str(e)
                })
        
        return health_data


class AgentMetricsCollector:
    """
    Simplified metrics collector for individual agent use.
    """
    
    def __init__(self, monitor: LangSmithMonitor):
        self.monitor = monitor
    
    async def log_agent_performance(self, agent_type: str, metrics: Dict[str, Any]):
        """Log agent performance metrics"""
        await self.monitor.log_agent_execution(
            agent_type=agent_type,
            input_data={"metrics_collection": True},
            output_data=metrics,
            execution_time=metrics.get("execution_time", 0),
            success=metrics.get("success", True),
            error_message=metrics.get("error_message")
        )
    
    async def log_handoff_quality(self, from_agent: str, to_agent: str, quality_score: float):
        """Log agent handoff quality"""
        await self.monitor.log_agent_handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            handoff_data={"quality_assessment": True},
            handoff_time=0.1,  # Minimal handoff time for quality logging
            quality_score=quality_score
        )


# Global monitor instance
langsmith_monitor = LangSmithMonitor()
metrics_collector = AgentMetricsCollector(langsmith_monitor)
