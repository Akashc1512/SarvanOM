import { NextRequest, NextResponse } from 'next/server';

// Mock data for demonstration - in production this would come from a database
const mockMemoryItems = [
  {
    id: '1',
    title: 'Machine Learning Fundamentals',
    summary: 'Core concepts and principles of machine learning including supervised, unsupervised, and reinforcement learning.',
    content: `Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. Here are the key concepts:

1. Supervised Learning
- Uses labeled training data
- Examples: classification, regression
- Algorithms: Linear Regression, Random Forest, Neural Networks

2. Unsupervised Learning
- Works with unlabeled data
- Examples: clustering, dimensionality reduction
- Algorithms: K-means, PCA, Autoencoders

3. Reinforcement Learning
- Learning through interaction with environment
- Examples: game playing, robotics
- Algorithms: Q-learning, Deep Q-Networks

Key Principles:
- Bias-Variance Tradeoff
- Overfitting and Underfitting
- Cross-validation
- Feature Engineering

This knowledge is essential for building intelligent systems and understanding modern AI applications.`,
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:30:00Z',
    tags: ['machine-learning', 'ai', 'fundamentals'],
    category: 'Technology',
    source_query: 'What are the fundamentals of machine learning?',
    confidence: 0.95
  },
  {
    id: '2',
    title: 'Web Development Best Practices',
    summary: 'Modern web development practices including responsive design, performance optimization, and security considerations.',
    content: `Web Development Best Practices

Modern web development requires attention to multiple aspects:

1. Responsive Design
- Mobile-first approach
- Flexible grids and layouts
- CSS Grid and Flexbox
- Progressive enhancement

2. Performance Optimization
- Image optimization
- Code splitting
- Lazy loading
- Caching strategies
- CDN usage

3. Security Considerations
- HTTPS implementation
- Input validation
- XSS prevention
- CSRF protection
- Content Security Policy

4. Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support
- Color contrast

5. SEO Best Practices
- Meta tags
- Structured data
- Sitemaps
- Page speed optimization

These practices ensure robust, scalable, and user-friendly web applications.`,
    created_at: '2024-01-10T14:20:00Z',
    updated_at: '2024-01-12T09:15:00Z',
    tags: ['web-development', 'frontend', 'best-practices'],
    category: 'Development',
    source_query: 'What are the best practices for modern web development?',
    confidence: 0.88
  },
  {
    id: '3',
    title: 'Data Science Workflow',
    summary: 'Comprehensive data science workflow from data collection to model deployment and monitoring.',
    content: `Data Science Workflow

A comprehensive data science project follows these stages:

1. Problem Definition
- Business understanding
- Success metrics
- Project scope
- Resource planning

2. Data Collection
- Identify data sources
- Data extraction
- Data quality assessment
- Legal and ethical considerations

3. Data Preparation
- Data cleaning
- Feature engineering
- Data transformation
- Missing value handling

4. Exploratory Data Analysis
- Statistical analysis
- Data visualization
- Pattern identification
- Hypothesis generation

5. Model Development
- Algorithm selection
- Model training
- Hyperparameter tuning
- Cross-validation

6. Model Evaluation
- Performance metrics
- Error analysis
- Business validation
- A/B testing

7. Model Deployment
- Production environment
- API development
- Monitoring setup
- Documentation

8. Model Monitoring
- Performance tracking
- Drift detection
- Retraining strategies
- Feedback loops

This systematic approach ensures reliable and maintainable data science solutions.`,
    created_at: '2024-01-08T16:45:00Z',
    updated_at: '2024-01-08T16:45:00Z',
    tags: ['data-science', 'workflow', 'mlops'],
    category: 'Data Science',
    source_query: 'What is the complete data science workflow?',
    confidence: 0.92
  }
];

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    
    // In a real application, you would fetch from a database
    // const memoryItem = await db.memory.findUnique({ where: { id } });
    
    const memoryItem = mockMemoryItems.find(item => item.id === id);
    
    if (!memoryItem) {
      return NextResponse.json(
        { error: 'Memory not found' },
        { status: 404 }
      );
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    return NextResponse.json(memoryItem);
  } catch (error) {
    console.error('Error fetching memory item:', error);
    return NextResponse.json(
      { error: 'Failed to fetch memory item' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body = await request.json();
    const { title, content, summary, tags, category, confidence } = body;

    // Validate required fields
    if (!title || !content) {
      return NextResponse.json(
        { error: 'Title and content are required' },
        { status: 400 }
      );
    }

    // In a real application, you would update in a database
    // const updatedMemory = await db.memory.update({
    //   where: { id },
    //   data: { title, content, summary, tags, category, confidence, updated_at: new Date() }
    // });

    const existingItem = mockMemoryItems.find(item => item.id === id);
    if (!existingItem) {
      return NextResponse.json(
        { error: 'Memory not found' },
        { status: 404 }
      );
    }

    const updatedMemory = {
      ...existingItem,
      title,
      content,
      summary: summary || content.substring(0, 200) + '...',
      tags: tags || existingItem.tags,
      category: category || existingItem.category,
      confidence: confidence || existingItem.confidence,
      updated_at: new Date().toISOString()
    };

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    return NextResponse.json(updatedMemory);
  } catch (error) {
    console.error('Error updating memory item:', error);
    return NextResponse.json(
      { error: 'Failed to update memory item' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    // In a real application, you would delete from a database
    // await db.memory.delete({ where: { id } });

    const existingItem = mockMemoryItems.find(item => item.id === id);
    if (!existingItem) {
      return NextResponse.json(
        { error: 'Memory not found' },
        { status: 404 }
      );
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));

    return NextResponse.json({ message: 'Memory deleted successfully' });
  } catch (error) {
    console.error('Error deleting memory item:', error);
    return NextResponse.json(
      { error: 'Failed to delete memory item' },
      { status: 500 }
    );
  }
} 