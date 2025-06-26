/**
 * API configuration for the application
 * This provides a consistent way to get API URLs based on the deployment environment
 */

// Base URL configuration for API endpoints
export const getApiBaseUrl = (): string => {
  // When accessing through the /app path, we need to ensure API calls work correctly
  const isAppPath = window.location.pathname.startsWith('/app');
  
  // Production/Docker environment
  if (window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1') {
    // For local development via docker, add /app prefix when needed
    return isAppPath ? '/app/api/v1' : '/api/v1';
  }
  
  // Other environments (could expand for staging, production, etc.)
  return '/api/v1';
};

// Specific API endpoints
export const API_ENDPOINTS = {
  AGENTS: {
    BASE: '/api/v1/enhanced/agents',
    CODE_ENGINEER_TASKS: '/api/v1/enhanced/agents/code_engineer/tasks'
  },
  // Enhanced endpoints
  ENHANCED: {
    TOOLS_REGISTRY: `${getApiBaseUrl()}/enhanced/tools/registry`,
    TOOLS_EXECUTE: `${getApiBaseUrl()}/enhanced/tools/execute`,
    SYSTEM_STATUS: `${getApiBaseUrl()}/enhanced/status`,
  },
  
  // Projects endpoints
  PROJECTS: {
    BASE: `${getApiBaseUrl()}/projects`,
    DETAILS: (id: number) => `${getApiBaseUrl()}/projects/${id}`,
    TASKS: (id: number) => `${getApiBaseUrl()}/projects/${id}/tasks`,
    MILESTONES: (id: number) => `${getApiBaseUrl()}/projects/${id}/milestones`,
  },
  
  // Specialized endpoints
  SPECIALIZED: {
    BASE: `${getApiBaseUrl()}/specialized`,
    QUERY: `${getApiBaseUrl()}/specialized/query`,
    FEEDBACK: `${getApiBaseUrl()}/specialized/feedback`,
    HEALTH: `${getApiBaseUrl()}/specialized/health`,
    METRICS: `${getApiBaseUrl()}/specialized/metrics`,
  },
  
  // GitHub endpoints
  GITHUB: {
    BASE: `${getApiBaseUrl()}/github`,
    REPOSITORIES: `${getApiBaseUrl()}/github/repositories`,
    TOKEN: `${getApiBaseUrl()}/github/token`,
    CONNECTION_STATUS: `${getApiBaseUrl()}/github/connection-status`,
  },
};
