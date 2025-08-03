# SarvanOM Modular Backend

This directory contains the new modular backend structure for the Universal Knowledge Hub.

## Architecture

The backend is organized into modular services, each with its own responsibility:

```
backend/
├── __init__.py                 # Main package initialization
├── retrieval/                  # Search and document retrieval
│   ├── __init__.py
│   ├── search_service.py       # Main search service
│   └── core/                   # Core search components
├── fact_check/                 # Fact verification and validation
│   ├── __init__.py
│   ├── factcheck_service.py    # Main fact check service
│   └── core/                   # Core fact checking components
├── synthesis/                  # Content synthesis and generation
│   ├── __init__.py
│   ├── synthesis_service.py    # Main synthesis service
│   ├── citation_manager.py     # Citation management
│   ├── recommendation_service.py # Recommendation generation
│   ├── ml_integration.py       # ML model integration
│   └── core/                   # Core synthesis components
├── auth/                       # Authentication and authorization
│   ├── __init__.py
│   ├── auth_service.py         # Main auth service
│   ├── user_management.py      # User management
│   ├── security.py             # Security utilities
│   └── validators.py           # Input validation
├── crawler/                    # Web crawling and content extraction
│   ├── __init__.py
│   └── web_crawler.py          # Web crawler service
├── vector/                     # Vector database operations
│   ├── __init__.py
│   └── vector_service.py       # Vector service
├── graph/                      # Knowledge graph operations
│   ├── __init__.py
│   └── graph_service.py        # Graph service
├── gateway/                    # API Gateway and routing
│   ├── __init__.py
│   ├── gateway_service.py      # Main gateway service
│   ├── router.py               # API router
│   └── middleware.py           # Gateway middleware
└── start_backend.py            # Startup script
```

## Services

### Retrieval Service (`retrieval/`)
- **Purpose**: Document search and retrieval
- **Key Features**:
  - Hybrid search (vector + keyword)
  - Multi-source retrieval
  - Query processing and classification
  - Result ranking and filtering

### Fact Check Service (`fact_check/`)
- **Purpose**: Fact verification and validation
- **Key Features**:
  - Fact verification
  - Expert review system
  - Source credibility assessment
  - Contradiction detection

### Synthesis Service (`synthesis/`)
- **Purpose**: Content synthesis and generation
- **Key Features**:
  - Content synthesis
  - Citation management
  - Recommendation generation
  - ML model integration

### Auth Service (`auth/`)
- **Purpose**: Authentication and authorization
- **Key Features**:
  - User authentication
  - JWT token management
  - Role-based access control
  - Security validation

### Crawler Service (`crawler/`)
- **Purpose**: Web crawling and content extraction
- **Key Features**:
  - Web page crawling
  - Content extraction
  - Link discovery
  - Rate limiting

### Vector Service (`vector/`)
- **Purpose**: Vector database operations
- **Key Features**:
  - Vector storage and retrieval
  - Embedding generation
  - Similarity search
  - Vector indexing

### Graph Service (`graph/`)
- **Purpose**: Knowledge graph operations
- **Key Features**:
  - Graph traversal
  - Entity management
  - Relationship management
  - Graph analytics

### Gateway Service (`gateway/`)
- **Purpose**: API Gateway and routing
- **Key Features**:
  - Request routing
  - Service orchestration
  - Authentication middleware
  - Rate limiting
  - Logging and monitoring

## API Endpoints

The gateway provides the following API endpoints:

### Search Endpoints
- `POST /api/v1/search` - Search for documents
- `GET /api/v1/search/{query_id}` - Get search result by ID

### Fact Check Endpoints
- `POST /api/v1/fact-check` - Fact check content
- `GET /api/v1/fact-check/{check_id}` - Get fact check result by ID

### Synthesis Endpoints
- `POST /api/v1/synthesis` - Synthesize content
- `GET /api/v1/synthesis/{synthesis_id}` - Get synthesis result by ID

### Auth Endpoints
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Crawler Endpoints
- `POST /api/v1/crawler/crawl` - Crawl website

### Vector Endpoints
- `POST /api/v1/vector` - Vector operations (search/store/update)

### Graph Endpoints
- `POST /api/v1/graph` - Graph operations (search/add/update)

### Health Endpoints
- `GET /api/v1/health` - Health check for all services
- `GET /` - Root endpoint with service information

## Getting Started

### Prerequisites
- Python 3.8+
- Required packages (see requirements.txt)

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (see env_template.txt)

3. Start the backend:
   ```bash
   python backend/start_backend.py
   ```

### Development
- The server will start on `http://localhost:8000`
- API documentation is available at `http://localhost:8000/docs`
- Health check is available at `http://localhost:8000/api/v1/health`

## Service Communication

All inter-service communication goes through the gateway layer:

1. **Client Request** → **Gateway** → **Service** → **Response**
2. **Service-to-Service** calls are routed through the gateway
3. **Authentication** and **rate limiting** are handled at the gateway level
4. **Logging** and **monitoring** are centralized in the gateway

## Configuration

Each service can be configured independently through:
- Environment variables
- Configuration files
- Service-specific settings

## Monitoring

The gateway provides:
- Request/response logging
- Performance metrics
- Health checks for all services
- Error handling and reporting

## Security

- Authentication middleware for all protected endpoints
- Rate limiting to prevent abuse
- CORS configuration for web clients
- Security headers for protection

## Future Enhancements

- Service discovery and load balancing
- Circuit breaker patterns
- Distributed tracing
- Advanced caching strategies
- Microservice deployment support 