import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const startTime = Date.now();
    
    // Basic health check
    const healthStatus = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: process.env.npm_package_version || '1.0.0',
      checks: {
        frontend: 'healthy',
        api: 'healthy',
        database: 'unknown', // Will be checked if backend is available
        llm_providers: 'unknown'
      }
    };

    // Try to check backend services if available
    try {
      const backendHealthResponse = await fetch('http://localhost:8000/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });

      if (backendHealthResponse.ok) {
        const backendHealth = await backendHealthResponse.json();
        healthStatus.checks.database = backendHealth.database || 'healthy';
        healthStatus.checks.llm_providers = backendHealth.llm_providers || 'healthy';
      } else {
        healthStatus.checks.database = 'unavailable';
        healthStatus.checks.llm_providers = 'unavailable';
      }
    } catch (error) {
      healthStatus.checks.database = 'unavailable';
      healthStatus.checks.llm_providers = 'unavailable';
    }

    const responseTime = Date.now() - startTime;
    
    return NextResponse.json({
      ...healthStatus,
      response_time_ms: responseTime,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    }, {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });

  } catch (error) {
    console.error('Health check failed:', error);
    
    return NextResponse.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: 'Health check failed',
      checks: {
        frontend: 'unhealthy',
        api: 'unhealthy',
        database: 'unknown',
        llm_providers: 'unknown'
      }
    }, {
      status: 503,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    });
  }
}

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
}
