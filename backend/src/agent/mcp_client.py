import httpx
from typing import List, Dict, Any, Optional
from pydantic import HttpUrl, ValidationError
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio
from datetime import datetime

# Reuse models from mcp_router for consistency, assuming external servers follow a similar spec.
# If not, client-specific models might be needed.
from api.mcp_router import MCPToolDefinition, MCPToolCallRequest, MCPToolCallResponse, MCPToolInputSchema, MCPToolOutputSchema, MCPToolParameter

logger = logging.getLogger(__name__)

class AuthType(str, Enum):
    """Supported authentication types for MCP servers"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"

@dataclass
class MCPServerAuth:
    """Authentication configuration for MCP servers"""
    auth_type: AuthType = AuthType.NONE
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class MCPClientError(Exception):
    """Base exception for MCPClient errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_content: Optional[str] = None, server_url: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_content = response_content
        self.server_url = server_url

class MCPServerHealthStatus(str, Enum):
    """Health status of MCP servers"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"

@dataclass
class MCPServerHealth:
    """Health information for MCP servers"""
    status: MCPServerHealthStatus
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    consecutive_failures: int = 0

class MCPClient:
    """Enhanced client for interacting with external MCP-compliant servers with authentication and health monitoring."""

    def __init__(self, http_client: Optional[httpx.AsyncClient] = None, timeout: float = 30.0, max_retries: int = 3):
        """
        Initializes the MCPClient.
        Args:
            http_client: An optional httpx.AsyncClient instance. If None, a new one is created.
            timeout: Default timeout for HTTP requests.
            max_retries: Maximum number of retry attempts for failed requests.
        """
        self._client = http_client if http_client else httpx.AsyncClient(timeout=timeout)
        self._timeout = timeout
        self._max_retries = max_retries
        self._server_health: Dict[str, MCPServerHealth] = {}
        self._auth_cache: Dict[str, MCPServerAuth] = {}

    def set_server_auth(self, server_url: str, auth: MCPServerAuth):
        """Set authentication configuration for a specific server"""
        self._auth_cache[server_url] = auth
        logger.info(f"Authentication configured for server {server_url} with type {auth.auth_type}")

    def _get_auth_headers(self, server_url: str) -> Dict[str, str]:
        """Get authentication headers for a server"""
        auth = self._auth_cache.get(server_url)
        if not auth or auth.auth_type == AuthType.NONE:
            return {}

        headers = {}
        if auth.auth_type == AuthType.API_KEY and auth.api_key:
            headers[auth.api_key_header] = auth.api_key
        elif auth.auth_type == AuthType.BEARER_TOKEN and auth.bearer_token:
            headers["Authorization"] = f"Bearer {auth.bearer_token}"
        elif auth.auth_type == AuthType.BASIC_AUTH and auth.username and auth.password:
            import base64
            credentials = base64.b64encode(f"{auth.username}:{auth.password}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"

        return headers

    async def check_server_health(self, server_base_url: HttpUrl) -> MCPServerHealth:
        """Check the health status of an MCP server"""
        server_url = str(server_base_url)
        start_time = datetime.now()

        try:
            health_url = f"{str(server_base_url).rstrip('/')}/mcp/v1/health"
            headers = self._get_auth_headers(server_url)

            response = await self._client.get(health_url, headers=headers, timeout=5.0)
            response_time = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                health = MCPServerHealth(
                    status=MCPServerHealthStatus.HEALTHY,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    consecutive_failures=0
                )
            else:
                health = MCPServerHealth(
                    status=MCPServerHealthStatus.UNHEALTHY,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_message=f"HTTP {response.status_code}",
                    consecutive_failures=self._server_health.get(server_url, MCPServerHealth(MCPServerHealthStatus.UNKNOWN, datetime.now())).consecutive_failures + 1
                )

        except Exception as e:
            health = MCPServerHealth(
                status=MCPServerHealthStatus.TIMEOUT if "timeout" in str(e).lower() else MCPServerHealthStatus.UNHEALTHY,
                last_check=datetime.now(),
                error_message=str(e),
                consecutive_failures=self._server_health.get(server_url, MCPServerHealth(MCPServerHealthStatus.UNKNOWN, datetime.now())).consecutive_failures + 1
            )

        self._server_health[server_url] = health
        return health

    async def discover_tools(self, server_base_url: HttpUrl, auth: Optional[MCPServerAuth] = None) -> List[MCPToolDefinition]:
        """
        Discovers available tools from an external MCP server with authentication and retry logic.
        Args:
            server_base_url: The base URL of the MCP server.
            auth: Optional authentication configuration for this request.
        Returns:
            A list of MCPToolDefinition objects.
        Raises:
            MCPClientError: If the request fails or the response is invalid.
        """
        server_url = str(server_base_url)

        # Set auth if provided
        if auth:
            self.set_server_auth(server_url, auth)

        tools_url = f"{str(server_base_url).rstrip('/')}/mcp/v1/tools"
        headers = self._get_auth_headers(server_url)

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self._max_retries):
            try:
                response = await self._client.get(tools_url, headers=headers, timeout=self._timeout)
                response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses

                tools_data = response.json()
                if not isinstance(tools_data, list):
                    raise MCPClientError(
                        message="Invalid response format from server: expected a list of tools.",
                        response_content=response.text,
                        server_url=server_url
                    )

                parsed_tools: List[MCPToolDefinition] = []
                for tool_dict in tools_data:
                    try:
                        # Manually reconstruct nested Pydantic models if necessary
                        input_schema_data = tool_dict.get('input_schema', {})
                        output_schema_data = tool_dict.get('output_schema', {})

                        input_schema = MCPToolInputSchema(
                            type=input_schema_data.get('type', 'object'),
                            properties={k: MCPToolParameter(**v) for k, v in input_schema_data.get('properties', {}).items()},
                            required=input_schema_data.get('required')
                        )
                        output_schema = MCPToolOutputSchema(
                            type=output_schema_data.get('type', 'object'),
                            properties=output_schema_data.get('properties')
                        )

                        parsed_tools.append(MCPToolDefinition(
                            tool_id=tool_dict['tool_id'],
                            name=tool_dict['name'],
                            description=tool_dict['description'],
                            input_schema=input_schema,
                            output_schema=output_schema
                        ))
                    except (ValidationError, KeyError) as e:
                        logger.error(f"Failed to parse tool definition: {tool_dict}. Error: {e}")
                        # Skip invalid tools instead of failing completely
                        continue

                # Update health status on success
                self._server_health[server_url] = MCPServerHealth(
                    status=MCPServerHealthStatus.HEALTHY,
                    last_check=datetime.now(),
                    consecutive_failures=0
                )

                return parsed_tools

            except (httpx.HTTPStatusError, httpx.RequestError, MCPClientError) as e:
                last_exception = e
                if attempt < self._max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed for {tools_url}, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    # Update health status on final failure
                    error_msg = str(e)
                    if hasattr(e, 'response'):
                        error_msg = f"HTTP {e.response.status_code}: {e.response.text}"

                    self._server_health[server_url] = MCPServerHealth(
                        status=MCPServerHealthStatus.UNHEALTHY,
                        last_check=datetime.now(),
                        error_message=error_msg,
                        consecutive_failures=self._server_health.get(server_url, MCPServerHealth(MCPServerHealthStatus.UNKNOWN, datetime.now())).consecutive_failures + 1
                    )
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error discovering tools from {tools_url}: {e}")
                break

        # If we get here, all retries failed
        if isinstance(last_exception, httpx.HTTPStatusError):
            raise MCPClientError(
                message=f"HTTP error {last_exception.response.status_code} while discovering tools after {self._max_retries} attempts.",
                status_code=last_exception.response.status_code,
                response_content=last_exception.response.text,
                server_url=server_url
            )
        elif isinstance(last_exception, httpx.RequestError):
            raise MCPClientError(
                message=f"Request error while discovering tools after {self._max_retries} attempts: {last_exception}",
                server_url=server_url
            )
        else:
            raise MCPClientError(
                message=f"Failed to discover tools after {self._max_retries} attempts: {last_exception}",
                server_url=server_url
            )

    async def call_tool(
        self,
        server_base_url: HttpUrl,
        tool_id: str,
        parameters: Dict[str, Any]
    ) -> MCPToolCallResponse:
        """
        Calls a specific tool on an external MCP server.
        Args:
            server_base_url: The base URL of the MCP server.
            tool_id: The ID of the tool to call.
            parameters: A dictionary of parameters for the tool.
        Returns:
            An MCPToolCallResponse object.
        Raises:
            MCPClientError: If the request fails or the response is invalid.
        """
        call_url = f"{str(server_base_url).rstrip('/')}/mcp/v1/tools/call"
        request_payload = MCPToolCallRequest(tool_id=tool_id, parameters=parameters)

        try:
            response = await self._client.post(
                call_url,
                json=request_payload.model_dump(), # Use .model_dump() in Pydantic v2
                timeout=self._timeout
            )
            response.raise_for_status()

            response_data = response.json()
            # Assuming the response directly matches MCPToolCallResponse structure
            return MCPToolCallResponse(**response_data)

        except ValidationError as e:
            logger.error(f"Failed to parse tool call response from {call_url}. Error: {e}. Response: {response.text}")
            raise MCPClientError(
                message=f"Invalid response format from tool call: {e}",
                response_content=response.text
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling tool {tool_id} on {call_url}: {e.response.status_code} - {e.response.text}")
            # Attempt to parse error response if possible, as it might contain MCPToolCallResponse with error status
            try:
                error_response_data = e.response.json()
                return MCPToolCallResponse(**error_response_data) # If server returns MCPToolCallResponse on error
            except Exception:
                pass # Fall through to generic MCPClientError
            raise MCPClientError(
                message=f"HTTP error {e.response.status_code} while calling tool.",
                status_code=e.response.status_code,
                response_content=e.response.text
            )
        except httpx.RequestError as e:
            logger.error(f"Request error calling tool {tool_id} on {call_url}: {e}")
            raise MCPClientError(message=f"Request error while calling tool: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling tool {tool_id} on {call_url}: {e}")
            raise MCPClientError(message=f"An unexpected error occurred: {e}")

    async def close(self):
        """Closes the underlying HTTP client. Should be called on application shutdown if client was created by MCPClient."""
        await self._client.aclose()

# Example usage (for illustration, not to be run directly here)
async def main_example():
    # Assume an MCP server is running at http://localhost:9999
    # and exposes the tools defined in our mcp_router.py
    client = MCPClient()
    server_url = HttpUrl("http://localhost:8000") # Point to our own server for testing

    try:
        print(f"Discovering tools from {server_url}...")
        tools = await client.discover_tools(server_url)
        print(f"Discovered {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.tool_id}: {tool.name}")

        if any(t.tool_id == "internal_get_config_value" for t in tools):
            print("\nCalling 'internal_get_config_value' tool...")
            # Example: Get a non-existent key to test error from tool executor
            # config_response = await client.call_tool(server_url, "internal_get_config_value", {"key": "NON_EXISTENT_KEY"})
            # print(f"Tool call response (NON_EXISTENT_KEY): {config_response}")

            # Example: Get an existing key (assuming 'agent_type' is in config)
            # This depends on your actual agent_config structure
            # For this test, let's assume 'default_agent_type' is a valid key in the config dict
            # or an attribute of the agent_config object.
            # You might need to adjust the key based on your actual agent_config.
            # A simple key like 'TEST_CONFIG_KEY' if you add it to agent_config.py
            # For instance, if agent_config.py has: TEST_CONFIG_KEY = "test_value"
            config_response_ok = await client.call_tool(server_url, "internal_get_config_value", {"key": "default_agent_llm"}) # or any valid key
            print(f"Tool call response (default_agent_llm): {config_response_ok}")

        if any(t.tool_id == "internal_specialized_agent_query" for t in tools):
            print("\nCalling 'internal_specialized_agent_query' tool...")
            query_response = await client.call_tool(server_url, "internal_specialized_agent_query", {"query_text": "Hello from MCP Client!"})
            print(f"Tool call response: {query_response}")

    except MCPClientError as e:
        print(f"MCP Client Error: {e.message}")
        if e.status_code:
            print(f"  Status Code: {e.status_code}")
        if e.response_content:
            print(f"  Response: {e.response_content[:200]}...") # Print a snippet
    finally:
        await client.close()

# if __name__ == "__main__":
#     import asyncio
#     # Ensure your FastAPI server (running app.py) is active on http://localhost:8000
#     # and agent.config has a 'default_agent_llm' key/attribute for the test to pass.
#     # Example in agent/config.py:
#     # agent_config = { "default_agent_llm": "gemini-pro" }
#     # OR class AgentConfig: default_agent_llm = "gemini-pro"; agent_config = AgentConfig()
#     asyncio.run(main_example())

