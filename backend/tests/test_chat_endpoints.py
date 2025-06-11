import pytest
from httpx import AsyncClient
from agent.app import app
from agent.database import db_manager

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    # Initialize and clear DB before tests
    await db_manager.initialize()
    async with db_manager.get_postgres_connection() as conn:
        await conn.execute("TRUNCATE chat_messages CASCADE")
        await conn.execute("TRUNCATE chat_threads CASCADE")
    yield
    await db_manager.close()

@pytest.mark.asyncio
async def test_chat_flow_and_get_messages():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Start new conversation
        post_resp = await client.post("/chat/", json={"content": "Hello"})
        assert post_resp.status_code == 200
        ai_msg = post_resp.json()
        assert "id" in ai_msg and "thread_id" in ai_msg
        thread_id = ai_msg["thread_id"]
        # Should have assistant role
        assert ai_msg["role"] == "assistant"
        # Retrieve full conversation
        get_resp = await client.get(f"/chat/{thread_id}")
        assert get_resp.status_code == 200
        msgs = get_resp.json()
        # Expect 2 messages: user + assistant
        assert len(msgs) == 2
        roles = [m["role"] for m in msgs]
        assert roles == ["user", "assistant"]

@pytest.mark.asyncio
async def test_get_unknown_thread():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/chat/invalid-thread-id")
        assert resp.status_code == 404
