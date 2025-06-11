import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { ResponsiveGrid } from '@/components/ui/horizontal-scroll';
import { useSpecializedGraphs, useGraphHealth, type SpecializedGraph, type GraphExecutionRequest } from '@/hooks/useSpecializedGraphs';
import {
  Play,
  Pause,
  RefreshCw,
  Settings,
  Activity,
  CheckCircle,
  AlertCircle,
  Clock,
  GitBranch,
  Code,
  FileText,
  TestTube,
  Users,
  Shield,
  Rocket,
  Brain,
  Search,
  BarChart3,
  Workflow,
  Zap,
  AlertTriangle
} from 'lucide-react';
import { cn } from '@/lib/utils';

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
    case 'analysis': return 'bg-blue-500';
    case 'planning': return 'bg-green-500';
    case 'research': return 'bg-purple-500';
    case 'quality': return 'bg-orange-500';
    case 'coordination': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical': return 'bg-red-100 text-red-800 border-red-200';
    case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low': return 'bg-green-100 text-green-800 border-green-200';
    default: return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'healthy': return CheckCircle;
    case 'failed': return AlertCircle;
    default: return Clock;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy': return 'text-green-600';
    case 'failed': return 'text-red-600';
    default: return 'text-yellow-600';
  }
};

interface GraphCardProps {
  graph: SpecializedGraph;
  onExecute: (graph: SpecializedGraph) => void;
}

const GraphCard: React.FC<GraphCardProps> = ({ graph, onExecute }) => {
  const CategoryIcon = getCategoryIcon(graph.category);
  const StatusIcon = getStatusIcon(graph.status);

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className={cn("p-2 rounded-lg", getCategoryColor(graph.category))}>
              <CategoryIcon size={16} className="text-white" />
            </div>
            <div>
              <CardTitle className="text-sm font-medium">{graph.name}</CardTitle>
              <CardDescription className="text-xs">{graph.category}</CardDescription>
            </div>
          </div>
          <StatusIcon size={16} className={getStatusColor(graph.status)} />
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        <p className="text-xs text-muted-foreground line-clamp-2">
          {graph.description}
        </p>
        
        <div className="flex flex-wrap gap-1">
          <Badge variant="outline" className={cn("text-xs", getPriorityColor(graph.priority))}>
            {graph.priority}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {graph.node_count} nodes
          </Badge>
          <Badge variant="outline" className="text-xs">
            {graph.estimated_duration}
          </Badge>
        </div>
        
        <div className="space-y-2">
          <div className="text-xs text-muted-foreground">Required Tools:</div>
          <div className="flex flex-wrap gap-1">
            {graph.required_tools.slice(0, 3).map((tool) => (
              <Badge key={tool} variant="secondary" className="text-xs">
                {tool}
              </Badge>
            ))}
            {graph.required_tools.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{graph.required_tools.length - 3}
              </Badge>
            )}
          </div>
        </div>
        
        {graph.dependencies.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs text-muted-foreground">Dependencies:</div>
            <div className="flex flex-wrap gap-1">
              {graph.dependencies.map((dep) => (
                <Badge key={dep} variant="outline" className="text-xs">
                  {dep}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        <Button 
          size="sm" 
          className="w-full"
          onClick={() => onExecute(graph)}
          disabled={graph.status === 'failed'}
        >
          <Play size={12} className="mr-1" />
          Execute Graph
        </Button>
      </CardContent>
    </Card>
  );
};

interface HealthOverviewProps {
  healthStatus: any;
}

const HealthOverview: React.FC<HealthOverviewProps> = ({ healthStatus }) => {
  if (!healthStatus) return null;

  const healthPercentage = (healthStatus.healthy_graphs / healthStatus.total_graphs) * 100;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Workflow size={16} className="text-blue-600" />
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
              <div className="text-lg font-bold">{healthPercentage.toFixed(0)}%</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

interface ExecutionDialogProps {
  graph: SpecializedGraph | null;
  onClose: () => void;
  onExecute: (request: GraphExecutionRequest) => void;
}

const ExecutionDialog: React.FC<ExecutionDialogProps> = ({ graph, onClose, onExecute }) => {
  const [query, setQuery] = useState('');
  const [projectContext, setProjectContext] = useState('');
  const [enableTracing, setEnableTracing] = useState(true);
  const [maxIterations, setMaxIterations] = useState(3);

  if (!graph) return null;

  const handleExecute = () => {
    const inputData: Record<string, any> = {
      query,
      project_context: projectContext ? JSON.parse(projectContext) : {},
    };

    // Add graph-specific fields
    if (graph.id === 'codebase_analysis') {
      inputData.repository_url = query;
      inputData.analysis_type = 'comprehensive';
    } else if (graph.id === 'task_planning') {
      inputData.project_scope = query;
      inputData.project_type = 'software_development';
    }

    onExecute({
      graph_id: graph.id,
      input_data: inputData,
      enable_tracing: enableTracing,
      max_iterations: maxIterations,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle>Execute {graph.name}</CardTitle>
          <CardDescription>{graph.description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Query/Input</label>
            <Textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query or input for this graph..."
              className="mt-1"
            />
          </div>
          
          <div>
            <label className="text-sm font-medium">Project Context (JSON)</label>
            <Textarea
              value={projectContext}
              onChange={(e) => setProjectContext(e.target.value)}
              placeholder='{"repository": "example/repo", "type": "web_app"}'
              className="mt-1"
            />
          </div>
          
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={enableTracing}
                onChange={(e) => setEnableTracing(e.target.checked)}
              />
              <span className="text-sm">Enable Tracing</span>
            </label>
            
            <div className="flex items-center gap-2">
              <label className="text-sm">Max Iterations:</label>
              <Input
                type="number"
                value={maxIterations}
                onChange={(e) => setMaxIterations(parseInt(e.target.value))}
                min={1}
                max={10}
                className="w-16"
              />
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button onClick={handleExecute} disabled={!query.trim()}>
              Execute
            </Button>
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export const SpecializedGraphsPage: React.FC = () => {
  const { graphs, healthStatus, executionOrder, loading, error, refreshGraphs, executeGraph } = useSpecializedGraphs();
  const [selectedGraph, setSelectedGraph] = useState<SpecializedGraph | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);

  const filteredGraphs = graphs.filter(graph => {
    const matchesSearch = graph.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         graph.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || graph.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...Array.from(new Set(graphs.map(g => g.category)))];

  const handleExecuteGraph = async (request: GraphExecutionRequest) => {
    try {
      setExecuting(true);
      const result = await executeGraph(request);
      setExecutionResult(result);
    } catch (err) {
      console.error('Graph execution failed:', err);
      setExecutionResult({ error: err instanceof Error ? err.message : 'Execution failed' });
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin mr-2" size={20} />
        Loading specialized graphs...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-600">
        <AlertTriangle className="mr-2" size={20} />
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Specialized Graphs</h1>
          <p className="text-muted-foreground">
            Manage and execute specialized LangGraph workflows
          </p>
        </div>
        <Button onClick={refreshGraphs} variant="outline">
          <RefreshCw size={16} className="mr-2" />
          Refresh
        </Button>
      </div>

      {/* Health Overview */}
      {healthStatus && <HealthOverview healthStatus={healthStatus} />}

      {/* Filters */}
      <div className="flex gap-4">
        <Input
          placeholder="Search graphs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border rounded-md"
        >
          {categories.map(category => (
            <option key={category} value={category}>
              {category === 'all' ? 'All Categories' : category}
            </option>
          ))}
        </select>
      </div>

      {/* Graphs Grid */}
      <ResponsiveGrid>
        {filteredGraphs.map((graph) => (
          <GraphCard
            key={graph.id}
            graph={graph}
            onExecute={setSelectedGraph}
          />
        ))}
      </ResponsiveGrid>

      {/* Execution Order */}
      {executionOrder.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Recommended Execution Order</CardTitle>
            <CardDescription>
              Optimal order for executing graphs based on dependencies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {executionOrder.map((graphId, index) => {
                const graph = graphs.find(g => g.id === graphId);
                return (
                  <Badge key={graphId} variant="outline" className="flex items-center gap-1">
                    <span className="text-xs bg-gray-200 rounded-full w-4 h-4 flex items-center justify-center">
                      {index + 1}
                    </span>
                    {graph?.name || graphId}
                  </Badge>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Execution Dialog */}
      <ExecutionDialog
        graph={selectedGraph}
        onClose={() => setSelectedGraph(null)}
        onExecute={handleExecuteGraph}
      />

      {/* Execution Result */}
      {executionResult && (
        <Card>
          <CardHeader>
            <CardTitle>Execution Result</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-64">
              {JSON.stringify(executionResult, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
