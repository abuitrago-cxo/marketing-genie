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
    "create_integrated_node"
]
