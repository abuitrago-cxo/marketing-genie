import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Save, 
  TestTube, 
  Eye, 
  Shield, 
  Settings, 
  AlertCircle,
  CheckCircle,
  Loader2
} from 'lucide-react';

interface MCPServer {
  id?: number;
  name: string;
  base_url: string;
  description?: string;
  enabled: boolean;
  auth_config?: {
    auth_type: 'none' | 'api_key' | 'bearer_token' | 'basic_auth';
    api_key?: string;
    api_key_header?: string;
    bearer_token?: string;
    username?: string;
    password?: string;
  };
  health_check_interval?: number;
  max_retries?: number;
  timeout_seconds?: number;
}

interface ServerConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  server?: MCPServer | null;
  onSave: (server: MCPServer) => Promise<void>;
}

const ServerConfigDialog: React.FC<ServerConfigDialogProps> = ({
  open,
  onOpenChange,
  server,
  onSave
}) => {
  const [formData, setFormData] = useState<MCPServer>({
    name: '',
    base_url: '',
    description: '',
    enabled: true,
    auth_config: {
      auth_type: 'none',
      api_key: '',
      api_key_header: 'X-API-Key',
      bearer_token: '',
      username: '',
      password: ''
    },
    health_check_interval: 300,
    max_retries: 3,
    timeout_seconds: 30.0
  });

  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    status: 'success' | 'failed' | 'error';
    message: string;
    tools_discovered?: number;
  } | null>(null);
  const [discovering, setDiscovering] = useState(false);
  const [discoveredTools, setDiscoveredTools] = useState<any[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (server) {
      setFormData({
        ...server,
        auth_config: server.auth_config || {
          auth_type: 'none',
          api_key: '',
          api_key_header: 'X-API-Key',
          bearer_token: '',
          username: '',
          password: ''
        }
      });
    } else {
      // Reset form for new server
      setFormData({
        name: '',
        base_url: '',
        description: '',
        enabled: true,
        auth_config: {
          auth_type: 'none',
          api_key: '',
          api_key_header: 'X-API-Key',
          bearer_token: '',
          username: '',
          password: ''
        },
        health_check_interval: 300,
        max_retries: 3,
        timeout_seconds: 30.0
      });
    }
    setTestResult(null);
    setDiscoveredTools([]);
  }, [server, open]);

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAuthConfigChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      auth_config: {
        ...prev.auth_config!,
        [field]: value
      }
    }));
  };

  const handleTestConnection = async () => {
    if (!formData.base_url) {
      setTestResult({
        status: 'error',
        message: 'Please enter a server URL first'
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      // For new servers, we need to create a temporary server to test
      if (!server?.id) {
        // Test without creating - this would need a special endpoint
        setTestResult({
          status: 'error',
          message: 'Save the server first to test connection'
        });
        return;
      }

      const response = await fetch(`/api/mcp/registry/servers/${server.id}/test-connection`, {
        method: 'POST'
      });
      
      const result = await response.json();
      setTestResult(result);
    } catch (error) {
      setTestResult({
        status: 'error',
        message: 'Failed to test connection'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleDiscoverTools = async () => {
    if (!server?.id) {
      alert('Save the server first to discover tools');
      return;
    }

    setDiscovering(true);
    try {
      const response = await fetch(`/api/mcp/registry/servers/${server.id}/discover-tools`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        setDiscoveredTools(result.tools);
      } else {
        alert('Failed to discover tools');
      }
    } catch (error) {
      alert('Failed to discover tools');
    } finally {
      setDiscovering(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(formData);
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to save server:', error);
    } finally {
      setSaving(false);
    }
  };

  const renderAuthConfig = () => {
    const authType = formData.auth_config?.auth_type || 'none';

    return (
      <div className="space-y-4">
        <div>
          <Label htmlFor="auth_type">Authentication Type</Label>
          <Select 
            value={authType} 
            onValueChange={(value) => handleAuthConfigChange('auth_type', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">None</SelectItem>
              <SelectItem value="api_key">API Key</SelectItem>
              <SelectItem value="bearer_token">Bearer Token</SelectItem>
              <SelectItem value="basic_auth">Basic Authentication</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {authType === 'api_key' && (
          <>
            <div>
              <Label htmlFor="api_key">API Key</Label>
              <Input
                id="api_key"
                type="password"
                value={formData.auth_config?.api_key || ''}
                onChange={(e) => handleAuthConfigChange('api_key', e.target.value)}
                placeholder="Enter your API key"
              />
            </div>
            <div>
              <Label htmlFor="api_key_header">API Key Header</Label>
              <Input
                id="api_key_header"
                value={formData.auth_config?.api_key_header || 'X-API-Key'}
                onChange={(e) => handleAuthConfigChange('api_key_header', e.target.value)}
                placeholder="X-API-Key"
              />
            </div>
          </>
        )}

        {authType === 'bearer_token' && (
          <div>
            <Label htmlFor="bearer_token">Bearer Token</Label>
            <Input
              id="bearer_token"
              type="password"
              value={formData.auth_config?.bearer_token || ''}
              onChange={(e) => handleAuthConfigChange('bearer_token', e.target.value)}
              placeholder="Enter your bearer token"
            />
          </div>
        )}

        {authType === 'basic_auth' && (
          <>
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                value={formData.auth_config?.username || ''}
                onChange={(e) => handleAuthConfigChange('username', e.target.value)}
                placeholder="Enter username"
              />
            </div>
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.auth_config?.password || ''}
                onChange={(e) => handleAuthConfigChange('password', e.target.value)}
                placeholder="Enter password"
              />
            </div>
          </>
        )}
      </div>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {server ? `Configure ${server.name}` : 'Add MCP Server'}
          </DialogTitle>
          <DialogDescription>
            Configure your MCP server connection, authentication, and settings.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="basic">Basic</TabsTrigger>
            <TabsTrigger value="auth">Authentication</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
            <TabsTrigger value="tools">Tools</TabsTrigger>
          </TabsList>

          <TabsContent value="basic" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Server Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="My MCP Server"
                />
              </div>
              <div>
                <Label htmlFor="base_url">Server URL</Label>
                <Input
                  id="base_url"
                  value={formData.base_url}
                  onChange={(e) => handleInputChange('base_url', e.target.value)}
                  placeholder="https://api.example.com"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description || ''}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe what this server provides..."
                rows={3}
              />
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="enabled"
                checked={formData.enabled}
                onCheckedChange={(checked) => handleInputChange('enabled', checked)}
              />
              <Label htmlFor="enabled">Enable this server</Label>
            </div>

            {/* Test Connection */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Connection Test</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleTestConnection}
                    disabled={testing || !formData.base_url}
                  >
                    {testing ? (
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <TestTube className="w-4 h-4 mr-1" />
                    )}
                    Test Connection
                  </Button>
                </div>
                
                {testResult && (
                  <Alert className={`mt-2 ${testResult.status === 'success' ? 'border-green-200' : 'border-red-200'}`}>
                    {testResult.status === 'success' ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    )}
                    <AlertDescription>
                      {testResult.message}
                      {testResult.tools_discovered !== undefined && (
                        <span className="block mt-1 text-sm">
                          Discovered {testResult.tools_discovered} tools
                        </span>
                      )}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="auth" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="w-4 h-4 mr-2" />
                  Authentication Configuration
                </CardTitle>
                <CardDescription>
                  Configure how to authenticate with this MCP server
                </CardDescription>
              </CardHeader>
              <CardContent>
                {renderAuthConfig()}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="advanced" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Settings className="w-4 h-4 mr-2" />
                  Advanced Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="health_check_interval">Health Check Interval (seconds)</Label>
                    <Input
                      id="health_check_interval"
                      type="number"
                      min="60"
                      max="3600"
                      value={formData.health_check_interval || 300}
                      onChange={(e) => handleInputChange('health_check_interval', parseInt(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="max_retries">Max Retries</Label>
                    <Input
                      id="max_retries"
                      type="number"
                      min="1"
                      max="10"
                      value={formData.max_retries || 3}
                      onChange={(e) => handleInputChange('max_retries', parseInt(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label htmlFor="timeout_seconds">Timeout (seconds)</Label>
                    <Input
                      id="timeout_seconds"
                      type="number"
                      min="5"
                      max="120"
                      step="0.1"
                      value={formData.timeout_seconds || 30.0}
                      onChange={(e) => handleInputChange('timeout_seconds', parseFloat(e.target.value))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="tools" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Eye className="w-4 h-4 mr-2" />
                    Available Tools
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleDiscoverTools}
                    disabled={discovering || !server?.id}
                  >
                    {discovering ? (
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <Eye className="w-4 h-4 mr-1" />
                    )}
                    Discover Tools
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {discoveredTools.length > 0 ? (
                  <div className="space-y-2">
                    {discoveredTools.map((tool, index) => (
                      <div key={index} className="border rounded p-3">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{tool.name}</h4>
                          <Badge variant="outline">{tool.tool_id}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{tool.description}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-center py-4">
                    No tools discovered yet. Save the server and click "Discover Tools" to see available tools.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving || !formData.name || !formData.base_url}>
            {saving ? (
              <Loader2 className="w-4 h-4 mr-1 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-1" />
            )}
            {server ? 'Update Server' : 'Add Server'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ServerConfigDialog;
