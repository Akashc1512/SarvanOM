import { NextRequest, NextResponse } from 'next/server';
import { api } from '@/services/api';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { url, depth = 1, max_pages = 10, extract_text = true } = body;

    if (!url) {
      return NextResponse.json(
        { error: 'URL parameter is required' },
        { status: 400 }
      );
    }

    // Validate URL format
    try {
      new URL(url);
    } catch {
      return NextResponse.json(
        { error: 'Invalid URL format' },
        { status: 400 }
      );
    }

    // Call the backend web crawler agent
    const response = await api.makeRequest<any>('post', '/agents/web-crawler/crawl', {
      url,
      depth,
      max_pages,
      extract_text,
      follow_links: true,
      respect_robots_txt: true,
      user_agent: 'SarvanomBot/1.0'
    });

    return NextResponse.json({
      success: true,
      data: response.data,
      url,
      pages_crawled: response.data.pages_crawled,
      total_size: response.data.total_size,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Web crawler agent error:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to crawl web page',
        details: error.message || 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    agent: 'web-crawler',
    description: 'Web crawling and indexing agent',
    capabilities: ['url_crawling', 'text_extraction', 'link_following', 'content_indexing'],
    max_depth: 3,
    max_pages: 50,
    supported_protocols: ['http', 'https'],
    respect_robots_txt: true,
    status: 'available'
  });
} 