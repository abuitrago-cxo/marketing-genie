"""System metrics and status endpoints.

Provides real runtime metrics (/metrics) and deep system status checks (/system-status)
covering database, Redis, and graph health.
"""
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
import asyncpg

try:
    import psutil  # type: ignore
except ImportError:  # graceful degradation if psutil not installed
    psutil = None  # type: ignore

try:
    import redis.asyncio as aioredis  # type: ignore
except ImportError:
    aioredis = None  # type: ignore

# LangSmith endpoints
import os
import httpx

from ..agent.graphs.graph_registry import get_graph_registry
from ...database import get_db_connection, release_db_connection
from ...utils.logging_config import logger

router = APIRouter(prefix="/api/v1", tags=["system"])

# Helper -------------------------------------------------------------

async def check_postgres() -> Dict[str, Any]:
    try:
        conn = await get_db_connection()
        await conn.execute("SELECT 1")
        await release_db_connection(conn)
        return {"status": "healthy"}
    except asyncpg.PostgresError as e:
        logger.error("PostgreSQL health check failed", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}


async def check_redis() -> Dict[str, Any]:
    if aioredis is None:
        return {"status": "unavailable", "error": "aioredis not installed"}
    try:
        redis_url = "redis://localhost:6379/0"  # TODO: read from settings/env
        redis = aioredis.from_url(redis_url)
        pong = await redis.ping()
        await redis.close()
        return {"status": "healthy" if pong else "unhealthy"}
    except Exception as e:
        logger.error("Redis health check failed", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}


async def check_langsmith() -> Dict[str, Any]:
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        return {"status": "unavailable", "error": "LANGSMITH_API_KEY not set"}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                "https://api.smith.langchain.com/health",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return {"status": "healthy" if data.get("status") == "ok" else "unhealthy"}
            return {"status": "unhealthy", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        logger.error("LangSmith health check failed", exc_info=True)
        return {"status": "unhealthy", "error": str(e)}


# Endpoints ----------------------------------------------------------

@router.get("/metrics", summary="System runtime metrics")
async def get_metrics() -> Dict[str, Any]:
    """Return system and application metrics."""
    try:
        registry = get_graph_registry()
        graph_health = registry.get_health_status()
        langsmith_status = await check_langsmith()

        system_metrics: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "graphs": graph_health,
            "langsmith": langsmith_status,
        }

        if psutil:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            system_metrics["os"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": mem.percent,
                "total_memory_mb": mem.total // (1024 * 1024),
                "available_memory_mb": mem.available // (1024 * 1024),
            }
        else:
            system_metrics["os"] = {"warning": "psutil not installed"}

        return system_metrics
    except Exception as e:
        logger.error("Failed to collect metrics", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to collect metrics: {str(e)}")


@router.get("/system-status", summary="Deep system status check")
async def get_system_status() -> Dict[str, Any]:
    """Return aggregated health status of core services."""
    try:
        postgres_status, redis_status, langsmith_status = (
            await check_postgres(),
            await check_redis(),
            await check_langsmith(),
        )
        registry = get_graph_registry()
        graphs_status = registry.get_health_status()

        overall_healthy = all([
            postgres_status.get("status") == "healthy",
            redis_status.get("status") in ("healthy", "unavailable"),  # treat unavailable as degraded
            graphs_status.get("healthy_graphs", 0) == graphs_status.get("total_graphs", 0),
            langsmith_status.get("status") in ("healthy", "unavailable"),
        ])

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if overall_healthy else "degraded",
            "postgres": postgres_status,
            "redis": redis_status,
            "graphs": graphs_status,
            "langsmith": langsmith_status,
        }
    except Exception as e:
        logger.error("Failed to get system status", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")
