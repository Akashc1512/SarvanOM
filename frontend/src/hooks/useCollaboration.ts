import { useEffect, useCallback, useRef, useState } from 'react';
import { websocketManager, type CollaborationMessage } from '@/services/websocket';

export interface CollaborationEvent {
  type: 'new_message' | 'editing_state' | 'user_joined' | 'user_left' | 'cursor_update' | 'document_update';
  data: any;
  userId?: string | undefined;
  sessionId?: string | undefined;
  timestamp: string;
}

export interface CollaboratorPresence {
  userId: string;
  isTyping: boolean;
  cursorPosition?: number;
  lastSeen: string;
  avatar?: string;
  name?: string;
}

export interface UseCollaborationOptions {
  sessionId: string;
  userId?: string;
  onEvent?: ((event: CollaborationEvent) => void) | undefined;
  onPresenceUpdate?: ((presence: CollaboratorPresence[]) => void) | undefined;
  autoReconnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export function useCollaboration({
  sessionId,
  userId = 'anonymous',
  onEvent,
  onPresenceUpdate,
  autoReconnect = true,
  reconnectAttempts = 5,
  reconnectDelay = 1000,
}: UseCollaborationOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [collaborators, setCollaborators] = useState<CollaboratorPresence[]>([]);
  const [error, setError] = useState<string | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);

  // Connect to WebSocket
  const connect = useCallback(async () => {
    try {
      setError(null);
      await websocketManager.connect();
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;

      // Join collaboration session
      websocketManager.joinSession(sessionId, userId);

      // Subscribe to collaboration messages
      const unsubscribe = websocketManager.onCollaborationMessage((message: CollaborationMessage) => {
        handleCollaborationMessage(message);
      });

      return unsubscribe;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect';
      setError(errorMessage);
      setIsConnected(false);
      
      if (autoReconnect && reconnectAttemptsRef.current < reconnectAttempts) {
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current++;
          connect();
        }, reconnectDelay * reconnectAttemptsRef.current);
      }
      
      return undefined;
    }
  }, [sessionId, userId, autoReconnect, reconnectAttempts, reconnectDelay]);

  // Handle collaboration messages
  const handleCollaborationMessage = useCallback((message: CollaborationMessage) => {
    const event: CollaborationEvent = {
      type: message.type as any,
      data: message.data,
      userId: message.userId || message.user_id || undefined,
      sessionId,
      timestamp: message.timestamp,
    };

    // Handle different event types
    switch (event.type) {
      case 'new_message':
        onEvent?.(event);
        break;

      case 'editing_state':
        updateCollaboratorPresence(event.userId!, {
          isTyping: event.data.isTyping,
          lastSeen: event.timestamp,
        });
        onEvent?.(event);
        break;

      case 'user_joined':
        addCollaborator(event.userId!, event.data);
        onEvent?.(event);
        break;

      case 'user_left':
        removeCollaborator(event.userId!);
        onEvent?.(event);
        break;

      case 'cursor_update':
        updateCollaboratorPresence(event.userId!, {
          cursorPosition: event.data.position,
          lastSeen: event.timestamp,
        });
        onEvent?.(event);
        break;

      case 'document_update':
        onEvent?.(event);
        break;

      default:
        onEvent?.(event);
    }
  }, [sessionId, onEvent]);

  // Update collaborator presence
  const updateCollaboratorPresence = useCallback((userId: string, updates: Partial<CollaboratorPresence>) => {
    setCollaborators(prev => {
      const existing = prev.find(c => c.userId === userId);
      if (existing) {
        const updated = { ...existing, ...updates };
        const filtered = prev.filter(c => c.userId !== userId);
        const newCollaborators = [...filtered, updated];
        onPresenceUpdate?.(newCollaborators);
        return newCollaborators;
      }
      return prev;
    });
  }, [onPresenceUpdate]);

  // Add new collaborator
  const addCollaborator = useCallback((userId: string, data: any) => {
    const newCollaborator: CollaboratorPresence = {
      userId,
      isTyping: false,
      lastSeen: new Date().toISOString(),
      avatar: data.avatar,
      name: data.name || userId,
    };
    
    setCollaborators(prev => {
      const newCollaborators = [...prev.filter(c => c.userId !== userId), newCollaborator];
      onPresenceUpdate?.(newCollaborators);
      return newCollaborators;
    });
  }, [onPresenceUpdate]);

  // Remove collaborator
  const removeCollaborator = useCallback((userId: string) => {
    setCollaborators(prev => {
      const newCollaborators = prev.filter(c => c.userId !== userId);
      onPresenceUpdate?.(newCollaborators);
      return newCollaborators;
    });
  }, [onPresenceUpdate]);

  // Send collaboration events
  const sendMessage = useCallback((type: string, data: any) => {
    if (isConnected) {
      websocketManager.send(type, {
        sessionId,
        userId,
        ...data,
      });
    }
  }, [isConnected, sessionId, userId]);

  // Send typing indicator
  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    sendMessage('editing_state', { isTyping });
  }, [sendMessage]);

  // Send cursor update
  const sendCursorUpdate = useCallback((position: number) => {
    websocketManager.updateCursor(sessionId, userId, position);
  }, [sessionId, userId]);

  // Send document update
  const sendDocumentUpdate = useCallback((changes: any[]) => {
    websocketManager.updateDocument(sessionId, userId, changes);
  }, [sessionId, userId]);

  // Disconnect
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    websocketManager.disconnect();
    setIsConnected(false);
    setCollaborators([]);
  }, []);

  // Connect on mount
  useEffect(() => {
    const unsubscribe = connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      disconnect();
      unsubscribe?.then(unsub => unsub?.());
    };
  }, [connect, disconnect]);

  return {
    // State
    isConnected,
    collaborators,
    error,
    
    // Actions
    sendMessage,
    sendTypingIndicator,
    sendCursorUpdate,
    sendDocumentUpdate,
    disconnect,
    connect,
    
    // Utilities
    getOnlineCount: () => collaborators.length,
    isUserTyping: (userId: string) => collaborators.find(c => c.userId === userId)?.isTyping || false,
  };
} 