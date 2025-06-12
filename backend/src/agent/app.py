# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

from agent.configuration import Configuration
from langchain_core.runnables import RunnableConfig # For type hinting or if we pass None

# Define the FastAPI app
app = FastAPI()


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

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

    return StaticFiles(directory=build_path, html=True)


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)


@app.get("/agent/config-defaults", response_model_exclude_none=True)
async def get_config_defaults():
    """
    Returns the default agent configuration based on environment variables
    and Pydantic model defaults. This represents the configuration the agent
    would use if no specific runtime configuration is provided for a request.
    """
    # Pass an empty 'configurable' dict to from_runnable_config.
    # This ensures that only environment variables and Pydantic defaults are used.
    # If None is passed, it defaults to an empty dict anyway.
    run_config_for_defaults: RunnableConfig = {"configurable": {}}
    default_config = Configuration.from_runnable_config(run_config_for_defaults)

    # model_dump() is Pydantic v2, dict() was for v1.
    # response_model_exclude_none=True in @app.get will handle not sending None values.
    return default_config.model_dump()
