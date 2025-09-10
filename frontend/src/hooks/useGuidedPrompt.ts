/**
 * Guided Prompt Hook
 * 
 * Custom hook for managing Guided Prompt Confirmation state and interactions.
 * Handles API calls, state management, and user preferences.
 */

import { useState, useEffect, useCallback } from 'react';

interface RefinementSuggestion {
  id: string;
  title: string;
  description: string;
  refined_query: string;
  type: 'refine' | 'disambiguate' | 'decompose' | 'constrain' | 'sanitize';
  confidence: number;
  reasoning: string;
}

interface ConstraintChip {
  id: string;
  label: string;
  type: 'select' | 'boolean' | 'range' | 'multi-select';
  options: string[];
  selected?: string | string[];
}

interface RefinementResult {
  should_trigger: boolean;
  suggestions: RefinementSuggestion[];
  constraints: ConstraintChip[];
  latency_ms: number;
  model_used: string;
  cost_usd: number;
  bypass_reason?: string;
}

interface GuidedPromptSettings {
  enabled: boolean;
  mode: 'ON' | 'OFF' | 'BYPASS_ONCE' | 'ALWAYS_BYPASS';
  preferences: {
    show_hints: boolean;
    auto_learn: boolean;
    constraint_chips: boolean;
    accessibility_mode: boolean;
  };
}

interface UseGuidedPromptOptions {
  userId?: string;
  sessionId?: string;
  deviceType?: 'desktop' | 'mobile';
  language?: string;
  onRefinementComplete?: (refinedQuery: string, constraints: ConstraintChip[]) => void;
  onRefinementSkip?: () => void;
}

export const useGuidedPrompt = (options: UseGuidedPromptOptions = {}) => {
  const {
    userId = 'anonymous',
    sessionId = 'default',
    deviceType = 'desktop',
    language = 'en',
    onRefinementComplete,
    onRefinementSkip
  } = options;

  // State
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [originalQuery, setOriginalQuery] = useState('');
  const [refinements, setRefinements] = useState<RefinementSuggestion[]>([]);
  const [constraints, setConstraints] = useState<ConstraintChip[]>([]);
  const [settings, setSettings] = useState<GuidedPromptSettings>({
    enabled: true,
    mode: 'ON',
    preferences: {
      show_hints: true,
      auto_learn: true,
      constraint_chips: true,
      accessibility_mode: false
    }
  });

  // Load user settings on mount
  useEffect(() => {
    loadUserSettings();
  }, [userId]);

  // Load user settings
  const loadUserSettings = async () => {
    try {
      const response = await fetch(`/api/guided-prompt/settings/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setSettings(data.settings);
      }
    } catch (error) {
      console.error('Failed to load user settings:', error);
    }
  };

  // Save user settings
  const saveUserSettings = async (newSettings: GuidedPromptSettings) => {
    try {
      const response = await fetch(`/api/guided-prompt/settings/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ settings: newSettings }),
      });
      
      if (response.ok) {
        setSettings(newSettings);
      }
    } catch (error) {
      console.error('Failed to save user settings:', error);
    }
  };

  // Process query for refinement
  const processQuery = useCallback(async (query: string, context: Record<string, any> = {}) => {
    // Check if refinement should be triggered
    if (!shouldTriggerRefinement(query, context)) {
      return { should_trigger: false, bypass_reason: 'user_preference_or_confidence' };
    }

    setIsLoading(true);
    setError(null);
    setOriginalQuery(query);

    try {
      const response = await fetch('/api/guided-prompt/refine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          context: {
            user_id: userId,
            session_id: sessionId,
            device_type: deviceType,
            language,
            ...context
          }
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: RefinementResult = await response.json();
      
      if (result.should_trigger) {
        setRefinements(result.suggestions);
        setConstraints(result.constraints);
        setIsOpen(true);
      }

      return result;
    } catch (error) {
      console.error('Failed to process query:', error);
      setError(error instanceof Error ? error.message : 'Failed to process query');
      return { should_trigger: false, bypass_reason: 'api_error' };
    } finally {
      setIsLoading(false);
    }
  }, [userId, sessionId, deviceType, language]);

  // Check if refinement should be triggered
  const shouldTriggerRefinement = (query: string, context: Record<string, any>) => {
    // Check user settings
    if (settings.mode === 'OFF' || settings.mode === 'ALWAYS_BYPASS') {
      return false;
    }

    // Check session bypass
    if (settings.mode === 'BYPASS_ONCE') {
      return false;
    }

    // Check for bypass keywords
    const bypassKeywords = ['skip', 'bypass', 'direct', 'immediate'];
    if (bypassKeywords.some(keyword => query.toLowerCase().includes(keyword))) {
      return false;
    }

    // Check intent confidence
    const intentConfidence = context.intent_confidence || 0.5;
    if (intentConfidence > 0.8) {
      return false;
    }

    // Check budget constraints
    const budgetRemaining = context.budget_remaining || 1.0;
    if (budgetRemaining < 0.25) {
      return false;
    }

    return true;
  };

  // Handle refinement acceptance
  const handleAccept = useCallback((refinedQuery: string, selectedConstraints: ConstraintChip[]) => {
    // Record feedback
    recordFeedback('accepted', refinedQuery);
    
    // Close modal
    setIsOpen(false);
    
    // Call completion callback
    onRefinementComplete?.(refinedQuery, selectedConstraints);
  }, [onRefinementComplete]);

  // Handle refinement edit
  const handleEdit = useCallback((suggestion: RefinementSuggestion) => {
    // Record feedback
    recordFeedback('edited', suggestion.refined_query);
  }, []);

  // Handle refinement skip
  const handleSkip = useCallback(() => {
    // Record feedback
    recordFeedback('skipped', originalQuery);
    
    // Close modal
    setIsOpen(false);
    
    // Call skip callback
    onRefinementSkip?.();
  }, [originalQuery, onRefinementSkip]);

  // Handle modal close
  const handleClose = useCallback(() => {
    setIsOpen(false);
    setError(null);
  }, []);

  // Record user feedback
  const recordFeedback = async (action: 'accepted' | 'edited' | 'skipped', query: string) => {
    try {
      await fetch('/api/guided-prompt/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          action,
          query,
          timestamp: new Date().toISOString()
        }),
      });
    } catch (error) {
      console.error('Failed to record feedback:', error);
    }
  };

  // Update constraint selection
  const updateConstraint = useCallback((constraintId: string, value: string | string[]) => {
    setConstraints(prev => 
      prev.map(constraint => 
        constraint.id === constraintId 
          ? { ...constraint, selected: value }
          : constraint
      )
    );
  }, []);

  // Remove constraint
  const removeConstraint = useCallback((constraintId: string) => {
    setConstraints(prev => 
      prev.map(constraint => 
        constraint.id === constraintId 
          ? { ...constraint, selected: undefined }
          : constraint
      )
    );
  }, []);

  return {
    // State
    isOpen,
    isLoading,
    error,
    originalQuery,
    refinements,
    constraints,
    settings,
    
    // Actions
    processQuery,
    handleAccept,
    handleEdit,
    handleSkip,
    handleClose,
    updateConstraint,
    removeConstraint,
    saveUserSettings,
    
    // Utilities
    shouldTriggerRefinement
  };
};

export default useGuidedPrompt;
