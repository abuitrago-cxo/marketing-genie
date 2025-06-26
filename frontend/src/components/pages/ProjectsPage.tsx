import React, { useState, useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { ResponsiveGrid } from '@/components/ui/horizontal-scroll';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Pencil,
  Calendar,
  Users,
  GitBranch,
  Activity,
  Archive,
  Star,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Loader2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { EditProjectDialog } from '@/components/projects/EditProjectDialog';
import {
  useProjects,
  Project,
  CodebaseAnalysisResponse,
  DocumentationAnalysisResponse,
  TaskPlanningRequest,
  ResearchAnalysisRequest,
  QATestingRequest,
  ProjectOrchestratorRequest,
} from '@/hooks/useProjects';
import { AnalysisResultsModal } from '@/components/analysis/AnalysisResultsModal';
import { AgentTaskResultsModal } from '@/components/agent/AgentTaskResultsModal';
import { useToast } from '@/components/ui/toast';

interface ProjectsPageProps {
  activeTab?: 'current' | 'archived';
}

// Use Omit to drop the original 'team' (string) field and replace with 'teamMembers' (string[])
interface UIProject extends Omit<Project, 'team'> {
  progress: number;
  dueDate: Date;
  teamMembers: string[];
  lastActivity: Date;
  tags: string[];
  isStarred: boolean;
}

// Helper function to convert API Project to UI Project
const convertToUIProject = (project: Project): UIProject => {
  // Extract team members from team string (comma-separated)
  const teamMembers = project.team ? project.team.split(',').map(t => t.trim()) : [];

  // Extract tags from metadata or generate from project info
  const tags = project.github_metadata?.topics ||
               [project.priority, project.status].filter(Boolean);

  // Calculate progress based on status (this could be enhanced with actual task completion)
  const progressMap: Record<string, number> = {
    'pending': 0,
    'active': 50,
    'in_progress': 50,
    'completed': 100,
    'archived': 100,
    'paused': 25
  };

  return {
    ...project,
    progress: progressMap[project.status] || 0,
    dueDate: new Date(project.updated_at), // Placeholder - could be enhanced with actual due dates
    teamMembers,
    lastActivity: new Date(project.updated_at),
    tags: tags,
    isStarred: false // This could be stored in user preferences
  };
};

const statusIcons = {
  active: <Activity className="h-4 w-4 text-green-500" />,
  completed: <CheckCircle className="h-4 w-4 text-blue-500" />,
  paused: <AlertCircle className="h-4 w-4 text-yellow-500" />,
  archived: <Archive className="h-4 w-4 text-gray-500" />
};

const priorityColors = {
  low: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  medium: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  high: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
};

const ProjectCard: React.FC<{
  project: UIProject;
  onStarToggle: (id: number) => void;
  onAnalyze: (id: number) => void;
  onAnalyzeDocs: (id: number) => void;
  onAnalyzeTasks: (id: number) => void;
  onAnalyzeResearch: (id: number) => void;
  onAnalyzeQA: (id: number) => void;
  onRunCodeEngineer: (id: number) => void;
  onOrchestrate: (id: number) => void;
  onShowResults: (id: number) => void;
  isEngineering: boolean;
  onEdit?: (project: UIProject) => void;
  hasAnalysisResults: boolean;
}> = ({
  project,
  onStarToggle,
  onAnalyze,
  onAnalyzeDocs,
  onAnalyzeTasks,
  onAnalyzeResearch,
  onAnalyzeQA,
  onRunCodeEngineer,
  isEngineering,
  onOrchestrate,
  onShowResults,
  onEdit,
  hasAnalysisResults
}) => {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return formatDate(date);
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {onEdit && (
              <button onClick={() => onEdit(project)} className="p-1 hover:bg-muted rounded">
                <Pencil className="h-4 w-4" />
              </button>
            )}
            {statusIcons[project.status]}
            <CardTitle className="text-lg">{project.name}</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onStarToggle(project.id)}
              className="p-1 h-auto"
            >
              <Star className={cn(
                "h-4 w-4",
                project.isStarred ? "fill-yellow-400 text-yellow-400" : "text-gray-400"
              )} />
            </Button>
          </div>
          <div className="flex gap-1 flex-wrap">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAnalyze(project.id)}
              title="Analyze Codebase"
            >
              <Activity className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAnalyzeDocs(project.id)}
              title="Analyze Documentation"
            >
              <Archive className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAnalyzeTasks(project.id)}
              title="Task Planning Analysis"
            >
              <Calendar className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAnalyzeResearch(project.id)}
              title="Research Analysis"
            >
              <Search className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onAnalyzeQA(project.id)}
              title="QA & Testing Analysis"
            >
              <CheckCircle className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onOrchestrate(project.id)}
              title="Project Orchestration"
            >
              <Users className="h-4 w-4" />
            </Button>
            {hasAnalysisResults && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onShowResults(project.id)}
                title="View Analysis Results"
                className="text-green-600 hover:text-green-700"
              >
                <Star className="h-4 w-4" />
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={() => onEdit(project)}>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={() => onAnalyze(project.id)} className="mr-2">
              Analyze Code
            </Button>
            <Button variant="secondary" size="sm" onClick={() => onRunCodeEngineer(project.id)} className="mr-2" disabled={isEngineering}>
              {isEngineering ? (
                <span className="flex items-center"><Loader2 className="h-4 w-4 animate-spin mr-1"/>Running...</span>
              ) : (
                'Code Engineer'
              )}
            </Button>
          </div>
        </div>
        <CardDescription className="text-sm">
          {project.description}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{project.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${project.progress}%` }}
            />
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1">
          {project.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
          {project.tags.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{project.tags.length - 3}
            </Badge>
          )}
          {hasAnalysisResults && (
            <Badge variant="default" className="text-xs bg-green-100 text-green-800 hover:bg-green-200">
              ✓ Analysis Ready
            </Badge>
          )}
        </div>

        {/* Project details */}
        <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Due {formatDate(project.dueDate)}</span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            <span>{project.teamMembers.length} members</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>{getTimeAgo(project.lastActivity)}</span>
          </div>
          {project.github_repo_url && (
            <div className="flex items-center gap-2">
              <GitBranch className="h-4 w-4" />
              <span className="truncate">Repository</span>
            </div>
          )}
        </div>

        {/* Priority badge */}
        <div className="flex justify-between items-center">
          <Badge className={cn("text-xs", priorityColors[project.priority])}>
            {project.priority.toUpperCase()} PRIORITY
          </Badge>
          <span className="text-xs text-muted-foreground capitalize">
            {project.status}
          </span>
        </div>
      </CardContent>
    </Card>
  );
};

export const ProjectsPage: React.FC<{ activeTab?: 'current' | 'archived' }> = ({ activeTab = 'current' }) => {
  const {
    projects: apiProjects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    analyzeCodebase,
    getAnalysisStatus,
    analyzeDocumentation,
    analyzeTasks,
    analyzeResearch,
    analyzeQA,
    runCodeEngineer,
    orchestrateProject,
  } = useProjects();
  const { addToast, ToastContainer } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [engineeringProjects, setEngineeringProjects] = useState<Set<number>>(new Set());
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState<'current' | 'archived'>(activeTab);
  const [starredProjects, setStarredProjects] = useState<Set<number>>(new Set());
  const [editingProject, setEditingProject] = useState<UIProject | null>(null);

  const location = useLocation();
  const runEngineerId = useMemo(() => {
    const param = new URLSearchParams(location.search).get('runEngineer');
    return param ? parseInt(param, 10) : null;
  }, [location]);
  const [runEngineerTriggered, setRunEngineerTriggered] = useState(false);

  // Auto-launch Code Engineer after projects load
  useEffect(() => {
    if (runEngineerId && !runEngineerTriggered && projects.length) {
      const exists = projects.some(p => p.id === runEngineerId);
      if (exists) {
        handleRunCodeEngineer(runEngineerId);
        setRunEngineerTriggered(true);
      }
    }
  }, [runEngineerId, runEngineerTriggered, projects]);
  const [editOpen, setEditOpen] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<Map<number, CodebaseAnalysisResponse>>(new Map());
  const [docAnalysisResults, setDocAnalysisResults] = useState<Map<number, DocumentationAnalysisResponse>>(new Map());
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [selectedProjectForAnalysis, setSelectedProjectForAnalysis] = useState<UIProject | null>(null);

  // Convert API projects to UI projects
  const projects = useMemo(() => apiProjects.map(convertToUIProject).map(project => ({
    ...project,
    isStarred: starredProjects.has(project.id)
  })), [apiProjects, starredProjects]);

  const handleStarToggle = (projectId: number) => {
    setStarredProjects(prev => {
      const newSet = new Set(prev);
      if (newSet.has(projectId)) {
        newSet.delete(projectId);
      } else {
        newSet.add(projectId);
      }
      return newSet;
    });
  };

  const handleAnalyzeCodebase = async (projectId: number) => {
    try {
      const project = projects.find(p => p.id === projectId);
      if (!project) return;

      const analysisRequest = {
        repository_url: project.github_repo_url,
        analysis_type: 'comprehensive' as const
      };

      const result = await analyzeCodebase(projectId, analysisRequest);

      if (result) {
        setAnalysisResults(prev => new Map(prev).set(projectId, result));

        // Show success toast
        addToast({
          type: 'success',
          title: 'Codebase Analysis Complete',
          description: `Analysis for ${project.name} completed with score ${result.results?.overall_score}/10`
        });

        // Show results modal
        setSelectedProjectForAnalysis(project);
        setShowAnalysisModal(true);

        console.log('Codebase analysis completed:', result);
      }
    } catch (error) {
      console.error('Failed to analyze codebase:', error);
      addToast({
        type: 'error',
        title: 'Analysis Failed',
        description: 'Failed to analyze codebase. Please try again.'
      });
    }
  };

  const handleAnalyzeDocumentation = async (projectId: number) => {
    try {
      const project = projects.find(p => p.id === projectId);
      if (!project) return;

      const analysisRequest = {
        repository_url: project.github_repo_url,
        analysis_scope: 'comprehensive' as const
      };

      const result = await analyzeDocumentation(projectId, analysisRequest);

      if (result) {
        setDocAnalysisResults(prev => new Map(prev).set(projectId, result));

        // Show success toast
        addToast({
          type: 'success',
          title: 'Documentation Analysis Complete',
          description: `Documentation analysis for ${project.name} completed with score ${result.results?.overall_score}/10`
        });

        // Show results modal
        setSelectedProjectForAnalysis(project);
        setShowAnalysisModal(true);

        console.log('Documentation analysis completed:', result);
      }
    } catch (error) {
      console.error('Failed to analyze documentation:', error);
      addToast({
        type: 'error',
        title: 'Documentation Analysis Failed',
        description: 'Failed to analyze documentation. Please try again.'
      });
    }
  };

  const handleAnalyzeTasks = async (projectId: number) => {
    try {
      const project = projects.find(p => p.id === projectId);
      if (!project) return;

      const analysisRequest: TaskPlanningRequest = {
        planning_scope: `Task planning for ${project.name}`,
        project_requirements: [project.description || 'Project requirements'],
        methodology: 'agile_scrum',
        team_size: project.teamMembers.length || 4,
        timeline_weeks: 12,
      };

      const result = await analyzeTasks(projectId, analysisRequest);

      if (result) {
        addToast({
          type: 'success',
          title: 'Task Planning Analysis Started',
          description: result.message,
        });
        console.log('Task planning analysis started:', result);
      }
    } catch (error) {
      console.error('Failed to start task planning analysis:', error);
      addToast({
        type: 'error',
        title: 'Task Planning Analysis Failed',
        description: 'Failed to start task planning analysis. Please try again.'
      });
    }
  };

  const handleAnalyzeResearch = async (projectId: number) => {
    try {
      const project = projects.find(p => p.id === projectId);
      if (!project) return;

      const analysisRequest: ResearchAnalysisRequest = {
        research_topic: `Research analysis for ${project.name}`,
        research_scope: 'comprehensive',
        information_sources: ['academic', 'technical', 'industry'],
        depth_level: 'comprehensive',
      };

      const result = await analyzeResearch(projectId, analysisRequest);

      if (result) {
        addToast({
          type: 'success',
          title: 'Research Analysis Started',
          description: result.message,
        });
        console.log('Research analysis started:', result);
      }
    } catch (error) {
      console.error('Failed to start research analysis:', error);
      addToast({
        type: 'error',
        title: 'Research Analysis Failed',
        description: 'Failed to start research analysis. Please try again.'
      });
    }
  };

  const handleAnalyzeQA = async (projectId: number) => {
    try {
      const project = projects.find(p => p.id === projectId);
      if (!project) return;

      const analysisRequest: QATestingRequest = {
        qa_scope: `QA analysis for ${project.name}`,
        test_categories: ['unit_testing', 'integration_testing', 'security_testing'],
        quality_standards: { code_coverage_target: 80, security_level: 'standard' },
        coverage_target: 80,
      };

      const result = await analyzeQA(projectId, analysisRequest);

      if (result) {
        addToast({
          type: 'success',
          title: 'QA Testing Analysis Started',
          description: result.message,
        });
        console.log('QA testing analysis started:', result);
      }
    } catch (error) {
      console.error('Failed to start QA testing analysis:', error);
      addToast({
        type: 'error',
        title: 'QA Testing Analysis Failed',
        description: 'Failed to start QA testing analysis. Please try again.'
      });
    }
  };

  const handleRunCodeEngineer = async (projectId: number) => {
  setEngineeringProjects(prev => new Set(prev).add(projectId));
    addToast({ type: 'info', title: 'Code Engineer', description: 'Starting Code Engineer task...' });
    const res = await runCodeEngineer(projectId);
  
    if (res?.success) {
    if (res.task_id) {
      setCurrentTaskId(res.task_id as string);
      setTaskModalOpen(true);
    }
    // keep spinner for a short period then remove
    setTimeout(() => {
      setEngineeringProjects(prev => { const n=new Set(prev); n.delete(projectId); return n;});
    }, 5000);
      addToast({ type: 'success', title: 'Code Engineer', description: 'Task created successfully.' });
    } else {
      addToast({ type: 'error', title: 'Code Engineer', description: res?.detail || 'Failed to start task' });
    }
  };

  const handleOrchestrate = async (projectId: number) => {
    try {
      const project = projects.find(p => p.id === projectId);
      if (!project) return;

      const orchestrationRequest: ProjectOrchestratorRequest = {
        project_context: {
          name: project.name,
          size: 'medium',
          team_size: project.teamMembers.length || 4,
          timeline_weeks: 12,
          complexity: project.priority,
        },
        active_graphs: [
          'codebase_analysis',
          'documentation_analysis',
          'task_planning',
          'research_analysis',
          'qa_testing',
        ],
        coordination_strategy: 'matrix_coordination',
        resource_constraints: { budget_level: 'standard' },
      };

      const result = await orchestrateProject(projectId, orchestrationRequest);

      if (result) {
        addToast({
          type: 'success',
          title: 'Project Orchestration Started',
          description: result.message,
        });
        console.log('Project orchestration started:', result);
      }
    } catch (error) {
      console.error('Failed to start project orchestration:', error);
      addToast({
        type: 'error',
        title: 'Project Orchestration Failed',
        description: 'Failed to start project orchestration. Please try again.'
      });
    }
  };

  const handleShowAnalysisResults = (projectId: number) => {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    // Check if we have any analysis results for this project
    const hasCodebaseResults = analysisResults.has(projectId);
    const hasDocResults = docAnalysisResults.has(projectId);

    if (hasCodebaseResults || hasDocResults) {
      setSelectedProjectForAnalysis(project);
      setShowAnalysisModal(true);
    }
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (project.description || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                         project.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    if (selectedTab === 'current') {
      return matchesSearch && project.status !== 'archived';
    } else {
      return matchesSearch && project.status === 'archived';
    }
  });

  const handleCreateProject = async () => {
    // This would open a modal or navigate to a create project page
    // For now, we'll create a sample project
    const newProject = await createProject({
      name: 'New Project',
      description: 'A new project created from the UI',
      status: 'active',
      priority: 'medium',
      user_id: 'current_user' // This would come from auth context
    });

    if (newProject) {
      console.log('Project created:', newProject);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Manage and track your software development projects
          </p>
        </div>
        <Button onClick={handleCreateProject} disabled={loading}>
          {loading ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Plus className="h-4 w-4 mr-2" />
          )}
          New Project
        </Button>
      </div>

      {/* Error display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error loading projects</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
              <Button
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={() => fetchProjects()}
              >
                Try Again
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Search and filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={selectedTab} onValueChange={(value) => setSelectedTab(value as 'current' | 'archived')}>
        <TabsList>
          <TabsTrigger value="current">Current Projects</TabsTrigger>
          <TabsTrigger value="archived">Archived</TabsTrigger>
        </TabsList>

        <TabsContent value="current" className="mt-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading projects...</span>
            </div>
          ) : (
            <ResponsiveGrid minItemWidth={350} gap={24}>
              {filteredProjects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onStarToggle={handleStarToggle}
                  onAnalyze={handleAnalyzeCodebase}
                  onAnalyzeDocs={handleAnalyzeDocumentation}
                  onAnalyzeTasks={handleAnalyzeTasks}
                  onAnalyzeResearch={handleAnalyzeResearch}
                  onAnalyzeQA={handleAnalyzeQA}
                  onRunCodeEngineer={handleRunCodeEngineer}
                  onOrchestrate={handleOrchestrate}
                  onShowResults={handleShowAnalysisResults}
                  onEdit={(p) => {
                    setEditingProject(p);
                    setEditOpen(true);
                  }}
                  hasAnalysisResults={analysisResults.has(project.id) || docAnalysisResults.has(project.id)}
                  isEngineering={engineeringProjects.has(project.id)}
                />
              ))}
            </ResponsiveGrid>
          )}
        </TabsContent>

        <TabsContent value="archived" className="mt-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading projects...</span>
            </div>
          ) : (
            <ResponsiveGrid minItemWidth={350} gap={24}>
              {filteredProjects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onStarToggle={handleStarToggle}
                  onAnalyze={handleAnalyzeCodebase}
                  onAnalyzeDocs={handleAnalyzeDocumentation}
                  onAnalyzeTasks={handleAnalyzeTasks}
                  onAnalyzeResearch={handleAnalyzeResearch}
                  onAnalyzeQA={handleAnalyzeQA}
                  onRunCodeEngineer={handleRunCodeEngineer}
                  onOrchestrate={handleOrchestrate}
                  onShowResults={handleShowAnalysisResults}
                  onEdit={(p) => {
                    setEditingProject(p);
                    setEditOpen(true);
                  }}
                  hasAnalysisResults={analysisResults.has(project.id) || docAnalysisResults.has(project.id)}
                  isEngineering={engineeringProjects.has(project.id)}
                />
              ))}
            </ResponsiveGrid>
          )}
        </TabsContent>
      </Tabs>

      {/* Empty state */}
      {filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <div className="mx-auto w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-4">
            <Archive className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-2">No projects found</h3>
          <p className="text-muted-foreground mb-4">
            {searchQuery ? 'Try adjusting your search criteria' : 'Get started by creating your first project'}
          </p>
          {!searchQuery && (
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Project
            </Button>
          )}
        </div>
      )}

      {/* Analysis Results Modal */}
      {selectedProjectForAnalysis && (
        <AnalysisResultsModal
          isOpen={showAnalysisModal}
          onClose={() => {
            setShowAnalysisModal(false);
            setSelectedProjectForAnalysis(null);
          }}
          projectName={selectedProjectForAnalysis.name}
          codebaseResults={analysisResults.get(selectedProjectForAnalysis.id)}
          documentationResults={docAnalysisResults.get(selectedProjectForAnalysis.id)}
        />
      )}

      {/* Edit Project Dialog */}
      <EditProjectDialog
        project={editingProject}
        open={editOpen}
        onOpenChange={(open) => {
          setEditOpen(open);
          if (!open) setEditingProject(null);
        }}
        onSave={async (id, data) => {
          await updateProject(id, data);
          setEditOpen(false);
          await fetchProjects();
        }}
      />

      {/* Toast Notifications */}
      <ToastContainer />

      {/* Agent Task Results Modal */}
      <AgentTaskResultsModal
        isOpen={taskModalOpen}
        taskId={currentTaskId}
        onClose={() => setTaskModalOpen(false)}
      />
    </div>
  );
};
