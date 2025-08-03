import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/ui/ui/button';
import { Textarea } from '@/ui/ui/TextArea';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Badge } from '@/ui/ui/badge';
import { Send, Users, MessageSquare } from 'lucide-react';
import { useCollaborationContext } from '@/providers/collaboration-provider';
import { PresenceIndicator } from './PresenceIndicator';
import { useDebounce } from '@/hooks/useDebounce';

interface CollaborativeQueryFormProps {
  onSubmit: (query: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export function CollaborativeQueryForm({
  onSubmit,
  placeholder = "Ask a question...",
  disabled = false,
  className = "",
}: CollaborativeQueryFormProps) {
  const [query, setQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const {
    collaborators,
    currentUserId,
    sendTypingIndicator,
    getOnlineCount,
  } = useCollaborationContext();

  // Debounce typing indicator to avoid spam
  const debouncedTypingIndicator = useDebounce(() => isTyping, 500);

  // Send typing indicator when user starts/stops typing
  useEffect(() => {
    sendTypingIndicator(isTyping);
  }, [isTyping, sendTypingIndicator]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setQuery(value);
    setIsTyping(value.length > 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (query.trim() && !disabled) {
      onSubmit(query.trim());
      setQuery('');
      setIsTyping(false);
      sendTypingIndicator(false);
    }
  };

  const onlineCount = getOnlineCount();

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Collaborative Query</CardTitle>
          {onlineCount > 0 && (
            <div className="flex items-center space-x-2">
              <PresenceIndicator 
                collaborators={collaborators}
                currentUserId={currentUserId}
                showDetails={false}
              />
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Collaboration status */}
        {onlineCount > 0 && (
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4" />
              <span>{onlineCount} collaborator{onlineCount !== 1 ? 's' : ''} online</span>
            </div>
            
            {/* Typing indicators */}
            {collaborators.some(c => c.isTyping && c.userId !== currentUserId) && (
              <div className="flex items-center space-x-1 text-green-600">
                <MessageSquare className="h-3 w-3 animate-pulse" />
                <span className="text-xs">Someone is typing...</span>
              </div>
            )}
          </div>
        )}

        {/* Query input */}
        <div className="relative">
          <Textarea
            ref={textareaRef}
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className="min-h-[100px] resize-none"
            rows={3}
          />
          
          {/* Typing indicator for current user */}
          {isTyping && (
            <div className="absolute bottom-2 right-2">
              <Badge variant="secondary" className="text-xs">
                <MessageSquare className="h-3 w-3 mr-1 animate-pulse" />
                typing...
              </Badge>
            </div>
          )}
        </div>

        {/* Submit button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {onlineCount > 0 && (
              <Badge variant="outline" className="text-xs">
                Live collaboration enabled
              </Badge>
            )}
          </div>
          
          <Button
            onClick={handleSubmit}
            disabled={!query.trim() || disabled}
            className="flex items-center space-x-2"
          >
            <Send className="h-4 w-4" />
            <span>Send Query</span>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
} 