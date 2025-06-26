import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
  MessageSquare,
  BarChart3,
  Settings,
  Users,
  FolderOpen,
  GitBranch,
  Activity,
  Bell,
  Search,
  ChevronLeft,
  ChevronRight,
  Bot,
  Zap,
  FileText,
  Target,
  Code,
  Database,
  Cloud,
  Shield,
  Workflow,
  Wrench,
  Server,
  Brain,
  FilePlus
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types for sidebar
interface SidebarItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  badge?: string | number;
  isActive?: boolean;
  children?: SidebarItem[];
}

interface AgentQuickAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
  color: string;
}

interface EnhancedSidebarProps {
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  activeItem?: string;
  onItemClick?: (itemId: string) => void;
  className?: string;
}

// Navigation items
const navigationItems: SidebarItem[] = [
  {
    id: 'chat',
    label: 'AI Chat',
    icon: <MessageSquare className="h-4 w-4" />,
    badge: '2',
    isActive: true
  },
  {
    id: 'research',
    label: 'Research-Augmented Conversational AI',
    icon: <Brain className="h-4 w-4" />,
    badge: 'Original'
  },
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <BarChart3 className="h-4 w-4" />
  },
  {
    id: 'tools',
    label: 'Tools',
    icon: <Wrench className="h-4 w-4" />,
    badge: '8'
  },
  {
    id: 'projects',
    label: 'Projects',
    icon: <FolderOpen className="h-4 w-4" />,
    children: [
      {
        id: 'current-project',
        label: 'Current Project',
        icon: <Target className="h-4 w-4" />
      },
      {
        id: 'archived',
        label: 'Archived',
        icon: <FileText className="h-4 w-4" />
      }
    ]
  },
  {
    id: 'import',
    label: 'Import Project',
    icon: <FilePlus className="h-4 w-4" />
  },
  {
    id: 'agents',
    label: 'AI Agents',
    icon: <Bot className="h-4 w-4" />,
    badge: '4',
    children: [
      {
        id: 'specialized',
        label: 'Specialized Dashboard',
        icon: <Brain className="h-4 w-4" />,
        badge: 'Enhanced'
      },
      {
        id: 'research-agent',
        label: 'Research Agent',
        icon: <Search className="h-4 w-4" />
      },
      {
        id: 'devops-agent',
        label: 'DevOps Agent',
        icon: <GitBranch className="h-4 w-4" />
      },
      {
        id: 'analysis-agent',
        label: 'Analysis Agent',
        icon: <Activity className="h-4 w-4" />
      },
      {
        id: 'communication-agent',
        label: 'Communication Agent',
        icon: <Users className="h-4 w-4" />
      }
    ]
  },
  {
    id: 'workflows',
    label: 'Workflows',
    icon: <Workflow className="h-4 w-4" />
  },
  {
    id: 'graphs',
    label: 'Specialized Graphs',
    icon: <GitBranch className="h-4 w-4" />,
    badge: '6'
  },
  {
    id: 'integrations',
    label: 'Integrations',
    icon: <Zap className="h-4 w-4" />,
    children: [
      {
        id: 'github',
        label: 'GitHub',
        icon: <Code className="h-4 w-4" />
      },
      {
        id: 'database',
        label: 'Database',
        icon: <Database className="h-4 w-4" />
      },
      {
        id: 'cloud',
        label: 'Cloud Services',
        icon: <Cloud className="h-4 w-4" />
      }
    ]
  },
  {
    id: 'mcp-servers',
    label: 'MCP Servers',
    icon: <Server className="h-4 w-4" />,
    badge: 'New'
  }
];

// Quick actions for agents
const agentQuickActions: AgentQuickAction[] = [
  {
    id: 'code-review',
    label: 'Code Review',
    icon: <Code className="h-4 w-4" />,
    description: 'Analyze code quality and security',
    color: 'bg-blue-500'
  },
  {
    id: 'deploy',
    label: 'Deploy',
    icon: <Cloud className="h-4 w-4" />,
    description: 'Deploy to staging/production',
    color: 'bg-green-500'
  },
  {
    id: 'security-scan',
    label: 'Security Scan',
    icon: <Shield className="h-4 w-4" />,
    description: 'Run security vulnerability scan',
    color: 'bg-red-500'
  },
  {
    id: 'generate-docs',
    label: 'Generate Docs',
    icon: <FileText className="h-4 w-4" />,
    description: 'Auto-generate documentation',
    color: 'bg-purple-500'
  }
];

// Sidebar item component
const SidebarItemComponent: React.FC<{
  item: SidebarItem;
  isCollapsed: boolean;
  level?: number;
  onItemClick?: (itemId: string) => void;
}> = ({ item, isCollapsed, level = 0, onItemClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasChildren = item.children && item.children.length > 0;

  const handleClick = () => {
    if (hasChildren) {
      setIsExpanded(!isExpanded);
    } else {
      onItemClick?.(item.id);
    }
  };

  const ItemContent = (
    <Button
      variant={item.isActive ? "secondary" : "ghost"}
      className={cn(
        "w-full justify-start gap-2 h-9",
        level > 0 && "ml-4",
        isCollapsed && "px-2"
      )}
      onClick={handleClick}
    >
      {item.icon}
      {!isCollapsed && (
        <>
          <span className="flex-1 text-left">{item.label}</span>
          {item.badge && (
            <Badge variant="secondary" className="text-xs">
              {item.badge}
            </Badge>
          )}
          {hasChildren && (
            <ChevronRight className={cn(
              "h-4 w-4 transition-transform",
              isExpanded && "rotate-90"
            )} />
          )}
        </>
      )}
    </Button>
  );

  if (isCollapsed) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            {ItemContent}
          </TooltipTrigger>
          <TooltipContent side="right">
            <p>{item.label}</p>
            {item.badge && <Badge className="ml-2">{item.badge}</Badge>}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <div>
      {ItemContent}
      {hasChildren && isExpanded && !isCollapsed && (
        <div className="mt-1 space-y-1">
          {item.children!.map((child) => (
            <SidebarItemComponent
              key={child.id}
              item={child}
              isCollapsed={isCollapsed}
              level={level + 1}
              onItemClick={onItemClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Quick action component
const QuickActionComponent: React.FC<{
  action: AgentQuickAction;
  isCollapsed: boolean;
  onActionClick: (actionId: string) => void;
}> = ({ action, isCollapsed, onActionClick }) => {
  if (isCollapsed) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="sm" className="w-full p-2">
              <div className={cn("w-2 h-2 rounded-full mr-2", action.color)} />
              {action.icon}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">
            <div>
              <p className="font-medium">{action.label}</p>
              <p className="text-xs text-muted-foreground">{action.description}</p>
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <Button variant="outline" className="w-full justify-start gap-3 h-auto p-3" onClick={() => onActionClick(action.id)}>

      <div className={cn("w-3 h-3 rounded-full", action.color)} />
      <div className="flex-1 text-left">
        <div className="font-medium text-sm">{action.label}</div>
        <div className="text-xs text-muted-foreground">{action.description}</div>
      </div>
    </Button>
  );
};

// Main enhanced sidebar component
export const EnhancedSidebar: React.FC<EnhancedSidebarProps> = ({
  isCollapsed = false,
  onToggleCollapse,
  activeItem,
  onItemClick,
  className
}) => {
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Auto-collapse on mobile
  const shouldCollapse = isCollapsed || isMobile;

  const handleQuickActionClick = (actionId: string) => {
    console.log(`Quick Action clicked: ${actionId}`);
    // Future: navigate to a specific page or trigger an agent action
    // For example: navigate(`/quick-actions/${actionId}`);
  };

  return (
    <div className={cn(
      "flex flex-col h-full bg-background border-r transition-all duration-300",
      shouldCollapse ? "w-16" : "w-72",
      "md:relative absolute md:translate-x-0",
      isMobile && !isCollapsed && "z-50 shadow-lg",
      className
    )}>

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {!shouldCollapse && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h2 className="font-semibold text-sm">AI Assistant</h2>
              <p className="text-xs text-muted-foreground">Project Manager</p>
            </div>
          </div>
        )}

        {onToggleCollapse && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleCollapse}
            className={cn("shrink-0", shouldCollapse && "w-full")}
          >
            {shouldCollapse ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        )}
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4 max-h-full overflow-y-auto min-h-0">
        <div className="space-y-1">
          {navigationItems.map((item) => (
            <SidebarItemComponent
              key={item.id}
              item={{...item, isActive: item.id === activeItem}}
              isCollapsed={shouldCollapse}
              onItemClick={onItemClick}
            />
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mt-6">
          <Separator className="mb-4" />
          {!shouldCollapse && (
            <div className="px-2 mb-3">
              <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Quick Actions
              </h3>
            </div>
          )}
          <div className="space-y-2">
            {agentQuickActions.map((action) => (
              <QuickActionComponent
                key={action.id}
                action={action}
                isCollapsed={shouldCollapse}
                onActionClick={handleQuickActionClick}
              />
            ))}
          </div>
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t p-3">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className={cn("flex-1", shouldCollapse && "px-2")}
            onClick={() => onItemClick?.('notifications')}
          >
            <Bell className="h-4 w-4" />
            {!shouldCollapse && <span className="ml-2">Notifications</span>}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            className={cn(shouldCollapse && "px-2")}
            onClick={() => onItemClick?.('settings')}
          >
            <Settings className="h-4 w-4" />
            {!shouldCollapse && <span className="ml-2">Settings</span>}
          </Button>
        </div>
      </div>
    </div>
  );
};
