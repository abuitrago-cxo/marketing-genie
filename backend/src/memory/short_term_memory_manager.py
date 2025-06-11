"""
Short-Term Memory Manager for AI Agents

This module provides temporary memory storage and caching using Redis.
It supports TTL-based expiration, session-based storage, and fast retrieval.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

import redis.asyncio as redis

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Represents a cached memory entry"""
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: Optional[datetime] = None
    accessed_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

class ShortTermMemoryManager:
    """
    Manages short-term memory and caching using Redis.

    Features:
    - TTL-based automatic expiration
    - Session-based memory storage
    - Tool result caching
    - Fast key-value retrieval
    - Memory usage optimization
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 3600):
        """
        Initialize the short-term memory manager.

        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (1 hour)
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.redis_client: Optional[redis.Redis] = None

    async def initialize(self):
        """Initialize the Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            await self.redis_client.ping()
            logger.info("ShortTermMemoryManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ShortTermMemoryManager: {e}")
            raise

    async def close(self):
        """Close the Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("ShortTermMemoryManager closed")

    def _make_key(self, agent_id: str, key: str, namespace: str = "memory") -> str:
        """Create a namespaced key for Redis"""
        return f"{namespace}:{agent_id}:{key}"

    async def store(
        self,
        agent_id: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "memory",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store a value in short-term memory.

        Args:
            agent_id: Agent identifier
            key: Memory key
            value: Value to store (will be JSON serialized)
            ttl: Time to live in seconds (uses default if None)
            namespace: Memory namespace
            metadata: Additional metadata

        Returns:
            True if stored successfully
        """
        if not self.redis_client:
            raise RuntimeError("Memory manager not initialized")

        redis_key = self._make_key(agent_id, key, namespace)
        ttl = ttl or self.default_ttl

        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            ttl=ttl,
            created_at=datetime.now(),
            accessed_count=0,
            metadata=metadata
        )

        try:
            # Serialize the entry
            serialized_entry = json.dumps(asdict(entry), default=str)

            # Store with TTL
            await self.redis_client.setex(redis_key, ttl, serialized_entry)

            logger.debug(f"Stored memory {redis_key} with TTL {ttl}s")
            return True

        except Exception as e:
            logger.error(f"Failed to store memory {redis_key}: {e}")
            return False

    async def retrieve(
        self,
        agent_id: str,
        key: str,
        namespace: str = "memory",
        update_access: bool = True
    ) -> Optional[Any]:
        """
        Retrieve a value from short-term memory.

        Args:
            agent_id: Agent identifier
            key: Memory key
            namespace: Memory namespace
            update_access: Whether to update access count and TTL

        Returns:
            The stored value or None if not found
        """
        if not self.redis_client:
            raise RuntimeError("Memory manager not initialized")

        redis_key = self._make_key(agent_id, key, namespace)

        try:
            # Get the entry
            serialized_entry = await self.redis_client.get(redis_key)
            if not serialized_entry:
                return None

            # Deserialize
            entry_dict = json.loads(serialized_entry)
            entry = CacheEntry(**entry_dict)

            # Update access count if requested
            if update_access:
                entry.accessed_count += 1
                # Extend TTL by 10% on access
                current_ttl = await self.redis_client.ttl(redis_key)
                if current_ttl > 0:
                    new_ttl = int(current_ttl * 1.1)
                    await self.redis_client.expire(redis_key, new_ttl)

                # Update the entry in Redis
                updated_entry = json.dumps(asdict(entry), default=str)
                await self.redis_client.setex(redis_key, new_ttl if current_ttl > 0 else self.default_ttl, updated_entry)

            logger.debug(f"Retrieved memory {redis_key} (accessed {entry.accessed_count} times)")
            return entry.value

        except Exception as e:
            logger.error(f"Failed to retrieve memory {redis_key}: {e}")
            return None

    async def delete(self, agent_id: str, key: str, namespace: str = "memory") -> bool:
        """Delete a memory entry"""
        if not self.redis_client:
            raise RuntimeError("Memory manager not initialized")

        redis_key = self._make_key(agent_id, key, namespace)

        try:
            result = await self.redis_client.delete(redis_key)
            logger.debug(f"Deleted memory {redis_key}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete memory {redis_key}: {e}")
            return False

    async def exists(self, agent_id: str, key: str, namespace: str = "memory") -> bool:
        """Check if a memory entry exists"""
        if not self.redis_client:
            raise RuntimeError("Memory manager not initialized")

        redis_key = self._make_key(agent_id, key, namespace)

        try:
            result = await self.redis_client.exists(redis_key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to check existence of {redis_key}: {e}")
            return False

    async def clear_agent_memory(self, agent_id: str, namespace: str = "memory") -> int:
        """Clear all memory entries for an agent"""
        if not self.redis_client:
            raise RuntimeError("Memory manager not initialized")

        pattern = self._make_key(agent_id, "*", namespace)

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} memory entries for agent {agent_id}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Failed to clear memory for agent {agent_id}: {e}")
            return 0

# Global instance
_short_memory_manager: Optional[ShortTermMemoryManager] = None

async def get_short_memory_manager() -> Optional[ShortTermMemoryManager]:
    """Get the global short-term memory manager instance"""
    global _short_memory_manager
    if _short_memory_manager is None:
        import os
        redis_url = os.getenv('REDIS_URI')
        if not redis_url:
            logger.warning("No Redis configured (REDIS_URI not set) - running without short-term memory")
            return None

        _short_memory_manager = ShortTermMemoryManager(redis_url=redis_url)
        try:
            await _short_memory_manager.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize short-term memory manager: {e}")
            # Return None for development mode
            _short_memory_manager = None
            return None
    return _short_memory_manager

async def close_short_memory_manager():
    """Close the global short-term memory manager instance"""
    global _short_memory_manager
    if _short_memory_manager:
        await _short_memory_manager.close()
        _short_memory_manager = None
