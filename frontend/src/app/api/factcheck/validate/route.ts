import { NextRequest, NextResponse } from 'next/server';

interface ValidationRequest {
  claim: string;
  query_id?: string;
  expert_networks?: string[];
}

interface ValidationResponse {
  status: "supported" | "contradicted" | "unclear" | "pending";
  confidence: number;
  consensus_score: number;
  total_experts: number;
  agreeing_experts: number;
  expert_network: string;
  validation_time: string;
  details?: {
    academic_validation?: {
      status: string;
      confidence: number;
      notes: string;
    };
    industry_validation?: {
      status: string;
      confidence: number;
      notes: string;
    };
    ai_model_validation?: {
      status: string;
      confidence: number;
      notes: string;
    };
  };
  sources_checked: string[];
  reasoning: string;
}

export async function POST(request: NextRequest) {
  try {
    const body: ValidationRequest = await request.json();
    
    if (!body.claim || !body.claim.trim()) {
      return NextResponse.json(
        { error: "Claim is required" },
        { status: 400 }
      );
    }

    // Call the backend validation service
    const backendUrl = process.env['NEXT_PUBLIC_API_URL'] || "http://localhost:8004";
    const response = await fetch(`${backendUrl}/api/factcheck/validate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": request.headers.get("Authorization") || "",
      },
      body: JSON.stringify({
        claim: body.claim.trim(),
        query_id: body.query_id,
        expert_networks: body.expert_networks || ["academic", "industry", "ai_model"],
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { 
          error: "Validation failed", 
          details: errorData.error || response.statusText 
        },
        { status: response.status }
      );
    }

    const validationResult: ValidationResponse = await response.json();

    // Add timestamp if not provided
    if (!validationResult.validation_time) {
      validationResult.validation_time = new Date().toISOString();
    }

    return NextResponse.json(validationResult);

  } catch (error) {
    console.error("Expert validation error:", error);
    
    return NextResponse.json(
      { 
        error: 'Failed to validate claim',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 