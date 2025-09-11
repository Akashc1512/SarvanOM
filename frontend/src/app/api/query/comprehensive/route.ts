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

    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/query/comprehensive`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({
        query,
        context,
        user_id,
        session_id,
        model,
        preferences,
        priority,
        timeout_seconds
      })
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

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