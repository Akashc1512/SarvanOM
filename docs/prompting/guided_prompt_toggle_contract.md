# Guided Prompt Toggle Contract

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Where the default-ON toggle lives, storage contract, and allowed values

---

## 🎛️ **Toggle Location**

### **Settings Page Integration**
The Guided Prompt Confirmation toggle is located in the user settings page under the "Query Preferences" section:

```
Settings → Query Preferences → Guided Prompt Confirmation
```

### **Toggle UI Design**
```
┌─────────────────────────────────────────────────────────────┐
│                    Query Preferences                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🔍 Guided Prompt Confirmation                              │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [ON]  Help me refine my queries before execution       │ │
│ │                                                         │ │
│ │ 💡 Get suggestions to make your queries more specific  │ │
│ │    and get better results.                              │ │
│ │                                                         │ │
│ │ [Learn more about Guided Prompt]                        │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Advanced Options:                                           │
│ [ ] Always bypass for this session                         │
│ [ ] Remember my preference across devices                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Toggle States**
| State | Description | Behavior | Default |
|-------|-------------|----------|---------|
| **ON** | Show refinement suggestions | Trigger refinement for ambiguous queries | ✅ **Default** |
| **OFF** | Skip refinement | Run queries directly without suggestions | No |
| **BYPASS_ONCE** | Skip for current session | Bypass refinement for current session only | No |
| **ALWAYS_BYPASS** | Skip permanently | Never show refinement suggestions | No |

---

## 💾 **Storage Contract**

### **Storage Locations**
1. **User Profile (Server)**: Primary storage in user database
2. **Local Override (Client)**: Browser localStorage for immediate changes
3. **Session Storage**: Temporary session-based overrides

### **Storage Schema**
```json
{
  "user_id": "user_12345",
  "guided_prompt_settings": {
    "enabled": true,
    "mode": "ON",
    "last_updated": "2025-09-09T10:00:00Z",
    "version": "1.0.0",
    "preferences": {
      "show_hints": true,
      "auto_learn": true,
      "constraint_chips": true,
      "accessibility_mode": false
    },
    "session_overrides": {
      "bypass_once": false,
      "session_id": "session_abc123"
    }
  }
}
```

### **Storage Implementation**
```python
# Example storage implementation
class GuidedPromptStorage:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.server_storage = ServerStorage()
        self.client_storage = ClientStorage()
    
    def get_setting(self, key: str) -> Any:
        """Get setting with last-write-wins logic"""
        # Check local override first
        local_value = self.client_storage.get(key)
        if local_value is not None:
            return local_value
        
        # Fall back to server storage
        server_value = self.server_storage.get(self.user_id, key)
        return server_value
    
    def set_setting(self, key: str, value: Any, persist: bool = True) -> bool:
        """Set setting with last-write-wins logic"""
        # Update local storage immediately
        self.client_storage.set(key, value)
        
        # Update server storage if persist is True
        if persist:
            return self.server_storage.set(self.user_id, key, value)
        
        return True
    
    def sync_settings(self) -> bool:
        """Sync local settings to server"""
        local_settings = self.client_storage.get_all()
        return self.server_storage.update_user_settings(self.user_id, local_settings)
```

---

## 🔄 **Last-Write-Wins Logic**

### **Conflict Resolution**
When there are conflicts between server and client storage:

1. **Client Override**: Local changes take precedence
2. **Timestamp Check**: Most recent change wins
3. **Sync on Login**: Server settings sync to client on login
4. **Background Sync**: Periodic sync to keep settings consistent

### **Sync Implementation**
```python
# Example sync implementation
class SettingsSync:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.last_sync = None
    
    def sync_settings(self) -> Dict:
        """Sync settings between client and server"""
        client_settings = self.get_client_settings()
        server_settings = self.get_server_settings()
        
        # Determine which settings to use
        synced_settings = self.resolve_conflicts(client_settings, server_settings)
        
        # Update both storages
        self.update_client_settings(synced_settings)
        self.update_server_settings(synced_settings)
        
        self.last_sync = time.time()
        return synced_settings
    
    def resolve_conflicts(self, client: Dict, server: Dict) -> Dict:
        """Resolve conflicts using last-write-wins logic"""
        resolved = {}
        
        # Get all unique keys
        all_keys = set(client.keys()) | set(server.keys())
        
        for key in all_keys:
            client_value = client.get(key)
            server_value = server.get(key)
            
            if client_value is None:
                resolved[key] = server_value
            elif server_value is None:
                resolved[key] = client_value
            else:
                # Both exist, check timestamps
                client_time = client.get(f"{key}_timestamp", 0)
                server_time = server.get(f"{key}_timestamp", 0)
                
                if client_time >= server_time:
                    resolved[key] = client_value
                else:
                    resolved[key] = server_value
        
        return resolved
```

---

## 🎯 **Allowed Values**

### **Primary Toggle Values**
| Value | Description | Behavior | Persistence |
|-------|-------------|----------|-------------|
| **ON** | Enable refinement | Show suggestions for ambiguous queries | Permanent |
| **OFF** | Disable refinement | Skip refinement, run queries directly | Permanent |
| **BYPASS_ONCE** | Skip for session | Bypass refinement for current session only | Session |
| **ALWAYS_BYPASS** | Skip permanently | Never show refinement suggestions | Permanent |

### **Value Validation**
```python
# Example value validation
class ToggleValueValidator:
    ALLOWED_VALUES = {
        'ON': {
            'description': 'Enable refinement suggestions',
            'persistent': True,
            'default': True
        },
        'OFF': {
            'description': 'Disable refinement suggestions',
            'persistent': True,
            'default': False
        },
        'BYPASS_ONCE': {
            'description': 'Skip refinement for current session',
            'persistent': False,
            'default': False
        },
        'ALWAYS_BYPASS': {
            'description': 'Never show refinement suggestions',
            'persistent': True,
            'default': False
        }
    }
    
    def validate_value(self, value: str) -> bool:
        """Validate toggle value"""
        return value in self.ALLOWED_VALUES
    
    def get_value_info(self, value: str) -> Dict:
        """Get information about a toggle value"""
        if not self.validate_value(value):
            raise ValueError(f"Invalid toggle value: {value}")
        
        return self.ALLOWED_VALUES[value]
    
    def get_default_value(self) -> str:
        """Get default toggle value"""
        for value, info in self.ALLOWED_VALUES.items():
            if info.get('default', False):
                return value
        return 'ON'  # Fallback
```

---

## 🔧 **Environment Variable Integration**

### **Environment Variable Names**
The toggle contract uses the following environment variable naming convention:

```bash
# Guided Prompt Toggle Settings
GUIDED_PROMPT_DEFAULT_ENABLED=true
GUIDED_PROMPT_STORAGE_BACKEND=server
GUIDED_PROMPT_SYNC_INTERVAL=300
GUIDED_PROMPT_FALLBACK_VALUE=ON
```

### **Environment Integration**
```python
# Example environment integration
import os
from typing import Optional

class EnvironmentToggleConfig:
    def __init__(self):
        self.default_enabled = os.getenv('GUIDED_PROMPT_DEFAULT_ENABLED', 'true').lower() == 'true'
        self.storage_backend = os.getenv('GUIDED_PROMPT_STORAGE_BACKEND', 'server')
        self.sync_interval = int(os.getenv('GUIDED_PROMPT_SYNC_INTERVAL', '300'))
        self.fallback_value = os.getenv('GUIDED_PROMPT_FALLBACK_VALUE', 'ON')
    
    def get_default_toggle_value(self) -> str:
        """Get default toggle value from environment"""
        if self.default_enabled:
            return 'ON'
        else:
            return 'OFF'
    
    def get_storage_backend(self) -> str:
        """Get storage backend from environment"""
        return self.storage_backend
    
    def get_sync_interval(self) -> int:
        """Get sync interval from environment"""
        return self.sync_interval
    
    def get_fallback_value(self) -> str:
        """Get fallback value from environment"""
        return self.fallback_value
```

---

## 📱 **Cross-Device Synchronization**

### **Sync Strategy**
1. **Login Sync**: Sync settings when user logs in
2. **Background Sync**: Periodic sync every 5 minutes
3. **Change Sync**: Immediate sync when settings change
4. **Conflict Resolution**: Last-write-wins with timestamp

### **Sync Implementation**
```python
# Example cross-device sync
class CrossDeviceSync:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.sync_interval = 300  # 5 minutes
        self.last_sync = None
    
    async def start_background_sync(self):
        """Start background sync process"""
        while True:
            try:
                await self.sync_settings()
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Background sync failed: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute
    
    async def sync_settings(self) -> bool:
        """Sync settings across devices"""
        try:
            # Get current settings
            current_settings = await self.get_current_settings()
            
            # Get server settings
            server_settings = await self.get_server_settings()
            
            # Resolve conflicts
            synced_settings = self.resolve_conflicts(current_settings, server_settings)
            
            # Update both storages
            await self.update_current_settings(synced_settings)
            await self.update_server_settings(synced_settings)
            
            self.last_sync = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return False
    
    def resolve_conflicts(self, current: Dict, server: Dict) -> Dict:
        """Resolve conflicts using last-write-wins"""
        # Implementation similar to previous example
        pass
```

---

## 🧪 **Testing Contract**

### **Test Scenarios**
1. **Toggle State Changes**: Test all toggle value transitions
2. **Storage Persistence**: Test settings persistence across sessions
3. **Sync Behavior**: Test cross-device synchronization
4. **Conflict Resolution**: Test last-write-wins logic
5. **Fallback Behavior**: Test fallback when storage fails

### **Test Implementation**
```python
# Example test implementation
class ToggleContractTests:
    def test_toggle_state_changes(self):
        """Test all toggle state changes"""
        toggle = GuidedPromptToggle()
        
        # Test ON -> OFF
        toggle.set_value('OFF')
        assert toggle.get_value() == 'OFF'
        
        # Test OFF -> BYPASS_ONCE
        toggle.set_value('BYPASS_ONCE')
        assert toggle.get_value() == 'BYPASS_ONCE'
        
        # Test BYPASS_ONCE -> ALWAYS_BYPASS
        toggle.set_value('ALWAYS_BYPASS')
        assert toggle.get_value() == 'ALWAYS_BYPASS'
    
    def test_storage_persistence(self):
        """Test settings persistence across sessions"""
        # Set a value
        toggle = GuidedPromptToggle()
        toggle.set_value('OFF')
        
        # Simulate session end
        toggle.end_session()
        
        # Simulate new session
        new_toggle = GuidedPromptToggle()
        assert new_toggle.get_value() == 'OFF'
    
    def test_sync_behavior(self):
        """Test cross-device synchronization"""
        # Simulate two devices
        device1 = GuidedPromptToggle(device_id='device1')
        device2 = GuidedPromptToggle(device_id='device2')
        
        # Change setting on device1
        device1.set_value('OFF')
        
        # Sync to device2
        device2.sync_settings()
        
        # Verify sync
        assert device2.get_value() == 'OFF'
```

---

## 📚 **References**

- Overview: `docs/prompting/guided_prompt_overview.md`
- UX Flow: `docs/prompting/guided_prompt_ux_flow.md`
- Policy: `docs/prompting/guided_prompt_policy.md`
- LLM Policy: `docs/prompting/guided_prompt_llm_policy.md`
- Metrics: `docs/prompting/guided_prompt_metrics.md`
- Experiments: `docs/prompting/guided_prompt_experiments.md`
- Test Cases: `docs/prompting/guided_prompt_test_cases.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This toggle contract ensures consistent and reliable Guided Prompt Confirmation settings across all user devices and sessions.*
