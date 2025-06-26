import { useState, useCallback, useRef } from 'react';
import { getApiBaseUrl } from '@/config/api';

export interface ChatMessage {
  id: string;
  type: 'human' | 'ai' | 'error';
  content: string;
  timestamp: Date;
  citations?: string[];
  quality_score?: number;
  execution_metrics?: Record<string, any>;
}

export interface ChatOptions {
  max_research_iterations?: number;
  enable_tracing?: boolean;
  use_memory?: boolean;
  project_id?: number;
  user_id?: string;
}

export const useChatWithMemory = (options: ChatOptions = {}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string>(`chat_session_${Date.now()}`);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Cancel any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    setError(null);
    setIsLoading(true);

    // Add user message
    const userMessage: ChatMessage = {
      id: `human_${Date.now()}`,
      type: 'human',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch(`${getApiBaseUrl()}/specialized/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content.trim(),
          max_research_iterations: options.max_research_iterations || 2,
          enable_tracing: options.enable_tracing ?? true,
          use_multi_agent: false,
          use_real_agents: true,
          use_memory: options.use_memory ?? true,
          session_id: sessionIdRef.current,
          user_id: options.user_id || 'default_user',
          project_id: options.project_id,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Add AI response
      console.log('API response data:', data);
      const aiMessage: ChatMessage = {
        id: `ai_${Date.now()}`,
        type: 'ai',
        content: data.content || data.final_answer || "I couldn't generate a response.",
        timestamp: new Date(),
        citations: data.citations || [],
        quality_score: data.quality_score,
        execution_metrics: data.execution_metrics,
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Request was aborted');
        return;
      }

      console.error('Error sending message:', error);
      setError(error.message);
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        type: 'error',
        content: `Error: ${error.message}. Please try again.`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [isLoading, options]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    // Generate new session ID for fresh conversation
    sessionIdRef.current = `chat_session_${Date.now()}`;
  }, []);

  const retryLastMessage = useCallback(() => {
    if (messages.length === 0) return;
    
    // Find the last human message
    const lastHumanMessage = [...messages].reverse().find(msg => msg.type === 'human');
    if (lastHumanMessage) {
      // Remove messages after the last human message
      const lastHumanIndex = messages.findIndex(msg => msg.id === lastHumanMessage.id);
      setMessages(prev => prev.slice(0, lastHumanIndex + 1));
      
      // Resend the message
      sendMessage(lastHumanMessage.content);
    }
  }, [messages, sendMessage]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    stopGeneration,
    clearMessages,
    retryLastMessage,
    sessionId: sessionIdRef.current,
  };
};
