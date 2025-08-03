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

    // For now, return mock data since backend is not available
    const mockResponse = {
      filename: file.name,
      file_size: file.size,
      text: 'This is a mock extracted text from the PDF.',
      metadata: {
        title: file.name,
        author: 'Mock Author',
        pages: 5
      },
      summary: 'This is a mock summary of the PDF document.'
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      filename: file.name,
      file_size: file.size,
      timestamp: new Date().toISOString()
    });

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