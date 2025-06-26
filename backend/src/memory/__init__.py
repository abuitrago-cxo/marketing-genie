"""
Memory management module for AI agents.

This module provides both long-term and short-term memory capabilities
for AI agents in the system.
"""

from .long_term_memory_manager import (
    LongTermMemoryManager,
    Memory,
    get_memory_manager,
    close_memory_manager
)

from .short_term_memory_manager import (
    ShortTermMemoryManager,
    CacheEntry,
    get_short_memory_manager,
    close_short_memory_manager
)

from .integration_pattern import (
    IntegratedNodePattern,
    create_integrated_node
)

from .graphiti_memory_manager import (
    GraphitiMemoryManager,
    get_graphiti_memory_manager,
    close_graphiti_memory_manager
)

__all__ = [
    "LongTermMemoryManager",
    "Memory",
    "get_memory_manager",
    "close_memory_manager",
    "ShortTermMemoryManager",
    "CacheEntry",
    "get_short_memory_manager",
    "close_short_memory_manager",
    "IntegratedNodePattern",
    "create_integrated_node",
    "GraphitiMemoryManager",
    "get_graphiti_memory_manager",
    "close_graphiti_memory_manager"
]
