import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ResponsiveGrid } from '@/components/ui/horizontal-scroll';
import {
  Plus,
  Code,
  Database,
  Cloud,
  Settings,
  CheckCircle,
  AlertCircle,
  ExternalLink
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'connected' | 'disconnected' | 'error';
  category: 'development' | 'infrastructure' | 'analytics';
  lastSync?: Date;
  path: string;
}

const integrations: Integration[] = [
  {
    id: 'github',
    name: 'GitHub',
    description: 'Repository management, code analysis, and project import',
    icon: <Code className="h-6 w-6" />,
    status: 'connected',
    category: 'development',
    lastSync: new Date(Date.now() - 5 * 60 * 1000),
    path: '/integrations/github'
  },
  {
    id: 'database',
    name: 'Database',
    description: 'Database connections and data management',
    icon: <Database className="h-6 w-6" />,
    status: 'disconnected',
    category: 'infrastructure',
    path: '/integrations/database'
  },
  {
    id: 'cloud',
    name: 'Cloud Services',
    description: 'AWS, Azure, and GCP integrations',
    icon: <Cloud className="h-6 w-6" />,
    status: 'error',
    category: 'infrastructure',
    lastSync: new Date(Date.now() - 2 * 60 * 60 * 1000),
    path: '/integrations/cloud'
  }
];

const statusColors = {
  connected: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  disconnected: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
};

const statusIcons = {
  connected: <CheckCircle className="h-4 w-4" />,
  disconnected: <AlertCircle className="h-4 w-4" />,
  error: <AlertCircle className="h-4 w-4" />
};

export const IntegrationsPage: React.FC = () => {
  const navigate = useNavigate();

  const handleIntegrationClick = (integration: Integration) => {
    navigate(integration.path);
  };

  const connectedCount = integrations.filter(i => i.status === 'connected').length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Integrations</h1>
          <p className="text-muted-foreground">
            Connect and manage external services and tools
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Integration
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-muted-foreground">Connected</p>
                <p className="text-2xl font-bold">{connectedCount}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-muted-foreground">Available</p>
                <p className="text-2xl font-bold">{integrations.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-muted-foreground">Issues</p>
                <p className="text-2xl font-bold">
                  {integrations.filter(i => i.status === 'error').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Integrations grid */}
      <ResponsiveGrid minItemWidth={350} gap={24}>
        {integrations.map((integration) => (
          <Card
            key={integration.id}
            className="hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => handleIntegrationClick(integration)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    {integration.icon}
                  </div>
                  <div>
                    <CardTitle className="text-lg">{integration.name}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={statusColors[integration.status]}>
                        {statusIcons[integration.status]}
                        <span className="ml-1 capitalize">{integration.status}</span>
                      </Badge>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription className="text-sm mt-2">
                {integration.description}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {integration.lastSync && (
                <div className="text-sm text-muted-foreground">
                  Last sync: {integration.lastSync.toLocaleTimeString()}
                </div>
              )}

              <div className="flex justify-between items-center">
                <Badge variant="outline" className="text-xs">
                  {integration.category}
                </Badge>
                <Button size="sm" variant="outline">
                  {integration.status === 'connected' ? 'Configure' : 'Connect'}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </ResponsiveGrid>
    </div>
  );
};
