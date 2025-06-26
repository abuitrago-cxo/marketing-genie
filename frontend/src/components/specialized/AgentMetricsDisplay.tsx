import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  Search, 
  BarChart3, 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  RefreshCw,
  TrendingUp,
  Activity
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { getApiBaseUrl } from '../../config/api';
import ErrorState from '../ui/ErrorState';

interface AgentPerformance {
  total_executions: number;
  success_rate: number;
  avg_execution_time: number;
  avg_quality_score: number;
  last_execution: string;
}

interface AgentMetrics {
  research_agent: AgentPerformance;
  analysis_agent: AgentPerformance;
  synthesis_agent: AgentPerformance;
}

interface AgentMetricsDisplayProps {
  className?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const AgentCard: React.FC<{
  name: string;
  icon: React.ReactNode;
  performance: AgentPerformance;
  color: string;
}> = ({ name, icon, performance, color }) => {
  const getStatusColor = (successRate: number) => {
    if (successRate >= 95) return 'text-green-600';
    if (successRate >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (successRate: number) => {
    if (successRate >= 95) return <CheckCircle size={14} className="text-green-600" />;
    if (successRate >= 80) return <Activity size={14} className="text-yellow-600" />;
    return <AlertCircle size={14} className="text-red-600" />;
  };

  const formatLastExecution = (timestamp: string) => {
    if (timestamp === 'Never') return 'Never';
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
      return `${Math.floor(diffMins / 1440)}d ago`;
    } catch {
      return 'Unknown';
    }
  };

  return (
    <Card className="relative overflow-hidden">
      <div className={cn("absolute top-0 left-0 w-full h-1", color)} />
      
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {icon}
            <CardTitle className="text-sm font-medium">{name}</CardTitle>
          </div>
          {getStatusIcon(performance.success_rate)}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Success Rate */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Success Rate</span>
            <span className={getStatusColor(performance.success_rate)}>
              {performance.success_rate.toFixed(1)}%
            </span>
          </div>
          <Progress 
            value={performance.success_rate} 
            className="h-2"
          />
        </div>

        {/* Quality Score */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Quality Score</span>
            <span className="font-medium">
              {performance.avg_quality_score.toFixed(2)}/5.0
            </span>
          </div>
          <Progress 
            value={(performance.avg_quality_score / 5) * 100} 
            className="h-2"
          />
        </div>

        {/* Execution Stats */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Clock size={10} />
              <span>Avg Time</span>
            </div>
            <div className="font-medium">
              {performance.avg_execution_time.toFixed(1)}s
            </div>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <TrendingUp size={10} />
              <span>Executions</span>
            </div>
            <div className="font-medium">
              {performance.total_executions}
            </div>
          </div>
        </div>

        {/* Last Execution */}
        <div className="pt-2 border-t">
          <div className="text-xs text-muted-foreground">
            Last execution: {formatLastExecution(performance.last_execution)}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const AgentMetricsDisplay: React.FC<AgentMetricsDisplayProps> = ({
  className,
  autoRefresh = true,
  refreshInterval = 30000
}) => {
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchMetrics = async () => {
    try {
      setError(null);
      const response = await fetch(`${getApiBaseUrl()}/specialized/metrics/agents`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setMetrics(data.agents);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
      console.error('Failed to fetch agent metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const handleRefresh = () => {
    setLoading(true);
    fetchMetrics();
  };

  if (loading && !metrics) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Activity size={16} className="animate-pulse" />
            Agent Performance Metrics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw size={24} className="animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <ErrorState
        message={error}
        onRetry={handleRefresh}
        className={className}
      />
    );
  }

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Activity size={18} />
          Agent Performance Metrics
        </h3>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">
            Updated {lastRefresh.toLocaleTimeString()}
          </Badge>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw size={14} className={cn("mr-2", loading && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {metrics && (
          <>
            <AgentCard
              name="Research Agent"
              icon={<Search size={16} className="text-blue-600" />}
              performance={metrics.research_agent}
              color="bg-blue-500"
            />
            
            <AgentCard
              name="Analysis Agent"
              icon={<BarChart3 size={16} className="text-green-600" />}
              performance={metrics.analysis_agent}
              color="bg-green-500"
            />
            
            <AgentCard
              name="Synthesis Agent"
              icon={<FileText size={16} className="text-purple-600" />}
              performance={metrics.synthesis_agent}
              color="bg-purple-500"
            />
          </>
        )}
      </div>
    </div>
  );
};
