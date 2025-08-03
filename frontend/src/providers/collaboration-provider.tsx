import React, { createContext, useContext, useCallback, useMemo } from 'react';
import { useCollaboration, type CollaborationEvent, type CollaboratorPresence } from '@/hooks/useCollaboration';
import { useAuth } from '@/hooks/useAuth';

interface CollaborationContextValue {
  // State
  isConnected: boolean;
  collaborators: CollaboratorPresence[];
  error: string | null;
  
  // Actions
  sendMessage: (type: string, data: any) => void;
  sendTypingIndicator: (isTyping: boolean) => void;
  sendCursorUpdate: (position: number) => void;
  sendDocumentUpdate: (changes: any[]) => void;
  
  // Utilities
  getOnlineCount: () => number;
  isUserTyping: (userId: string) => boolean;
  
  // Session management
  sessionId: string;
  currentUserId: string;
}

const CollaborationContext = createContext<CollaborationContextValue | null>(null);

interface CollaborationProviderProps {
  children: React.ReactNode;
  sessionId: string;
  onEvent?: (event: CollaborationEvent) => void;
  onPresenceUpdate?: (presence: CollaboratorPresence[]) => void;
}

export function CollaborationProvider({
  children,
  sessionId,
  onEvent,
  onPresenceUpdate,
}: CollaborationProviderProps) {
  const { user } = useAuth();
  const currentUserId = user?.id || 'anonymous';

  const {
    isConnected,
    collaborators,
    error,
    sendMessage,
    sendTypingIndicator,
    sendCursorUpdate,
    sendDocumentUpdate,
    getOnlineCount,
    isUserTyping,
  } = useCollaboration({
    sessionId,
    userId: currentUserId,
    onEvent,
    onPresenceUpdate,
  });

  const contextValue = useMemo<CollaborationContextValue>(() => ({
    // State
    isConnected,
    collaborators,
    error,
    
    // Actions
    sendMessage,
    sendTypingIndicator,
    sendCursorUpdate,
    sendDocumentUpdate,
    
    // Utilities
    getOnlineCount,
    isUserTyping,
    
    // Session management
    sessionId,
    currentUserId,
  }), [
    isConnected,
    collaborators,
    error,
    sendMessage,
    sendTypingIndicator,
    sendCursorUpdate,
    sendDocumentUpdate,
    getOnlineCount,
    isUserTyping,
    sessionId,
    currentUserId,
  ]);

  return (
    <CollaborationContext.Provider value={contextValue}>
      {children}
    </CollaborationContext.Provider>
  );
}

export function useCollaborationContext() {
  const context = useContext(CollaborationContext);
  if (!context) {
    throw new Error('useCollaborationContext must be used within a CollaborationProvider');
  }
  return context;
} 