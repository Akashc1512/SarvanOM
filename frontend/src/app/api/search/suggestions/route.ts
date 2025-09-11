/**
 * Search Suggestions API Route
 * 
 * Provides search suggestions based on query input.
 */

import { NextRequest, NextResponse } from 'next/server';

interface SuggestionsRequest {
  q: string;
  limit?: number;
}

interface SuggestionsResponse {
  suggestions: string[];
  query: string;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q');
    const limit = parseInt(searchParams.get('limit') || '5');

    if (!query || query.length < 2) {
      return NextResponse.json(
        { suggestions: [], query: query || '' },
        { status: 200 }
      );
    }

    // Mock suggestions - in real implementation, this would come from a search service
    const mockSuggestions = [
      'What is machine learning?',
      'How does quantum computing work?',
      'Latest news about artificial intelligence',
      'Compare different programming languages',
      'Explain blockchain technology',
      'What are the benefits of renewable energy?',
      'How to improve productivity at work?',
      'Best practices for software development',
      'Climate change impact on environment',
      'Future of electric vehicles'
    ];

    // Filter suggestions based on query
    const filteredSuggestions = mockSuggestions
      .filter(suggestion => 
        suggestion.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, limit);

    const response: SuggestionsResponse = {
      suggestions: filteredSuggestions,
      query
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Search suggestions error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to get suggestions',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function POST() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405 }
  );
}
