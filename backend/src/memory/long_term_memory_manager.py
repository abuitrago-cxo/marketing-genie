"""
Long-Term Memory Manager for AI Agents

This module provides persistent memory storage and retrieval for AI agents using PostgreSQL.
It supports vector embeddings, importance scoring, and semantic search capabilities.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

import asyncpg

logger = logging.getLogger(__name__)

@dataclass
class Memory:
    """Represents a single memory entry"""
    id: Optional[int] = None
    agent_id: str = ""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    project_id: Optional[int] = None
    memory_type: str = ""
    content: str = ""
    content_vector: Optional[List[float]] = None
    importance_score: float = 0.5
    last_accessed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class LongTermMemoryManager:
    """
    Manages long-term memory storage and retrieval for AI agents.

    Features:
    - Persistent storage in PostgreSQL
    - Vector embeddings for semantic search
    - Importance scoring for memory prioritization
    - Memory type categorization
    - Project and user association
    """

    def __init__(self, embedding_model: str = "simple"):
        """
        Initialize the memory manager.

        Args:
            embedding_model: Type of embedding to use ("simple" for basic text matching)
        """
        self.embedding_model = embedding_model
        self.pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        """Initialize the database connection pool"""
        try:
            import os
            import asyncpg

            # Get database URL from environment (fallback to None for development)
            database_url = os.getenv('POSTGRES_URI')
            if not database_url:
                logger.warning("No database configured (POSTGRES_URI not set) - running in development mode")
                self.pool = None
                return

            # Create connection pool
            self.pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("LongTermMemoryManager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LongTermMemoryManager: {e}")
            # Don't raise the exception, just log it for now
            self.pool = None

    async def close(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("LongTermMemoryManager closed")

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate simple embedding for text (basic implementation)"""
        try:
            # Simple word-based embedding for now
            words = text.lower().split()
            # Create a simple hash-based embedding
            embedding = [0.0] * 100  # 100-dimensional vector
            for i, word in enumerate(words[:100]):
                embedding[i % 100] += hash(word) % 1000 / 1000.0
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return [0.0] * 100

    def _calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            if not vector1 or not vector2 or len(vector1) != len(vector2):
                return 0.0

            dot_product = sum(a * b for a, b in zip(vector1, vector2))
            norm_v1 = sum(a * a for a in vector1) ** 0.5
            norm_v2 = sum(b * b for b in vector2) ** 0.5

            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0

            similarity = dot_product / (norm_v1 * norm_v2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

    async def store_memory(
        self,
        agent_id: str,
        content: str,
        memory_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_id: Optional[int] = None,
        importance_score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Store a new memory entry.

        Args:
            agent_id: Identifier of the agent storing the memory
            content: Text content of the memory
            memory_type: Type/category of the memory
            user_id: Associated user ID (optional)
            session_id: Associated session/thread ID (optional)
            project_id: Associated project ID (optional)
            importance_score: Importance score (0.0 to 1.0)
            metadata: Additional metadata (optional)

        Returns:
            ID of the stored memory entry
        """
        if not self.pool:
            raise RuntimeError("Memory manager not initialized")

        # Generate embedding for the content
        content_vector = self._generate_embedding(content)
        content_vector_json = json.dumps(content_vector) if content_vector else None

        query = """
        INSERT INTO agent_long_term_memory
        (agent_id, user_id, session_id, project_id, memory_type, content,
         content_vector, importance_score, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id
        """

        try:
            async with self.pool.acquire() as conn:
                memory_id = await conn.fetchval(
                    query,
                    agent_id,
                    user_id,
                    session_id,
                    project_id,
                    memory_type,
                    content,
                    content_vector_json,
                    importance_score,
                    json.dumps(metadata) if metadata else None
                )

                logger.info(f"Stored memory {memory_id} for agent {agent_id}")
                return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    async def retrieve_memories(
        self,
        agent_id: str,
        query_text: Optional[str] = None,
        memory_type: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[int] = None,
        limit: int = 10,
        min_importance: float = 0.0,
        similarity_threshold: float = 0.7
    ) -> List[Memory]:
        """
        Retrieve memories based on various criteria.

        Args:
            agent_id: Agent identifier
            query_text: Text to search for (semantic search)
            memory_type: Filter by memory type
            user_id: Filter by user ID
            project_id: Filter by project ID
            limit: Maximum number of memories to return
            min_importance: Minimum importance score
            similarity_threshold: Minimum similarity for semantic search

        Returns:
            List of matching Memory objects
        """
        if not self.pool:
            raise RuntimeError("Memory manager not initialized")

        # Build query conditions
        conditions = ["agent_id = $1", "importance_score >= $2"]
        params = [agent_id, min_importance]
        param_count = 2

        if memory_type:
            param_count += 1
            conditions.append(f"memory_type = ${param_count}")
            params.append(memory_type)

        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)

        if project_id:
            param_count += 1
            conditions.append(f"project_id = ${param_count}")
            params.append(project_id)

        where_clause = " AND ".join(conditions)

        query = f"""
        SELECT id, agent_id, user_id, session_id, project_id, memory_type,
               content, content_vector, importance_score, last_accessed_at,
               created_at, metadata
        FROM agent_long_term_memory
        WHERE {where_clause}
        ORDER BY importance_score DESC, created_at DESC
        LIMIT {limit}
        """

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *params)

                memories = []
                query_vector = None

                if query_text:
                    query_vector = self._generate_embedding(query_text)

                for row in rows:
                    memory = Memory(
                        id=row['id'],
                        agent_id=row['agent_id'],
                        user_id=row['user_id'],
                        session_id=row['session_id'],
                        project_id=row['project_id'],
                        memory_type=row['memory_type'],
                        content=row['content'],
                        content_vector=json.loads(row['content_vector']) if row['content_vector'] else None,
                        importance_score=row['importance_score'],
                        last_accessed_at=row['last_accessed_at'],
                        created_at=row['created_at'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else None
                    )

                    # Apply semantic similarity filter if query_text provided
                    if query_text and query_vector and memory.content_vector:
                        similarity = self._calculate_similarity(query_vector, memory.content_vector)
                        if similarity >= similarity_threshold:
                            memories.append(memory)
                    else:
                        memories.append(memory)

                # Update last_accessed_at for retrieved memories
                if memories:
                    memory_ids = [m.id for m in memories if m.id]
                    await self._update_last_accessed(memory_ids)

                logger.info(f"Retrieved {len(memories)} memories for agent {agent_id}")
                return memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            raise

    async def _update_last_accessed(self, memory_ids: List[int]):
        """Update last_accessed_at timestamp for given memory IDs"""
        if not memory_ids or not self.pool:
            return

        query = """
        UPDATE agent_long_term_memory
        SET last_accessed_at = CURRENT_TIMESTAMP
        WHERE id = ANY($1)
        """

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, memory_ids)
        except Exception as e:
            logger.error(f"Failed to update last_accessed timestamps: {e}")

    async def update_memory_importance(self, memory_id: int, importance_score: float):
        """Update the importance score of a memory"""
        if not self.pool:
            raise RuntimeError("Memory manager not initialized")

        query = """
        UPDATE agent_long_term_memory
        SET importance_score = $1, last_accessed_at = CURRENT_TIMESTAMP
        WHERE id = $2
        """

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, importance_score, memory_id)
                logger.info(f"Updated importance score for memory {memory_id}")
        except Exception as e:
            logger.error(f"Failed to update memory importance: {e}")
            raise

    async def delete_memory(self, memory_id: int):
        """Delete a memory entry"""
        if not self.pool:
            raise RuntimeError("Memory manager not initialized")

        query = "DELETE FROM agent_long_term_memory WHERE id = $1"

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, memory_id)
                logger.info(f"Deleted memory {memory_id}")
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            raise

    async def get_memory_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics about stored memories for an agent"""
        if not self.pool:
            raise RuntimeError("Memory manager not initialized")

        query = """
        SELECT
            COUNT(*) as total_memories,
            COUNT(DISTINCT memory_type) as memory_types,
            AVG(importance_score) as avg_importance,
            MAX(created_at) as latest_memory,
            MIN(created_at) as earliest_memory
        FROM agent_long_term_memory
        WHERE agent_id = $1
        """

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, agent_id)

                return {
                    'total_memories': row['total_memories'],
                    'memory_types': row['memory_types'],
                    'avg_importance': float(row['avg_importance']) if row['avg_importance'] else 0.0,
                    'latest_memory': row['latest_memory'],
                    'earliest_memory': row['earliest_memory']
                }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}

# Global instance
_memory_manager: Optional[LongTermMemoryManager] = None

async def get_memory_manager() -> LongTermMemoryManager:
    """Get the global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = LongTermMemoryManager()
        await _memory_manager.initialize()
    return _memory_manager

async def close_memory_manager():
    """Close the global memory manager instance"""
    global _memory_manager
    if _memory_manager:
        await _memory_manager.close()
        _memory_manager = None

# Alias for get_memory_manager to maintain API compatibility with imports
async def get_long_memory_manager() -> LongTermMemoryManager:
    """Alias for get_memory_manager. Returns the global memory manager instance."""
    return await get_memory_manager()
