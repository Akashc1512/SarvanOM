import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'PDF file is required' },
        { status: 400 }
      );
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return NextResponse.json(
        { error: 'Only PDF files are supported' },
        { status: 400 }
      );
    }

    // Forward request to backend API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8004';
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${backendUrl}/agents/pdf`, {
      method: 'POST',
      headers: {
        'Authorization': request.headers.get('Authorization') || '',
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error('PDF agent error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to process PDF file',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    agent: 'pdf',
    description: 'PDF document processing and analysis agent',
    capabilities: ['text_extraction', 'metadata_extraction', 'content_summarization'],
    supported_formats: ['pdf'],
    status: 'available'
  });
} 