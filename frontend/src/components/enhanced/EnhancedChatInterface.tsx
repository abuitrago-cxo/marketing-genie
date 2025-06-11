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

export interface EnhancedMessage {
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
  const [input, setInput] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text); // Assuming text is unique enough for ID
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages, isLoading]);

  return (
    <div className={cn("flex flex-col h-full", className)}>
      <div className="flex-1 p-4 pb-0 overflow-auto">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <EnhancedMessageBubble
              key={message.id || index}
              message={message}
              onCopy={handleCopy}
              copiedId={copiedId}
            />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted border rounded-lg p-3 max-w-[80%] flex items-center space-x-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Agent is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" /> {/* Spacer to ensure last message is visible */}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex items-end p-4 border-t bg-background gap-2 flex-none">
        <textarea
          ref={textareaRef}
          placeholder={isLoading ? "Agent is thinking..." : "Type your message..."}
          value={input}
          onChange={handleInputChange}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          className="flex-1 resize-none overflow-hidden max-h-40 p-2.5 text-sm rounded-lg border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          rows={1}
          disabled={isLoading}
        />
        <Button type="submit" disabled={!input.trim() || isLoading} size="icon" className="h-11 w-11">
          {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          <span className="sr-only">Send message</span>
        </Button>
        {isLoading && onStopGeneration && (
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={onStopGeneration}
            className="h-11 w-11"
          >
            <Square className="h-5 w-5" />
            <span className="sr-only">Stop generation</span>
          </Button>
        )}
      </form>
    </div>
  );
};
