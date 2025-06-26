"""
Projects API endpoints for the AI Agent Assistant

This module provides REST API endpoints for project management,
integrating with the new PostgreSQL database schema and memory system.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from ..auth.firebase import get_current_user
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
import asyncpg
import httpx

from ...database import get_db_connection, release_db_connection
from ...utils.logging_config import logger
from ..agent.graphs.graph_registry import get_specialized_graph
from ..agent.state import CodebaseAnalysisState, DocumentationAnalysisState, ResearchAnalysisState, QualityAssuranceState, ProjectOrchestratorState
from langchain_core.messages import HumanMessage

# Create router for projects endpoints
projects_router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

# Pydantic models for request/response
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    github_repo_url: Optional[str] = None
    status: str = "active"
    priority: str = "medium"
    team: Optional[str] = None
    user_id: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    github_repo_url: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    team: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    github_repo_id: Optional[str] = None
    github_metadata: Optional[Dict[str, Any]] = None
    repository_analysis: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    ai_generated: bool = False

class TaskCreate(TaskBase):
    project_id: int

class TaskResponse(TaskBase):
    id: int
    project_id: int
    github_issue_id: Optional[str] = None
    github_issue_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    target_date: Optional[datetime] = None
    ai_generated: bool = False

class MilestoneCreate(MilestoneBase):
    project_id: int

class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

# Database helper functions
async def get_db_connection():
    """Get database connection from pool"""
    from agent.database import get_database_pool
    pool = await get_database_pool()
    return await pool.acquire()

async def release_db_connection(conn):
    """Release database connection back to pool"""
    from agent.database import get_database_pool
    pool = await get_database_pool()
    await pool.release(conn)

# Projects endpoints
@projects_router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    current_user: Optional[Dict[str, Any]] = None, # Depends(get_current_user),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all projects with optional filtering"""
    try:
        conn = await get_db_connection()

        # Build query with filters
        conditions = []
        params = []
        param_count = 0

        user_id = current_user.get('uid') if current_user else None
        if user_id:
            param_count += 1
            conditions.append(f"user_id = ${param_count}")
            params.append(user_id)

        if status:
            param_count += 1
            conditions.append(f"status = ${param_count}")
            params.append(status)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
        SELECT id, name, description, github_repo_url, github_repo_id,
               github_metadata, repository_analysis, status, priority,
               team, created_at, updated_at, user_id
        FROM projects
        {where_clause}
        ORDER BY updated_at DESC
        LIMIT {limit} OFFSET {offset}
        """

        rows = await conn.fetch(query, *params)

        projects = []
        for row in rows:
            project = ProjectResponse(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                github_repo_url=row['github_repo_url'],
                github_repo_id=row['github_repo_id'],
                github_metadata=row['github_metadata'],
                repository_analysis=row['repository_analysis'],
                status=row['status'],
                priority=row['priority'],
                team=row['team'],
                user_id=row['user_id'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            projects.append(project)

        await release_db_connection(conn)

        logger.info(f"Retrieved {len(projects)} projects")
        return projects

    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve projects")

@projects_router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Create a new project"""
    try:
        conn = await get_db_connection()

        query = """
        INSERT INTO projects (name, description, github_repo_url, status, priority, team, user_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, name, description, github_repo_url, github_repo_id,
                  github_metadata, repository_analysis, status, priority,
                  team, created_at, updated_at, user_id
        """

        row = await conn.fetchrow(
            query,
            project.name,
            project.description,
            project.github_repo_url,
            project.status,
            project.priority,
            project.team,
            project.user_id
        )

        await release_db_connection(conn)

        # Store project creation in memory for future reference
        try:
            from ..memory import get_memory_manager
            memory_manager = await get_memory_manager()
            await memory_manager.store_memory(
                agent_id="project_manager",
                content=f"Created project '{project.name}' with description: {project.description}",
                memory_type="project_creation",
                project_id=row['id'],
                importance_score=0.7,
                metadata={
                    "project_id": row['id'],
                    "github_repo": project.github_repo_url,
                    "priority": project.priority
                }
            )
        except Exception as mem_error:
            logger.warning(f"Failed to store project creation memory: {mem_error}")

        result = ProjectResponse(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            github_repo_url=row['github_repo_url'],
            github_repo_id=row['github_repo_id'],
            github_metadata=row['github_metadata'],
            repository_analysis=row['repository_analysis'],
            status=row['status'],
            priority=row['priority'],
            team=row['team'],
            user_id=row['user_id'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

        logger.info(f"Created project {result.id}: {result.name}")
        return result

    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@projects_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user))
    """Get a specific project by ID"""
    conn = None  # Initialize conn to None
    try:
        conn = await get_db_connection()
        project_query = """
            SELECT p.*, 
                   (SELECT json_agg(json_build_object('id', t.id, 'title', t.title, 'status', t.status)) 
                    FROM tasks t WHERE t.project_id = p.id) as tasks,
                   (SELECT json_agg(json_build_object('id', m.id, 'title', m.title, 'status', m.status)) 
                    FROM milestones m WHERE m.project_id = p.id) as milestones
            FROM projects p 
            WHERE p.id = $1
        """
        project_record = await conn.fetchrow(project_query, project_id)

        if not project_record:
            raise HTTPException(status_code=404, detail="Project not found")

        # Authorization check (currently disabled)
        # if current_user and project_record['user_id'] != current_user.get('uid'):
        #     raise HTTPException(status_code=403, detail="Not authorized to view this project")
        
        project_data = dict(project_record)
        
        # Process tasks and milestones if they exist
        project_data['tasks'] = project_data.get('tasks') or []
        project_data['milestones'] = project_data.get('milestones') or []

        return ProjectResponse(**project_data)
    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"Database error while fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"Unexpected error while fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if conn:
            await release_db_connection(conn)

@projects_router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project_update: ProjectUpdate, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Update an existing project"""
    conn = None
    try:
        conn = await get_db_connection()

        # Fetch the existing project
        existing_project = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if not existing_project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Authorization check (currently disabled)
        # user_id = current_user.get('uid') if current_user else None
        # if user_id and existing_project['user_id'] != user_id:
        #     raise HTTPException(status_code=403, detail="Not authorized to update this project")

        update_data = project_update.model_dump(exclude_unset=True)
        
        if not update_data:
            # If there's nothing to update, we could return the existing project or a 304 Not Modified.
            # For simplicity, let's return the existing project data as if it were updated (though no DB write occurs for empty update_data).
            # Alternatively, raise a 400 error if an empty update is considered invalid.
            # Returning existing project to align with potential frontend expectations of always getting a project back.
            # logger.info(f"No update data provided for project {project_id}. Returning existing project.")
            # return ProjectResponse(**dict(existing_project)) # This might not have all fields of ProjectResponse if tasks/milestones are not fetched here.
            # Let's fetch the full project details for the response to be consistent.
            # Re-fetch with joins to ensure the response model is satisfied, or raise 400.
            raise HTTPException(status_code=400, detail="No update data provided")

        set_clauses = []
        params = []
        param_idx = 1 # Start parameter index at 1 for PostgreSQL

        for key, value in update_data.items():
            set_clauses.append(f"{key} = ${param_idx}")
            params.append(value)
            param_idx += 1
        
        set_clauses.append(f"updated_at = NOW()") # Always update updated_at
        
        params.append(project_id) # Add project_id for the WHERE clause
        # The project_id will be the last parameter, so its index is param_idx

        update_query = f"UPDATE projects SET {', '.join(set_clauses)} WHERE id = ${param_idx} RETURNING *"
        
        logger.debug(f"Executing update query: {update_query} with params: {params}")
        updated_project_record = await conn.fetchrow(update_query, *params)

        if not updated_project_record:
            # This case should ideally not happen if the initial fetch succeeded and DB is consistent, 
            # unless the RETURNING * clause failed for some reason or the project was deleted concurrently.
            logger.error(f"Failed to update project {project_id} or retrieve updated record after update attempt.")
            raise HTTPException(status_code=500, detail="Failed to update project or retrieve updated record")
        
        # To ensure the response contains all fields expected by ProjectResponse (like tasks/milestones if defined in the model)
        # we should re-fetch the project with all necessary joins, similar to get_project.
        # For now, the RETURNING * will give us the columns from the 'projects' table.
        # If ProjectResponse includes joined data not in 'projects' table, this will be incomplete.
        # Let's assume ProjectResponse for an update primarily concerns the direct fields of the project entity.
        # The `get_project` endpoint already has the logic for fetching with joins.
        # We can call it or replicate its query if ProjectResponse needs more than `projects` table fields.
        # For now, RETURNING * from projects table is used.
        # The ProjectResponse model includes: id, name, description, github_repo_url, status, priority, team, user_id (from ProjectBase)
        # PLUS github_repo_id, github_metadata, repository_analysis, created_at, updated_at.
        # The `RETURNING *` will cover all columns in the `projects` table.
        
        # Re-fetch the project with all details to ensure the response is complete
        # This is safer to ensure the ProjectResponse model is fully populated, especially if it includes joined data.
        # However, this means an extra DB call. The alternative is to ensure RETURNING * and the ProjectResponse model align perfectly
        # or to construct the ProjectResponse manually if some fields are optional/derived.
        
        # Let's use the existing get_project logic to return the full, consistent response
        # This avoids duplicating the query logic for fetching related data.
        # Note: This means the `update_project` function itself doesn't directly use `updated_project_record` for the final response object.
        # It's used to confirm the update happened.
        
        # After successful update, fetch the complete project details for the response
        # This ensures consistency with the get_project endpoint's response structure.
        project_details_query = """
            SELECT p.*, 
                   (SELECT json_agg(json_build_object('id', t.id, 'title', t.title, 'status', t.status)) 
                    FROM tasks t WHERE t.project_id = p.id) as tasks,
                   (SELECT json_agg(json_build_object('id', m.id, 'title', m.title, 'status', m.status)) 
                    FROM milestones m WHERE m.project_id = p.id) as milestones
            FROM projects p 
            WHERE p.id = $1
        """
        final_project_record = await conn.fetchrow(project_details_query, project_id)
        if not final_project_record:
             logger.error(f"Failed to re-fetch project {project_id} after update.")
             raise HTTPException(status_code=500, detail="Failed to retrieve project details after update.")

        project_data = dict(final_project_record)
        project_data['tasks'] = project_data.get('tasks') or []
        project_data['milestones'] = project_data.get('milestones') or []

        return ProjectResponse(**project_data)

    except asyncpg.exceptions.PostgresError as e:
        logger.error(f"Database error while updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if conn:
            await release_db_connection(conn)


# Tasks endpoints
@projects_router.get("/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(project_id: int, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Get all tasks for a specific project"""
    try:
        conn = await get_db_connection()

        # Check if project exists and user has access
        project = await conn.fetchrow("SELECT id, user_id FROM projects WHERE id = $1", project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Not authorized to access tasks for this project")

        query = """
        SELECT id, project_id, title, description, status, priority,
               assigned_to, due_date, created_at, updated_at,
               github_issue_id, github_issue_url, ai_generated, metadata
        FROM project_tasks
        WHERE project_id = $1
        ORDER BY created_at DESC
        """

        rows = await conn.fetch(query, project_id)

        tasks = []
        for row in rows:
            task = TaskResponse(
                id=row['id'],
                project_id=row['project_id'],
                title=row['title'],
                description=row['description'],
                status=row['status'],
                priority=row['priority'],
                assigned_to=row['assigned_to'],
                due_date=row['due_date'],
                github_issue_id=row['github_issue_id'],
                github_issue_url=row['github_issue_url'],
                ai_generated=row['ai_generated'],
                metadata=row['metadata'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            tasks.append(task)

        await release_db_connection(conn)

        logger.info(f"Retrieved {len(tasks)} tasks for project {project_id}")
        return tasks

    except Exception as e:
        logger.error(f"Failed to get tasks for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")

@projects_router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(project_id: int, task: TaskCreate, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Create a new task for a project"""
    try:
        # Verify project exists
        conn = await get_db_connection()

        project = await conn.fetchrow("SELECT id, user_id FROM projects WHERE id = $1", project_id)
        if not project:
            await release_db_connection(conn)
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            await release_db_connection(conn)
            raise HTTPException(status_code=403, detail="Not authorized to create tasks for this project")

        query = """
        INSERT INTO project_tasks (project_id, title, description, status, priority,
                                 assigned_to, due_date, ai_generated)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id, project_id, title, description, status, priority,
                  assigned_to, due_date, created_at, updated_at,
                  github_issue_id, github_issue_url, ai_generated, metadata
        """

        row = await conn.fetchrow(
            query,
            project_id,
            task.title,
            task.description,
            task.status,
            task.priority,
            task.assigned_to,
            task.due_date,
            task.ai_generated
        )

        await release_db_connection(conn)

        result = TaskResponse(
            id=row['id'],
            project_id=row['project_id'],
            title=row['title'],
            description=row['description'],
            status=row['status'],
            priority=row['priority'],
            assigned_to=row['assigned_to'],
            due_date=row['due_date'],
            github_issue_id=row['github_issue_id'],
            github_issue_url=row['github_issue_url'],
            ai_generated=row['ai_generated'],
            metadata=row['metadata'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

        logger.info(f"Created task {result.id} for project {project_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create task for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")

# Milestones endpoints
@projects_router.get("/{project_id}/milestones", response_model=List[MilestoneResponse])
async def get_project_milestones(project_id: int, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Get all milestones for a specific project"""
    try:
        conn = await get_db_connection()

        # Check if project exists and user has access
        project = await conn.fetchrow("SELECT id, user_id FROM projects WHERE id = $1", project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Not authorized to access milestones for this project")

        query = """
        SELECT id, project_id, title, description, status, target_date,
               completed_at, created_at, updated_at, ai_generated, metadata
        FROM project_milestones
        WHERE project_id = $1
        ORDER BY target_date ASC
        """

        rows = await conn.fetch(query, project_id)

        milestones = []
        for row in rows:
            milestone = MilestoneResponse(
                id=row['id'],
                project_id=row['project_id'],
                title=row['title'],
                description=row['description'],
                status=row['status'],
                target_date=row['target_date'],
                completed_at=row['completed_at'],
                ai_generated=row['ai_generated'],
                metadata=row['metadata'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            milestones.append(milestone)

        await release_db_connection(conn)

        logger.info(f"Retrieved {len(milestones)} milestones for project {project_id}")
        return milestones

    except Exception as e:
        logger.error(f"Failed to get milestones for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve milestones")

@projects_router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=201)
async def create_milestone(project_id: int, milestone: MilestoneCreate, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Create a new milestone for a project"""
    try:
        # Verify project exists
        conn = await get_db_connection()

        project = await conn.fetchrow("SELECT id, user_id FROM projects WHERE id = $1", project_id)
        if not project:
            await release_db_connection(conn)
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            await release_db_connection(conn)
            raise HTTPException(status_code=403, detail="Not authorized to create a milestone for this project")

        query = """
        INSERT INTO project_milestones (project_id, title, description, status,
                                      target_date, ai_generated)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, project_id, title, description, status, target_date,
                  completed_at, created_at, updated_at, ai_generated, metadata
        """

        row = await conn.fetchrow(
            query,
            project_id,
            milestone.title,
            milestone.description,
            milestone.status,
            milestone.target_date,
            milestone.ai_generated
        )

        await release_db_connection(conn)

        result = MilestoneResponse(
            id=row['id'],
            project_id=row['project_id'],
            title=row['title'],
            description=row['description'],
            status=row['status'],
            target_date=row['target_date'],
            completed_at=row['completed_at'],
            ai_generated=row['ai_generated'],
            metadata=row['metadata'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

        logger.info(f"Created milestone {result.id} for project {project_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create milestone for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create milestone")

# Codebase Analysis endpoints
class CodebaseAnalysisRequest(BaseModel):
    repository_url: Optional[str] = None
    repository_path: Optional[str] = None
    analysis_type: str = "comprehensive"  # 'architecture', 'security', 'performance', 'quality', 'comprehensive'

class CodebaseAnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    progress: float
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Documentation Analysis endpoints
class DocumentationAnalysisRequest(BaseModel):
    repository_path: str
    analysis_scope: str = "comprehensive"  # 'structure', 'quality', 'completeness', 'comprehensive'

class DocumentationAnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: Optional[str] = None
    project_id: Optional[int] = None
    analysis_type: Optional[str] = None
    estimated_completion: Optional[str] = None
    progress: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Task Planning Models
class TaskPlanningRequest(BaseModel):
    planning_scope: str
    project_requirements: Optional[List[str]] = []
    methodology: Optional[str] = "agile_scrum"
    team_size: Optional[int] = 4
    timeline_weeks: Optional[int] = 12

class TaskPlanningResponse(BaseModel):
    analysis_id: str
    status: str
    message: Optional[str] = None
    project_id: Optional[int] = None
    planning_scope: Optional[str] = None
    estimated_completion: Optional[str] = None
    progress: Optional[float] = None
    results: Optional[Dict[str, Any]] = None

# Research Analysis Models
class ResearchAnalysisRequest(BaseModel):
    research_topic: str
    research_scope: Optional[str] = "general"
    information_sources: Optional[List[str]] = []
    depth_level: Optional[str] = "comprehensive"

class ResearchAnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: Optional[str] = None
    project_id: Optional[int] = None
    research_topic: Optional[str] = None
    estimated_completion: Optional[str] = None
    progress: Optional[float] = None
    results: Optional[Dict[str, Any]] = None

# QA Testing Models
class QATestingRequest(BaseModel):
    qa_scope: str
    test_categories: Optional[List[str]] = []
    quality_standards: Optional[Dict[str, Any]] = {}
    coverage_target: Optional[int] = 80

class QATestingResponse(BaseModel):
    analysis_id: str
    status: str
    project_id: Optional[int] = None
    progress: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Project Orchestrator Models
class ProjectOrchestratorRequest(BaseModel):
    project_context: Dict[str, Any]
    active_graphs: Optional[List[str]] = []
    coordination_strategy: Optional[str] = "matrix_coordination"
    resource_constraints: Optional[Dict[str, Any]] = {}

class ProjectOrchestratorResponse(BaseModel):
    orchestration_id: str
    status: str
    message: Optional[str] = None
    project_id: Optional[int] = None
    project_context: Optional[Dict[str, Any]] = None
    estimated_completion: Optional[str] = None
    progress: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@projects_router.post("/{project_id}/analyze-codebase", response_model=CodebaseAnalysisResponse)
async def analyze_codebase(project_id: int, request: CodebaseAnalysisRequest, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Start codebase analysis for a project using the specialized graph"""
    try:
        # Verify project exists
        conn = await get_db_connection()

        project = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if not project:
            await release_db_connection(conn)
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            await release_db_connection(conn)
            raise HTTPException(status_code=403, detail="Not authorized to analyze codebase for this project")

        # ... (rest of the code remains the same)

    except Exception as e:
        logger.error(f"Failed to analyze codebase for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze codebase")

@projects_router.post("/{project_id}/analyze-documentation", response_model=DocumentationAnalysisResponse)
async def analyze_documentation(project_id: int, request: DocumentationAnalysisRequest, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Start documentation analysis for a project using the specialized graph"""
    try:
        # Verify project exists
        conn = await get_db_connection()

        project = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if not project:
            await release_db_connection(conn)
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            await release_db_connection(conn)
            raise HTTPException(status_code=403, detail="Not authorized to analyze documentation for this project")

        await release_db_connection(conn)

        # ... (rest of the code remains the same)

    except Exception as e:
        logger.error(f"Failed to analyze documentation for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze documentation")

@projects_router.post("/{project_id}/plan-tasks", response_model=TaskPlanningResponse)
async def plan_tasks(project_id: int, request: TaskPlanningRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Start task planning analysis for a project using the specialized graph"""
    try:
        # Verify project exists
        conn = await get_db_connection()

        project = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if not project:
            await release_db_connection(conn)
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            await release_db_connection(conn)
            raise HTTPException(status_code=403, detail="Not authorized to plan tasks for this project")

        await release_db_connection(conn)

        # ... (rest of the code remains the same)

    except Exception as e:
        logger.error(f"Failed to plan tasks for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to plan tasks")

# ... (rest of the code remains the same)
@projects_router.post("/{project_id}/run-qa", response_model=QATestingResponse)
async def run_qa_analysis(project_id: int, request: QATestingRequest, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Start QA testing analysis for a project using the specialized graph"""
    try:
        conn = await get_db_connection()

        project = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if not project:
            await release_db_connection(conn)
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            await release_db_connection(conn)
            raise HTTPException(status_code=403, detail="Not authorized to run QA on this project")

        await release_db_connection(conn)

        analysis_id = f"qa_testing_{project_id}_{int(datetime.now().timestamp())}"

        try:
            graph = get_specialized_graph("qa_testing")
            if not graph:
                logger.error("QATestingGraph not found in registry.")
                raise HTTPException(status_code=500, detail="QA testing tool is unavailable.")

            initial_state = QualityAssuranceState(
                messages=[HumanMessage(content=f"Execute {request.qa_scope} QA testing for project {project_id}")],
                agent_type="QATestingAgent",
                task_classification={"task_type": "qa_testing"},

                qa_scope=request.qa_scope,
                test_categories=request.test_categories or [],
                quality_standards=request.quality_standards or {},
                coverage_target=request.coverage_target,

                test_results={},
                quality_metrics={},
                compliance_check={},
                qa_stage="started",
                qa_progress=0.0,

                search_query=[],
                web_research_result=[],
                sources_gathered=[],
                initial_search_query_count=0,
                max_research_loops=0,
            )

            config = {"configurable": {"thread_id": analysis_id, "project_id": project_id}}

            logger.debug(f"Invoking QATestingGraph with initial state for analysis {analysis_id}")
            final_state = await graph.ainvoke(initial_state, config=config)

            status = final_state.get("qa_stage", "unknown")
            if status == "complete" or status == "completed":
                status = "completed"
                progress = 1.0
            else:
                progress = final_state.get("qa_progress", 0.0)

            error_msg = None
            if status == "failed":
                error_msg = str(final_state.get("errors", "Unknown error"))

            return QATestingResponse(
                analysis_id=analysis_id,
                status=status,
                project_id=project_id,
                progress=progress,
                results=final_state.get("test_recommendations") or final_state.get("test_results"),
                error=error_msg
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled exception during QA testing {analysis_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to complete QA testing analysis: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start QA testing analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to start QA testing analysis")


@projects_router.post("/{project_id}/orchestrate", response_model=ProjectOrchestratorResponse)
async def orchestrate_project(project_id: int, request: ProjectOrchestratorRequest, current_user: Optional[Dict[str, Any]] = None): # Depends(get_current_user)):
    """Start project orchestration using the specialized graph"""
    try:
        conn = await get_db_connection()

        project = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if not project:
            await release_db_connection(conn)
            raise HTTPException(status_code=404, detail="Project not found")
        if current_user and project['user_id'] != current_user.get('uid'):
            await release_db_connection(conn)
            raise HTTPException(status_code=403, detail="Not authorized to orchestrate this project")

        await release_db_connection(conn)

        orchestration_id = f"orchestrator_{project_id}_{int(datetime.now().timestamp())}"

        try:
            graph = get_specialized_graph("project_orchestrator")
            if not graph:
                logger.error("ProjectOrchestratorGraph not found in registry.")
                raise HTTPException(status_code=500, detail="Project orchestrator tool is unavailable.")

            initial_state = ProjectOrchestratorState(
                messages=[HumanMessage(content="Initiate project orchestration")],
                agent_type="ProjectOrchestratorAgent",
                task_classification={"task_type": "project_orchestration"},

                project_context=request.project_context,
                active_graphs=request.active_graphs or [],
                graph_dependencies={},
                coordination_plan={"strategy": request.coordination_strategy},
                execution_status={},
                resource_allocation=request.resource_constraints or {},
                conflict_resolution={},

                orchestration_stage="started",
                orchestration_progress=0.0,
                efficiency_score=0.0,
                resource_utilization=0.0,
                coordination_recommendations=[],
                optimization_suggestions=[],
                files_updated=[],

                search_query=[],
                web_research_result=[],
                sources_gathered=[],
                initial_search_query_count=0,
                max_research_loops=0,
            )

            config = {"configurable": {"thread_id": orchestration_id, "project_id": project_id}}

            logger.debug(f"Invoking ProjectOrchestratorGraph for project {project_id} with id {orchestration_id}")
            final_state = await graph.ainvoke(initial_state, config=config)

            status = final_state.get("orchestration_stage", "unknown")
            if status in ["complete", "completed"]:
                status = "completed"
                progress = 1.0
            else:
                progress = final_state.get("orchestration_progress", 0.0)

            error_msg = None
            if status == "failed":
                error_msg = str(final_state.get("errors", "Unknown error"))

            return ProjectOrchestratorResponse(
                orchestration_id=orchestration_id,
                status=status,
                project_id=project_id,
                progress=progress,
                results=final_state.get("coordination_recommendations") or final_state.get("optimization_suggestions"),
                error=error_msg
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled exception during project orchestration {orchestration_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to complete project orchestration: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start project orchestration: {e}")
        raise HTTPException(status_code=500, detail="Failed to start project orchestration")
