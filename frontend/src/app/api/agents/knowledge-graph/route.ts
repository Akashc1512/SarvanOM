import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, query_type = 'entity_search', max_entities = 10, max_relationships = 5 } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter is required' },
        { status: 400 }
      );
    }

    const mockResponse = {
      entities: [
        {
          id: "entity_1",
          name: "Knowledge Graph",
          type: "concept",
          properties: { description: "Graph-based knowledge representation" },
          confidence: 0.95
        }
      ],
      relationships: [
        {
          source_id: "entity_1",
          target_id: "entity_2",
          relationship_type: "related_to",
          properties: { strength: "strong" },
          confidence: 0.85
        }
      ],
      query_entities: [query],
      confidence: 0.9,
      processing_time_ms: 1200
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
    console.error('Knowledge graph agent error:', error);
    
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
    agent: 'knowledge-graph',
    description: 'Knowledge graph query and exploration agent',
    capabilities: ['entity_search', 'relationship_query', 'graph_traversal', 'metadata_retrieval'],
    query_types: ['entity_search', 'relationship_query', 'path_finding', 'similarity_search'],
    max_entities: 50,
    max_relationships: 20,
    status: 'available'
  });
} 