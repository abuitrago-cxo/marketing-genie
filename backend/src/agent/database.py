"""
Database integration for Enhanced AI Agent Assistant
Provides database connectivity and ORM models for enhanced features.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import json

import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class EventSeverity(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AgentTask:
    task_id: str
    agent_type: str
    task_type: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None

@dataclass
class AgentMetric:
    agent_type: str
    metric_name: str
    metric_value: float
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class LLMUsage:
    provider_id: str
    model_name: str
    tokens_used: int
    cost_estimate: Optional[float] = None
    response_time_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None
    task_id: Optional[str] = None
    agent_type: Optional[str] = None

@dataclass
class SystemEvent:
    event_type: str
    event_data: Optional[Dict[str, Any]] = None
    severity: EventSeverity = EventSeverity.INFO
    source: Optional[str] = None
    timestamp: Optional[datetime] = None

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections."""
        if self._initialized:
            return
        
        try:
            # Initialize PostgreSQL connection pool
            postgres_uri = os.getenv('POSTGRES_URI')
            if postgres_uri:
                self.postgres_pool = await asyncpg.create_pool(
                    postgres_uri,
                    min_size=2,
                    max_size=10,
                    command_timeout=60
                )
                logger.info("✅ PostgreSQL connection pool initialized")
            
            # Initialize Redis connection
            redis_uri = os.getenv('REDIS_URI')
            if redis_uri:
                self.redis_client = redis.from_url(
                    redis_uri,
                    encoding="utf-8",
                    decode_responses=True
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("✅ Redis connection initialized")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    async def close(self):
        """Close database connections."""
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self._initialized = False
    
    @asynccontextmanager
    async def get_postgres_connection(self):
        """Get a PostgreSQL connection from the pool."""
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL pool not initialized")
        
        async with self.postgres_pool.acquire() as connection:
            yield connection
    
    async def get_redis_client(self) -> redis.Redis:
        """Get Redis client."""
        if not self.redis_client:
            raise RuntimeError("Redis client not initialized")
        return self.redis_client

class TaskRepository:
    """Repository for agent task operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def create_task(self, task: AgentTask) -> str:
        """Create a new agent task."""
        async with self.db.get_postgres_connection() as conn:
            task_id = await conn.fetchval("""
                INSERT INTO agent_tasks (
                    task_id, agent_type, task_type, status, priority,
                    input_data, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
                RETURNING task_id
            """, 
                task.task_id,
                task.agent_type,
                task.task_type,
                task.status.value,
                task.priority.value,
                json.dumps(task.input_data) if task.input_data else None,
                datetime.now(timezone.utc)
            )
            return task_id
    
    async def update_task_status(
        self, 
        task_id: str, 
        status: TaskStatus,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        """Update task status and results."""
        async with self.db.get_postgres_connection() as conn:
            completed_at = datetime.now(timezone.utc) if status in [TaskStatus.COMPLETED, TaskStatus.FAILED] else None
            
            await conn.execute("""
                UPDATE agent_tasks 
                SET status = $2, output_data = $3, error_message = $4,
                    completed_at = $5, execution_time_ms = $6, updated_at = $7
                WHERE task_id = $1
            """,
                task_id,
                status.value,
                json.dumps(output_data) if output_data else None,
                error_message,
                completed_at,
                execution_time_ms,
                datetime.now(timezone.utc)
            )
    
    async def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID."""
        async with self.db.get_postgres_connection() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM agent_tasks WHERE task_id = $1
            """, task_id)
            
            if not row:
                return None
            
            return AgentTask(
                task_id=row['task_id'],
                agent_type=row['agent_type'],
                task_type=row['task_type'],
                status=TaskStatus(row['status']),
                priority=TaskPriority(row['priority']),
                input_data=json.loads(row['input_data']) if row['input_data'] else None,
                output_data=json.loads(row['output_data']) if row['output_data'] else None,
                error_message=row['error_message'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                completed_at=row['completed_at'],
                execution_time_ms=row['execution_time_ms']
            )
    
    async def get_tasks_by_agent(self, agent_type: str, limit: int = 100) -> List[AgentTask]:
        """Get tasks for a specific agent type."""
        async with self.db.get_postgres_connection() as conn:
            rows = await conn.fetch("""
                SELECT * FROM agent_tasks 
                WHERE agent_type = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            """, agent_type, limit)
            
            return [
                AgentTask(
                    task_id=row['task_id'],
                    agent_type=row['agent_type'],
                    task_type=row['task_type'],
                    status=TaskStatus(row['status']),
                    priority=TaskPriority(row['priority']),
                    input_data=json.loads(row['input_data']) if row['input_data'] else None,
                    output_data=json.loads(row['output_data']) if row['output_data'] else None,
                    error_message=row['error_message'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    completed_at=row['completed_at'],
                    execution_time_ms=row['execution_time_ms']
                )
                for row in rows
            ]

class MetricsRepository:
    """Repository for agent metrics operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def record_metric(self, metric: AgentMetric):
        """Record an agent metric."""
        async with self.db.get_postgres_connection() as conn:
            await conn.execute("""
                INSERT INTO agent_metrics (
                    agent_type, metric_name, metric_value, timestamp, metadata
                ) VALUES ($1, $2, $3, $4, $5)
            """,
                metric.agent_type,
                metric.metric_name,
                metric.metric_value,
                metric.timestamp or datetime.now(timezone.utc),
                json.dumps(metric.metadata) if metric.metadata else None
            )
    
    async def get_metrics(
        self, 
        agent_type: Optional[str] = None,
        metric_name: Optional[str] = None,
        hours: int = 24
    ) -> List[AgentMetric]:
        """Get metrics with optional filtering."""
        async with self.db.get_postgres_connection() as conn:
            query = """
                SELECT * FROM agent_metrics 
                WHERE timestamp > NOW() - INTERVAL '%s hours'
            """ % hours
            
            params = []
            if agent_type:
                query += " AND agent_type = $%d" % (len(params) + 1)
                params.append(agent_type)
            
            if metric_name:
                query += " AND metric_name = $%d" % (len(params) + 1)
                params.append(metric_name)
            
            query += " ORDER BY timestamp DESC"
            
            rows = await conn.fetch(query, *params)
            
            return [
                AgentMetric(
                    agent_type=row['agent_type'],
                    metric_name=row['metric_name'],
                    metric_value=row['metric_value'],
                    timestamp=row['timestamp'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                )
                for row in rows
            ]

class CacheManager:
    """Manages Redis cache operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set a cache value with TTL."""
        redis_client = await self.db.get_redis_client()
        await redis_client.setex(key, ttl, json.dumps(value))
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a cache value."""
        redis_client = await self.db.get_redis_client()
        value = await redis_client.get(key)
        return json.loads(value) if value else None
    
    async def delete(self, key: str):
        """Delete a cache value."""
        redis_client = await self.db.get_redis_client()
        await redis_client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a cache key exists."""
        redis_client = await self.db.get_redis_client()
        return await redis_client.exists(key)

# Global database manager instance
db_manager = DatabaseManager()
task_repository = TaskRepository(db_manager)
metrics_repository = MetricsRepository(db_manager)
cache_manager = CacheManager(db_manager)
