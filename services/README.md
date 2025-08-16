# Backend Services

This directory contains the modular backend services for the knowledge platform. The backend is organized into separate service modules, each with its own responsibility, and a unified API gateway that orchestrates all services.

## Architecture

The backend follows a modular microservices architecture with the following structure:

```
backend/
├── __init__.py                 # Main backend package
├── main.py                     # Application entry point
├── retrieval/                  # Search and retrieval services
│   ├── __init__.py
│   ├── search_service.py       # Search service wrapper
│   └── retrieval_agent.py      # Existing retrieval agent
├── fact_check/                 # Fact checking services
│   ├── __init__.py
│   ├── factcheck_service.py    # Fact check service wrapper
│   └── factcheck_agent.py      # Existing fact check agent
├── synthesis/                  # Content synthesis services
│   ├── __init__.py
│   ├── synthesis_service.py    # Synthesis service wrapper
│   └── synthesis_agent.py      # Existing synthesis agent
├── auth/                       # Authentication services
│   ├── __init__.py
│   ├── auth_service.py         # Auth service wrapper
│   └── auth.py                 # Existing auth modules
├── crawler/                    # Web crawling services
│   ├── __init__.py
│   └── crawler_service.py      # Crawler service wrapper
├── vector/                     # Vector database services
│   ├── __init__.py
│   └── vector_service.py       # Vector service implementation
├── graph/                      # Knowledge graph services
│   ├── __init__.py
│   └── graph_service.py        # Graph service implementation
└── gateway/                    # API gateway
    ├── __init__.py
    ├── gateway_service.py      # Main gateway service
    └── router.py               # API routing logic
```

## Services

### 1. Retrieval Service (`retrieval/`)
- **Purpose**: Search and retrieval operations
- **Features**:
  - Document search and retrieval
  - Semantic search capabilities
  - Hybrid retrieval (keyword + semantic)
  - Search result ranking and filtering
  - Query processing and optimization

### 2. Fact Check Service (`fact_check/`)
- **Purpose**: Fact checking and validation
- **Features**:
  - Fact verification and validation
  - Source credibility assessment
  - Claim verification against knowledge base
  - Expert review system integration
  - Validation result reporting

### 3. Synthesis Service (`synthesis/`)
- **Purpose**: Content synthesis and generation
- **Features**:
  - Content generation and summarization
  - Multi-source information synthesis
  - Citation and reference management
  - Content recommendation
  - ML model integration for generation

### 4. Auth Service (`auth/`)
- **Purpose**: Authentication and authorization
- **Features**:
  - User authentication and session management
  - Authorization and permission control
  - User management and profiles
  - Security and token management
  - Role-based access control

### 5. Crawler Service (`crawler/`)
- **Purpose**: Web crawling and data collection
- **Features**:
  - Web page crawling and scraping
  - Data extraction and parsing
  - Content discovery and indexing
  - Rate limiting and politeness
  - Data quality assessment

### 6. Vector Service (`vector/`)
- **Purpose**: Vector database operations
- **Features**:
  - Vector embeddings generation
  - Vector database operations (Pinecone, Qdrant)
  - Similarity search and matching
  - Embedding model management
  - Vector indexing and storage

### 7. Graph Service (`graph/`)
- **Purpose**: Knowledge graph operations
- **Features**:
  - Knowledge graph construction and maintenance
  - Relationship extraction and modeling
  - Graph traversal and querying
  - Entity linking and disambiguation
  - Graph analytics and insights

### 8. Gateway Service (`gateway/`)
- **Purpose**: API routing and orchestration
- **Features**:
  - Request routing to appropriate services
  - Service discovery and load balancing
  - Authentication and authorization middleware
  - Rate limiting and security
  - Request/response transformation
  - Error handling and logging

## API Endpoints

The gateway provides the following API endpoints:

### Search Endpoints
- `POST /api/v1/search` - Search for information
- `GET /api/v1/search/{query}` - GET search endpoint

### Fact Check Endpoints
- `POST /api/v1/fact-check` - Fact check a claim
- `POST /api/v1/fact-check/batch` - Fact check multiple claims

### Synthesis Endpoints
- `POST /api/v1/synthesize` - Synthesize content
- `POST /api/v1/synthesize/citations` - Generate citations

### Crawler Endpoints
- `POST /api/v1/crawl` - Start crawling a website
- `GET /api/v1/crawl/status/{job_id}` - Get crawling job status

### Vector Search Endpoints
- `POST /api/v1/vector/search` - Vector similarity search
- `POST /api/v1/vector/upsert` - Upsert documents to vector database

### Graph Endpoints
- `POST /api/v1/graph/query` - Query the knowledge graph
- `POST /api/v1/graph/entities` - Find entities in text
- `POST /api/v1/graph/triple` - Add knowledge triple

### Auth Endpoints
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/profile` - Get user profile
- `POST /api/v1/auth/logout` - User logout

### Health and Status Endpoints
- `GET /health` - Health check
- `GET /api/v1/services/status` - Service status

## Getting Started

### Prerequisites
- Python 3.8+
- Required dependencies (see requirements.txt)

### Installation
1. Install dependencies:
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export BACKEND_HOST=0.0.0.0
   export BACKEND_PORT=8000
   export BACKEND_RELOAD=true
   ```

3. Run the backend:
   ```bash
   npm run start:gateway
   ```

### Development
For development with auto-reload:
```bash
npm run dev:backend
```

## Configuration

Each service can be configured through environment variables or configuration files. See individual service documentation for specific configuration options.

## Inter-Service Communication

All inter-service communication goes through the gateway layer. Services do not communicate directly with each other but are orchestrated by the gateway service.

## Error Handling

The gateway provides centralized error handling and logging for all services. Errors are logged and appropriate HTTP status codes are returned to clients.

## Monitoring

Each service provides a `get_status()` method that returns health and configuration information. The gateway aggregates this information and provides it through the `/health` endpoint.

## Security

- Authentication is handled by the auth service
- All endpoints (except login/register) require authentication
- CORS is configured for cross-origin requests
- Rate limiting can be configured per endpoint

## Testing

Run tests for the backend:
```bash
pytest backend/tests/
```

## Deployment

The backend can be deployed using:
- Docker containers
- Kubernetes
- Traditional server deployment

See deployment documentation for specific instructions. 