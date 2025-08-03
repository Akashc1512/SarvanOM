# Collaboration Features Implementation Guide

## Overview

This document describes the implementation of real-time collaboration features for the SarvanOM platform, including WebSocket-based communication, presence indicators, typing indicators, and live document synchronization.

## Architecture

### Frontend Components

#### 1. useCollaboration Hook (`frontend/src/hooks/useCollaboration.ts`)

The core collaboration hook that manages WebSocket connections and collaboration state.

**Features:**
- Automatic WebSocket connection management
- Session-based collaboration
- Presence tracking
- Typing indicators
- Message broadcasting
- Auto-reconnection with exponential backoff

**Usage:**
```typescript
import { useCollaboration } from '@/hooks/useCollaboration';

const {
  isConnected,
  collaborators,
  sendTypingIndicator,
  sendMessage,
  getOnlineCount,
} = useCollaboration({
  sessionId: 'unique-session-id',
  userId: 'current-user-id',
  onEvent: (event) => {
    // Handle collaboration events
  },
  onPresenceUpdate: (presence) => {
    // Handle presence updates
  },
});
```

#### 2. CollaborationProvider (`frontend/src/providers/collaboration-provider.tsx`)

React context provider that makes collaboration state available throughout the application.

**Features:**
- Global collaboration state management
- Automatic user identification
- Session management
- Error handling

**Usage:**
```typescript
import { CollaborationProvider } from '@/providers/collaboration-provider';

<CollaborationProvider sessionId="session-id">
  <YourApp />
</CollaborationProvider>
```

#### 3. PresenceIndicator Component (`frontend/src/ui/collaboration/PresenceIndicator.tsx`)

Visual component that displays online collaborators with avatars and typing indicators.

**Features:**
- Avatar display with fallback initials
- Typing indicators
- Online count badges
- Tooltip information
- Color-coded avatars

**Usage:**
```typescript
import { PresenceIndicator } from '@/ui/collaboration/PresenceIndicator';

<PresenceIndicator
  collaborators={collaborators}
  currentUserId={currentUserId}
  showDetails={true}
/>
```

#### 4. CollaborativeQueryForm Component (`frontend/src/ui/collaboration/CollaborativeQueryForm.tsx`)

Enhanced query form with real-time collaboration features.

**Features:**
- Real-time typing indicators
- Collaboration status display
- Live presence updates
- Debounced typing detection

**Usage:**
```typescript
import { CollaborativeQueryForm } from '@/ui/collaboration/CollaborativeQueryForm';

<CollaborativeQueryForm
  onSubmit={handleQuerySubmit}
  placeholder="Ask a question..."
/>
```

### Backend Components

#### 1. WebSocket Manager (`services/api_gateway/realtime.py`)

Comprehensive real-time communication system with multiple managers.

**Components:**
- `ConnectionManager`: Manages WebSocket connections
- `CollaborationManager`: Handles collaboration sessions
- `NotificationManager`: Manages real-time notifications
- `StreamProcessor`: Processes real-time data streams

**Features:**
- Session-based collaboration
- User presence tracking
- Document synchronization
- Cursor position updates
- Typing indicators
- Message broadcasting

#### 2. WebSocket Endpoint (`services/api_gateway/main.py`)

FastAPI WebSocket endpoint for real-time communication.

**Endpoint:** `/ws/collaboration`

**Message Types:**
- `join_session`: Join a collaboration session
- `leave_session`: Leave a collaboration session
- `editing_state`: Update typing indicator
- `cursor_update`: Update cursor position
- `update_document`: Update document content
- `new_message`: Send a new message

## Implementation Details

### Message Flow

1. **Connection Establishment:**
   ```
   Client → WebSocket Connect → Server Accept → Join Session → Session Confirmation
   ```

2. **Typing Indicator:**
   ```
   User Types → Debounced Event → WebSocket Message → Server Broadcast → Other Clients
   ```

3. **Message Broadcasting:**
   ```
   User Sends Message → WebSocket → Server Process → Broadcast to Session → All Clients
   ```

4. **Presence Updates:**
   ```
   User Joins/Leaves → Server Update → Broadcast Presence → Update UI
   ```

### State Management

#### Frontend State
```typescript
interface CollaboratorPresence {
  userId: string;
  isTyping: boolean;
  cursorPosition?: number;
  lastSeen: string;
  avatar?: string;
  name?: string;
}

interface CollaborationEvent {
  type: 'new_message' | 'editing_state' | 'user_joined' | 'user_left' | 'cursor_update' | 'document_update';
  data: any;
  userId?: string;
  sessionId?: string;
  timestamp: string;
}
```

#### Backend State
```python
class CollaborationManager:
    collaboration_sessions: Dict[str, Dict[str, Any]]
    user_cursors: Dict[str, Dict[str, Any]]
    document_versions: Dict[str, int]
```

### Error Handling

#### Frontend
- Automatic reconnection with exponential backoff
- Connection state monitoring
- Graceful degradation when WebSocket unavailable
- User-friendly error messages

#### Backend
- Connection validation
- Session management
- Message validation
- Error broadcasting to clients

## Testing

### Manual Testing

1. **Open Collaboration Demo:**
   - Navigate to `/collaboration-demo`
   - Copy the session ID
   - Open the same URL in another browser tab
   - Test real-time features

2. **Test Features:**
   - Typing indicators
   - Message broadcasting
   - Presence updates
   - Cursor synchronization
   - Connection stability

### Automated Testing

Run the comprehensive test script:
```bash
python test_collaboration_features.py
```

**Test Coverage:**
- Basic WebSocket connections
- Multi-user sessions
- Typing indicators
- Message broadcasting
- Cursor updates
- Presence management

## Integration Examples

### 1. Basic Integration

```typescript
import { useCollaboration } from '@/hooks/useCollaboration';

function MyComponent() {
  const { isConnected, collaborators, sendMessage } = useCollaboration({
    sessionId: 'my-session',
    onEvent: (event) => {
      console.log('Collaboration event:', event);
    },
  });

  return (
    <div>
      {isConnected && <div>Connected to collaboration</div>}
      <div>Online: {collaborators.length}</div>
    </div>
  );
}
```

### 2. Enhanced Query Form

```typescript
import { CollaborativeQueryForm } from '@/ui/collaboration/CollaborativeQueryForm';

function QueryPage() {
  return (
    <CollaborationProvider sessionId="query-session">
      <CollaborativeQueryForm
        onSubmit={handleQuery}
        placeholder="Ask a question..."
      />
    </CollaborationProvider>
  );
}
```

### 3. Presence Integration

```typescript
import { PresenceIndicator } from '@/ui/collaboration/PresenceIndicator';
import { useCollaborationContext } from '@/providers/collaboration-provider';

function Header() {
  const { collaborators, currentUserId } = useCollaborationContext();
  
  return (
    <header>
      <PresenceIndicator
        collaborators={collaborators}
        currentUserId={currentUserId}
      />
    </header>
  );
}
```

## Configuration

### Environment Variables

```bash
# WebSocket URL
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Backend WebSocket settings
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8000
```

### Backend Configuration

```python
# services/api_gateway/realtime.py
WEBSOCKET_SETTINGS = {
    'max_connections': 1000,
    'message_queue_size': 100,
    'heartbeat_interval': 30,
    'connection_timeout': 300,
}
```

## Performance Considerations

### Frontend
- Debounced typing indicators (500ms)
- Efficient re-rendering with React.memo
- Connection pooling
- Message batching

### Backend
- Connection pooling
- Message queuing
- Efficient broadcasting
- Memory management
- Scalable architecture

## Security

### Authentication
- Session-based authentication
- User validation
- Permission checking
- Rate limiting

### Data Protection
- Message validation
- Input sanitization
- XSS prevention
- CSRF protection

## Monitoring

### Metrics
- Active connections
- Message throughput
- Error rates
- Response times
- User engagement

### Logging
- Connection events
- Message flow
- Error tracking
- Performance metrics

## Troubleshooting

### Common Issues

1. **Connection Failed:**
   - Check WebSocket URL
   - Verify backend is running
   - Check firewall settings

2. **Messages Not Broadcasting:**
   - Verify session ID
   - Check user permissions
   - Validate message format

3. **Typing Indicators Not Working:**
   - Check debounce settings
   - Verify event handlers
   - Check WebSocket connection

### Debug Tools

1. **Browser DevTools:**
   - WebSocket tab for connection monitoring
   - Console for error messages
   - Network tab for message flow

2. **Backend Logs:**
   - Connection events
   - Message processing
   - Error details

## Future Enhancements

### Planned Features
- Document versioning
- Conflict resolution
- Offline support
- Mobile optimization
- Advanced presence features
- File sharing
- Voice/video integration

### Scalability Improvements
- Redis clustering
- Load balancing
- Microservices architecture
- CDN integration
- Edge computing

## Conclusion

The collaboration features provide a robust foundation for real-time collaborative experiences in the SarvanOM platform. The implementation follows best practices for WebSocket communication, state management, and user experience design.

For questions or issues, refer to the test script and demo page for examples of proper usage. 