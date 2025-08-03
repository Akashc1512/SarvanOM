import { NextRequest, NextResponse } from 'next/server';

// Mock data for demonstration purposes
const mockPendingReviews = [
  {
    id: '1',
    query: 'What are the main benefits of machine learning in healthcare?',
    answerSnippet: 'Machine learning in healthcare offers improved diagnosis accuracy, personalized treatment plans, and predictive analytics for patient outcomes. It can help identify patterns in medical data that humans might miss, leading to earlier disease detection and more effective treatments.',
    confidence: 0.85,
    createdAt: new Date().toISOString(),
    status: 'pending' as const,
    expertComments: undefined
  },
  {
    id: '2',
    query: 'How does blockchain technology work?',
    answerSnippet: 'Blockchain is a distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography. Each block contains a cryptographic hash of the previous block, a timestamp, and transaction data.',
    confidence: 0.72,
    createdAt: new Date().toISOString(),
    status: 'pending' as const,
    expertComments: undefined
  },
  {
    id: '3',
    query: 'What is the difference between supervised and unsupervised learning?',
    answerSnippet: 'Supervised learning uses labeled training data to learn patterns and make predictions, while unsupervised learning finds hidden patterns in unlabeled data. Supervised learning is used for classification and regression tasks, while unsupervised learning is used for clustering and dimensionality reduction.',
    confidence: 0.91,
    createdAt: new Date().toISOString(),
    status: 'pending' as const,
    expertComments: undefined
  }
];

export async function GET(request: NextRequest) {
  try {
    // In a real application, you would fetch this data from your database
    // For now, we'll return mock data
    return NextResponse.json(mockPendingReviews);
  } catch (error) {
    console.error('Error fetching pending reviews:', error);
    return NextResponse.json(
      { error: 'Failed to fetch pending reviews' },
      { status: 500 }
    );
  }
} 