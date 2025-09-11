import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, query_type, max_entities, max_relationships } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }


    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/knowledge-graph/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({ query, query_type })
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error('Knowledge graph query error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to query knowledge graph',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: 'knowledge-graph-query',
    description: 'Query the knowledge graph for entities and relationships',
    capabilities: ['entity_search', 'relationship_query', 'graph_traversal'],
    query_types: ['entity_search', 'relationship_query', 'path_finding'],
    status: 'available'
  });
} 