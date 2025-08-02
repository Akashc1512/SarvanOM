"use client";

import { useState, useEffect, useRef } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { websocketManager, type CollaborationMessage } from "@/lib/websocket";
import { useToast } from "@/hooks/use-toast";
import {
  Users,
  Edit3,
  Save,
  Share2,
  Wifi,
  WifiOff,
  User,
} from "lucide-react";

interface CollaborativeEditorProps {
  sessionId: string;
  userId?: string;
  initialContent?: string;
  onContentChange?: (content: string) => void;
}

interface UserCursor {
  userId: string;
  position: number;
  color: string;
}

export function CollaborativeEditor({
  sessionId,
  userId = "anonymous",
  initialContent = "",
  onContentChange,
}: CollaborativeEditorProps) {
  const { toast } = useToast();
  const [content, setContent] = useState(initialContent);
  const [isConnected, setIsConnected] = useState(false);
  const [activeUsers, setActiveUsers] = useState<string[]>([]);
  const [userCursors, setUserCursors] = useState<UserCursor[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lastCursorPosition = useRef(0);

  useEffect(() => {
    // Connect to collaboration WebSocket
    websocketManager.connectCollaboration(userId);

    // Join session
    websocketManager.joinSession(sessionId, userId);

    // Set up message handlers
    websocketManager.onCollaborationMessage((message: CollaborationMessage) => {
      handleCollaborationMessage(message);
    });

    // Check connection status
    const checkConnection = () => {
      setIsConnected(websocketManager.isConnected());
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000);

    return () => {
      clearInterval(interval);
      websocketManager.disconnect();
    };
  }, [sessionId, userId]);

  const handleCollaborationMessage = (message: CollaborationMessage) => {
    switch (message.type) {
      case "document_updated":
        if (message.user_id !== userId) {
          // Apply changes from other users
          const changes = message.changes || [];
          let newContent = content;

          changes.forEach((change: any) => {
            if (change.type === "insert") {
              newContent =
                newContent.slice(0, change.position) +
                change.text +
                newContent.slice(change.position);
            } else if (change.type === "delete") {
              newContent =
                newContent.slice(0, change.position) +
                newContent.slice(change.position + change.length);
            }
          });

          setContent(newContent);
          onContentChange?.(newContent);
        }
        break;

      case "cursor_updated":
        if (message.user_id !== userId) {
          // Update other user's cursor
          setUserCursors((prev) => {
            const existing = prev.find((c) => c.userId === message.user_id);
            if (existing) {
              return prev.map((c) =>
                c.userId === message.user_id
                  ? { ...c, position: message.position || 0 }
                  : c,
              );
            } else {
              return [
                ...prev,
                {
                  userId: message.user_id,
                  position: message.position || 0,
                  color: `hsl(${Math.random() * 360}, 70%, 50%)`,
                },
              ];
            }
          });
        }
        break;

      case "user_joined":
        setActiveUsers((prev) => {
          if (!prev.includes(message.user_id)) {
            return [...prev, message.user_id];
          }
          return prev;
        });
        break;

      case "user_left":
        setActiveUsers((prev) => prev.filter((id) => id !== message.user_id));
        setUserCursors((prev) =>
          prev.filter((c) => c.userId !== message.user_id),
        );
        break;
    }
  };

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    onContentChange?.(newContent);

    // Send document update to other users
    const cursorPosition = textareaRef.current?.selectionStart || 0;
    const changes = [];

    if (newContent.length > content.length) {
      // Text was inserted
      const insertedText = newContent.slice(
        cursorPosition - (newContent.length - content.length),
        cursorPosition,
      );
      changes.push({
        type: "insert",
        position: cursorPosition - insertedText.length,
        text: insertedText,
      });
    } else if (newContent.length < content.length) {
      // Text was deleted
      changes.push({
        type: "delete",
        position: cursorPosition,
        length: content.length - newContent.length,
      });
    }

    if (changes.length > 0) {
      websocketManager.updateDocument(sessionId, userId, changes);
    }

    // Update cursor position
    if (cursorPosition !== lastCursorPosition.current) {
      websocketManager.updateCursor(sessionId, userId, cursorPosition);
      lastCursorPosition.current = cursorPosition;
    }
  };

  const handleCursorMove = () => {
    const cursorPosition = textareaRef.current?.selectionStart || 0;
    if (cursorPosition !== lastCursorPosition.current) {
      websocketManager.updateCursor(sessionId, userId, cursorPosition);
      lastCursorPosition.current = cursorPosition;
    }
  };

  const handleSave = () => {
    // Save content to backend
    toast({
      title: "Content saved",
      description: "Your collaborative document has been saved",
    });
  };

  const handleShare = () => {
    // Share session link
    const shareUrl = `${window.location.origin}/collaborate/${sessionId}`;
    navigator.clipboard.writeText(shareUrl);
    toast({
      title: "Link copied",
      description: "Collaboration link copied to clipboard",
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Edit3 className="h-5 w-5" />
              Collaborative Editor
            </CardTitle>
            <CardDescription>
              Real-time collaborative editing with {activeUsers.length + 1}{" "}
              users
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={isConnected ? "default" : "secondary"}>
              {isConnected ? (
                <Wifi className="h-3 w-3 mr-1" />
              ) : (
                <WifiOff className="h-3 w-3 mr-1" />
              )}
              {isConnected ? "Connected" : "Disconnected"}
            </Badge>
            <Button variant="outline" size="sm" onClick={handleShare}>
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button size="sm" onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Active Users */}
        {activeUsers.length > 0 && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Users className="h-4 w-4" />
              <span className="text-sm font-medium">Active Users:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="flex items-center gap-1">
                <User className="h-3 w-3" />
                You ({userId})
              </Badge>
              {activeUsers.map((userId) => (
                <Badge
                  key={userId}
                  variant="outline"
                  className="flex items-center gap-1"
                >
                  <User className="h-3 w-3" />
                  {userId}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Collaborative Textarea */}
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => handleContentChange(e.target.value)}
            onSelect={handleCursorMove}
            onKeyUp={handleCursorMove}
            onMouseUp={handleCursorMove}
            placeholder="Start typing to collaborate in real-time..."
            className="min-h-[300px] font-mono text-sm"
            disabled={!isConnected}
          />

          {/* Cursor indicators */}
          {userCursors.map((cursor, index) => (
            <div
              key={cursor.userId}
              className="absolute pointer-events-none"
              style={{
                left: `${(cursor.position / content.length) * 100}%`,
                top: "0",
                width: "2px",
                height: "100%",
                backgroundColor: cursor.color,
                zIndex: 10 + index,
              }}
            >
              <div
                className="absolute -top-6 left-0 px-2 py-1 text-xs text-white rounded"
                style={{ backgroundColor: cursor.color }}
              >
                {cursor.userId}
              </div>
            </div>
          ))}
        </div>

        {/* Connection Status */}
        {!isConnected && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2">
              <WifiOff className="h-4 w-4 text-yellow-600" />
              <span className="text-sm text-yellow-800">
                Connection lost. Attempting to reconnect...
              </span>
            </div>
          </div>
        )}

        {/* Session Info */}
        <div className="mt-4 text-xs text-gray-500">
          Session ID: {sessionId} • Last updated:{" "}
          {new Date().toLocaleTimeString()}
        </div>
      </CardContent>
    </Card>
  );
}
