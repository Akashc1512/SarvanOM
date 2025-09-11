/**
 * Refinement Suggestion Component
 * 
 * Displays individual refinement suggestions with confidence scores,
 * reasoning, and interactive elements for the Guided Prompt system.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Edit3, Check, AlertCircle, Clock, Globe, FileText, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { designTokens } from '@/lib/design-tokens';

interface RefinementSuggestionProps {
  suggestion: {
    id: string;
    title: string;
    description: string;
    refined_query: string;
    type: 'refine' | 'disambiguate' | 'decompose' | 'constrain' | 'sanitize';
    confidence: number;
    reasoning: string;
  };
  isSelected: boolean;
  onSelect: () => void;
  onEdit: () => void;
  onAccept: () => void;
  isLoading?: boolean;
  className?: string;
}

const typeIcons = {
  refine: Edit3,
  disambiguate: AlertCircle,
  decompose: FileText,
  constrain: Globe,
  sanitize: Zap,
};

const typeColors = {
  refine: 'text-blue-600 bg-blue-50 border-blue-200',
  disambiguate: 'text-amber-600 bg-amber-50 border-amber-200',
  decompose: 'text-purple-600 bg-purple-50 border-purple-200',
  constrain: 'text-green-600 bg-green-50 border-green-200',
  sanitize: 'text-red-600 bg-red-50 border-red-200',
};

const confidenceColors = {
  high: 'text-green-600 bg-green-100',
  medium: 'text-yellow-600 bg-yellow-100',
  low: 'text-red-600 bg-red-100',
};

export const RefinementSuggestion: React.FC<RefinementSuggestionProps> = ({
  suggestion,
  isSelected,
  onSelect,
  onEdit,
  onAccept,
  isLoading = false,
  className,
}) => {
  const Icon = typeIcons[suggestion.type];
  const typeColor = typeColors[suggestion.type];
  
  const getConfidenceLevel = (confidence: number) => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
  };
  
  const confidenceLevel = getConfidenceLevel(suggestion.confidence);
  const confidenceColor = confidenceColors[confidenceLevel];

  return (
    <motion.div
      className={cn(
        'relative p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer',
        'hover:shadow-md hover:scale-[1.02]',
        isSelected 
          ? 'border-blue-500 bg-blue-50 shadow-md' 
          : 'border-gray-200 bg-white hover:border-gray-300',
        className
      )}
      onClick={onSelect}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={cn(
            'p-2 rounded-lg border',
            typeColor
          )}>
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">
              {suggestion.title}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={cn(
                'px-2 py-1 rounded-full text-xs font-medium',
                confidenceColor
              )}>
                {Math.round(suggestion.confidence * 100)}% confidence
              </span>
              <span className="text-xs text-gray-500 capitalize">
                {suggestion.type}
              </span>
            </div>
          </div>
        </div>
        
        {isSelected && (
          <motion.div
            className="flex items-center gap-1"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2 }}
          >
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-100 rounded-md transition-colors"
              aria-label="Edit suggestion"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onAccept();
              }}
              disabled={isLoading}
              className="p-1.5 text-gray-600 hover:text-green-600 hover:bg-green-100 rounded-md transition-colors disabled:opacity-50"
              aria-label="Accept suggestion"
            >
              <Check className="w-4 h-4" />
            </button>
          </motion.div>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-gray-700 mb-3">
        {suggestion.description}
      </p>

      {/* Refined Query Preview */}
      <div className="bg-gray-50 rounded-md p-3 mb-3">
        <p className="text-sm font-medium text-gray-900 mb-1">
          Refined Query:
        </p>
        <p className="text-sm text-gray-700 italic">
          "{suggestion.refined_query}"
        </p>
      </div>

      {/* Reasoning */}
      <div className="bg-blue-50 rounded-md p-3">
        <p className="text-xs font-medium text-blue-900 mb-1">
          Reasoning:
        </p>
        <p className="text-xs text-blue-800">
          {suggestion.reasoning}
        </p>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <motion.div
          className="absolute inset-0 bg-white bg-opacity-75 rounded-lg flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="flex items-center gap-2 text-blue-600">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm font-medium">Processing...</span>
          </div>
        </motion.div>
      )}

      {/* Selection Indicator */}
      {isSelected && (
        <motion.div
          className="absolute -top-1 -right-1 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.2 }}
        >
          <Check className="w-4 h-4 text-white" />
        </motion.div>
      )}
    </motion.div>
  );
};

export default RefinementSuggestion;
