"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Users, User, MessageCircle, Share2, Eye, EyeOff, Mic, MicOff, Video, VideoOff } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/ui/ui/avatar";
import { cn } from "@/lib/utils";

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

interface CollaborationPanelProps {
  className?: string;
  sessionId?: string;
  onInvite?: (email: string) => void;
  onPermissionChange?: (userId: string, permission: string) => void;
}

export function CollaborationPanel({
  className = "",
  sessionId,
  onInvite,
  onPermissionChange
}: CollaborationPanelProps) {
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
    },
    {
      id: "3",
      name: "Carol Davis",
      email: "carol@example.com",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=carol",
      isOnline: false,
      isTyping: false,
      lastSeen: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
      permissions: "edit"
    }
  ]);

  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [showInviteForm, setShowInviteForm] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  // Simulate real-time cursor updates
  useEffect(() => {
    const updateCursors = () => {
      setCollaborators(prev => prev.map(collaborator => {
        if (collaborator.isOnline && Math.random() > 0.7) {
          return {
            ...collaborator,
            cursorPosition: {
              x: Math.random() * 800,
              y: Math.random() * 600
            }
          };
        }
        return collaborator;
      }));
    };

    const interval = setInterval(updateCursors, 2000);
    return () => clearInterval(interval);
  }, []);

  // Render cursor positions on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const renderCursors = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      collaborators.forEach(collaborator => {
        if (collaborator.isOnline && collaborator.cursorPosition) {
          const { x, y } = collaborator.cursorPosition;
          
          // Draw cursor
          ctx.fillStyle = getCollaboratorColor(collaborator.id);
          ctx.fillRect(x, y, 2, 20);
          
          // Draw cursor label
          ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
          ctx.font = "12px system-ui";
          ctx.fillText(collaborator.name, x + 5, y - 5);
        }
      });

      animationRef.current = requestAnimationFrame(renderCursors);
    };

    renderCursors();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [collaborators]);

  const getCollaboratorColor = (id: string) => {
    const colors = [
      "#3b82f6", // blue
      "#ef4444", // red
      "#10b981", // green
      "#f59e0b", // amber
      "#8b5cf6", // purple
      "#06b6d4", // cyan
    ];
    return colors[parseInt(id) % colors.length];
  };

  const handleInvite = useCallback(() => {
    if (inviteEmail.trim() && onInvite) {
      onInvite(inviteEmail.trim());
      setInviteEmail("");
      setShowInviteForm(false);
    }
  }, [inviteEmail, onInvite]);

  const handlePermissionChange = useCallback((userId: string, permission: string) => {
    setCollaborators(prev => prev.map(collaborator => 
      collaborator.id === userId 
        ? { ...collaborator, permissions: permission as any }
        : collaborator
    ));
    onPermissionChange?.(userId, permission);
  }, [onPermissionChange]);

  const onlineCount = collaborators.filter(c => c.isOnline).length;
  const typingCount = collaborators.filter(c => c.isTyping).length;

  return (
    <div className={cn("relative", className)}>
      {/* Floating Action Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsPanelOpen(!isPanelOpen)}
        className={cn(
          "fixed bottom-4 right-4 z-50 rounded-full w-12 h-12 p-0",
          "bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm",
          "border-purple-200/50 dark:border-purple-800/50",
          "hover:bg-white dark:hover:bg-slate-800",
          "transition-all duration-300 hover:scale-110",
          "shadow-lg hover:shadow-xl"
        )}
      >
        <Users className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        {onlineCount > 0 && (
          <Badge 
            variant="secondary" 
            className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs bg-purple-500 text-white"
          >
            {onlineCount}
          </Badge>
        )}
      </Button>

      {/* Collaboration Panel */}
      {isPanelOpen && (
        <div className="fixed bottom-20 right-4 z-40 w-80">
          <Card className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Collaboration
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {onlineCount} online
                  </Badge>
                  {typingCount > 0 && (
                    <Badge variant="secondary" className="text-xs">
                      {typingCount} typing
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Session Controls */}
              <div className="flex items-center space-x-2">
                <Button
                  variant={isSharing ? "default" : "outline"}
                  size="sm"
                  onClick={() => setIsSharing(!isSharing)}
                  className="flex-1"
                >
                  <Share2 className="h-4 w-4 mr-2" />
                  {isSharing ? "Stop Sharing" : "Share Session"}
                </Button>
                <Button
                  variant={isAudioEnabled ? "default" : "outline"}
                  size="sm"
                  onClick={() => setIsAudioEnabled(!isAudioEnabled)}
                >
                  {isAudioEnabled ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
                </Button>
                <Button
                  variant={isVideoEnabled ? "default" : "outline"}
                  size="sm"
                  onClick={() => setIsVideoEnabled(!isVideoEnabled)}
                >
                  {isVideoEnabled ? <Video className="h-4 w-4" /> : <VideoOff className="h-4 w-4" />}
                </Button>
              </div>

              {/* Collaborators List */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Collaborators
                </h4>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {collaborators.map((collaborator) => (
                    <div
                      key={collaborator.id}
                      className="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-slate-700/50"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="relative">
                          <Avatar className="h-8 w-8">
                            <AvatarImage src={collaborator.avatar} />
                            <AvatarFallback>
                              {collaborator.name.split(" ").map(n => n[0]).join("")}
                            </AvatarFallback>
                          </Avatar>
                          <div
                            className={cn(
                              "absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white dark:border-slate-800",
                              collaborator.isOnline ? "bg-green-500" : "bg-gray-400"
                            )}
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {collaborator.name}
                          </p>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {collaborator.permissions}
                            </span>
                            {collaborator.isTyping && (
                              <span className="text-xs text-purple-600 dark:text-purple-400">
                                typing...
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1">
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: getCollaboratorColor(collaborator.id) }}
                        />
                        <select
                          value={collaborator.permissions}
                          onChange={(e) => handlePermissionChange(collaborator.id, e.target.value)}
                          className="text-xs bg-transparent border-none focus:outline-none text-gray-600 dark:text-gray-400"
                        >
                          <option value="view">View</option>
                          <option value="edit">Edit</option>
                          <option value="admin">Admin</option>
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Invite Section */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Invite Others
                  </h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowInviteForm(!showInviteForm)}
                  >
                    {showInviteForm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
                {showInviteForm && (
                  <div className="space-y-2">
                    <input
                      type="email"
                      placeholder="Enter email address"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-slate-600 rounded-md bg-white dark:bg-slate-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                    <Button
                      size="sm"
                      onClick={handleInvite}
                      disabled={!inviteEmail.trim()}
                      className="w-full"
                    >
                      Send Invite
                    </Button>
                  </div>
                )}
              </div>

              {/* Session Info */}
              {sessionId && (
                <div className="pt-2 border-t border-gray-200 dark:border-slate-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Session ID: {sessionId}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Cursor Canvas (hidden but active) */}
      <canvas
        ref={canvasRef}
        className="fixed inset-0 pointer-events-none z-30"
        style={{ width: "100vw", height: "100vh" }}
      />
    </div>
  );
}

export function useCollaboration() {
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const joinSession = useCallback(async (sessionId: string) => {
    // Simulate joining a collaboration session
    setSessionId(sessionId);
    setIsConnected(true);
  }, []);

  const leaveSession = useCallback(async () => {
    setSessionId(null);
    setIsConnected(false);
  }, []);

  const inviteUser = useCallback(async (email: string) => {
    // Simulate inviting a user
    console.log("Inviting user:", email);
  }, []);

  return {
    isConnected,
    sessionId,
    joinSession,
    leaveSession,
    inviteUser,
  };
}
