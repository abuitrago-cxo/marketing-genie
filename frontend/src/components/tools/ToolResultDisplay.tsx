import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  FileText,
  FolderOpen,
  Globe,
  Settings,
  ChevronDown,
  ChevronRight,
  Copy
} from 'lucide-react';
import { useState } from 'react';

interface ToolResult {
  tool_name: string;
  action: string;
  success: boolean;
  result: {
    success: boolean;
    data?: any;
    message?: string;
    error?: string;
    execution_time: number;
    tool_name: string;
    tool_id: string;
    metadata?: any;
  };
}

interface ToolResultDisplayProps {
  toolResults: ToolResult[];
  className?: string;
}

const ToolResultDisplay: React.FC<ToolResultDisplayProps> = ({ toolResults, className }) => {
  const [expandedResults, setExpandedResults] = useState<Set<number>>(new Set());
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedResults(newExpanded);
  };

  const copyToClipboard = async (content: string, index: number) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const getToolIcon = (toolName: string) => {
    switch (toolName) {
      case 'file_operations':
        return <FolderOpen size={16} className="text-blue-500" />;
      case 'project_management':
        return <Settings size={16} className="text-purple-500" />;
      case 'web_operations':
        return <Globe size={16} className="text-green-500" />;
      default:
        return <FileText size={16} className="text-gray-500" />;
    }
  };

  const formatData = (data: any): string => {
    if (typeof data === 'string') return data;
    if (typeof data === 'object') {
      return JSON.stringify(data, null, 2);
    }
    return String(data);
  };

  const renderDataPreview = (data: any): React.ReactNode => {
    if (!data) return null;

    if (typeof data === 'string') {
      return (
        <div className="bg-muted p-3 rounded-md">
          <pre className="text-sm whitespace-pre-wrap">{data.length > 200 ? data.substring(0, 200) + '...' : data}</pre>
        </div>
      );
    }

    if (typeof data === 'object') {
      // Handle specific data types
      if (data.content) {
        return (
          <div className="space-y-2">
            <div className="bg-muted p-3 rounded-md">
              <pre className="text-sm whitespace-pre-wrap">
                {data.content.length > 200 ? data.content.substring(0, 200) + '...' : data.content}
              </pre>
            </div>
            {data.file_path && (
              <div className="text-xs text-muted-foreground">
                File: {data.file_path}
              </div>
            )}
          </div>
        );
      }

      if (data.tasks && Array.isArray(data.tasks)) {
        return (
          <div className="space-y-2">
            <div className="text-sm font-medium">Tasks ({data.total_count || data.tasks.length})</div>
            <div className="space-y-1">
              {data.tasks.slice(0, 3).map((task: any, idx: number) => (
                <div key={idx} className="bg-muted p-2 rounded text-sm">
                  <div className="font-medium">{task.title}</div>
                  <div className="text-muted-foreground text-xs">{task.status} • {task.priority}</div>
                </div>
              ))}
              {data.tasks.length > 3 && (
                <div className="text-xs text-muted-foreground">
                  +{data.tasks.length - 3} more tasks
                </div>
              )}
            </div>
          </div>
        );
      }

      if (data.analysis) {
        return (
          <div className="space-y-2">
            <div className="text-sm font-medium">Project Analysis</div>
            <div className="bg-muted p-3 rounded-md space-y-2">
              {data.analysis.completion_rate !== undefined && (
                <div className="flex justify-between text-sm">
                  <span>Completion Rate:</span>
                  <span className="font-medium">{data.analysis.completion_rate}%</span>
                </div>
              )}
              {data.analysis.total_tasks !== undefined && (
                <div className="flex justify-between text-sm">
                  <span>Total Tasks:</span>
                  <span className="font-medium">{data.analysis.total_tasks}</span>
                </div>
              )}
            </div>
          </div>
        );
      }

      // Generic object display
      const keys = Object.keys(data).slice(0, 3);
      return (
        <div className="bg-muted p-3 rounded-md">
          <div className="text-sm space-y-1">
            {keys.map(key => (
              <div key={key} className="flex justify-between">
                <span className="text-muted-foreground">{key}:</span>
                <span className="font-mono text-xs">
                  {String(data[key]).length > 30 
                    ? String(data[key]).substring(0, 30) + '...' 
                    : String(data[key])
                  }
                </span>
              </div>
            ))}
            {Object.keys(data).length > 3 && (
              <div className="text-xs text-muted-foreground">
                +{Object.keys(data).length - 3} more fields
              </div>
            )}
          </div>
        </div>
      );
    }

    return <div className="text-sm text-muted-foreground">{String(data)}</div>;
  };

  if (!toolResults || toolResults.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
        <Settings size={14} />
        Tool Execution Results
      </div>
      
      {toolResults.map((toolResult, index) => {
        const isExpanded = expandedResults.has(index);
        const result = toolResult.result;
        
        return (
          <Card key={index} className="border-l-4 border-l-blue-500">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getToolIcon(toolResult.tool_name)}
                  <CardTitle className="text-sm">
                    {toolResult.tool_name}.{toolResult.action}
                  </CardTitle>
                  {result.success ? (
                    <CheckCircle size={14} className="text-green-500" />
                  ) : (
                    <XCircle size={14} className="text-red-500" />
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={result.success ? 'default' : 'destructive'} className="text-xs">
                    {result.success ? 'Success' : 'Failed'}
                  </Badge>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock size={12} />
                    {result.execution_time?.toFixed(2)}s
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleExpanded(index)}
                    className="h-6 w-6 p-0"
                  >
                    {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="pt-0">
              {/* Always show message/error */}
              <div className="mb-3">
                {result.success && result.message && (
                  <div className="text-sm text-green-700 bg-green-50 p-2 rounded">
                    {result.message}
                  </div>
                )}
                {!result.success && result.error && (
                  <div className="text-sm text-red-700 bg-red-50 p-2 rounded">
                    {result.error}
                  </div>
                )}
              </div>

              {/* Show data preview even when collapsed */}
              {result.success && result.data && (
                <div className="space-y-2">
                  {!isExpanded && (
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Preview:</div>
                      {renderDataPreview(result.data)}
                    </div>
                  )}
                  
                  {isExpanded && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">Full Data:</div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(formatData(result.data), index)}
                          className="h-6 text-xs"
                        >
                          <Copy size={12} className="mr-1" />
                          {copiedIndex === index ? 'Copied!' : 'Copy'}
                        </Button>
                      </div>
                      <div className="bg-muted p-3 rounded-md max-h-60 overflow-auto">
                        <pre className="text-xs whitespace-pre-wrap">
                          {formatData(result.data)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default ToolResultDisplay;
