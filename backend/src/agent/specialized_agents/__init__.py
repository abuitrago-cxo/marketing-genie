"""
Specialized Agents Module

This module contains the specialized agent implementations for the 3-agent system.
These agents work together to provide comprehensive research, analysis, and synthesis.
"""

from .base_agent import BaseSpecializedAgent
from .research_agent import ResearchAgent
from .analysis_agent import AnalysisAgent
from .synthesis_agent import SynthesisAgent

__all__ = [
    "BaseSpecializedAgent",
    "ResearchAgent", 
    "AnalysisAgent",
    "SynthesisAgent"
]
