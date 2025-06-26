"""
Graphiti Memory Manager for AI Agents

This module provides memory storage and retrieval using Graphiti (Zep).
"""

import os
import logging
from typing import Optional, Dict, Any, List

import httpx

logger = logging.getLogger(__name__)

class GraphitiMemoryManager:
    """
    Manages memory using the Graphiti (Zep) service.
    """

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.http_client: Optional[httpx.AsyncClient] = None

    async def initialize(self):
        """Initialize the HTTP client."""
        if not self.http_client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            self.http_client = httpx.AsyncClient(base_url=self.api_url, headers=headers)
            try:
                response = await self.http_client.get("/healthz")
                response.raise_for_status()
                logger.info("GraphitiMemoryManager initialized successfully")
            except httpx.RequestError as e:
                logger.error(f"Failed to connect to Zep at {self.api_url}: {e}")
                self.http_client = None
                raise

    async def close(self):
        """Close the HTTP client."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
            logger.info("GraphitiMemoryManager closed")

    async def get_or_create_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get or create a Zep session."""
        if not self.http_client:
            raise RuntimeError("Memory manager not initialized")
        try:
            response = await self.http_client.get(f"/sessions/{session_id}")
            if response.status_code == 404:
                response = await self.http_client.post("/sessions", json={"session_id": session_id})
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Failed to get or create session {session_id}: {e}")
            return None

    async def add_memory(self, session_id: str, role: str, content: str) -> bool:
        """Add a memory to a Zep session."""
        if not self.http_client:
            raise RuntimeError("Memory manager not initialized")
        try:
            payload = {"messages": [{"role": role, "content": content}]}
            response = await self.http_client.post(f"/sessions/{session_id}/memory", json=payload)
            response.raise_for_status()
            logger.debug(f"Added memory to session {session_id}")
            return True
        except httpx.RequestError as e:
            logger.error(f"Failed to add memory to session {session_id}: {e}")
            return False

    async def search_memory(self, session_id: str, query: str, limit: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Search for memories in a Zep session."""
        if not self.http_client:
            raise RuntimeError("Memory manager not initialized")
        try:
            payload = {"search_query": query, "search_limit": limit}
            response = await self.http_client.post(f"/sessions/{session_id}/search", json=payload)
            response.raise_for_status()
            return response.json().get("results", [])
        except httpx.RequestError as e:
            logger.error(f"Failed to search memory in session {session_id}: {e}")
            return None

# Global instance
_graphiti_memory_manager: Optional[GraphitiMemoryManager] = None

async def get_graphiti_memory_manager() -> Optional[GraphitiMemoryManager]:
    """Get the global Graphiti memory manager instance."""
    global _graphiti_memory_manager
    if _graphiti_memory_manager is None:
        api_url = os.getenv('ZEP_API_URL')
        api_key = os.getenv('ZEP_API_KEY')

        if not api_url or not api_key:
            logger.warning("Zep not configured (ZEP_API_URL or ZEP_API_KEY not set)")
            return None

        _graphiti_memory_manager = GraphitiMemoryManager(api_url=api_url, api_key=api_key)
        try:
            await _graphiti_memory_manager.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize GraphitiMemoryManager: {e}")
            _graphiti_memory_manager = None
            return None
            
    return _graphiti_memory_manager

async def close_graphiti_memory_manager():
    """Close the global Graphiti memory manager instance."""
    global _graphiti_memory_manager
    if _graphiti_memory_manager:
        await _graphiti_memory_manager.close()
        _graphiti_memory_manager = None
