import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const queryId = params.id;

    if (!queryId) {
      return NextResponse.json(
        { error: 'Query ID is required' },
        { status: 400 }
      );
    }

    // For now, return mock data since backend is not available
    const mockResponse = {
      query_id: queryId,
      status: "completed" as const,
      answer: "This is a mock completed query response.",
      sources: [],
      confidence: 0.85,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      llm_provider: "openai",
      llm_model: "gpt-4",
      processing_time: 2.5
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      query_id: queryId,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Query status error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to get query status',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
} 