/**
 * Constraint Chip Component
 * 
 * Interactive chips for adding constraints to queries.
 * Supports time range, sources, citations, cost ceiling, and depth constraints.
 */

import React, { useState } from 'react';
import { Clock, Globe, FileText, DollarSign, Layers, Check, X } from 'lucide-react';

interface ConstraintChipProps {
  id: string;
  label: string;
  type: 'select' | 'boolean' | 'range' | 'multi-select';
  options: string[];
  selected?: string | string[];
  onToggle: (id: string, value: string | string[]) => void;
  onRemove?: (id: string) => void;
  disabled?: boolean;
  required?: boolean;
}

export const ConstraintChip: React.FC<ConstraintChipProps> = ({
  id,
  label,
  type,
  options,
  selected,
  onToggle,
  onRemove,
  disabled = false,
  required = false
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Get icon for constraint type
  const getIcon = () => {
    switch (id) {
      case 'time_range': return <Clock className="w-4 h-4" />;
      case 'sources': return <Globe className="w-4 h-4" />;
      case 'citations': return <FileText className="w-4 h-4" />;
      case 'cost_ceiling': return <DollarSign className="w-4 h-4" />;
      case 'depth': return <Layers className="w-4 h-4" />;
      default: return <Check className="w-4 h-4" />;
    }
  };

  // Get color for constraint type
  const getColor = () => {
    switch (id) {
      case 'time_range': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'sources': return 'text-green-600 bg-green-50 border-green-200';
      case 'citations': return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'cost_ceiling': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'depth': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  // Handle option selection
  const handleOptionSelect = (option: string) => {
    if (type === 'multi-select') {
      const currentSelected = Array.isArray(selected) ? selected : [];
      const newSelected = currentSelected.includes(option)
        ? currentSelected.filter(item => item !== option)
        : [...currentSelected, option];
      onToggle(id, newSelected);
    } else {
      onToggle(id, option);
      setIsOpen(false);
    }
  };

  // Handle boolean toggle
  const handleBooleanToggle = () => {
    const newValue = selected === 'Yes' ? 'No' : 'Yes';
    onToggle(id, newValue);
  };

  // Get display text
  const getDisplayText = () => {
    if (type === 'multi-select' && Array.isArray(selected)) {
      if (selected.length === 0) return label;
      if (selected.length === 1) return `${label}: ${selected[0]}`;
      return `${label}: ${selected.length} selected`;
    }
    
    if (selected) {
      return `${label}: ${selected}`;
    }
    
    return label;
  };

  // Check if constraint is active
  const isActive = () => {
    if (type === 'multi-select') {
      return Array.isArray(selected) && selected.length > 0;
    }
    return selected && selected !== 'No';
  };

  return (
    <div className="relative">
      {/* Constraint chip */}
      <div
        className={`inline-flex items-center space-x-2 px-3 py-2 rounded-full border cursor-pointer transition-colors ${
          isActive() 
            ? `${getColor()} border-opacity-100` 
            : 'text-gray-600 bg-gray-50 border-gray-200 hover:border-gray-300'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        onClick={() => {
          if (disabled) return;
          if (type === 'boolean') {
            handleBooleanToggle();
          } else {
            setIsOpen(!isOpen);
          }
        }}
        role="button"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (disabled) return;
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (type === 'boolean') {
              handleBooleanToggle();
            } else {
              setIsOpen(!isOpen);
            }
          }
        }}
      >
        {getIcon()}
        <span className="text-sm font-medium">{getDisplayText()}</span>
        {required && <span className="text-red-500">*</span>}
        
        {/* Remove button */}
        {onRemove && isActive() && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRemove(id);
            }}
            className="ml-1 p-1 hover:bg-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-gray-500"
            aria-label="Remove constraint"
          >
            <X className="w-3 h-3" />
          </button>
        )}
      </div>

      {/* Dropdown options */}
      {isOpen && type !== 'boolean' && (
        <div className="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
          <div className="py-1">
            {options.map((option) => {
              const isSelected = type === 'multi-select' 
                ? Array.isArray(selected) && selected.includes(option)
                : selected === option;
              
              return (
                <button
                  key={option}
                  onClick={() => handleOptionSelect(option)}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 focus:outline-none focus:bg-gray-50 ${
                    isSelected ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    {type === 'multi-select' && (
                      <div className={`w-4 h-4 border rounded ${
                        isSelected ? 'bg-blue-600 border-blue-600' : 'border-gray-300'
                      }`}>
                        {isSelected && <Check className="w-3 h-3 text-white" />}
                      </div>
                    )}
                    <span>{option}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConstraintChip;
