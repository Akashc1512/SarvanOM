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

    // For now, return mock data since backend is not available
    const mockResponse = {
      entities: [
        {
          id: "entity_1",
          name: "Artificial Intelligence",
          type: "concept",
          properties: { description: "Machine intelligence" },
          confidence: 0.95
        },
        {
          id: "entity_2",
          name: "Machine Learning",
          type: "technology",
          properties: { description: "Subset of AI" },
          confidence: 0.9
        }
      ],
      relationships: [
        {
          source_id: "entity_1",
          target_id: "entity_2",
          relationship_type: "includes",
          properties: { strength: "strong" },
          confidence: 0.85
        }
      ],
      paths: [],
      query_entities: [query],
      confidence: 0.9,
      processing_time_ms: 1500,
      metadata: { query_type: query_type || 'entity_search' }
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      query,
      query_type,
      timestamp: new Date().toISOString()
    });

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