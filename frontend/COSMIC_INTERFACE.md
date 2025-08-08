# SarvanOM Cosmic Interface

## Overview

This document describes the new cosmic-themed interface for SarvanOM, implementing a MAANG-grade user experience with space-inspired design elements.

## Key Components

### 1. Theme Toggle (`/src/ui/ThemeToggle.tsx`)
- **Purpose**: Allows users to switch between light and dark cosmic themes
- **Features**: 
  - Smooth animations with cosmic particle effects
  - Persistent theme preference in localStorage
  - Responsive design with different sizes
  - Accessible with proper ARIA labels

### 2. Search Page (`/src/app/search/page.tsx`)
- **Purpose**: Main entry point for user queries
- **Features**:
  - Centered search interface with cosmic background
  - Example queries for user guidance
  - Responsive design for all devices
  - Loading states with cosmic animations

### 3. Results Page (`/src/app/search/results/page.tsx`)
- **Purpose**: Displays search results with full markdown support
- **Features**:
  - React Markdown rendering with syntax highlighting
  - Citation display with relevance scores
  - Copy and share functionality
  - Feedback buttons for answer quality
  - Error handling with graceful fallbacks

### 4. Cosmic Loader (`/src/ui/CosmicLoader.tsx`)
- **Purpose**: Consistent loading states throughout the app
- **Features**:
  - Animated sparkles and particles
  - Multiple sizes (sm, md, lg)
  - Customizable text messages
  - Dark/light theme support

### 5. Navigation (`/src/ui/navigation/MainNav.tsx`)
- **Purpose**: Updated navigation with cosmic branding
- **Features**:
  - Sticky navigation with backdrop blur
  - Cosmic logo with animated elements
  - Theme toggle integration
  - Mobile-responsive design

### 6. Voice Search (`/src/ui/VoiceSearch.tsx`)
- **Purpose**: Speech-to-text functionality for hands-free searching
- **Features**:
  - Real-time speech recognition with confidence indicators
  - Live transcript preview
  - Error handling for unsupported browsers
  - Cosmic styling with recording animations
  - Accessibility support with ARIA labels

### 7. Advanced Particles (`/src/ui/CosmicParticles.tsx`)
- **Purpose**: Complex particle systems for immersive backgrounds
- **Features**:
  - Interactive particle effects with mouse attraction
  - Multiple themes (purple, blue, mixed)
  - Performance optimized with intersection observer
  - Canvas-based rendering for smooth animations
  - Pre-built effects: StarField, NebulaEffect, ConstellationEffect

### 8. Theme Selector (`/src/ui/ThemeSelector.tsx`)
- **Purpose**: User-selectable cosmic themes with previews
- **Features**:
  - 6 different cosmic themes (Cosmic Purple, Nebula Blue, Aurora Borealis, etc.)
  - Live theme previews with particle count and speed
  - Persistent theme selection in localStorage
  - Smooth theme transitions
  - Color palette previews for each theme

### 9. Collaboration Panel (`/src/ui/CollaborationPanel.tsx`)
- **Purpose**: Real-time collaboration features with user presence and cursor tracking
- **Features**:
  - Live user presence indicators with avatars and status
  - Real-time cursor position tracking across all users
  - Session sharing controls (audio, video, screen)
  - User permission management (view, edit, admin)
  - Invite system with email integration
  - Floating action button with online user count

### 10. Collaboration Chat (`/src/ui/CollaborationChat.tsx`)
- **Purpose**: Real-time messaging system for team collaboration
- **Features**:
  - Live chat with typing indicators
  - Message history with timestamps
  - User avatars and message bubbles
  - System messages for user join/leave events
  - Auto-scroll to latest messages
  - Connection status indicators

### 11. Collaboration Provider (`/src/providers/collaboration-provider.tsx`)
- **Purpose**: Global state management for collaboration features
- **Features**:
  - Session management (join/leave)
  - Real-time state synchronization
  - User presence tracking
  - Message broadcasting
  - Permission management
  - Toast notifications for collaboration events

## Design System

### Color Palette
- **Primary**: Purple (#8B5CF6) to Blue (#3B82F6) gradients
- **Background**: Slate gradients with cosmic transparency
- **Text**: Gray scale with proper contrast ratios
- **Accents**: Purple and blue for interactive elements

### Typography
- **Headings**: Bold with gradient text effects
- **Body**: Clean, readable fonts with proper spacing
- **Code**: Syntax highlighting with cosmic theme

### Animations
- **Particles**: Floating dots with pulse animations
- **Transitions**: Smooth 300-500ms duration
- **Hover Effects**: Scale and glow effects
- **Loading**: Bouncing dots and spinning elements

## Implementation Notes

### Backend Integration
The current implementation uses mock data. To connect to the actual FastAPI backend:

1. Update `/src/app/api/query/route.ts` to call your backend services
2. Replace mock responses with real API calls
3. Handle authentication and error cases
4. Implement proper CORS configuration

### Performance Optimizations
- Lazy loading for heavy components
- Image optimization with Next.js Image component
- Bundle splitting for better load times
- Caching strategies for repeat queries

### Accessibility
- Proper ARIA labels on all interactive elements
- Keyboard navigation support
- High contrast mode compatibility
- Screen reader friendly markup

## Usage Examples

### Adding the Theme Toggle
```tsx
import { ThemeToggle } from "@/ui/ThemeToggle";

<ThemeToggle size="sm" className="ml-auto" />
```

### Using the Cosmic Loader
```tsx
import { CosmicLoader } from "@/ui/CosmicLoader";

<CosmicLoader 
  size="md" 
  text="Loading your results..." 
  className="my-8" 
/>
```

### Using Voice Search
```tsx
import { VoiceSearch } from "@/ui/VoiceSearch";

<VoiceSearch
  onTranscript={(transcript) => setQuery(transcript)}
  size="sm"
  className="ml-2"
/>
```

### Using Advanced Particles
```tsx
import { StarField, NebulaEffect } from "@/ui/CosmicParticles";

<div className="relative">
  <StarField />
  <NebulaEffect />
  {/* Your content */}
</div>
```

### Using Theme Selector
```tsx
import { ThemeSelector } from "@/ui/ThemeSelector";

<ThemeSelector
  onThemeChange={(theme) => console.log('Theme changed:', theme.name)}
/>
```

### Using Collaboration Panel
```tsx
import { CollaborationPanel } from "@/ui/CollaborationPanel";

<CollaborationPanel
  sessionId="my-session-123"
  onInvite={(email) => console.log('Inviting:', email)}
  onPermissionChange={(userId, permission) => console.log('Permission changed:', userId, permission)}
/>
```

### Using Collaboration Chat
```tsx
import { CollaborationChat, useCollaborationChat } from "@/ui/CollaborationChat";

function MyComponent() {
  const { isOpen, toggleChat } = useCollaborationChat();
  
  return (
    <div>
      <button onClick={toggleChat}>Toggle Chat</button>
      <CollaborationChat isOpen={isOpen} onToggle={toggleChat} />
    </div>
  );
}
```

### Using Collaboration Provider
```tsx
import { useCollaboration } from "@/providers/collaboration-provider";

function MyComponent() {
  const { 
    isConnected, 
    sessionId, 
    collaborators,
    joinSession, 
    leaveSession,
    sendMessage 
  } = useCollaboration();
  
  return (
    <div>
      <p>Connected: {isConnected ? 'Yes' : 'No'}</p>
      <p>Online users: {collaborators.filter(c => c.isOnline).length}</p>
      <button onClick={() => joinSession('my-session')}>Join Session</button>
    </div>
  );
}
```

### Creating a Cosmic Card
```tsx
<Card className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50">
  <CardContent className="p-6">
    {/* Your content */}
  </CardContent>
</Card>
```

## Future Enhancements

1. **AR Elements**: Augmented reality features for immersive search
2. **Advanced AI Integration**: Real-time conversation with AI agents
3. **Gesture Controls**: Touch and motion-based interactions
4. **Holographic Effects**: 3D visual elements and depth
5. **Advanced Cursor Tracking**: More sophisticated cursor visualization and interaction
6. **Screen Sharing**: Real-time screen sharing capabilities
7. **Voice Chat**: Integrated voice communication
8. **File Sharing**: Collaborative file upload and sharing

## Development Guidelines

1. **Consistency**: Use the cosmic design system throughout
2. **Performance**: Optimize animations and transitions
3. **Accessibility**: Maintain WCAG compliance
4. **Responsive**: Test on all device sizes
5. **Testing**: Include component and integration tests

## Troubleshooting

### Common Issues
- **Hydration Mismatch**: Ensure client-side only components are properly marked
- **Theme Persistence**: Check localStorage implementation
- **Animation Performance**: Use `transform` and `opacity` for smooth animations
- **Mobile Responsiveness**: Test on actual devices, not just dev tools

### Debug Tips
- Use browser dev tools to inspect cosmic elements
- Check console for theme-related errors
- Verify API endpoints are accessible
- Test with different screen sizes and orientations
