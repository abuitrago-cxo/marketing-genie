import asyncio
import os
import sys
from pathlib import Path
import json

# Configuración robusta de Python Path para manejar ambos estilos de importación
# - Para ejecución local: añadimos 'backend/src' para importaciones directas como 'from agent.app'
# - Para compatibilidad con Docker: añadimos 'backend' para importaciones con prefijo como 'from src.agent.app'

# Primero añadimos backend/src para importaciones directas
src_dir = Path(__file__).resolve().parent.parent / "src"  # Points to backend/src
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
    
# Luego añadimos backend para importaciones con prefijo src.
backend_dir = Path(__file__).resolve().parent.parent  # Points to backend
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

print(f"Attempting to run with src_dir in sys.path: {src_dir}")
print(f"Current sys.path: {sys.path}")

# Set environment variables that might be expected by the app
# Adjust these to your local setup or comment out if not needed for basic testing
os.environ["POSTGRES_USER"] = os.environ.get("POSTGRES_USER", "user")
os.environ["POSTGRES_PASSWORD"] = os.environ.get("POSTGRES_PASSWORD", "password")
os.environ["POSTGRES_DB"] = os.environ.get("POSTGRES_DB", "agent_db")
os.environ["POSTGRES_HOST"] = os.environ.get("POSTGRES_HOST", "localhost")
os.environ["POSTGRES_PORT"] = os.environ.get("POSTGRES_PORT", "5432")
os.environ["REDIS_HOST"] = os.environ.get("REDIS_HOST", "localhost")
os.environ["REDIS_PORT"] = os.environ.get("REDIS_PORT", "6379")

# Import httpx for making API calls
import httpx

API_BASE_URL = "http://localhost:8123" # Puerto 8123 como se indica en docker-compose.yml

async def run_chat_tests():
    """Runs a series of tests against the chat API endpoints."""
    print("\n--- Running Chat API Tests ---")
    async with httpx.AsyncClient(base_url=API_BASE_URL, follow_redirects=True) as client:
        thread_id = None
        try:
            # 1. Create a new thread
            print("\n1. Creating a new thread...")
            # Intentamos primero con la ruta directa y luego con prefijo /api/v1 según la configuración de router
            try:
                print("   Sending request to /threads/...")
                response = await client.post("/threads/", json={"title": "Test Thread"})
                print(f"   Status code: {response.status_code}")
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"   Direct route failed with status {e.response.status_code}, trying with /api/v1 prefix...")
                response = await client.post("/api/v1/threads/", json={"title": "Test Thread"})
                print(f"   Status code with prefix: {response.status_code}")
                response.raise_for_status() # Raise an exception for bad status codes
            
            # Imprimir la respuesta completa para diagnóstico
            print(f"   Raw response: {response.text}")
            
            thread_data = response.json()
            # La API devuelve thread_id en lugar de id
            thread_id = thread_data.get("thread_id") or thread_data.get("id")
            print(f"   Thread created successfully: ID = {thread_id}")
            print(f"   Full thread data: {thread_data}")

            if not thread_id:
                print("   ERROR: Failed to create thread or get thread ID.")
                return

            # 2. Post a user message to the thread
            print(f"\n2. Posting a message to thread {thread_id}...")
            user_message_content = "Hello AI, how are you today?"
            message_payload = {"content": user_message_content, "role": "user"}
            response = await client.post(f"/threads/{thread_id}/messages", json=message_payload)
            response.raise_for_status()
            sent_message_data = response.json()
            print(f"   User message sent: ID = {sent_message_data.get('id')}, Content = '{sent_message_data.get('content')}'")

            # 3. Wait a moment for potential asynchronous AI processing
            print("\n3. Waiting for 5 seconds for potential AI response...")
            await asyncio.sleep(5)

            # 4. Get all messages for the thread
            print(f"\n4. Retrieving all messages for thread {thread_id}...")
            response = await client.get(f"/threads/{thread_id}/messages")
            response.raise_for_status()
            messages = response.json()
            
            print(f"   Messages in thread {thread_id}:")
            if messages:
                for msg in messages:
                    print(f"     - [{msg.get('role')}] {msg.get('content')} (ID: {msg.get('id')}, Created: {msg.get('created_at')})")
            else:
                print("     No messages found in the thread.")

            # 5. Analyze results - Check for AI response
            print("\n5. Analyzing results...")
            ai_responses = [msg for msg in messages if msg.get('role') != 'user' and msg.get('content') != user_message_content]
            if ai_responses:
                print("   SUCCESS: AI responded.")
                for resp in ai_responses:
                    print(f"     AI Response: [{resp.get('role')}] {resp.get('content')}")
            else:
                print("   INFO: No distinct AI response detected in the thread messages.")
                print("         This might indicate that the AI agent logic is not yet fully integrated")
                print("         with the '/threads/{thread_id}/messages' endpoint or operates differently.")

            # Placeholder for more advanced tests (memory, tool usage)
            print("\n--- Placeholder for Advanced Chat Tests ---")
            print("   Future tests could include:")
            print("     - Testing conversation memory (e.g., AI remembering user's name).")
            print("     - Testing tool invocation (e.g., asking for weather or a web search).")
            print("     These depend on the AI agent being fully connected to these endpoints.")

        except httpx.HTTPStatusError as e:
            print(f"   ERROR: HTTP Error occurred: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"   ERROR: Request failed: {e}")
        except Exception as e:
            print(f"   ERROR: An unexpected error occurred: {e}")
        finally:
            print("\n--- Chat API Tests Finished ---")

async def main():
    # You can add other test suites here if needed
    await run_chat_tests()

if __name__ == "__main__":
    print("Starting local backend test script...")
    # This script is intended to be run when the FastAPI backend is already running.
    # Example: Run 'bash scripts/startup.sh' in one terminal, then run this script in another.
    asyncio.run(main())
os.environ["REDIS_HOST"] = os.environ.get("REDIS_HOST", "localhost")
os.environ["REDIS_PORT"] = os.environ.get("REDIS_PORT", "6379")
os.environ["DATABASE_URL"] = f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
os.environ["REDIS_URL"] = f"redis://{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}/0"

# Add any other LLM API keys or configurations if your agent needs them for basic startup
# For example, if your agent initialization depends on these:
# os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_KEY_HERE" # Replace with your actual key if needed
# os.environ["LANGCHAIN_API_KEY"] = "YOUR_LANGCHAIN_KEY_HERE"
# os.environ["TAVILY_API_KEY"] = "YOUR_TAVILY_KEY_HERE"

# Mock any services that are problematic for local testing if necessary
# For example, if agent_router initialization is problematic:
# from unittest.mock import patch
# mock_agent_router = patch('agent.router.agent_router') # Adjust path as needed
# mock_agent_router.start()
# print("Mocked agent_router")


try:
    print("Attempting to import TestClient...")
    from fastapi.testclient import TestClient
    print("TestClient imported successfully.")

    print("Attempting to import agent.app...")
    try:
        # Ensure that the app is imported after sys.path is modified
        from agent.app import app # Assuming 'app' is the FastAPI instance
        print("agent.app imported successfully.")
    except ImportError as e:
        print(f"ImportError for agent.app: {e}")
        app = None
    except SystemExit as e:
        print(f"SystemExit during import of agent.app: {e}")
        app = None
        sys.exit(1)
    except BaseException as e:
        print(f"VERY UNEXPECTED EXCEPTION during import of agent.app: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        app = None
        sys.exit(1)

except ImportError as e:
    print(f"❌ Caught ImportError during main imports: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except SystemExit as e:
    print(f"❌ Caught SystemExit during main imports: {e}")
    import traceback
    traceback.print_exc()
    # Potentially re-raise or handle, but for debugging, printing is key
    sys.exit(1) # Or sys.exit(e.code)
except BaseException as e: # Catch everything else
    print(f"❌ Caught BaseException during main imports: {type(e).__name__} - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if app:
    client = TestClient(app)

    def run_query(question: str, agent_type: str = "Specialized", thread_id: str = "local_test_thread_01"):
        """Sends a query to the specified agent endpoint."""
        print(f"\n--- Sending query: '{question}' to agent: {agent_type} (Thread: {thread_id}) ---")
        payload = {
            "input": question,
            # "agent_type": agent_type, # This might vary based on your actual API payload for specialized query
            # "thread_id": thread_id,
            "query": question, # Based on SpecializedQuery model
            "max_research_iterations": 3,
            "enable_tracing": True,
            "user_id": "local_test_user",
            "session_id": thread_id,
            "use_multi_agent": False, # Or True, depending on what you want to test
            "use_real_agents": True
        }
        response = client.post("/api/v1/specialized/query", json=payload)

        print(f"Status Code: {response.status_code}")
        try:
            response_json = response.json()
            print("Response JSON:")
            print(json.dumps(response_json, indent=2))
        except json.JSONDecodeError:
            print("Response is not valid JSON.")
            print(f"Response Text: {response.text}")
        except Exception as e:
            print(f"Could not parse or handle JSON response: {e}")
            print(f"Response Text: {response.text}")
        return response

    async def main():
        print("🚀 Starting local backend test script...")

        # Test basic health check if available
        print("\n--- Testing /health endpoint ---")
        try:
            health_response = client.get("/health") # Standard health check
            print(f"Health Status Code: {health_response.status_code}")
            print(f"Health Response: {health_response.json()}")

            api_health_response = client.get("/api/health") # Your custom health check
            print(f"API Health Status Code: {api_health_response.status_code}")
            print(f"API Health Response: {api_health_response.json()}")

        except Exception as e:
            print(f"Error during health check: {e}")

        # 1. Send "hello"
        run_query("Hello, how are you today?", thread_id="local_test_hello")

        # 2. First question
        run_query("What is LangGraph?", thread_id="local_test_q1")

        # 3. Second question
        run_query("Can you explain the RAG pattern in simple terms?", thread_id="local_test_q2")

        # 4. Third question
        run_query("Tell me a fun fact about Large Language Models.", thread_id="local_test_q3")

        # 5. Fourth question
        run_query("What are the key components of this application's backend?", thread_id="local_test_q4")

        print("\n✅ Test script finished.")

    if __name__ == "__main__":
        # Using asyncio.run() is good practice for async main,
        # TestClient handles the event loop for its requests.
        asyncio.run(main())
