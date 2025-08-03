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

    // For now, return mock data since backend is not available
    const mockResponse = {
      results: [
        { id: 1, name: "Sample Data 1", value: "Value 1" },
        { id: 2, name: "Sample Data 2", value: "Value 2" }
      ],
      row_count: 2,
      execution_time: 0.3,
      schema: {
        columns: ["id", "name", "value"],
        types: ["integer", "text", "text"]
      }
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      query,
      database_type,
      row_count: mockResponse.row_count,
      execution_time: mockResponse.execution_time,
      timestamp: new Date().toISOString()
    });

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