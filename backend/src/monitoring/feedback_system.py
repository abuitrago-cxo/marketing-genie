"""
Feedback system for monitoring agent performance and user satisfaction.
This module provides functionality for collecting and analyzing feedback.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json

class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"

class FeedbackEntry:
    """Represents a single feedback entry."""

    def __init__(
        self,
        feedback_type: FeedbackType,
        message: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = f"feedback_{datetime.now().timestamp()}"
        self.feedback_type = feedback_type
        self.message = message
        self.user_id = user_id
        self.agent_id = agent_id
        self.session_id = session_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.processed = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback entry to dictionary."""
        return {
            "id": self.id,
            "feedback_type": self.feedback_type.value,
            "message": self.message,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "processed": self.processed
        }

class FeedbackCollector:
    """Collects and manages feedback entries."""

    def __init__(self):
        self.feedback_entries: List[FeedbackEntry] = []
        self.feedback_stats: Dict[str, int] = {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "bug_reports": 0,
            "feature_requests": 0
        }

    def add_feedback(
        self,
        feedback_type: FeedbackType,
        message: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a new feedback entry."""
        entry = FeedbackEntry(
            feedback_type=feedback_type,
            message=message,
            user_id=user_id,
            agent_id=agent_id,
            session_id=session_id,
            metadata=metadata
        )

        self.feedback_entries.append(entry)
        self._update_stats(feedback_type)

        return entry.id

    def _update_stats(self, feedback_type: FeedbackType):
        """Update feedback statistics."""
        self.feedback_stats["total"] += 1

        if feedback_type == FeedbackType.POSITIVE:
            self.feedback_stats["positive"] += 1
        elif feedback_type == FeedbackType.NEGATIVE:
            self.feedback_stats["negative"] += 1
        elif feedback_type == FeedbackType.NEUTRAL:
            self.feedback_stats["neutral"] += 1
        elif feedback_type == FeedbackType.BUG_REPORT:
            self.feedback_stats["bug_reports"] += 1
        elif feedback_type == FeedbackType.FEATURE_REQUEST:
            self.feedback_stats["feature_requests"] += 1

    def get_feedback_by_agent(self, agent_id: str) -> List[FeedbackEntry]:
        """Get all feedback for a specific agent."""
        return [entry for entry in self.feedback_entries if entry.agent_id == agent_id]

    def get_feedback_by_user(self, user_id: str) -> List[FeedbackEntry]:
        """Get all feedback from a specific user."""
        return [entry for entry in self.feedback_entries if entry.user_id == user_id]

    def get_recent_feedback(self, hours: int = 24) -> List[FeedbackEntry]:
        """Get feedback from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [entry for entry in self.feedback_entries if entry.timestamp > cutoff_time]

    def get_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        total = self.feedback_stats["total"]
        if total == 0:
            return self.feedback_stats

        return {
            **self.feedback_stats,
            "satisfaction_rate": (self.feedback_stats["positive"] / total) * 100,
            "issue_rate": (self.feedback_stats["negative"] + self.feedback_stats["bug_reports"]) / total * 100
        }

    def export_feedback(self, format: str = "json") -> str:
        """Export feedback data."""
        if format == "json":
            return json.dumps([entry.to_dict() for entry in self.feedback_entries], indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

class FeedbackAnalyzer:
    """Analyzes feedback patterns and trends."""

    def __init__(self, collector: FeedbackCollector):
        self.collector = collector

    def analyze_sentiment_trends(self) -> Dict[str, Any]:
        """Analyze sentiment trends over time."""
        # Simple implementation - in production this would use ML models
        stats = self.collector.get_stats()
        total = stats["total"]

        if total == 0:
            return {"trend": "no_data", "confidence": 0}

        positive_ratio = stats["positive"] / total
        negative_ratio = (stats["negative"] + stats["bug_reports"]) / total

        if positive_ratio > 0.7:
            return {"trend": "positive", "confidence": positive_ratio}
        elif negative_ratio > 0.3:
            return {"trend": "negative", "confidence": negative_ratio}
        else:
            return {"trend": "neutral", "confidence": 0.5}

    def get_top_issues(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most common issues reported."""
        # Simple keyword-based analysis
        issue_keywords = {}

        for entry in self.collector.feedback_entries:
            if entry.feedback_type in [FeedbackType.NEGATIVE, FeedbackType.BUG_REPORT]:
                words = entry.message.lower().split()
                for word in words:
                    if len(word) > 3:  # Filter short words
                        issue_keywords[word] = issue_keywords.get(word, 0) + 1

        # Sort by frequency and return top issues
        sorted_issues = sorted(issue_keywords.items(), key=lambda x: x[1], reverse=True)
        return [{"keyword": word, "frequency": freq} for word, freq in sorted_issues[:limit]]

class AgentFeedbackSystem:
    """Main feedback system for agent performance monitoring."""

    def __init__(self):
        self.collector = FeedbackCollector()
        self.analyzer = FeedbackAnalyzer(self.collector)

    def submit_feedback(self, feedback_type: str, message: str, **kwargs) -> str:
        """Submit feedback to the system."""
        fb_type = FeedbackType(feedback_type)
        return self.collector.add_feedback(fb_type, message, **kwargs)

    def get_agent_feedback(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get feedback for a specific agent."""
        feedback_entries = self.collector.get_feedback_by_agent(agent_id)
        return [entry.to_dict() for entry in feedback_entries]

    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system feedback statistics."""
        return self.collector.get_stats()

    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze feedback trends."""
        return self.analyzer.analyze_sentiment_trends()

# Global feedback collector instance
feedback_collector = FeedbackCollector()
feedback_analyzer = FeedbackAnalyzer(feedback_collector)
agent_feedback_system = AgentFeedbackSystem()

# Convenience functions for easy import
def add_feedback(feedback_type: str, message: str, **kwargs) -> str:
    """Add feedback with string type."""
    fb_type = FeedbackType(feedback_type)
    return feedback_collector.add_feedback(fb_type, message, **kwargs)

def get_feedback_stats() -> Dict[str, Any]:
    """Get current feedback statistics."""
    return feedback_collector.get_stats()

def analyze_feedback() -> Dict[str, Any]:
    """Get feedback analysis."""
    return {
        "stats": feedback_collector.get_stats(),
        "sentiment_trends": feedback_analyzer.analyze_sentiment_trends(),
        "top_issues": feedback_analyzer.get_top_issues()
    }
