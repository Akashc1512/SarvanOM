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

    // For now, return mock data since backend is not available
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

    return NextResponse.json({
      success: true,
      data: mockResponse,
      query,
      query_type,
      timestamp: new Date().toISOString()
    });

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