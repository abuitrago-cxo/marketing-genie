import sys
import os

# Get the absolute path of the current script (app.py)
# e.g., /path/to/your/project/backend/src/agent/app.py
current_script_path = os.path.abspath(__file__)

# Get the directory containing app.py (the 'agent' directory)
# e.g., /path/to/your/project/backend/src/agent
agent_dir = os.path.dirname(current_script_path)

# Get the directory containing the 'agent' directory (the 'src' directory)
# e.g., /path/to/your/project/backend/src
src_dir = os.path.dirname(agent_dir)

# Add the 'src' directory to the beginning of sys.path
# This allows Python to find packages like 'agent' directly from 'src'
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

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
