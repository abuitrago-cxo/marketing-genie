import logging
from typing import List, Dict, Any, Optional, Set
from pydantic import HttpUrl, Field
from datetime import datetime
import asyncio

from agent.database import db_manager, mcp_registry_repository, MCPRegistryEntry
from api.mcp_router import MCPToolDefinition, MCPToolParameter, MCPToolCallResponse # Re-using these models
from agent.tools.base import BaseTool, ToolCapability, ToolResult, ToolError # Your custom base tool
from agent.mcp_client import MCPServerAuth, AuthType, MCPServerHealth, MCPServerHealthStatus

logger = logging.getLogger(__name__)

class MCPToolConflictResolution:
    """Strategies for resolving tool name conflicts"""
    SKIP = "skip"  # Skip conflicting tools
    PREFIX = "prefix"  # Add server prefix to tool name
    REPLACE = "replace"  # Replace existing tool
    VERSION = "version"  # Add version suffix

# --- Helper to format MCP parameters for ToolCapability ---
def _mcp_params_to_tool_capability_params(mcp_params: Optional[Dict[str, MCPToolParameter]]) -> Dict[str, Any]:
    """Converts MCPToolParameters into the dict structure expected by ToolCapability."""
    if not mcp_params:
        return {"required": [], "optional": [], "properties": {}}

    required_params = []
    optional_params = []
    properties_desc = {}

    for name, param_def in mcp_params.items():
        if param_def.required:
            required_params.append(name)
        else:
            optional_params.append(name)
        properties_desc[name] = f"({param_def.type}) {param_def.description or ''}".strip()

    return {
        "required": required_params,
        "optional": optional_params,
        "properties": properties_desc # Store descriptions for validation/help messages
    }

# --- Enhanced Dynamic MCP Tool Wrapper ---
class DynamicMCPToolWrapper(BaseTool):
    """Enhanced wrapper for dynamically discovered MCP tools with better error handling and metadata."""

    def __init__(self, mcp_tool_def: MCPToolDefinition, server_base_url: HttpUrl, server_name: str = "unknown", conflict_resolution: str = MCPToolConflictResolution.PREFIX):
        # Handle tool name conflicts
        tool_name = self._resolve_tool_name(mcp_tool_def.tool_id, server_name, conflict_resolution)

        super().__init__(
            name=tool_name,
            description=f"[MCP:{server_name}] {mcp_tool_def.description}",
            category="dynamic_mcp_tool"
        )
        self.mcp_tool_def = mcp_tool_def
        self.server_base_url = server_base_url
        self.server_name = server_name
        self.original_tool_id = mcp_tool_def.tool_id
        self.conflict_resolution = conflict_resolution
        self._capabilities = self._generate_capabilities()
        self._last_health_check = None
        self._consecutive_failures = 0

    def _resolve_tool_name(self, original_name: str, server_name: str, resolution: str) -> str:
        """Resolve tool name conflicts based on strategy"""
        if resolution == MCPToolConflictResolution.PREFIX:
            return f"{server_name}_{original_name}"
        elif resolution == MCPToolConflictResolution.VERSION:
            return f"{original_name}_v1"
        else:
            return original_name

    def _generate_capabilities(self) -> List[ToolCapability]:
        """Generates the single capability for this MCP tool."""
        # An MCP tool is treated as a single capability/action
        # The 'action' name for execute() will be this capability's name.
        action_name = self.name # Or a fixed name like "invoke_mcp_tool"

        capability_params = {}
        if self.mcp_tool_def.input_schema and self.mcp_tool_def.input_schema.properties:
            capability_params = _mcp_params_to_tool_capability_params(
                self.mcp_tool_def.input_schema.properties
            )
        else: # Tool takes no parameters
             capability_params = _mcp_params_to_tool_capability_params(None)

        return [
            ToolCapability(
                name=action_name,
                description=self.mcp_tool_def.description, # Capability desc can be same as tool desc
                parameters=capability_params,
                examples=[], # MCP definition doesn't have examples, could be added if useful
                category=self.category
            )
        ]

    def get_capabilities(self) -> List[ToolCapability]:
        return self._capabilities

    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResult:
        """
        Enhanced execution with health monitoring and better error handling.
        """
        # Validate action matches tool name or original tool ID
        if action not in [self.name, self.original_tool_id]:
            logger.warning(f"DynamicMCPToolWrapper '{self.name}' called with unexpected action '{action}'. Expected '{self.name}' or '{self.original_tool_id}'.")

        if not db_manager.mcp_client:
            logger.error(f"MCPClient not available for tool {self.name}. Cannot execute.")
            raise ToolError("MCPClient not initialized", tool_name=self.name)

        start_time = datetime.now()

        try:
            logger.info(f"Executing MCP tool '{self.name}' (server: {self.server_name}, original_id: {self.original_tool_id}) with params: {parameters}")

            # Check server health before execution
            server_health = await db_manager.mcp_client.check_server_health(self.server_base_url)
            if server_health.status != MCPServerHealthStatus.HEALTHY:
                logger.warning(f"Server {self.server_name} is not healthy: {server_health.status}")
                if server_health.consecutive_failures > 3:
                    raise ToolError(f"Server {self.server_name} has failed {server_health.consecutive_failures} consecutive times", tool_name=self.name)

            mcp_response: MCPToolCallResponse = await db_manager.mcp_client.call_tool(
                server_base_url=self.server_base_url,
                tool_id=self.original_tool_id,  # Use original tool ID for MCP call
                parameters=parameters
            )

            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"MCP tool '{self.name}' completed in {execution_time:.2f}s with status: {mcp_response.status}")

            # Reset failure counter on success
            self._consecutive_failures = 0
            self._last_health_check = datetime.now()

            if mcp_response.status == "success":
                return ToolResult(
                    success=True,
                    data=mcp_response.result,
                    message=f"MCP tool '{self.name}' executed successfully on server '{self.server_name}'.",
                    tool_name=self.name,
                    tool_id=self.tool_id,
                    metadata={
                        "server_name": self.server_name,
                        "original_tool_id": self.original_tool_id,
                        "server_url": str(self.server_base_url),
                        "execution_time_ms": execution_time * 1000
                    }
                )
            else:
                error_msg = mcp_response.error_message or f"MCP tool '{self.name}' failed with no specific error message."
                logger.error(f"MCP tool '{self.name}' execution failed: {error_msg}")

                self._consecutive_failures += 1

                return ToolResult(
                    success=False,
                    error=error_msg,
                    message=f"MCP tool '{self.name}' execution failed on server '{self.server_name}'.",
                    tool_name=self.name,
                    tool_id=self.tool_id,
                    metadata={
                        "server_name": self.server_name,
                        "original_tool_id": self.original_tool_id,
                        "consecutive_failures": self._consecutive_failures
                    }
                )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._consecutive_failures += 1

            logger.error(f"Error during MCP tool '{self.name}' execution after {execution_time:.2f}s: {e}", exc_info=True)

            # Enhanced error context
            error_details = {
                "server_name": self.server_name,
                "original_tool_id": self.original_tool_id,
                "server_url": str(self.server_base_url),
                "consecutive_failures": self._consecutive_failures,
                "execution_time_ms": execution_time * 1000,
                "error_type": type(e).__name__
            }

            raise ToolError(
                f"MCP tool '{self.name}' failed on server '{self.server_name}': {str(e)}",
                tool_name=self.name,
                details=error_details
            )

# --- Enhanced function to create an Agent Tool from an MCPToolDefinition ---
def mcp_tool_def_to_agent_tool(
    mcp_tool_def: MCPToolDefinition,
    server_base_url: HttpUrl,
    server_name: str = "unknown",
    conflict_resolution: str = MCPToolConflictResolution.PREFIX
) -> BaseTool:
    """
    Creates a custom agent BaseTool from an MCPToolDefinition using the enhanced wrapper.

    Args:
        mcp_tool_def: The MCP tool definition
        server_base_url: Base URL of the MCP server
        server_name: Human-readable name of the server
        conflict_resolution: Strategy for handling name conflicts

    Returns:
        Enhanced DynamicMCPToolWrapper instance
    """
    return DynamicMCPToolWrapper(
        mcp_tool_def,
        server_base_url,
        server_name,
        conflict_resolution
    )

# --- Enhanced main function to load all dynamic MCP tools ---
async def load_dynamic_mcp_tools(
    conflict_resolution: str = MCPToolConflictResolution.PREFIX,
    max_concurrent_servers: int = 5,
    timeout_per_server: float = 30.0
) -> List[BaseTool]:
    """
    Enhanced loading of MCP tools with better error handling, conflict resolution, and concurrency control.

    Args:
        conflict_resolution: Strategy for handling tool name conflicts
        max_concurrent_servers: Maximum number of servers to query concurrently
        timeout_per_server: Timeout for each server discovery operation

    Returns:
        List of successfully loaded BaseTool instances
    """
    if not db_manager.mcp_client:
        logger.error("MCPClient not initialized. Cannot load dynamic MCP tools.")
        return []

    all_agent_tools: List[BaseTool] = []
    tool_names_seen: Set[str] = set()
    server_stats = {
        "total": 0,
        "successful": 0,
        "failed": 0,
        "tools_loaded": 0,
        "tools_skipped": 0
    }

    try:
        enabled_servers: List[MCPRegistryEntry] = await mcp_registry_repository.list_servers(enabled_only=True)
        server_stats["total"] = len(enabled_servers)
        logger.info(f"Found {len(enabled_servers)} enabled MCP servers in the registry.")

        # Process servers with concurrency control
        semaphore = asyncio.Semaphore(max_concurrent_servers)

        async def process_server(server_entry: MCPRegistryEntry) -> List[BaseTool]:
            async with semaphore:
                return await _process_single_server(
                    server_entry,
                    conflict_resolution,
                    tool_names_seen,
                    timeout_per_server
                )

        # Execute server processing concurrently
        server_tasks = [process_server(server) for server in enabled_servers]
        server_results = await asyncio.gather(*server_tasks, return_exceptions=True)

        # Collect results and update statistics
        for i, result in enumerate(server_results):
            server_entry = enabled_servers[i]
            if isinstance(result, Exception):
                logger.error(f"Server {server_entry.name} failed completely: {result}")
                server_stats["failed"] += 1
            else:
                tools_from_server = result
                all_agent_tools.extend(tools_from_server)
                server_stats["successful"] += 1
                server_stats["tools_loaded"] += len(tools_from_server)
                logger.info(f"Successfully loaded {len(tools_from_server)} tools from server {server_entry.name}")

    except Exception as e:
        logger.error(f"Critical error occurred while loading dynamic MCP tools: {e}", exc_info=True)
        server_stats["failed"] = server_stats["total"]

    # Log final statistics
    logger.info(f"MCP Tool Loading Summary:")
    logger.info(f"  - Servers processed: {server_stats['total']}")
    logger.info(f"  - Servers successful: {server_stats['successful']}")
    logger.info(f"  - Servers failed: {server_stats['failed']}")
    logger.info(f"  - Tools loaded: {server_stats['tools_loaded']}")
    logger.info(f"  - Tools skipped: {server_stats['tools_skipped']}")

    return all_agent_tools

async def _process_single_server(
    server_entry: MCPRegistryEntry,
    conflict_resolution: str,
    tool_names_seen: Set[str],
    timeout: float
) -> List[BaseTool]:
    """Process a single MCP server and return its tools"""
    server_tools: List[BaseTool] = []

    try:
        logger.info(f"Discovering tools from server: {server_entry.name} ({server_entry.base_url})")

        server_http_url = HttpUrl(str(server_entry.base_url))

        # Discover tools with timeout
        discovered_mcp_tools: List[MCPToolDefinition] = await asyncio.wait_for(
            db_manager.mcp_client.discover_tools(server_http_url),
            timeout=timeout
        )

        logger.info(f"Discovered {len(discovered_mcp_tools)} tools from {server_entry.name}")

        for mcp_tool_def in discovered_mcp_tools:
            try:
                agent_tool = mcp_tool_def_to_agent_tool(
                    mcp_tool_def,
                    server_http_url,
                    server_entry.name,
                    conflict_resolution
                )

                # Handle name conflicts
                if agent_tool.name in tool_names_seen:
                    if conflict_resolution == MCPToolConflictResolution.SKIP:
                        logger.warning(f"Skipping tool '{agent_tool.name}' due to name conflict")
                        continue
                    elif conflict_resolution == MCPToolConflictResolution.REPLACE:
                        logger.warning(f"Replacing existing tool '{agent_tool.name}'")
                        tool_names_seen.discard(agent_tool.name)

                tool_names_seen.add(agent_tool.name)
                server_tools.append(agent_tool)
                logger.debug(f"Successfully converted MCP tool '{mcp_tool_def.tool_id}' from {server_entry.name} to agent tool '{agent_tool.name}'")

            except Exception as e:
                logger.error(f"Failed to convert MCP tool '{mcp_tool_def.tool_id}' from server {server_entry.name}: {e}", exc_info=True)
                continue

    except asyncio.TimeoutError:
        logger.error(f"Timeout ({timeout}s) while discovering tools from server {server_entry.name}")
    except Exception as e:
        logger.error(f"Failed to process server {server_entry.name} ({server_entry.base_url}): {e}", exc_info=True)

    return server_tools

# Example usage (remains largely conceptual):
# async def main():
#     await db_manager.initialize()
#     from agent.tools.registry import get_tool_registry
#     dynamic_tools = await load_dynamic_mcp_tools()
#     registry = get_tool_registry()
#     for tool in dynamic_tools:
#         registry.register_tool(tool) # Register them into your existing registry
#         print(f"Registered tool: {tool.name}")
#     # ... rest of your agent setup using the registry ...
#     await db_manager.close()

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())
