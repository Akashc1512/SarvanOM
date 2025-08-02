# SarvanOM Docker Setup Guide

This guide provides instructions for running SarvanOM locally using Docker, optimized for 8GB RAM laptops.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- At least 8GB RAM available
- 10GB free disk space

### 1. Setup Environment

```bash
# Copy the environment template
cp env.docker.template .env.docker

# Edit the environment file (optional)
# nano .env.docker
```

### 2. Start the Stack

```bash
# Start all services
make up

# Or use docker-compose directly
docker-compose --env-file .env.docker up --build -d
```

### 3. Check Health

```bash
# Run health check
make docker-health

# Or manually
python test_docker_health.py
```

### 4. Access Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health/basic
- **ArangoDB**: http://localhost:8529
- **Meilisearch**: http://localhost:7700
- **Qdrant**: http://localhost:6333
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Ollama**: http://localhost:11434

## 📋 Service Details

### Core Services

| Service | Port | Memory Limit | Purpose |
|---------|------|--------------|---------|
| `sarvanom_backend` | 8000 | 1GB | FastAPI backend |
| `ollama` | 11434 | 2GB | Local LLM |
| `meilisearch` | 7700 | 512MB | Search engine |
| `arangodb` | 8529 | 512MB | Knowledge graph |
| `postgres` | 5432 | 512MB | Primary database |
| `qdrant` | 6333 | 512MB | Vector database |
| `redis` | 6379 | 256MB | Caching |

### Resource Allocation

Total memory usage: ~5.5GB (optimized for 8GB laptops)
- Backend: 1GB
- Ollama: 2GB (LLM processing)
- Databases: 1.5GB total
- System overhead: ~1GB

## 🔧 Configuration

### Environment Variables

The `.env.docker` file contains all necessary configuration:

```bash
# Core settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Database URLs (Docker internal)
DATABASE_URL=postgresql://postgres:password@postgres:5432/sarvanom_db
REDIS_URL=redis://redis:6379/0
MEILISEARCH_URL=http://meilisearch:7700
ARANGODB_URL=http://arangodb:8529
QDRANT_URL=http://qdrant:6333
OLLAMA_BASE_URL=http://ollama:11434

# Security keys (change in production)
SECRET_KEY=sarvanom-secret-key-2024-change-in-production
JWT_SECRET_KEY=sarvanom-jwt-secret-2024-change-in-production
MEILISEARCH_MASTER_KEY=sarvanom-master-key-2024
```

### Database Credentials

- **PostgreSQL**: `postgres` / `password`
- **ArangoDB**: `root` / `sarvanom-root-password-2024`
- **Redis**: No authentication (development)

## 🛠️ Management Commands

### Makefile Commands

```bash
# Start services
make up

# Stop services
make down

# Restart services
make restart

# View logs
make logs

# Health check
make docker-health

# Setup (first time)
make docker-setup
```

### Docker Compose Commands

```bash
# Start services
docker-compose --env-file .env.docker up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose --env-file .env.docker up --build -d

# View service status
docker-compose ps
```

## 🔍 Monitoring & Debugging

### Health Check

The health check script tests all services:

```bash
python test_docker_health.py
```

This will:
- Test HTTP endpoints
- Check database connections
- Verify service responsiveness
- Generate a detailed report

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f sarvanom_backend

# Last 100 lines
docker-compose logs --tail=100
```

### Service Status

```bash
# Check running containers
docker-compose ps

# Check resource usage
docker stats

# Check volumes
docker volume ls
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Conflicts

If ports are already in use:

```bash
# Check what's using the ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432

# Stop conflicting services or change ports in docker-compose.yml
```

#### 2. Memory Issues

If you see memory errors:

```bash
# Check available memory
free -h

# Reduce memory limits in docker-compose.yml
# Or close other applications
```

#### 3. Ollama Model Download

Ollama needs to download models on first run:

```bash
# Check Ollama logs
docker-compose logs ollama

# Pull model manually
docker exec sarvanom-ollama ollama pull llama3.2:3b
```

#### 4. Database Connection Issues

```bash
# Check database logs
docker-compose logs postgres
docker-compose logs arangodb

# Restart databases
docker-compose restart postgres arangodb
```

### Performance Optimization

#### For Low Memory Systems (4-6GB)

Edit `docker-compose.yml`:

```yaml
# Reduce Ollama memory
ollama:
  deploy:
    resources:
      limits:
        memory: 1G  # Reduce from 2G
        cpus: '0.5'  # Reduce from 1.0

# Reduce backend memory
sarvanom_backend:
  deploy:
    resources:
      limits:
        memory: 512M  # Reduce from 1G
        cpus: '0.25'  # Reduce from 0.5
```

#### For High Memory Systems (16GB+)

Increase limits for better performance:

```yaml
ollama:
  deploy:
    resources:
      limits:
        memory: 4G  # Increase for larger models
        cpus: '2.0'

sarvanom_backend:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
```

## 🔒 Security Notes

### Development vs Production

This setup is configured for **development only**:

- Default passwords
- No SSL/TLS
- Debug logging enabled
- No rate limiting
- CORS allows all origins

For production:

1. Change all default passwords
2. Enable SSL/TLS
3. Configure proper CORS
4. Set up monitoring
5. Use secrets management
6. Enable rate limiting

### Data Persistence

All data is persisted in Docker volumes:

- `postgres_data`: PostgreSQL database
- `arangodb_data`: ArangoDB data
- `meilisearch_data`: Search index
- `qdrant_data`: Vector database
- `redis_data`: Cache data
- `ollama_data`: LLM models

To backup data:

```bash
# Backup volumes
docker run --rm -v sarvanom_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 📊 Monitoring

### Built-in Health Checks

Each service has health checks configured:

- **Backend**: `/health/basic` endpoint
- **Ollama**: `/api/tags` endpoint
- **Meilisearch**: `/version` endpoint
- **ArangoDB**: `/_api/version` endpoint
- **Qdrant**: `/health` endpoint
- **PostgreSQL**: `pg_isready` command
- **Redis**: `ping` command

### Metrics

The backend exposes metrics at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

## 🧪 Testing

### API Testing

```bash
# Test basic health
curl http://localhost:8000/health/basic

# Test API docs
curl http://localhost:8000/docs

# Test with authentication
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/queries
```

### Database Testing

```bash
# PostgreSQL
docker exec sarvanom-postgres psql -U postgres -d sarvanom_db -c "SELECT 1;"

# Redis
docker exec sarvanom-redis redis-cli ping

# ArangoDB
curl -u root:sarvanom-root-password-2024 http://localhost:8529/_api/version
```

## 🚀 Next Steps

After successful setup:

1. **Load Sample Data**: Use the provided scripts to load test data
2. **Configure LLM**: Set up your preferred LLM providers
3. **Test Queries**: Try the API endpoints
4. **Monitor Performance**: Watch resource usage
5. **Scale Up**: Adjust memory limits as needed

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Run health check: `python test_docker_health.py`
3. Check system resources: `docker stats`
4. Restart services: `make restart`

For more help, check the main README.md or create an issue in the repository. 