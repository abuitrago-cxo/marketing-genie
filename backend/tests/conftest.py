import sys
import pathlib
import sys

# Ensure backend/src is on Python path for imports
root = pathlib.Path(__file__).parent.parent
# Add backend and backend/src to sys.path for both 'src' and package-root imports
sys.path.insert(0, str(root))            # project_root/backend
sys.path.insert(0, str(root / "src"))  # project_root/backend/src

# Monkey-patch httpx.AsyncClient to accept ASGI app for FastAPI testing
import httpx
from httpx import ASGITransport as _ASGITransport, AsyncClient as _OriginalAsyncClient

class AsyncClient(_OriginalAsyncClient):
    def __init__(self, *args, app=None, **kwargs):
        if app is not None:
            transport = kwargs.pop('transport', None) or _ASGITransport(app=app)
            kwargs['transport'] = transport
        super().__init__(*args, **kwargs)

# Override httpx.AsyncClient
httpx.AsyncClient = AsyncClient
