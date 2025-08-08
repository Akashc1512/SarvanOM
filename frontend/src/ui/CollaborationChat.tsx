"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Send, MessageCircle, Users, Mic, MicOff, Video, VideoOff, MoreVertical } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Input } from "@/ui/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/ui/ui/avatar";
import { Badge } from "@/ui/ui/badge";
import { cn } from "@/lib/utils";
import { useCollaboration } from "@/providers/collaboration-provider";

interface ChatMessage {
  id: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  message: string;
  timestamp: Date;
  type: "text" | "system" | "typing";
}

interface CollaborationChatProps {
  className?: string;
  isOpen?: boolean;
  onToggle?: () => void;
}

export function CollaborationChat({
  className = "",
  isOpen = false,
  onToggle
}: CollaborationChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      userId: "1",
      userName: "Alice Johnson",
      userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=alice",
      message: "Hey everyone! I'm working on the search results page.",
      timestamp: new Date(Date.now() - 5 * 60 * 1000),
      type: "text"
    },
    {
      id: "2",
      userId: "2",
      userName: "Bob Smith",
      userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=bob",
      message: "Great! I can see the cosmic theme is looking really good.",
      timestamp: new Date(Date.now() - 3 * 60 * 1000),
      type: "text"
    },
    {
      id: "3",
      userId: "system",
      userName: "System",
      message: "Bob joined the session",
      timestamp: new Date(Date.now() - 4 * 60 * 1000),
      type: "system"
    }
  ]);

  const [newMessage, setNewMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { isConnected, collaborators, sendMessage, sendTypingStatus } = useCollaboration();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Simulate typing indicators
  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        const randomCollaborator = collaborators[Math.floor(Math.random() * collaborators.length)];
        if (randomCollaborator && Math.random() > 0.8) {
          setMessages(prev => [
            ...prev,
            {
              id: Date.now().toString(),
              userId: randomCollaborator.id,
              userName: randomCollaborator.name,
              userAvatar: randomCollaborator.avatar,
              message: "",
              timestamp: new Date(),
              type: "typing"
            }
          ]);

          // Remove typing indicator after 3 seconds
          setTimeout(() => {
            setMessages(prev => prev.filter(msg => msg.type !== "typing"));
          }, 3000);
        }
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [isConnected, collaborators]);

  const handleSendMessage = useCallback(() => {
    if (newMessage.trim() && isConnected) {
      const message: ChatMessage = {
        id: Date.now().toString(),
        userId: "current-user",
        userName: "You",
        userAvatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=current",
        message: newMessage.trim(),
        timestamp: new Date(),
        type: "text"
      };

      setMessages(prev => [...prev, message]);
      sendMessage(newMessage.trim());
      setNewMessage("");
      setIsTyping(false);
      sendTypingStatus(false);
    }
  }, [newMessage, isConnected, sendMessage, sendTypingStatus]);

  const handleTyping = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setNewMessage(e.target.value);
    
    if (!isTyping && e.target.value.length > 0) {
      setIsTyping(true);
      sendTypingStatus(true);
    } else if (isTyping && e.target.value.length === 0) {
      setIsTyping(false);
      sendTypingStatus(false);
    }
  }, [isTyping, sendTypingStatus]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const getMessageStyle = (message: ChatMessage) => {
    if (message.type === "system") {
      return "text-center text-xs text-gray-500 dark:text-gray-400 italic";
    }
    if (message.type === "typing") {
      return "text-sm text-gray-500 dark:text-gray-400 italic";
    }
    return message.userId === "current-user" 
      ? "text-right" 
      : "text-left";
  };

  const getMessageBubbleStyle = (message: ChatMessage) => {
    if (message.type === "system") {
      return "inline-block px-2 py-1 text-xs";
    }
    if (message.type === "typing") {
      return "inline-flex items-center space-x-1 px-3 py-2 text-sm";
    }
    return message.userId === "current-user"
      ? "bg-purple-600 text-white rounded-lg px-3 py-2 max-w-xs"
      : "bg-gray-100 dark:bg-slate-700 text-gray-900 dark:text-white rounded-lg px-3 py-2 max-w-xs";
  };

  return (
    <div className={cn("relative", className)}>
      {/* Chat Toggle Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={onToggle}
        className={cn(
          "fixed bottom-20 right-4 z-50 rounded-full w-12 h-12 p-0",
          "bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm",
          "border-purple-200/50 dark:border-purple-800/50",
          "hover:bg-white dark:hover:bg-slate-800",
          "transition-all duration-300 hover:scale-110",
          "shadow-lg hover:shadow-xl"
        )}
      >
        <MessageCircle className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        {messages.length > 0 && (
          <Badge 
            variant="secondary" 
            className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs bg-purple-500 text-white"
          >
            {messages.filter(m => m.type === "text").length}
          </Badge>
        )}
      </Button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-32 right-4 z-40 w-80 h-96">
          <Card className="h-full bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 shadow-xl flex flex-col">
            <CardHeader className="pb-3 border-b border-gray-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Collaboration Chat
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    {collaborators.filter(c => c.isOnline).length} online
                  </Badge>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col p-0">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((message) => (
                  <div key={message.id} className={getMessageStyle(message)}>
                    {message.type === "system" ? (
                      <span className={getMessageBubbleStyle(message)}>
                        {message.message}
                      </span>
                    ) : message.type === "typing" ? (
                      <div className={getMessageBubbleStyle(message)}>
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                        </div>
                        <span className="ml-2">{message.userName} is typing...</span>
                      </div>
                    ) : (
                      <div className="flex items-start space-x-2">
                        {message.userId !== "current-user" && (
                          <Avatar className="h-6 w-6">
                            <AvatarImage src={message.userAvatar} />
                            <AvatarFallback className="text-xs">
                              {message.userName.split(" ").map(n => n[0]).join("")}
                            </AvatarFallback>
                          </Avatar>
                        )}
                        <div className="flex-1">
                          <div className={cn(
                            "inline-block",
                            getMessageBubbleStyle(message)
                          )}>
                            {message.message}
                          </div>
                          <div className={cn(
                            "text-xs mt-1",
                            message.userId === "current-user" 
                              ? "text-right text-gray-500 dark:text-gray-400"
                              : "text-left text-gray-500 dark:text-gray-400"
                          )}>
                            {formatTime(message.timestamp)}
                          </div>
                        </div>
                        {message.userId === "current-user" && (
                          <Avatar className="h-6 w-6">
                            <AvatarImage src={message.userAvatar} />
                            <AvatarFallback className="text-xs">
                              {message.userName.split(" ").map(n => n[0]).join("")}
                            </AvatarFallback>
                          </Avatar>
                        )}
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-4 border-t border-gray-200 dark:border-slate-700">
                <div className="flex items-center space-x-2">
                  <Input
                    ref={inputRef}
                    type="text"
                    placeholder="Type a message..."
                    value={newMessage}
                    onChange={handleTyping}
                    onKeyPress={handleKeyPress}
                    disabled={!isConnected}
                    className="flex-1 text-sm"
                  />
                  <Button
                    size="sm"
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim() || !isConnected}
                    className="px-3"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                
                {/* Connection Status */}
                {!isConnected && (
                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
                    Not connected to collaboration session
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

export function useCollaborationChat() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    isOpen,
    toggleChat,
  };
}
