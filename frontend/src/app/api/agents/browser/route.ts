import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    // For now, return mock data since backend is not available
    const mockResponse = {
      results: [
        {
          title: "Search Result 1",
          url: "https://example.com/result1",
          snippet: "This is a mock search result for demonstration purposes.",
          relevance_score: 0.95
        },
        {
          title: "Search Result 2", 
          url: "https://example.com/result2",
          snippet: "Another mock search result with relevant information.",
          relevance_score: 0.88
        }
      ],
      total_results: 2,
      search_time: 1.2
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      query,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Browser agent error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to perform web search',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    agent: 'browser',
    description: 'Web search agent for real-time information retrieval',
    capabilities: ['web_search', 'result_summarization'],
    status: 'available'
  });
} 