from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks

# Assuming db_manager and mcp_registry_repository are initialized and accessible
# This might require adjustment based on your project's structure for dependency injection
# For now, let's assume they can be imported directly or handled by a dependency injection system
from agent.database import mcp_registry_repository, MCPRegistryEntry, db_manager # Import db_manager for lifecycle
from agent.mcp_client import MCPServerAuth, AuthType, MCPServerHealth, MCPServerHealthStatus
from agent.dynamic_mcp_tools import load_dynamic_mcp_tools, MCPToolConflictResolution

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/mcp/registry",
    tags=["MCP Server Registry"],
)

# Enhanced Pydantic Models for MCP Server Management
class MCPAuthTypeEnum(str, Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"

class MCPServerInstallationStatus(str, Enum):
    PENDING = "pending"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    UNINSTALLING = "uninstalling"

class MCPServerAuthConfig(BaseModel):
    auth_type: MCPAuthTypeEnum = MCPAuthTypeEnum.NONE
    api_key: Optional[str] = None
    api_key_header: str = "X-API-Key"
    bearer_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class MCPServerBase(BaseModel):
    name: str
    base_url: HttpUrl
    description: Optional[str] = None
    enabled: bool = True
    auth_config: Optional[MCPServerAuthConfig] = None
    health_check_interval: int = Field(default=300, ge=60, le=3600)
    max_retries: int = Field(default=3, ge=1, le=10)
    timeout_seconds: float = Field(default=30.0, ge=5.0, le=120.0)

class MCPServerCreate(MCPServerBase):
    pass

class MCPServerUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    auth_config: Optional[MCPServerAuthConfig] = None
    health_check_interval: Optional[int] = Field(default=None, ge=60, le=3600)
    max_retries: Optional[int] = Field(default=None, ge=1, le=10)
    timeout_seconds: Optional[float] = Field(default=None, ge=5.0, le=120.0)

class MCPServerHealthResponse(BaseModel):
    status: str
    last_check: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    consecutive_failures: int = 0

class MCPServerResponse(MCPServerBase):
    id: int
    last_checked_at: Optional[datetime] = None
    last_known_status: Optional[str] = None
    available_tools_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    installation_status: Optional[str] = None
    health: Optional[MCPServerHealthResponse] = None

    class Config:
        from_attributes = True  # Updated for Pydantic v2

class MCPServerStatusUpdate(BaseModel):
    last_known_status: str
    available_tools_json: Optional[Dict[str, Any]] = None

class MCPServerInstallRequest(BaseModel):
    name: str
    source_url: HttpUrl  # GitHub repo, npm package, etc.
    source_type: str = Field(default="github", pattern="^(github|npm|local|url)$")
    description: Optional[str] = None
    auth_config: Optional[MCPServerAuthConfig] = None
    auto_enable: bool = True

class MCPToolDiscoveryResponse(BaseModel):
    server_id: int
    server_name: str
    tools: List[Dict[str, Any]]
    discovery_time: datetime
    status: str

# Dependency to ensure database is initialized (if not handled globally)
# This is a placeholder; actual DB initialization should be in app startup/lifespan events
async def get_db_mngr(): # Simple dependency, replace with your actual DB session management if needed
    if not db_manager._initialized:
        # In a real app, this should be handled by FastAPI's lifespan events
        # or a more robust dependency injection system.
        # For this context, we'll assume it's initialized elsewhere or raise an error.
        # await db_manager.initialize() # Avoid calling initialize here directly in endpoint logic
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager

@router.post("/servers/", response_model=MCPServerResponse, status_code=201)
async def create_mcp_server(server_data: MCPServerCreate, _dbm = Depends(get_db_mngr)):
    existing_by_name = await mcp_registry_repository.get_server_by_name(server_data.name)
    if existing_by_name:
        raise HTTPException(status_code=400, detail=f"Server with name '{server_data.name}' already exists.")

    existing_by_url = await mcp_registry_repository.get_server_by_url(str(server_data.base_url))
    if existing_by_url:
        raise HTTPException(status_code=400, detail=f"Server with base_url '{server_data.base_url}' already exists.")

    entry = MCPRegistryEntry(**server_data.model_dump())
    server_id = await mcp_registry_repository.create_server(entry)
    created_server = await mcp_registry_repository.get_server_by_id(server_id)
    if not created_server:
        raise HTTPException(status_code=500, detail="Failed to create MCP server entry after insert.")
    return created_server

@router.get("/servers/", response_model=List[MCPServerResponse])
async def list_mcp_servers(
    enabled_only: bool = Query(True, description="Filter by enabled status"),
    limit: int = Query(100, ge=1, le=1000, description="Number of servers to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    _dbm = Depends(get_db_mngr)
):
    servers = await mcp_registry_repository.list_servers(enabled_only=enabled_only, limit=limit, offset=offset)
    return servers

@router.get("/servers/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(server_id: int, _dbm = Depends(get_db_mngr)):
    server = await mcp_registry_repository.get_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")
    return server

@router.put("/servers/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(server_id: int, server_data: MCPServerUpdate, _dbm = Depends(get_db_mngr)):
    existing_server = await mcp_registry_repository.get_server_by_id(server_id)
    if not existing_server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    update_payload = server_data.model_dump(exclude_unset=True)
    if not update_payload:
        raise HTTPException(status_code=400, detail="No update data provided.")

    # Check for name/URL conflicts if they are being updated
    if 'name' in update_payload and update_payload['name'] != existing_server.name:
        conflict_name = await mcp_registry_repository.get_server_by_name(update_payload['name'])
        if conflict_name and conflict_name.id != server_id:
            raise HTTPException(status_code=400, detail=f"Server with name '{update_payload['name']}' already exists.")

    if 'base_url' in update_payload and str(update_payload['base_url']) != str(existing_server.base_url):
        conflict_url = await mcp_registry_repository.get_server_by_url(str(update_payload['base_url']))
        if conflict_url and conflict_url.id != server_id:
            raise HTTPException(status_code=400, detail=f"Server with base_url '{update_payload['base_url']}' already exists.")

    success = await mcp_registry_repository.update_server(server_id, update_payload)
    if not success:
        # This might happen if the row doesn't exist or if the update_data was empty after filtering
        # but we check for empty update_payload earlier.
        raise HTTPException(status_code=500, detail="Failed to update MCP server. Ensure server exists and data is valid.")

    updated_server = await mcp_registry_repository.get_server_by_id(server_id)
    if not updated_server:
         raise HTTPException(status_code=404, detail="MCP Server not found after update.") # Should not happen if update was successful
    return updated_server

@router.delete("/servers/{server_id}", status_code=204)
async def delete_mcp_server(server_id: int, _dbm = Depends(get_db_mngr)):
    existing_server = await mcp_registry_repository.get_server_by_id(server_id)
    if not existing_server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    success = await mcp_registry_repository.delete_server(server_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete MCP server.")
    return None # No content response

@router.put("/servers/{server_id}/status", response_model=MCPServerResponse)
async def update_mcp_server_status_and_tools(
    server_id: int,
    status_update: MCPServerStatusUpdate,
    _dbm = Depends(get_db_mngr)
):
    existing_server = await mcp_registry_repository.get_server_by_id(server_id)
    if not existing_server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    success = await mcp_registry_repository.update_server_status(
        server_id,
        status_update.last_known_status,
        status_update.available_tools_json
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update MCP server status.")

    updated_server = await mcp_registry_repository.get_server_by_id(server_id)
    if not updated_server:
         raise HTTPException(status_code=404, detail="MCP Server not found after status update.")
    return updated_server

# Enhanced endpoints for MCP server management

@router.get("/servers/{server_id}/health", response_model=MCPServerHealthResponse)
async def check_server_health(server_id: int, _dbm = Depends(get_db_mngr)):
    """Check the health status of a specific MCP server"""
    server = await mcp_registry_repository.get_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    if not db_manager.mcp_client:
        raise HTTPException(status_code=503, detail="MCP Client not available.")

    try:
        from pydantic import HttpUrl
        server_url = HttpUrl(server.base_url)
        health = await db_manager.mcp_client.check_server_health(server_url)

        return MCPServerHealthResponse(
            status=health.status.value,
            last_check=health.last_check,
            response_time_ms=health.response_time_ms,
            error_message=health.error_message,
            consecutive_failures=health.consecutive_failures
        )
    except Exception as e:
        logger.error(f"Failed to check health for server {server_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/servers/{server_id}/discover-tools", response_model=MCPToolDiscoveryResponse)
async def discover_server_tools(server_id: int, _dbm = Depends(get_db_mngr)):
    """Discover available tools from a specific MCP server"""
    server = await mcp_registry_repository.get_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    if not db_manager.mcp_client:
        raise HTTPException(status_code=503, detail="MCP Client not available.")

    try:
        from pydantic import HttpUrl
        server_url = HttpUrl(server.base_url)

        # Set up authentication if configured
        if server.auth_config:
            from agent.mcp_client import MCPServerAuth, AuthType
            auth = MCPServerAuth(
                auth_type=AuthType(server.auth_config.get('auth_type', 'none')),
                api_key=server.auth_config.get('api_key'),
                api_key_header=server.auth_config.get('api_key_header', 'X-API-Key'),
                bearer_token=server.auth_config.get('bearer_token'),
                username=server.auth_config.get('username'),
                password=server.auth_config.get('password')
            )
            tools = await db_manager.mcp_client.discover_tools(server_url, auth)
        else:
            tools = await db_manager.mcp_client.discover_tools(server_url)

        # Convert tools to dict format
        tools_data = [
            {
                "tool_id": tool.tool_id,
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema.model_dump() if tool.input_schema else None,
                "output_schema": tool.output_schema.model_dump() if tool.output_schema else None
            }
            for tool in tools
        ]

        # Update server with discovered tools
        await mcp_registry_repository.update_server_status(
            server_id,
            "healthy",
            {"tools": tools_data, "tool_count": len(tools_data)}
        )

        return MCPToolDiscoveryResponse(
            server_id=server_id,
            server_name=server.name,
            tools=tools_data,
            discovery_time=datetime.now(),
            status="success"
        )

    except Exception as e:
        logger.error(f"Failed to discover tools for server {server_id}: {e}")
        # Update server status to indicate failure
        await mcp_registry_repository.update_server_status(
            server_id,
            "unhealthy",
            {"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Tool discovery failed: {str(e)}")

@router.post("/servers/{server_id}/test-connection")
async def test_server_connection(server_id: int, _dbm = Depends(get_db_mngr)):
    """Test connection to an MCP server"""
    server = await mcp_registry_repository.get_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="MCP Server not found.")

    if not db_manager.mcp_client:
        raise HTTPException(status_code=503, detail="MCP Client not available.")

    try:
        from pydantic import HttpUrl
        server_url = HttpUrl(server.base_url)

        # Check health and discover tools
        health = await db_manager.mcp_client.check_server_health(server_url)

        if health.status == MCPServerHealthStatus.HEALTHY:
            # Try to discover tools as well
            tools = await db_manager.mcp_client.discover_tools(server_url)
            return {
                "status": "success",
                "health": {
                    "status": health.status.value,
                    "response_time_ms": health.response_time_ms
                },
                "tools_discovered": len(tools),
                "message": f"Successfully connected to {server.name}. Discovered {len(tools)} tools."
            }
        else:
            return {
                "status": "failed",
                "health": {
                    "status": health.status.value,
                    "error": health.error_message
                },
                "message": f"Failed to connect to {server.name}: {health.error_message}"
            }

    except Exception as e:
        logger.error(f"Connection test failed for server {server_id}: {e}")
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}"
        }

@router.post("/servers/install", response_model=MCPServerResponse, status_code=201)
async def install_mcp_server(install_request: MCPServerInstallRequest, background_tasks: BackgroundTasks, _dbm = Depends(get_db_mngr)):
    """Install an MCP server from various sources (GitHub, npm, etc.)"""
    # Check if server already exists
    existing_by_name = await mcp_registry_repository.get_server_by_name(install_request.name)
    if existing_by_name:
        raise HTTPException(status_code=400, detail=f"Server with name '{install_request.name}' already exists.")

    # Create server entry with installation status
    server_data = MCPServerCreate(
        name=install_request.name,
        base_url=install_request.source_url,  # This will be updated after installation
        description=install_request.description,
        enabled=False,  # Start disabled until installation completes
        auth_config=install_request.auth_config
    )

    entry = MCPRegistryEntry(**server_data.model_dump())
    entry.installation_status = MCPServerInstallationStatus.PENDING.value

    server_id = await mcp_registry_repository.create_server(entry)

    # Start background installation task
    background_tasks.add_task(
        _install_server_background,
        server_id,
        install_request
    )

    created_server = await mcp_registry_repository.get_server_by_id(server_id)
    if not created_server:
        raise HTTPException(status_code=500, detail="Failed to create MCP server entry after insert.")

    return created_server

async def _install_server_background(server_id: int, install_request: MCPServerInstallRequest):
    """Background task for MCP server installation"""
    try:
        logger.info(f"Starting installation of MCP server {install_request.name} from {install_request.source_url}")

        # Update status to installing
        await mcp_registry_repository.update_server_status(
            server_id,
            "installing",
            {"installation_progress": "Starting installation..."}
        )

        # Simulate installation process (in real implementation, this would:
        # 1. Clone/download from source
        # 2. Install dependencies
        # 3. Configure server
        # 4. Start server process
        # 5. Validate server is running

        import asyncio
        await asyncio.sleep(2)  # Simulate installation time

        # For now, we'll assume the source_url is the actual server URL
        # In a real implementation, this would be the discovered server URL after installation

        # Test connection to verify installation
        if db_manager.mcp_client:
            health = await db_manager.mcp_client.check_server_health(install_request.source_url)

            if health.status == MCPServerHealthStatus.HEALTHY:
                # Installation successful
                await mcp_registry_repository.update_server_status(
                    server_id,
                    "installed",
                    {"installation_completed": datetime.now().isoformat()}
                )

                # Enable server if auto_enable is True
                if install_request.auto_enable:
                    server = await mcp_registry_repository.get_server_by_id(server_id)
                    if server:
                        server.enabled = True
                        # Update server (this would need to be implemented in the repository)

                logger.info(f"Successfully installed MCP server {install_request.name}")
            else:
                # Installation failed - server not responding
                await mcp_registry_repository.update_server_status(
                    server_id,
                    "failed",
                    {"error": f"Server not responding after installation: {health.error_message}"}
                )
                logger.error(f"MCP server {install_request.name} installation failed: server not responding")
        else:
            # No MCP client available
            await mcp_registry_repository.update_server_status(
                server_id,
                "failed",
                {"error": "MCP client not available for validation"}
            )
            logger.error(f"MCP server {install_request.name} installation failed: no MCP client")

    except Exception as e:
        logger.error(f"Failed to install MCP server {install_request.name}: {e}")
        await mcp_registry_repository.update_server_status(
            server_id,
            "failed",
            {"error": str(e)}
        )
