# 🚀 SarvanOM - Universal Knowledge Hub

A comprehensive AI-powered knowledge platform with multi-agent architecture, vector databases, and real-time collaboration capabilities.

## 🌟 Features

- **🤖 Multi-Agent AI System**: Retrieval, Fact-Checking, Synthesis, and Citation agents
- **🔍 Vector Database Integration**: Pinecone, Elasticsearch, Qdrant, and Neo4j support
- **⚡ Real-time Collaboration**: WebSocket-based live collaboration
- **📊 Analytics & Monitoring**: Comprehensive metrics and health checks
- **🔐 Enterprise Security**: Role-based access control and threat detection
- **🌐 Modern Web Interface**: Next.js frontend with responsive design

## 🏗️ Architecture

```
├── services/
│   ├── api-gateway/          # FastAPI backend with comprehensive endpoints
│   ├── auth-service/         # Authentication and authorization
│   ├── analytics-service/    # Analytics and monitoring
│   ├── factcheck-service/    # Fact verification agent
│   ├── search-service/       # Document retrieval agent
│   └── synthesis-service/    # Answer synthesis agent
├── shared/
│   └── core/                # Shared libraries and agent implementations
├── frontend/                # Next.js React application
└── infrastructure/          # Kubernetes and Terraform configurations
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
- Vector databases (Pinecone, Elasticsearch, Qdrant, Neo4j)

### 1. Clone the Repository

```bash
git clone https://github.com/akashc1512/sarvanom.git
cd sarvanom
```

### 2. Set Up Environment

```bash
# Copy environment template
cp env.template .env

# Edit .env with your API keys and configurations
# See VECTOR_BACKEND_CONFIGURATION_GUIDE.md for details
```

### 3. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

### 4. Start the Backend

```bash
# Start the API server
python -m uvicorn services.api_gateway.main:app --host 127.0.0.1 --port 8000
```

### 5. Start the Frontend

```bash
# In a new terminal
cd frontend
npm run dev
```

## 🔧 Configuration

### Environment Variables

Key environment variables to configure:

```bash
# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Vector Databases
PINECONE_API_KEY=your_pinecone_api_key
ELASTICSEARCH_URL=your_elasticsearch_url
QDRANT_URL=your_qdrant_url
NEO4J_URI=your_neo4j_uri

# Redis
REDIS_URL=your_redis_url
```

### Vector Database Setup

See `VECTOR_BACKEND_CONFIGURATION_GUIDE.md` for detailed setup instructions for:
- Pinecone v3 configuration
- Elasticsearch authentication
- Qdrant Cloud setup
- Neo4j Aura configuration

## 📊 API Endpoints

### Core Endpoints

- `POST /query` - Submit knowledge queries
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /analytics` - Analytics dashboard
- `GET /integrations` - Integration status

### Authentication

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Current user info

### WebSocket

- `ws://localhost:8000/ws/collaboration` - Real-time collaboration
- `ws://localhost:8000/ws/query-updates` - Query progress updates

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/
```

### Production Setup

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for enterprise deployment instructions.

## 📈 Monitoring

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check vector backends
python scripts/check_vector_backends.py
```

### Metrics

- Prometheus metrics available at `/metrics`
- Grafana dashboards in `infrastructure/monitoring/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/akashc1512/sarvanom/issues)
- 💬 [Discussions](https://github.com/akashc1512/sarvanom/discussions)

## 🏆 Acknowledgments

- Built with FastAPI, Next.js, and modern AI technologies
- Vector database integrations with Pinecone, Elasticsearch, Qdrant, and Neo4j
- Real-time collaboration powered by WebSockets
- Enterprise-grade security and monitoring

---

**SarvanOM** - Your Own Knowledge Hub Powered by AI 🚀
