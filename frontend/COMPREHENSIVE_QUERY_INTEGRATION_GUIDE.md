# Comprehensive Query Integration Guide

## Overview

This guide documents the integration of the comprehensive query feature that combines AI-powered research with fact-checking and automatic citation generation.

## Features

### 1. Comprehensive Query Processing
- **Endpoint**: `/query/comprehensive`
- **Method**: POST
- **Features**: 
  - Fact-checking with confidence scoring
  - Automatic citation generation
  - Inline citation parsing `[1]`, `[2]`, etc.
  - Source management with relevance scoring

### 2. Frontend Components

#### QueryForm Component
- **Location**: `frontend/src/ui/QueryForm.tsx`
- **Function**: Handles query submission with comprehensive options
- **Integration**: Uses `api.submitComprehensiveQuery()` with fact-checking and citations enabled

```typescript
// Example usage
const response = await api.submitComprehensiveQuery(query.trim(), {
  factcheck: true,
  citations: true,
});
```

#### AnswerDisplay Component
- **Location**: `frontend/src/ui/AnswerDisplay.tsx`
- **Function**: Displays answers with parsed citations
- **Features**:
  - Inline citation parsing with clickable links
  - Source list display
  - Confidence score visualization
  - Feedback collection

#### SourcesList Component
- **Location**: `frontend/src/ui/SourcesList.tsx`
- **Function**: Displays numbered source list with metadata
- **Features**:
  - Relevance scoring display
  - Credibility scoring (if available)
  - Source type classification
  - Direct link to sources

### 3. State Management

#### Query Store (Zustand)
- **Location**: `frontend/src/state/query-store.ts`
- **Function**: Global state management for queries
- **Features**:
  - Current query tracking
  - Recent queries history
  - Polling for status updates
  - Error handling

### 4. Citation Parsing

#### Citation Parser Utility
- **Location**: `frontend/src/utils/citation-parser.ts`
- **Function**: Converts `[n]` citations to clickable HTML links
- **Features**:
  - Regex-based citation detection
  - HTML link generation
  - Fallback for missing sources

```typescript
// Example: Parse citations in answer text
const parsedAnswer = parseCitations(answer, sources);
```

## API Integration

### Request Format
```typescript
interface ComprehensiveQueryRequest {
  query: string;
  context?: string;
  preferences: {
    factcheck: boolean;
    citations: boolean;
    priority: "low" | "medium" | "high";
  };
}
```

### Response Format
```typescript
interface ComprehensiveQueryResponse {
  query_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  answer?: string;
  sources?: Source[];
  confidence?: number;
  created_at: string;
  updated_at: string;
}
```

## User Flow

1. **Query Submission**
   - User enters research question
   - QueryForm submits to `/query/comprehensive`
   - Backend processes with fact-checking and citations

2. **Answer Display**
   - AnswerDisplay renders parsed answer with inline citations
   - SourcesList shows numbered source references
   - Confidence score indicates fact-checking results

3. **Citation Interaction**
   - Clickable `[1]`, `[2]` citations link to sources
   - Sources list provides detailed metadata
   - Direct links to original sources

## Testing

### Manual Testing
1. Navigate to `/comprehensive-query`
2. Submit a research question
3. Verify answer contains inline citations
4. Check sources list for references
5. Test citation link functionality

### Automated Testing
```bash
# Run the integration test
node frontend/test_comprehensive_integration.js
```

## Error Handling

### Frontend Error Handling
- Network error detection and retry logic
- User-friendly error messages
- Graceful degradation for offline scenarios
- Circuit breaker pattern for API failures

### Backend Error Handling
- Validation error responses
- Processing timeout handling
- Source availability fallbacks
- Confidence score calculation errors

## Performance Considerations

### Frontend Optimizations
- Debounced input validation
- Memoized component rendering
- Efficient state updates
- Optimized polling intervals

### Backend Optimizations
- Async processing for long queries
- Caching of fact-checking results
- Source relevance scoring
- Response streaming for large answers

## Security Considerations

### Input Validation
- Query length limits
- Content sanitization
- Rate limiting
- Authentication requirements

### Output Sanitization
- HTML injection prevention
- XSS protection for parsed citations
- Safe external link handling

## Monitoring and Analytics

### Metrics to Track
- Query submission success rate
- Processing time distribution
- Citation accuracy
- User feedback scores
- Source relevance ratings

### Logging
- Query processing events
- Error occurrences
- Performance metrics
- User interaction patterns

## Future Enhancements

### Planned Features
- Advanced citation formatting (APA, MLA, etc.)
- Collaborative fact-checking
- Source credibility scoring
- Multi-language support
- Real-time collaboration

### Technical Improvements
- WebSocket integration for real-time updates
- Advanced caching strategies
- Machine learning for citation relevance
- Enhanced error recovery mechanisms

## Troubleshooting

### Common Issues

1. **Citations not appearing**
   - Check backend citation generation
   - Verify citation parser utility
   - Ensure sources are properly formatted

2. **Fact-checking not working**
   - Verify fact-checking service status
   - Check confidence score calculation
   - Review fact-checking agent logs

3. **Sources not loading**
   - Check source retrieval service
   - Verify URL accessibility
   - Review source relevance scoring

### Debug Commands
```bash
# Check API health
curl http://localhost:8000/health

# Test comprehensive query endpoint
curl -X POST http://localhost:8000/query/comprehensive \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "preferences": {"factcheck": true, "citations": true}}'

# Check frontend build
npm run build
```

## Conclusion

The comprehensive query integration provides a robust foundation for AI-powered research with fact-checking and citations. The modular architecture allows for easy extension and maintenance while providing a smooth user experience.

For questions or issues, refer to the backend integration documentation and API reference guides. 