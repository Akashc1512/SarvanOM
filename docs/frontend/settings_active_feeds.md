# Frontend Settings - Active Data Sources

**Date**: September 9, 2025  
**Status**: ✅ **PR-1 IMPLEMENTATION** - Settings panel for active data sources  
**Purpose**: Frontend settings page configuration for displaying active data sources and fallback status

---

## 📋 **Settings Page Configuration**

### **Active Data Sources Panel**

The settings page (`/settings`) should include an "Active data sources" panel that displays:

#### **Provider Status Display**
```typescript
interface ProviderStatus {
  name: string;
  configured: boolean;
  keyless_fallback_enabled: boolean;
  status: 'active' | 'fallback' | 'unavailable';
  last_checked: string;
}
```

#### **Panel Layout**
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Active Data Sources                                  │
├─────────────────────────────────────────────────────────┤
│ 🔍 Web Search                                           │
│   ✅ Brave Search (Primary)                             │
│   ⚠️  SerpAPI (Fallback)                               │
│   🔄 DuckDuckGo (Keyless)                              │
│                                                         │
│ 📰 News                                                 │
│   ✅ Guardian Open Platform (Primary)                  │
│   ⚠️  NewsAPI (Fallback)                               │
│   🔄 GDELT (Keyless)                                   │
│                                                         │
│ 📈 Markets                                              │
│   ✅ Alpha Vantage (Primary)                           │
│   ⚠️  Finnhub (Fallback)                               │
│   🔄 Stooq (Keyless)                                   │
│                                                         │
│ 🤖 AI Models                                            │
│   ✅ OpenAI (Text LLM)                                 │
│   ✅ Anthropic (Text LLM)                              │
│   ✅ Gemini (Vision/LMM)                               │
│                                                         │
│ 🔧 Keyless Fallbacks: ✅ ENABLED                       │
└─────────────────────────────────────────────────────────┘
```

### **API Endpoints**

#### **Get Active Data Sources**
```http
GET /api/settings/active-sources
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "keyless_fallbacks_enabled": true,
    "providers": {
      "web_search": {
        "lane": "Web Search",
        "providers": [
          {
            "name": "Brave Search",
            "configured": true,
            "status": "active",
            "type": "primary"
          },
          {
            "name": "SerpAPI",
            "configured": true,
            "status": "fallback",
            "type": "fallback"
          },
          {
            "name": "DuckDuckGo",
            "configured": false,
            "status": "keyless",
            "type": "keyless"
          }
        ]
      },
      "news": {
        "lane": "News",
        "providers": [
          {
            "name": "Guardian Open Platform",
            "configured": true,
            "status": "active",
            "type": "primary"
          },
          {
            "name": "NewsAPI",
            "configured": false,
            "status": "keyless",
            "type": "keyless"
          }
        ]
      },
      "markets": {
        "lane": "Markets",
        "providers": [
          {
            "name": "Alpha Vantage",
            "configured": true,
            "status": "active",
            "type": "primary"
          },
          {
            "name": "Finnhub",
            "configured": false,
            "status": "keyless",
            "type": "keyless"
          }
        ]
      },
      "ai_models": {
        "lane": "AI Models",
        "providers": [
          {
            "name": "OpenAI",
            "configured": true,
            "status": "active",
            "type": "text_llm"
          },
          {
            "name": "Anthropic",
            "configured": true,
            "status": "active",
            "type": "text_llm"
          },
          {
            "name": "Gemini",
            "configured": true,
            "status": "active",
            "type": "vision_lmm"
          }
        ]
      }
    }
  }
}
```

#### **Toggle Keyless Fallbacks**
```http
POST /api/settings/toggle-keyless-fallbacks
Content-Type: application/json

{
  "enabled": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Keyless fallbacks enabled",
  "data": {
    "keyless_fallbacks_enabled": true
  }
}
```

### **Frontend Implementation**

#### **React Component Structure**
```typescript
// components/settings/ActiveDataSources.tsx
interface ActiveDataSourcesProps {
  providers: ProviderStatus[];
  keylessFallbacksEnabled: boolean;
  onToggleKeylessFallbacks: (enabled: boolean) => void;
}

const ActiveDataSources: React.FC<ActiveDataSourcesProps> = ({
  providers,
  keylessFallbacksEnabled,
  onToggleKeylessFallbacks
}) => {
  return (
    <div className="active-data-sources-panel">
      <h3>📊 Active Data Sources</h3>
      
      {Object.entries(providers).map(([lane, laneProviders]) => (
        <LaneProviderList
          key={lane}
          lane={lane}
          providers={laneProviders}
        />
      ))}
      
      <KeylessFallbacksToggle
        enabled={keylessFallbacksEnabled}
        onToggle={onToggleKeylessFallbacks}
      />
    </div>
  );
};
```

#### **Provider Status Icons**
```typescript
const getProviderIcon = (status: string, type: string) => {
  switch (status) {
    case 'active':
      return '✅';
    case 'fallback':
      return '⚠️';
    case 'keyless':
      return '🔄';
    case 'unavailable':
      return '❌';
    default:
      return '❓';
  }
};

const getProviderTypeLabel = (type: string) => {
  switch (type) {
    case 'primary':
      return '(Primary)';
    case 'fallback':
      return '(Fallback)';
    case 'keyless':
      return '(Keyless)';
    case 'text_llm':
      return '(Text LLM)';
    case 'vision_lmm':
      return '(Vision/LMM)';
    default:
      return '';
  }
};
```

### **Status Indicators**

#### **Provider Status Types**
- **✅ Active**: Provider is configured and working
- **⚠️ Fallback**: Provider is configured but used as fallback
- **🔄 Keyless**: Provider uses keyless fallback (no API key required)
- **❌ Unavailable**: Provider is not configured and no fallback available

#### **Provider Type Labels**
- **Primary**: Main provider for the lane
- **Fallback**: Secondary provider used when primary fails
- **Keyless**: Free provider that doesn't require API keys
- **Text LLM**: Text-based language model
- **Vision/LMM**: Vision-capable large multimodal model

### **Keyless Fallbacks Toggle**

#### **Toggle Component**
```typescript
const KeylessFallbacksToggle: React.FC<{
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}> = ({ enabled, onToggle }) => {
  return (
    <div className="keyless-fallbacks-toggle">
      <label>
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => onToggle(e.target.checked)}
        />
        🔧 Keyless Fallbacks: {enabled ? '✅ ENABLED' : '❌ DISABLED'}
      </label>
      <p className="help-text">
        When enabled, the system will use free, keyless providers when 
        configured providers are unavailable.
      </p>
    </div>
  );
};
```

### **Real-time Updates**

#### **WebSocket Integration**
```typescript
// Real-time provider status updates
useEffect(() => {
  const ws = new WebSocket('/ws/provider-status');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'provider_status_update') {
      updateProviderStatus(data.providers);
    }
  };
  
  return () => ws.close();
}, []);
```

### **Error Handling**

#### **Provider Status Errors**
```typescript
const handleProviderError = (error: Error) => {
  console.error('Provider status error:', error);
  
  // Show user-friendly error message
  toast.error('Failed to load provider status. Please try again.');
  
  // Fallback to cached data if available
  const cachedData = localStorage.getItem('provider_status_cache');
  if (cachedData) {
    setProviders(JSON.parse(cachedData));
  }
};
```

### **Caching Strategy**

#### **Local Storage Cache**
```typescript
// Cache provider status for offline viewing
const cacheProviderStatus = (providers: ProviderStatus[]) => {
  localStorage.setItem(
    'provider_status_cache',
    JSON.stringify({
      data: providers,
      timestamp: Date.now()
    })
  );
};

// Use cached data if fresh (less than 5 minutes old)
const getCachedProviderStatus = (): ProviderStatus[] | null => {
  const cached = localStorage.getItem('provider_status_cache');
  if (!cached) return null;
  
  const { data, timestamp } = JSON.parse(cached);
  const age = Date.now() - timestamp;
  
  return age < 5 * 60 * 1000 ? data : null; // 5 minutes
};
```

---

## 🎯 **Implementation Checklist**

### **Backend API**
- [ ] Create `/api/settings/active-sources` endpoint
- [ ] Create `/api/settings/toggle-keyless-fallbacks` endpoint
- [ ] Implement provider status aggregation
- [ ] Add WebSocket support for real-time updates

### **Frontend Components**
- [ ] Create `ActiveDataSources` component
- [ ] Create `LaneProviderList` component
- [ ] Create `KeylessFallbacksToggle` component
- [ ] Implement provider status icons and labels
- [ ] Add error handling and loading states

### **Integration**
- [ ] Integrate with existing settings page
- [ ] Add real-time WebSocket updates
- [ ] Implement local storage caching
- [ ] Add accessibility features

---

## 📚 **References**

- Environment Contract Matrix: `docs/contracts/env_matrix.md`
- Provider Configuration: `sarvanom/shared/core/config/provider_config.py`
- Service Configurations: `sarvanom/services/*/config.py`
- Frontend Settings: `frontend/src/pages/settings/`

---

*This document defines the frontend settings implementation for displaying active data sources and managing keyless fallbacks in SarvanOM v2.*
