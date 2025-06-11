"""
Integration Pattern for Tools + Memory in LangGraph Nodes

This module provides a standardized pattern for integrating tools and memory
in all LangGraph nodes across the 6 specialized graphs.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from agent.state import OverallState, MemoryEnhancedState
from . import get_memory_manager, get_short_memory_manager
from agent.mcp_client import MCPClient
from agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

class IntegratedNodePattern:
    """
    Base pattern for all LangGraph nodes with integrated tools and memory.

    This class provides a standardized way to:
    1. Load and use tools (static + dynamic MCP)
    2. Retrieve relevant memories before processing
    3. Store important findings in long-term memory
    4. Cache results in short-term memory
    5. Track performance and errors
    """

    def __init__(
        self,
        node_name: str,
        agent_id: str,
        required_tools: Optional[List[str]] = None,
        memory_types: Optional[List[str]] = None,
        cache_ttl: int = 3600
    ):
        """
        Initialize the integrated node pattern.

        Args:
            node_name: Name of the node (for logging and caching)
            agent_id: Agent identifier for memory operations
            required_tools: List of required tool names
            memory_types: List of memory types to retrieve
            cache_ttl: Cache TTL in seconds
        """
        self.node_name = node_name
        self.agent_id = agent_id
        self.required_tools = required_tools or []
        self.memory_types = memory_types or []
        self.cache_ttl = cache_ttl

        # Will be initialized in setup
        self.tool_registry: Optional[ToolRegistry] = None
        self.long_memory = None
        self.short_memory = None
        self.mcp_client: Optional[MCPClient] = None

    async def setup(self):
        """Initialize all components"""
        try:
            # Initialize tool registry
            self.tool_registry = ToolRegistry()

            # Initialize memory managers
            self.long_memory = await get_memory_manager()
            self.short_memory = await get_short_memory_manager()

            # Initialize MCP client for dynamic tools
            self.mcp_client = MCPClient()

            logger.info(f"IntegratedNodePattern setup complete for {self.node_name}")

        except Exception as e:
            logger.error(f"Failed to setup IntegratedNodePattern for {self.node_name}: {e}")
            raise

    async def retrieve_relevant_memories(
        self,
        state: Union[OverallState, MemoryEnhancedState],
        query_text: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for the current context.

        Args:
            state: Current state
            query_text: Text to search for in memories
            limit: Maximum number of memories to retrieve

        Returns:
            List of relevant memories
        """
        if not self.long_memory:
            return []

        try:
            memories = []

            # Retrieve memories for each type
            for memory_type in self.memory_types:
                type_memories = await self.long_memory.retrieve_memories(
                    agent_id=self.agent_id,
                    query_text=query_text,
                    memory_type=memory_type,
                    project_id=getattr(state, 'project_id', None),
                    limit=limit
                )
                memories.extend([{
                    'id': m.id,
                    'type': m.memory_type,
                    'content': m.content,
                    'importance': m.importance_score,
                    'metadata': m.metadata
                } for m in type_memories])

            # Sort by importance and limit
            memories.sort(key=lambda x: x['importance'], reverse=True)
            memories = memories[:limit]

            logger.info(f"Retrieved {len(memories)} relevant memories for {self.node_name}")
            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories for {self.node_name}: {e}")
            return []

    async def store_memory(
        self,
        state: Union[OverallState, MemoryEnhancedState],
        content: str,
        memory_type: str,
        importance_score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Store a new memory entry.

        Args:
            state: Current state
            content: Memory content
            memory_type: Type of memory
            importance_score: Importance score (0.0 to 1.0)
            metadata: Additional metadata

        Returns:
            Memory ID if stored successfully
        """
        if not self.long_memory:
            return None

        try:
            from datetime import datetime
            memory_id = await self.long_memory.store_memory(
                agent_id=self.agent_id,
                content=content,
                memory_type=memory_type,
                session_id=getattr(state, 'session_id', None),
                project_id=getattr(state, 'project_id', None),
                importance_score=importance_score,
                metadata={
                    **(metadata or {}),
                    'node_name': self.node_name,
                    'stored_at': datetime.now().isoformat()
                }
            )

            logger.info(f"Stored memory {memory_id} from {self.node_name}")
            return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory from {self.node_name}: {e}")
            return None

    async def get_cached_result(
        self,
        cache_key: str,
        namespace: str = "node_results"
    ) -> Optional[Any]:
        """Get cached result if available"""
        if not self.short_memory:
            return None

        try:
            result = await self.short_memory.retrieve(
                agent_id=self.agent_id,
                key=f"{self.node_name}:{cache_key}",
                namespace=namespace
            )

            if result:
                logger.debug(f"Cache hit for {self.node_name}:{cache_key}")

            return result

        except Exception as e:
            logger.error(f"Failed to get cached result for {self.node_name}: {e}")
            return None

    async def store_cached_result(
        self,
        cache_key: str,
        result: Any,
        namespace: str = "node_results",
        ttl: Optional[int] = None
    ) -> bool:
        """Store result in cache"""
        if not self.short_memory:
            return False

        try:
            from datetime import datetime
            success = await self.short_memory.store(
                agent_id=self.agent_id,
                key=f"{self.node_name}:{cache_key}",
                value=result,
                ttl=ttl or self.cache_ttl,
                namespace=namespace,
                metadata={
                    'node_name': self.node_name,
                    'cached_at': datetime.now().isoformat()
                }
            )

            if success:
                logger.debug(f"Cached result for {self.node_name}:{cache_key}")

            return success

        except Exception as e:
            logger.error(f"Failed to cache result for {self.node_name}: {e}")
            return False

    async def load_required_tools(self) -> Dict[str, Any]:
        """Load all required tools (static + dynamic MCP)"""
        tools = {}

        try:
            # Load static tools from registry
            if self.tool_registry:
                for tool_name in self.required_tools:
                    tool = self.tool_registry.get_tool(tool_name)
                    if tool:
                        tools[tool_name] = tool
                        logger.debug(f"Loaded static tool: {tool_name}")

            # Load dynamic MCP tools if available
            if self.mcp_client:
                # This would be implemented based on MCP client capabilities
                # For now, we'll just log that MCP tools are available
                logger.debug(f"MCP client available for dynamic tool loading")

            logger.info(f"Loaded {len(tools)} tools for {self.node_name}")
            return tools

        except Exception as e:
            logger.error(f"Failed to load tools for {self.node_name}: {e}")
            return {}

    async def execute_with_pattern(
        self,
        state: Union[OverallState, MemoryEnhancedState],
        execution_func: Any,  # Callable
        cache_key: Optional[str] = None,
        memory_content: Optional[str] = None,
        memory_type: Optional[str] = None,
        importance_score: float = 0.5
    ) -> Any:
        """
        Execute a function with the full integrated pattern.

        This method:
        1. Checks cache first
        2. Retrieves relevant memories
        3. Loads required tools
        4. Executes the function
        5. Stores results in cache and memory
        6. Returns the result
        """
        start_time = datetime.now()

        try:
            # 1. Check cache first
            if cache_key:
                cached_result = await self.get_cached_result(cache_key)
                if cached_result:
                    logger.info(f"Returning cached result for {self.node_name}")
                    return cached_result

            # 2. Retrieve relevant memories
            memories = []
            if self.memory_types:
                query_text = memory_content or str(state.get('messages', [])[-1] if state.get('messages') else '')
                memories = await self.retrieve_relevant_memories(state, query_text)

            # 3. Load required tools
            tools = await self.load_required_tools()

            # 4. Execute the function with context
            context = {
                'memories': memories,
                'tools': tools,
                'node_name': self.node_name,
                'agent_id': self.agent_id
            }

            result = await execution_func(state, context)

            # 5. Store in cache if cache_key provided
            if cache_key and result:
                await self.store_cached_result(cache_key, result)

            # 6. Store important findings in memory
            if memory_content and memory_type:
                await self.store_memory(
                    state=state,
                    content=memory_content,
                    memory_type=memory_type,
                    importance_score=importance_score,
                    metadata={
                        'execution_time': (datetime.now() - start_time).total_seconds(),
                        'tools_used': list(tools.keys()),
                        'memories_retrieved': len(memories)
                    }
                )

            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Executed {self.node_name} in {execution_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"Failed to execute {self.node_name}: {e}")
            raise

# Convenience function for creating integrated nodes
def create_integrated_node(
    node_name: str,
    agent_id: str,
    execution_func: Any,  # Callable
    required_tools: Optional[List[str]] = None,
    memory_types: Optional[List[str]] = None,
    cache_ttl: int = 3600
) -> Any:  # Callable
    """
    Create an integrated node function with tools and memory.

    Args:
        node_name: Name of the node
        agent_id: Agent identifier
        execution_func: The actual node execution function
        required_tools: List of required tool names
        memory_types: List of memory types to retrieve
        cache_ttl: Cache TTL in seconds

    Returns:
        Integrated node function
    """
    async def integrated_node(state: Union[OverallState, MemoryEnhancedState]) -> Union[OverallState, MemoryEnhancedState]:
        pattern = IntegratedNodePattern(
            node_name=node_name,
            agent_id=agent_id,
            required_tools=required_tools,
            memory_types=memory_types,
            cache_ttl=cache_ttl
        )

        await pattern.setup()

        # Execute with the pattern
        result = await pattern.execute_with_pattern(
            state=state,
            execution_func=execution_func,
            cache_key=f"state_{hash(str(state))}"  # Simple state-based cache key
        )

        return result or state

    return integrated_node
