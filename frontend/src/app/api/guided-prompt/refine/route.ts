/**
 * Guided Prompt Refinement API Route
 * 
 * Handles query refinement requests for the Guided Prompt Confirmation feature.
 * Integrates with the backend guided-prompt service.
 */

import { NextRequest, NextResponse } from 'next/server';

interface RefinementRequest {
  query: string;
  context?: string;
  user_preferences?: Record<string, any>;
}

interface RefinementSuggestion {
  id: string;
  title: string;
  description: string;
  refined_query: string;
  type: 'refine' | 'disambiguate' | 'decompose' | 'constrain' | 'sanitize';
  confidence: number;
  reasoning: string;
}

interface ConstraintChip {
  id: string;
  label: string;
  type: 'select' | 'boolean';
  options: string[];
  selected?: string;
}

interface RefinementResponse {
  refinements: RefinementSuggestion[];
  constraints: ConstraintChip[];
  original_query: string;
  processing_time: number;
}

export async function POST(request: NextRequest) {
  try {
    const body: RefinementRequest = await request.json();
    const { query, context, user_preferences } = body;

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required and must be a string' },
        { status: 400 }
      );
    }

    // Call the backend guided-prompt service
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/guided-prompt/refine`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: JSON.stringify({
        query,
        context,
        user_preferences
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend guided-prompt service error: ${response.status}`);
    }

    const data = await response.json();

    // Transform the response to match our interface
    const refinementResponse: RefinementResponse = {
      refinements: data.refinements || [],
      constraints: data.constraints || [],
      original_query: query,
      processing_time: data.processing_time || 0
    };

    return NextResponse.json(refinementResponse);
  } catch (error) {
    console.error('Guided prompt refinement error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to refine query',
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
