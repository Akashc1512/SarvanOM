"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useToast } from "@/hooks/useToast";

interface CollaborationContextType {
  // State
  isConnected: boolean;
  sessionId: string | null;
  collaborators: Collaborator[];
  isSharing: boolean;
  isAudioEnabled: boolean;
  isVideoEnabled: boolean;
  
  // Actions
  joinSession: (sessionId: string) => Promise<void>;
  leaveSession: () => Promise<void>;
  inviteUser: (email: string) => Promise<void>;
  toggleSharing: () => void;
  toggleAudio: () => void;
  toggleVideo: () => void;
  updateCollaboratorPermissions: (userId: string, permission: string) => void;
  
  // Real-time features
  sendCursorPosition: (x: number, y: number) => void;
  sendTypingStatus: (isTyping: boolean) => void;
  sendMessage: (message: string) => void;
}

interface Collaborator {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  isOnline: boolean;
  isTyping: boolean;
  cursorPosition?: { x: number; y: number };
  lastSeen: Date;
  permissions: "view" | "edit" | "admin";
}

const CollaborationContext = createContext<CollaborationContextType | undefined>(undefined);

interface CollaborationProviderProps {
  children: React.ReactNode;
}

export function CollaborationProvider({ children }: CollaborationProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isSharing, setIsSharing] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [collaborators, setCollaborators] = useState<Collaborator[]>([
    {
      id: "1",
      name: "Alice Johnson",
      email: "alice@example.com",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=alice",
      isOnline: true,
      isTyping: false,
      lastSeen: new Date(),
      permissions: "edit"
    },
    {
      id: "2",
      name: "Bob Smith",
      email: "bob@example.com",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=bob",
      isOnline: true,
      isTyping: true,
      cursorPosition: { x: 150, y: 200 },
      lastSeen: new Date(),
      permissions: "view"
    }
  ]);

  const { toast } = useToast();

  // Simulate WebSocket connection
  useEffect(() => {
    if (sessionId) {
      // Simulate connection to collaboration server
      const interval = setInterval(() => {
        // Simulate receiving updates from other collaborators
        setCollaborators(prev => prev.map(collaborator => {
          if (collaborator.isOnline && Math.random() > 0.8) {
            return {
              ...collaborator,
              cursorPosition: {
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight
              },
              isTyping: Math.random() > 0.9
            };
          }
          return collaborator;
        }));
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [sessionId]);

  const joinSession = useCallback(async (newSessionId: string) => {
    try {
      // Simulate API call to join session
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSessionId(newSessionId);
      setIsConnected(true);
      
      toast({
        title: "Connected",
        description: `Joined collaboration session: ${newSessionId}`,
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Connection Failed",
        description: "Failed to join collaboration session",
        variant: "destructive",
      });
    }
  }, [toast]);

  const leaveSession = useCallback(async () => {
    try {
      // Simulate API call to leave session
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSessionId(null);
      setIsConnected(false);
      setIsSharing(false);
      setIsAudioEnabled(false);
      setIsVideoEnabled(false);
      
      toast({
        title: "Disconnected",
        description: "Left collaboration session",
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to leave session",
        variant: "destructive",
      });
    }
  }, [toast]);

  const inviteUser = useCallback(async (email: string) => {
    try {
      // Simulate API call to invite user
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Add new collaborator to the list
      const newCollaborator: Collaborator = {
        id: Date.now().toString(),
        name: email.split('@')[0],
        email,
        avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`,
        isOnline: false,
        isTyping: false,
        lastSeen: new Date(),
        permissions: "view"
      };
      
      setCollaborators(prev => [...prev, newCollaborator]);
      
      toast({
        title: "Invitation Sent",
        description: `Invitation sent to ${email}`,
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Invitation Failed",
        description: "Failed to send invitation",
        variant: "destructive",
      });
    }
  }, [toast]);

  const toggleSharing = useCallback(() => {
    setIsSharing(prev => !prev);
    toast({
      title: isSharing ? "Sharing Stopped" : "Sharing Started",
      description: isSharing ? "Session is no longer shared" : "Session is now shared",
      variant: "default",
    });
  }, [isSharing, toast]);

  const toggleAudio = useCallback(() => {
    setIsAudioEnabled(prev => !prev);
    toast({
      title: isAudioEnabled ? "Audio Disabled" : "Audio Enabled",
      description: isAudioEnabled ? "Microphone turned off" : "Microphone turned on",
      variant: "default",
    });
  }, [isAudioEnabled, toast]);

  const toggleVideo = useCallback(() => {
    setIsVideoEnabled(prev => !prev);
    toast({
      title: isVideoEnabled ? "Video Disabled" : "Video Enabled",
      description: isVideoEnabled ? "Camera turned off" : "Camera turned on",
      variant: "default",
    });
  }, [isVideoEnabled, toast]);

  const updateCollaboratorPermissions = useCallback((userId: string, permission: string) => {
    setCollaborators(prev => prev.map(collaborator => 
      collaborator.id === userId 
        ? { ...collaborator, permissions: permission as any }
        : collaborator
    ));
  }, []);

  const sendCursorPosition = useCallback((x: number, y: number) => {
    // Simulate sending cursor position to other collaborators
    if (isConnected) {
      console.log("Sending cursor position:", { x, y });
    }
  }, [isConnected]);

  const sendTypingStatus = useCallback((isTyping: boolean) => {
    // Simulate sending typing status to other collaborators
    if (isConnected) {
      console.log("Sending typing status:", isTyping);
    }
  }, [isConnected]);

  const sendMessage = useCallback((message: string) => {
    // Simulate sending message to other collaborators
    if (isConnected) {
      console.log("Sending message:", message);
      toast({
        title: "Message Sent",
        description: message,
        variant: "default",
      });
    }
  }, [isConnected, toast]);

  const contextValue: CollaborationContextType = {
    // State
    isConnected,
    sessionId,
    collaborators,
    isSharing,
    isAudioEnabled,
    isVideoEnabled,
    
    // Actions
    joinSession,
    leaveSession,
    inviteUser,
    toggleSharing,
    toggleAudio,
    toggleVideo,
    updateCollaboratorPermissions,
    
    // Real-time features
    sendCursorPosition,
    sendTypingStatus,
    sendMessage,
  };

  return (
    <CollaborationContext.Provider value={contextValue}>
      {children}
    </CollaborationContext.Provider>
  );
}

export function useCollaboration() {
  const context = useContext(CollaborationContext);
  if (context === undefined) {
    throw new Error("useCollaboration must be used within a CollaborationProvider");
  }
  return context;
} 