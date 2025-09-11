/**
 * Guided Prompt Confirmation Modal Component
 * 
 * A11y-first, keyboard/screen-reader ready modal for guided prompt confirmation.
 * Supports modal, inline compact bar, and mobile sheet layouts.
 * Default ON, toggleable, with constraint chips and refinement suggestions.
 */

import React, { useState, useEffect, useRef } from 'react';
import { X, Edit3, SkipForward, Check, AlertCircle, Clock, Globe, FileText, Settings, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { designTokens } from '@/lib/design-tokens';
import RefinementSuggestion from './guided-prompt/RefinementSuggestion';
import ConstraintChip from './guided-prompt/ConstraintChip';

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

interface GuidedPromptModalProps {
  isOpen: boolean;
  originalQuery: string;
  refinements: RefinementSuggestion[];
  constraints: ConstraintChip[];
  onAccept: (refinedQuery: string, constraints: ConstraintChip[]) => void;
  onEdit: (suggestion: RefinementSuggestion) => void;
  onSkip: () => void;
  onClose: () => void;
  isLoading?: boolean;
  error?: string;
  deviceType?: 'desktop' | 'mobile';
  language?: string;
}

export const GuidedPromptModal: React.FC<GuidedPromptModalProps> = ({
  isOpen,
  originalQuery,
  refinements,
  constraints,
  onAccept,
  onEdit,
  onSkip,
  onClose,
  isLoading = false,
  error,
  deviceType = 'desktop',
  language = 'en'
}) => {
  const [selectedSuggestion, setSelectedSuggestion] = useState<RefinementSuggestion | null>(null);
  const [selectedConstraints, setSelectedConstraints] = useState<ConstraintChip[]>(constraints);
  const [isEditing, setIsEditing] = useState(false);
  const [editQuery, setEditQuery] = useState('');
  
  const modalRef = useRef<HTMLDivElement>(null);
  const firstButtonRef = useRef<HTMLButtonElement>(null);

  // Focus management for accessibility
  useEffect(() => {
    if (isOpen && firstButtonRef.current) {
      firstButtonRef.current.focus();
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Handle constraint selection
  const handleConstraintChange = (constraintId: string, value: string) => {
    setSelectedConstraints(prev => 
      prev.map(constraint => 
        constraint.id === constraintId 
          ? { ...constraint, selected: value }
          : constraint
      )
    );
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion: RefinementSuggestion) => {
    setSelectedSuggestion(suggestion);
    setEditQuery(suggestion.refined_query);
  };

  // Handle accept
  const handleAccept = () => {
    if (selectedSuggestion) {
      onAccept(selectedSuggestion.refined_query, selectedConstraints);
    }
  };

  // Handle edit
  const handleEdit = () => {
    if (selectedSuggestion) {
      setIsEditing(true);
      onEdit(selectedSuggestion);
    }
  };

  // Handle edit confirm
  const handleEditConfirm = () => {
    if (editQuery.trim()) {
      onAccept(editQuery, selectedConstraints);
    }
  };

  // Handle edit cancel
  const handleEditCancel = () => {
    setIsEditing(false);
    setEditQuery(selectedSuggestion?.refined_query || '');
  };

  // Get type icon
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'disambiguate': return <AlertCircle className="w-4 h-4" />;
      case 'decompose': return <FileText className="w-4 h-4" />;
      case 'constrain': return <Clock className="w-4 h-4" />;
      case 'sanitize': return <AlertCircle className="w-4 h-4" />;
      default: return <Globe className="w-4 h-4" />;
    }
  };

  // Get type color
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'disambiguate': return 'text-blue-600 bg-blue-50';
      case 'decompose': return 'text-green-600 bg-green-50';
      case 'constrain': return 'text-orange-600 bg-orange-50';
      case 'sanitize': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (!isOpen) return null;

  // Mobile sheet layout
  if (deviceType === 'mobile') {
    return (
      <div className="fixed inset-0 z-50 flex items-end justify-center">
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
        
        {/* Mobile sheet */}
        <div 
          ref={modalRef}
          className="relative w-full max-w-md bg-white rounded-t-lg shadow-xl transform transition-transform"
          role="dialog"
          aria-modal="true"
          aria-labelledby="guided-prompt-title"
        >
          <div className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h2 id="guided-prompt-title" className="text-lg font-semibold text-gray-900">
                Guided Prompt
              </h2>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="space-y-4">
              {/* Original query */}
              <div>
                <p className="text-sm text-gray-600 mb-2">Your query:</p>
                <p className="text-gray-900 bg-gray-50 p-3 rounded-lg">
                  "{originalQuery}"
                </p>
              </div>

              {/* Loading state */}
              {isLoading && (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Generating suggestions...</span>
                </div>
              )}

              {/* Error state */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                    <p className="text-red-800">{error}</p>
                  </div>
                </div>
              )}

              {/* Refinement suggestions */}
              {!isLoading && !error && refinements.length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-3">💡 I can help you be more specific:</p>
                  <div className="space-y-3">
                    {refinements.map((suggestion) => (
                      <div
                        key={suggestion.id}
                        className={`p-4 border rounded-lg cursor-pointer transition-colors ${
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
                            {getTypeIcon(suggestion.type)}
                          </div>
                          <div className="flex-1">
                            <h3 className="font-medium text-gray-900">{suggestion.title}</h3>
                            <p className="text-sm text-gray-600 mt-1">{suggestion.description}</p>
                            <p className="text-sm text-gray-500 mt-2 italic">"{suggestion.refined_query}"</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Constraints */}
              {!isLoading && !error && constraints.length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-3">Add constraints:</p>
                  <div className="flex flex-wrap gap-2">
                    {constraints.map((constraint) => (
                      <div key={constraint.id} className="flex items-center space-x-2">
                        <label className="text-sm text-gray-700">{constraint.label}:</label>
                        <select
                          value={constraint.selected || ''}
                          onChange={(e) => handleConstraintChange(constraint.id, e.target.value)}
                          className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select...</option>
                          {constraint.options.map((option) => (
                            <option key={option} value={option}>{option}</option>
                          ))}
                        </select>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Edit mode */}
              {isEditing && (
                <div>
                  <p className="text-sm text-gray-600 mb-2">Edit your query:</p>
                  <textarea
                    value={editQuery}
                    onChange={(e) => setEditQuery(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Enter your refined query..."
                  />
                  <div className="flex space-x-2 mt-2">
                    <button
                      onClick={handleEditConfirm}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <Check className="w-4 h-4 mr-1 inline" />
                      Confirm
                    </button>
                    <button
                      onClick={handleEditCancel}
                      className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Actions */}
              {!isLoading && !error && !isEditing && (
                <div className="flex space-x-2 pt-4">
                  <button
                    ref={firstButtonRef}
                    onClick={handleAccept}
                    disabled={!selectedSuggestion}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Check className="w-4 h-4 mr-1 inline" />
                    Looks good → Run
                  </button>
                  <button
                    onClick={handleEdit}
                    disabled={!selectedSuggestion}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={onSkip}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    <SkipForward className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Desktop modal layout
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Modal */}
      <div 
        ref={modalRef}
        className="relative w-full max-w-2xl bg-white rounded-lg shadow-xl transform transition-transform"
        role="dialog"
        aria-modal="true"
        aria-labelledby="guided-prompt-title"
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h2 id="guided-prompt-title" className="text-xl font-semibold text-gray-900">
              Guided Prompt Confirmation
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="space-y-6">
            {/* Original query */}
            <div>
              <p className="text-sm text-gray-600 mb-2">Your query:</p>
              <p className="text-gray-900 bg-gray-50 p-4 rounded-lg">
                "{originalQuery}"
              </p>
            </div>

            {/* Loading state */}
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Generating suggestions...</span>
              </div>
            )}

            {/* Error state */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <p className="text-red-800">{error}</p>
                </div>
              </div>
            )}

            {/* Refinement suggestions */}
            {!isLoading && !error && refinements.length > 0 && (
              <div>
                <p className="text-sm text-gray-600 mb-4">💡 I can help you be more specific:</p>
                <div className="grid gap-4">
                  {refinements.map((suggestion) => (
                    <div
                      key={suggestion.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
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
                        <div className={`p-2 rounded-full ${getTypeColor(suggestion.type)}`}>
                          {getTypeIcon(suggestion.type)}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">{suggestion.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{suggestion.description}</p>
                          <p className="text-sm text-gray-500 mt-2 italic">"{suggestion.refined_query}"</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Constraints */}
            {!isLoading && !error && constraints.length > 0 && (
              <div>
                <p className="text-sm text-gray-600 mb-3">Add constraints:</p>
                <div className="flex flex-wrap gap-4">
                  {constraints.map((constraint) => (
                    <div key={constraint.id} className="flex items-center space-x-2">
                      <label className="text-sm text-gray-700">{constraint.label}:</label>
                      <select
                        value={constraint.selected || ''}
                        onChange={(e) => handleConstraintChange(constraint.id, e.target.value)}
                        className="text-sm border border-gray-300 rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select...</option>
                        {constraint.options.map((option) => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Edit mode */}
            {isEditing && (
              <div>
                <p className="text-sm text-gray-600 mb-2">Edit your query:</p>
                <textarea
                  value={editQuery}
                  onChange={(e) => setEditQuery(e.target.value)}
                  className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder="Enter your refined query..."
                />
                <div className="flex space-x-3 mt-3">
                  <button
                    onClick={handleEditConfirm}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <Check className="w-4 h-4 mr-1 inline" />
                    Confirm
                  </button>
                  <button
                    onClick={handleEditCancel}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Actions */}
            {!isLoading && !error && !isEditing && (
              <div className="flex space-x-3 pt-4">
                <button
                  ref={firstButtonRef}
                  onClick={handleAccept}
                  disabled={!selectedSuggestion}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Check className="w-4 h-4 mr-2 inline" />
                  Looks good → Run
                </button>
                <button
                  onClick={handleEdit}
                  disabled={!selectedSuggestion}
                  className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Edit3 className="w-4 h-4 mr-2 inline" />
                  Edit
                </button>
                <button
                  onClick={onSkip}
                  className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  <SkipForward className="w-4 h-4 mr-2 inline" />
                  Skip refinement
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GuidedPromptModal;
