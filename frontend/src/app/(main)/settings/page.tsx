/**
 * Settings Page - SarvanOM v2
 * 
 * Comprehensive settings page with Guided Prompt toggle and other user preferences.
 * Follows Cosmic Pro design system with accessibility features.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  ToggleLeft, 
  ToggleRight, 
  Bell, 
  Shield, 
  Palette, 
  Globe, 
  Database,
  Zap,
  Eye,
  EyeOff,
  Save,
  RotateCcw
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { designTokens } from '@/lib/design-tokens';

interface SettingsSection {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  settings: SettingItem[];
}

interface SettingItem {
  id: string;
  label: string;
  description: string;
  type: 'toggle' | 'select' | 'input' | 'textarea';
  value: any;
  options?: string[];
  placeholder?: string;
  required?: boolean;
  category: 'guided-prompt' | 'privacy' | 'appearance' | 'notifications' | 'data';
}

const settingsSections: SettingsSection[] = [
  {
    id: 'guided-prompt',
    title: 'Guided Prompt Confirmation',
    description: 'Configure how the system helps refine your queries',
    icon: Zap,
    settings: [
      {
        id: 'enabled',
        label: 'Enable Guided Prompt',
        description: 'Show refinement suggestions before processing queries',
        type: 'toggle',
        value: true,
        category: 'guided-prompt'
      },
      {
        id: 'default-mode',
        label: 'Default Refinement Mode',
        description: 'Choose the default refinement approach',
        type: 'select',
        value: 'refine',
        options: ['refine', 'disambiguate', 'decompose', 'constrain', 'sanitize'],
        category: 'guided-prompt'
      },
      {
        id: 'auto-skip-threshold',
        label: 'Auto-skip Threshold',
        description: 'Skip refinement if confidence is below this percentage',
        type: 'input',
        value: '30',
        placeholder: '30',
        category: 'guided-prompt'
      },
      {
        id: 'show-reasoning',
        label: 'Show Reasoning',
        description: 'Display the reasoning behind refinement suggestions',
        type: 'toggle',
        value: true,
        category: 'guided-prompt'
      },
      {
        id: 'constraint-chips',
        label: 'Enable Constraint Chips',
        description: 'Show constraint selection chips for query refinement',
        type: 'toggle',
        value: true,
        category: 'guided-prompt'
      }
    ]
  },
  {
    id: 'privacy',
    title: 'Privacy & Data',
    description: 'Control how your data is handled and stored',
    icon: Shield,
    settings: [
      {
        id: 'raw-draft-storage',
        label: 'Store Raw Drafts',
        description: 'Allow storage of unrefined user queries for improvement',
        type: 'toggle',
        value: false,
        category: 'privacy'
      },
      {
        id: 'refined-prompt-storage',
        label: 'Store Refined Prompts',
        description: 'Allow storage of refined prompts for analytics',
        type: 'toggle',
        value: true,
        category: 'privacy'
      },
      {
        id: 'analytics-tracking',
        label: 'Analytics Tracking',
        description: 'Allow usage analytics and performance tracking',
        type: 'toggle',
        value: true,
        category: 'privacy'
      },
      {
        id: 'personalization',
        label: 'Personalization',
        description: 'Use data for personalized experiences',
        type: 'toggle',
        value: true,
        category: 'privacy'
      },
      {
        id: 'data-retention',
        label: 'Data Retention Period',
        description: 'How long to keep your data (in days)',
        type: 'input',
        value: '30',
        placeholder: '30',
        category: 'privacy'
      }
    ]
  },
  {
    id: 'appearance',
    title: 'Appearance',
    description: 'Customize the look and feel of the interface',
    icon: Palette,
    settings: [
      {
        id: 'theme',
        label: 'Theme',
        description: 'Choose your preferred color scheme',
        type: 'select',
        value: 'system',
        options: ['light', 'dark', 'system'],
        category: 'appearance'
      },
      {
        id: 'compact-mode',
        label: 'Compact Mode',
        description: 'Use a more compact interface layout',
        type: 'toggle',
        value: false,
        category: 'appearance'
      },
      {
        id: 'animations',
        label: 'Animations',
        description: 'Enable interface animations and transitions',
        type: 'toggle',
        value: true,
        category: 'appearance'
      },
      {
        id: 'high-contrast',
        label: 'High Contrast',
        description: 'Use high contrast colors for better visibility',
        type: 'toggle',
        value: false,
        category: 'appearance'
      }
    ]
  },
  {
    id: 'notifications',
    title: 'Notifications',
    description: 'Manage notification preferences',
    icon: Bell,
    settings: [
      {
        id: 'email-notifications',
        label: 'Email Notifications',
        description: 'Receive notifications via email',
        type: 'toggle',
        value: true,
        category: 'notifications'
      },
      {
        id: 'push-notifications',
        label: 'Push Notifications',
        description: 'Receive browser push notifications',
        type: 'toggle',
        value: false,
        category: 'notifications'
      },
      {
        id: 'query-completion',
        label: 'Query Completion Alerts',
        description: 'Notify when long-running queries complete',
        type: 'toggle',
        value: true,
        category: 'notifications'
      },
      {
        id: 'system-updates',
        label: 'System Updates',
        description: 'Notify about system updates and maintenance',
        type: 'toggle',
        value: true,
        category: 'notifications'
      }
    ]
  },
  {
    id: 'data',
    title: 'Data Management',
    description: 'Control data export, import, and management',
    icon: Database,
    settings: [
      {
        id: 'auto-backup',
        label: 'Auto Backup',
        description: 'Automatically backup your data',
        type: 'toggle',
        value: true,
        category: 'data'
      },
      {
        id: 'backup-frequency',
        label: 'Backup Frequency',
        description: 'How often to create backups',
        type: 'select',
        value: 'weekly',
        options: ['daily', 'weekly', 'monthly'],
        category: 'data'
      },
      {
        id: 'export-format',
        label: 'Export Format',
        description: 'Default format for data exports',
        type: 'select',
        value: 'json',
        options: ['json', 'csv', 'xml'],
        category: 'data'
      }
    ]
  }
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, any>>({});
  const [activeSection, setActiveSection] = useState('guided-prompt');
  const [hasChanges, setHasChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Initialize settings from localStorage or defaults
  useEffect(() => {
    const savedSettings = localStorage.getItem('sarvanom-settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    } else {
      // Initialize with default values
      const defaultSettings: Record<string, any> = {};
      settingsSections.forEach(section => {
        section.settings.forEach(setting => {
          defaultSettings[setting.id] = setting.value;
        });
      });
      setSettings(defaultSettings);
    }
  }, []);

  // Handle setting changes
  const handleSettingChange = (settingId: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [settingId]: value
    }));
    setHasChanges(true);
  };

  // Save settings
  const handleSave = async () => {
    setIsSaving(true);
    try {
      localStorage.setItem('sarvanom-settings', JSON.stringify(settings));
      setHasChanges(false);
      // Show success message
      console.log('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Reset settings
  const handleReset = () => {
    const defaultSettings: Record<string, any> = {};
    settingsSections.forEach(section => {
      section.settings.forEach(setting => {
        defaultSettings[setting.id] = setting.value;
      });
    });
    setSettings(defaultSettings);
    setHasChanges(true);
  };

  // Render setting input based on type
  const renderSettingInput = (setting: SettingItem) => {
    const value = settings[setting.id] ?? setting.value;

    switch (setting.type) {
      case 'toggle':
        return (
          <button
            onClick={() => handleSettingChange(setting.id, !value)}
            className={cn(
              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
              value ? 'bg-blue-600' : 'bg-gray-200'
            )}
            role="switch"
            aria-checked={value}
            aria-label={setting.label}
          >
            <span
              className={cn(
                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                value ? 'translate-x-6' : 'translate-x-1'
              )}
            />
          </button>
        );

      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleSettingChange(setting.id, e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label={setting.label}
          >
            {setting.options?.map(option => (
              <option key={option} value={option}>
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </option>
            ))}
          </select>
        );

      case 'input':
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleSettingChange(setting.id, e.target.value)}
            placeholder={setting.placeholder}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            aria-label={setting.label}
          />
        );

      case 'textarea':
        return (
          <textarea
            value={value}
            onChange={(e) => handleSettingChange(setting.id, e.target.value)}
            placeholder={setting.placeholder}
            rows={3}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
            aria-label={setting.label}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <SettingsIcon className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
                  <p className="text-gray-600">Manage your preferences and configuration</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                {hasChanges && (
                  <motion.button
                    onClick={handleReset}
                    className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <RotateCcw className="w-4 h-4" />
                    Reset
                  </motion.button>
                )}
                
                <motion.button
                  onClick={handleSave}
                  disabled={!hasChanges || isSaving}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-md transition-colors',
                    hasChanges && !isSaving
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  )}
                  whileHover={hasChanges && !isSaving ? { scale: 1.02 } : undefined}
                  whileTap={hasChanges && !isSaving ? { scale: 0.98 } : undefined}
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </motion.button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <nav className="space-y-2">
              {settingsSections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={cn(
                      'w-full flex items-center gap-3 px-4 py-3 text-left rounded-lg transition-colors',
                      activeSection === section.id
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-700 hover:bg-gray-50'
                    )}
                  >
                    <Icon className="w-5 h-5" />
                    <div>
                      <div className="font-medium">{section.title}</div>
                      <div className="text-sm text-gray-500">{section.description}</div>
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-lg shadow-sm border border-gray-200"
            >
              <div className="p-6">
                {settingsSections
                  .filter(section => section.id === activeSection)
                  .map(section => {
                    const Icon = section.icon;
                    return (
                      <div key={section.id}>
                        <div className="flex items-center gap-3 mb-6">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <Icon className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                              {section.title}
                            </h2>
                            <p className="text-gray-600">{section.description}</p>
                          </div>
                        </div>

                        <div className="space-y-6">
                          {section.settings.map((setting) => (
                            <div
                              key={setting.id}
                              className="flex items-start justify-between py-4 border-b border-gray-100 last:border-b-0"
                            >
                              <div className="flex-1 pr-6">
                                <div className="flex items-center gap-2 mb-1">
                                  <label className="font-medium text-gray-900">
                                    {setting.label}
                                  </label>
                                  {setting.required && (
                                    <span className="text-red-500 text-sm">*</span>
                                  )}
                                </div>
                                <p className="text-sm text-gray-600">
                                  {setting.description}
                                </p>
                              </div>
                              
                              <div className="flex-shrink-0">
                                {renderSettingInput(setting)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
