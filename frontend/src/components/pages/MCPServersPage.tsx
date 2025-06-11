import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Plus,
  Server,
  Activity,
  Settings,
  Trash2,
  TestTube,
  Download,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  Eye,
  RefreshCw
} from 'lucide-react';

// Import our custom components
import ServerConfigDialog from '@/components/mcp/ServerConfigDialog';
import MCPMarketplace from '@/components/mcp/MCPMarketplace';

// Types based on our backend models
interface MCPServer {
  id: number;
  name: string;
  base_url: string;
  description?: string;
  enabled: boolean;
  last_checked_at?: string;
  last_known_status?: string;
  available_tools_json?: any;
  created_at: string;
  updated_at: string;
  installation_status?: string;
  health?: {
    status: string;
    last_check: string;
    response_time_ms?: number;
    error_message?: string;
    consecutive_failures: number;
  };
}

interface MCPAuthConfig {
  auth_type: 'none' | 'api_key' | 'bearer_token' | 'basic_auth';
  api_key?: string;
  api_key_header?: string;
  bearer_token?: string;
  username?: string;
  password?: string;
}

const MCPServersPage: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('installed');
  const [showConfigDialog, setShowConfigDialog] = useState(false);
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);

  useEffect(() => {
    fetchServers();
  }, []);

  const fetchServers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/mcp/registry/servers/');
      if (response.ok) {
        const data = await response.json();
        setServers(data);
      }
    } catch (error) {
      console.error('Failed to fetch MCP servers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveServer = async (serverData: any) => {
    try {
      const url = selectedServer
        ? `/api/mcp/registry/servers/${selectedServer.id}`
        : '/api/mcp/registry/servers/';

      const method = selectedServer ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(serverData),
      });

      if (response.ok) {
        await fetchServers(); // Refresh the list
        setSelectedServer(null);
      } else {
        throw new Error('Failed to save server');
      }
    } catch (error) {
      console.error('Failed to save server:', error);
      throw error;
    }
  };

  const handleEditServer = (server: MCPServer) => {
    setSelectedServer(server);
    setShowConfigDialog(true);
  };

  const handleAddServer = () => {
    setSelectedServer(null);
    setShowConfigDialog(true);
  };

  const getStatusBadge = (server: MCPServer) => {
    const status = server.health?.status || server.last_known_status || 'unknown';

    switch (status.toLowerCase()) {
      case 'healthy':
        return <Badge variant="default" className="bg-green-500"><CheckCircle className="w-3 h-3 mr-1" />Healthy</Badge>;
      case 'unhealthy':
        return <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Unhealthy</Badge>;
      case 'installing':
        return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />Installing</Badge>;
      case 'pending':
        return <Badge variant="outline"><Clock className="w-3 h-3 mr-1" />Pending</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  const handleTestConnection = async (serverId: number) => {
    try {
      const response = await fetch(`/api/mcp/registry/servers/${serverId}/test-connection`, {
        method: 'POST'
      });
      const result = await response.json();

      if (result.status === 'success') {
        alert(`Connection successful! Discovered ${result.tools_discovered} tools.`);
      } else {
        alert(`Connection failed: ${result.message}`);
      }

      // Refresh servers to update status
      fetchServers();
    } catch (error) {
      alert('Failed to test connection');
    }
  };

  const handleDiscoverTools = async (serverId: number) => {
    try {
      const response = await fetch(`/api/mcp/registry/servers/${serverId}/discover-tools`, {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Discovered ${result.tools.length} tools from ${result.server_name}`);
        fetchServers();
      } else {
        alert('Failed to discover tools');
      }
    } catch (error) {
      alert('Failed to discover tools');
    }
  };

  const ServerCard: React.FC<{ server: MCPServer }> = ({ server }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Server className="w-5 h-5 text-blue-500" />
            <CardTitle className="text-lg">{server.name}</CardTitle>
            {getStatusBadge(server)}
          </div>
          <div className="flex items-center space-x-1">
            <Switch checked={server.enabled} />
            <Button variant="ghost" size="sm" onClick={() => handleEditServer(server)}>
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>
        <CardDescription className="text-sm">
          {server.description || 'No description provided'}
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">URL:</span>
            <span className="font-mono text-xs">{server.base_url}</span>
          </div>
          {server.health?.response_time_ms && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Response Time:</span>
              <span>{server.health.response_time_ms.toFixed(0)}ms</span>
            </div>
          )}
          {server.available_tools_json?.tool_count && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Tools:</span>
              <span>{server.available_tools_json.tool_count} available</span>
            </div>
          )}
        </div>

        <div className="flex space-x-2 mt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleTestConnection(server.id)}
            className="flex-1"
          >
            <TestTube className="w-4 h-4 mr-1" />
            Test
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleDiscoverTools(server.id)}
            className="flex-1"
          >
            <Eye className="w-4 h-4 mr-1" />
            Discover
          </Button>
        </div>
      </CardContent>
    </Card>
  );

  const InstalledServers = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Installed Servers ({servers.length})</h3>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm" onClick={fetchServers}>
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </Button>
          <Button size="sm" onClick={handleAddServer}>
            <Plus className="w-4 h-4 mr-1" />
            Add Server
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : servers.length === 0 ? (
        <Card className="text-center py-8">
          <CardContent>
            <Server className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">No MCP Servers</h3>
            <p className="text-muted-foreground mb-4">
              Get started by adding your first MCP server or installing one from the marketplace.
            </p>
            <Button onClick={handleAddServer}>
              <Plus className="w-4 h-4 mr-1" />
              Add Your First Server
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {servers.map(server => (
            <ServerCard key={server.id} server={server} />
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center justify-between p-4">
          <div>
            <h1 className="text-2xl font-bold">MCP Servers</h1>
            <p className="text-muted-foreground">Manage Model Context Protocol servers and tools</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              <Activity className="w-3 h-3 mr-1" />
              {servers.filter(s => s.enabled).length} Active
            </Badge>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="installed">Installed</TabsTrigger>
            <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
            <TabsTrigger value="remote">Remote Servers</TabsTrigger>
          </TabsList>

          <TabsContent value="installed" className="mt-4">
            <InstalledServers />
          </TabsContent>

          <TabsContent value="marketplace" className="mt-4">
            <MCPMarketplace
            />
          </TabsContent>

          <TabsContent value="remote" className="mt-4">
            <div className="text-center py-8">
              <Zap className="w-12 h-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold mb-2">Remote Servers</h3>
              <p className="text-muted-foreground">
                Connect to external MCP servers running on remote hosts.
              </p>
              <p className="text-sm text-muted-foreground mt-2">Coming soon...</p>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Server Configuration Dialog */}
      <ServerConfigDialog
        open={showConfigDialog}
        onOpenChange={setShowConfigDialog}
        server={selectedServer}
        onSave={handleSaveServer}
      />
    </div>
  );
};

export default MCPServersPage;
