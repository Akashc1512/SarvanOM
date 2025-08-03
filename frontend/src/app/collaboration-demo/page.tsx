"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Badge } from '@/ui/ui/badge';
import { Button } from '@/ui/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/ui/ui/tabs';
import { Alert, AlertDescription } from '@/ui/ui/alert';
import { 
  Users, 
  MessageSquare, 
  Wifi, 
  WifiOff, 
  RefreshCw,
  Copy,
  CheckCircle
} from 'lucide-react';
import { CollaborationProvider, useCollaborationContext } from '@/providers/collaboration-provider';
import { CollaborativeQueryForm } from '@/ui/collaboration/CollaborativeQueryForm';
import { PresenceIndicator } from '@/ui/collaboration/PresenceIndicator';
import { useToast } from '@/hooks/use-toast';

// Generate a unique session ID for this demo
const DEMO_SESSION_ID = `demo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

function CollaborationDemoContent() {
  const [messages, setMessages] = useState<Array<{id: string, text: string, userId: string, timestamp: string}>>([]);
  const [copiedSessionId, setCopiedSessionId] = useState(false);
  const { toast } = useToast();
  
  const {
    isConnected,
    collaborators,
    error,
    sendMessage,
    getOnlineCount,
    sessionId,
    currentUserId,
  } = useCollaborationContext();

  // Handle collaboration events
  const handleCollaborationEvent = (event: any) => {
    if (event.type === 'new_message') {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: event.data.message,
        userId: event.userId || 'anonymous',
        timestamp: event.timestamp,
      }]);
    }
  };

  const copySessionId = async () => {
    try {
      await navigator.clipboard.writeText(sessionId);
      setCopiedSessionId(true);
      toast({
        title: "Session ID copied",
        description: "Share this ID with others to join the collaboration",
      });
      setTimeout(() => setCopiedSessionId(false), 2000);
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Please copy the session ID manually",
        variant: "destructive",
      });
    }
  };

  const handleQuerySubmit = (query: string) => {
    // Send message to other collaborators
    sendMessage('new_message', { message: query });
    
    // Add to local messages
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      text: query,
      userId: currentUserId,
      timestamp: new Date().toISOString(),
    }]);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Collaboration Demo</h1>
          <p className="text-gray-600">Test real-time collaboration features</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Connection status */}
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <Wifi className="h-5 w-5 text-green-500" />
            ) : (
              <WifiOff className="h-5 w-5 text-red-500" />
            )}
            <span className="text-sm">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          {/* Online count */}
          <Badge variant="secondary">
            <Users className="h-3 w-3 mr-1" />
            {getOnlineCount()} online
          </Badge>
        </div>
      </div>

      {/* Session info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Session Information
            <Button
              variant="outline"
              size="sm"
              onClick={copySessionId}
              className="flex items-center space-x-2"
            >
              {copiedSessionId ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
              <span>Copy Session ID</span>
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Session ID:</span>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                {sessionId}
              </code>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Your ID:</span>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                {currentUserId}
              </code>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Status:</span>
              <Badge variant={isConnected ? "default" : "destructive"}>
                {isConnected ? 'Active' : 'Inactive'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error display */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>
            Connection error: {error}
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="chat" className="space-y-4">
        <TabsList>
          <TabsTrigger value="chat">Live Chat</TabsTrigger>
          <TabsTrigger value="collaborators">Collaborators</TabsTrigger>
          <TabsTrigger value="query">Query Form</TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Live Chat
                <PresenceIndicator 
                  collaborators={collaborators}
                  currentUserId={currentUserId}
                />
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p>No messages yet. Start typing to see collaboration in action!</p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${
                          message.userId === currentUserId ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-xs px-4 py-2 rounded-lg ${
                            message.userId === currentUserId
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <div className="text-sm font-medium mb-1">
                            {message.userId === currentUserId ? 'You' : message.userId}
                          </div>
                          <div className="text-sm">{message.text}</div>
                          <div className="text-xs opacity-70 mt-1">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="collaborators" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Collaborators</CardTitle>
            </CardHeader>
            <CardContent>
              {collaborators.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No other collaborators online</p>
                  <p className="text-sm">Open this page in another tab to see collaboration</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {collaborators.map((collaborator) => (
                    <div
                      key={collaborator.userId}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                          {(collaborator.name || collaborator.userId).charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div className="font-medium">
                            {collaborator.name || collaborator.userId}
                          </div>
                          <div className="text-sm text-gray-500">
                            Last seen: {new Date(collaborator.lastSeen).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {collaborator.isTyping && (
                          <Badge variant="secondary" className="text-xs">
                            <MessageSquare className="h-3 w-3 mr-1 animate-pulse" />
                            typing
                          </Badge>
                        )}
                        <Badge variant="outline" className="text-xs">
                          online
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="query" className="space-y-4">
          <CollaborativeQueryForm
            onSubmit={handleQuerySubmit}
            placeholder="Type a message to test collaboration..."
          />
        </TabsContent>
      </Tabs>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How to Test</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <p>Copy the session ID and open this page in another browser tab</p>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <p>Type messages in the chat or query form to see real-time updates</p>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <p>Watch for typing indicators and presence updates</p>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <p>Test connection stability by refreshing the page</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function CollaborationDemoPage() {
  return (
    <CollaborationProvider
      sessionId={DEMO_SESSION_ID}
      onEvent={(event) => {
        console.log('Collaboration event:', event);
      }}
    >
      <CollaborationDemoContent />
    </CollaborationProvider>
  );
} 