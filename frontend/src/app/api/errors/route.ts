import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const errorData = await request.json();
    
    // Log the error for debugging
    console.error('[Frontend Error]', {
      timestamp: new Date().toISOString(),
      error: errorData.error,
      stack: errorData.stack,
      url: errorData.url,
      userAgent: request.headers.get('user-agent'),
    });
    
    // In production, you might want to send this to an error tracking service
    // like Sentry, LogRocket, or your own error collection service
    
    return NextResponse.json(
      { 
        success: true, 
        message: 'Error logged successfully',
        timestamp: new Date().toISOString()
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('[Error Handler] Failed to process error:', error);
    
    return NextResponse.json(
      { 
        success: false, 
        message: 'Failed to log error',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
