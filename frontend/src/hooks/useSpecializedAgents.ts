import { useState, useCallback, useRef } from 'react';
import { getApiBaseUrl } from '../config/api';

const API_BASE_URL = `${getApiBaseUrl()}/specialized`;

// Types for specialized agents API
interface SpecializedQuery {
  query: string;
  max_research_iterations?: number;
  enable_tracing?: boolean;
  user_id?: string;
  use_real_agents?: boolean;
}

interface Citation {
  source_id: number;
  title: string;
  url: string;
  snippet: string;
  relevance_score: number;
}

interface ExecutionMetrics {
  workflow_stage: string;
  research_iterations: number;
  total_agents_used: number;
  has_research: boolean;
  has_analysis: boolean;
  has_synthesis: boolean;
  overall_quality: number;
  fallback_used: boolean;
  error_count: number;
  total_execution_time?: number;
}

interface SpecializedResponse {
  content?: string;         // Respuesta directa del API
  final_answer?: string;    // Formato legacy
  citations: Citation[];
  quality_score: number;
  execution_metrics: ExecutionMetrics;
  workflow_complete: boolean;
  fallback_used: boolean;
  trace_id?: string;
}

interface SpecializedMessage {
  id: string;
  type: 'human' | 'ai';
  content: string;
  citations?: Citation[];
  qualityScore?: number;
  executionMetrics?: ExecutionMetrics;
  isStreaming?: boolean;
  timestamp: Date;
  activities?: Array<{
    id: string;
    type: 'research' | 'analysis' | 'synthesis';
    status: 'active' | 'completed' | 'error';
    message: string;
    timestamp: Date;
    duration?: number;
  }>;
}

interface UseSpecializedAgentsOptions {
  maxResearchIterations?: number;
  enableTracing?: boolean;
  userId?: string;
  useRealAgents?: boolean;
}

interface UseSpecializedAgentsReturn {
  messages: SpecializedMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  stopGeneration: () => void;
  clearMessages: () => void;
  submitFeedback: (messageId: string, rating: number, comment?: string) => Promise<void>;
  retryLastMessage: () => Promise<void>;
}

export const useSpecializedAgents = (
  options: UseSpecializedAgentsOptions = {}
): UseSpecializedAgentsReturn => {
  const [messages, setMessages] = useState<SpecializedMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastQueryRef = useRef<string>('');

  const {
    maxResearchIterations = 3,
    enableTracing = true,
    userId,
    useRealAgents = true  // Use REAL agents by default
  } = options;

  const generateMessageId = () => `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const createActivityFromStage = (stage: string, isActive: boolean = false) => {
    const activities = [];

    if (stage === 'research' || stage === 'analysis' || stage === 'synthesis' || stage === 'complete') {
      activities.push({
        id: `activity_research_${Date.now()}`,
        type: 'research' as const,
        status: (stage === 'research' && isActive) ? 'active' as const :
                stage === 'research' ? 'completed' as const : 'completed' as const,
        message: 'Gathering information from web sources',
        timestamp: new Date()
      });
    }

    if (stage === 'analysis' || stage === 'synthesis' || stage === 'complete') {
      activities.push({
        id: `activity_analysis_${Date.now()}`,
        type: 'analysis' as const,
        status: (stage === 'analysis' && isActive) ? 'active' as const :
                stage === 'analysis' ? 'completed' as const : 'completed' as const,
        message: 'Analyzing information quality and identifying gaps',
        timestamp: new Date()
      });
    }

    if (stage === 'synthesis' || stage === 'complete') {
      activities.push({
        id: `activity_synthesis_${Date.now()}`,
        type: 'synthesis' as const,
        status: (stage === 'synthesis' && isActive) ? 'active' as const : 'completed' as const,
        message: 'Synthesizing final answer with citations',
        timestamp: new Date()
      });
    }

    return activities;
  };

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);
    lastQueryRef.current = message;

    // Create abort controller for this request
    abortControllerRef.current = new AbortController();

    // Add user message
    const userMessage: SpecializedMessage = {
      id: generateMessageId(),
      type: 'human',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    // Create initial AI message with streaming indicator
    const aiMessageId = generateMessageId();
    const initialAiMessage: SpecializedMessage = {
      id: aiMessageId,
      type: 'ai',
      content: '',
      isStreaming: true,
      timestamp: new Date(),
      activities: createActivityFromStage('research', true)
    };

    setMessages(prev => [...prev, initialAiMessage]);

    try {
      const requestBody: SpecializedQuery = {
        query: message,
        max_research_iterations: maxResearchIterations,
        enable_tracing: enableTracing,
        user_id: userId,
        use_real_agents: useRealAgents
      };

      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result: SpecializedResponse = await response.json();
      console.log('useSpecializedAgents API response:', result);

      // Update the AI message with the final result
      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId ? {
          ...msg,
          content: result.content || result.final_answer || "I couldn't generate a response.",
          citations: result.citations,
          qualityScore: result.quality_score,
          executionMetrics: result.execution_metrics,
          isStreaming: false,
          activities: createActivityFromStage('complete')
        } : msg
      ));

    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Request was cancelled
        setMessages(prev => prev.filter(msg => msg.id !== aiMessageId));
        return;
      }

      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);

      // Update AI message with error
      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId ? {
          ...msg,
          content: `I apologize, but I encountered an error while processing your request: ${errorMessage}`,
          isStreaming: false,
          activities: [{
            id: `error_${Date.now()}`,
            type: 'research' as const,
            status: 'error' as const,
            message: `Error: ${errorMessage}`,
            timestamp: new Date()
          }]
        } : msg
      ));

      console.error('Specialized agents error:', err);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [isLoading, maxResearchIterations, enableTracing, userId, useRealAgents]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
  }, []);

  const submitFeedback = useCallback(async (messageId: string, rating: number, comment?: string) => {
    try {
      // Find the message to get trace_id
      const message = messages.find(msg => msg.id === messageId);
      if (!message || message.type !== 'ai') {
        throw new Error('Message not found or invalid');
      }

      // Use message ID as trace_id if no specific trace_id is available
      const traceId = messageId;

      const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trace_id: traceId,
          rating,
          comment,
          user_id: userId
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to submit feedback');
      }

      console.log('Feedback submitted successfully');
    } catch (err) {
      console.error('Failed to submit feedback:', err);
      throw err;
    }
  }, [messages, userId]);

  const retryLastMessage = useCallback(async () => {
    if (lastQueryRef.current) {
      await sendMessage(lastQueryRef.current);
    }
  }, [sendMessage]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    stopGeneration,
    clearMessages,
    submitFeedback,
    retryLastMessage
  };
};
