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

    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/queries/${queryId}/status`, {
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