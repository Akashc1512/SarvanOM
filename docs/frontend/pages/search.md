# Search Page Specification

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Frontend Team  

## Overview

The search page provides the main interface for querying SarvanOM v2 with real-time streaming results, citation tracking, and source attribution. It includes Guided Prompt Confirmation integration and fallback provider indicators.

## Page Structure

### 1. Search Interface

#### 1.1 Search Input
- **Free-text Input**: Primary search interface with autocomplete
- **Guided Prompt Integration**: Default ON, shows refinement suggestions
- **Constraint Chips**: Time range, sources, citations, cost ceiling
- **Attach Files**: Support for document and image uploads

#### 1.2 Mode Selection
- **Mode Pills**: All, Web, Vector, KG, Comprehensive
- **Visual Indicators**: Active mode highlighting
- **Budget Display**: Shows remaining time budget for current mode

### 2. Results Display

#### 2.1 Streaming Answer Card
- **Real-time Streaming**: SSE-based answer streaming
- **Inline Citations**: Clickable citation markers in text
- **Source Attribution**: Clear source labels with credibility indicators
- **Fallback Indicators**: "ⓘ via fallback" badge when keyless providers used

#### 2.2 Sources Panel
- **Grouped by Lane**: Web, Vector, KG, News, Markets
- **Provider Status**: Shows which provider was used (API key vs keyless)
- **Fallback Badge**: Clear indication when keyless fallback was used
- **Hover Details**: Passage preview on hover
- **Click Actions**: Scroll to reference, open source

#### 2.3 Lane Performance Chips
- **Time Taken**: Actual vs budget time for each lane
- **Budget Status**: Green (under budget), Yellow (close), Red (over budget)
- **Partial Results**: Flag when lane timed out but returned partial results
- **Provider Health**: Visual indicator of provider success/failure

### 3. Fallback Provider UX

#### 3.1 Provider Status Indicators
- **API Key Providers**: Standard source labels
- **Keyless Fallbacks**: "ⓘ via fallback" badge next to source name
- **Provider Chain**: Shows fallback chain (e.g., "Brave → SerpAPI → DuckDuckGo")
- **Rate Limit Indicators**: Shows when provider was rate-limited

#### 3.2 Fallback Information
- **Help Text**: "Some results from keyless sources for better coverage"
- **Toggle Option**: "Hide keyless results" in settings
- **Quality Indicators**: Shows confidence level for keyless sources
- **Attribution**: Clear labeling of keyless vs API key sources

### 4. States and Interactions

#### 4.1 Loading States
- **Empty State**: Welcome message with example queries
- **Refining State**: Guided Prompt modal with suggestions
- **Streaming State**: Real-time answer with progress indicators
- **Partial Results**: Timeout indicators with partial data
- **Error State**: Friendly error with retry options

#### 4.2 User Actions
- **Submit Query**: May trigger Guided Prompt modal
- **Accept/Edit/Skip**: Guided Prompt refinement actions
- **Copy Answer**: One-click copy with citations
- **Save Query**: Save to personal memory
- **Share Results**: Generate shareable link
- **Export**: Download as PDF/Markdown

### 5. Accessibility Features

#### 5.1 Keyboard Navigation
- **Tab Order**: Logical focus progression
- **Modal Traps**: Focus management in Guided Prompt modal
- **Escape Key**: Close modals and clear selections
- **Arrow Keys**: Navigate between results and sources

#### 5.2 Screen Reader Support
- **ARIA Labels**: All interactive elements properly labeled
- **Live Regions**: Announce streaming updates and status changes
- **Role Definitions**: Proper semantic roles for all components
- **Focus Management**: Clear focus indicators and announcements

### 6. Performance Requirements

#### 6.1 Response Times
- **TTFT**: < 1 second for first token
- **E2E Budget**: 5s (Simple), 7s (Technical), 10s (Research)
- **Pre-flight**: ≤ 800ms p95 for Guided Prompt refinement
- **Provider Timeout**: ≤ 800ms per individual provider

#### 6.2 Streaming Performance
- **Chunk Size**: Optimal chunk sizes for smooth streaming
- **Buffer Management**: Efficient handling of streaming data
- **Error Recovery**: Graceful handling of stream interruptions
- **Progressive Enhancement**: Works without JavaScript for basic functionality

### 7. Telemetry and Analytics

#### 7.1 User Interaction Events
- **Query Submitted**: Track query types and complexity
- **Refinement Actions**: Accept/edit/skip rates for Guided Prompt
- **Fallback Usage**: Track when keyless providers are used
- **Source Clicks**: Track which sources users interact with
- **Export Actions**: Track result sharing and export usage

#### 7.2 Performance Metrics
- **Response Times**: Track actual vs target response times
- **Budget Compliance**: Monitor lane budget adherence
- **Provider Health**: Track success/failure rates per provider
- **Fallback Rates**: Monitor keyless provider usage patterns

### 8. Error Handling

#### 8.1 Provider Errors
- **API Key Missing**: Graceful fallback to keyless providers
- **Rate Limiting**: Automatic fallback with user notification
- **Timeout Handling**: Partial results with clear indicators
- **Network Errors**: Retry mechanisms with exponential backoff

#### 8.2 User Communication
- **Error Messages**: Clear, actionable error descriptions
- **Fallback Notifications**: Inform users when keyless providers are used
- **Retry Options**: Easy retry mechanisms for failed requests
- **Help Links**: Contextual help for error resolution

### 9. Mobile Responsiveness

#### 9.1 Mobile Layout
- **Responsive Design**: Adapts to mobile screen sizes
- **Touch Interactions**: Optimized for touch input
- **Modal Behavior**: Sheet-style modals on mobile
- **Compact Mode**: Condensed view for smaller screens

#### 9.2 Mobile-Specific Features
- **Voice Input**: Support for voice queries
- **Camera Integration**: Document/image capture
- **Offline Support**: Basic offline functionality
- **Progressive Web App**: PWA capabilities for mobile users

---

## Implementation Notes

### Key Requirements
1. **Fallback Indicators**: Always show when keyless providers are used
2. **Provider Chain**: Display the fallback chain for transparency
3. **Budget Compliance**: Visual indicators for budget adherence
4. **Accessibility**: Full keyboard and screen reader support
5. **Performance**: Meet all response time requirements
6. **Error Handling**: Graceful degradation for all failure modes

### Integration Points
- **Guided Prompt Service**: Seamless integration with refinement suggestions
- **Observability Service**: Real-time metrics and health monitoring
- **Security Service**: PII redaction and privacy compliance
- **Analytics Service**: User behavior and performance tracking
