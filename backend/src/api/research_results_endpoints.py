from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from agent.database import research_result_repository, ResearchResult

router = APIRouter(prefix="/api/v1/research-results", tags=["research-results"])

class ResearchResultIn(BaseModel):
    query: str
    summary: str
    sources: list
    context_json: Optional[dict] = None

class ResearchResultOut(BaseModel):
    id: int
    query: str
    summary: str
    sources: list
    created_at: str
    context_json: Optional[dict] = None

@router.post("/", response_model=ResearchResultOut)
async def create_research_result(result: ResearchResultIn):
    try:
        result_id = await research_result_repository.create_research_result(
            result.query, result.summary, result.sources, result.context_json
        )
        db_result = await research_result_repository.get_research_result(result_id)
        if db_result:
            return db_result
        raise HTTPException(status_code=500, detail="Failed to fetch created result")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ResearchResultOut])
async def list_research_results(limit: int = 20, offset: int = 0):
    try:
        return await research_result_repository.list_research_results(limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{result_id}", response_model=ResearchResultOut)
async def get_research_result(result_id: int):
    db_result = await research_result_repository.get_research_result(result_id)
    if db_result:
        return db_result
    raise HTTPException(status_code=404, detail="Research result not found")
