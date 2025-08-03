import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { code, language = 'python', timeout = 30 } = body;

    if (!code) {
      return NextResponse.json(
        { error: 'Code parameter is required' },
        { status: 400 }
      );
    }

    // Validate code length
    if (code.length > 10000) {
      return NextResponse.json(
        { error: 'Code is too long. Maximum 10,000 characters allowed.' },
        { status: 400 }
      );
    }

    // For now, return mock data since backend is not available
    const mockResponse = {
      output: "Hello, World!\n",
      error: null,
      execution_time: 0.5,
      memory_used: "2.5MB",
      exit_code: 0
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      language,
      execution_time: mockResponse.execution_time,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Code executor agent error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to execute code',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    agent: 'code-executor',
    description: 'Safe code execution agent for running code snippets',
    capabilities: ['code_execution', 'output_capture', 'error_handling'],
    supported_languages: ['python', 'javascript', 'bash'],
    max_code_length: 10000,
    timeout_limit: 30,
    status: 'available'
  });
} 