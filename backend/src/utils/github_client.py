from typing import Dict, Any, Optional, List
from fastapi import Depends, HTTPException
import httpx

from ..auth.firebase import get_current_user
from ..database import get_db_connection, release_db_connection
from ..utils.logging_config import logger

async def get_user_github_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Optional[str]:
    """
    Retrieves the GitHub access token for the current user from the database.
    """
    user_id = current_user.get("uid")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    conn = None
    try:
        conn = await get_db_connection()
        # We assume a table 'user_identities' exists with:
        # user_id (TEXT), provider (TEXT), access_token (TEXT)
        token_record = await conn.fetchrow(
            "SELECT access_token FROM user_identities WHERE user_id = $1 AND provider = 'github'",
            user_id
        )
        if token_record:
            return token_record['access_token']
        return None
    except Exception as e:
        logger.error(f"Database error while fetching GitHub token for user {user_id}: {e}")
        # In a real app, you might not want to expose DB errors.
        # For now, we return None and the endpoint will handle it.
        return None
    finally:
        if conn:
            await release_db_connection(conn)

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"

    async def _request(self, method: str, url: str, token: str, **kwargs) -> httpx.Response:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
        async with httpx.AsyncClient() as client:
            response = await client.request(method, f"{self.base_url}{url}", headers=headers, **kwargs)
            response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx
            return response

    async def get_user_repositories(self, token: str) -> List[Dict[str, Any]]:
        response = await self._request("GET", "/user/repos?sort=updated&per_page=100", token)
        return response.json()
    
    async def get_repository_details(self, token: str, owner: str, repo: str) -> Dict[str, Any]:
        response = await self._request("GET", f"/repos/{owner}/{repo}", token)
        return response.json()

    async def get_repository_contents(self, token: str, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        response = await self._request("GET", f"/repos/{owner}/{repo}/contents/{path}", token)
        return response.json()


github_client = GitHubClient()
