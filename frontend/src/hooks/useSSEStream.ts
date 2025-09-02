import { useCallback, useEffect, useRef, useState } from 'react';

interface SSEEvent {
  type: 'content_chunk' | 'heartbeat' | 'complete' | 'error';
  data: any;
  timestamp: string;
  trace_id?: string;
}

interface SSEStreamOptions {
  query: string;
  maxTokens?: number;
  temperature?: number;
  onContent?: (content: string) => void;
  onComplete?: (data: any) => void;
  onError?: (error: string) => void;
  onHeartbeat?: (data: any) => void;
  silenceThreshold?: number; // seconds of silence before reconnect
  maxReconnectAttempts?: number;
  reconnectDelay?: number; // ms between reconnect attempts
}

interface SSEStreamState {
  isConnected: boolean;
  isReconnecting: boolean;
  reconnectAttempts: number;
  lastMessageTime: number;
  traceId?: string;
  error?: string;
}

export function useSSEStream(options: SSEStreamOptions) {
  const {
    query,
    maxTokens = 1000,
    temperature = 0.2,
    onContent,
    onComplete,
    onError,
    onHeartbeat,
    silenceThreshold = 15, // 15 seconds default
    maxReconnectAttempts = 3,
    reconnectDelay = 2000 // 2 seconds default
  } = options;

  const [state, setState] = useState<SSEStreamState>({
    isConnected: false,
    isReconnecting: false,
    reconnectAttempts: 0,
    lastMessageTime: Date.now()
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isActiveRef = useRef<boolean>(false);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const clearTimeouts = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
      silenceTimeoutRef.current = null;
    }
  }, []);

  const closeConnection = useCallback(() => {
    isActiveRef.current = false;
    clearTimeouts();
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
      isReconnecting: false
    }));
  }, [clearTimeouts]);

  const handleMessage = useCallback((event: MessageEvent) => {
    const now = Date.now();
    
    setState(prev => ({
      ...prev,
      lastMessageTime: now,
      error: undefined
    }));

    // Clear silence timeout and set new one
    if (silenceTimeoutRef.current) {
      clearTimeout(silenceTimeoutRef.current);
    }

    silenceTimeoutRef.current = setTimeout(() => {
      if (isActiveRef.current && !state.isReconnecting) {
        console.warn('SSE silence threshold exceeded, reconnecting...');
        closeConnection();
        // Trigger reconnect
        setTimeout(() => {
          if (isActiveRef.current) {
            connect();
          }
        }, reconnectDelay);
      }
    }, silenceThreshold * 1000);

    try {
      const data = JSON.parse(event.data);
      const sseEvent: SSEEvent = {
        type: data.type || 'content_chunk',
        data: data,
        timestamp: new Date().toISOString(),
        trace_id: data.trace_id
      };

      // Update trace ID from first message
      if (sseEvent.trace_id && !state.traceId) {
        setState(prev => ({ ...prev, traceId: sseEvent.trace_id }));
      }

      switch (sseEvent.type) {
        case 'content_chunk':
          if (sseEvent.data.type === 'content' && sseEvent.data.text) {
            onContent?.(sseEvent.data.text);
          }
          break;
        
        case 'heartbeat':
          onHeartbeat?.(sseEvent.data);
          break;
        
        case 'complete':
          onComplete?.(sseEvent.data);
          closeConnection();
          break;
        
        case 'error':
          onError?.(sseEvent.data.error || 'Unknown error');
          closeConnection();
          break;
      }
    } catch (error) {
      console.error('Error parsing SSE message:', error);
      onError?.('Failed to parse server message');
    }
  }, [onContent, onComplete, onError, onHeartbeat, silenceThreshold, reconnectDelay, state.isReconnecting, state.traceId, closeConnection]);

  const connect = useCallback(() => {
    if (!isActiveRef.current) return;

    // Don't reconnect if we've exceeded max attempts
    if (state.reconnectAttempts >= maxReconnectAttempts) {
      setState(prev => ({
        ...prev,
        error: `Max reconnection attempts (${maxReconnectAttempts}) exceeded`,
        isReconnecting: false
      }));
      onError?.(`Max reconnection attempts (${maxReconnectAttempts}) exceeded`);
      return;
    }

    setState(prev => ({
      ...prev,
      isReconnecting: true,
      reconnectAttempts: prev.reconnectAttempts + 1
    }));

    const url = new URL(`${API_BASE_URL}/stream/search`);
    url.searchParams.set('query', query);
    url.searchParams.set('max_tokens', maxTokens.toString());
    url.searchParams.set('temperature', temperature.toString());

    const eventSource = new EventSource(url.toString());
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('SSE connection opened');
      setState(prev => ({
        ...prev,
        isConnected: true,
        isReconnecting: false,
        reconnectAttempts: 0, // Reset on successful connection
        lastMessageTime: Date.now()
      }));
    };

    eventSource.onmessage = handleMessage;

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      
      if (eventSource.readyState === EventSource.CLOSED) {
        setState(prev => ({
          ...prev,
          isConnected: false,
          error: 'Connection closed by server'
        }));
        
        // Attempt to reconnect if still active
        if (isActiveRef.current && state.reconnectAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isActiveRef.current) {
              connect();
            }
          }, reconnectDelay);
        } else if (state.reconnectAttempts >= maxReconnectAttempts) {
          setState(prev => ({
            ...prev,
            isReconnecting: false,
            error: `Max reconnection attempts (${maxReconnectAttempts}) exceeded`
          }));
          onError?.(`Max reconnection attempts (${maxReconnectAttempts}) exceeded`);
        }
      }
    };
  }, [query, maxTokens, temperature, API_BASE_URL, handleMessage, state.reconnectAttempts, maxReconnectAttempts, reconnectDelay, onError]);

  const start = useCallback(() => {
    if (isActiveRef.current) {
      closeConnection();
    }

    isActiveRef.current = true;
    setState({
      isConnected: false,
      isReconnecting: false,
      reconnectAttempts: 0,
      lastMessageTime: Date.now()
    });

    connect();
  }, [connect, closeConnection]);

  const stop = useCallback(() => {
    isActiveRef.current = false;
    closeConnection();
  }, [closeConnection]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isActiveRef.current = false;
      clearTimeouts();
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [clearTimeouts]);

  return {
    start,
    stop,
    isConnected: state.isConnected,
    isReconnecting: state.isReconnecting,
    reconnectAttempts: state.reconnectAttempts,
    traceId: state.traceId,
    error: state.error,
    lastMessageTime: state.lastMessageTime
  };
}
