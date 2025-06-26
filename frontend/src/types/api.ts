// TypeScript interfaces for backend API responses and requests
// Centralised here for consistent reuse across hooks and components

// ========================= Research =========================
export interface ResearchSource {
  id?: string;
  title: string;
  url: string;
  domain?: string;
  relevance?: number;
  credibility?: number;
  snippet?: string;
}

export interface ResearchResult {
  id: number;
  query: string;
  summary: string;
  sources: ResearchSource[];
  created_at: string; // ISO timestamp
  context_json?: Record<string, any>;
}

export interface CreateResearchData {
  query: string;
  summary: string;
  sources: ResearchSource[];
  context_json?: Record<string, any>;
}

// ========================= System / Metrics =========================
export type SystemHealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'error';

export interface SystemHealth {
  status: SystemHealthStatus;
  postgres_connected: boolean;
  redis_connected: boolean;
  langsmith_connected: boolean;
  specialized_graphs_health: Record<string, SystemHealthStatus>;
  timestamp: string;
}

export interface WorkflowMetrics {
  total_executions: number;
  average_quality_score: number;
  average_execution_time_ms: number;
  per_graph: Array<{
    graph_id: string;
    executions: number;
    avg_quality_score: number;
    avg_execution_time_ms: number;
  }>;
}

export interface AgentPerformanceMetrics {
  tasks_completed: number;
  average_response_time_ms: number;
  average_quality_score: number;
}

export interface AgentMetrics {
  [agent_id: string]: AgentPerformanceMetrics;
}
