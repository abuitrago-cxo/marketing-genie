from fastapi import APIRouter, Depends, HTTPException, Body, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import inspect # For inspecting function signatures if needed later

# Placeholder for application base URL - should be configured
# This would be the URL where this FastAPI app itself is running.
# For internal calls, we might call functions directly or use TestClient.
# For external representation, this app needs a known base URL.
APP_BASE_URL = "http://localhost:8000" # Example, configure properly

# Import existing routers or service functions to be exposed as tools
# This requires careful consideration of what to expose and how.
# For example, we might wrap calls to specialized_endpoints
# from api.specialized_endpoints import specialized_query # Example import - REMOVED TO FIX CIRCULAR IMPORT
from agent.config import get_system_config # For getting config values as a tool

router = APIRouter(
    prefix="/mcp/v1", # Standard MCP prefix
    tags=["MCP Service (Exposed Tools)"],
)

# --- MCP Tool Definition Models ---
class MCPToolParameter(BaseModel):
    type: str = Field(..., description="Parameter type (e.g., 'string', 'integer', 'boolean', 'object', 'array')")
    description: Optional[str] = None
    required: bool = True
    # For object/array types, could include 'properties' or 'items' for schema
    properties: Optional[Dict[str, Any]] = None # For 'object' type
    items: Optional[Dict[str, Any]] = None      # For 'array' type

class MCPToolInputSchema(BaseModel):
    type: str = Field(default="object", description="Schema type, typically 'object' for multiple params.")
    properties: Dict[str, MCPToolParameter] = Field(..., description="Dictionary of input parameters.")
    required: Optional[List[str]] = None # List of required parameter names

class MCPToolOutputSchema(BaseModel):
    # Define how the output schema should look. For simplicity, can be Dict or a specific model.
    # For now, let's assume it's a generic object or can be more specific per tool.
    type: str = Field(default="object", description="Output schema type.")
    properties: Optional[Dict[str, Any]] = None # Example: {'result': {'type': 'string'}}

class MCPToolDefinition(BaseModel):
    tool_id: str = Field(..., description="Unique identifier for the tool.")
    name: str = Field(..., description="Human-readable name for the tool.")
    description: str = Field(..., description="Detailed description of what the tool does.")
    input_schema: MCPToolInputSchema = Field(..., description="JSON schema for the tool's input parameters.")
    output_schema: MCPToolOutputSchema = Field(..., description="JSON schema for the tool's output.")
    # Potentially add: category, version, tags, etc.

# --- MCP Tool Invocation Models ---
class MCPToolCallRequest(BaseModel):
    tool_id: str = Field(..., description="The ID of the tool to call.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Input parameters for the tool call.")

class MCPToolCallResponse(BaseModel):
    tool_id: str
    status: str = Field(..., description="Status of the tool call (e.g., 'success', 'error')")
    result: Optional[Any] = None # Can be any valid JSON type
    error_message: Optional[str] = None

# --- In-memory Tool Registry for this service ---
# In a more complex scenario, this could also come from a database or dynamic registration.
_INTERNAL_MCP_TOOLS: Dict[str, MCPToolDefinition] = {}
_TOOL_EXECUTORS: Dict[str, callable] = {}

# --- Tool Registration Helper ---
def register_mcp_tool(definition: MCPToolDefinition, executor: callable):
    if definition.tool_id in _INTERNAL_MCP_TOOLS:
        raise ValueError(f"Tool with ID '{definition.tool_id}' already registered.")
    _INTERNAL_MCP_TOOLS[definition.tool_id] = definition
    _TOOL_EXECUTORS[definition.tool_id] = executor

# --- Define and Register Internal Tools ---

# Example Tool 1: Get Configuration Value
async def execute_get_config_value(key: str) -> Dict[str, Any]:
    """Executor for getting a configuration value."""
    try:
        # Get system configuration
        system_config = get_system_config()

        # Try to get the value from system config
        if hasattr(system_config, key):
            value = getattr(system_config, key)
        else:
            # Try environment variable as a fallback
            import os
            value = os.getenv(key.upper())
            if value is None:
                raise KeyError(f"Configuration key '{key}' not found.")

        return {"key": key, "value": str(value)}
    except KeyError as e:
        raise ValueError(str(e)) # Re-raise as ValueError for consistent error handling by caller
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in execute_get_config_value: {e}")
        raise ValueError(f"An unexpected error occurred while fetching config key '{key}'.")

get_config_tool_def = MCPToolDefinition(
    tool_id="internal_get_config_value",
    name="Get Configuration Value",
    description="Retrieves a specific configuration value from the application's settings.",
    input_schema=MCPToolInputSchema(
        properties={
            "key": MCPToolParameter(type="string", description="The configuration key to retrieve.")
        },
        required=["key"]
    ),
    output_schema=MCPToolOutputSchema(properties={"key": {"type": "string"}, "value": {"type": "string"}}) # Value type is simplified
)
register_mcp_tool(get_config_tool_def, execute_get_config_value)

# Example Tool 2: Wrapper for Specialized Query (Illustrative - needs proper async handling and error mapping)
# This is a simplified example. The actual specialized_query might take a Pydantic model.
# We'd need to map MCP params to that model.
async def execute_specialized_agent_query(query_text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Executor for the specialized agent query tool."""
    from api.specialized_endpoints import SpecializedQuery, SpecializedResponse # Local import for clarity
    from fastapi import BackgroundTasks # Required by specialized_query

    request_payload = SpecializedQuery(query=query_text, user_id=user_id, config={}) # Assuming default config
    background_tasks = BackgroundTasks() # Create a new BackgroundTasks instance
    try:
        # Note: specialized_query is an async endpoint function.
        # If calling it directly, ensure it behaves like a regular async function here.
        # If it's meant to be called via HTTP, use httpx.AsyncClient.
        # For direct call:
        response_model: SpecializedResponse = await specialized_query(request_payload, background_tasks)
        # We need to await background tasks if they are critical for the result or have side effects we need to ensure complete.
        # However, specialized_query itself is async and should complete its primary work.
        return response_model.model_dump() # Convert Pydantic model to dict
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in execute_specialized_agent_query: {e}")
        # Potentially map to a more structured error for MCP
        raise ValueError(f"Error executing specialized query: {str(e)}")

specialized_query_tool_def = MCPToolDefinition(
    tool_id="internal_specialized_agent_query",
    name="Specialized Agent Query",
    description="Submits a query to the specialized multi-agent system and returns the result.",
    input_schema=MCPToolInputSchema(
        properties={
            "query_text": MCPToolParameter(type="string", description="The natural language query for the agents."),
            "user_id": MCPToolParameter(type="string", description="Optional user ID for context.", required=False)
        },
        required=["query_text"]
    ),
    output_schema=MCPToolOutputSchema(type="object", properties={ # Define based on SpecializedResponse structure
        "response": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "object"}},
        "query_id": {"type": "string"}
        # Add other fields from SpecializedResponse as needed
    })
)
register_mcp_tool(specialized_query_tool_def, execute_specialized_agent_query)


# --- MCP Endpoints ---
@router.get("/tools", response_model=List[MCPToolDefinition])
async def list_mcp_tools():
    """Lists all available MCP tools provided by this service."""
    return list(_INTERNAL_MCP_TOOLS.values())

@router.post("/tools/call", response_model=MCPToolCallResponse)
async def call_mcp_tool(request: MCPToolCallRequest = Body(...)):
    """Calls a specific MCP tool with the given parameters."""
    tool_id = request.tool_id
    if tool_id not in _INTERNAL_MCP_TOOLS or tool_id not in _TOOL_EXECUTORS:
        raise HTTPException(status_code=404, detail=f"Tool with ID '{tool_id}' not found.")

    executor = _TOOL_EXECUTORS[tool_id]
    tool_def = _INTERNAL_MCP_TOOLS[tool_id]

    # Validate parameters against input_schema (basic validation)
    validated_params = {}
    input_props = tool_def.input_schema.properties
    for param_name, param_def in input_props.items():
        if param_def.required and param_name not in request.parameters:
            raise HTTPException(status_code=400, detail=f"Missing required parameter: '{param_name}' for tool '{tool_id}'.")
        if param_name in request.parameters:
            # Further type validation could be added here if Pydantic models aren't used directly for execution
            validated_params[param_name] = request.parameters[param_name]
        elif not param_def.required:
            validated_params[param_name] = None # Or some default if specified in schema

    # For more robust validation, consider dynamically creating a Pydantic model from input_schema
    # and validating request.parameters against it.

    try:
        # Inspect executor signature to pass parameters correctly
        sig = inspect.signature(executor)
        tool_params = {}
        for p_name, p_obj in sig.parameters.items():
            if p_name in validated_params:
                tool_params[p_name] = validated_params[p_name]
            elif p_obj.default is inspect.Parameter.empty: # Required by function but not provided after validation (should not happen if schema is correct)
                 if p_name in tool_def.input_schema.required: # Check against our schema's required list
                    raise HTTPException(status_code=500, detail=f"Internal error: Mismatch between tool schema and executor signature for '{p_name}'.")

        # Execute the tool
        result = await executor(**tool_params)
        return MCPToolCallResponse(tool_id=tool_id, status="success", result=result)

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except ValueError as ve: # Expected errors from tool executors
        return MCPToolCallResponse(tool_id=tool_id, status="error", error_message=str(ve))
    except Exception as e:
        # Log the full error for debugging
        print(f"Unhandled error calling tool '{tool_id}': {e}")
        # Return a generic error response
        return MCPToolCallResponse(
            tool_id=tool_id,
            status="error",
            error_message=f"An unexpected error occurred: {str(e)}"
        )
