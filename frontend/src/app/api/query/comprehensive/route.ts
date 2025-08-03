import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, context, user_id, session_id, model, preferences, priority, timeout_seconds } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    // For now, return mock data since backend is not available
    const mockResponse = {
      query_id: `query_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      status: "completed" as const,
      answer: `This is a mock response for: "${query}". In a real implementation, this would be processed by the backend AI system with fact-checking and citations enabled.`,
      sources: [
        {
          title: "Mock Source 1",
          url: "https://example.com/source1",
          snippet: "This is a mock source for demonstration purposes.",
          relevance_score: 0.95,
          source_type: "web" as const,
          credibility_score: 0.9
        }
      ],
      confidence: 0.85,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      llm_provider: model || "openai",
      llm_model: model || "gpt-4",
      processing_time: 2.5
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      query,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Comprehensive query error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to process comprehensive query',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: 'comprehensive-query',
    description: 'Comprehensive query processing with fact-checking and citations',
    capabilities: ['fact_checking', 'citations', 'multi_model_support', 'context_awareness'],
    supported_models: ['openai', 'ollama', 'huggingface'],
    status: 'available'
  });
} 