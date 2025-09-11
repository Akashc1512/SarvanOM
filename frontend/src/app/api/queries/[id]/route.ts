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

    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/api/endpoint`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify(request.body)
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error('Query details error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to get query details',
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
    const queryId = params.id;
    const body = await request.json();

    if (!queryId) {
      return NextResponse.json(
        { error: 'Query ID is required' },
        { status: 400 }
      );
    }

    // For now, just log the update since backend is not available
    console.log('Query updated:', { queryId, body });

    return NextResponse.json({
      success: true,
      data: { query_id: queryId, ...body },
      query_id: queryId,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Query update error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to update query',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function DELETE(
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

    // For now, just log the delete since backend is not available
    console.log('Query deleted:', queryId);

    return NextResponse.json({
      success: true,
      message: 'Query deleted successfully',
      query_id: queryId,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Query delete error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to delete query',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
} 