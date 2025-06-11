import React, { useState, useEffect } from 'react';
import { useResearchAgent, ResearchResult, ResearchSource, CreateResearchData } from '@/hooks/useResearchAgent';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { 
  Search, 
  Play, 
  Settings, 
  BarChart3, 
  Clock, 
  CheckCircle, 
  ExternalLink,
  FileText,
  Globe,
  BookOpen,
  TrendingUp,
  Activity,
  ArrowLeft
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const TaskCard: React.FC<{ task: ResearchResult }> = ({ task }) => {
  const getFormattedDate = () => {
    return task.created_at ? `Created: ${new Date(task.created_at).toLocaleDateString()}` : 'Date N/A';
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold">{task.query}</CardTitle>
            <div className="flex items-center gap-2 mt-2">
              {/* Status display removed as it's not in ResearchResult */}
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* task.summary is available but not explicitly displayed here. Confidence was removed. */}
        
        <div className="grid grid-cols-2 gap-4 text-sm"> {/* Changed to 2 cols as citations removed */} 
          <div className="text-center">
            <div className="font-medium">{task.sources?.length || 0}</div>
            <div className="text-muted-foreground">Sources</div>
          </div>
          <div className="text-center">
            <div className="font-medium">{getFormattedDate()}</div>
            <div className="text-muted-foreground">Created</div>
          </div>
        </div>

        {/* Progress bar section removed as it depended on 'status' and 'confidence' which are not in ResearchResult */}
      </CardContent>
    </Card>
  );
};

const SourceCard: React.FC<{ source: ResearchSource }> = ({ source }) => {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="space-y-3">
          <div className="flex items-start justify-between">
            <h4 className="font-medium text-sm leading-tight">{source.title}</h4>
            <Button variant="ghost" size="sm" className="shrink-0">
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Globe className="h-4 w-4" />
            <span>{source.domain}</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Relevance</span>
                <span className="font-medium">{source.relevance}%</span>
              </div>
              <Progress value={source.relevance} className="h-1" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Credibility</span>
                <span className="font-medium">{source.credibility}%</span>
              </div>
              <Progress value={source.credibility} className="h-1" />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const ResearchAgentPage = () => {
  const navigate = useNavigate();
  const [newQuery, setNewQuery] = useState('');
  const {
    researchTasks,
    loading,
    error,
    fetchResearchTasks, // We call this in useEffect
    createResearchTask
  } = useResearchAgent();

  const handleStartResearch = () => {
    if (!newQuery.trim()) return;
    console.log('Starting research for:', newQuery);
    // Here you would integrate with the backend to start research
    setNewQuery('');
  };

  const completedTasks = researchTasks.filter(task => task.summary && task.summary.length > 0).length; // Approximation: tasks with a summary are 'completed'
  // Avg Confidence cannot be calculated as 'confidence' is not available in ResearchResult
  const avgConfidence = 0;
  const totalSources = researchTasks.reduce((acc, t) => acc + (t.sources?.length || 0), 0);

  useEffect(() => {
    fetchResearchTasks();
  }, [fetchResearchTasks]);

  if (loading && researchTasks.length === 0) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-100px)]">
        <div role="status">
          <svg aria-hidden="true" className="w-10 h-10 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
              <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0492C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
          </svg>
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-[calc(100vh-100px)] text-red-600 dark:text-red-400 p-6">
        <FileText size={48} className="mb-4" />
        <h2 className="text-2xl font-semibold mb-2">Error Fetching Research Data</h2>
        <p className="mb-4 text-center">{error}</p>
        <Button onClick={() => fetchResearchTasks()}><Activity className="mr-2 h-4 w-4"/>Retry</Button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/agents')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Search className="h-8 w-8 text-blue-600" />
            Research Specialist
          </h1>
          <p className="text-muted-foreground">
            Comprehensive research and analysis with multi-source validation
          </p>
        </div>
        <Button variant="outline">
          <Settings className="h-4 w-4 mr-2" />
          Configure
        </Button>
      </div>

      {/* Stats overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold">{completedTasks}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-xs text-muted-foreground">Confidence: {avgConfidence}%</p>
                <p className="text-2xl font-bold">{avgConfidence > 0 ? `${avgConfidence}%` : 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-xs text-muted-foreground">Sources: {totalSources}</p>
                <p className="text-2xl font-bold">{totalSources}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="text-2xl font-bold text-green-600">Active</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* New research input */}
      <Card>
        <CardHeader>
          <CardTitle>Start New Research</CardTitle>
          <CardDescription>
            Enter your research query and the agent will conduct comprehensive analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="What would you like to research? (e.g., 'Latest developments in quantum computing applications')"
            value={newQuery}
            onChange={(e) => setNewQuery(e.target.value)}
            rows={3}
          />
          <Button onClick={handleStartResearch} disabled={!newQuery.trim()}>
            <Play className="h-4 w-4 mr-2" />
            Start Research
          </Button>
        </CardContent>
      </Card>

      {/* Tabs for tasks and sources */}
      <Tabs defaultValue="tasks">
        <TabsList>
          <TabsTrigger value="tasks">Research Tasks</TabsTrigger>
          <TabsTrigger value="sources">Sources</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="tasks" className="space-y-4">
          {researchTasks.map((task) => (
            <TaskCard key={task.id.toString()} task={task} /> /* task.id is number */
          ))}
        </TabsContent>

                <TabsContent value="sources" className="space-y-4">
          {researchTasks.length === 0 && !loading && (
            <Card>
              <CardContent className="p-6 text-center text-muted-foreground">
                <FileText size={32} className="mx-auto mb-2" />
                No research tasks with sources found.
              </CardContent>
            </Card>
          )}
          {researchTasks.map(task => (
            task.sources && task.sources.length > 0 && (
              <Card key={`task-src-${task.id}`} className='mb-4'>
                <CardHeader>
                  <CardTitle className="text-md">Sources for: "{task.query.length > 60 ? task.query.substring(0, 60) + '...' : task.query}"</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {task.sources.map((source, index) => (
                      <SourceCard key={`${task.id}-s-${index}`} source={source} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            )
          ))}
        </TabsContent>

        <TabsContent value="analytics">
          <Card>
            <CardHeader>
              <CardTitle>Performance Analytics</CardTitle>
              <CardDescription>
                Detailed analytics and performance metrics for the Research Agent
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                <BarChart3 className="h-12 w-12 mx-auto mb-4" />
                <p>Analytics dashboard coming soon...</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};
