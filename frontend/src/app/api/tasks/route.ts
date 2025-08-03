import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { answer, query } = body;

    if (!answer && !query) {
      return NextResponse.json(
        { error: 'Either answer or query is required' },
        { status: 400 }
      );
    }

    // For now, return mock data since backend is not available
    const mockResponse = {
      tasks: [
        {
          task: "Research the latest developments in the field",
          priority: "high",
          status: "pending"
        },
        {
          task: "Compile a comprehensive summary of findings",
          priority: "medium",
          status: "pending"
        },
        {
          task: "Create visualizations for the data",
          priority: "low",
          status: "pending"
        }
      ],
      total_tasks: 3,
      generated_at: new Date().toISOString(),
      request_id: `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };

    return NextResponse.json({
      success: true,
      data: mockResponse,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Task generation error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to generate tasks',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    endpoint: 'tasks',
    description: 'Generate actionable tasks from queries and answers',
    capabilities: ['task_generation', 'priority_assignment', 'status_tracking'],
    status: 'available'
  });
} 