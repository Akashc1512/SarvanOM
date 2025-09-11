import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const backendUrl = process.env['NEXT_PUBLIC_API_BASE_URL'] || 'http://localhost:8004';
    const response = await fetch(`${backendUrl}/system/diagnostics`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching system diagnostics:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to fetch system diagnostics',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 