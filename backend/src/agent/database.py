"""
Database integration for Enhanced AI Agent Assistant
Provides database connectivity and ORM models for enhanced features.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
import json

import asyncpg
import redis.asyncio as redis
from contextlib import asynccontextmanager
from agent.mcp_client import MCPClient

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

@dataclass
class MCPRegistryEntry:
    name: str
    base_url: str
    id: Optional[int] = None # Typically set by DB
    description: Optional[str] = None
    enabled: bool = True
    last_checked_at: Optional[datetime] = None
    last_known_status: Optional[str] = None
    available_tools_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None # Typically set by DB
    updated_at: Optional[datetime] = None # Typically set by DB
    # Enhanced authentication fields
    auth_type: Optional[str] = None  # none, api_key, bearer_token, basic_auth
    auth_config: Optional[Dict[str, Any]] = None  # Encrypted auth configuration
    health_check_interval: int = 300  # Health check interval in seconds
    max_retries: int = 3  # Maximum retry attempts
    timeout_seconds: float = 30.0  # Request timeout

class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self):
        self.postgres_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.mcp_client: Optional[MCPClient] = None # MCPClient instance
        self._initialized = False
        # In-memory storage for tests and fallback
        self._threads: Dict[str, str] = {}
        self._messages: Dict[str, List[Dict[str, Any]]] = {}

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

            # Initialize MCPClient
            self.mcp_client = MCPClient() # MCPClient creates its own httpx.AsyncClient by default
            logger.info("MCPClient initialized.")

            self._initialized = True
            logger.info("DatabaseManager initialized successfully.")

        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise

    async def close(self):
        """Close database connections."""
        if self.postgres_pool:
            await self.postgres_pool.close()

        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed.")

        if self.mcp_client:
            await self.mcp_client.close() # Call MCPClient's own close method
            logger.info("MCPClient closed.")

        self._initialized = False
        logger.info("DatabaseManager closed.")

    @asynccontextmanager
    async def get_postgres_connection(self):
        """Get a PostgreSQL connection from the pool or in-memory for testing."""
        if not self.postgres_pool:
            # In-memory fake DB for tests
            class FakeConnection:
                def __init__(self, db_manager):
                    self.dbm = db_manager

                async def execute(self, query, *args):
                    if query.startswith("INSERT INTO chat_threads"):
                        thread_id, created_at = args
                        self.dbm._threads[thread_id] = created_at
                    elif query.startswith("INSERT INTO chat_messages"):
                        msg_id, thread_id, content, role, created_at = args
                        self.dbm._messages.setdefault(thread_id, []).append({
                            'id': msg_id,
                            'thread_id': thread_id,
                            'content': content,
                            'role': role,
                            'created_at': created_at
                        })
                    else:
                        pass

                async def fetchrow(self, query, *args):
                    if "SELECT id FROM chat_threads" in query:
                        thread_id = args[0]
                        if thread_id in self.dbm._threads:
                            return {'id': thread_id}
                        return None
                    return None

                async def fetch(self, query, *args):
                    if "SELECT content, role FROM chat_messages" in query:
                        thread_id = args[0]
                        msgs = self.dbm._messages.get(thread_id, [])
                        return [{'content': m['content'], 'role': m['role']} for m in msgs]
                    if "SELECT id, content, role, created_at FROM chat_messages" in query:
                        thread_id = args[0]
                        return self.dbm._messages.get(thread_id, []).copy()
                    return []

            conn = FakeConnection(self)
            yield conn
        else:
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

# --- ResearchResult Model and Repository ---
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class ResearchResult:
    id: Optional[int]
    query: str
    summary: str
    sources: List[Dict[str, Any]]
    created_at: str
    context_json: Optional[Dict[str, Any]] = None

class ResearchResultRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def create_research_result(self, query: str, summary: str, sources: List[Dict[str, Any]], context_json: Optional[Dict[str, Any]] = None) -> int:
        async with self.db.get_postgres_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO research_results (query, summary, sources, created_at, context_json)
                VALUES ($1, $2, $3, NOW(), $4)
                RETURNING id
                """,
                query, summary, json.dumps(sources), json.dumps(context_json) if context_json else None
            )
            return row["id"]

    async def get_research_result(self, result_id: int) -> Optional[ResearchResult]:
        async with self.db.get_postgres_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM research_results WHERE id = $1", result_id
            )
            if row:
                return ResearchResult(
                    id=row["id"],
                    query=row["query"],
                    summary=row["summary"],
                    sources=json.loads(row["sources"]),
                    created_at=row["created_at"].isoformat(),
                    context_json=json.loads(row["context_json"]) if row["context_json"] else None
                )
            return None

    async def list_research_results(self, limit: int = 20, offset: int = 0) -> List[ResearchResult]:
        async with self.db.get_postgres_connection() as conn:
            rows = await conn.fetch(
                "SELECT * FROM research_results ORDER BY created_at DESC LIMIT $1 OFFSET $2", limit, offset
            )
            return [
                ResearchResult(
                    id=row["id"],
                    query=row["query"],
                    summary=row["summary"],
                    sources=json.loads(row["sources"]),
                    created_at=row["created_at"].isoformat(),
                    context_json=json.loads(row["context_json"]) if row["context_json"] else None
                ) for row in rows
            ]

# Global database manager instance
db_manager = DatabaseManager()
task_repository = TaskRepository(db_manager)
metrics_repository = MetricsRepository(db_manager)
cache_manager = CacheManager(db_manager)
research_result_repository = ResearchResultRepository(db_manager)


class MCPRegistryRepository:
    """Repository for MCP Server Registry operations."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    async def _row_to_mcp_entry(self, row: asyncpg.Record) -> Optional[MCPRegistryEntry]:
        if not row:
            return None
        return MCPRegistryEntry(
            name=row['name'],
            base_url=row['base_url'],
            id=row['id'],
            description=row['description'],
            enabled=row['enabled'],
            last_checked_at=row['last_checked_at'],
            last_known_status=row['last_known_status'],
            available_tools_json=json.loads(row['available_tools_json']) if row['available_tools_json'] else None,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

    async def create_server(self, entry: MCPRegistryEntry) -> int:
        """Create a new MCP server entry."""
        async with self.db.get_postgres_connection() as conn:
            # Ensure created_at and updated_at are not part of the insert if relying on DB defaults
            # or set them explicitly if preferred
            now = datetime.now(timezone.utc)
            server_id = await conn.fetchval("""
                INSERT INTO mcp_server_registry (
                    name, base_url, description, enabled,
                    last_checked_at, last_known_status, available_tools_json,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8)
                RETURNING id
            """,
                entry.name,
                entry.base_url,
                entry.description,
                entry.enabled,
                entry.last_checked_at,
                entry.last_known_status,
                json.dumps(entry.available_tools_json) if entry.available_tools_json else None,
                now
            )
            return server_id

    async def get_server_by_id(self, server_id: int) -> Optional[MCPRegistryEntry]:
        """Get MCP server entry by ID."""
        async with self.db.get_postgres_connection() as conn:
            row = await conn.fetchrow("SELECT * FROM mcp_server_registry WHERE id = $1", server_id)
            return await self._row_to_mcp_entry(row)

    async def get_server_by_name(self, name: str) -> Optional[MCPRegistryEntry]:
        """Get MCP server entry by name."""
        async with self.db.get_postgres_connection() as conn:
            row = await conn.fetchrow("SELECT * FROM mcp_server_registry WHERE name = $1", name)
            return await self._row_to_mcp_entry(row)

    async def get_server_by_url(self, base_url: str) -> Optional[MCPRegistryEntry]:
        """Get MCP server entry by base_url."""
        async with self.db.get_postgres_connection() as conn:
            row = await conn.fetchrow("SELECT * FROM mcp_server_registry WHERE base_url = $1", base_url)
            return await self._row_to_mcp_entry(row)

    async def list_servers(self, enabled_only: bool = True, limit: int = 100, offset: int = 0) -> List[MCPRegistryEntry]:
        """List MCP server entries."""
        async with self.db.get_postgres_connection() as conn:
            query = "SELECT * FROM mcp_server_registry"
            params = []
            if enabled_only:
                query += " WHERE enabled = TRUE"
            query += " ORDER BY name ASC LIMIT $1 OFFSET $2"
            params.extend([limit, offset])

            if enabled_only: # Adjust param indexing if enabled_only is true
                 query = query.replace("$1", f"${len(params)-1}").replace("$2", f"${len(params)}")
            else: # if not enabled_only, WHERE clause is not added, so params are $1 and $2
                 query = query.replace("$1", "$1").replace("$2", "$2")

            # A more robust way for parameter indexing if WHERE clause is conditional
            final_query = "SELECT * FROM mcp_server_registry"
            conditions = []
            current_params = []
            if enabled_only:
                conditions.append(f"enabled = ${len(current_params) + 1}")
                current_params.append(True)

            if conditions:
                final_query += " WHERE " + " AND ".join(conditions)

            final_query += f" ORDER BY name ASC LIMIT ${len(current_params) + 1} OFFSET ${len(current_params) + 2}"
            current_params.extend([limit, offset])

            rows = await conn.fetch(final_query, *current_params)
            return [await self._row_to_mcp_entry(row) for row in rows if row is not None]

    async def update_server(self, server_id: int, update_data: Dict[str, Any]) -> bool:
        """Update an MCP server entry. update_data should contain field names and new values."""
        if not update_data:
            return False

        async with self.db.get_postgres_connection() as conn:
            fields = []
            values = []
            placeholder_idx = 1
            for key, value in update_data.items():
                # Ensure key is a valid column name to prevent SQL injection if keys are from unsafe source
                # For this controlled environment, we assume keys are valid.
                if key in ["id", "created_at"]: # Cannot update these
                    continue
                fields.append(f"{key} = ${placeholder_idx}")
                if isinstance(value, dict) or isinstance(value, list):
                    values.append(json.dumps(value))
                elif isinstance(value, datetime):
                    values.append(value)
                else:
                    values.append(value)
                placeholder_idx += 1

            if not fields: # No valid fields to update
                return False

            # Add updated_at manually as the trigger handles it
            # fields.append(f"updated_at = ${placeholder_idx}")
            # values.append(datetime.now(timezone.utc))

            query = f"UPDATE mcp_server_registry SET {', '.join(fields)} WHERE id = ${placeholder_idx}"
            values.append(server_id)

            result = await conn.execute(query, *values)
            return result.split(" ")[-1] == "1" # Check if one row was updated

    async def delete_server(self, server_id: int) -> bool:
        """Delete an MCP server entry by ID."""
        async with self.db.get_postgres_connection() as conn:
            result = await conn.execute("DELETE FROM mcp_server_registry WHERE id = $1", server_id)
            return result.split(" ")[-1] == "1"

    async def update_server_status(self, server_id: int, status: str, tools_json: Optional[Dict[str, Any]]) -> bool:
        """Update the status, last_checked_at, and available_tools_json of a server."""
        async with self.db.get_postgres_connection() as conn:
            now = datetime.now(timezone.utc)
            result = await conn.execute("""
                UPDATE mcp_server_registry
                SET last_known_status = $1, available_tools_json = $2, last_checked_at = $3, updated_at = $3
                WHERE id = $4
            """, status, json.dumps(tools_json) if tools_json else None, now, server_id)
            return result.split(" ")[-1] == "1"

mcp_registry_repository = MCPRegistryRepository(db_manager)

async def get_database_pool():
    """
    Initialize and return the PostgreSQL pool for testing and basic usage.
    """
    await db_manager.initialize()
    return db_manager.postgres_pool

def get_mcp_client() -> MCPClient:
    if not db_manager.mcp_client:
        # This case should ideally not be hit if accessed within FastAPI request lifecycle
        # after app startup, or if db_manager.initialize() is called explicitly before use.
        raise RuntimeError("MCPClient not initialized. Access it after DatabaseManager.initialize() or via db_manager.mcp_client.")
    return db_manager.mcp_client

def get_db_connection():
    """Get a synchronous database connection for simple operations."""
    import psycopg2
    import os

    # Try to get database URL from environment (fallback to None for development)
    database_url = os.getenv('POSTGRES_URI')
    if not database_url:
        # No database configured - return None for development mode
        print("⚠️ No database configured (POSTGRES_URI not set)")
        return None

    try:
        # Create a synchronous connection
        connection = psycopg2.connect(database_url)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        # Return None for development mode
        return None
