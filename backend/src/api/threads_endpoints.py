from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, List, Optional
from uuid import uuid4
from datetime import datetime
import logging
from src.agent.database import db_manager, DatabaseManager
from src.api.chat_endpoints import ensure_datetime, format_datetime_for_json

# Dependency to get DatabaseManager
def get_db_manager() -> DatabaseManager:
    return db_manager

from src.agent.graph import get_agent_executor
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

router = APIRouter(prefix="/threads", tags=["threads"])

class ThreadCreateRequest(BaseModel):
    title: Optional[str] = None

class ThreadResponse(BaseModel):
    id: str
    title: Optional[str] = None
    created_at: str

class MessageCreateRequest(BaseModel):
    content: str
    role: str = "user"

class MessageResponse(BaseModel):
    id: str
    thread_id: str
    content: str
    role: str
    created_at: str

@router.post("/", response_model=ThreadResponse)
async def create_thread(req: ThreadCreateRequest, db: DatabaseManager = Depends(get_db_manager)):
    thread_id = str(uuid4())
    now = ensure_datetime(datetime.utcnow())  # Usar objeto datetime
    now_str = format_datetime_for_json(now)  # Solo para respuesta JSON
    async with db.get_postgres_connection() as conn:
        await conn.execute(
            "INSERT INTO chat_threads(id, created_at) VALUES($1, $2)",
            thread_id, now)
    return {"id": thread_id, "title": req.title, "created_at": now_str}

@router.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str, db: DatabaseManager = Depends(get_db_manager)):
    async with db.get_postgres_connection() as conn:
        row = await conn.fetchrow(
            "SELECT id, created_at FROM chat_threads WHERE id=$1", thread_id)
    if not row:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"id": row["id"], "title": None, "created_at": row["created_at"].isoformat()}

@router.post("/{thread_id}/messages", response_model=MessageResponse)
async def post_message(thread_id: str, req: MessageCreateRequest, db: DatabaseManager = Depends(get_db_manager)):
    # Create a logger for this function
    logger = logging.getLogger("threads_endpoints.post_message")
    logger.setLevel(logging.DEBUG)
    
    try:
        # Check if thread exists
        async with db.get_postgres_connection() as conn:
            exists = await conn.fetchval(
                "SELECT 1 FROM chat_threads WHERE id=$1", thread_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Thread not found")
            
        # Generate message ID and timestamp
        msg_id = str(uuid4())
        now = ensure_datetime(datetime.utcnow())  
        now_str = format_datetime_for_json(now)  
        
        # Insert user message into database
        try:
            async with db.get_postgres_connection() as conn:
                await conn.execute(
                    "INSERT INTO chat_messages(id, thread_id, content, role, created_at) VALUES($1,$2,$3,$4,$5)",
                    msg_id, thread_id, req.content, req.role, now)
            logger.debug(f"User message successfully inserted with ID: {msg_id}")
        except Exception as db_error:
            logger.error(f"Database error inserting user message: {str(db_error)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")

        # Retrieve and prepare messages for the agent
        messages_for_agent: List[BaseMessage] = []
        try:
            async with db.get_postgres_connection() as conn:
                rows = await conn.fetch(
                    "SELECT content, role FROM chat_messages WHERE thread_id=$1 ORDER BY created_at", thread_id)
                
            for content, role in [(r["content"], r["role"]) for r in rows]:
                if role == "user":
                    messages_for_agent.append(HumanMessage(content=content))
                else:
                    messages_for_agent.append(AIMessage(content=content))
                    
            logger.debug(f"Retrieved {len(messages_for_agent)} messages for agent")
        except Exception as fetch_error:
            logger.error(f"Error fetching thread messages: {str(fetch_error)}")
            raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(fetch_error)}")

        # Get agent executor
        try:
            agent_executor = get_agent_executor()
            logger.debug("Successfully retrieved agent executor")
        except Exception as exec_error:
            logger.error(f"Error getting agent executor: {str(exec_error)}")
            raise HTTPException(status_code=500, detail=f"Error initializing AI assistant: {str(exec_error)}")

        # Default AI response in case of errors
        ai_response_content = "Sorry, I encountered an error processing your request."
        ai_message_obj = None

        try:
            # Invoke agent with proper error handling
            initial_agent_input = {"messages": messages_for_agent}
            logger.debug(f"Invoking agent executor with {len(messages_for_agent)} messages")
            
            # Attempt to invoke the agent with proper exception handling
            try:
                final_state = await agent_executor.ainvoke(initial_agent_input)
                logger.debug(f"Agent execution successful, state type: {type(final_state).__name__}")
                
                # Safe extraction of AI response from the final state
                if isinstance(final_state, dict):
                    # Extract message from final state with thorough validation
                    if "messages" in final_state and final_state["messages"]:
                        messages_list = final_state["messages"]
                        logger.debug(f"Found {len(messages_list)} messages in final_state")
                        
                        # Try to get the last message
                        if messages_list and len(messages_list) > 0:
                            ai_message_obj = messages_list[-1]
                            
                            if hasattr(ai_message_obj, 'content') and ai_message_obj.content:
                                ai_response_content = ai_message_obj.content
                                logger.debug(f"Extracted AI response content, length: {len(ai_response_content)}")
                            else:
                                logger.warning(f"AI message has no content attribute or empty content: {type(ai_message_obj).__name__}")
                                ai_response_content = "I processed your request, but encountered an issue generating a response."
                    # Direct extraction for alternate format
                    elif "final_answer" in final_state and final_state["final_answer"]:
                        ai_response_content = final_state["final_answer"]
                        logger.debug(f"Found final_answer in state, length: {len(ai_response_content)}")
                    else:
                        logger.warning(f"Unexpected final_state structure: keys={', '.join(final_state.keys()) if isinstance(final_state, dict) else 'not a dict'}")
                else:
                    logger.warning(f"Final state is not a dictionary: {type(final_state).__name__}")
            except Exception as agent_error:
                logger.error(f"Agent invocation error: {str(agent_error)}")
                if "timeout" in str(agent_error).lower():
                    ai_response_content = "Sorry, it's taking longer than expected to process your request. Please try again with a simpler query."
                else:
                    ai_response_content = "I encountered a technical issue while processing your request. Our team has been notified."

        except Exception as outer_error:
            logger.error(f"Unexpected error in agent processing: {str(outer_error)}")
            import traceback
            logger.error(traceback.format_exc())
            # Continue with the default response
            
        # Ensure we have a valid AI response
        if not ai_response_content or len(ai_response_content.strip()) == 0:
            ai_response_content = "I'm sorry, I couldn't generate a proper response at this time."
            
        # Store AI response with proper error handling
        ai_msg_id = str(uuid4())
        ai_now = ensure_datetime(datetime.utcnow())
        ai_now_str = format_datetime_for_json(ai_now)
        
        try:
            async with db.get_postgres_connection() as conn:
                await conn.execute(
                    "INSERT INTO chat_messages(id, thread_id, content, role, created_at) VALUES($1,$2,$3,$4,$5)",
                    ai_msg_id, thread_id, ai_response_content, "assistant", ai_now)
                logger.debug(f"AI response stored successfully with ID: {ai_msg_id}")
        except Exception as db_error:
            logger.error(f"Error storing AI response: {str(db_error)}")
            # Still try to return the AI response to the user even if DB storage fails
            
        ai_msg_data = {"id": ai_msg_id, "thread_id": thread_id, "content": ai_response_content, "role": "assistant", "created_at": ai_now_str}
        return ai_msg_data  # Return the AI's message
        
    except Exception as critical_error:
        # This is the outermost exception handler for truly unexpected errors
        logger.critical(f"Critical error in post_message: {str(critical_error)}")
        import traceback
        logger.critical(traceback.format_exc())
        
        # Return a generic error response rather than failing with 500
        fallback_msg_id = str(uuid4())
        fallback_now = format_datetime_for_json(datetime.utcnow())
        return {
            "id": fallback_msg_id,
            "thread_id": thread_id,
            "content": "I'm sorry, but I encountered a system error. Please try again later.",
            "role": "assistant",
            "created_at": fallback_now
        }

@router.get("/{thread_id}/messages", response_model=List[MessageResponse])
async def get_messages(thread_id: str, db: DatabaseManager = Depends(get_db_manager)):
    async with db.get_postgres_connection() as conn:
        exists = await conn.fetchval("SELECT 1 FROM chat_threads WHERE id=$1", thread_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Thread not found")
    async with db.get_postgres_connection() as conn:
        rows = await conn.fetch(
            "SELECT id, content, role, created_at FROM chat_messages WHERE thread_id=$1 ORDER BY created_at", thread_id)
    return [
        {"id": r["id"], "thread_id": thread_id, "content": r["content"], "role": r["role"], "created_at": format_datetime_for_json(r["created_at"])}
        for r in rows
    ]
