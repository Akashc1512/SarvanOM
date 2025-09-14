/**
 * Fallback Badge Component - SarvanOM v2
 * 
 * Displays fallback status badges for keyless lane responses with info tooltips.
 * Implements PR-5 requirements for fallback UX indicators.
 */

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Info, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useFrontendEvents } from '@/hooks/useFrontendEvents';

export interface FallbackBadgeProps {
  /** Whether this response used a fallback provider */
  fallbackUsed: boolean;
  /** Source type: 'keyed' | 'keyless' */
  source: 'keyed' | 'keyless';
  /** Provider name */
  provider: string;
  /** Lane type */
  lane: 'web_search' | 'news' | 'markets' | 'vector' | 'kg' | 'keyword';
  /** Trace ID for metrics */
  traceId?: string;
  /** Additional CSS classes */
  className?: string;
  /** Whether to show detailed tooltip */
  showTooltip?: boolean;
}

export function FallbackBadge({
  fallbackUsed,
  source,
  provider,
  lane,
  traceId,
  className,
  showTooltip = true
}: FallbackBadgeProps) {
  const [showInfo, setShowInfo] = useState(false);
  const { emitFallbackBadgeEvent } = useFrontendEvents();

  // Don't show badge if not using fallback
  if (!fallbackUsed) {
    return null;
  }

  // Determine badge appearance based on source
  const isKeyless = source === 'keyless';
  const badgeVariant = isKeyless ? 'warning' : 'info';
  
  const badgeConfig = {
    warning: {
      icon: AlertTriangle,
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      iconColor: 'text-yellow-600'
    },
    info: {
      icon: Info,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      iconColor: 'text-blue-600'
    }
  };

  const config = badgeConfig[badgeVariant];
  const Icon = config.icon;

  const handleBadgeClick = () => {
    if (showTooltip) {
      setShowInfo(!showInfo);
      
      // Emit frontend event for metrics
      emitFallbackBadgeEvent({
        trace_id: traceId,
        provider,
        lane,
        source,
        fallback_used: fallbackUsed
      });
    }
  };

  const getTooltipContent = () => {
    if (isKeyless) {
      return (
        <div className="space-y-2">
          <div className="font-medium text-yellow-900">ⓘ Via Fallback</div>
          <div className="text-sm text-yellow-800">
            This response used a keyless fallback provider ({provider}) because 
            no API keys were configured for the {lane.replace('_', ' ')} lane.
          </div>
          <div className="text-xs text-yellow-700">
            Configure API keys in Settings to use premium providers.
          </div>
        </div>
      );
    } else {
      return (
        <div className="space-y-2">
          <div className="font-medium text-blue-900">ⓘ Via Fallback</div>
          <div className="text-sm text-blue-800">
            This response used a fallback provider ({provider}) because the 
            primary provider was unavailable for the {lane.replace('_', ' ')} lane.
          </div>
        </div>
      );
    }
  };

  return (
    <div className="relative inline-block">
      <motion.button
        onClick={handleBadgeClick}
        className={cn(
          'inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium',
          'border transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-1',
          config.bgColor,
          config.borderColor,
          config.textColor,
          className
        )}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        aria-label={`Fallback badge for ${provider} provider`}
      >
        <Icon className={cn('w-3 h-3', config.iconColor)} />
        <span>ⓘ via fallback</span>
      </motion.button>

      <AnimatePresence>
        {showInfo && showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2',
              'w-64 p-3 rounded-lg shadow-lg border z-50',
              config.bgColor,
              config.borderColor
            )}
            role="tooltip"
          >
            {getTooltipContent()}
            
            {/* Tooltip arrow */}
            <div className={cn(
              'absolute top-full left-1/2 transform -translate-x-1/2',
              'w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent',
              `border-t-${isKeyless ? 'yellow' : 'blue'}-200`
            )} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * Provider Status Badge - Shows overall provider status
 */
export interface ProviderStatusBadgeProps {
  /** Provider name */
  provider: string;
  /** Whether provider is available */
  available: boolean;
  /** Whether provider is configured */
  configured: boolean;
  /** Additional CSS classes */
  className?: string;
}

export function ProviderStatusBadge({
  provider,
  available,
  configured,
  className
}: ProviderStatusBadgeProps) {
  const getStatusConfig = () => {
    if (configured && available) {
      return {
        icon: CheckCircle,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        textColor: 'text-green-800',
        iconColor: 'text-green-600',
        label: 'Active'
      };
    } else if (configured && !available) {
      return {
        icon: Clock,
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        textColor: 'text-yellow-800',
        iconColor: 'text-yellow-600',
        label: 'Unavailable'
      };
    } else {
      return {
        icon: AlertTriangle,
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        textColor: 'text-gray-600',
        iconColor: 'text-gray-500',
        label: 'Not Configured'
      };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className={cn(
      'inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium',
      'border',
      config.bgColor,
      config.borderColor,
      config.textColor,
      className
    )}>
      <Icon className={cn('w-3 h-3', config.iconColor)} />
      <span>{provider}</span>
      <span className="text-xs opacity-75">({config.label})</span>
    </div>
  );
}
