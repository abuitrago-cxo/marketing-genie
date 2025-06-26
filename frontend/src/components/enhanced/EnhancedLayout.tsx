import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { EnhancedSidebar } from './EnhancedSidebar';
import { AppRouter } from '../routing/AppRouter';
import { EnhancedMessage } from './EnhancedChatInterface';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import {
  Sun,
  Moon,
  Maximize2,
  Minimize2,
  Wifi,
  WifiOff,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  Settings
} from 'lucide-react';
import { cn } from '@/lib/utils';
// import { AuthNav } from '@/components/auth/AuthNav';

// Types for the enhanced layout
interface SystemStatus {
  isOnline: boolean;
  activeAgents: number;
  lastSync: Date;
  systemHealth: 'healthy' | 'warning' | 'error';
}

interface NotificationItem {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: Date;
  isRead: boolean;
}

interface EnhancedLayoutProps {
  children?: React.ReactNode;
  headerActions?: React.ReactNode;
}

// Sample data
const sampleNotifications: NotificationItem[] = [
  {
    id: '1',
    type: 'success',
    title: 'Deployment Complete',
    message: 'Successfully deployed to staging environment',
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    isRead: false
  },
  {
    id: '2',
    type: 'warning',
    title: 'Code Quality Alert',
    message: 'Found 3 potential security vulnerabilities',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    isRead: false
  },
  {
    id: '3',
    type: 'info',
    title: 'Agent Update',
    message: 'Research Agent completed market analysis',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    isRead: true
  }
];

// System status component
const SystemStatusBar: React.FC<{ status: SystemStatus }> = ({ status }) => {
  const healthColors = {
    'healthy': 'text-green-600',
    'warning': 'text-yellow-600',
    'error': 'text-red-600'
  };

  const healthIcons = {
    'healthy': <CheckCircle className="h-4 w-4" />,
    'warning': <AlertCircle className="h-4 w-4" />,
    'error': <AlertCircle className="h-4 w-4" />
  };

  return (
    <div className="flex items-center gap-4 text-sm text-muted-foreground">
      {/* Connection status */}
      <div className="flex items-center gap-1">
        {status.isOnline ? (
          <Wifi className="h-4 w-4 text-green-600" />
        ) : (
          <WifiOff className="h-4 w-4 text-red-600" />
        )}
        <span>{status.isOnline ? 'Online' : 'Offline'}</span>
      </div>

      <Separator orientation="vertical" className="h-4" />

      {/* Active agents */}
      <div className="flex items-center gap-1">
        <Activity className="h-4 w-4" />
        <span>{status.activeAgents} agents active</span>
      </div>

      <Separator orientation="vertical" className="h-4" />

      {/* System health */}
      <div className={cn("flex items-center gap-1", healthColors[status.systemHealth])}>
        {healthIcons[status.systemHealth]}
        <span className="capitalize">{status.systemHealth}</span>
      </div>

      <Separator orientation="vertical" className="h-4" />

      {/* Last sync */}
      <div className="flex items-center gap-1">
        <Clock className="h-4 w-4" />
        <span>Synced {status.lastSync.toLocaleTimeString()}</span>
      </div>
    </div>
  );
};

// Notification panel component
const NotificationPanel: React.FC<{
  notifications: NotificationItem[];
  isOpen: boolean;
  onClose: () => void;
}> = ({ notifications, isOpen, onClose }) => {
  if (!isOpen) return null;

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const typeIcons = {
    'info': <Activity className="h-4 w-4 text-blue-500" />,
    'warning': <AlertCircle className="h-4 w-4 text-yellow-500" />,
    'error': <AlertCircle className="h-4 w-4 text-red-500" />,
    'success': <CheckCircle className="h-4 w-4 text-green-500" />
  };

  return (
    <Card className="absolute top-12 right-4 w-80 max-h-96 z-50 shadow-lg">
      <CardContent className="p-0">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Notifications</h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {unreadCount} new
                </Badge>
              )}
              <Button variant="ghost" size="sm" onClick={onClose}>
                ×
              </Button>
            </div>
          </div>
        </div>

        <div className="max-h-64 overflow-y-auto">
          {notifications.length === 0 ? (
            <div className="p-4 text-center text-muted-foreground">
              No notifications
            </div>
          ) : (
            <div className="divide-y">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={cn(
                    "p-4 hover:bg-muted/50 transition-colors",
                    !notification.isRead && "bg-muted/30"
                  )}
                >
                  <div className="flex items-start gap-3">
                    {typeIcons[notification.type]}
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium">{notification.title}</h4>
                        {!notification.isRead && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {notification.message}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {notification.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Settings panel component
const SettingsPanel: React.FC<{
  isDarkMode: boolean;
  setIsDarkMode: (isDarkMode: boolean) => void;
  isOpen: boolean;
  onClose: () => void;
}> = ({ isDarkMode, setIsDarkMode, isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <Card className="absolute top-12 right-4 w-80 z-50 shadow-lg bg-background">
      <CardContent className="p-0">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Settings</h3>
            <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onClose}>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </Button>
          </div>
        </div>
        <div className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm">Dark Mode</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="px-2"
            >
              {isDarkMode ? <Sun className="h-4 w-4 mr-1" /> : <Moon className="h-4 w-4 mr-1" />}
              {isDarkMode ? 'Light' : 'Dark'}
            </Button>
          </div>
          {/* Future settings can be added here */}
        </div>
      </CardContent>
    </Card>
  );
};

// Main enhanced layout component
export const EnhancedLayout: React.FC<EnhancedLayoutProps> = ({
  children,
  headerActions
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Get current view from URL path
  const getCurrentView = () => {
    const path = location.pathname;
    if (path.startsWith('/dashboard')) return 'dashboard';
    if (path.startsWith('/projects')) return 'projects';
    if (path.startsWith('/specialized')) return 'specialized';
    if (path.startsWith('/agents')) return 'agents';
    if (path.startsWith('/workflows')) return 'workflows';
    if (path.startsWith('/graphs')) return 'graphs';
    if (path.startsWith('/integrations')) return 'integrations';
    if (path.startsWith('/tools')) return 'tools';
    if (path.startsWith('/mcp-servers')) return 'mcp-servers';
    if (path.startsWith('/settings')) return 'settings';
    if (path.startsWith('/notifications')) return 'notifications';
    return 'chat';
  };

  const currentView = getCurrentView();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [messages, setMessages] = useState<EnhancedMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false); // New state for settings panel

  const [systemStatus] = useState<SystemStatus>({
    isOnline: true,
    activeAgents: 4,
    lastSync: new Date(),
    systemHealth: 'healthy'
  });

  // Handle theme toggle
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Handle fullscreen toggle
  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Handle sidebar item clicks
  const handleSidebarItemClick = (itemId: string) => {
    switch (itemId) {
      case 'chat':
        navigate('/chat');
        break;
      case 'research':
        navigate('/research');
        break;
      case 'dashboard':
        navigate('/dashboard');
        break;
      case 'tools':
        navigate('/tools');
        break;
      case 'projects':
        navigate('/projects');
        break;
      case 'current-project':
        navigate('/projects/current');
        break;
      case 'archived':
        navigate('/projects/archived');
        break;
      case 'agents':
        navigate('/agents');
        break;
      case 'specialized':
        navigate('/specialized');
        break;
      case 'research-agent':
        navigate('/agents/research');
        break;
      case 'devops-agent':
        navigate('/agents/devops');
        break;
      case 'analysis-agent':
        navigate('/agents/analysis');
        break;
      case 'communication-agent':
        navigate('/agents/communication');
        break;
      case 'workflows':
        navigate('/workflows');
        break;
      case 'graphs':
        navigate('/graphs');
        break;
      case 'integrations':
        navigate('/integrations');
        break;
      case 'github':
        navigate('/integrations/github');
        break;
      case 'database':
        navigate('/integrations/database');
        break;
      case 'cloud':
        navigate('/integrations/cloud');
        break;
      case 'mcp-servers':
        navigate('/mcp-servers');
        break;
      case 'settings':
        navigate('/settings');
        break;
      case 'notifications':
        navigate('/notifications');
        break;
      default:
        console.log('Navigate to:', itemId);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const newUserMessage: EnhancedMessage = {
      id: `human-${Date.now()}`,
      type: 'human',
      content: message.trim(),
    };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);

    setIsLoading(true);

    try {
      const response = await fetch('/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: message.trim()
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json(); // Expects ThreadResponse
      console.log('EnhancedLayout API response:', data);
      // Check for different response formats
      let aiResponseMessage;
      if (data.content) {
        // Direct content in response
        aiResponseMessage = data.content;
      } else if (data.messages && data.messages.length > 0) {
        // Messages array in response
        aiResponseMessage = data.messages[0].content;
      } else if (data.final_answer) {
        // Legacy format with final_answer
        aiResponseMessage = data.final_answer;
      } else {
        // Fallback
        aiResponseMessage = "I couldn't generate a response.";
      }
      const agentResponse: EnhancedMessage = {
        id: `ai-${data.id || Date.now()}`,
        type: 'ai',
        content: aiResponseMessage,
      };
      setMessages((prevMessages) => [...prevMessages, agentResponse]);
    } catch (error) {
      console.error('Error sending message to backend:', error);
      const errorMessage: EnhancedMessage = {
        id: `error-${Date.now()}`,
        type: 'error',
        content: `Error: Could not connect to the AI agent. Please try again. (${error.message})`,
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopGeneration = () => {
    console.log('Stopping generation');
    // This would stop the current AI generation
    // For now, we don't have a way to stop an ongoing fetch request easily.
    // In a real-world scenario, you might use AbortController.
  };

  // Main content is now handled by AppRouter

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <SystemStatusBar status={systemStatus} />

        <div className="flex items-center gap-4">
          {/* Header actions (like specialized agent toggle) */}
          {headerActions}

          <div className="flex items-center gap-2">
            
            {/* Settings button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4" />
            </Button>

            {/* Fullscreen toggle */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleFullscreen}
            >
              {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
            </Button>

            {/* Notifications */}
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowNotifications(!showNotifications)}
              >
                <Activity className="h-4 w-4" />
                {sampleNotifications.filter(n => !n.isRead).length > 0 && (
                  <Badge className="absolute -top-1 -right-1 w-5 h-5 p-0 text-xs">
                    {sampleNotifications.filter(n => !n.isRead).length}
                  </Badge>
                )}
              </Button>

              <NotificationPanel
                notifications={sampleNotifications}
                isOpen={showNotifications}
                onClose={() => setShowNotifications(false)}
              />
              <SettingsPanel
                isDarkMode={isDarkMode}
                setIsDarkMode={setIsDarkMode}
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main layout */}
      <div className="flex flex-row flex-1 overflow-hidden">
        {/* Sidebar - with its own scroll container */}
        <div className="h-full overflow-y-auto">
          <EnhancedSidebar
            isCollapsed={isSidebarCollapsed}
            onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            activeItem={currentView}
            onItemClick={handleSidebarItemClick}
          />
        </div>

        {/* Main content - with its own scroll container */}
        <div className="flex-1 flex flex-col h-full overflow-hidden">
          {children || <AppRouter messages={messages} isLoading={isLoading} onSendMessage={handleSendMessage} onStopGeneration={handleStopGeneration} />}
        </div>
      </div>
    </div>
  );
};
