# Guided Prompt Settings Contract

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Product Team  

## Overview

This document defines the contract for storing and managing user preferences related to the Guided Prompt Confirmation feature. It covers data storage, synchronization, privacy considerations, and user control mechanisms.

## Settings Data Model

### 1. Core Settings Structure
```typescript
// User settings interface
interface GuidedPromptSettings {
  // Core feature toggle
  enabled: boolean;
  
  // User preference mode
  mode: 'default' | 'expert' | 'adaptive';
  
  // Confirmation preferences
  confirmation: {
    showForHighConfidence: boolean;  // Show for confidence > 0.8
    showForMediumConfidence: boolean; // Show for confidence 0.5-0.8
    showForLowConfidence: boolean;   // Show for confidence < 0.5
    minimumConfidenceThreshold: number; // Minimum confidence to show
  };
  
  // Learning preferences
  learning: {
    enableAutoTeach: boolean;        // Show educational tooltips
    trackImprovements: boolean;      // Track query quality improvements
    adaptiveMode: boolean;           // Enable adaptive behavior
  };
  
  // Privacy preferences
  privacy: {
    storeQueryHistory: boolean;      // Store queries for analysis
    shareAnonymizedData: boolean;    // Share anonymized usage data
    enablePersonalization: boolean;  // Enable personalized suggestions
  };
  
  // Advanced preferences
  advanced: {
    customConfidenceThreshold: number; // Custom confidence threshold
    preferredLane: QueryLane | null;   // Preferred query lane
    skipCategories: string[];          // Categories to skip
    customPrompts: string[];           // Custom prompt templates
  };
  
  // Metadata
  metadata: {
    createdAt: Date;
    updatedAt: Date;
    version: string;
    userId: string;
  };
}
```

### 2. Default Settings Configuration
```typescript
// Default settings for new users
const DEFAULT_GUIDED_PROMPT_SETTINGS: GuidedPromptSettings = {
  enabled: true,
  mode: 'default',
  confirmation: {
    showForHighConfidence: true,
    showForMediumConfidence: true,
    showForLowConfidence: false,
    minimumConfidenceThreshold: 0.5
  },
  learning: {
    enableAutoTeach: true,
    trackImprovements: true,
    adaptiveMode: false
  },
  privacy: {
    storeQueryHistory: true,
    shareAnonymizedData: false,
    enablePersonalization: true
  },
  advanced: {
    customConfidenceThreshold: 0.7,
    preferredLane: null,
    skipCategories: [],
    customPrompts: []
  },
  metadata: {
    createdAt: new Date(),
    updatedAt: new Date(),
    version: '1.0',
    userId: ''
  }
};
```

## Storage Implementation

### 1. Database Schema
```sql
-- User settings table
CREATE TABLE user_guided_prompt_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    settings JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version VARCHAR(10) NOT NULL DEFAULT '1.0',
    
    -- Indexes
    UNIQUE(user_id),
    INDEX idx_user_settings_updated_at (updated_at),
    INDEX idx_user_settings_version (version)
);

-- Settings change history table
CREATE TABLE user_settings_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    settings_before JSONB,
    settings_after JSONB NOT NULL,
    change_reason VARCHAR(255),
    changed_by VARCHAR(255) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_settings_history_user_id (user_id),
    INDEX idx_settings_history_created_at (created_at)
);
```

### 2. Session Storage
```typescript
// Session storage for temporary settings
interface SessionSettings {
  guidedPromptEnabled: boolean;
  lastUsedAt: Date;
  sessionId: string;
  temporaryOverrides: Partial<GuidedPromptSettings>;
}

// Session storage implementation
class SessionSettingsManager {
  private sessionKey = 'sarvanom_guided_prompt_session';
  
  getSessionSettings(): SessionSettings | null {
    try {
      const stored = sessionStorage.getItem(this.sessionKey);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Failed to retrieve session settings:', error);
      return null;
    }
  }
  
  setSessionSettings(settings: SessionSettings): void {
    try {
      sessionStorage.setItem(this.sessionKey, JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to store session settings:', error);
    }
  }
  
  clearSessionSettings(): void {
    sessionStorage.removeItem(this.sessionKey);
  }
}
```

### 3. Local Storage
```typescript
// Local storage for persistent settings
interface LocalSettings {
  guidedPromptSettings: GuidedPromptSettings;
  lastSyncAt: Date;
  syncVersion: string;
}

// Local storage implementation
class LocalSettingsManager {
  private localKey = 'sarvanom_guided_prompt_local';
  
  getLocalSettings(): LocalSettings | null {
    try {
      const stored = localStorage.getItem(this.localKey);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Failed to retrieve local settings:', error);
      return null;
    }
  }
  
  setLocalSettings(settings: LocalSettings): void {
    try {
      localStorage.setItem(this.localKey, JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to store local settings:', error);
    }
  }
  
  clearLocalSettings(): void {
    localStorage.removeItem(this.localKey);
  }
}
```

## Settings Synchronization

### 1. Multi-Layer Storage Strategy
```typescript
// Settings synchronization manager
class SettingsSyncManager {
  private dbManager: DatabaseSettingsManager;
  private sessionManager: SessionSettingsManager;
  private localManager: LocalSettingsManager;
  
  async getSettings(userId: string): Promise<GuidedPromptSettings> {
    // Priority order: Session > Local > Database > Default
    
    // 1. Check session storage first (highest priority)
    const sessionSettings = this.sessionManager.getSessionSettings();
    if (sessionSettings?.guidedPromptEnabled !== undefined) {
      return this.mergeWithDefaults(sessionSettings);
    }
    
    // 2. Check local storage
    const localSettings = this.localManager.getLocalSettings();
    if (localSettings?.guidedPromptSettings) {
      return localSettings.guidedPromptSettings;
    }
    
    // 3. Check database
    const dbSettings = await this.dbManager.getSettings(userId);
    if (dbSettings) {
      return dbSettings;
    }
    
    // 4. Return defaults
    return DEFAULT_GUIDED_PROMPT_SETTINGS;
  }
  
  async updateSettings(
    userId: string, 
    settings: Partial<GuidedPromptSettings>
  ): Promise<void> {
    // Update all storage layers
    await Promise.all([
      this.dbManager.updateSettings(userId, settings),
      this.localManager.setLocalSettings({
        guidedPromptSettings: settings as GuidedPromptSettings,
        lastSyncAt: new Date(),
        syncVersion: '1.0'
      }),
      this.sessionManager.setSessionSettings({
        guidedPromptEnabled: settings.enabled ?? true,
        lastUsedAt: new Date(),
        sessionId: this.generateSessionId(),
        temporaryOverrides: settings
      })
    ]);
  }
  
  private mergeWithDefaults(settings: Partial<GuidedPromptSettings>): GuidedPromptSettings {
    return {
      ...DEFAULT_GUIDED_PROMPT_SETTINGS,
      ...settings,
      metadata: {
        ...DEFAULT_GUIDED_PROMPT_SETTINGS.metadata,
        ...settings.metadata,
        updatedAt: new Date()
      }
    };
  }
}
```

### 2. Conflict Resolution
```typescript
// Conflict resolution strategy
interface ConflictResolutionStrategy {
  resolveConflicts(
    localSettings: GuidedPromptSettings,
    remoteSettings: GuidedPromptSettings
  ): GuidedPromptSettings;
}

class TimestampBasedResolution implements ConflictResolutionStrategy {
  resolveConflicts(
    localSettings: GuidedPromptSettings,
    remoteSettings: GuidedPromptSettings
  ): GuidedPromptSettings {
    // Use the most recently updated settings
    const localTime = new Date(localSettings.metadata.updatedAt).getTime();
    const remoteTime = new Date(remoteSettings.metadata.updatedAt).getTime();
    
    return localTime > remoteTime ? localSettings : remoteSettings;
  }
}

class UserPreferenceResolution implements ConflictResolutionStrategy {
  resolveConflicts(
    localSettings: GuidedPromptSettings,
    remoteSettings: GuidedPromptSettings
  ): GuidedPromptSettings {
    // Merge settings based on user preferences
    return {
      ...localSettings,
      ...remoteSettings,
      // Preserve user's explicit choices
      enabled: localSettings.enabled,
      mode: localSettings.mode,
      metadata: {
        ...localSettings.metadata,
        updatedAt: new Date()
      }
    };
  }
}
```

## Privacy and Data Protection

### 1. Data Minimization
```typescript
// Data minimization implementation
class PrivacyManager {
  private anonymizeSettings(settings: GuidedPromptSettings): AnonymizedSettings {
    return {
      enabled: settings.enabled,
      mode: settings.mode,
      confirmation: {
        showForHighConfidence: settings.confirmation.showForHighConfidence,
        showForMediumConfidence: settings.confirmation.showForMediumConfidence,
        showForLowConfidence: settings.confirmation.showForLowConfidence,
        minimumConfidenceThreshold: settings.confirmation.minimumConfidenceThreshold
      },
      // Remove personal identifiers
      metadata: {
        createdAt: settings.metadata.createdAt,
        updatedAt: settings.metadata.updatedAt,
        version: settings.metadata.version
        // userId removed for privacy
      }
    };
  }
  
  private shouldStoreQueryHistory(settings: GuidedPromptSettings): boolean {
    return settings.privacy.storeQueryHistory && 
           settings.privacy.shareAnonymizedData;
  }
}
```

### 2. Consent Management
```typescript
// Consent management
interface ConsentPreferences {
  essential: boolean;        // Required for basic functionality
  analytics: boolean;        // For usage analytics
  personalization: boolean;  // For personalized suggestions
  marketing: boolean;        // For marketing communications
}

class ConsentManager {
  private consentKey = 'sarvanom_consent_preferences';
  
  getConsentPreferences(): ConsentPreferences {
    const stored = localStorage.getItem(this.consentKey);
    return stored ? JSON.parse(stored) : {
      essential: true,
      analytics: false,
      personalization: false,
      marketing: false
    };
  }
  
  updateConsentPreferences(consent: ConsentPreferences): void {
    localStorage.setItem(this.consentKey, JSON.stringify(consent));
  }
  
  hasConsentFor(feature: keyof ConsentPreferences): boolean {
    const consent = this.getConsentPreferences();
    return consent[feature];
  }
}
```

### 3. Data Retention
```typescript
// Data retention policy
interface DataRetentionPolicy {
  settings: {
    active: number;      // 2 years for active users
    inactive: number;    // 1 year for inactive users
  };
  queryHistory: {
    active: number;      // 6 months for active users
    inactive: number;    // 3 months for inactive users
  };
  analytics: {
    active: number;      // 1 year for active users
    inactive: number;    // 6 months for inactive users
  };
}

class DataRetentionManager {
  private retentionPolicy: DataRetentionPolicy = {
    settings: { active: 730, inactive: 365 },      // days
    queryHistory: { active: 180, inactive: 90 },   // days
    analytics: { active: 365, inactive: 180 }      // days
  };
  
  async cleanupExpiredData(userId: string): Promise<void> {
    const userActivity = await this.getUserActivity(userId);
    const isActive = userActivity.lastActiveAt > this.getActiveThreshold();
    
    await Promise.all([
      this.cleanupSettings(userId, isActive),
      this.cleanupQueryHistory(userId, isActive),
      this.cleanupAnalytics(userId, isActive)
    ]);
  }
  
  private getActiveThreshold(): Date {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    return thirtyDaysAgo;
  }
}
```

## User Control Mechanisms

### 1. Settings UI Components
```typescript
// Settings page component
const GuidedPromptSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<GuidedPromptSettings>(DEFAULT_GUIDED_PROMPT_SETTINGS);
  const [isLoading, setIsLoading] = useState(true);
  const [hasChanges, setHasChanges] = useState(false);
  
  useEffect(() => {
    loadSettings();
  }, []);
  
  const loadSettings = async () => {
    try {
      const userSettings = await settingsSyncManager.getSettings(getCurrentUserId());
      setSettings(userSettings);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const updateSettings = async (updates: Partial<GuidedPromptSettings>) => {
    try {
      const newSettings = { ...settings, ...updates };
      setSettings(newSettings);
      setHasChanges(true);
      
      await settingsSyncManager.updateSettings(getCurrentUserId(), updates);
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to update settings:', error);
    }
  };
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return (
    <div className="guided-prompt-settings">
      <h2>Guided Prompt Settings</h2>
      
      <div className="setting-group">
        <h3>Core Settings</h3>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={settings.enabled}
              onChange={(e) => updateSettings({ enabled: e.target.checked })}
            />
            Enable Guided Prompt Confirmation
          </label>
          <p className="setting-description">
            Get suggestions to refine your queries for better results.
          </p>
        </div>
        
        <div className="setting-item">
          <label>Confidence Threshold</label>
          <select
            value={settings.confirmation.minimumConfidenceThreshold}
            onChange={(e) => updateSettings({
              confirmation: {
                ...settings.confirmation,
                minimumConfidenceThreshold: parseFloat(e.target.value)
              }
            })}
          >
            <option value={0.3}>Low (0.3)</option>
            <option value={0.5}>Medium (0.5)</option>
            <option value={0.7}>High (0.7)</option>
            <option value={0.9}>Very High (0.9)</option>
          </select>
        </div>
      </div>
      
      <div className="setting-group">
        <h3>Privacy Settings</h3>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={settings.privacy.storeQueryHistory}
              onChange={(e) => updateSettings({
                privacy: {
                  ...settings.privacy,
                  storeQueryHistory: e.target.checked
                }
              })}
            />
            Store Query History
          </label>
          <p className="setting-description">
            Store your queries to improve suggestions and learn from your preferences.
          </p>
        </div>
        
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={settings.privacy.shareAnonymizedData}
              onChange={(e) => updateSettings({
                privacy: {
                  ...settings.privacy,
                  shareAnonymizedData: e.target.checked
                }
              })}
            />
            Share Anonymized Data
          </label>
          <p className="setting-description">
            Share anonymized usage data to help improve the service for all users.
          </p>
        </div>
      </div>
      
      {hasChanges && (
        <div className="save-indicator">
          <span>Changes saved</span>
        </div>
      )}
    </div>
  );
};
```

### 2. Quick Toggle Component
```typescript
// Quick toggle component for easy access
const GuidedPromptToggle: React.FC = () => {
  const [enabled, setEnabled] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  
  const toggleEnabled = async () => {
    setIsLoading(true);
    try {
      const newValue = !enabled;
      setEnabled(newValue);
      
      await settingsSyncManager.updateSettings(getCurrentUserId(), {
        enabled: newValue
      });
      
      // Track toggle event
      analytics.track('guided_prompt_toggle', {
        enabled: newValue,
        location: 'quick_toggle'
      });
    } catch (error) {
      console.error('Failed to toggle guided prompt:', error);
      setEnabled(!enabled); // Revert on error
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <button
      className={`guided-prompt-toggle ${enabled ? 'enabled' : 'disabled'}`}
      onClick={toggleEnabled}
      disabled={isLoading}
      title={enabled ? 'Disable guided prompts' : 'Enable guided prompts'}
    >
      {isLoading ? (
        <Spinner size="small" />
      ) : (
        <Icon name={enabled ? 'lightbulb' : 'lightbulb-off'} />
      )}
    </button>
  );
};
```

## API Endpoints

### 1. Settings Management API
```typescript
// API endpoints for settings management
interface SettingsAPI {
  // Get user settings
  GET /api/settings/guided-prompt
  Response: {
    settings: GuidedPromptSettings;
    lastUpdated: Date;
    version: string;
  };
  
  // Update user settings
  PUT /api/settings/guided-prompt
  Request: {
    settings: Partial<GuidedPromptSettings>;
  };
  Response: {
    success: boolean;
    settings: GuidedPromptSettings;
    message?: string;
  };
  
  // Reset to defaults
  POST /api/settings/guided-prompt/reset
  Response: {
    success: boolean;
    settings: GuidedPromptSettings;
  };
  
  // Export settings
  GET /api/settings/guided-prompt/export
  Response: {
    settings: GuidedPromptSettings;
    exportDate: Date;
    format: 'json';
  };
  
  // Import settings
  POST /api/settings/guided-prompt/import
  Request: {
    settings: GuidedPromptSettings;
  };
  Response: {
    success: boolean;
    importedSettings: GuidedPromptSettings;
    conflicts?: string[];
  };
}
```

### 2. Consent Management API
```typescript
// API endpoints for consent management
interface ConsentAPI {
  // Get consent preferences
  GET /api/consent/preferences
  Response: {
    consent: ConsentPreferences;
    lastUpdated: Date;
  };
  
  // Update consent preferences
  PUT /api/consent/preferences
  Request: {
    consent: ConsentPreferences;
  };
  Response: {
    success: boolean;
    consent: ConsentPreferences;
  };
  
  // Withdraw consent
  DELETE /api/consent/preferences
  Request: {
    feature: keyof ConsentPreferences;
  };
  Response: {
    success: boolean;
    message: string;
  };
}
```

## Migration and Versioning

### 1. Settings Versioning
```typescript
// Settings version management
interface SettingsVersion {
  version: string;
  migrationScript: (oldSettings: any) => any;
  description: string;
}

const SETTINGS_VERSIONS: SettingsVersion[] = [
  {
    version: '1.0',
    migrationScript: (settings) => settings, // No migration needed
    description: 'Initial version'
  },
  {
    version: '1.1',
    migrationScript: (settings) => ({
      ...settings,
      learning: {
        ...settings.learning,
        adaptiveMode: false // New field with default value
      }
    }),
    description: 'Added adaptive mode support'
  }
];

class SettingsMigrationManager {
  migrateSettings(settings: any, targetVersion: string): any {
    const currentVersion = settings.metadata?.version || '1.0';
    
    if (currentVersion === targetVersion) {
      return settings;
    }
    
    let migratedSettings = settings;
    const currentIndex = SETTINGS_VERSIONS.findIndex(v => v.version === currentVersion);
    const targetIndex = SETTINGS_VERSIONS.findIndex(v => v.version === targetVersion);
    
    if (currentIndex === -1 || targetIndex === -1) {
      throw new Error('Invalid version specified');
    }
    
    // Apply migrations in sequence
    for (let i = currentIndex + 1; i <= targetIndex; i++) {
      migratedSettings = SETTINGS_VERSIONS[i].migrationScript(migratedSettings);
    }
    
    return migratedSettings;
  }
}
```

### 2. Data Migration
```typescript
// Data migration for settings
class DataMigrationManager {
  async migrateUserSettings(userId: string): Promise<void> {
    const currentSettings = await this.dbManager.getSettings(userId);
    
    if (!currentSettings) {
      return; // No settings to migrate
    }
    
    const migratedSettings = this.settingsMigrationManager.migrateSettings(
      currentSettings,
      '1.1'
    );
    
    await this.dbManager.updateSettings(userId, migratedSettings);
    
    // Log migration
    await this.logMigration(userId, currentSettings.metadata.version, '1.1');
  }
  
  private async logMigration(
    userId: string,
    fromVersion: string,
    toVersion: string
  ): Promise<void> {
    await this.dbManager.logMigration({
      userId,
      fromVersion,
      toVersion,
      migratedAt: new Date()
    });
  }
}
```

---

## Appendix

### A. Database Schema
- User settings table structure
- Settings history table structure
- Migration tracking table structure

### B. API Documentation
- Complete API endpoint documentation
- Request/response schemas
- Error handling specifications

### C. Privacy Compliance
- GDPR compliance checklist
- CCPA compliance requirements
- Data retention policies
- User rights implementation
