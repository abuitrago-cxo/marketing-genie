import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// import { useAuth } from '../auth/Auth0Provider'; // Auth0 removed
import { API_ENDPOINTS } from '@/config/api';
import ErrorState from '@/components/ui/ErrorState';

// Types
interface Repository {
  id: number;
  name: string;
  full_name: string;
  description: string | null;
  private: boolean;
  html_url: string;
  clone_url: string;
  language: string | null;
  updated_at: string;
  size: number;
  stargazers_count: number;
  forks_count: number;
}

interface RepositoryAnalysis {
  repository_info: {
    name: string;
    description: string;
    language: string;
    size: number;
    stars: number;
    forks: number;
  };
  structure_analysis: {
    total_files: number;
    total_directories: number;
    file_types: Record<string, number>;
  };
  project_type: string;
  technologies: string[];
  complexity_score: number;
  ai_analysis?: {
    final_answer: string;
    quality_score: number;
    citations: any[];
  };
  recommendations?: string[];
}

export const GitHubRepositories: React.FC = () => {
  const navigate = useNavigate();
  // const { getAccessTokenSilently, githubConnected } = useAuth(); // Auth0 removed
  const githubConnected = true;

  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [analysis, setAnalysis] = useState<RepositoryAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Fetch repositories
  const fetchRepositories = async () => {
    // if (!githubConnected) return; // Auth0 removed, placeholder above

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(API_ENDPOINTS.GITHUB.REPOSITORIES);

      if (!response.ok) {
        throw new Error(`Failed to fetch repositories: ${response.statusText}`);
      }

      const data = await response.json();
      setRepositories(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch repositories');
    } finally {
      setLoading(false);
    }
  };

  // Analyze repository
  const analyzeRepository = async (repo: Repository) => {
    setAnalyzing(true);
    setError(null);

    try {
        const [owner, repoName] = repo.full_name.split('/');
      
      const response = await fetch(`${API_ENDPOINTS.GITHUB.BASE}/repositories/${owner}/${repoName}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          repository_full_name: repo.full_name,
          analysis_type: 'comprehensive',
          include_code_review: true,
          include_architecture_analysis: true,
          include_improvement_suggestions: true
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const analysisData = await response.json();
      setAnalysis(analysisData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  // Import repository
  const importRepository = async (repo: Repository) => {
    try {
        const [owner, repoName] = repo.full_name.split('/');
      
      const response = await fetch(`${API_ENDPOINTS.GITHUB.BASE}/repositories/${owner}/${repoName}/import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          repository_full_name: repo.full_name,
          import_type: 'comprehensive',
          create_project_plan: true,
          analyze_codebase: true,
          generate_documentation: true
        })
      });

      if (!response.ok) {
        throw new Error(`Import failed: ${response.statusText}`);
      }

      const importData = await response.json();
      if (importData?.project_id) {
        navigate(`/projects?runEngineer=${importData.project_id}`);
      }
      // Trigger Code Engineer agent task for the imported project
        try {
          await fetch(API_ENDPOINTS.AGENTS.CODE_ENGINEER_TASKS, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              project_id: importData.project_id,
              action: 'improve_codebase'
            })
          });
        } catch (e) {
          console.error('Failed to create code engineer task', e);
        }
        alert(`Repository imported successfully! Project ID: ${importData.project_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    }
  };

  useEffect(() => {
    if (githubConnected) {
      fetchRepositories();
    }
  }, [githubConnected]);

  if (!githubConnected) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No GitHub Connection</h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Connect your GitHub account to view and analyze repositories.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          GitHub Repositories
        </h2>
        <button
          onClick={fetchRepositories}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <ErrorState message={error} onRetry={fetchRepositories} className="my-4" />
      )}

      {/* Repository List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {repositories.map((repo) => (
          <div
            key={repo.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                  {repo.name}
                </h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {repo.description || 'No description'}
                </p>
              </div>
              {repo.private && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                  Private
                </span>
              )}
            </div>

            <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
              {repo.language && (
                <span className="flex items-center">
                  <span className="w-3 h-3 rounded-full bg-blue-500 mr-1"></span>
                  {repo.language}
                </span>
              )}
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                {repo.stargazers_count}
              </span>
              <span className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7.707 3.293a1 1 0 010 1.414L5.414 7H11a7 7 0 017 7v2a1 1 0 11-2 0v-2a5 5 0 00-5-5H5.414l2.293 2.293a1 1 0 11-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                {repo.forks_count}
              </span>
            </div>

            <div className="mt-6 flex space-x-3">
              <button
                onClick={() => {
                  setSelectedRepo(repo);
                  analyzeRepository(repo);
                }}
                disabled={analyzing}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
              >
                {analyzing && selectedRepo?.id === repo.id ? 'Analyzing...' : 'Analyze'}
              </button>
              <button
                onClick={() => importRepository(repo)}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors"
              >
                Import
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Analysis Results */}
      {analysis && selectedRepo && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Analysis Results: {selectedRepo.name}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Project Overview</h4>
              <dl className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <dt className="text-gray-500 dark:text-gray-400">Type:</dt>
                  <dd className="text-gray-900 dark:text-white">{analysis.project_type}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500 dark:text-gray-400">Complexity:</dt>
                  <dd className="text-gray-900 dark:text-white">{analysis.complexity_score}/10</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-gray-500 dark:text-gray-400">Files:</dt>
                  <dd className="text-gray-900 dark:text-white">{analysis.structure_analysis.total_files}</dd>
                </div>
              </dl>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Technologies</h4>
              <div className="flex flex-wrap gap-2">
                {analysis.technologies.map((tech, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {analysis.ai_analysis && (
            <div className="mt-6">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">AI Analysis</h4>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {analysis.ai_analysis.final_answer}
                </p>
              </div>
            </div>
          )}

          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <div className="mt-6">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Recommendations</h4>
              <ul className="space-y-2">
                {analysis.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="flex-shrink-0 w-1.5 h-1.5 bg-blue-600 rounded-full mt-2 mr-3"></span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && repositories.length === 0 && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">Loading repositories...</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && repositories.length === 0 && !error && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No repositories found</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            No repositories were found in your GitHub account.
          </p>
        </div>
      )}
    </div>
  );
};
