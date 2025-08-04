# API Gateway Service

The API Gateway serves as the main entry point for all client requests, routing them to the appropriate microservices.

## Features

- **Health Check**: `/health` endpoint for service monitoring
- **Service Routing**: Routes requests to appropriate microservices
- **Request Logging**: Logs all incoming requests
- **CORS Support**: Cross-origin resource sharing enabled
- **API Documentation**: Auto-generated docs at `/docs` and `/redoc`

## Service Routes

### Health
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with service info

### Search Service
- `POST /search/` - General search
- `GET /search/hybrid` - Hybrid search
- `GET /search/vector` - Vector search

### Fact Check Service
- `POST /fact-check/` - Fact checking
- `GET /fact-check/verify` - Claim verification

### Synthesis Service
- `POST /synthesize/` - Content synthesis
- `POST /synthesize/citations` - Add citations

### Auth Service
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/profile` - Get user profile

### Crawler Service
- `POST /crawler/` - Web crawling
- `GET /crawler/status` - Crawl job status

### Vector Service
- `POST /vector/` - Vector operations
- `POST /vector/embed` - Text embedding
- `GET /vector/search` - Vector similarity search

### Graph Service
- `POST /graph/` - Graph queries
- `GET /graph/entities` - Get entities
- `GET /graph/relationships` - Get relationships

## Running the Service

```bash
# Run directly
python services/gateway/main.py

# Or using uvicorn
uvicorn services.gateway.gateway_app:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development

The gateway is designed to be easily extensible. To add new routes:

1. Add route definitions in `routes.py`
2. Import and include the router in `gateway_app.py`
3. Update the `__init__.py` exports if needed

## Architecture

The gateway follows a modular design:
- `gateway_app.py` - Main FastAPI application
- `routes.py` - Route definitions for all services
- `main.py` - Entry point for running the service
- `__init__.py` - Module exports 