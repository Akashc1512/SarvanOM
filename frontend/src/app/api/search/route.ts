/**
 * Search API Route
 * 
 * Handles search requests and integrates with the backend retrieval service.
 */

import { NextRequest, NextResponse } from 'next/server';

interface SearchRequest {
  query: string;
  filters?: Record<string, any>;
  limit?: number;
  offset?: number;
}

interface SearchResult {
  id: string;
  title: string;
  content: string;
  source: string;
  url: string;
  relevance_score: number;
  timestamp: string;
  type: 'web' | 'document' | 'knowledge' | 'news';
}

interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  search_time: number;
  sources_used: string[];
}

export async function POST(request: NextRequest) {
  try {
    const body: SearchRequest = await request.json();
    const { query, filters, limit = 10, offset = 0 } = body;

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required and must be a string' },
        { status: 400 }
      );
    }

    // Call the backend retrieval service
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/retrieval/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({
        query,
        filters,
        limit,
        offset
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend retrieval service error: ${response.status}`);
    }

    const data = await response.json();

    // Transform the response to match our interface
    const searchResponse: SearchResponse = {
      results: data.results || [],
      total: data.total || 0,
      query,
      search_time: data.search_time || 0,
      sources_used: data.sources_used || []
    };

    return NextResponse.json(searchResponse);
  } catch (error) {
    console.error('Search API error:', error);
    
    return NextResponse.json(
      { 
        error: 'Search failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405 }
  );
}
