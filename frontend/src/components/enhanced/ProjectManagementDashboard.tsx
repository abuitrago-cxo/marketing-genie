import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  Code,
  GitBranch,
  Users,
  TrendingUp,
  Calendar,
  Settings,
  Bell,
  Search,
  Filter,
  Plus,
  MoreHorizontal
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types for project management
interface ProjectTask {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'review' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee?: string;
  dueDate?: Date;
  tags: string[];
  progress: number;
}

interface ProjectMetric {
  label: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'stable';
  icon: React.ReactNode;
}

interface AgentStatus {
  id: string;
  name: string;
  type: 'research' | 'analysis' | 'devops' | 'communication';
  status: 'active' | 'idle' | 'error';
  currentTask?: string;
  lastActivity: Date;
}

// Sample data
const sampleTasks: ProjectTask[] = [
  {
    id: '1',
    title: 'Implement user authentication',
    description: 'Add JWT-based authentication system',
    status: 'in-progress',
    priority: 'high',
    assignee: 'DevOps Agent',
    dueDate: new Date('2025-01-10'),
    tags: ['backend', 'security'],
    progress: 65
  },
  {
    id: '2',
    title: 'Code quality analysis',
    description: 'Run automated code review and security scan',
    status: 'completed',
    priority: 'medium',
    assignee: 'Analysis Agent',
    tags: ['quality', 'security'],
    progress: 100
  },
  {
    id: '3',
    title: 'API documentation update',
    description: 'Update OpenAPI specs for new endpoints',
    status: 'todo',
    priority: 'low',
    tags: ['documentation'],
    progress: 0
  }
];

const sampleMetrics: ProjectMetric[] = [
  {
    label: 'Tasks Completed',
    value: '24/30',
    change: 12,
    trend: 'up',
    icon: <CheckCircle className="h-4 w-4" />
  },
  {
    label: 'Code Coverage',
    value: '87%',
    change: 5,
    trend: 'up',
    icon: <Code className="h-4 w-4" />
  },
  {
    label: 'Active Agents',
    value: 4,
    trend: 'stable',
    icon: <Activity className="h-4 w-4" />
  },
  {
    label: 'Issues Found',
    value: 3,
    change: -2,
    trend: 'down',
    icon: <AlertTriangle className="h-4 w-4" />
  }
];

const sampleAgents: AgentStatus[] = [
  {
    id: '1',
    name: 'Research Agent',
    type: 'research',
    status: 'active',
    currentTask: 'Analyzing market trends',
    lastActivity: new Date()
  },
  {
    id: '2',
    name: 'DevOps Agent',
    type: 'devops',
    status: 'active',
    currentTask: 'Deploying to staging',
    lastActivity: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: '3',
    name: 'Analysis Agent',
    type: 'analysis',
    status: 'idle',
    lastActivity: new Date(Date.now() - 30 * 60 * 1000)
  }
];

// Status badge component
const StatusBadge: React.FC<{ status: ProjectTask['status'] }> = ({ status }) => {
  const variants = {
    'todo': 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    'in-progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'review': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  };

  return (
    <Badge variant="secondary" className={cn("text-xs", variants[status])}>
      {status.replace('-', ' ').toUpperCase()}
    </Badge>
  );
};

// Priority badge component
const PriorityBadge: React.FC<{ priority: ProjectTask['priority'] }> = ({ priority }) => {
  const variants = {
    'low': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'medium': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'high': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    'urgent': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  };

  return (
    <Badge variant="outline" className={cn("text-xs", variants[priority])}>
      {priority.toUpperCase()}
    </Badge>
  );
};

// Agent status indicator
const AgentStatusIndicator: React.FC<{ agent: AgentStatus }> = ({ agent }) => {
  const statusColors = {
    'active': 'bg-green-500',
    'idle': 'bg-yellow-500',
    'error': 'bg-red-500'
  };

  const typeIcons = {
    'research': <Search className="h-4 w-4" />,
    'analysis': <TrendingUp className="h-4 w-4" />,
    'devops': <GitBranch className="h-4 w-4" />,
    'communication': <Users className="h-4 w-4" />
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              {typeIcons[agent.type]}
              <span className="font-medium">{agent.name}</span>
            </div>
            <div className={cn("w-2 h-2 rounded-full", statusColors[agent.status])} />
          </div>
          <Badge variant="outline" className="text-xs">
            {agent.status}
          </Badge>
        </div>

        {agent.currentTask && (
          <p className="text-sm text-muted-foreground mt-2">{agent.currentTask}</p>
        )}

        <p className="text-xs text-muted-foreground mt-1">
          Last active: {agent.lastActivity.toLocaleTimeString()}
        </p>
      </CardContent>
    </Card>
  );
};

// Task card component
const TaskCard: React.FC<{ task: ProjectTask }> = ({ task }) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-start justify-between">
            <h3 className="font-medium text-sm">{task.title}</h3>
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>

          <p className="text-sm text-muted-foreground">{task.description}</p>

          <div className="flex items-center gap-2 flex-wrap">
            <StatusBadge status={task.status} />
            <PriorityBadge priority={task.priority} />
            {task.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>

          {task.progress > 0 && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span>Progress</span>
                <span>{task.progress}%</span>
              </div>
              <Progress value={task.progress} className="h-2" />
            </div>
          )}

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            {task.assignee && (
              <span className="flex items-center gap-1">
                <Users className="h-3 w-3" />
                {task.assignee}
              </span>
            )}
            {task.dueDate && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {task.dueDate.toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Metrics card component
const MetricCard: React.FC<{ metric: ProjectMetric }> = ({ metric }) => {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">{metric.label}</p>
            <p className="text-2xl font-bold">{metric.value}</p>
          </div>
          <div className="text-muted-foreground">{metric.icon}</div>
        </div>

        {metric.change !== undefined && (
          <div className="flex items-center gap-1 mt-2">
            <TrendingUp className={cn(
              "h-3 w-3",
              metric.trend === 'up' ? "text-green-500" :
              metric.trend === 'down' ? "text-red-500" : "text-gray-500"
            )} />
            <span className={cn(
              "text-xs",
              metric.change > 0 ? "text-green-600" :
              metric.change < 0 ? "text-red-600" : "text-gray-600"
            )}>
              {metric.change > 0 ? '+' : ''}{metric.change}%
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Main dashboard component
export const ProjectManagementDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center justify-between p-4">
          <div>
            <h1 className="text-2xl font-bold">Project Dashboard</h1>
            <p className="text-muted-foreground">AI-powered project management</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Bell className="h-4 w-4 mr-2" />
              Notifications
            </Button>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              New Task
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="agents">Agents</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-4 space-y-4">
            {/* Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {sampleMetrics.map((metric, index) => (
                <MetricCard key={index} metric={metric} />
              ))}
            </div>

            {/* Recent tasks and active agents */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Recent Tasks</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-64">
                    <div className="space-y-3">
                      {sampleTasks.slice(0, 3).map((task) => (
                        <TaskCard key={task.id} task={task} />
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Active Agents</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-64">
                    <div className="space-y-3">
                      {sampleAgents.map((agent) => (
                        <AgentStatusIndicator key={agent.id} agent={agent} />
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="tasks" className="mt-4">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
                <Button variant="outline" size="sm">
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sampleTasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="agents" className="mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sampleAgents.map((agent) => (
                <AgentStatusIndicator key={agent.id} agent={agent} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Analytics Dashboard</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Analytics and reporting features will be implemented here.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
