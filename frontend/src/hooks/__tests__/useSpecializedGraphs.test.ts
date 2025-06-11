import { renderHook, waitFor } from '@testing-library/react';
import { useSpecializedGraphs, useGraphHealth } from '../useSpecializedGraphs';

// Mock fetch globally
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('useSpecializedGraphs', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  const mockGraphsResponse = {
    graphs: {
      'codebase_analysis': {
        name: 'Codebase Analysis',
        description: 'Analyze codebase architecture and quality',
        category: 'analysis',
        priority: 'high',
        dependencies: [],
        estimated_duration: '15-20 minutes',
        required_tools: ['file_operations', 'code_analysis'],
        memory_types: ['analysis_pattern', 'code_insight'],
        workflow_pattern: 'route_analysis → generate_queries → execute_analysis → reflection_gaps → finalize_analysis',
        node_count: 5
      },
      'documentation_analysis': {
        name: 'Documentation Analysis',
        description: 'Analyze documentation quality and completeness',
        category: 'analysis',
        priority: 'medium',
        dependencies: [],
        estimated_duration: '10-15 minutes',
        required_tools: ['file_operations', 'web_operations'],
        memory_types: ['documentation_pattern', 'quality_standard'],
        workflow_pattern: 'discover_docs → analyze_structure → evaluate_quality → check_completeness → generate_recommendations',
        node_count: 5
      }
    },
    health_status: {
      total_graphs: 6,
      compiled_graphs: 6,
      healthy_graphs: 5,
      failed_graphs: ['task_planning'],
      graph_status: {
        'codebase_analysis': 'healthy',
        'documentation_analysis': 'healthy',
        'task_planning': 'failed',
        'research_analysis': 'healthy',
        'qa_testing': 'healthy',
        'project_orchestrator': 'healthy'
      }
    },
    execution_order: [
      'codebase_analysis',
      'documentation_analysis',
      'task_planning',
      'research_analysis',
      'qa_testing',
      'project_orchestrator'
    ]
  };

  it('should fetch graphs successfully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockGraphsResponse,
    } as Response);

    const { result } = renderHook(() => useSpecializedGraphs());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.graphs).toHaveLength(2);
    expect(result.current.graphs[0]).toMatchObject({
      id: 'codebase_analysis',
      name: 'Codebase Analysis',
      category: 'analysis',
      status: 'healthy'
    });
    expect(result.current.healthStatus).toEqual(mockGraphsResponse.health_status);
    expect(result.current.executionOrder).toEqual(mockGraphsResponse.execution_order);
    expect(result.current.error).toBeNull();
  });

  it('should handle fetch error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useSpecializedGraphs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.graphs).toEqual([]);
  });

  it('should execute graph successfully', async () => {
    const mockExecutionResult = {
      success: true,
      graph_id: 'codebase_analysis',
      result: {
        final_analysis_report: {
          overall_score: 8.5,
          recommendations: []
        }
      },
      metadata: mockGraphsResponse.graphs.codebase_analysis,
      execution_complete: true
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockGraphsResponse,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockExecutionResult,
      } as Response);

    const { result } = renderHook(() => useSpecializedGraphs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const executionRequest = {
      graph_id: 'codebase_analysis',
      input_data: {
        repository_url: 'https://github.com/example/repo',
        analysis_type: 'comprehensive'
      },
      enable_tracing: true,
      max_iterations: 3
    };

    const executionResult = await result.current.executeGraph(executionRequest);

    expect(executionResult).toEqual(mockExecutionResult);
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/v1/specialized/graphs/execute/codebase_analysis',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          graph_id: 'codebase_analysis',
          input_data: {
            repository_url: 'https://github.com/example/repo',
            analysis_type: 'comprehensive'
          },
          enable_tracing: true,
          max_iterations: 3
        }),
      })
    );
  });

  it('should orchestrate graphs successfully', async () => {
    const mockOrchestrationResult = {
      success: true,
      orchestration_result: {
        project_analysis_complete: true,
        overall_score: 8.2
      },
      coordination_plan: {
        execution_order: ['codebase_analysis', 'documentation_analysis'],
        estimated_total_duration: '25-35 minutes'
      },
      graph_results: {
        'codebase_analysis': { score: 8.5 },
        'documentation_analysis': { score: 7.9 }
      },
      total_graphs_executed: 2,
      successful_executions: 2
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockGraphsResponse,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOrchestrationResult,
      } as Response);

    const { result } = renderHook(() => useSpecializedGraphs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const orchestrationRequest = {
      project_context: {
        repository: 'example/repo',
        type: 'web_app'
      },
      query: 'Analyze this project comprehensively',
      enable_tracing: true,
      max_iterations: 3
    };

    const orchestrationResult = await result.current.orchestrateGraphs(orchestrationRequest);

    expect(orchestrationResult).toEqual(mockOrchestrationResult);
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/v1/specialized/graphs/orchestrate',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orchestrationRequest),
      })
    );
  });

  it('should get graph metadata successfully', async () => {
    const mockMetadata = {
      graph_id: 'codebase_analysis',
      metadata: mockGraphsResponse.graphs.codebase_analysis
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockGraphsResponse,
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetadata,
      } as Response);

    const { result } = renderHook(() => useSpecializedGraphs());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    const metadata = await result.current.getGraphMetadata('codebase_analysis');

    expect(metadata).toMatchObject({
      id: 'codebase_analysis',
      name: 'Codebase Analysis',
      category: 'analysis',
      status: 'healthy'
    });
  });
});

describe('useGraphHealth', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    jest.clearAllTimers();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should fetch health status successfully', async () => {
    const mockHealthResponse = {
      health_status: {
        total_graphs: 6,
        compiled_graphs: 6,
        healthy_graphs: 5,
        failed_graphs: ['task_planning'],
        graph_status: {
          'codebase_analysis': 'healthy',
          'documentation_analysis': 'healthy',
          'task_planning': 'failed',
          'research_analysis': 'healthy',
          'qa_testing': 'healthy',
          'project_orchestrator': 'healthy'
        }
      }
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockHealthResponse,
    } as Response);

    const { result } = renderHook(() => useGraphHealth());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.healthStatus).toEqual(mockHealthResponse.health_status);
    expect(result.current.error).toBeNull();
  });

  it('should refresh health status periodically', async () => {
    const mockHealthResponse = {
      health_status: {
        total_graphs: 6,
        compiled_graphs: 6,
        healthy_graphs: 5,
        failed_graphs: [],
        graph_status: {}
      }
    };

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockHealthResponse,
    } as Response);

    renderHook(() => useGraphHealth());

    // Initial call
    expect(mockFetch).toHaveBeenCalledTimes(1);

    // Fast-forward 30 seconds
    jest.advanceTimersByTime(30000);

    // Should have been called again
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });
});
