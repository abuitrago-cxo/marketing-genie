"""
Performance tracking system for monitoring agent execution metrics.
This module provides functionality for tracking and analyzing agent performance.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import time
import statistics

@dataclass
class PerformanceMetric:
    """Represents a single performance metric."""
    agent_id: str
    metric_type: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]

class PerformanceTracker:
    """Tracks and analyzes agent performance metrics."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def start_session(self, session_id: str, agent_id: str, task_type: str) -> None:
        """Start tracking a new performance session."""
        self.active_sessions[session_id] = {
            "agent_id": agent_id,
            "task_type": task_type,
            "start_time": time.time(),
            "start_datetime": datetime.now(),
            "metrics": {}
        }
    
    def end_session(self, session_id: str, success: bool = True) -> Dict[str, Any]:
        """End a performance session and calculate metrics."""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        session = self.active_sessions[session_id]
        end_time = time.time()
        duration = end_time - session["start_time"]
        
        # Create performance metrics
        metrics = {
            "duration": duration,
            "success": success,
            "agent_id": session["agent_id"],
            "task_type": session["task_type"],
            "timestamp": datetime.now()
        }
        
        # Store the metric
        self.add_metric(
            agent_id=session["agent_id"],
            metric_type="execution_time",
            value=duration,
            metadata={
                "task_type": session["task_type"],
                "success": success,
                "session_id": session_id
            }
        )
        
        # Clean up session
        del self.active_sessions[session_id]
        
        return metrics
    
    def add_metric(
        self,
        agent_id: str,
        metric_type: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a performance metric."""
        metric = PerformanceMetric(
            agent_id=agent_id,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.metrics.append(metric)
    
    def get_agent_metrics(
        self,
        agent_id: str,
        metric_type: Optional[str] = None,
        hours: int = 24
    ) -> List[PerformanceMetric]:
        """Get metrics for a specific agent."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_metrics = [
            metric for metric in self.metrics
            if metric.agent_id == agent_id
            and metric.timestamp > cutoff_time
            and (metric_type is None or metric.metric_type == metric_type)
        ]
        
        return filtered_metrics
    
    def get_agent_stats(self, agent_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get statistical summary for an agent."""
        metrics = self.get_agent_metrics(agent_id, hours=hours)
        
        if not metrics:
            return {
                "agent_id": agent_id,
                "total_executions": 0,
                "avg_execution_time": 0.0,
                "success_rate": 0.0,
                "last_execution": None
            }
        
        # Calculate execution times
        execution_times = [
            m.value for m in metrics 
            if m.metric_type == "execution_time"
        ]
        
        # Calculate success rate
        success_metrics = [
            m for m in metrics 
            if m.metric_type == "execution_time" and "success" in m.metadata
        ]
        
        successful_executions = sum(
            1 for m in success_metrics 
            if m.metadata.get("success", False)
        )
        
        success_rate = (
            (successful_executions / len(success_metrics)) * 100
            if success_metrics else 0.0
        )
        
        return {
            "agent_id": agent_id,
            "total_executions": len(execution_times),
            "avg_execution_time": statistics.mean(execution_times) if execution_times else 0.0,
            "min_execution_time": min(execution_times) if execution_times else 0.0,
            "max_execution_time": max(execution_times) if execution_times else 0.0,
            "success_rate": success_rate,
            "last_execution": max(m.timestamp for m in metrics) if metrics else None,
            "total_metrics": len(metrics)
        }
    
    def get_system_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get system-wide performance statistics."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            metric for metric in self.metrics
            if metric.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "total_executions": 0,
                "active_agents": 0,
                "avg_system_performance": 0.0,
                "system_success_rate": 0.0
            }
        
        # Get unique agents
        active_agents = set(metric.agent_id for metric in recent_metrics)
        
        # Calculate system-wide metrics
        execution_metrics = [
            m for m in recent_metrics 
            if m.metric_type == "execution_time"
        ]
        
        successful_executions = sum(
            1 for m in execution_metrics 
            if m.metadata.get("success", False)
        )
        
        system_success_rate = (
            (successful_executions / len(execution_metrics)) * 100
            if execution_metrics else 0.0
        )
        
        avg_execution_time = statistics.mean([
            m.value for m in execution_metrics
        ]) if execution_metrics else 0.0
        
        return {
            "total_executions": len(execution_metrics),
            "active_agents": len(active_agents),
            "avg_system_performance": avg_execution_time,
            "system_success_rate": system_success_rate,
            "metrics_collected": len(recent_metrics),
            "time_range_hours": hours
        }
    
    def get_trending_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get trending performance metrics."""
        # Simple trending analysis
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            metric for metric in self.metrics
            if metric.timestamp > cutoff_time and metric.metric_type == "execution_time"
        ]
        
        if len(recent_metrics) < 2:
            return {"trend": "insufficient_data"}
        
        # Split into two halves to compare
        mid_point = len(recent_metrics) // 2
        first_half = recent_metrics[:mid_point]
        second_half = recent_metrics[mid_point:]
        
        first_avg = statistics.mean([m.value for m in first_half])
        second_avg = statistics.mean([m.value for m in second_half])
        
        trend_direction = "improving" if second_avg < first_avg else "declining"
        trend_magnitude = abs(second_avg - first_avg) / first_avg * 100
        
        return {
            "trend": trend_direction,
            "magnitude_percent": trend_magnitude,
            "first_period_avg": first_avg,
            "second_period_avg": second_avg,
            "sample_size": len(recent_metrics)
        }

# Global performance tracker instance
performance_tracker = PerformanceTracker()

# Convenience functions
def start_tracking(session_id: str, agent_id: str, task_type: str) -> None:
    """Start tracking performance for a session."""
    performance_tracker.start_session(session_id, agent_id, task_type)

def end_tracking(session_id: str, success: bool = True) -> Dict[str, Any]:
    """End tracking and get performance metrics."""
    return performance_tracker.end_session(session_id, success)

def track_metric(agent_id: str, metric_type: str, value: float, **metadata) -> None:
    """Track a custom metric."""
    performance_tracker.add_metric(agent_id, metric_type, value, metadata)

def get_agent_performance(agent_id: str, hours: int = 24) -> Dict[str, Any]:
    """Get performance statistics for an agent."""
    return performance_tracker.get_agent_stats(agent_id, hours)

def get_system_performance(hours: int = 24) -> Dict[str, Any]:
    """Get system-wide performance statistics."""
    return performance_tracker.get_system_stats(hours)
