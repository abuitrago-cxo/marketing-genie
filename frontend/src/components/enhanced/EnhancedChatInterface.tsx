import React, { useState, useRef, useEffect } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  Send,
  Bot,
  User,
  Loader2,
  Copy,
  CopyCheck,
  Play,
  Square,
  Activity,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

// Types for enhanced chat functionality
interface AgentActivity {
  id: string;
  type: 'thinking' | 'searching' | 'analyzing' | 'executing' | 'completed' | 'error';
  message: string;
  timestamp: Date;
  duration?: number;
}

interface EnhancedMessage {
  id?: string;
  type: string; // Allow any string type to be flexible with LangGraph message types
  content: string;
  activities?: AgentActivity[];
  isStreaming?: boolean;
  agentType?: 'research' | 'analysis' | 'project-mgmt' | 'devops';
}

interface EnhancedChatInterfaceProps {
  messages: EnhancedMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onStopGeneration?: () => void;
  className?: string;
}

// Activity status icon component
const ActivityIcon: React.FC<{ type: AgentActivity['type'] }> = ({ type }) => {
  const iconProps = { size: 16, className: "shrink-0" };

  switch (type) {
    case 'thinking':
      return <Loader2 {...iconProps} className="animate-spin text-blue-500" />;
    case 'searching':
      return <Activity {...iconProps} className="animate-pulse text-green-500" />;
    case 'analyzing':
      return <Clock {...iconProps} className="text-yellow-500" />;
    case 'executing':
      return <Play {...iconProps} className="text-purple-500" />;
    case 'completed':
      return <CheckCircle {...iconProps} className="text-green-600" />;
    case 'error':
      return <AlertCircle {...iconProps} className="text-red-500" />;
    default:
      return <Activity {...iconProps} className="text-gray-500" />;
  }
};

// Agent type badge component
const AgentTypeBadge: React.FC<{ type: EnhancedMessage['agentType'] }> = ({ type }) => {
  const variants = {
    'research': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'analysis': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'project-mgmt': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    'devops': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
  };

  if (!type) return null;

  return (
    <Badge variant="secondary" className={cn("text-xs", variants[type])}>
      {type.replace('-', ' ').toUpperCase()}
    </Badge>
  );
};

// Activity timeline component
const ActivityTimeline: React.FC<{ activities: AgentActivity[] }> = ({ activities }) => {
  if (!activities || activities.length === 0) return null;

  return (
    <Card className="mt-3 bg-muted/50">
      <CardContent className="p-3">
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-muted-foreground">Agent Activity</h4>
          <div className="space-y-1">
            {activities.map((activity) => (
              <div key={activity.id} className="flex items-center gap-2 text-sm">
                <ActivityIcon type={activity.type} />
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

// Enhanced message bubble component
const EnhancedMessageBubble: React.FC<{
  message: EnhancedMessage;
  onCopy: (text: string) => void;
  copiedId: string | null;
}> = ({ message, onCopy, copiedId }) => {
  const isHuman = message.type === 'human';
  const isCopied = copiedId === message.id;

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
        "max-w-[80%] space-y-2",
        isHuman ? "order-first" : ""
      )}>
        {/* Agent type badge for AI messages */}
        {!isHuman && message.agentType && (
          <div className="flex items-center gap-2">
            <AgentTypeBadge type={message.agentType} />
            {message.isStreaming && (
              <Badge variant="outline" className="text-xs animate-pulse">
                Streaming...
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
          <CardContent className="p-3">
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

        {/* Activity timeline for AI messages */}
        {!isHuman && <ActivityTimeline activities={message.activities || []} />}
      </div>

      {isHuman && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
          <User size={16} className="text-muted-foreground" />
        </div>
      )}
    </div>
  );
};

// Main enhanced chat interface component
export const EnhancedChatInterface: React.FC<EnhancedChatInterfaceProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onStopGeneration,
  className
}) => {
  const [inputValue, setInputValue] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
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
    <div className={cn("flex flex-col h-full", className)}>
      {/* Messages area */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4 max-w-4xl mx-auto">
          {messages.map((message, index) => (
            <EnhancedMessageBubble
              key={message.id || `msg-${index}`}
              message={message}
              onCopy={(text) => handleCopy(text, message.id || `msg-${index}`)}
              copiedId={copiedId}
            />
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 size={16} className="animate-spin" />
              <span className="text-sm">Agent is thinking...</span>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input area */}
      <div className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="p-4 max-w-4xl mx-auto">
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your AI assistant..."
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
