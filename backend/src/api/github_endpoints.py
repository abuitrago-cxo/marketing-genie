"""
GitHub Integration Endpoints

This module provides API endpoints for GitHub OAuth integration,
repository management, and project analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import httpx

from ..auth.firebase import get_current_user
from ..utils.github_client import github_client, get_user_github_token
from ..utils.public_repo_analyzer import analyze_public_repository
from ..agent.multi_agent_state import run_multi_agent_workflow
from ..database import get_db_connection, release_db_connection
from ..utils.logging_config import logger

router = APIRouter(prefix="/api/v1/github", tags=["GitHub Integration"])

# Request/Response Models
class RepositoryInfo(BaseModel):
    id: int
    name: str
    full_name: str
    description: Optional[str]
    private: bool
    html_url: str
    clone_url: str
    language: Optional[str]
    updated_at: str
    size: int
    stargazers_count: int
    forks_count: int

class ProjectAnalysisRequest(BaseModel):
    repository_full_name: str
    analysis_type: str = "comprehensive"
    include_code_review: bool = True
    include_architecture_analysis: bool = True
    include_improvement_suggestions: bool = True

class ProjectAnalysisResponse(BaseModel):
    repository_info: Dict[str, Any]
    structure_analysis: Dict[str, Any]
    project_type: str
    technologies: List[str]
    complexity_score: int
    ai_analysis: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    timestamp: str

class ProjectImportRequest(BaseModel):
    repository_full_name: str
    import_type: str = "analysis"
    create_project_plan: bool = True
    analyze_codebase: bool = True
    generate_documentation: bool = False

class PublicRepoAnalysisRequest(BaseModel):
    repo_url: str

class GitHubTokenRequest(BaseModel):
    token: str

# Endpoints

@router.post("/token")
async def save_github_token(
    request: GitHubTokenRequest,
    current_user: Optional[Dict[str, Any]] = None 
):
    """Saves or updates the user's GitHub access token."""
    user_id = current_user.get("uid") if current_user else None
    if not user_id:
        # Optionally, raise an error or return a specific response
        # For now, let it proceed, it might fail at DB insertion if user_id is required by DB schema
        logger.warning("Attempting to save GitHub token without a user ID.")
    conn = None
    try:
        conn = await get_db_connection()
        await conn.execute(
            """
            INSERT INTO user_identities (user_id, provider, access_token)
            VALUES ($1, 'github', $2)
            ON CONFLICT (user_id, provider) DO UPDATE
            SET access_token = EXCLUDED.access_token, updated_at = NOW()
            """,
            user_id, request.token
        )
        return {"status": "success", "message": "GitHub token saved successfully."}
    except Exception as e:
        logger.error(f"Failed to save GitHub token for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not save GitHub token.")
    finally:
        if conn:
            await release_db_connection(conn)

@router.post("/public/analyze-by-url")
async def analyze_public_repo_by_url(request: PublicRepoAnalysisRequest):
    """Analyze a public GitHub repository from its URL."""
    try:
        result = analyze_public_repository(request.repo_url)
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to analyze repository.")
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.get("/repositories", response_model=List[RepositoryInfo])
async def get_user_repositories(
    github_token: Optional[str] = None, # Depends(get_user_github_token),
    current_user: Optional[Dict[str, Any]] = None # Depends(get_current_user)
):
    """Get user's GitHub repositories"""
    if not github_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account not connected or token not found."
        )
    try:
        repositories = await github_client.get_user_repositories(github_token)
        return [RepositoryInfo(**repo) for repo in repositories]
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid GitHub token.")
        logger.error(f"GitHub API error fetching repositories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch repositories from GitHub.")
    except Exception as e:
        logger.error(f"Unexpected error fetching repositories: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.get("/repositories/{owner}/{repo}")
async def get_repository_details(
    owner: str,
    repo: str,
    github_token: Optional[str] = None, # Depends(get_user_github_token),
    current_user: Optional[Dict[str, Any]] = None # Depends(get_current_user)
):
    """Get detailed information about a specific repository"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub account not connected.")
    try:
        repository = await github_client.get_repository_details(github_token, owner, repo)
        return repository
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Repository not found.")
        logger.error(f"GitHub API error fetching repo details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch repository details.")
    except Exception as e:
        logger.error(f"Unexpected error fetching repo details: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@router.post("/repositories/{owner}/{repo}/analyze", response_model=ProjectAnalysisResponse)
async def analyze_repository_with_ai(
    owner: str,
    repo: str,
    request: ProjectAnalysisRequest,
    background_tasks: BackgroundTasks,
    github_token: Optional[str] = None, # Depends(get_user_github_token),
    current_user: Optional[Dict[str, Any]] = None # Depends(get_current_user)
):
    """Analyze repository using AI agents"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub account not connected.")
    try:
        repo_details = await github_client.get_repository_details(github_token, owner, repo)
        repo_contents = await github_client.get_repository_contents(github_token, owner, repo)

        analysis_data = {
            "repository_info": repo_details,
            "structure_analysis": {"files": [item["name"] for item in repo_contents if "name" in item]},
            "project_type": "Web Application",
            "technologies": [repo_details.get("language", "N/A")],
            "complexity_score": 8,
        }

        query = create_repository_analysis_query(analysis_data, request)
        ai_result = run_multi_agent_workflow(query)

        user_id_for_log = current_user.get("uid") if current_user else "anonymous_analysis"
        background_tasks.add_task(
            log_repository_analysis, user_id_for_log, repo, analysis_data, ai_result
        )

        return ProjectAnalysisResponse(
            **analysis_data,
            ai_analysis=ai_result,
            recommendations=extract_recommendations_from_ai_result(ai_result),
            timestamp=datetime.utcnow().isoformat(),
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"GitHub API error during analysis: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to communicate with GitHub: {e.response.text}")
    except Exception as e:
        logger.error(f"Failed to analyze repository {owner}/{repo}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze repository: {str(e)}")

@router.post("/repositories/{owner}/{repo}/import", status_code=202)
async def import_repository_project(
    owner: str,
    repo: str,
    request: ProjectImportRequest,
    background_tasks: BackgroundTasks,
    github_token: Optional[str] = None, # Depends(get_user_github_token),
    current_user: Optional[Dict[str, Any]] = None # Depends(get_current_user)
):
    """Import repository as a new project with AI-powered analysis"""
    if not github_token:
        raise HTTPException(status_code=401, detail="GitHub account not connected.")
    try:
        repo_details = await github_client.get_repository_details(github_token, owner, repo)

        analysis_data = {
            "repository_info": repo_details,
            "project_type": "Web Application",
            "technologies": [repo_details.get("language", "N/A")],
        }

        query = create_repository_import_query(analysis_data, request)
        import_result = run_multi_agent_workflow(query)
        project_data = process_import_results(analysis_data, import_result, request)

        user_id_for_log = current_user.get("uid") if current_user else "anonymous_import"
        background_tasks.add_task(
            log_repository_import, user_id_for_log, repo, project_data, import_result
        )

        return {"message": "Repository import started.", "details": project_data}
    except httpx.HTTPStatusError as e:
        logger.error(f"GitHub API error during import: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to communicate with GitHub: {e.response.text}")
    except Exception as e:
        logger.error(f"Failed to import repository {owner}/{repo}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import repository: {str(e)}")

@router.get("/connection-status")
async def get_github_connection_status(
    github_token: Optional[str] = None, # Depends(get_user_github_token),
    current_user: Optional[Dict[str, Any]] = None # Depends(get_current_user)
):
    """Check GitHub connection status for current user"""
    if not github_token:
        return {"status": "disconnected", "message": "GitHub token not found."}
    try:
        await github_client._request("GET", "/user", token=github_token)
        return {"status": "connected", "message": "GitHub account is connected and token is valid."}
    except httpx.HTTPStatusError as e:
        if e.response.status_code in [401, 403]:
            return {"status": "error", "message": "Invalid or expired GitHub token."}
        logger.error(f"GitHub API error checking connection status: {e}")
        return {"status": "error", "message": "Could not verify connection with GitHub."}
    except Exception as e:
        logger.error(f"Unexpected error checking connection status: {e}")
        return {"status": "error", "message": "An unexpected error occurred."}

# Helper Functions

def create_repository_analysis_query(analysis_data: Dict[str, Any], request: ProjectAnalysisRequest) -> str:
    """Create AI query for repository analysis"""
    query = f"""
Analyze the GitHub repository '{analysis_data['repository_info']['full_name']}'.

**Repository Details**:
- **Description**: {analysis_data['repository_info'].get('description', 'N/A')}
- **Language**: {analysis_data['repository_info'].get('language', 'N/A')}
- **Size**: {analysis_data['repository_info'].get('size', 0)} KB
- **Last Updated**: {analysis_data['repository_info'].get('updated_at', 'N/A')}

**Analysis Request**:
- **Type**: {request.analysis_type}
- **Include Code Review**: {request.include_code_review}
- **Include Architecture Analysis**: {request.include_architecture_analysis}
- **Include Improvement Suggestions**: {request.include_improvement_suggestions}

**File Structure**:
{', '.join(analysis_data['structure_analysis']['files'][:20])}...

Based on this information, please provide:
1. A detailed analysis of the project's structure and purpose.
2. An assessment of the code quality and architecture.
3. Actionable recommendations for improvement.
"""
    return query

def create_repository_import_query(analysis_data: Dict[str, Any], request: ProjectImportRequest) -> str:
    """Create AI query for repository import"""
    query = f"""
Import and analyze the GitHub repository '{analysis_data['repository_info']['full_name']}'.

**Project Details**:
**Project Type**: {analysis_data['project_type']}
**Technologies**: {', '.join(analysis_data['technologies'])}

**Import Requirements**:
- Import Type: {request.import_type}
- Create Project Plan: {request.create_project_plan}
- Analyze Codebase: {request.analyze_codebase}
- Generate Documentation: {request.generate_documentation}

Please provide:
1. Comprehensive project analysis
2. Development roadmap and milestones
3. Code quality assessment and improvements
4. Architecture recommendations
5. Testing strategy
6. Documentation plan
7. Risk assessment and mitigation
8. Resource requirements and timeline

Create a complete project management package for this repository.
"""
    return query

def extract_recommendations_from_ai_result(ai_result: Dict[str, Any]) -> List[str]:
    """Extract actionable recommendations from AI analysis"""
    recommendations = []
    final_answer = ai_result.get('final_answer', '')
    lines = final_answer.split('\n')
    current_section = None
    for line in lines:
        line = line.strip()
        if 'recommendation' in line.lower() or 'suggest' in line.lower():
            current_section = 'recommendations'
        elif line.startswith(('-', '•', '*')) and current_section == 'recommendations':
            recommendation = line.lstrip('-•* ').strip()
            if recommendation:
                recommendations.append(recommendation)
    if not recommendations:
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')):
                item = line.lstrip('-•* ').strip()
                if len(item) > 20 and any(word in item.lower() for word in ['should', 'could', 'recommend', 'improve', 'consider']):
                    recommendations.append(item)
    return recommendations[:10]

def process_import_results(analysis_data: Dict[str, Any], import_result: Dict[str, Any], request: ProjectImportRequest) -> Dict[str, Any]:
    """Process and structure import results"""
    return {
        'repository_analysis': analysis_data,
        'ai_insights': {
            'summary': import_result.get('final_answer', ''),
            'quality_score': import_result.get('quality_score', 0),
            'deliverables': import_result.get('deliverables', []),
            'execution_metrics': import_result.get('execution_metrics', {})
        },
        'project_plan': import_result.get('project_plan'),
        'code_artifacts': import_result.get('code_artifacts', []),
        'quality_reports': import_result.get('quality_reports', []),
        'import_settings': {
            'import_type': request.import_type,
            'create_project_plan': request.create_project_plan,
            'analyze_codebase': request.analyze_codebase,
            'generate_documentation': request.generate_documentation
        }
    }

async def log_repository_analysis(user_id: str, repo_name: str, analysis_data: Dict[str, Any], ai_result: Dict[str, Any]):
    """Background task to log repository analysis"""
    try:
        logger.info(f"Repository analysis logged for user {user_id} on repo {repo_name}")
    except Exception as e:
        logger.error(f"Failed to log repository analysis: {e}")

async def log_repository_import(user_id: str, repo_name: str, project_data: Dict[str, Any], import_result: Dict[str, Any]):
    """Background task to log repository import"""
    try:
        logger.info(f"Repository import logged for user {user_id} on repo {repo_name}")
    except Exception as e:
        logger.error(f"Failed to log repository import: {e}")
