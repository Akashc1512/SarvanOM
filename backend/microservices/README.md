# SarvanOM Microservices Architecture

This directory contains the refactored backend organized into distinct microservice modules. Each service is self-contained with its own API endpoints, business logic, and data models.

## Architecture Overview

The backend has been restructured into the following microservices:

### Core Services

1. **Retrieval Service** (`/retrieval`)
   - Document search and retrieval
   - Query processing and analysis
   - Hybrid search (vector + keyword)
   - Knowledge graph integration

2. **Fact-Check Service** (`/fact-check`)
   - Content fact verification
   - Expert validation
   - Source verification
   - Confidence scoring

3. **Synthesis Service** (`/synthesis`)
   - Content synthesis from search results
   - Citation management
   - Content generation
   - Response orchestration

4. **Auth Service** (`/auth`)
   - User authentication
   - JWT token management
   - User management
   - Security validation

5. **Crawler Service** (`/crawler`)
   - Web crawling
   - Content extraction
   - Link discovery
   - Metadata extraction

6. **Vector Service** (`/vector`)
   - Vector embeddings
   - Vector search
   - Document indexing
   - Similarity search

7. **Graph Service** (`/graph`)
   - Knowledge graph operations
   - Entity extraction
   - Relationship management
   - Graph queries

### API Gateway

The **API Gateway** (`/gateway`) serves as the single entry point for all frontend requests, providing:
- Request routing to appropriate microservices
- Response aggregation
- Authentication and authorization
- Rate limiting and monitoring
- CORS handling

## Service Structure

Each microservice follows this structure:

```
microservices/
├── {service_name}/
│   ├── __init__.py
│   ├── api.py              # FastAPI router with endpoints
│   ├── {service_name}_service.py  # Core business logic
│   ├── core/               # Core functionality modules
│   └── tests/              # Service-specific tests
├── gateway/
│   ├── __init__.py
│   ├── gateway_service.py  # Main gateway application
│   ├── router.py           # Request routing logic
│   └── middleware.py       # Gateway middleware
└── README.md
```

## API Endpoints

### Retrieval Service
- `POST /api/v1/retrieval/search` - Search documents
- `GET /api/v1/retrieval/result/{query_id}` - Get search result
- `POST /api/v1/retrieval/analyze` - Analyze query
- `GET /api/v1/retrieval/health` - Health check
- `GET /api/v1/retrieval/status` - Service status

### Fact-Check Service
- `POST /api/v1/fact-check/verify` - Verify facts
- `GET /api/v1/fact-check/result/{check_id}` - Get fact-check result
- `POST /api/v1/fact-check/validate-claim` - Validate claim
- `GET /api/v1/fact-check/health` - Health check
- `GET /api/v1/fact-check/status` - Service status

### Synthesis Service
- `POST /api/v1/synthesis/synthesize` - Synthesize content
- `GET /api/v1/synthesis/result/{synthesis_id}` - Get synthesis result
- `POST /api/v1/synthesis/add-citations` - Add citations
- `GET /api/v1/synthesis/health` - Health check
- `GET /api/v1/synthesis/status` - Service status

### Auth Service
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/validate-token` - Validate JWT token
- `GET /api/v1/auth/user/{user_id}` - Get user
- `GET /api/v1/auth/health` - Health check
- `GET /api/v1/auth/status` - Service status

### Crawler Service
- `POST /api/v1/crawler/crawl` - Crawl website
- `GET /api/v1/crawler/crawl/{crawl_id}` - Get crawl result
- `POST /api/v1/crawler/extract` - Extract content
- `GET /api/v1/crawler/health` - Health check
- `GET /api/v1/crawler/status` - Service status

### Vector Service
- `POST /api/v1/vector/embed` - Create embedding
- `POST /api/v1/vector/search` - Search similar vectors
- `POST /api/v1/vector/index` - Index document
- `GET /api/v1/vector/embedding/{embedding_id}` - Get embedding
- `GET /api/v1/vector/health` - Health check
- `GET /api/v1/vector/status` - Service status

### Graph Service
- `POST /api/v1/graph/entity` - Add entity
- `POST /api/v1/graph/relationship` - Add relationship
- `POST /api/v1/graph/query` - Query graph
- `POST /api/v1/graph/extract` - Extract entities
- `GET /api/v1/graph/entity/{entity_id}` - Get entity
- `GET /api/v1/graph/health` - Health check
- `GET /api/v1/graph/status` - Service status

### Gateway
- `GET /` - Root endpoint with service information
- `GET /api/v1/health` - Overall health check
- `GET /api/v1/gateway/status` - Gateway status

## Development

### Starting the Services

```bash
# Start the API Gateway (includes all microservices)
python backend/start_backend.py

# Or start individual services
python -m backend.microservices.gateway.gateway_service
```

### Environment Variables

Each service uses environment variables for configuration:

```bash
# Core settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# Database connections
MEILISEARCH_URL=http://localhost:7700
MEILI_MASTER_KEY=sarvanom-master-key-2024
ARANGO_URL=http://localhost:8529
QDRANT_URL=http://localhost:6333

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Feature flags
ENABLE_FACTCHECKING=true
ENABLE_CITATIONS=true
ENABLE_KNOWLEDGE_GRAPH=true
ENABLE_VECTOR_SEARCH=true
```

### Testing

```bash
# Test the API Gateway
curl http://localhost:8000/api/v1/health

# Test individual services
curl http://localhost:8000/api/v1/retrieval/health
curl http://localhost:8000/api/v1/fact-check/health
curl http://localhost:8000/api/v1/synthesis/health
```

## Benefits of This Architecture

1. **Single Responsibility**: Each service has a focused purpose
2. **Maintainability**: Services can be developed and deployed independently
3. **Scalability**: Services can be scaled individually based on load
4. **Technology Flexibility**: Each service can use different technologies
5. **Fault Isolation**: Issues in one service don't affect others
6. **API Gateway**: Provides unified interface and handles cross-cutting concerns

## Migration Notes

This refactoring consolidates the original backend structure:

- `backend/retrieval/` → `backend/microservices/retrieval/`
- `backend/fact_check/` → `backend/microservices/fact_check/`
- `backend/synthesis/` → `backend/microservices/synthesis/`
- `backend/auth/` → `backend/microservices/auth/`
- `backend/crawler/` → `backend/microservices/crawler/`
- `backend/vector/` → `backend/microservices/vector/`
- `backend/graph/` → `backend/microservices/graph/`

All services are now self-contained with their own APIs and can be accessed through the unified API Gateway. 