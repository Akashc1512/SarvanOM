import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const sessionId = params.id;

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      );
    }

    // For now, return mock data since backend is not available
    const mockResponse = {
      session_id: sessionId,
      conversation_history: [
        {
          query: "What is artificial intelligence?",
          answer: "Artificial intelligence is a branch of computer science...",
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          confidence: 0.9,
          query_id: "mock_query_1",
          llm_provider: "openai",
          processing_time: 2.1
        }
      ],
      user_preferences: {
        model: "gpt-4",
        factcheck: true,
        citations: true
      }
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      session_id: sessionId,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Session state error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to get session state',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const sessionId = params.id;
    const body = await request.json();

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      );
    }

    // For now, just log the update since backend is not available
    console.log('Session state updated:', { sessionId, body });

    return NextResponse.json({
      success: true,
      data: { session_id: sessionId, ...body },
      session_id: sessionId,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Session state update error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to update session state',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
} 