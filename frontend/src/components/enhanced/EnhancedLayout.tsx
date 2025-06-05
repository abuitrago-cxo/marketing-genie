import React, { useState, useEffect } from 'react';
import { EnhancedSidebar } from './EnhancedSidebar';
import { EnhancedChatInterface } from './EnhancedChatInterface';
import { ProjectManagementDashboard } from './ProjectManagementDashboard';
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
  Clock
} from 'lucide-react';
import { cn } from '@/lib/utils';

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
  initialView?: 'chat' | 'dashboard';
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

// Main enhanced layout component
export const EnhancedLayout: React.FC<EnhancedLayoutProps> = ({
  children,
  initialView = 'chat'
}) => {
  const [currentView, setCurrentView] = useState(initialView);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
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
        setCurrentView('chat');
        break;
      case 'dashboard':
        setCurrentView('dashboard');
        break;
      default:
        console.log('Navigate to:', itemId);
    }
  };

  // Mock chat functionality
  const handleSendMessage = (message: string) => {
    console.log('Sending message:', message);
    // This would integrate with your actual chat system
  };

  const handleStopGeneration = () => {
    console.log('Stopping generation');
    // This would stop the current AI generation
  };

  // Render main content based on current view
  const renderMainContent = () => {
    switch (currentView) {
      case 'dashboard':
        return <ProjectManagementDashboard />;
      case 'chat':
      default:
        return (
          <EnhancedChatInterface
            messages={[]} // This would come from your chat state
            isLoading={false}
            onSendMessage={handleSendMessage}
            onStopGeneration={handleStopGeneration}
          />
        );
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <SystemStatusBar status={systemStatus} />

        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsDarkMode(!isDarkMode)}
          >
            {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
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
          </div>
        </div>
      </div>

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <EnhancedSidebar
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          activeItem={currentView}
          onItemClick={handleSidebarItemClick}
        />

        {/* Main content */}
        <div className="flex-1 overflow-hidden">
          {children || renderMainContent()}
        </div>
      </div>
    </div>
  );
};
