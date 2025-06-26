import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Activity,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  BarChart3,
  Users,
  Zap,
  Globe,
  GitBranch,
  Brain
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { AgentMetricsDisplay } from './AgentMetricsDisplay';
import { useSpecializedGraphs } from '@/hooks/useSpecializedGraphs';
import { getApiBaseUrl } from '@/config/api';
import ErrorState from '@/components/ui/ErrorState';

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy' | 'error';
  timestamp: string;
  agents: {
    research_agent: { operational: boolean; last_execution: string };
    analysis_agent: { operational: boolean; last_execution: string };
    synthesis_agent: { operational: boolean; last_execution: string };
  };
  workflow: {
    success_rate: number;
    avg_quality: number;
    total_executions: number;
  };
  langsmith_connected: boolean;
}

interface WorkflowMetrics {
  total_workflows: number;
  successful_workflows: number;
  failed_workflows: number;
  avg_execution_time: number;
  avg_quality_score: number;
  success_rate: number;
  time_range_hours: number;
}

interface SpecializedDashboardProps {
  className?: string;
}

const SystemStatusCard: React.FC<{ health: SystemHealth }> = ({ health }) => {
  const getStatusColor = (status: SystemHealth['status']) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'unhealthy':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'error':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
    }
  };

  const getStatusIcon = (status: SystemHealth['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle size={16} className="text-green-600" />;
      case 'degraded':
        return <AlertCircle size={16} className="text-yellow-600" />;
      case 'unhealthy':
      case 'error':
        return <AlertCircle size={16} className="text-red-600" />;
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Activity size={16} />
          System Health
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Overall Status</span>
          <Badge className={cn("text-xs", getStatusColor(health.status))}>
            {getStatusIcon(health.status)}
            <span className="ml-1 capitalize">{health.status}</span>
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="text-sm font-medium">Agent Status</div>
          <div className="space-y-1">
            {Object.entries(health.agents).map(([agentName, agentStatus]) => (
              <div key={agentName} className="flex items-center justify-between text-xs">
                <span className="capitalize">{agentName.replace('_', ' ')}</span>
                <div className="flex items-center gap-1">
                  {agentStatus.operational ? (
                    <CheckCircle size={12} className="text-green-600" />
                  ) : (
                    <AlertCircle size={12} className="text-red-600" />
                  )}
                  <span className={agentStatus.operational ? 'text-green-600' : 'text-red-600'}>
                    {agentStatus.operational ? 'Operational' : 'Down'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <div className="text-sm font-medium">Integrations</div>
          <div className="flex items-center justify-between text-xs">
            <span>LangSmith Tracing</span>
            <div className="flex items-center gap-1">
              {health.langsmith_connected ? (
                <CheckCircle size={12} className="text-green-600" />
              ) : (
                <AlertCircle size={12} className="text-red-600" />
              )}
              <span className={health.langsmith_connected ? 'text-green-600' : 'text-red-600'}>
                {health.langsmith_connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

        <div className="pt-2 border-t text-xs text-muted-foreground">
          Last updated: {new Date(health.timestamp).toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
};

const WorkflowMetricsCard: React.FC<{ metrics: WorkflowMetrics }> = ({ metrics }) => {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <BarChart3 size={16} />
          Workflow Performance
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Total Workflows</div>
            <div className="text-2xl font-bold">{metrics.total_workflows}</div>
          </div>
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Success Rate</div>
            <div className="text-2xl font-bold text-green-600">
              {metrics.success_rate.toFixed(1)}%
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Success Rate</span>
            <span className="font-medium">{metrics.success_rate.toFixed(1)}%</span>
          </div>
          <Progress value={metrics.success_rate} className="h-2" />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Avg Quality Score</span>
            <span className="font-medium">{metrics.avg_quality_score.toFixed(2)}/5.0</span>
          </div>
          <Progress value={(metrics.avg_quality_score / 5) * 100} className="h-2" />
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock size={10} />
              <span>Avg Time</span>
            </div>
            <div className="font-medium">{metrics.avg_execution_time.toFixed(1)}s</div>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <TrendingUp size={10} />
              <span>Failed</span>
            </div>
            <div className="font-medium text-red-600">{metrics.failed_workflows}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const SpecializedGraphsCard: React.FC = () => {
  const { graphs, healthStatus, loading, error } = useSpecializedGraphs();

  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <GitBranch size={16} />
            Specialized Graphs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-4">
            <RefreshCw size={16} className="animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <GitBranch size={16} />
            Specialized Graphs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <AlertCircle size={16} className="mx-auto mb-2 text-red-500" />
            <p className="text-xs text-muted-foreground">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <GitBranch size={16} />
          Specialized Graphs
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {healthStatus && (
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <div className="text-xs text-muted-foreground">Total Graphs</div>
              <div className="text-2xl font-bold">{healthStatus.total_graphs}</div>
            </div>
            <div className="space-y-1">
              <div className="text-xs text-muted-foreground">Health Rate</div>
              <div className="text-2xl font-bold text-green-600">
                {((healthStatus.healthy_graphs / healthStatus.total_graphs) * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Healthy Graphs</span>
            <span className="font-medium">{healthStatus?.healthy_graphs || 0}/{healthStatus?.total_graphs || 0}</span>
          </div>
          <Progress
            value={healthStatus ? (healthStatus.healthy_graphs / healthStatus.total_graphs) * 100 : 0}
            className="h-2"
          />
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Compiled Graphs</span>
            <span className="font-medium">{healthStatus?.compiled_graphs || 0}/{healthStatus?.total_graphs || 0}</span>
          </div>
          <Progress
            value={healthStatus ? (healthStatus.compiled_graphs / healthStatus.total_graphs) * 100 : 0}
            className="h-2"
          />
        </div>

        {healthStatus?.failed_graphs && healthStatus.failed_graphs.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-medium text-red-600">Failed Graphs</div>
            <div className="space-y-1">
              {healthStatus.failed_graphs.map((graphId) => (
                <div key={graphId} className="flex items-center gap-1 text-xs">
                  <AlertCircle size={10} className="text-red-600" />
                  <span className="text-red-600">{graphId}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {graphs.length > 0 && (
          <div className="pt-2 border-t">
            <div className="text-xs text-muted-foreground mb-2">Available Graphs:</div>
            <div className="flex flex-wrap gap-1">
              {graphs.slice(0, 4).map((graph) => (
                <Badge
                  key={graph.id}
                  variant={graph.status === 'healthy' ? 'default' : 'destructive'}
                  className="text-xs"
                >
                  {graph.name}
                </Badge>
              ))}
              {graphs.length > 4 && (
                <Badge variant="outline" className="text-xs">
                  +{graphs.length - 4} more
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const QuickStatsGrid: React.FC<{ health: SystemHealth; metrics: WorkflowMetrics }> = ({
  health,
  metrics
}) => {
  const { healthStatus } = useSpecializedGraphs();
  const operationalAgents = Object.values(health.agents).filter(agent => agent.operational).length;

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Users size={16} className="text-blue-600" />
            <div>
              <div className="text-xs text-muted-foreground">Active Agents</div>
              <div className="text-lg font-bold">{operationalAgents}/3</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Zap size={16} className="text-green-600" />
            <div>
              <div className="text-xs text-muted-foreground">Success Rate</div>
              <div className="text-lg font-bold">{metrics.success_rate.toFixed(0)}%</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Clock size={16} className="text-purple-600" />
            <div>
              <div className="text-xs text-muted-foreground">Avg Response</div>
              <div className="text-lg font-bold">{metrics.avg_execution_time.toFixed(1)}s</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Globe size={16} className="text-orange-600" />
            <div>
              <div className="text-xs text-muted-foreground">Quality Score</div>
              <div className="text-lg font-bold">{metrics.avg_quality_score.toFixed(1)}/5</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Brain size={16} className="text-indigo-600" />
            <div>
              <div className="text-xs text-muted-foreground">Graphs Health</div>
              <div className="text-lg font-bold">
                {healthStatus ? `${healthStatus.healthy_graphs}/${healthStatus.total_graphs}` : '0/0'}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export const SpecializedDashboard: React.FC<SpecializedDashboardProps> = ({ className }) => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [metrics, setMetrics] = useState<WorkflowMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setError(null);

      const [healthResponse, metricsResponse] = await Promise.all([
        fetch(`${getApiBaseUrl()}/specialized/health`),
        fetch(`${getApiBaseUrl()}/specialized/metrics/workflow?time_range_hours=24`)
      ]);

      if (!healthResponse.ok || !metricsResponse.ok) {
        throw new Error('Failed to fetch dashboard data');
      }

      const healthData = await healthResponse.json();
      const metricsData = await metricsResponse.json();

      setHealth(healthData);
      setMetrics(metricsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    fetchData();
  };

  if (loading && !health && !metrics) {
    return (
      <div className={cn("space-y-6", className)}>
        <div className="flex items-center justify-center py-12">
          <RefreshCw size={24} className="animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  return error ? (
    <ErrorState message={error} onRetry={handleRefresh} />
  ) : (
    <div className={cn("space-y-6", className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Specialized Agents Dashboard</h2>
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={loading}>
          <RefreshCw size={14} className={cn("mr-2", loading && "animate-spin")} />
          Refresh
        </Button>
      </div>

      {health && metrics && <QuickStatsGrid health={health} metrics={metrics} />}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="graphs">Specialized Graphs</TabsTrigger>
          <TabsTrigger value="agents">Agent Metrics</TabsTrigger>
          <TabsTrigger value="system">System Health</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {health && <SystemStatusCard health={health} />}
            {metrics && <WorkflowMetricsCard metrics={metrics} />}
            <SpecializedGraphsCard />
          </div>
        </TabsContent>

        <TabsContent value="graphs" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SpecializedGraphsCard />
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Graph Categories</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Analysis Graphs</span>
                    <Badge variant="outline">2</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Planning Graphs</span>
                    <Badge variant="outline">1</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Research Graphs</span>
                    <Badge variant="outline">1</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Quality Graphs</span>
                    <Badge variant="outline">1</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Coordination Graphs</span>
                    <Badge variant="outline">1</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <AgentMetricsDisplay />
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          {health && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <SystemStatusCard health={health} />
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">System Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">LangSmith Project:</span>
                    <span className="font-medium">ai-agent-real-specialization</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Agent Architecture:</span>
                    <span className="font-medium">Real Specialized Agents</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Tracing:</span>
                    <Badge variant={health.langsmith_connected ? "default" : "destructive"}>
                      {health.langsmith_connected ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last Health Check:</span>
                    <span className="font-medium">
                      {new Date(health.timestamp).toLocaleString()}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};
