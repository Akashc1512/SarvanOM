# Enhanced API Service with Orchestration Flags

## Overview

The API service has been enhanced to support orchestration flags for fact-checking and citations. This allows fine-grained control over the query processing pipeline.

## Enhanced Features

### 1. Orchestration Options

The `QueryRequest` interface now supports an `options` object with the following flags:

- `factcheck?: boolean` - Enable/disable fact-checking (default: `true`)
- `citations?: boolean` - Enable/disable citations (default: `true`)

### 2. Request Structure

The enhanced `submitQuery` function structures requests to match backend orchestrator expectations:

```typescript
{
  query: "Explain Knowledge Graphs",
  context: {},
  user_id: "user123",
  session_id: "session456",
  preferences: {
    factcheck: true,
    citations: true,
    priority: "normal",
    max_tokens: 1000,
    temperature: 0.7
  },
  priority: "normal",
  timeout_seconds: 30
}
```

## Usage Examples

### Basic Usage

```typescript
import { api } from './api';

// Basic query with default options
const response = await api.submitQuery({
  query: "Explain Knowledge Graphs",
  options: { factcheck: true, citations: true }
});
```

### Custom Orchestration Options

```typescript
// Query with fact-checking disabled
const response = await api.submitQuery({
  query: "What is AI?",
  options: { factcheck: false, citations: true },
  priority: "high",
  max_tokens: 1500
});
```

### Using Convenience Method

```typescript
// Using the convenience method for cleaner syntax
const response = await api.submitQueryWithOptions("Explain Quantum Computing", {
  factcheck: true,
  citations: true,
  priority: "medium",
  max_tokens: 1000,
  context: "For a beginner audience"
});
```

### Minimal Options

```typescript
// Uses default options (factcheck: true, citations: true)
const response = await api.submitQuery({
  query: "What is Machine Learning?"
});
```

## API Methods

### `submitQuery(request: QueryRequest): Promise<QueryResponse>`

Main method for submitting queries with orchestration options.

**Parameters:**
- `request.query: string` - The query string
- `request.options?: { factcheck?: boolean, citations?: boolean }` - Orchestration flags
- `request.priority?: "low" | "medium" | "high"` - Query priority
- `request.max_tokens?: number` - Maximum tokens for response
- `request.temperature?: number` - Response creativity (0.0-1.0)
- `request.context?: string` - Additional context
- `request.user_id?: string` - User identifier
- `request.workspace_id?: string` - Workspace identifier

### `submitQueryWithOptions(query: string, options: object): Promise<QueryResponse>`

Convenience method for submitting queries with explicit options.

**Parameters:**
- `query: string` - The query string
- `options: object` - All query options including orchestration flags

## Backend Integration

The enhanced API service properly structures requests to match the backend orchestrator expectations:

1. **Query Processing**: Sends requests to `/query/comprehensive` endpoint
2. **Preferences**: Includes orchestration flags in the `preferences` object
3. **Session Management**: Generates session IDs for tracking
4. **Error Handling**: Comprehensive error handling with retry logic

## Default Behavior

- **factcheck**: `true` - Fact-checking is enabled by default
- **citations**: `true` - Citations are enabled by default
- **priority**: `"normal"` - Normal priority by default
- **timeout**: `30` seconds - 30-second timeout by default

## Error Handling

The API service includes comprehensive error handling:

- **Circuit Breaker**: Prevents cascading failures
- **Retry Logic**: Automatic retries for transient failures
- **Timeout Handling**: Configurable timeouts
- **Fallback Strategies**: Graceful degradation when services are unavailable

## Testing

See `api-example.ts` for comprehensive usage examples and testing scenarios.

## Migration Guide

### From Previous Version

If you were using the previous `submitQuery` method:

```typescript
// Old way
const response = await api.submitQuery({
  query: "What is AI?",
  priority: "high"
});

// New way (same behavior, but with explicit options)
const response = await api.submitQuery({
  query: "What is AI?",
  priority: "high",
  options: { factcheck: true, citations: true } // Defaults
});
```

The new API is backward compatible - if you don't specify `options`, it will use the default values (both fact-checking and citations enabled). 