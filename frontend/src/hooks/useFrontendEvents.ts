/**
 * Frontend Events Hook - SarvanOM v2
 * 
 * Emits frontend events for metrics tracking as specified in PR-5.
 * Handles fallback badge interactions and guided prompt events.
 */

'use client';

import { useCallback } from 'react';

export interface FrontendEvent {
  event_name: string;
  trace_id?: string;
  [key: string]: any;
}

export interface FallbackBadgeEvent extends FrontendEvent {
  event_name: 'fallback_badge_seen';
  provider: string;
  lane: string;
  source: 'keyed' | 'keyless';
  fallback_used: boolean;
}

export interface GuidedPromptEvent extends FrontendEvent {
  event_name: 'guided_refine_shown' | 'guided_refine_accept' | 'guided_refine_edit' | 'guided_refine_skip';
  refinement_type?: string;
  budget_exceeded?: boolean;
  user_action?: 'accept' | 'edit' | 'skip';
}

export function useFrontendEvents() {
  const emitEvent = useCallback((event: FrontendEvent) => {
    try {
      // Emit to Google Analytics if available
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', event.event_name, {
          trace_id: event.trace_id,
          ...event
        });
      }

      // Emit to custom analytics endpoint
      if (typeof window !== 'undefined' && window.fetch) {
        fetch('/api/analytics/events', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...event,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            url: window.location.href
          })
        }).catch(error => {
          console.warn('Failed to emit frontend event:', error);
        });
      }

      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log('Frontend Event:', event);
      }
    } catch (error) {
      console.warn('Failed to emit frontend event:', error);
    }
  }, []);

  const emitFallbackBadgeEvent = useCallback((event: Omit<FallbackBadgeEvent, 'event_name'>) => {
    emitEvent({
      event_name: 'fallback_badge_seen',
      ...event
    });
  }, [emitEvent]);

  const emitGuidedPromptEvent = useCallback((event: Omit<GuidedPromptEvent, 'event_name'>) => {
    emitEvent({
      event_name: event.user_action ? `guided_refine_${event.user_action}` : 'guided_refine_shown',
      ...event
    });
  }, [emitEvent]);

  return {
    emitEvent,
    emitFallbackBadgeEvent,
    emitGuidedPromptEvent
  };
}

// Global type declarations for gtag
declare global {
  interface Window {
    gtag?: (...args: any[]) => void;
  }
}
