import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query_id, rating, feedback_text, helpful, category } = body;

    if (!query_id || rating === undefined || helpful === undefined) {
      return NextResponse.json(
        { error: 'Query ID, rating, and helpful status are required' },
        { status: 400 }
      );
    }

    // For now, just log the feedback since backend is not available
    console.log('Feedback submitted:', { query_id, rating, feedback_text, helpful, category });

    return NextResponse.json({
      success: true,
      message: 'Feedback submitted successfully',
      query_id,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Feedback submission error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to submit feedback',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: 'feedback',
    description: 'Submit feedback for queries and answers',
    capabilities: ['rating_submission', 'text_feedback', 'category_classification'],
    status: 'available'
  });
} 