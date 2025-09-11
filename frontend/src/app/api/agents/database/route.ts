import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, database_type = 'postgres', limit = 100, include_schema = false } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    // Validate query for security (basic SQL injection prevention)
    const dangerousKeywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER', 'TRUNCATE'];
    const upperQuery = query.toUpperCase();
    if (dangerousKeywords.some(keyword => upperQuery.includes(keyword))) {
      return NextResponse.json(
        { error: 'Query contains potentially dangerous operations' },
        { status: 400 }
      );
    }

    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/agents/database`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({
        query,
        database_type,
        limit,
        include_schema
      })
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error('Database agent error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to execute database query',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    agent: 'database',
    description: 'Database query and analysis agent',
    capabilities: ['sql_query', 'schema_inspection', 'data_analysis', 'result_formatting'],
    supported_databases: ['postgres', 'mysql', 'sqlite'],
    max_query_length: 5000,
    timeout_limit: 30,
    read_only: true,
    status: 'available'
  });
} 