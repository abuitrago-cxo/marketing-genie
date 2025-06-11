import { useState, useCallback, useEffect } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface WorkflowStep {
  id: string;
  name: string;
  type: 'code' | 'test' | 'deploy' | 'review' | 'security' | 'docs';
  // Status might not be part of a template, but rather an execution instance.
  // For a template, it might be more about configuration.
  // Let's assume for now the backend provides a default or typical status if relevant for display.
  status?: 'pending' | 'running' | 'completed' | 'failed'; 
  duration?: number; // Expected/average duration for the template step
  agent?: string;    // Suggested or required agent
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'ci-cd' | 'testing' | 'deployment' | 'security' | 'documentation' | 'custom';
  steps: WorkflowStep[];
  isActive?: boolean; // If the template is active and can be run
  lastRun?: string | Date; // ISO string or Date object from backend
  successRate?: number;
  avgDuration?: number;
  triggers?: string[];
  // Add any other relevant fields from your mock data or backend
  // For example, input schema, default parameters, etc.
  inputSchema?: Record<string, any>; // Example: { "branch": "string", "commit_sha": "string" }
}

export interface WorkflowRunRequest {
  template_id: string;
  input_data?: Record<string, any>;
  // any other parameters needed to start a workflow
}

export interface WorkflowRunResponse {
  execution_id: string;
  message: string;
  // other details about the initiated run
}

interface UseWorkflowTemplatesReturn {
  templates: WorkflowTemplate[];
  loading: boolean;
  error: string | null;
  fetchTemplates: () => Promise<void>;
  runWorkflow: (request: WorkflowRunRequest) => Promise<WorkflowRunResponse>;
}

export const useWorkflowTemplates = (): UseWorkflowTemplatesReturn => {
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/workflows/templates`);
      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to fetch workflow templates: ${response.status} ${errorData || response.statusText}`);
      }
      const data: WorkflowTemplate[] = await response.json();
      // Process dates if necessary (e.g., string to Date object)
      const processedTemplates = data.map(template => ({
        ...template,
        lastRun: template.lastRun ? new Date(template.lastRun) : undefined,
      }));
      setTemplates(processedTemplates);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      console.error('Error fetching workflow templates:', err);
      setError(errorMessage);
      setTemplates([]); // Clear templates on error
    } finally {
      setLoading(false);
    }
  }, []);

  const runWorkflow = useCallback(async (request: WorkflowRunRequest): Promise<WorkflowRunResponse> => {
    // Note: setLoading/setError for this specific action can be handled differently,
    // e.g., by returning a promise that the component can use to set its own loading state for the run action.
    try {
      const response = await fetch(`${API_BASE_URL}/workflows/run/${request.template_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request.input_data || {}),
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`Failed to run workflow ${request.template_id}: ${response.status} ${errorData || response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred while running the workflow';
      console.error(`Error running workflow ${request.template_id}:`, err);
      // Re-throw the error so the calling component can handle it (e.g., show a notification)
      throw new Error(errorMessage);
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  return {
    templates,
    loading,
    error,
    fetchTemplates, // Expose fetchTemplates for manual refresh if needed
    runWorkflow,
  };
};
