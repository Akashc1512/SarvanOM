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

    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/state/${sessionId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      }
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

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