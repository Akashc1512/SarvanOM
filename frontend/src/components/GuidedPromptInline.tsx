/**
 * Guided Prompt Inline Compact Bar Component
 * 
 * Compact inline refinement suggestions that appear below the search input.
 * Designed for desktop layouts where space is limited.
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Check, Edit3, X } from 'lucide-react';

interface RefinementSuggestion {
  id: string;
  title: string;
  description: string;
  refined_query: string;
  type: 'refine' | 'disambiguate' | 'decompose' | 'constrain' | 'sanitize';
  confidence: number;
  reasoning: string;
}

interface GuidedPromptInlineProps {
  originalQuery: string;
  refinements: RefinementSuggestion[];
  onAccept: (refinedQuery: string) => void;
  onEdit: (suggestion: RefinementSuggestion) => void;
  onSkip: () => void;
  onClose: () => void;
  isLoading?: boolean;
  error?: string;
}

export const GuidedPromptInline: React.FC<GuidedPromptInlineProps> = ({
  originalQuery,
  refinements,
  onAccept,
  onEdit,
  onSkip,
  onClose,
  isLoading = false,
  error
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState<RefinementSuggestion | null>(null);

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion: RefinementSuggestion) => {
    setSelectedSuggestion(suggestion);
  };

  // Handle accept
  const handleAccept = () => {
    if (selectedSuggestion) {
      onAccept(selectedSuggestion.refined_query);
    }
  };

  // Handle edit
  const handleEdit = () => {
    if (selectedSuggestion) {
      onEdit(selectedSuggestion);
    }
  };

  // Get type color
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'disambiguate': return 'text-blue-600';
      case 'decompose': return 'text-green-600';
      case 'constrain': return 'text-orange-600';
      case 'sanitize': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-2">
        <div className="flex items-center justify-between">
          <p className="text-red-800 text-sm">Failed to generate suggestions</p>
          <button
            onClick={onClose}
            className="text-red-600 hover:text-red-800 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-2">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
          <p className="text-blue-800 text-sm">Generating suggestions...</p>
        </div>
      </div>
    );
  }

  if (refinements.length === 0) {
    return null;
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg mt-2">
      {/* Compact header */}
      <div className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-blue-800 text-sm font-medium">💡 More specific?</span>
            <div className="flex space-x-1">
              {refinements.slice(0, 3).map((suggestion) => (
                <button
                  key={suggestion.id}
                  onClick={() => handleSuggestionSelect(suggestion)}
                  className={`px-2 py-1 text-xs rounded-full border transition-colors ${
                    selectedSuggestion?.id === suggestion.id
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:border-blue-300'
                  }`}
                >
                  {suggestion.title}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
              aria-label={isExpanded ? "Collapse" : "Expand"}
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            <button
              onClick={onClose}
              className="p-1 text-blue-600 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Quick actions */}
        {selectedSuggestion && (
          <div className="flex items-center space-x-2 mt-2">
            <button
              onClick={handleAccept}
              className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <Check className="w-3 h-3 mr-1 inline" />
              Use this
            </button>
            <button
              onClick={handleEdit}
              className="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              <Edit3 className="w-3 h-3 mr-1 inline" />
              Edit
            </button>
            <button
              onClick={onSkip}
              className="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Skip
            </button>
          </div>
        )}
      </div>

      {/* Expanded details */}
      {isExpanded && (
        <div className="border-t border-blue-200 p-3 bg-white rounded-b-lg">
          <div className="space-y-3">
            {refinements.map((suggestion) => (
              <div
                key={suggestion.id}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedSuggestion?.id === suggestion.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleSuggestionSelect(suggestion)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleSuggestionSelect(suggestion);
                  }
                }}
              >
                <div className="flex items-start space-x-3">
                  <div className={`p-1 rounded-full ${getTypeColor(suggestion.type)}`}>
                    <span className="text-xs font-medium">{suggestion.type}</span>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">{suggestion.title}</h4>
                    <p className="text-xs text-gray-600 mt-1">{suggestion.description}</p>
                    <p className="text-xs text-gray-500 mt-2 italic">"{suggestion.refined_query}"</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GuidedPromptInline;
