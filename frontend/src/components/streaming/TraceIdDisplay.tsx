'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';

interface TraceIdDisplayProps {
  traceId: string;
  className?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const TraceIdDisplay: React.FC<TraceIdDisplayProps> = ({
  traceId,
  className,
  showLabel = true,
  size = 'md'
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(traceId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy trace ID:', err);
    }
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {showLabel && (
        <span className="text-xs cosmic-text-secondary font-medium">Trace ID:</span>
      )}
      <motion.button
        onClick={handleCopy}
        className={cn(
          'inline-flex items-center gap-2 rounded-lg border border-cosmic-border-primary bg-cosmic-bg-secondary text-cosmic-text-primary font-mono transition-all duration-200 hover:bg-cosmic-bg-tertiary hover:border-cosmic-border-accent cosmic-hover-lift',
          sizeClasses[size]
        )}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        title="Click to copy trace ID"
      >
        <span className="truncate max-w-32">{traceId}</span>
        <motion.div
          initial={false}
          animate={{ scale: copied ? 1.2 : 1 }}
          transition={{ duration: 0.2 }}
        >
          {copied ? (
            <CheckIcon className={cn(iconSizes[size], 'text-cosmic-success')} />
          ) : (
            <ClipboardIcon className={cn(iconSizes[size], 'text-cosmic-text-tertiary')} />
          )}
        </motion.div>
      </motion.button>
      {copied && (
        <motion.span
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -10 }}
          className="text-xs text-cosmic-success font-medium"
        >
          Copied!
        </motion.span>
      )}
    </div>
  );
};

interface StreamingStatusProps {
  isStreaming: boolean;
  connectionStatus: 'connected' | 'connecting' | 'reconnecting' | 'disconnected';
  lastHeartbeat?: number;
  className?: string;
}

const StreamingStatus: React.FC<StreamingStatusProps> = ({
  isStreaming,
  connectionStatus,
  lastHeartbeat,
  className
}) => {
  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-cosmic-success';
      case 'connecting':
      case 'reconnecting':
        return 'text-cosmic-warning';
      case 'disconnected':
        return 'text-cosmic-error';
      default:
        return 'text-cosmic-text-tertiary';
    }
  };

  const getStatusText = () => {
    if (isStreaming) return 'Streaming';
    switch (connectionStatus) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'reconnecting':
        return 'Reconnecting...';
      case 'disconnected':
        return 'Disconnected';
      default:
        return 'Unknown';
    }
  };

  const getStatusIcon = () => {
    if (isStreaming) return '🔄';
    switch (connectionStatus) {
      case 'connected':
        return '🟢';
      case 'connecting':
      case 'reconnecting':
        return '🟡';
      case 'disconnected':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const getLastHeartbeatText = () => {
    if (!lastHeartbeat) return '';
    const elapsed = Date.now() - lastHeartbeat;
    if (elapsed < 1000) return 'Just now';
    if (elapsed < 60000) return `${Math.floor(elapsed / 1000)}s ago`;
    return `${Math.floor(elapsed / 60000)}m ago`;
  };

  return (
    <div className={cn('flex items-center gap-3', className)}>
      <div className="flex items-center gap-2">
        <span className="text-sm">{getStatusIcon()}</span>
        <span className={cn('text-sm font-medium', getStatusColor())}>
          {getStatusText()}
        </span>
      </div>
      
      {lastHeartbeat && (
        <div className="text-xs cosmic-text-tertiary">
          Last heartbeat: {getLastHeartbeatText()}
        </div>
      )}
      
      {isStreaming && (
        <motion.div
          className="w-2 h-2 bg-cosmic-primary-500 rounded-full"
          animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      )}
    </div>
  );
};

export { TraceIdDisplay, StreamingStatus };
