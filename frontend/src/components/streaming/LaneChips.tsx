'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface LaneStatus {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'timeout' | 'error';
  startTime?: number;
  endTime?: number;
  timeout?: number;
  result?: any;
  error?: string;
}

interface LaneChipsProps {
  lanes: LaneStatus[];
  className?: string;
}

const LaneChips: React.FC<LaneChipsProps> = ({ lanes, className }) => {
  const getStatusColor = (status: LaneStatus['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-cosmic-bg-secondary border-cosmic-border-primary text-cosmic-text-tertiary';
      case 'running':
        return 'bg-cosmic-primary-500/20 border-cosmic-primary-500 text-cosmic-primary-500 cosmic-glow-soft';
      case 'completed':
        return 'bg-cosmic-success/20 border-cosmic-success text-cosmic-success';
      case 'timeout':
        return 'bg-cosmic-warning/20 border-cosmic-warning text-cosmic-warning';
      case 'error':
        return 'bg-cosmic-error/20 border-cosmic-error text-cosmic-error';
      default:
        return 'bg-cosmic-bg-secondary border-cosmic-border-primary text-cosmic-text-tertiary';
    }
  };

  const getStatusIcon = (status: LaneStatus['status']) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'running':
        return '🔄';
      case 'completed':
        return '✅';
      case 'timeout':
        return '⏰';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  const calculateElapsedTime = (lane: LaneStatus) => {
    if (!lane.startTime) return 0;
    const endTime = lane.endTime || Date.now();
    return Math.round((endTime - lane.startTime) / 100) / 10; // Convert to seconds with 1 decimal
  };

  const getTimerColor = (lane: LaneStatus) => {
    const elapsed = calculateElapsedTime(lane);
    const timeout = lane.timeout || 3000; // Default 3s timeout
    
    if (lane.status === 'completed') return 'text-cosmic-success';
    if (lane.status === 'error') return 'text-cosmic-error';
    if (lane.status === 'timeout') return 'text-cosmic-warning';
    if (elapsed > timeout / 1000) return 'text-cosmic-warning';
    if (elapsed > timeout / 2000) return 'text-cosmic-primary-500';
    return 'text-cosmic-text-tertiary';
  };

  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {lanes.map((lane) => (
        <motion.div
          key={lane.id}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className={cn(
            'inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-all duration-200',
            getStatusColor(lane.status)
          )}
          title={`${lane.name}: ${lane.status}${lane.error ? ` - ${lane.error}` : ''}`}
        >
          <span className="text-xs">{getStatusIcon(lane.status)}</span>
          <span className="text-xs font-medium">{lane.name}</span>
          {lane.startTime && (
            <span className={cn('text-xs font-mono', getTimerColor(lane))}>
              {calculateElapsedTime(lane)}s
            </span>
          )}
          {lane.status === 'running' && (
            <motion.div
              className="w-2 h-2 bg-current rounded-full"
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
          )}
        </motion.div>
      ))}
    </div>
  );
};

interface LaneProgressProps {
  lanes: LaneStatus[];
  className?: string;
}

const LaneProgress: React.FC<LaneProgressProps> = ({ lanes, className }) => {
  const completedLanes = lanes.filter(lane => lane.status === 'completed').length;
  const totalLanes = lanes.length;
  const progress = totalLanes > 0 ? (completedLanes / totalLanes) * 100 : 0;

  return (
    <div className={cn('w-full', className)}>
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm cosmic-text-secondary">Processing Lanes</span>
        <span className="text-sm cosmic-text-primary font-mono">
          {completedLanes}/{totalLanes}
        </span>
      </div>
      <div className="w-full bg-cosmic-bg-secondary rounded-full h-2">
        <motion.div
          className="h-2 bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 rounded-full cosmic-glow-soft"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
};

interface PartialAnswerBannerProps {
  isVisible: boolean;
  completedLanes: number;
  totalLanes: number;
  onDismiss?: () => void;
  className?: string;
}

const PartialAnswerBanner: React.FC<PartialAnswerBannerProps> = ({
  isVisible,
  completedLanes,
  totalLanes,
  onDismiss,
  className
}) => {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className={cn(
            'cosmic-card border-cosmic-warning bg-cosmic-warning/10 p-4 mb-4',
            className
          )}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-cosmic-warning/20 rounded-full flex items-center justify-center">
                <span className="text-cosmic-warning text-sm">⚠️</span>
              </div>
              <div>
                <h4 className="text-sm font-medium cosmic-text-primary">
                  Partial Results Available
                </h4>
                <p className="text-xs cosmic-text-secondary">
                  {completedLanes} of {totalLanes} lanes completed. Some sources may still be loading.
                </p>
              </div>
            </div>
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="cosmic-btn-ghost p-1 text-cosmic-text-tertiary hover:text-cosmic-text-primary"
                aria-label="Dismiss banner"
              >
                <span className="text-sm">×</span>
              </button>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

interface TTFTIndicatorProps {
  ttft?: number;
  target?: number;
  className?: string;
}

const TTFTIndicator: React.FC<TTFTIndicatorProps> = ({
  ttft,
  target = 800,
  className
}) => {
  const isGood = ttft && ttft <= target;
  const isWarning = ttft && ttft <= target * 1.5;
  const isSlow = ttft && ttft > target * 1.5;

  const getColor = () => {
    if (isGood) return 'text-cosmic-success';
    if (isWarning) return 'text-cosmic-warning';
    if (isSlow) return 'text-cosmic-error';
    return 'text-cosmic-text-tertiary';
  };

  const getProgress = () => {
    if (!ttft) return 0;
    return Math.min((ttft / target) * 100, 100);
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className="text-xs cosmic-text-secondary">TTFT:</span>
      <div className="flex items-center gap-1">
        <div className="w-16 bg-cosmic-bg-secondary rounded-full h-1">
          <motion.div
            className={cn(
              'h-1 rounded-full',
              isGood ? 'bg-cosmic-success' : isWarning ? 'bg-cosmic-warning' : 'bg-cosmic-error'
            )}
            initial={{ width: 0 }}
            animate={{ width: `${getProgress()}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
        <span className={cn('text-xs font-mono', getColor())}>
          {ttft ? `${ttft}ms` : '--'}
        </span>
      </div>
    </div>
  );
};

export { LaneChips, LaneProgress, PartialAnswerBanner, TTFTIndicator };
