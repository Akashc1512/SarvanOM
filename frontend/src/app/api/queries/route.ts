import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('page_size') || '20');

    // Since backend doesn't have a /queries endpoint, return a simple response
    // This could be enhanced to call a proper queries endpoint when available
    const response = {
      queries: [],
      total: 0,
      page,
      page_size: pageSize,
      has_next: false,
      has_prev: false,
      message: "Queries endpoint not yet implemented in backend"
    };

    return NextResponse.json(response);

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