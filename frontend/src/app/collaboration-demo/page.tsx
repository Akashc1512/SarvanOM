"use client";

import { useState, useEffect } from "react";
import { Users, MessageCircle, Share2, Zap, Sparkles, Globe, Brain } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { CollaborationPanel } from "@/ui/CollaborationPanel";
import { CollaborationChat } from "@/ui/CollaborationChat";
import { TestRunner } from "@/ui/TestRunner";
import { PerformanceMonitor } from "@/ui/PerformanceMonitor";
import { useCollaboration } from "@/providers/collaboration-provider";
import { useCollaborationChat } from "@/ui/CollaborationChat";
import { useTestRunner } from "@/ui/TestRunner";
import { usePerformanceMonitor } from "@/ui/PerformanceMonitor";
import { cn } from "@/lib/utils";

export default function CollaborationDemoPage() {
  const [sessionId, setSessionId] = useState("demo-session-123");
  const [isConnected, setIsConnected] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  
  const { 
    isConnected: isCollaborationConnected, 
    joinSession, 
    leaveSession, 
    collaborators,
    isSharing,
    isAudioEnabled,
    isVideoEnabled
  } = useCollaboration();
  
  const { isOpen: isChatOpen, toggleChat } = useCollaborationChat();

  useEffect(() => {
    // Auto-join demo session
    if (!isConnected) {
      joinSession(sessionId);
      setIsConnected(true);
      setDemoMode(true);
    }
  }, [joinSession, sessionId, isConnected]);

  const handleLeaveSession = async () => {
    await leaveSession();
    setIsConnected(false);
    setDemoMode(false);
  };

  const onlineCount = collaborators.filter(c => c.isOnline).length;
  const typingCount = collaborators.filter(c => c.isTyping).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-purple-900">
      {/* Cosmic Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-blue-500/5 to-cyan-500/5" />
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 left-20 w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
          <div className="absolute top-40 right-32 w-1 h-1 bg-blue-400 rounded-full animate-pulse delay-100" />
          <div className="absolute bottom-32 left-1/4 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse delay-200" />
          <div className="absolute top-1/2 right-1/4 w-1 h-1 bg-purple-300 rounded-full animate-pulse delay-300" />
        </div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="relative">
              <Sparkles className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-400 rounded-full animate-pulse" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Collaboration Demo
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Experience real-time collaboration features with cosmic styling. 
            See live cursors, chat with team members, and share your session.
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/50 rounded-lg">
                  <Users className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Online Users</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{onlineCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                  <MessageCircle className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Typing</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{typingCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-lg">
                  <Zap className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Status</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {isCollaborationConnected ? "Connected" : "Disconnected"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Demo Controls */}
        <div className="max-w-4xl mx-auto mb-8">
          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                Demo Controls
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900 dark:text-white">Session Status</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Session ID: {sessionId}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge 
                    variant={isCollaborationConnected ? "default" : "secondary"}
                    className={cn(
                      isCollaborationConnected 
                        ? "bg-green-500 text-white" 
                        : "bg-gray-500 text-white"
                    )}
                  >
                    {isCollaborationConnected ? "Connected" : "Disconnected"}
                  </Badge>
                  {demoMode && (
                    <Badge variant="outline" className="text-xs">
                      Demo Mode
                    </Badge>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <Button
                  variant={isCollaborationConnected ? "outline" : "default"}
                  onClick={isCollaborationConnected ? handleLeaveSession : () => joinSession(sessionId)}
                  className="flex-1"
                >
                  {isCollaborationConnected ? "Leave Session" : "Join Session"}
                </Button>
                <Button
                  variant="outline"
                  onClick={toggleChat}
                  className="flex-1"
                >
                  <MessageCircle className="h-4 w-4 mr-2" />
                  {isChatOpen ? "Close Chat" : "Open Chat"}
                </Button>
              </div>

              {/* Feature Indicators */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-slate-700">
                <div className="flex items-center space-x-2">
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    isSharing ? "bg-green-500" : "bg-gray-300"
                  )} />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Sharing</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    isAudioEnabled ? "bg-green-500" : "bg-gray-300"
                  )} />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Audio</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    isVideoEnabled ? "bg-green-500" : "bg-gray-300"
                  )} />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Video</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Cursors</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Feature Showcase */}
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Live Cursors Demo */}
            <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                  Live Cursor Tracking
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative h-64 bg-gray-50 dark:bg-slate-700/50 rounded-lg border-2 border-dashed border-gray-300 dark:border-slate-600 overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <p className="text-gray-500 dark:text-gray-400 text-center">
                      Move your mouse around to see live cursor tracking
                      <br />
                      <span className="text-sm">Other users' cursors will appear here</span>
                    </p>
                  </div>
                  
                  {/* Simulated cursors */}
                  {collaborators.map((collaborator) => (
                    collaborator.cursorPosition && (
                      <div
                        key={collaborator.id}
                        className="absolute w-4 h-4 pointer-events-none"
                        style={{
                          left: collaborator.cursorPosition.x,
                          top: collaborator.cursorPosition.y,
                          transform: 'translate(-50%, -50%)'
                        }}
                      >
                        <div className="w-4 h-4 bg-purple-500 rounded-full animate-pulse" />
                        <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                          {collaborator.name}
                        </div>
                      </div>
                    )
                  ))}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
                  Real-time cursor positions are shared across all connected users
                </p>
              </CardContent>
            </Card>

            {/* Collaboration Features */}
            <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                  Collaboration Features
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/50 rounded-lg">
                      <Users className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">User Presence</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        See who's online and their current activity
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                      <MessageCircle className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Real-time Chat</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Instant messaging with typing indicators
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-lg">
                      <Share2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Session Sharing</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Share your screen and collaborate in real-time
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-cyan-100 dark:bg-cyan-900/50 rounded-lg">
                      <Globe className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Permission Control</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Manage access levels for different users
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Instructions */}
        <div className="max-w-4xl mx-auto mt-8">
          <Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white">
                How to Use
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Getting Started</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li>• Click the collaboration button (bottom right) to open the panel</li>
                    <li>• Use the chat button to start messaging with team members</li>
                    <li>• Move your mouse to see live cursor tracking</li>
                    <li>• Invite others by entering their email address</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Features</h4>
                  <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                    <li>• Real-time cursor tracking across all users</li>
                    <li>• Live chat with typing indicators</li>
                    <li>• User presence and activity status</li>
                    <li>• Permission management for different access levels</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Collaboration Components */}
      <CollaborationPanel />
      <CollaborationChat isOpen={isChatOpen} onToggle={toggleChat} />
    </div>
  );
} 