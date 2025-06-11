import React, { useState, useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  Send,
  Bot,
  User,
  Loader2,
  Copy,
  CopyCheck,
  Square,
  Search,
  BarChart3,
  FileText,
  ExternalLink,
  Star,
  Clock,
  CheckCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

// Types for specialized chat functionality
interface Citation {
  source_id: number;
  title: string;
  url: string;
  snippet: string;
  relevance_score: number;
}

interface SpecializedActivity {
  id: string;
  type: 'research' | 'analysis' | 'synthesis';
  status: 'active' | 'completed' | 'error';
  message: string;
  timestamp: Date;
  duration?: number;
}

interface SpecializedMessage {
  id?: string;
  type: string;
  content: string;
  citations?: Citation[];
  activities?: SpecializedActivity[];
  isStreaming?: boolean;
  qualityScore?: number;
  executionMetrics?: {
    total_agents_used: number;
    research_iterations: number;
    total_execution_time: number;
  };
}

interface SpecializedChatInterfaceProps {
  messages: SpecializedMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onStopGeneration?: () => void;
  onFeedback?: (messageId: string, rating: number, comment?: string) => void;
  className?: string;
}

// Agent activity indicator component
const AgentActivityIndicator: React.FC<{ activities: SpecializedActivity[] }> = ({ activities }) => {
  if (!activities || activities.length === 0) return null;

  const getAgentIcon = (type: SpecializedActivity['type']) => {
    switch (type) {
      case 'research':
        return <Search size={14} className="text-blue-500" />;
      case 'analysis':
        return <BarChart3 size={14} className="text-green-500" />;
      case 'synthesis':
        return <FileText size={14} className="text-purple-500" />;
    }
  };

  const getStatusIcon = (status: SpecializedActivity['status']) => {
    switch (status) {
      case 'active':
        return <Loader2 size={12} className="animate-spin" />;
      case 'completed':
        return <CheckCircle size={12} className="text-green-600" />;
      case 'error':
        return <div className="w-3 h-3 rounded-full bg-red-500" />;
    }
  };

  return (
    <Card className="mt-3 bg-muted/30">
      <CardContent className="p-3">
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            Agent Workflow
          </h4>
          <div className="space-y-2">
            {activities.map((activity) => (
              <div key={activity.id} className="flex items-center gap-3 text-sm">
                <div className="flex items-center gap-1">
                  {getAgentIcon(activity.type)}
                  {getStatusIcon(activity.status)}
                </div>
                <span className="flex-1">{activity.message}</span>
                {activity.duration && (
                  <span className="text-xs text-muted-foreground">
                    {activity.duration}ms
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Citations display component
const CitationsDisplay: React.FC<{ citations: Citation[] }> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  return (
    <Card className="mt-3 bg-blue-50/50 dark:bg-blue-950/20">
      <CardContent className="p-3">
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-blue-700 dark:text-blue-300 flex items-center gap-2">
            <ExternalLink size={14} />
            Sources & Citations ({citations.length})
          </h4>
          <div className="space-y-2">
            {citations.slice(0, 5).map((citation) => (
              <div key={citation.source_id} className="flex items-start gap-2 text-xs">
                <Badge variant="outline" className="text-xs shrink-0">
                  {citation.source_id}
                </Badge>
                <div className="flex-1 space-y-1">
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-blue-600 dark:text-blue-400 hover:underline line-clamp-1"
                  >
                    {citation.title}
                  </a>
                  <p className="text-muted-foreground line-clamp-2">
                    {citation.snippet}
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      <Star size={10} className="text-yellow-500" />
                      <span className="text-muted-foreground">
                        {citation.relevance_score.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {citations.length > 5 && (
              <div className="text-xs text-muted-foreground text-center pt-1">
                +{citations.length - 5} more sources
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Quality metrics display
const QualityMetricsDisplay: React.FC<{
  qualityScore?: number;
  executionMetrics?: SpecializedMessage['executionMetrics']
}> = ({ qualityScore, executionMetrics }) => {
  if (!qualityScore && !executionMetrics) return null;

  return (
    <Card className="mt-3 bg-green-50/50 dark:bg-green-950/20">
      <CardContent className="p-3">
        <div className="grid grid-cols-2 gap-4 text-xs">
          {qualityScore && (
            <div className="space-y-1">
              <div className="flex items-center gap-1 text-green-700 dark:text-green-300">
                <Star size={12} />
                <span className="font-medium">Quality Score</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span>{qualityScore.toFixed(2)}/5.0</span>
                  <span className="text-muted-foreground">
                    {qualityScore >= 4 ? 'Excellent' : qualityScore >= 3 ? 'Good' : 'Fair'}
                  </span>
                </div>
                <Progress value={(qualityScore / 5) * 100} className="h-1" />
              </div>
            </div>
          )}

          {executionMetrics && (
            <div className="space-y-1">
              <div className="flex items-center gap-1 text-green-700 dark:text-green-300">
                <Clock size={12} />
                <span className="font-medium">Execution</span>
              </div>
              <div className="space-y-1 text-muted-foreground">
                <div>Agents: {executionMetrics.total_agents_used}/3</div>
                <div>Iterations: {executionMetrics.research_iterations}</div>
                <div>Time: {executionMetrics.total_execution_time?.toFixed(1)}s</div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Enhanced message bubble for specialized system
const SpecializedMessageBubble: React.FC<{
  message: SpecializedMessage;
  onCopy: (text: string) => void;
  onFeedback?: (rating: number, comment?: string) => void;
  copiedId: string | null;
}> = ({ message, onCopy, onFeedback, copiedId }) => {
  const isHuman = message.type === 'human';
  const isCopied = copiedId === message.id;
  const [showFeedback, setShowFeedback] = useState(false);

  return (
    <div className={cn(
      "flex gap-3 group",
      isHuman ? "justify-end" : "justify-start"
    )}>
      {!isHuman && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
          <Bot size={16} className="text-primary" />
        </div>
      )}

      <div className={cn(
        "max-w-[85%] space-y-2",
        isHuman ? "order-first" : ""
      )}>
        {/* Specialized agent badge for AI messages */}
        {!isHuman && (
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs bg-gradient-to-r from-blue-500 to-purple-500 text-white">
              Real Specialized Agents
            </Badge>
            {message.isStreaming && (
              <Badge variant="outline" className="text-xs animate-pulse">
                Processing...
              </Badge>
            )}
          </div>
        )}

        {/* Message content */}
        <Card className={cn(
          "relative",
          isHuman
            ? "bg-primary text-primary-foreground"
            : "bg-card border"
        )}>
          <CardContent className="p-4">
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>

            {/* Copy button */}
            <Button
              variant="ghost"
              size="sm"
              className={cn(
                "absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity",
                isHuman ? "text-primary-foreground/70 hover:text-primary-foreground" : ""
              )}
              onClick={() => onCopy(message.content)}
            >
              {isCopied ? <CopyCheck size={14} /> : <Copy size={14} />}
            </Button>
          </CardContent>
        </Card>

        {/* Agent activities */}
        {!isHuman && <AgentActivityIndicator activities={message.activities || []} />}

        {/* Citations */}
        {!isHuman && <CitationsDisplay citations={message.citations || []} />}

        {/* Quality metrics */}
        {!isHuman && (
          <QualityMetricsDisplay
            qualityScore={message.qualityScore}
            executionMetrics={message.executionMetrics}
          />
        )}

        {/* Feedback section for AI messages */}
        {!isHuman && onFeedback && !message.isStreaming && (
          <div className="flex items-center gap-2 pt-2">
            <span className="text-xs text-muted-foreground">Rate this response:</span>
            {[1, 2, 3, 4, 5].map((rating) => (
              <Button
                key={rating}
                variant="ghost"
                size="sm"
                className="p-1 h-auto"
                onClick={() => onFeedback(rating)}
              >
                <Star size={14} className="text-yellow-500" />
              </Button>
            ))}
          </div>
        )}
      </div>

      {isHuman && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
          <User size={16} className="text-muted-foreground" />
        </div>
      )}
    </div>
  );
};

// Main specialized chat interface component
export const SpecializedChatInterface: React.FC<SpecializedChatInterfaceProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onStopGeneration,
  onFeedback,
  className
}) => {
  const [inputValue, setInputValue] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(messageId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={cn("flex flex-col h-full min-h-0", className)}>
      {/* Messages area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="p-4">
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map((message, index) => (
                <SpecializedMessageBubble
                  key={message.id || `msg-${index}`}
                  message={message}
                  onCopy={(text) => handleCopy(text, message.id || `msg-${index}`)}
                  onFeedback={onFeedback ? (rating, comment) =>
                    onFeedback(message.id || `msg-${index}`, rating, comment) : undefined}
                  copiedId={copiedId}
                />
              ))}

              {/* Loading indicator with agent workflow */}
              {isLoading && (
                <div className="flex flex-col items-center gap-3 text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Loader2 size={16} className="animate-spin" />
                    <span className="text-sm">Real specialized agents are working...</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-1">
                      <Search size={12} className="text-blue-500" />
                      <span>Research</span>
                    </div>
                    <div className="w-2 h-0.5 bg-muted-foreground/30" />
                    <div className="flex items-center gap-1">
                      <BarChart3 size={12} className="text-green-500" />
                      <span>Analysis</span>
                    </div>
                    <div className="w-2 h-0.5 bg-muted-foreground/30" />
                    <div className="flex items-center gap-1">
                      <FileText size={12} className="text-purple-500" />
                      <span>Synthesis</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Invisible element for auto-scroll */}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </ScrollArea>
      </div>

      {/* Input area */}
      <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="p-4 max-w-4xl mx-auto">
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your specialized AI agents..."
              disabled={isLoading}
              className="flex-1"
            />

            {isLoading && onStopGeneration ? (
              <Button
                variant="outline"
                size="icon"
                onClick={onStopGeneration}
                className="shrink-0"
              >
                <Square size={16} />
              </Button>
            ) : (
              <Button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                size="icon"
                className="shrink-0"
              >
                <Send size={16} />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
