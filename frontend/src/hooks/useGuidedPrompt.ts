/**
 * useGuidedPrompt Hook
 * 
 * React hook for managing Guided Prompt Confirmation functionality.
 * Handles state management, API calls, and user interactions.
 */

import { useState, useCallback, useEffect } from 'react';

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
  type: 'select' | 'boolean';
  options: string[];
  selected?: string;
}

interface GuidedPromptData {
  originalQuery: string;
  refinements: RefinementSuggestion[];
  constraints: ConstraintChip[];
}

interface UseGuidedPromptReturn {
  isGuidedPromptEnabled: boolean;
  showGuidedPrompt: boolean;
  guidedPromptData: GuidedPromptData | null;
  isLoading: boolean;
  error: string | null;
  handleGuidedPromptAccept: (refinedQuery: string, constraints: ConstraintChip[]) => void;
  handleGuidedPromptEdit: (suggestion: RefinementSuggestion) => void;
  handleGuidedPromptSkip: () => void;
  handleGuidedPromptClose: () => void;
  triggerGuidedPrompt: (query: string) => Promise<void>;
}

export const useGuidedPrompt = (): UseGuidedPromptReturn => {
  const [isGuidedPromptEnabled, setIsGuidedPromptEnabled] = useState(true);
  const [showGuidedPrompt, setShowGuidedPrompt] = useState(false);
  const [guidedPromptData, setGuidedPromptData] = useState<GuidedPromptData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('sarvanom-settings');
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        setIsGuidedPromptEnabled(settings.enabled ?? true);
      } catch (error) {
        console.error('Failed to load guided prompt settings:', error);
      }
    }
  }, []);

  // Trigger guided prompt for a query
  const triggerGuidedPrompt = useCallback(async (query: string) => {
    if (!isGuidedPromptEnabled || !query.trim()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Call the guided prompt service
      const response = await fetch('/api/guided-prompt/refine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`Guided prompt service error: ${response.status}`);
      }

      const data = await response.json();
      
      setGuidedPromptData({
        originalQuery: query,
        refinements: data.refinements || [],
        constraints: data.constraints || []
      });
      
      setShowGuidedPrompt(true);
    } catch (error) {
      console.error('Failed to trigger guided prompt:', error);
      setError(error instanceof Error ? error.message : 'Failed to load guided prompt');
    } finally {
      setIsLoading(false);
    }
  }, [isGuidedPromptEnabled]);

  // Handle accepting a refinement
  const handleGuidedPromptAccept = useCallback((refinedQuery: string, constraints: ConstraintChip[]) => {
    // Record the acceptance
    console.log('Guided prompt accepted:', { refinedQuery, constraints });
    
    // Close the modal
    setShowGuidedPrompt(false);
    setGuidedPromptData(null);
    
    // You can emit analytics events here
    // analytics.track('guided_prompt_accepted', { originalQuery, refinedQuery, constraints });
  }, []);

  // Handle editing a suggestion
  const handleGuidedPromptEdit = useCallback((suggestion: RefinementSuggestion) => {
    console.log('Guided prompt edit requested:', suggestion);
    
    // You can emit analytics events here
    // analytics.track('guided_prompt_edit_requested', { suggestion });
  }, []);

  // Handle skipping guided prompt
  const handleGuidedPromptSkip = useCallback(() => {
    console.log('Guided prompt skipped');
    
    // Close the modal
    setShowGuidedPrompt(false);
    setGuidedPromptData(null);
    
    // You can emit analytics events here
    // analytics.track('guided_prompt_skipped', { originalQuery: guidedPromptData?.originalQuery });
  }, [guidedPromptData?.originalQuery]);

  // Handle closing the modal
  const handleGuidedPromptClose = useCallback(() => {
    setShowGuidedPrompt(false);
    setGuidedPromptData(null);
    setError(null);
  }, []);

  return {
    isGuidedPromptEnabled,
    showGuidedPrompt,
    guidedPromptData,
    isLoading,
    error,
    handleGuidedPromptAccept,
    handleGuidedPromptEdit,
    handleGuidedPromptSkip,
    handleGuidedPromptClose,
    triggerGuidedPrompt,
  };
};

export default useGuidedPrompt;