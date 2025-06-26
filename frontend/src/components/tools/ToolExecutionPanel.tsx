import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Play, 
  Square, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Settings,
  FileText,
  Globe,
  FolderOpen
} from 'lucide-react';
import { getApiBaseUrl } from '@/config/api';
import ErrorState from '@/components/ui/ErrorState';

interface ToolCapability {
  name: string;
  description: string;
  parameters: Record<string, any>;
  examples: string[];
  category: string;
}

interface Tool {
  name: string;
  description: string;
  category: string;
  status: string;
  capabilities: ToolCapability[];
  usage_count: number;
  last_used?: string;
}

interface ToolResult {
  success: boolean;
  tool_name: string;
  action: string;
  result: any;
  execution_time: number;
  timestamp: string;
}

interface ToolExecutionPanelProps {
  className?: string;
}

const ToolExecutionPanel: React.FC<ToolExecutionPanelProps> = ({ className }) => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [toolResults, setToolResults] = useState<ToolResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTools();
  }, []);

  const fetchTools = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/enhanced/tools/registry`);
      const data = await response.json();
      
      if (data.success) {
        const toolsArray = Object.values(data.data.tools) as Tool[];
        setTools(toolsArray);
      }
    } catch (error) {
      console.error('Failed to fetch tools:', error);
      setError('Failed to fetch tools');
    }
  };

  const executeToolAction = async (toolName: string, action: string, parameters: Record<string, any>) => {
    setLoading(true);
    try {
      const response = await fetch(`${getApiBaseUrl()}/enhanced/tools/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool_name: toolName,
          action: action,
          parameters: parameters
        })
      });

      const result = await response.json();
      
      const toolResult: ToolResult = {
        ...result,
        timestamp: new Date().toISOString()
      };

      setToolResults(prev => [toolResult, ...prev]);
      
    } catch (error) {
      console.error('Tool execution failed:', error);
      setError('Tool execution failed');
    } finally {
      setLoading(false);
    }
  };

  const getToolIcon = (category: string) => {
    switch (category) {
      case 'file_system':
        return <FolderOpen size={16} />;
      case 'project_management':
        return <Settings size={16} />;
      case 'web':
        return <Globe size={16} />;
      default:
        return <FileText size={16} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'bg-gray-500';
      case 'running':
        return 'bg-blue-500';
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (error) {
    return <ErrorState message={error} onRetry={fetchTools} />;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings size={20} />
            Tool Execution Panel
          </CardTitle>
          <CardDescription>
            Execute and monitor agent tools for file operations, project management, and web tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="tools" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="tools">Available Tools</TabsTrigger>
              <TabsTrigger value="execution">Quick Execute</TabsTrigger>
              <TabsTrigger value="results">Execution History</TabsTrigger>
            </TabsList>

            <TabsContent value="tools" className="space-y-4">
              <ScrollArea className="h-[400px]">
                <div className="space-y-3">
                  {tools.map((tool) => (
                    <Card key={tool.name} className="cursor-pointer hover:bg-accent/50" 
                          onClick={() => setSelectedTool(tool)}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            {getToolIcon(tool.category)}
                            <div>
                              <h4 className="font-medium">{tool.name}</h4>
                              <p className="text-sm text-muted-foreground">{tool.description}</p>
                              <div className="flex items-center gap-2 mt-2">
                                <Badge variant="outline">{tool.category}</Badge>
                                <Badge variant="outline">{tool.capabilities.length} capabilities</Badge>
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${getStatusColor(tool.status)}`} />
                            <span className="text-xs text-muted-foreground">{tool.status}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="execution" className="space-y-4">
              {selectedTool ? (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {getToolIcon(selectedTool.category)}
                      {selectedTool.name}
                    </CardTitle>
                    <CardDescription>{selectedTool.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      {selectedTool.capabilities.map((capability) => (
                        <Card key={capability.name} className="border-dashed">
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <h5 className="font-medium">{capability.name}</h5>
                                <p className="text-sm text-muted-foreground">{capability.description}</p>
                                {capability.examples.length > 0 && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    Example: {capability.examples[0]}
                                  </p>
                                )}
                              </div>
                              <Button
                                size="sm"
                                onClick={() => executeToolAction(selectedTool.name, capability.name, {})}
                                disabled={loading}
                              >
                                {loading ? <Clock size={14} /> : <Play size={14} />}
                                Execute
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="p-8 text-center">
                    <p className="text-muted-foreground">Select a tool from the "Available Tools" tab to execute its capabilities</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="results" className="space-y-4">
              <ScrollArea className="h-[400px]">
                <div className="space-y-3">
                  {toolResults.map((result, index) => (
                    <Card key={index}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            {result.success ? (
                              <CheckCircle size={16} className="text-green-500 mt-0.5" />
                            ) : (
                              <XCircle size={16} className="text-red-500 mt-0.5" />
                            )}
                            <div>
                              <h5 className="font-medium">{result.tool_name}.{result.action}</h5>
                              <p className="text-sm text-muted-foreground">
                                {result.success ? 'Executed successfully' : 'Execution failed'}
                              </p>
                              <div className="flex items-center gap-2 mt-1">
                                <Badge variant={result.success ? 'default' : 'destructive'}>
                                  {result.success ? 'Success' : 'Failed'}
                                </Badge>
                                <span className="text-xs text-muted-foreground">
                                  {result.execution_time.toFixed(2)}s
                                </span>
                              </div>
                            </div>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {new Date(result.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {toolResults.length === 0 && (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <p className="text-muted-foreground">No tool executions yet</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default ToolExecutionPanel;
