"""
GitHub Integration Endpoints

This module provides API endpoints for GitHub OAuth integration,
repository management, and project analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from auth.auth0_config import get_current_user, get_user_github_token, github_integration
from agent.multi_agent_state import run_multi_agent_workflow


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
    analysis_type: str = "comprehensive"  # basic, comprehensive, detailed
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
    import_type: str = "analysis"  # analysis, planning, development
    create_project_plan: bool = True
    analyze_codebase: bool = True
    generate_documentation: bool = False


# Endpoints

@router.get("/repositories", response_model=List[RepositoryInfo])
async def get_user_repositories(
    user: Dict[str, Any] = Depends(get_current_user),
    github_token: Optional[str] = Depends(get_user_github_token)
):
    """Get user's GitHub repositories"""
    
    if not github_token:
        raise HTTPException(
            status_code=401, 
            detail="GitHub account not connected. Please connect your GitHub account in Auth0."
        )
    
    try:
        repositories = await github_integration.get_user_repositories(github_token)
        
        return [RepositoryInfo(**repo) for repo in repositories]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch repositories: {str(e)}"
        )


@router.get("/repositories/{owner}/{repo}")
async def get_repository_details(
    owner: str,
    repo: str,
    user: Dict[str, Any] = Depends(get_current_user),
    github_token: Optional[str] = Depends(get_user_github_token)
):
    """Get detailed information about a specific repository"""
    
    if not github_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account not connected"
        )
    
    try:
        repo_full_name = f"{owner}/{repo}"
        analysis = await github_integration.analyze_repository_structure(github_token, repo_full_name)
        
        if not analysis['success']:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found or access denied: {analysis.get('error', 'Unknown error')}"
            )
        
        return analysis['analysis']
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze repository: {str(e)}"
        )


@router.post("/repositories/{owner}/{repo}/analyze", response_model=ProjectAnalysisResponse)
async def analyze_repository_with_ai(
    owner: str,
    repo: str,
    request: ProjectAnalysisRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user),
    github_token: Optional[str] = Depends(get_user_github_token)
):
    """Analyze repository using AI agents"""
    
    if not github_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account not connected"
        )
    
    try:
        repo_full_name = f"{owner}/{repo}"
        
        # Get basic repository analysis
        basic_analysis = await github_integration.analyze_repository_structure(github_token, repo_full_name)
        
        if not basic_analysis['success']:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found: {basic_analysis.get('error', 'Unknown error')}"
            )
        
        analysis_data = basic_analysis['analysis']
        
        # Create AI analysis query
        ai_query = create_repository_analysis_query(analysis_data, request)
        
        # Run multi-agent analysis
        ai_result = await run_multi_agent_workflow(
            ai_query,
            config={
                "configurable": {
                    "max_iterations": 2,
                    "enable_tracing": True,
                    "user_id": user['user_id'],
                    "context": {
                        "repository": repo_full_name,
                        "analysis_type": request.analysis_type
                    }
                }
            }
        )
        
        # Extract recommendations from AI analysis
        recommendations = extract_recommendations_from_ai_result(ai_result)
        
        # Log analysis in background
        background_tasks.add_task(
            log_repository_analysis,
            user['user_id'],
            repo_full_name,
            analysis_data,
            ai_result
        )
        
        return ProjectAnalysisResponse(
            repository_info=analysis_data['repository_info'],
            structure_analysis=analysis_data['structure_analysis'],
            project_type=analysis_data['project_type'],
            technologies=analysis_data['technologies'],
            complexity_score=analysis_data['complexity_score'],
            ai_analysis={
                'final_answer': ai_result['final_answer'],
                'quality_score': ai_result.get('quality_score', 0),
                'execution_metrics': ai_result.get('execution_metrics', {}),
                'citations': ai_result.get('citations', [])
            },
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze repository with AI: {str(e)}"
        )


@router.post("/repositories/{owner}/{repo}/import")
async def import_repository_project(
    owner: str,
    repo: str,
    request: ProjectImportRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user),
    github_token: Optional[str] = Depends(get_user_github_token)
):
    """Import repository as a new project with AI-powered analysis"""
    
    if not github_token:
        raise HTTPException(
            status_code=401,
            detail="GitHub account not connected"
        )
    
    try:
        repo_full_name = f"{owner}/{repo}"
        
        # Get repository analysis
        analysis = await github_integration.analyze_repository_structure(github_token, repo_full_name)
        
        if not analysis['success']:
            raise HTTPException(
                status_code=404,
                detail=f"Repository not found: {analysis.get('error', 'Unknown error')}"
            )
        
        # Create comprehensive import query
        import_query = create_repository_import_query(analysis['analysis'], request)
        
        # Run multi-agent workflow for project import
        import_result = await run_multi_agent_workflow(
            import_query,
            config={
                "configurable": {
                    "max_iterations": 3,
                    "enable_tracing": True,
                    "user_id": user['user_id'],
                    "context": {
                        "repository": repo_full_name,
                        "import_type": request.import_type,
                        "create_project_plan": request.create_project_plan,
                        "analyze_codebase": request.analyze_codebase
                    }
                }
            }
        )
        
        # Process import results
        project_data = process_import_results(analysis['analysis'], import_result, request)
        
        # Log import in background
        background_tasks.add_task(
            log_repository_import,
            user['user_id'],
            repo_full_name,
            project_data,
            import_result
        )
        
        return {
            "success": True,
            "project_id": f"github_{repo_full_name.replace('/', '_')}_{int(datetime.now().timestamp())}",
            "repository": repo_full_name,
            "project_data": project_data,
            "ai_analysis": {
                'final_answer': import_result['final_answer'],
                'deliverables': import_result.get('deliverables', []),
                'project_plan': import_result.get('project_plan'),
                'code_artifacts': import_result.get('code_artifacts', []),
                'quality_reports': import_result.get('quality_reports', [])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import repository: {str(e)}"
        )


@router.get("/connection/status")
async def get_github_connection_status(
    user: Dict[str, Any] = Depends(get_current_user),
    github_token: Optional[str] = Depends(get_user_github_token)
):
    """Check GitHub connection status for current user"""
    
    return {
        "connected": github_token is not None,
        "user_id": user['user_id'],
        "connection_time": datetime.now().isoformat() if github_token else None,
        "permissions": ["read:user", "repo"] if github_token else []
    }


# Helper Functions

def create_repository_analysis_query(analysis_data: Dict[str, Any], request: ProjectAnalysisRequest) -> str:
    """Create AI query for repository analysis"""
    
    repo_info = analysis_data['repository_info']
    structure = analysis_data['structure_analysis']
    
    query = f"""
Analyze this GitHub repository for software project management insights:

**Repository**: {repo_info['name']}
**Description**: {repo_info.get('description', 'No description')}
**Language**: {repo_info.get('language', 'Unknown')}
**Project Type**: {analysis_data['project_type']}
**Technologies**: {', '.join(analysis_data['technologies'])}
**Complexity Score**: {analysis_data['complexity_score']}/10

**Structure Analysis**:
- Total Files: {structure['total_files']}
- Directories: {structure['total_directories']}
- File Types: {structure['file_types']}

**Analysis Requirements**:
- Analysis Type: {request.analysis_type}
- Include Code Review: {request.include_code_review}
- Include Architecture Analysis: {request.include_architecture_analysis}
- Include Improvement Suggestions: {request.include_improvement_suggestions}

Please provide:
1. Project assessment and quality evaluation
2. Architecture and code structure analysis
3. Technology stack evaluation
4. Development best practices assessment
5. Improvement recommendations
6. Potential risks and challenges
7. Suggested next steps for development

Focus on actionable insights for project management and development planning.
"""
    
    return query


def create_repository_import_query(analysis_data: Dict[str, Any], request: ProjectImportRequest) -> str:
    """Create AI query for repository import"""
    
    repo_info = analysis_data['repository_info']
    
    query = f"""
Import and analyze this GitHub repository for comprehensive project management:

**Repository**: {repo_info['name']}
**Description**: {repo_info.get('description', 'No description')}
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
    
    # Simple extraction - in production, this would be more sophisticated
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
    
    # If no specific recommendations found, extract general insights
    if not recommendations:
        # Extract bullet points that look like recommendations
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')):
                item = line.lstrip('-•* ').strip()
                if len(item) > 20 and any(word in item.lower() for word in ['should', 'could', 'recommend', 'improve', 'consider']):
                    recommendations.append(item)
    
    return recommendations[:10]  # Limit to top 10 recommendations


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
        # In production, this would log to database or analytics service
        print(f"Repository analysis logged: {user_id} analyzed {repo_name}")
    except Exception as e:
        print(f"Failed to log repository analysis: {e}")


async def log_repository_import(user_id: str, repo_name: str, project_data: Dict[str, Any], import_result: Dict[str, Any]):
    """Background task to log repository import"""
    try:
        # In production, this would log to database or analytics service
        print(f"Repository import logged: {user_id} imported {repo_name}")
    except Exception as e:
        print(f"Failed to log repository import: {e}")
