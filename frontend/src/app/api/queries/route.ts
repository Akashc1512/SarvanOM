import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('page_size') || '20');

    // For now, return mock data since backend is not available
    const mockResponse = {
      queries: [
        {
          query_id: "mock_query_1",
          query: "What is artificial intelligence?",
          status: "completed",
          confidence: 0.9,
          created_at: new Date().toISOString(),
          processing_time: 2.1
        },
        {
          query_id: "mock_query_2",
          query: "How does machine learning work?",
          status: "completed",
          confidence: 0.85,
          created_at: new Date(Date.now() - 3600000).toISOString(),
          processing_time: 1.8
        }
      ],
      total: 2,
      page,
      page_size: pageSize,
      has_next: false,
      has_prev: false
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      page,
      page_size: pageSize,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Queries list error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to get queries list',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
} 