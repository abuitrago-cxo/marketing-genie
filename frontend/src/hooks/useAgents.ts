import { useState, useEffect, useCallback } from 'react';
import { getApiBaseUrl } from '../config/api';

export interface Agent {
  id: string;
  name: string;
  type: 'research' | 'devops' | 'analysis' | 'communication' | 'code-engineer' | 'project-manager' | 'qa-specialist';
  description: string;
  status: 'active' | 'idle' | 'busy' | 'offline';
  capabilities: string[];
  current_task?: string;
  tasks_completed: number;
  success_rate: number;
  avg_response_time: number;
  last_activity: Date;
  is_enabled: boolean;
}

export interface AgentMetrics {
  total_agents: number;
  active_agents: number;
  busy_agents: number;
  avg_success_rate: number;
  total_tasks_completed: number;
}

interface UseAgentsReturn {
  agents: Agent[];
  metrics: AgentMetrics | null;
  loading: boolean;
  error: string | null;
  refreshAgents: () => Promise<void>;
  toggleAgent: (agentId: string) => Promise<void>;
}

const API_BASE_URL = getApiBaseUrl();

export const useAgents = (): UseAgentsReturn => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAgents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/agents/status`);
      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.statusText}`);
      }

      const agentsData = await response.json();
      
      // Convert date strings to Date objects
      const processedAgents = agentsData.map((agent: any) => ({
        ...agent,
        last_activity: new Date(agent.last_activity)
      }));

      setAgents(processedAgents);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch agents';
      setError(errorMessage);
      console.error('Error fetching agents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents/metrics`);
      if (!response.ok) {
        throw new Error(`Failed to fetch metrics: ${response.statusText}`);
      }

      const metricsData = await response.json();
      setMetrics(metricsData);
    } catch (err) {
      console.error('Error fetching metrics:', err);
      // Don't set error for metrics as it's not critical
    }
  }, []);

  const refreshAgents = useCallback(async () => {
    await Promise.all([fetchAgents(), fetchMetrics()]);
  }, [fetchAgents, fetchMetrics]);

  const toggleAgent = useCallback(async (agentId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/agents/${agentId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to toggle agent: ${response.statusText}`);
      }

      // Update local state optimistically
      setAgents(prev => prev.map(agent =>
        agent.id === agentId
          ? { ...agent, is_enabled: !agent.is_enabled }
          : agent
      ));

      // Refresh data to get latest state
      await refreshAgents();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to toggle agent';
      setError(errorMessage);
      console.error('Error toggling agent:', err);
    }
  }, [refreshAgents]);

  useEffect(() => {
    refreshAgents();
  }, [refreshAgents]);

  return {
    agents,
    metrics,
    loading,
    error,
    refreshAgents,
    toggleAgent,
  };
};

// Hook for workflow history
export interface WorkflowExecution {
  id: string;
  name: string;
  category: string;
  agent_type: string;
  status: 'completed' | 'running' | 'failed' | 'pending';
  success_rate: number;
  avg_duration: number;
  last_execution: Date;
  total_executions: number;
}

interface UseWorkflowsReturn {
  workflows: WorkflowExecution[];
  loading: boolean;
  error: string | null;
  refreshWorkflows: () => Promise<void>;
}

export const useWorkflows = (): UseWorkflowsReturn => {
  const [workflows, setWorkflows] = useState<WorkflowExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/workflows/history`);
      if (!response.ok) {
        throw new Error(`Failed to fetch workflows: ${response.statusText}`);
      }

      const workflowsData = await response.json();
      
      // Convert date strings to Date objects
      const processedWorkflows = workflowsData.map((workflow: any) => ({
        ...workflow,
        last_execution: new Date(workflow.last_execution)
      }));

      setWorkflows(processedWorkflows);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch workflows';
      setError(errorMessage);
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshWorkflows = useCallback(async () => {
    await fetchWorkflows();
  }, [fetchWorkflows]);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  return {
    workflows,
    loading,
    error,
    refreshWorkflows,
  };
};
