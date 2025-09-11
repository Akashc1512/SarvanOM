/**
 * Constraint Chip Component
 * 
 * Interactive constraint selection chips for the Guided Prompt system.
 * Supports both select and boolean constraint types with accessibility features.
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check, X, Clock, Globe, FileText, DollarSign } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ConstraintChipProps {
  constraint: {
    id: string;
    label: string;
    type: 'select' | 'boolean';
    options: string[];
    selected?: string;
    description?: string;
    icon?: string;
  };
  onSelectionChange: (constraintId: string, value: string) => void;
  onRemove?: (constraintId: string) => void;
  isRequired?: boolean;
  className?: string;
}

const constraintIcons = {
  time: Clock,
  region: Globe,
  sources: FileText,
  cost: DollarSign,
  default: FileText,
};

export const ConstraintChip: React.FC<ConstraintChipProps> = ({
  constraint,
  onSelectionChange,
  onRemove,
  isRequired = false,
  className,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(constraint.selected || '');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Get icon component
  const IconComponent = constraintIcons[constraint.icon as keyof typeof constraintIcons] || constraintIcons.default;

  // Handle outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle keyboard navigation
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      setIsOpen(false);
      buttonRef.current?.focus();
    }
  };

  const handleOptionSelect = (option: string) => {
    setSelectedValue(option);
    onSelectionChange(constraint.id, option);
    setIsOpen(false);
    buttonRef.current?.focus();
  };

  const handleBooleanToggle = () => {
    const newValue = selectedValue === 'true' ? 'false' : 'true';
    setSelectedValue(newValue);
    onSelectionChange(constraint.id, newValue);
  };

  const handleRemove = () => {
    if (onRemove && !isRequired) {
      onRemove(constraint.id);
    }
  };

  return (
    <div className={cn('relative', className)}>
      {/* Constraint Chip */}
      <motion.div
        className={cn(
          'inline-flex items-center gap-2 px-3 py-2 rounded-full border-2 transition-all duration-200',
          'hover:shadow-md hover:scale-105',
          selectedValue 
            ? 'border-blue-500 bg-blue-50 text-blue-900' 
            : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400',
          isRequired && 'border-orange-300 bg-orange-50'
        )}
        whileHover={{ y: -1 }}
        whileTap={{ scale: 0.95 }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
      >
        {/* Icon */}
        <IconComponent className="w-4 h-4 flex-shrink-0" />
        
        {/* Label */}
        <span className="text-sm font-medium">
          {constraint.label}
        </span>

        {/* Selection Display */}
        {constraint.type === 'select' ? (
          <button
            ref={buttonRef}
            onClick={() => setIsOpen(!isOpen)}
            onKeyDown={handleKeyDown}
            className={cn(
              'flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium transition-colors',
              selectedValue 
                ? 'bg-blue-100 text-blue-800' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
            aria-expanded={isOpen}
            aria-haspopup="listbox"
            aria-label={`Select ${constraint.label}`}
          >
            <span>
              {selectedValue || 'Select...'}
            </span>
            <ChevronDown className={cn(
              'w-3 h-3 transition-transform duration-200',
              isOpen && 'rotate-180'
            )} />
          </button>
        ) : (
          <button
            onClick={handleBooleanToggle}
            className={cn(
              'flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium transition-colors',
              selectedValue === 'true'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            )}
            aria-pressed={selectedValue === 'true'}
            aria-label={`Toggle ${constraint.label}`}
          >
            <span>
              {selectedValue === 'true' ? 'Yes' : 'No'}
            </span>
            <Check className={cn(
              'w-3 h-3 transition-opacity duration-200',
              selectedValue === 'true' ? 'opacity-100' : 'opacity-0'
            )} />
          </button>
        )}

        {/* Remove Button */}
        {onRemove && !isRequired && (
          <button
            onClick={handleRemove}
            className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-100 rounded-full transition-colors"
            aria-label={`Remove ${constraint.label} constraint`}
          >
            <X className="w-3 h-3" />
          </button>
        )}

        {/* Required Indicator */}
        {isRequired && (
          <span className="text-xs text-orange-600 font-medium">
            Required
          </span>
        )}
      </motion.div>

      {/* Description Tooltip */}
      {constraint.description && (
        <div className="absolute top-full left-0 mt-1 px-2 py-1 bg-gray-900 text-white text-xs rounded-md opacity-0 hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
          {constraint.description}
        </div>
      )}

      {/* Dropdown Options */}
      <AnimatePresence>
        {isOpen && constraint.type === 'select' && (
          <motion.div
            ref={dropdownRef}
            className="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-20"
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            role="listbox"
            aria-label={`${constraint.label} options`}
          >
            {constraint.options.map((option, index) => (
              <motion.button
                key={option}
                onClick={() => handleOptionSelect(option)}
                className={cn(
                  'w-full px-3 py-2 text-left text-sm transition-colors',
                  'hover:bg-gray-50 focus:bg-gray-50 focus:outline-none',
                  'first:rounded-t-lg last:rounded-b-lg',
                  selectedValue === option && 'bg-blue-50 text-blue-900'
                )}
                role="option"
                aria-selected={selectedValue === option}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.1, delay: index * 0.05 }}
              >
                <div className="flex items-center justify-between">
                  <span>{option}</span>
                  {selectedValue === option && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </div>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ConstraintChip;
