import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();
    const { verdict, comment } = body;

    // Validate the request
    if (!verdict || !['approved', 'rejected'].includes(verdict)) {
      return NextResponse.json(
        { error: 'Invalid verdict. Must be "approved" or "rejected"' },
        { status: 400 }
      );
    }

    // In a real application, you would:
    // 1. Validate the review ID exists
    // 2. Update the review status in your database
    // 3. Store the expert comment
    // 4. Trigger any necessary notifications or workflows
    // 5. Update the factcheck service with the expert's decision

    console.log(`Review ${id} ${verdict} with comment: ${comment || 'No comment'}`);

    // Mock successful response
    return NextResponse.json({
      success: true,
      reviewId: id,
      verdict,
      comment,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error submitting review:', error);
    return NextResponse.json(
      { error: 'Failed to submit review' },
      { status: 500 }
    );
  }
} 