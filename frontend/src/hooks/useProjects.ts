/**
 * Custom hook for managing projects with the new backend API
 * Integrates with the PostgreSQL database and memory system
 */

import { useState, useEffect, useCallback } from 'react';
import { getApiBaseUrl } from '../config/api';

// Types matching the backend Pydantic models
export interface Project {
  id: number;
  name: string;
  description?: string;
  github_repo_url?: string;
  github_repo_id?: string;
  github_metadata?: Record<string, any>;
  repository_analysis?: string;
  status: string;
  priority: string;
  team?: string;
  user_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  project_id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_to?: string;
  due_date?: string;
  github_issue_id?: string;
  github_issue_url?: string;
  ai_generated: boolean;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface UpdateProjectData {
  name?: string;
  description?: string;
  github_repo_url?: string;
  status?: string;
  priority?: string;
  team?: string;
  user_id?: string;
}

export interface CreateProjectData {
  name: string;
  description?: string;
  github_repo_url?: string;
  status?: string;
  priority?: string;
  team?: string;
  user_id?: string;
}

export interface CodebaseAnalysisRequest {
  repository_url?: string;
  repository_path?: string;
  analysis_type?: 'architecture' | 'security' | 'performance' | 'quality' | 'comprehensive';
}

export interface DocumentationAnalysisRequest {
  repository_url?: string;
  repository_path?: string;
  analysis_scope?: 'structure' | 'quality' | 'completeness' | 'comprehensive';
}

export interface CodebaseAnalysisResponse {
  analysis_id: string;
  status: string;
  progress: number;
  results?: {
    project_id: number;
    repository_url?: string;
    analysis_type: string;
    detected_tech_stack: string[];
    analysis_focus: string[];
    findings: {
      architecture?: {
        score: number;
        patterns_found: string[];
        recommendations: string[];
      };
      security?: {
        score: number;
        vulnerabilities: string[];
        recommendations: string[];
      };
      performance?: {
        score: number;
        bottlenecks: string[];
        recommendations: string[];
      };
      quality?: {
        score: number;
        metrics: Record<string, any>;
        recommendations: string[];
      };
    };
    overall_score: number;
    completion_time: string;
  };
  error?: string;
}

export interface DocumentationAnalysisResponse {
  analysis_id: string;
  status: string;
  progress: number;
  results?: {
    project_id: number;
    repository_url?: string;
    analysis_scope: string;
    overall_score: number;
    analysis_summary: {
      structure_score: number;
      quality_score: number;
      completeness_percentage: number;
      total_documents_found: number;
    };
    discovered_documentation: {
      readme_files: string[];
      api_documentation: string[];
      user_guides: string[];
      developer_docs: string[];
      changelog: string[];
      license: string[];
      code_comments: {
        total: number;
        documented_functions: number;
      };
    };
    recommendations: {
      priority_actions: Array<{
        action: string;
        priority: string;
        effort: string;
        impact: string;
      }>;
      improvement_suggestions: Array<{
        action: string;
        priority: string;
        effort: string;
        impact: string;
      }>;
      estimated_effort: {
        high_priority: string;
        medium_priority: string;
        low_priority: string;
      };
    };
    completion_time: string;
  };
  error?: string;
}

export interface TaskPlanningRequest {
  planning_scope: string;
  project_requirements: string[];
  methodology: string;
  team_size: number;
  timeline_weeks: number;
}

export interface TaskPlanningResponse {
  analysis_id: string;
  status: string;
  message: string;
  project_id: number;
  planning_scope: string;
  estimated_completion: string;
  error?: string;
}

export interface ResearchAnalysisRequest {
  research_topic: string;
  research_scope: string;
  information_sources: string[];
  depth_level: string;
}

export interface ResearchAnalysisResponse {
  analysis_id: string;
  status: string;
  message: string;
  project_id: number;
  research_topic: string;
  estimated_completion: string;
  error?: string;
}

export interface QATestingRequest {
  qa_scope: string;
  test_categories: string[];
  quality_standards: Record<string, any>;
  coverage_target: number;
}

export interface QATestingResponse {
  analysis_id: string;
  status: string;
  message: string;
  project_id: number;
  qa_scope: string;
  estimated_completion: string;
  error?: string;
}

export interface ProjectOrchestratorRequest {
  project_context: Record<string, any>;
  active_graphs: string[];
  coordination_strategy: string;
  resource_constraints: Record<string, any>;
}

export interface ProjectOrchestratorResponse {
  orchestration_id: string;
  status: string;
  message: string;
  project_id: number;
  project_context: Record<string, any>;
  estimated_completion: string;
  error?: string;
}

const API_BASE = `${getApiBaseUrl()}/projects`;

export const useProjects = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update an existing project
  const updateProject = useCallback(
    async (projectId: number, data: UpdateProjectData): Promise<Project | null> => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/${projectId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error(`Failed to update project: ${response.statusText}`);
        }

        const updatedProject: Project = await response.json();
        // Update local state
        setProjects((prev) =>
          prev.map((p) => (p.id === projectId ? updatedProject : p))
        );
        return updatedProject;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update project');
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // Fetch all projects
  const fetchProjects = useCallback(async (filters?: {
    user_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (filters?.user_id) params.append('user_id', filters.user_id);
      if (filters?.status) params.append('status', filters.status);
      if (filters?.limit) params.append('limit', filters.limit.toString());
      if (filters?.offset) params.append('offset', filters.offset.toString());

      const response = await fetch(`${API_BASE}?${params}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch projects: ${response.statusText}`);
      }

      const data = await response.json();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  }, []);

  // Create a new project
  const createProject = useCallback(async (projectData: CreateProjectData): Promise<Project | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(API_BASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData),
      });

      if (!response.ok) {
        throw new Error(`Failed to create project: ${response.statusText}`);
      }

      const newProject = await response.json();
      setProjects(prev => [newProject, ...prev]);
      return newProject;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get a specific project
  const getProject = useCallback(async (projectId: number): Promise<Project | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/${projectId}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch project: ${response.statusText}`);
      }

      const project = await response.json();
      return project;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Analyze project codebase
  const analyzeCodebase = useCallback(async (
    projectId: number,
    analysisRequest: CodebaseAnalysisRequest
  ): Promise<CodebaseAnalysisResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/${projectId}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisRequest),
      });

      if (!response.ok) {
        throw new Error(`Failed to start analysis: ${response.statusText}`);
      }

      const analysisResult = await response.json();
      return analysisResult;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze codebase');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get analysis status
  const getAnalysisStatus = useCallback(async (
    projectId: number,
    analysisId: string
  ): Promise<CodebaseAnalysisResponse | null> => {
    try {
      const response = await fetch(`${API_BASE}/${projectId}/analysis/${analysisId}`);

      if (!response.ok) {
        throw new Error(`Failed to get analysis status: ${response.statusText}`);
      }

      const analysisStatus = await response.json();
      return analysisStatus;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get analysis status');
      return null;
    }
  }, []);

  // Analyze project documentation
  const analyzeDocumentation = useCallback(async (
    projectId: number,
    analysisRequest: DocumentationAnalysisRequest
  ): Promise<DocumentationAnalysisResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/${projectId}/analyze-docs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisRequest),
      });

      if (!response.ok) {
        throw new Error(`Failed to start documentation analysis: ${response.statusText}`);
      }

      const analysisResult = await response.json();
      return analysisResult;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze documentation');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Analyze project tasks (Task Planning)
  const analyzeTasks = useCallback(async (
    projectId: number,
    request: TaskPlanningRequest
  ): Promise<TaskPlanningResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/${projectId}/analyze-tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        throw new Error(`Failed to start task planning analysis: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze tasks');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Analyze project research
  const analyzeResearch = useCallback(async (
    projectId: number,
    request: ResearchAnalysisRequest
  ): Promise<ResearchAnalysisResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/${projectId}/analyze-research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        throw new Error(`Failed to start research analysis: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze research');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Analyze QA testing
  const analyzeQA = useCallback(async (
    projectId: number,
    request: QATestingRequest
  ): Promise<QATestingResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/${projectId}/analyze-qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        throw new Error(`Failed to start QA analysis: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze QA');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Run Code Engineer task on project
  const runCodeEngineer = useCallback(async (
    projectId: number,
    action: string = 'improve_codebase'
  ): Promise<any | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/v1/enhanced/agents/code_engineer/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, action }),
      });
      if (!response.ok) {
        throw new Error(`Failed to create code engineer task: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create code engineer task');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Orchestrate project
  const orchestrateProject = useCallback(async (
    projectId: number,
    request: ProjectOrchestratorRequest
  ): Promise<ProjectOrchestratorResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/${projectId}/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        throw new Error(`Failed to start orchestration: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to orchestrate project');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Load projects on mount
  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    loading,
    error,
    fetchProjects,
    updateProject,
    createProject,
    getProject,
    analyzeCodebase,
    getAnalysisStatus,
    analyzeDocumentation,
    analyzeTasks,
    analyzeResearch,
    analyzeQA,
    runCodeEngineer,
    orchestrateProject,
  };
};
