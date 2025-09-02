# Setup Guide

## Overview
This guide provides comprehensive instructions for setting up SarvanOM on your local development environment or production server.

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11
- **Python**: 3.11+ (3.13+ recommended)
- **Node.js**: 18.0+ (20.0+ recommended)
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 20GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

### Required Software
- **Git**: Latest version
- **Docker**: 20.10+ with Docker Compose
- **PostgreSQL**: 14+ (if not using Docker)
- **Redis**: 6.0+ (if not using Docker)

## Quick Start (Docker)

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/sarvanom.git
cd sarvanom
```

### 2. Copy Environment Template
```bash
cp env.docker.template .env
```

### 3. Configure Environment Variables
Edit `.env` file with your API keys and configuration:
```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here

# Vector Databases
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_key_here

# PostgreSQL
POSTGRES_URL=postgresql://user:password@localhost:5432/sarvanom

# Redis
REDIS_URL=redis://localhost:6379
```

### 4. Start Services
```bash
docker-compose up -d
```

### 5. Verify Installation
```bash
# Check service status
docker-compose ps

# Test API endpoint
curl http://localhost:8000/health
```

## Manual Setup

### 1. Python Environment Setup

#### Create Virtual Environment
```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Build Frontend
```bash
npm run build
```

### 3. Database Setup

#### PostgreSQL
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu
brew install postgresql  # macOS

# Create database
sudo -u postgres createdb sarvanom
sudo -u postgres createuser sarvanom_user
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sarvanom TO sarvanom_user;"
```

#### Redis
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu
brew install redis  # macOS

# Start Redis
sudo systemctl start redis-server  # Ubuntu
brew services start redis  # macOS
```

### 4. Vector Database Setup

#### Qdrant (Recommended)
```bash
# Using Docker
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Or install locally
pip install qdrant-client
```

#### Chroma (Alternative)
```bash
pip install chromadb
```

### 5. LLM Setup

#### Ollama (Local Models)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama2:7b
ollama pull mistral:7b
```

#### OpenAI/Anthropic
- Get API keys from respective platforms
- Add to `.env` file

## Configuration

### 1. Core Configuration
Edit `shared/core/config/central_config.py`:
```python
class CentralConfig:
    # Service URLs
    GATEWAY_URL = "http://localhost:8000"
    RETRIEVAL_URL = "http://localhost:8001"
    SYNTHESIS_URL = "http://localhost:8002"
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER = "ollama"
    FALLBACK_LLM_PROVIDER = "openai"
    
    # Vector Database
    VECTOR_DB_PROVIDER = "qdrant"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

### 2. Service Configuration
Each service has its own configuration file in `services/{service_name}/config/`.

### 3. Frontend Configuration
Edit `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SarvanOM
```

## Development Setup

### 1. Install Development Dependencies
```bash
pip install -r requirements-dev.txt
npm install --workspace=frontend
```

### 2. Setup Pre-commit Hooks
```bash
pre-commit install
```

### 3. Setup Testing
```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### 4. Setup Linting
```bash
# Python
black .
flake8 .
mypy .

# Frontend
cd frontend
npm run lint
npm run type-check
```

## Production Deployment

### 1. Environment Configuration
```bash
# Production environment
cp env.docker.template .env.prod
# Edit with production values
```

### 2. Docker Production Build
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. SSL Certificate (Let's Encrypt)
```bash
sudo certbot --nginx -d your-domain.com
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using port 8000
lsof -i :8000
# Kill process or change port in .env
```

#### 2. Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U sarvanom_user -d sarvanom

# Test Redis connection
redis-cli ping
```

#### 3. LLM Provider Issues
```bash
# Test Ollama
ollama list

# Test OpenAI
python -c "import openai; print(openai.api_key)"
```

#### 4. Frontend Build Issues
```bash
# Clear cache
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Performance Tuning

#### 1. Database Optimization
```sql
-- PostgreSQL
CREATE INDEX idx_queries_timestamp ON queries(created_at);
CREATE INDEX idx_queries_user_id ON queries(user_id);

-- Redis
CONFIG SET maxmemory-policy allkeys-lru
```

#### 2. Vector Database Optimization
```python
# Qdrant optimization
qdrant_client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    ),
    optimizers_config=OptimizersConfigDiff(
        memmap_threshold=10000
    )
)
```

## Monitoring and Logging

### 1. Application Logs
```bash
# View logs
docker-compose logs -f gateway
docker-compose logs -f retrieval
```

### 2. System Monitoring
```bash
# CPU and memory usage
htop
# Disk usage
df -h
# Network connections
netstat -tulpn
```

### 3. Health Checks
```bash
# API health
curl http://localhost:8000/health
# Service status
curl http://localhost:8000/status
```

## Security Considerations

### 1. API Keys
- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly

### 2. Network Security
- Use HTTPS in production
- Configure firewall rules
- Implement rate limiting

### 3. Data Privacy
- Encrypt sensitive data at rest
- Implement user authentication
- Audit access logs

## Support and Community

### 1. Documentation
- [API Reference](docs/api-reference.md)
- [Architecture Guide](docs/architecture.md)
- [Contributing Guide](CONTRIBUTING.md)

### 2. Community
- [GitHub Issues](https://github.com/your-org/sarvanom/issues)
- [Discord Server](https://discord.gg/sarvanom)
- [Discussion Forum](https://github.com/your-org/sarvanom/discussions)

### 3. Professional Support
- Enterprise support available
- Custom development services
- Training and consulting

## Conclusion
This setup guide covers the essential steps to get SarvanOM running in your environment. For additional help, refer to the documentation or reach out to the community.
