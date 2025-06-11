import pathlib
import os
import pytest
from dotenv import load_dotenv
import asyncio
from fastapi.testclient import TestClient
from agent.app import app
from agent.database import db_manager

# Load .env for POSTGRES_URI
env_path = pathlib.Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Skip if no Postgres URI
if not os.getenv('POSTGRES_URI'):
    pytest.skip("POSTGRES_URI not set, skipping integration tests", allow_module_level=True)

async def clear_tables():
    async with db_manager.get_postgres_connection() as conn:
        await conn.execute("TRUNCATE chat_messages CASCADE")
        await conn.execute("TRUNCATE chat_threads CASCADE")


def test_chat_ws_streaming_tokens_and_end():
    # Initialize DB pool
    asyncio.run(db_manager.initialize())

    with TestClient(app) as client:
        # Clear tables with initialized pool
        asyncio.run(clear_tables())

        # WebSocket interaction
        with client.websocket_connect("/chat/ws") as ws:
            ws.send_json({"content": "Hello WebSocket"})
            collected = ""
            thread_id = None
            while True:
                msg = ws.receive_json()
                assert "type" in msg
                if msg["type"] == "token":
                    collected += msg.get("data", "")
                elif msg["type"] == "end":
                    thread_id = msg.get("thread_id")
                    break
            assert collected, "No tokens received"
            assert thread_id, "No thread_id received"

        # Verify messages persisted via REST
        resp = client.get(f"/chat/{thread_id}")
        assert resp.status_code == 200
        msgs = resp.json()
        assert len(msgs) == 2
        assert [m.get("role") for m in msgs] == ["user", "assistant"]

    # Close DB pool
    asyncio.run(db_manager.close())
