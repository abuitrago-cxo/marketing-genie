import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ResponsiveGrid } from '@/components/ui/horizontal-scroll';
// import { useWorkflows, type WorkflowExecution } from '@/hooks/useAgents'; // Replaced by useWorkflowTemplates
import { useSpecializedGraphs, type SpecializedGraph, type GraphHealthStatus } from '@/hooks/useSpecializedGraphs';
import { useWorkflowTemplates, type WorkflowTemplate, type WorkflowStep } from '@/hooks/useWorkflowTemplates';
import {
  Plus,
  Search,
  Play,
  Pause,
  MoreHorizontal,
  Clock,
  CheckCircle,
  AlertCircle,
  Workflow,
  GitBranch,
  Code,
  TestTube,
  Rocket,
  Shield,
  FileText,
  Users,
  Calendar,
  Activity,
  RefreshCw,
  Brain,
  Zap,
  BarChart3
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface WorkflowExecutionCardProps {
  workflow: WorkflowTemplate;
  onRun: (workflowId: string, inputSchema?: Record<string, any>) => void;
}

const stepIcons = {
  code: <Code className="h-4 w-4" />,
  test: <TestTube className="h-4 w-4" />,
  deploy: <Rocket className="h-4 w-4" />,
  review: <Users className="h-4 w-4" />,
  security: <Shield className="h-4 w-4" />,
  docs: <FileText className="h-4 w-4" />
};

const statusColors = {
  pending: 'text-gray-500',
  running: 'text-blue-500',
  completed: 'text-green-500',
  failed: 'text-red-500'
};

const categoryColors = {
  'ci-cd': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  'testing': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  'deployment': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  'security': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  'documentation': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
};

const WorkflowExecutionCard: React.FC<WorkflowExecutionCardProps> = ({ workflow, onRun }) => {
  const getTimeAgo = (dateInput: string | Date | undefined) => {
    if (!dateInput) return 'N/A';
    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));

    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Workflow className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">{workflow.name}</CardTitle>
            <Badge className={cn("text-xs", categoryColors[workflow.category])}>
              {workflow.category.toUpperCase()}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <CardDescription className="text-sm">
          {workflow.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Workflow stats */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="text-center">
            <div className="font-medium">{workflow.successRate !== undefined ? `${workflow.successRate.toFixed(1)}%` : 'N/A'}</div>
            <div className="text-muted-foreground">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="font-medium">{workflow.avgDuration !== undefined ? `${workflow.avgDuration.toFixed(1)}m` : 'N/A'}</div>
            <div className="text-muted-foreground">Avg Duration</div>
          </div>
        </div>

        {/* Status and actions */}
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>Last run: {getTimeAgo(workflow.lastRun)}</span>
            </div>
          </div>
          <Button
            size="sm"
            onClick={() => onRun(workflow.id, workflow.inputSchema)}
          >
            <Play className="h-4 w-4 mr-1" />
            Run Workflow
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

const SpecializedGraphCard: React.FC<{
  graph: SpecializedGraph;
  onExecute: (graphId: string) => void;
}> = ({ graph, onExecute }) => {
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'analysis': return Code;
      case 'planning': return GitBranch;
      case 'research': return Search;
      case 'quality': return TestTube;
      case 'coordination': return Users;
      default: return Brain;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'analysis': return 'bg-blue-100 text-blue-800';
      case 'planning': return 'bg-green-100 text-green-800';
      case 'research': return 'bg-purple-100 text-purple-800';
      case 'quality': return 'bg-orange-100 text-orange-800';
      case 'coordination': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const CategoryIcon = getCategoryIcon(graph.category);

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <CategoryIcon className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">{graph.name}</CardTitle>
            <Badge className={cn("text-xs", getCategoryColor(graph.category))}>
              {graph.category.toUpperCase()}
            </Badge>
            <Badge
              className={cn("text-xs",
                graph.status === 'healthy' ? 'bg-green-100 text-green-800' :
                graph.status === 'failed' ? 'bg-red-100 text-red-800' :
                'bg-yellow-100 text-yellow-800'
              )}
            >
              {graph.status.toUpperCase()}
            </Badge>
          </div>
        </div>
        <CardDescription className="text-sm">
          {graph.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="font-medium">{graph.node_count}</div>
            <div className="text-muted-foreground">Nodes</div>
          </div>
          <div className="text-center">
            <div className="font-medium">{graph.estimated_duration}</div>
            <div className="text-muted-foreground">Duration</div>
          </div>
          <div className="text-center">
            <div className="font-medium">{graph.required_tools?.length || 0}</div>
            <div className="text-muted-foreground">Tools</div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="text-sm text-muted-foreground">
            Priority: {graph.priority}
          </div>
          <Button
            size="sm"
            onClick={() => onExecute(graph.id)}
            disabled={graph.status === 'failed'}
          >
            <Play className="h-4 w-4 mr-1" />
            Execute
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export const WorkflowsPage: React.FC = () => {
  const handleExecuteGraph = async (graphId: string) => {
    console.log(`Attempting to execute graph: ${graphId}`);
    try {
      // Assuming executeGraph from useSpecializedGraphs takes the graphId and optional inputs
      // and returns a promise that resolves with the execution result or status.
      const result = await executeGraph({ graph_id: graphId, input_data: {} }); 
      console.log('Graph execution initiated:', result);
      alert(`Graph '${graphId}' execution initiated successfully! Check console for details.`);
      // Potentially refresh graph list or show a success notification
    } catch (error) {
      console.error('Failed to execute graph:', error);
      alert(`Failed to execute graph '${graphId}'. Error: ${error instanceof Error ? error.message : String(error)}`);
      // Show an error notification
    }
  };

  const [activeTab, setActiveTab] = useState<'workflows' | 'graphs'>('workflows');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const { templates: workflowTemplates, loading: templatesLoading, error: templatesError, runWorkflow: runWorkflowTemplate, fetchTemplates: refreshWorkflowTemplates } = useWorkflowTemplates();
  const { graphs, healthStatus, loading: graphsLoading, error: graphsError, executeGraph } = useSpecializedGraphs();

  const handleRunWorkflow = async (workflowId: string, inputSchema?: Record<string, any>) => {
    console.log(`Attempting to run workflow: ${workflowId}`);
    try {
      const result = await runWorkflowTemplate({ template_id: workflowId, input_data: {} });
      console.log('Workflow run initiated:', result);
      alert(`Workflow '${workflowId}' initiated successfully! Check console for details.`);
    } catch (error) {
      console.error('Failed to run workflow:', error);
      alert(`Failed to run workflow '${workflowId}'. Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const filteredWorkflows = workflowTemplates.filter(workflow =>
    (workflow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    workflow.description.toLowerCase().includes(searchQuery.toLowerCase())) &&
    (selectedCategory === 'all' || workflow.category === selectedCategory)
  );

  const categories = ['all', ...Array.from(new Set(workflowTemplates.map(w => w.category)))];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflows & Graphs</h1>
          <p className="text-muted-foreground">
            Manage AI-powered workflows and specialized LangGraph executions
          </p>
          {templatesError && (
            <div className="flex items-center gap-2 mt-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{templatesError}</span>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={refreshWorkflowTemplates} disabled={templatesLoading} className="flex items-center">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Create Workflow
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'workflows' | 'graphs')}>
        <TabsList>
          <TabsTrigger value="workflows" className="flex items-center gap-2">
            <Workflow className="h-4 w-4" />
            Workflows ({workflowTemplates.length})
          </TabsTrigger>
          <TabsTrigger value="graphs" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            Specialized Graphs ({graphs.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="workflows" className="space-y-6">
          {templatesLoading && (
            <div className="flex justify-center items-center py-10">
              <RefreshCw className="h-8 w-8 animate-spin text-primary" />
              <p className="ml-2">Loading workflow templates...</p>
            </div>
          )}
          {templatesError && (
            <div className="text-center py-10 text-red-600">
              <AlertCircle className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-medium">Error loading workflows</h3>
              <p>{templatesError}</p>
              <Button onClick={refreshWorkflowTemplates} className="mt-4">Try Again</Button>
            </div>
          )}
          {!templatesLoading && !templatesError && (
            <>
              {/* Search and filters - always show if not loading/error */}
              <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search workflows..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div className="flex gap-2">
                  {categories.map((category) => (
                    <Button
                      key={category}
                      variant={selectedCategory === category ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedCategory(category)}
                    >
                      {category === 'all' ? 'All' : category.replace('-', ' ').toUpperCase()}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Conditional rendering for workflow list or empty state */}
              {filteredWorkflows.length > 0 ? (
                <ResponsiveGrid minItemWidth={400} gap={24}>
                  {filteredWorkflows.map((workflow) => (
                    <WorkflowExecutionCard
                      key={workflow.id}
                      workflow={workflow}
                      onRun={() => handleRunWorkflow(workflow.id, workflow.inputSchema)}
                    />
                  ))}
                </ResponsiveGrid>
              ) : (
                <div className="text-center py-12">
                  <div className="mx-auto w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-4">
                    <Workflow className="h-12 w-12 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-medium mb-2">
                    {workflowTemplates.length === 0 ? "No Workflow Templates Available" : "No Workflows Found"}
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    {workflowTemplates.length === 0
                      ? "No workflow templates are currently available. You can create one to get started."
                      : (searchQuery || selectedCategory !== 'all')
                        ? "No workflows match your current search or filter. Try adjusting them."
                        : "There are no workflows in this category yet."}
                  </p>
                  {workflowTemplates.length === 0 && !searchQuery && selectedCategory === 'all' && (
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Workflow
                    </Button>
                  )}
                </div>
              )}
            </>
          )}
        </TabsContent>

        <TabsContent value="graphs" className="space-y-6">
          {/* Graph Health Overview */}
          {healthStatus && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Brain size={16} className="text-blue-600" />
                    <div>
                      <div className="text-xs text-muted-foreground">Total Graphs</div>
                      <div className="text-lg font-bold">{healthStatus.total_graphs}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-green-600" />
                    <div>
                      <div className="text-xs text-muted-foreground">Healthy</div>
                      <div className="text-lg font-bold">{healthStatus.healthy_graphs}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <Zap size={16} className="text-purple-600" />
                    <div>
                      <div className="text-xs text-muted-foreground">Compiled</div>
                      <div className="text-lg font-bold">{healthStatus.compiled_graphs}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <BarChart3 size={16} className="text-orange-600" />
                    <div>
                      <div className="text-xs text-muted-foreground">Health</div>
                      <div className="text-lg font-bold">
                        {healthStatus.total_graphs > 0 ? 
                          ((healthStatus.healthy_graphs / healthStatus.total_graphs) * 100).toFixed(0) + '%'
                          : 'N/A'}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Loading State for Graphs */}
          {graphsLoading && (
            <div className="flex justify-center items-center py-10">
              <RefreshCw className="h-8 w-8 animate-spin text-primary" />
              <p className="ml-2">Loading specialized graphs...</p>
            </div>
          )}

          {/* Error State for Graphs */}
          {!graphsLoading && graphsError && (
            <div className="text-center py-10 text-red-600">
              <AlertCircle className="h-12 w-12 mx-auto mb-2" />
              <h3 className="text-lg font-medium">Error loading graphs</h3>
              <p>{graphsError}</p>
              {/* Consider adding a refresh button for graphs if useSpecializedGraphs hook provides one */}
              {/* e.g., <Button onClick={refreshGraphs} className="mt-4">Try Again</Button> */}
            </div>
          )}

          {/* Content: Graphs Grid or Empty State */}
          {!graphsLoading && !graphsError && (
            <>
              {graphs.length > 0 ? (
                <ResponsiveGrid minItemWidth={400} gap={24}>
                  {graphs.map((graph) => (
                    <SpecializedGraphCard
                      key={graph.id}
                      graph={graph}
                      onExecute={() => handleExecuteGraph(graph.id)}
                    />
                  ))}
                </ResponsiveGrid>
              ) : (
                <div className="text-center py-12">
                  <div className="mx-auto w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-4">
                    <Brain className="h-12 w-12 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-medium mb-2">No Specialized Graphs Available</h3>
                  <p className="text-muted-foreground mb-4">
                    There are currently no specialized graphs to display.
                  </p>
                </div>
              )}
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};
