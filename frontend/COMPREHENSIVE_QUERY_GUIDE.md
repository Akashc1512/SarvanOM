# Comprehensive Query System

This guide explains the new comprehensive query system that provides advanced AI-powered research with fact-checking and citations.

## Features

### 1. Smart Query Processing
- Advanced query understanding with context-aware processing
- Real-time validation and error handling
- Debounced input to prevent excessive API calls

### 2. Fact-Checking
- Automated fact verification with confidence scoring
- Multiple source validation
- Confidence threshold management

### 3. Citation Management
- Automatic source citation with inline references
- Numbered citation format [1], [2], [3], etc.
- Clickable citation links that open source URLs
- Comprehensive sources list with metadata

## Components

### QueryInput Component
Located at `src/ui/QueryInput.tsx`

**Features:**
- Clean, modern input interface
- Loading states with spinner
- Error handling with toast notifications
- Keyboard navigation support (Enter to submit)
- Accessibility compliance

**Usage:**
```tsx
import { QueryInput } from "@/ui/QueryInput";

<QueryInput
  onQuerySubmit={(query) => console.log('Query submitted:', query)}
  onQueryUpdate={(query) => console.log('Query updated:', query)}
/>
```

### SourcesList Component
Located at `src/ui/SourcesList.tsx`

**Features:**
- Numbered list display of sources
- Source metadata (relevance, credibility, type)
- Direct links to source URLs
- Responsive design

**Usage:**
```tsx
import { SourcesList } from "@/ui/SourcesList";

<SourcesList sources={sources} />
```

### Citation Parser
Located at `src/utils/citation-parser.ts`

**Features:**
- Parses inline citations in format [n]
- Converts citations to clickable links
- Handles missing sources gracefully
- Extracts citation numbers for analysis

**Usage:**
```tsx
import { parseCitations } from "@/utils/citation-parser";

const htmlContent = parseCitations(answerText, sources);
```

## API Integration

### submitComprehensiveQuery Function
Located in `src/services/api.ts`

**Signature:**
```typescript
async submitComprehensiveQuery(
  query: string, 
  options = { factcheck: true, citations: true }
): Promise<QueryResponse>
```

**Usage:**
```typescript
import { api } from "@/services/api";

// Basic usage with default options
const response = await api.submitComprehensiveQuery("What is quantum computing?");

// Custom options
const response = await api.submitComprehensiveQuery("What is AI?", {
  factcheck: true,
  citations: false
});
```

## Demo Page

Visit `/comprehensive-query` to see the system in action.

**Features:**
- Interactive query input
- Real-time results display
- Citation parsing demonstration
- Sources list showcase
- Usage instructions

## Citation Format

The system supports inline citations in the format `[n]` where `n` is the citation number.

**Example:**
```
Quantum computing is a revolutionary technology [1] that uses quantum mechanical phenomena [2] to process information. Recent developments have shown significant progress [3] in error correction and scalability.
```

**Rendered as:**
- `[1]` becomes a clickable link to the first source
- `[2]` becomes a clickable link to the second source
- `[3]` becomes a clickable link to the third source

## Error Handling

The system includes comprehensive error handling:

1. **Network Errors**: Automatic retry with exponential backoff
2. **Validation Errors**: User-friendly error messages
3. **Rate Limiting**: Appropriate messaging and cooldown
4. **Timeout Handling**: Graceful degradation for long-running queries

## Accessibility

All components are built with accessibility in mind:

- ARIA labels and descriptions
- Keyboard navigation support
- Screen reader compatibility
- Focus management
- Semantic HTML structure

## Testing

Run the citation parser tests:

```bash
npm test citation-parser.test.ts
```

## Future Enhancements

1. **Advanced Citation Styles**: Support for different citation formats
2. **Citation Export**: Export citations in various formats (APA, MLA, etc.)
3. **Citation Analytics**: Track citation usage and impact
4. **Multi-language Support**: Internationalization for citations
5. **Citation Validation**: Verify citation accuracy and relevance

## Troubleshooting

### Common Issues

1. **Citations not appearing**: Check that the answer text contains `[n]` format citations
2. **Links not working**: Verify that sources have valid URLs
3. **Loading issues**: Check network connectivity and API endpoint availability

### Debug Mode

Enable debug logging by setting the environment variable:
```
NEXT_PUBLIC_DEBUG=true
```

This will provide detailed console output for troubleshooting. 