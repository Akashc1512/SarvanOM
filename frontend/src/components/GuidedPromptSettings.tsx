/**
 * Guided Prompt Settings Component
 * 
 * Settings page component for configuring Guided Prompt Confirmation.
 * Includes toggle, mode selection, and preference options.
 */

import React, { useState, useEffect } from 'react';
import { Settings, Toggle, Info, HelpCircle, Check, X } from 'lucide-react';

interface GuidedPromptSettingsProps {
  userId: string;
  onSettingsChange: (settings: GuidedPromptSettings) => void;
  onClose?: () => void;
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
  session_overrides: {
    bypass_once: boolean;
    session_id: string;
  };
}

export const GuidedPromptSettings: React.FC<GuidedPromptSettingsProps> = ({
  userId,
  onSettingsChange,
  onClose
}) => {
  const [settings, setSettings] = useState<GuidedPromptSettings>({
    enabled: true,
    mode: 'ON',
    preferences: {
      show_hints: true,
      auto_learn: true,
      constraint_chips: true,
      accessibility_mode: false
    },
    session_overrides: {
      bypass_once: false,
      session_id: ''
    }
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, [userId]);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      // In real implementation, this would fetch from API
      const response = await fetch(`/api/guided-prompt/settings/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setSettings(data.settings);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      setIsSaving(true);
      // In real implementation, this would save to API
      const response = await fetch(`/api/guided-prompt/settings/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ settings }),
      });
      
      if (response.ok) {
        onSettingsChange(settings);
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleChange = (key: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handlePreferenceChange = (key: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: value
      }
    }));
  };

  const handleModeChange = (mode: 'ON' | 'OFF' | 'BYPASS_ONCE' | 'ALWAYS_BYPASS') => {
    setSettings(prev => ({
      ...prev,
      mode,
      enabled: mode !== 'OFF'
    }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading settings...</span>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Settings className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-semibold text-gray-900">Query Preferences</h1>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Main Settings */}
      <div className="space-y-6">
        {/* Guided Prompt Confirmation Toggle */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h2 className="text-lg font-medium text-gray-900">🔍 Guided Prompt Confirmation</h2>
                <button
                  onClick={() => setShowHelp(!showHelp)}
                  className="p-1 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-full"
                >
                  <HelpCircle className="w-4 h-4" />
                </button>
              </div>
              
              <p className="text-sm text-gray-600 mb-4">
                Get suggestions to make your queries more specific and get better results.
              </p>

              {/* Help text */}
              {showHelp && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <h3 className="font-medium text-blue-900 mb-2">How it works:</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• When you enter a query, we'll suggest ways to make it more specific</li>
                    <li>• You can accept, edit, or skip the suggestions</li>
                    <li>• This helps you get more accurate and relevant results</li>
                    <li>• You can always bypass suggestions if you prefer</li>
                  </ul>
                </div>
              )}

              {/* Mode Selection */}
              <div className="space-y-3">
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="mode"
                      value="ON"
                      checked={settings.mode === 'ON'}
                      onChange={() => handleModeChange('ON')}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">ON - Show refinement suggestions</span>
                  </label>
                </div>
                
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="mode"
                      value="OFF"
                      checked={settings.mode === 'OFF'}
                      onChange={() => handleModeChange('OFF')}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">OFF - Skip refinement</span>
                  </label>
                </div>
                
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="mode"
                      value="BYPASS_ONCE"
                      checked={settings.mode === 'BYPASS_ONCE'}
                      onChange={() => handleModeChange('BYPASS_ONCE')}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">BYPASS ONCE - Skip for current session</span>
                  </label>
                </div>
                
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="mode"
                      value="ALWAYS_BYPASS"
                      checked={settings.mode === 'ALWAYS_BYPASS'}
                      onChange={() => handleModeChange('ALWAYS_BYPASS')}
                      className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">ALWAYS BYPASS - Never show suggestions</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Advanced Options */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Advanced Options</h3>
          
          <div className="space-y-4">
            {/* Show hints */}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Show helpful hints</label>
                <p className="text-xs text-gray-500">Display tips and explanations with suggestions</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.preferences.show_hints}
                  onChange={(e) => handlePreferenceChange('show_hints', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Auto learn */}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Auto-learn from your choices</label>
                <p className="text-xs text-gray-500">Improve suggestions based on your preferences</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.preferences.auto_learn}
                  onChange={(e) => handlePreferenceChange('auto_learn', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Constraint chips */}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Show constraint chips</label>
                <p className="text-xs text-gray-500">Display options for time range, sources, and depth</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.preferences.constraint_chips}
                  onChange={(e) => handlePreferenceChange('constraint_chips', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Accessibility mode */}
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">Accessibility mode</label>
                <p className="text-xs text-gray-500">Enhanced keyboard navigation and screen reader support</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.preferences.accessibility_mode}
                  onChange={(e) => handlePreferenceChange('accessibility_mode', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end space-x-3">
          <button
            onClick={saveSettings}
            disabled={isSaving}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline"></div>
                Saving...
              </>
            ) : (
              <>
                <Check className="w-4 h-4 mr-2 inline" />
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GuidedPromptSettings;
