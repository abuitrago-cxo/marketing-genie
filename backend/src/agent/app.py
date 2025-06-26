# mypy: disable - error - code = "no-untyped-def,misc"
print("DEBUG: src.agent.app - Top of file")
import pathlib
import sys
# Add src directory to Python path for correct package imports
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import importlib
from typing import Any # Importar Any
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import fastapi.exceptions
from agent.database import db_manager
from memory import (
    get_short_memory_manager, 
    close_short_memory_manager, 
    get_graphiti_memory_manager, 
    close_graphiti_memory_manager
)
from contextlib import asynccontextmanager

# Define lifespan for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB and memory managers
    await db_manager.initialize()
    await get_short_memory_manager()
    await get_graphiti_memory_manager()
    yield
    # Close DB and memory managers
    await close_graphiti_memory_manager()
    await close_short_memory_manager()
    await db_manager.close()

# Define FastAPI app with lifespan
app = FastAPI(
    title="AI Agent Assistant - Enhanced System",
    description="Comprehensive AI agent system with specialized multi-agent capabilities",
    version="2.0.0",
    lifespan=lifespan,
)

print("DEBUG: src.agent.app - After FastAPI app instantiation")

print("DEBUG: src.agent.app - Before API router import try-except block")
try:
    print("DEBUG: src.agent.app - Attempting to import specialized_endpoints...")
    
    # List of all API modules to load using absolute imports
    api_modules = [
        ('api.specialized_endpoints', 'router', None),
        ('api.enhanced_endpoints', 'enhanced_router', None),
        ('api.system_endpoints', 'router', None),
        ('api.github_endpoints', 'router', None),
        ('api.mcp_registry_endpoints', 'router', None),
        ('api.mcp_router', 'router', None),
        ('api.projects_endpoints', 'projects_router', None),
        ('api.agents_endpoints', 'router', None),
        ('api.research_results_endpoints', 'router', None),
        ('api.chat_endpoints', 'router', None),  # C801: register chat router
        ('api.threads_endpoints', 'router', None),
    ]
    
    # Importar y registrar cada router
    successfully_loaded_routers = []
    failed_routers = []
    
    for module_path, router_name, prefix in api_modules:
        try:
            # Use absolute imports instead of relative imports
            module = importlib.import_module(module_path)
            
            # Obtenemos el router usando el nombre del atributo
            router = getattr(module, router_name)
            
            # Registramos el router con o sin prefijo adicional
            if prefix:
                app.include_router(router, prefix=prefix)
            else:
                app.include_router(router)
                
            successfully_loaded_routers.append(module_path)
            
        except (ImportError, AttributeError) as e:
            failed_routers.append((module_path, str(e)))
    
    if successfully_loaded_routers:
        print(f"✅ Successfully loaded API routers: {', '.join(successfully_loaded_routers)}")
    
    if failed_routers:
        print(f"⚠️ Warning: Failed to load some API routers:")
        for router_path, error in failed_routers:
            print(f"  - {router_path}: {error}")
    else:
        print("✅ All API routers registered successfully")

    print("✅ All API routers registered successfully")

except ImportError as e:
    import traceback
    print(f"⚠️ Warning: Some API routers could not be imported: {e}")
except Exception as e:
    print(f"❌ Error registering API routers: {e}")
print("DEBUG: src.agent.app - After API router import try-except block")


# Add health check endpoint
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Agent Assistant - Enhanced System is running",
        "version": "2.0.0",
        "features": [
            "Real specialized agents system",
            "4-agent multi-agent system",
            "GitHub integration",
            "MCP server management",
            "Enhanced chat interface"
        ]
    }


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "endpoints": {
            "specialized": "/api/v1/specialized",
            "enhanced": "/api/v1/enhanced",
            "github": "/api/v1/github",
            "mcp_registry": "/mcp/registry",
            "mcp_tools": "/mcp/v1",
            "projects": "/api/v1/projects"
        }
    }


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir
    static_files_path = build_path / "assets"  # Vite uses 'assets' subdir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    build_dir = pathlib.Path(build_dir)

    react = FastAPI(openapi_url="")
    react.mount(
        "/assets", StaticFiles(directory=static_files_path), name="static_assets"
    )

    @react.get("/{path:path}")
    async def handle_catch_all(request: Request, path: str):
        fp = build_path / path
        if not fp.exists() or not fp.is_file():
            fp = build_path / "index.html"
        return fastapi.responses.FileResponse(fp)

    return react


# Create a FastAPI sub-application that will be mounted inside /app to handle API requests
# This ensures API routes are accessible both at root level and within /app
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send


class PathRewriteMiddleware(BaseHTTPMiddleware):
    """Middleware to rewrite API paths by removing /app prefix for internal forwarding"""
    
    async def dispatch(self, request: Request, call_next):
        # If request path starts with /app/api, rewrite it to just /api for internal handling
        if request.url.path.startswith('/app/api/'):
            # Store original path for reference
            request.scope['original_path'] = request.url.path
            # Rewrite path by removing /app prefix
            request.scope['path'] = request.url.path.replace('/app/', '/', 1)
        
        # Continue with the request
        response = await call_next(request)
        return response

# Add the path rewrite middleware to the main app
print("DEBUG: src.agent.app - Before app.add_middleware(PathRewriteMiddleware)")
app.add_middleware(PathRewriteMiddleware)
print("DEBUG: src.agent.app - After app.add_middleware(PathRewriteMiddleware)")

# Create the frontend router
print("DEBUG: src.agent.app - Before create_frontend_router() call")
frontend_router = create_frontend_router()
print("DEBUG: src.agent.app - After create_frontend_router() call")

# Mount the frontend under /app
print("DEBUG: src.agent.app - Before app.mount('/app', frontend_router)")
app.mount(
    "/app",
    frontend_router,
    name="frontend",
)
print("DEBUG: src.agent.app - After app.mount('/app', frontend_router)")

# Define a root route handler to redirect to /app
@app.get("/")
async def redirect_to_app():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")
print("DEBUG: src.agent.app - End of file")
