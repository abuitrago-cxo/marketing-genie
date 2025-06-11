import { renderHook, waitFor } from '@testing-library/react';
import { useAgents, useWorkflows } from '../useAgents';

// Mock fetch globally
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('useAgents', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('should fetch agents successfully', async () => {
    const mockAgentsData = [
      {
        id: 'codebase-analysis',
        name: 'Code Analysis Specialist',
        type: 'code-engineer',
        description: 'Analyzes codebase structure',
        status: 'active',
        capabilities: ['Code Analysis', 'Dependency Mapping'],
        tasks_completed: 156,
        success_rate: 94.5,
        avg_response_time: 2.3,
        last_activity: '2024-01-27T10:00:00Z',
        is_enabled: true
      }
    ];

    const mockMetricsData = {
      total_agents: 6,
      active_agents: 4,
      busy_agents: 1,
      avg_success_rate: 92.5,
      total_tasks_completed: 1250
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAgentsData,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetricsData,
      } as Response);

    const { result } = renderHook(() => useAgents());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.agents).toHaveLength(1);
    expect(result.current.agents[0].name).toBe('Code Analysis Specialist');
    expect(result.current.metrics?.total_agents).toBe(6);
    expect(result.current.error).toBeNull();
  });

  it('should handle fetch error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useAgents());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.agents).toHaveLength(0);
  });

  it('should toggle agent successfully', async () => {
    const mockAgentsData = [
      {
        id: 'test-agent',
        name: 'Test Agent',
        type: 'research',
        description: 'Test description',
        status: 'active',
        capabilities: ['Testing'],
        tasks_completed: 10,
        success_rate: 90,
        avg_response_time: 1.5,
        last_activity: '2024-01-27T10:00:00Z',
        is_enabled: true
      }
    ];

    // Mock initial fetch
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAgentsData,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ total_agents: 1, active_agents: 1, busy_agents: 0, avg_success_rate: 90, total_tasks_completed: 10 }),
      } as Response)
      // Mock toggle request
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      } as Response)
      // Mock refresh after toggle
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{ ...mockAgentsData[0], is_enabled: false }],
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ total_agents: 1, active_agents: 0, busy_agents: 0, avg_success_rate: 90, total_tasks_completed: 10 }),
      } as Response);

    const { result } = renderHook(() => useAgents());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.agents[0].is_enabled).toBe(true);

    await result.current.toggleAgent('test-agent');

    await waitFor(() => {
      expect(result.current.agents[0].is_enabled).toBe(false);
    });
  });
});

describe('useWorkflows', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('should fetch workflows successfully', async () => {
    const mockWorkflowsData = [
      {
        id: 'workflow-codebase-analysis',
        name: 'Code Analysis Specialist Workflow',
        category: 'code-engineer',
        agent_type: 'codebase-analysis',
        status: 'completed',
        success_rate: 95.5,
        avg_duration: 3.2,
        last_execution: '2024-01-27T09:30:00Z',
        total_executions: 45
      }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockWorkflowsData,
    } as Response);

    const { result } = renderHook(() => useWorkflows());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.workflows).toHaveLength(1);
    expect(result.current.workflows[0].name).toBe('Code Analysis Specialist Workflow');
    expect(result.current.workflows[0].status).toBe('completed');
    expect(result.current.error).toBeNull();
  });

  it('should handle workflow fetch error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('API Error'));

    const { result } = renderHook(() => useWorkflows());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('API Error');
    expect(result.current.workflows).toHaveLength(0);
  });

  it('should refresh workflows', async () => {
    const initialData = [
      {
        id: 'workflow-1',
        name: 'Initial Workflow',
        category: 'test',
        agent_type: 'test-agent',
        status: 'pending',
        success_rate: 80,
        avg_duration: 2.0,
        last_execution: '2024-01-27T08:00:00Z',
        total_executions: 10
      }
    ];

    const updatedData = [
      {
        ...initialData[0],
        status: 'completed',
        total_executions: 11
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => initialData,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => updatedData,
      } as Response);

    const { result } = renderHook(() => useWorkflows());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.workflows[0].status).toBe('pending');
    expect(result.current.workflows[0].total_executions).toBe(10);

    await result.current.refreshWorkflows();

    await waitFor(() => {
      expect(result.current.workflows[0].status).toBe('completed');
      expect(result.current.workflows[0].total_executions).toBe(11);
    });
  });
});
