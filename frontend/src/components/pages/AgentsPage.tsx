import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ResponsiveGrid } from '@/components/ui/horizontal-scroll';
import { useAgents, type Agent } from '@/hooks/useAgents';
import { useSpecializedGraphs } from '@/hooks/useSpecializedGraphs';
import {
  Bot,
  Search,
  GitBranch,
  Activity,
  Users,
  Settings,
  Play,
  Pause,
  BarChart3,
  Clock,
  CheckCircle,
  AlertTriangle,
  Zap,
  Brain,
  Code,
  Shield,
  FileText,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Agent icons mapping
const agentIcons = {
  'research': <Search className="h-6 w-6" />,
  'devops': <GitBranch className="h-6 w-6" />,
  'analysis': <BarChart3 className="h-6 w-6" />,
  'communication': <Users className="h-6 w-6" />,
  'code-engineer': <Code className="h-6 w-6" />,
  'project-manager': <FileText className="h-6 w-6" />,
  'qa-specialist': <Shield className="h-6 w-6" />
};

const statusColors = {
  'active': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  'idle': 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  'busy': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  'offline': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
};

const statusIcons = {
  'active': <CheckCircle className="h-4 w-4" />,
  'idle': <Clock className="h-4 w-4" />,
  'busy': <Activity className="h-4 w-4" />,
  'offline': <AlertTriangle className="h-4 w-4" />
};

const AgentCard: React.FC<{
  agent: Agent;
  onToggle: (id: string) => void;
  onConfigure: (id: string) => void;
  onViewDetails: (id: string) => void;
}> = ({ agent, onToggle, onConfigure, onViewDetails }) => {
  const navigate = useNavigate();

  const getTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  const handleViewDetails = () => {
    navigate(`/agents/${agent.type.replace('-', '')}`);
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              {agentIcons[agent.type]}
            </div>
            <div>
              <CardTitle className="text-lg">{agent.name}</CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge className={cn("text-xs", statusColors[agent.status])}>
                  {statusIcons[agent.status]}
                  <span className="ml-1 capitalize">{agent.status}</span>
                </Badge>
                {!agent.is_enabled && (
                  <Badge variant="outline" className="text-xs">
                    Disabled
                  </Badge>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onToggle(agent.id)}
            >
              {agent.is_enabled ? (
                <Pause className="h-4 w-4 text-orange-500" />
              ) : (
                <Play className="h-4 w-4 text-green-500" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onConfigure(agent.id)}
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <CardDescription className="text-sm mt-2">
          {agent.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Current task */}
        {agent.current_task && (
          <div className="p-3 bg-muted/50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Activity className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Current Task</span>
            </div>
            <p className="text-sm text-muted-foreground">{agent.current_task}</p>
          </div>
        )}

        {/* Capabilities */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Capabilities</h4>
          <div className="flex flex-wrap gap-1">
            {agent.capabilities.slice(0, 3).map((capability) => (
              <Badge key={capability} variant="secondary" className="text-xs">
                {capability}
              </Badge>
            ))}
            {agent.capabilities.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{agent.capabilities.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Performance metrics */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-muted-foreground">Success Rate</span>
              <span className="font-medium">{agent.success_rate}%</span>
            </div>
            <Progress value={agent.success_rate} className="h-2" />
          </div>
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-muted-foreground">Response Time</span>
              <span className="font-medium">{agent.avg_response_time}s</span>
            </div>
            <Progress value={Math.max(0, 100 - agent.avg_response_time * 20)} className="h-2" />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            <span>{agent.tasks_completed} tasks completed</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>Active {getTimeAgo(agent.last_activity)}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={handleViewDetails}
          >
            View Details
          </Button>
          <Button
            size="sm"
            className="flex-1"
            disabled={!agent.is_enabled}
          >
            <Zap className="h-4 w-4 mr-1" />
            Quick Task
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export const AgentsPage: React.FC = () => {
  const { agents, metrics, loading, error, refreshAgents, toggleAgent } = useAgents();
  const { graphs, healthStatus } = useSpecializedGraphs();

  const handleToggleAgent = async (agentId: string) => {
    await toggleAgent(agentId);
  };

  const handleConfigureAgent = (agentId: string) => {
    console.log('Configure agent:', agentId);
    // Here you would open a configuration modal or navigate to settings
  };

  const handleViewDetails = (agentId: string) => {
    console.log('View agent details:', agentId);
    // Navigation is handled in the AgentCard component
  };

  // Use metrics from API if available, otherwise calculate from agents
  const activeAgents = metrics?.active_agents ?? agents.filter(agent => agent.is_enabled && agent.status !== 'offline').length;
  const busyAgents = metrics?.busy_agents ?? agents.filter(agent => agent.status === 'busy').length;
  const avgSuccessRate = metrics?.avg_success_rate ?? (agents.length > 0 ? Math.round(agents.reduce((sum, agent) => sum + agent.success_rate, 0) / agents.length) : 0);
  const totalTasks = metrics?.total_tasks_completed ?? agents.reduce((sum, agent) => sum + agent.tasks_completed, 0);

  // Loading state
  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">AI Agents</h1>
            <p className="text-muted-foreground">Loading agents...</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Agents</h1>
          <p className="text-muted-foreground">
            Manage and monitor your specialized AI agents
          </p>
          {error && (
            <div className="flex items-center gap-2 mt-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={refreshAgents}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Bot className="h-4 w-4 mr-2" />
            Add Agent
          </Button>
        </div>
      </div>

      {/* Overview stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-muted-foreground">Active Agents</p>
                <p className="text-2xl font-bold">{activeAgents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-muted-foreground">Currently Busy</p>
                <p className="text-2xl font-bold">{busyAgents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-muted-foreground">Avg Success Rate</p>
                <p className="text-2xl font-bold">{avgSuccessRate}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-muted-foreground">Total Tasks</p>
                <p className="text-2xl font-bold">{totalTasks}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Specialized Graphs Status */}
      {healthStatus && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitBranch className="h-5 w-5" />
              Specialized Graphs Status
            </CardTitle>
            <CardDescription>
              Status of LangGraph specialized workflows
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{healthStatus.total_graphs}</div>
                <div className="text-sm text-muted-foreground">Total Graphs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{healthStatus.healthy_graphs}</div>
                <div className="text-sm text-muted-foreground">Healthy</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{healthStatus.compiled_graphs}</div>
                <div className="text-sm text-muted-foreground">Compiled</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {((healthStatus.healthy_graphs / healthStatus.total_graphs) * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-muted-foreground">Health Rate</div>
              </div>
            </div>

            {graphs.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <div className="text-sm font-medium mb-2">Available Graphs:</div>
                <div className="flex flex-wrap gap-2">
                  {graphs.map((graph) => (
                    <Badge
                      key={graph.id}
                      variant={graph.status === 'healthy' ? 'default' : 'destructive'}
                      className="text-xs"
                    >
                      {graph.name}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Agents grid */}
      <ResponsiveGrid minItemWidth={400} gap={24}>
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onToggle={handleToggleAgent}
            onConfigure={handleConfigureAgent}
            onViewDetails={handleViewDetails}
          />
        ))}
      </ResponsiveGrid>
    </div>
  );
};
