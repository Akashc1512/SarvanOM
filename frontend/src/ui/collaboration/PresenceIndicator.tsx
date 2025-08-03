import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/ui/ui/avatar';
import { Badge } from '@/ui/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/ui/ui/tooltip';
import { Users, User, MessageSquare } from 'lucide-react';
import { type CollaboratorPresence } from '@/hooks/useCollaboration';

interface PresenceIndicatorProps {
  collaborators: CollaboratorPresence[];
  currentUserId?: string;
  className?: string;
  showDetails?: boolean;
}

export function PresenceIndicator({
  collaborators,
  currentUserId,
  className = '',
  showDetails = true,
}: PresenceIndicatorProps) {
  const onlineCollaborators = collaborators.filter(c => c.userId !== currentUserId);
  const typingCollaborators = onlineCollaborators.filter(c => c.isTyping);

  if (onlineCollaborators.length === 0) {
    return null;
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (userId: string) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-yellow-500',
      'bg-red-500',
      'bg-teal-500',
    ];
    const index = userId.charCodeAt(0) % colors.length;
    return colors[index];
  };

  return (
    <TooltipProvider>
      <div className={`flex items-center space-x-2 ${className}`}>
        {/* Online count badge */}
        <Badge variant="secondary" className="flex items-center space-x-1">
          <Users className="h-3 w-3" />
          <span>{onlineCollaborators.length}</span>
        </Badge>

        {/* Collaborator avatars */}
        <div className="flex -space-x-2">
          {onlineCollaborators.slice(0, 3).map((collaborator, index) => (
            <Tooltip key={collaborator.userId}>
              <TooltipTrigger asChild>
                <div className="relative">
                  <Avatar className="h-8 w-8 border-2 border-white">
                    <AvatarImage src={collaborator.avatar} alt={collaborator.name} />
                    <AvatarFallback className={`text-xs text-white ${getAvatarColor(collaborator.userId)}`}>
                      {getInitials(collaborator.name || collaborator.userId)}
                    </AvatarFallback>
                  </Avatar>
                  {collaborator.isTyping && (
                    <div className="absolute -bottom-1 -right-1 bg-green-500 rounded-full p-1">
                      <MessageSquare className="h-2 w-2 text-white" />
                    </div>
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="text-sm">
                  <p className="font-medium">{collaborator.name}</p>
                  {collaborator.isTyping && (
                    <p className="text-green-600 text-xs">typing...</p>
                  )}
                </div>
              </TooltipContent>
            </Tooltip>
          ))}
          
          {onlineCollaborators.length > 3 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <div className="relative">
                  <Avatar className="h-8 w-8 border-2 border-white bg-gray-100">
                    <AvatarFallback className="text-xs text-gray-600">
                      +{onlineCollaborators.length - 3}
                    </AvatarFallback>
                  </Avatar>
                </div>
              </TooltipTrigger>
              <TooltipContent>
                <div className="text-sm">
                  <p>{onlineCollaborators.length - 3} more collaborators</p>
                </div>
              </TooltipContent>
            </Tooltip>
          )}
        </div>

        {/* Typing indicator */}
        {typingCollaborators.length > 0 && showDetails && (
          <div className="flex items-center space-x-1 text-sm text-gray-600">
            <MessageSquare className="h-3 w-3 animate-pulse" />
            <span>
              {typingCollaborators.length === 1
                ? `${typingCollaborators[0]?.name || 'Someone'} is typing...`
                : `${typingCollaborators.length} people are typing...`}
            </span>
          </div>
        )}
      </div>
    </TooltipProvider>
  );
} 