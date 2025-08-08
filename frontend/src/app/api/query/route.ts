import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { query } = await request.json();

    if (!query) {
      return NextResponse.json(
        { error: "Query is required" },
        { status: 400 }
      );
    }

    // For now, return a mock response
    // In production, this would connect to your FastAPI backend
    const mockResponse = {
      query: query,
      answer: `# Search Results for "${query}"

This is a **demonstration** of how SarvanOM would display search results. In a real implementation, this would contain the actual AI-generated answer based on your query.

## Key Features

- **Markdown Rendering**: This text is rendered using React Markdown
- **Citations**: Sources are displayed with relevance scores
- **Cosmic Theme**: Beautiful space-inspired design
- **Responsive**: Works perfectly on all devices

### Example Code Block

\`\`\`javascript
// This would be actual code from the answer
function searchKnowledge(query) {
  return fetch('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query })
  });
}
\`\`\`

> This is a blockquote showing how quoted content would appear.

The system provides **intelligent answers** with proper formatting and structure.

## Real Backend Integration

To connect to your actual FastAPI backend, you would:

1. Replace this mock response with a real API call
2. Use the backend URL from environment variables
3. Handle authentication and error cases
4. Process the actual response from your AI services

\`\`\`typescript
// Example of real backend integration
const response = await fetch(\`\${process.env.BACKEND_URL}/api/query\`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': \`Bearer \${token}\`
  },
  body: JSON.stringify({ query })
});
\`\`\``,
      confidence: 0.85,
      processing_time: 1200,
      citations: [
        {
          title: "Example Source 1",
          url: "https://example.com/source1",
          snippet: "This is an example citation that would appear in the sources panel.",
          source_type: "web",
          relevance_score: 0.9,
          credibility_score: 0.8,
        },
        {
          title: "Example Source 2", 
          url: "https://example.com/source2",
          snippet: "Another example citation showing how multiple sources are displayed.",
          source_type: "academic",
          relevance_score: 0.8,
          credibility_score: 0.9,
        },
      ],
      query_id: `query_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    };

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    return NextResponse.json(mockResponse);
  } catch (error) {
    console.error("Query API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { message: "Query API endpoint - use POST to submit queries" },
    { status: 200 }
  );
}
