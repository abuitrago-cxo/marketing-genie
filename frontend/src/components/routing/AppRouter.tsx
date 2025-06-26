import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { EnhancedChatInterface, EnhancedMessage } from '../enhanced/EnhancedChatInterface';

interface AppRouterProps {
  messages: EnhancedMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => Promise<void>;
  onStopGeneration: () => void;
  currentView?: string;
  onViewChange?: (view: string) => void;
}


import { ProjectManagementDashboard } from '../enhanced/ProjectManagementDashboard';
import { SpecializedDashboard } from '../specialized/SpecializedDashboard';
import { GitHubRepositories } from '../github/GitHubRepositories';
import ToolExecutionPanel from '../tools/ToolExecutionPanel';
import { AIResearchPage } from '../pages/AIResearchPage';

// Import new page components we'll create
import { ProjectsPage } from '../pages/ProjectsPage';
import { WorkflowsPage } from '../pages/WorkflowsPage';
import { AgentsPage } from '../pages/AgentsPage';
import { IntegrationsPage } from '../pages/IntegrationsPage';
import { SettingsPage } from '../pages/SettingsPage';
import { NotificationsPage } from '../pages/NotificationsPage';
import { SpecializedGraphsPage } from '../pages/SpecializedGraphsPage';

// Individual agent pages
import { ResearchAgentPage } from '../pages/agents/ResearchAgentPage';
import { DevOpsAgentPage } from '../pages/agents/DevOpsAgentPage';
import { AnalysisAgentPage } from '../pages/agents/AnalysisAgentPage';
import { CommunicationAgentPage } from '../pages/agents/CommunicationAgentPage';

// Integration pages
import { DatabaseIntegrationPage } from '../pages/integrations/DatabaseIntegrationPage';
import { CloudServicesPage } from '../pages/integrations/CloudServicesPage';

// MCP Server Management
import MCPServersPage from '../pages/MCPServersPage';
import ImportPage from '../../pages/ImportPage';

export const AppRouter: React.FC<AppRouterProps> = ({ messages, isLoading, onSendMessage, onStopGeneration, currentView, onViewChange }) => {
  return (
    <Routes>
      {/* Main routes */}
      <Route path="/" element={<EnhancedChatInterface messages={messages} isLoading={isLoading} onSendMessage={onSendMessage} onStopGeneration={onStopGeneration} />} />
      <Route path="/chat" element={<EnhancedChatInterface messages={messages} isLoading={isLoading} onSendMessage={onSendMessage} onStopGeneration={onStopGeneration} />} />
      <Route path="/dashboard" element={<ProjectManagementDashboard />} />
      <Route path="/specialized" element={<SpecializedDashboard />} />
      <Route path="/tools" element={<ToolExecutionPanel />} />

      {/* AI Research - Original Google Gemini Interface */}
      <Route path="/research" element={<AIResearchPage />} />

      {/* Projects routes */}
      <Route path="/projects" element={<ProjectsPage />} />
      <Route path="/projects/current" element={<ProjectsPage activeTab="current" />} />
      <Route path="/projects/archived" element={<ProjectsPage activeTab="archived" />} />

      {/* Workflows */}
      <Route path="/workflows" element={<WorkflowsPage />} />

      {/* Specialized Graphs */}
      <Route path="/graphs" element={<SpecializedGraphsPage />} />

      {/* AI Agents routes */}
      <Route path="/agents" element={<AgentsPage />} />
      <Route path="/agents/research" element={<ResearchAgentPage />} />
      <Route path="/agents/devops" element={<DevOpsAgentPage />} />
      <Route path="/agents/analysis" element={<AnalysisAgentPage />} />
      <Route path="/agents/communication" element={<CommunicationAgentPage />} />

      {/* Integrations routes */}
      <Route path="/integrations" element={<IntegrationsPage />} />
      <Route path="/integrations/github" element={<GitHubRepositories />} />
      <Route path="/integrations/database" element={<DatabaseIntegrationPage />} />
      <Route path="/integrations/cloud" element={<CloudServicesPage />} />

      {/* MCP Server Management */}
      <Route path="/mcp-servers" element={<MCPServersPage />} />

      {/* Project Import */}
      <Route path="/import" element={<ImportPage />} />

      {/* Settings and notifications */}
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="/notifications" element={<NotificationsPage />} />

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
