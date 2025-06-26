import { useState, useEffect, useCallback } from 'react';
import { getApiBaseUrl } from '../config/api';

export interface SpecializedGraph {
  id: string;
  name: string;
  description: string;
  category: 'analysis' | 'planning' | 'research' | 'quality' | 'coordination';
  priority: 'critical' | 'high' | 'medium' | 'low';
  dependencies: string[];
  estimated_duration: string;
  required_tools: string[];
  memory_types: string[];
  workflow_pattern: string;
  node_count: number;
  status: 'healthy' | 'failed' | 'unknown';
}

export interface GraphMetadata {
  graph_id: string;
  metadata: SpecializedGraph;
}

export interface GraphHealthStatus {
  total_graphs: number;
  compiled_graphs: number;
  healthy_graphs: number;
  failed_graphs: string[];
  graph_status: Record<string, 'healthy' | 'failed'>;
}

export interface GraphExecutionRequest {
  graph_id: string;
  input_data: Record<string, any>;
  enable_tracing?: boolean;
  max_iterations?: number;
}

export interface GraphExecutionResult {
  success: boolean;
  graph_id: string;
  result: any;
  metadata: SpecializedGraph;
  execution_complete: boolean;
}

export interface OrchestrationRequest {
  project_context: Record<string, any>;
  query: string;
  graph_inputs?: Record<string, any>;
  enable_tracing?: boolean;
  max_iterations?: number;
}

export interface OrchestrationResult {
  success: boolean;
  orchestration_result: any;
  coordination_plan: any;
  graph_results: Record<string, any>;
  total_graphs_executed: number;
  successful_executions: number;
}

interface UseSpecializedGraphsReturn {
  graphs: SpecializedGraph[];
  healthStatus: GraphHealthStatus | null;
  executionOrder: string[];
  loading: boolean;
  error: string | null;
  refreshGraphs: () => Promise<void>;
  executeGraph: (request: GraphExecutionRequest) => Promise<GraphExecutionResult>;
  orchestrateGraphs: (request: OrchestrationRequest) => Promise<OrchestrationResult>;
  getGraphMetadata: (graphId: string) => Promise<SpecializedGraph | null>;
}

const API_BASE_URL = `${getApiBaseUrl()}/specialized`;

export const useSpecializedGraphs = (): UseSpecializedGraphsReturn => {
  const [graphs, setGraphs] = useState<SpecializedGraph[]>([]);
  const [healthStatus, setHealthStatus] = useState<GraphHealthStatus | null>(null);
  const [executionOrder, setExecutionOrder] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchGraphs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/graphs/available`);
      if (!response.ok) {
        throw new Error(`Failed to fetch graphs: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Convert the graphs object to array format
      const graphsArray = Object.entries(data.graphs).map(([id, metadata]: [string, any]) => ({
        id,
        ...metadata,
        status: data.health_status.graph_status[id] || 'unknown'
      }));

      setGraphs(graphsArray);
      setHealthStatus(data.health_status);
      setExecutionOrder(data.execution_order || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch graphs';
      setError(errorMessage);
      console.error('Error fetching specialized graphs:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const executeGraph = useCallback(async (request: GraphExecutionRequest): Promise<GraphExecutionResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/graphs/execute/${request.graph_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          graph_id: request.graph_id,
          input_data: request.input_data,
          enable_tracing: request.enable_tracing ?? true,
          max_iterations: request.max_iterations ?? 3
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to execute graph: ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to execute graph';
      throw new Error(errorMessage);
    }
  }, []);

  const orchestrateGraphs = useCallback(async (request: OrchestrationRequest): Promise<OrchestrationResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/graphs/orchestrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Failed to orchestrate graphs: ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to orchestrate graphs';
      throw new Error(errorMessage);
    }
  }, []);

  const getGraphMetadata = useCallback(async (graphId: string): Promise<SpecializedGraph | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/graphs/${graphId}/metadata`);
      if (!response.ok) {
        throw new Error(`Failed to fetch graph metadata: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        id: data.graph_id,
        ...data.metadata,
        status: 'healthy' // Assume healthy if we can fetch metadata
      };
    } catch (err) {
      console.error(`Error fetching metadata for graph ${graphId}:`, err);
      return null;
    }
  }, []);

  const refreshGraphs = useCallback(async () => {
    await fetchGraphs();
  }, [fetchGraphs]);

  useEffect(() => {
    fetchGraphs();
  }, [fetchGraphs]);

  return {
    graphs,
    healthStatus,
    executionOrder,
    loading,
    error,
    refreshGraphs,
    executeGraph,
    orchestrateGraphs,
    getGraphMetadata,
  };
};

// Hook for graph health monitoring
export const useGraphHealth = () => {
  const [healthStatus, setHealthStatus] = useState<GraphHealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/graphs/health`);
      if (!response.ok) {
        throw new Error(`Failed to fetch graph health: ${response.statusText}`);
      }

      const data = await response.json();
      setHealthStatus(data.health_status);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch graph health';
      setError(errorMessage);
      console.error('Error fetching graph health:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    
    // Set up periodic health checks every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  return {
    healthStatus,
    loading,
    error,
    refreshHealth: fetchHealth,
  };
};
