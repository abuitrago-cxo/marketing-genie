import { useState, useCallback, useEffect } from 'react';
import { getApiBaseUrl } from '../config/api';
import {
  ResearchResult,
  ResearchSource,
  CreateResearchData,
} from '../types/api';

const API_BASE_URL = `${getApiBaseUrl()}/research-results`;

interface UseResearchAgentReturn {
  researchTasks: ResearchResult[];
  loading: boolean;
  error: string | null;
  fetchResearchTasks: () => Promise<void>;
  createResearchTask: (data: CreateResearchData) => Promise<ResearchResult | null>;
}

export const useResearchAgent = (): UseResearchAgentReturn => {
  const [researchTasks, setResearchTasks] = useState<ResearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResearchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: ResearchResult[] = await response.json();
      setResearchTasks(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch research tasks');
      console.error('Failed to fetch research tasks:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  const createResearchTask = useCallback(
    async (data: CreateResearchData): Promise<ResearchResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Failed to create research task. Invalid JSON response.' }));
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        const newResearchTask: ResearchResult = await response.json();
        setResearchTasks((prevTasks) => [newResearchTask, ...prevTasks]);
        return newResearchTask;
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to create research task');
        console.error('Failed to create research task:', e);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    fetchResearchTasks();
  }, [fetchResearchTasks]);

  return {
    researchTasks,
    loading,
    error,
    fetchResearchTasks,
    createResearchTask,
  };
};
