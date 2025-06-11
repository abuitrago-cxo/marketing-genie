from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel
from typing import List, Optional, Any, Dict, Union
from uuid import uuid4
from datetime import datetime
import logging

from agent.graph import get_agent_executor
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from agent.database import db_manager, DatabaseManager

router = APIRouter(prefix="/chat", tags=["chat"])

# Helper functions for timestamp handling
def ensure_datetime(timestamp) -> datetime:
    """Convert various timestamp formats to datetime object, used before DB insertion."""
    if timestamp is None:
        return datetime.utcnow()
        
    if isinstance(timestamp, str):
        try:
            # Remove Z suffix if present (UTC indicator)
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1]
            
            # Handle milliseconds format (PostgreSQL compatibility)
            # Check for '+' timezone indicator and remove it with the timezone part
            if '+' in timestamp:
                timestamp = timestamp.split('+')[0]
                
            # Ensure we have a proper format for fromisoformat
            return datetime.fromisoformat(timestamp)
        except ValueError as e:
            logging.error(f"Could not parse timestamp: {timestamp}, error: {e}")
            return datetime.utcnow()
    elif isinstance(timestamp, datetime):
        return timestamp
    else:
        logging.error(f"Unknown timestamp type: {type(timestamp)}, value: {timestamp}")
        return datetime.utcnow()

def format_datetime_for_json(dt) -> str:
    """Format a datetime object to ISO 8601 format string for JSON response."""
    if isinstance(dt, datetime):
        return dt.isoformat() + "Z"
    elif isinstance(dt, str):
        # If it's already a string, return as is or ensure it ends with Z
        return dt if dt.endswith('Z') else dt + "Z"
    else:
        logging.error(f"Cannot format unknown type as ISO datetime: {type(dt)}")
        return datetime.utcnow().isoformat() + "Z"

# Dependency to get the database manager
def get_db_manager() -> DatabaseManager:
    return db_manager

class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    content: str

class MessageResponse(BaseModel):
    id: str
    thread_id: str
    content: str
    role: str
    created_at: str  # Always returned as ISO string in API responses

@router.post("/", response_model=MessageResponse)
async def chat(request: ChatRequest, db: DatabaseManager = Depends(get_db_manager)):
    # Configure logger
    logger = logging.getLogger("chat_endpoints.chat")
    logger.setLevel(logging.DEBUG)
    
    try:
        # Initialize DB if not
        # Create new thread if needed
        if not request.thread_id:
            thread_id = str(uuid4())
            now = ensure_datetime(datetime.utcnow())
            try:
                async with db.get_postgres_connection() as conn:
                    await conn.execute(
                        "INSERT INTO chat_threads(id, created_at) VALUES($1, $2)",
                        thread_id, now)
                logger.debug(f"Created new thread with ID: {thread_id}")
            except Exception as db_error:
                logger.error(f"Failed to create thread: {str(db_error)}")
                raise HTTPException(status_code=500, detail="Database error when creating thread")
        else:
            thread_id = request.thread_id
            try:
                async with db.get_postgres_connection() as conn:
                    row = await conn.fetchrow(
                        "SELECT id FROM chat_threads WHERE id=$1", thread_id)
                if not row:
                    raise HTTPException(status_code=404, detail="Thread not found")
                logger.debug(f"Using existing thread with ID: {thread_id}")
            except HTTPException:
                raise
            except Exception as db_error:
                logger.error(f"Failed to verify thread existence: {str(db_error)}")
                raise HTTPException(status_code=500, detail="Database error when verifying thread")

        # Store user message in DB
        user_msg_id = str(uuid4())
        msg_time = ensure_datetime(datetime.utcnow())
        try:
            async with db.get_postgres_connection() as conn:
                await conn.execute(
                    "INSERT INTO chat_messages(id, thread_id, content, role, created_at) VALUES($1, $2, $3, $4, $5)",
                    user_msg_id, thread_id, request.content, "user", msg_time)
            logger.debug(f"Stored user message with ID: {user_msg_id}")
        except Exception as db_error:
            logger.error(f"Failed to store user message: {str(db_error)}")
            raise HTTPException(status_code=500, detail="Database error when storing user message")

        # Retrieve all messages for the agent
        messages_for_agent: List[BaseMessage] = []
        try:
            async with db.get_postgres_connection() as conn:
                rows = await conn.fetch(
                    "SELECT content, role FROM chat_messages WHERE thread_id=$1 ORDER BY created_at", thread_id)
                
            for content, role in [(r['content'], r['role']) for r in rows]:
                if role == "user":
                    messages_for_agent.append(HumanMessage(content=content))
                else:
                    messages_for_agent.append(AIMessage(content=content))
                    
            logger.debug(f"Retrieved {len(messages_for_agent)} messages for agent")
        except Exception as fetch_error:
            logger.error(f"Failed to retrieve messages: {str(fetch_error)}")
            raise HTTPException(status_code=500, detail="Error retrieving chat history")

        # Initialize a proper default response in case of errors
        ai_content = f"I received your message: '{request.content}'. Let me process that for you."
        
        # Invoke the LangGraph chat flow with proper error handling
        try:
            # Get the agent executor
            agent_executor = get_agent_executor()
            logger.debug("Got agent executor successfully")
            
            # Call the agent with proper timeout and error handling
            try:
                final_state = await agent_executor.ainvoke({"messages": messages_for_agent})
                logger.debug(f"Agent invoked successfully - state type: {type(final_state).__name__}")
                
                # Extract AI response with validation
                if isinstance(final_state, dict):
                    # Try to extract from messages list
                    if "messages" in final_state and final_state["messages"]:
                        messages_list = final_state["messages"]
                        logger.debug(f"Found {len(messages_list)} messages in final_state")
                        
                        # Get the last message if available
                        if messages_list and len(messages_list) > 0:
                            last_message = messages_list[-1]
                            
                            if hasattr(last_message, 'content') and last_message.content:
                                ai_content = last_message.content
                                logger.debug(f"Extracted AI response content, length: {len(ai_content)}")
                            else:
                                logger.warning("Last message object doesn't have valid content")
                        else:
                            logger.warning("Messages list is empty")
                    # Try alternate formats
                    elif "final_answer" in final_state and final_state["final_answer"]:
                        ai_content = final_state["final_answer"]
                        logger.debug(f"Found final_answer in state, length: {len(ai_content)}")
                    else:
                        logger.warning(f"Unexpected state structure: {list(final_state.keys()) if isinstance(final_state, dict) else 'not a dict'}")
                else:
                    logger.warning(f"Unexpected final_state type: {type(final_state).__name__}")
            except Exception as agent_error:
                logger.error(f"Error during agent invocation: {str(agent_error)}")
                error_str = str(agent_error).lower()
                
                # Provide more helpful error messages
                if "timeout" in error_str or "time limit" in error_str:
                    ai_content = "I'm taking longer than expected to process your request. Let me provide a simpler response instead."
                elif "resource exhausted" in error_str or "429" in error_str:
                    ai_content = "I'm currently experiencing high demand. I've received your message and will respond as soon as possible."
                elif "api" in error_str and ("key" in error_str or "credential" in error_str):
                    ai_content = "I'm currently experiencing configuration issues. Your message has been received and logged."
                else:
                    ai_content = f"I received your message about '{request.content[:30]}...' but encountered a technical issue while processing it. Let me try a different approach."
        except Exception as outer_error:
            logger.error(f"Critical error in chat endpoint: {str(outer_error)}")
            ai_content = "I'm currently experiencing technical difficulties. Your message has been received."

        # Ensure we have a valid AI response content
        if not ai_content or len(ai_content.strip()) == 0:
            ai_content = "I understand your message and I'm working on a proper response."
        
        # Store AI message in DB
        ai_msg_id = str(uuid4())
        ai_time = ensure_datetime(datetime.utcnow())
        try:
            async with db.get_postgres_connection() as conn:
                await conn.execute(
                    "INSERT INTO chat_messages(id, thread_id, content, role, created_at) VALUES($1, $2, $3, $4, $5)",
                    ai_msg_id, thread_id, ai_content, "assistant", ai_time)
            logger.debug(f"Stored AI message with ID: {ai_msg_id}")
        except Exception as db_error:
            logger.error(f"Failed to store AI message: {str(db_error)}")
            # Still try to return the message even if DB storage fails
        
        # Convert datetime to ISO format string for JSON response
        return {"id": ai_msg_id, "thread_id": thread_id, "content": ai_content, "role": "assistant", "created_at": format_datetime_for_json(ai_time)}
        
    except Exception as critical_error:
        # Top-level error handler
        logger.critical(f"Critical error in chat endpoint: {str(critical_error)}")
        import traceback
        logger.critical(traceback.format_exc())
        
        # Return a fallback response rather than letting the API fail with 500
        fallback_msg_id = str(uuid4())
        fallback_time = format_datetime_for_json(datetime.utcnow())
        return {
            "id": fallback_msg_id,
            "thread_id": request.thread_id or str(uuid4()),
            "content": "I've received your message. Our system is currently experiencing technical difficulties, but your request has been logged.",
            "role": "assistant",
            "created_at": fallback_time
        }

@router.get("/{thread_id}", response_model=List[MessageResponse])
async def get_chat(thread_id: str, db: DatabaseManager = Depends(get_db_manager)):
    # Ensure thread exists
    async with db.get_postgres_connection() as conn:
        row = await conn.fetchrow("SELECT id FROM chat_threads WHERE id=$1", thread_id)
    if not row:
        raise HTTPException(status_code=404, detail="Thread not found")
    # Retrieve messages
    async with db.get_postgres_connection() as conn:
        rows = await conn.fetch(
            "SELECT id, content, role, created_at FROM chat_messages WHERE thread_id=$1 ORDER BY created_at", thread_id)
    return [
        {
            "id": r['id'],
            "thread_id": thread_id,
            "content": r['content'],
            "role": r['role'],
            # Handle both datetime and string for created_at
            "created_at": format_datetime_for_json(r['created_at'])
        }
        for r in rows
    ]

@router.websocket("/ws")
async def chat_ws(websocket: WebSocket, db: DatabaseManager = Depends(get_db_manager)):
    """WebSocket endpoint for streaming chat responses."""
    # Configure logger
    logger = logging.getLogger("chat_endpoints.ws")
    logger.setLevel(logging.DEBUG)
    
    thread_id = None
    await websocket.accept()
    
    try:
        # Parse request data
        try:
            data = await websocket.receive_json()
            req = ChatRequest(**data)
            logger.debug(f"Received WebSocket request: {req.content[:50]}...")
        except Exception as parse_error:
            logger.error(f"Failed to parse WebSocket request: {str(parse_error)}")
            await websocket.send_json({"type": "error", "message": "Invalid request format"})
            return
        
        # Create or validate thread
        try:
            if not req.thread_id:
                thread_id = str(uuid4())
                now = ensure_datetime(datetime.utcnow())
                async with db.get_postgres_connection() as conn:
                    await conn.execute(
                        "INSERT INTO chat_threads(id, created_at) VALUES($1, $2)",
                        thread_id, now
                    )
                logger.debug(f"Created new thread with ID: {thread_id}")
            else:
                thread_id = req.thread_id
                async with db.get_postgres_connection() as conn:
                    row = await conn.fetchrow(
                        "SELECT id FROM chat_threads WHERE id=$1", thread_id
                    )
                if not row:
                    logger.warning(f"Thread not found: {thread_id}")
                    await websocket.send_json({"type": "error", "message": "Thread not found"})
                    return
                logger.debug(f"Using existing thread with ID: {thread_id}")
        except Exception as thread_error:
            logger.error(f"Database error when handling thread: {str(thread_error)}")
            await websocket.send_json({"type": "error", "message": "Database error when processing thread"})
            return
            
        # Store user message
        try:
            user_msg_id = str(uuid4())
            msg_time = ensure_datetime(datetime.utcnow())
            async with db.get_postgres_connection() as conn:
                await conn.execute(
                    "INSERT INTO chat_messages(id, thread_id, content, role, created_at) VALUES($1,$2,$3,$4,$5)",
                    user_msg_id, thread_id, req.content, "user", msg_time
                )
            logger.debug(f"Stored user message with ID: {user_msg_id}")
        except Exception as msg_error:
            logger.error(f"Failed to store user message: {str(msg_error)}")
            await websocket.send_json({"type": "error", "message": "Failed to store your message"})
            return
            
        # Build messages list
        try:
            messages_for_agent = []
            async with db.get_postgres_connection() as conn:
                rows = await conn.fetch(
                    "SELECT content, role FROM chat_messages WHERE thread_id=$1 ORDER BY created_at", thread_id
                )
            
            for content, role in [(r['content'], r['role']) for r in rows]:
                if role == "user":
                    messages_for_agent.append(HumanMessage(content=content))
                else:
                    messages_for_agent.append(AIMessage(content=content))
                    
            logger.debug(f"Retrieved {len(messages_for_agent)} messages for agent")
        except Exception as fetch_error:
            logger.error(f"Failed to retrieve message history: {str(fetch_error)}")
            await websocket.send_json({"type": "error", "message": "Error retrieving message history"})
            return
        
        # Default response in case we need it
        ai_content = f"I received your message: '{req.content[:30]}...'. Let me think about that."
        
        # Invoke LangGraph
        try:
            # Get agent executor
            executor = get_agent_executor()
            logger.debug("Got agent executor successfully")
            
            # Invoke agent with proper error handling
            try:
                final_state = await executor.ainvoke({"messages": messages_for_agent})
                logger.debug(f"Agent invoked successfully - state type: {type(final_state).__name__}")
                
                # Extract AI response with validation
                if isinstance(final_state, dict):
                    # Try to extract from messages list
                    if "messages" in final_state and final_state["messages"]:
                        messages_list = final_state["messages"]
                        logger.debug(f"Found {len(messages_list)} messages in final_state")
                        
                        # Get the last message if available
                        if messages_list and len(messages_list) > 0:
                            last_message = messages_list[-1]
                            
                            if hasattr(last_message, 'content') and last_message.content:
                                ai_content = last_message.content
                                logger.debug(f"Extracted AI response content, length: {len(ai_content)}")
                            else:
                                logger.warning("Last message object doesn't have valid content")
                    # Try alternate formats
                    elif "final_answer" in final_state and final_state["final_answer"]:
                        ai_content = final_state["final_answer"]
                        logger.debug(f"Found final_answer in state, length: {len(ai_content)}")
                    else:
                        logger.warning(f"Unexpected state structure: {list(final_state.keys()) if isinstance(final_state, dict) else 'not a dict'}")
                else:
                    logger.warning(f"Unexpected final_state type: {type(final_state).__name__}")
            except Exception as agent_error:
                logger.error(f"Error during agent invocation: {str(agent_error)}")
                error_str = str(agent_error).lower()
                
                if "timeout" in error_str or "time limit" in error_str:
                    ai_content = "La respuesta está tomando más tiempo del esperado. Intentaré darte una respuesta más simple."
                elif "resource exhausted" in error_str or "429" in error_str:
                    ai_content = "Estoy experimentando alta demanda. He recibido tu mensaje y responderé tan pronto como sea posible."
                elif "api" in error_str and ("key" in error_str or "credential" in error_str):
                    ai_content = "Estoy experimentando problemas de configuración. Tu mensaje ha sido recibido y registrado."
                else:
                    ai_content = "Lo siento, hubo un error al procesar tu solicitud. Por favor, intenta de nuevo."
        except Exception as executor_error:
            logger.error(f"Failed to execute agent: {str(executor_error)}")
            ai_content = "I received your message but am having trouble processing it right now."
            # Ensure we have a valid AI response content
            if not ai_content or len(ai_content.strip()) == 0:
                ai_content = "Lo siento, no pude generar una respuesta en este momento. Por favor, intenta reformular tu pregunta."
        
        # Stream tokens with error handling
        try:
            # Send a confirmation message first to verify WebSocket is still open
            await websocket.send_json({"type": "start", "thread_id": thread_id})
            
            # Stream each character of the response
            for ch in ai_content:
                try:
                    await websocket.send_json({"type": "token", "data": ch})
                except Exception as stream_error:
                    logger.error(f"Error streaming token: {str(stream_error)}")
                    break
                    
            logger.debug("Successfully streamed full response")
        except Exception as ws_error:
            logger.error(f"WebSocket stream error: {str(ws_error)}")
            # If we can't stream, we'll still try to save the message to DB
            
        # Store AI message in DB
        try:
            ai_msg_id = str(uuid4())
            ai_time = ensure_datetime(datetime.utcnow())
            async with db.get_postgres_connection() as conn:
                await conn.execute(
                    "INSERT INTO chat_messages(id, thread_id, content, role, created_at) VALUES($1,$2,$3,$4,$5)",
                    ai_msg_id, thread_id, ai_content, "assistant", ai_time
                )
            logger.debug(f"Stored AI message with ID: {ai_msg_id}")
        except Exception as db_error:
            logger.error(f"Failed to store AI message: {str(db_error)}")
            # Continue to end the WebSocket even if storage fails
        
        # Send end signal
        try:
            await websocket.send_json({"type": "end", "thread_id": thread_id})
            logger.debug("WebSocket communication completed successfully")
        except Exception as end_error:
            logger.error(f"Error sending end signal: {str(end_error)}")
            
    except Exception as e:
        # General error handler
        logger.critical(f"Critical error in WebSocket handler: {str(e)}")
        import traceback
        logger.critical(traceback.format_exc())
        
        # Try to send an error message if possible
        try:
            error_msg = "Ha ocurrido un error inesperado. Por favor, intenta de nuevo."
            await websocket.send_json({
                "type": "error",
                "message": error_msg,
                "details": str(e) if not isinstance(e, str) else e
            })
            # También intentamos guardar el mensaje de error en la base de datos
            try:
                error_msg_id = str(uuid4())
                error_time = ensure_datetime(datetime.utcnow())
                async with db.get_postgres_connection() as conn:
                    await conn.execute(
                        "INSERT INTO chat_messages(id, thread_id, content, role, created_at) VALUES($1,$2,$3,$4,$5)",
                        error_msg_id, thread_id, error_msg, "assistant", error_time
                    )
            except Exception as db_error:
                logger.error(f"Failed to store error message: {str(db_error)}")
        except Exception as ws_error:
            logger.error(f"Failed to send error message via WebSocket: {str(ws_error)}")
    finally:
        # Always close the WebSocket connection
        try:
            await websocket.close()
        except Exception as close_error:
            logger.error(f"Error closing WebSocket: {str(close_error)}")
            # Nothing more we can do here
