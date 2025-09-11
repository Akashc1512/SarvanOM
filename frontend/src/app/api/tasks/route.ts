import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { answer, query } = body;

    if (!answer && !query) {
      return NextResponse.json(
        { error: 'Either answer or query is required' },
        { status: 400 }
      );
    }

    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({ answer, query })
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error('Task generation error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to generate tasks',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: 'tasks',
    description: 'Generate actionable tasks from queries and answers',
    capabilities: ['task_generation', 'priority_assignment', 'status_tracking'],
    status: 'available'
  });
} 