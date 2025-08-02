# SarvanOM Docker Setup for Windows 11

This guide provides comprehensive instructions for setting up and running SarvanOM on Windows 11 using Docker Desktop with WSL2 backend.

## 🚀 Quick Start

### Prerequisites

1. **Windows 11** with latest updates
2. **Docker Desktop for Windows** with WSL2 backend
3. **Git** for cloning the repository
4. **PowerShell 7** (recommended) or Command Prompt

### Installation Steps

1. **Clone the repository:**
   ```powershell
   git clone <repository-url>
   cd sarvanom
   ```

2. **Setup environment:**
   ```powershell
   # Using PowerShell
   .\docker-windows.bat setup
   
   # Or using Make (if available)
   make setup-data-dirs
   ```

3. **Start all services:**
   ```powershell
   .\docker-windows.bat up
   ```

4. **Check health:**
   ```powershell
   .\docker-windows.bat health
   ```

## 📋 Services Overview

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| **Frontend** | 3000 | React/Next.js UI | `http://localhost:3000` |
| **Backend** | 8000 | FastAPI API Gateway | `http://localhost:8000/health/basic` |
| **Ollama** | 11434 | Local LLM Server | `http://localhost:11434/api/tags` |
| **Meilisearch** | 7700 | Search Engine | `http://localhost:7700/version` |
| **ArangoDB** | 8529 | Knowledge Graph DB | `http://localhost:8529/_api/version` |
| **PostgreSQL** | 5432 | Primary Database | `pg_isready` |
| **Qdrant** | 6333 | Vector Database | `http://localhost:6333/health` |
| **Redis** | 6379 | Caching & Sessions | `redis-cli ping` |

## 🛠️ Management Commands

### Using Windows Batch File

```powershell
# Start all services
.\docker-windows.bat up

# Stop all services
.\docker-windows.bat down

# View logs
.\docker-windows.bat logs

# Check health
.\docker-windows.bat health

# Run comprehensive tests
.\docker-windows.bat test

# Show service status
.\docker-windows.bat status

# Restart services
.\docker-windows.bat restart

# Clean up everything
.\docker-windows.bat clean

# Build services
.\docker-windows.bat build
```

### Using Make (if available)

```bash
# Start all services
make up

# Stop all services
make down

# View logs
make logs

# Check health
make health-check

# Run comprehensive tests
make test-docker-health

# Show service status
make status

# Restart services
make restart

# Clean up everything
make clean

# Build services
make build
```

### Using Docker Compose Directly

```powershell
# Start services
docker compose --env-file .env.docker up --build -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Check status
docker compose ps
```

## 🔧 Configuration

### Environment Variables

The system uses `.env.docker` for configuration. Key variables:

```bash
# Core Configuration
ENVIRONMENT=development
SERVICE_NAME=sarvanom-backend

# Database URLs (Docker internal)
DATABASE_URL=postgresql://postgres:password@postgres:5432/sarvanom_db
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
ARANGODB_URL=http://arangodb:8529
MEILISEARCH_URL=http://meilisearch:7700
OLLAMA_BASE_URL=http://ollama:11434

# Security
SECRET_KEY=sarvanom-secret-key-2024-change-in-production
JWT_SECRET_KEY=sarvanom-jwt-secret-2024-change-in-production

# LLM Configuration
OLLAMA_MODEL=llama3.2:3b
USE_DYNAMIC_SELECTION=true
PRIORITIZE_FREE_MODELS=true
```

### Frontend Configuration

The frontend is configured to proxy API requests to the backend:

- **Development**: `http://sarvanom_backend:8000` (Docker internal)
- **Production**: `http://localhost:8000` (External access)

## 🏥 Health Monitoring

### Quick Health Check

```powershell
.\docker-windows.bat health
```

### Comprehensive Health Test

```powershell
.\docker-windows.bat test
```

This runs a comprehensive test that checks:
- ✅ All Docker services are running
- ✅ Backend health endpoint
- ✅ Frontend accessibility
- ✅ Ollama LLM service
- ✅ Meilisearch search engine
- ✅ ArangoDB knowledge graph
- ✅ Qdrant vector database
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Environment variable validation
- ✅ Service connectivity
- ✅ Performance metrics

### Manual Health Checks

```powershell
# Backend
curl http://localhost:8000/health/basic

# Frontend
curl http://localhost:3000

# Ollama
curl http://localhost:11434/api/tags

# Meilisearch
curl http://localhost:7700/version

# ArangoDB
curl http://localhost:8529/_api/version

# Qdrant
curl http://localhost:6333/health

# PostgreSQL
docker exec sarvanom-postgres pg_isready -U postgres -d sarvanom_db

# Redis
docker exec sarvanom-redis redis-cli ping
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Docker Desktop Not Running
```
Error: Cannot connect to the Docker daemon
```
**Solution**: Start Docker Desktop and wait for it to fully initialize.

#### 2. Port Conflicts
```
Error: Port is already in use
```
**Solution**: 
```powershell
# Check what's using the port
netstat -ano | findstr :8000

# Stop conflicting service or change port in docker-compose.yml
```

#### 3. WSL2 Issues
```
Error: WSL2 backend not available
```
**Solution**: 
1. Enable WSL2 in Windows Features
2. Update Docker Desktop settings to use WSL2
3. Restart Docker Desktop

#### 4. Memory Issues
```
Error: Container killed due to memory limit
```
**Solution**: 
1. Increase Docker Desktop memory limit (Settings > Resources)
2. Reduce service memory limits in `docker-compose.yml`

#### 5. Service Startup Order
```
Error: Service dependencies not met
```
**Solution**: Services are configured with health checks and dependencies. Wait for all services to be healthy.

### Debug Commands

```powershell
# Check Docker status
docker info

# Check service logs
docker compose logs sarvanom_backend
docker compose logs frontend
docker compose logs ollama

# Check container status
docker compose ps

# Check resource usage
docker stats

# Check network connectivity
docker network ls
docker network inspect sarvanom_sarvanom-network
```

## 📊 Performance Optimization

### Windows 11 Optimizations

1. **WSL2 Backend**: Ensure Docker Desktop uses WSL2 backend
2. **Memory Allocation**: Allocate at least 8GB RAM to Docker Desktop
3. **CPU Allocation**: Allocate at least 4 CPU cores
4. **Disk Space**: Ensure sufficient disk space for data volumes

### Resource Limits

Current resource limits per service:

| Service | Memory | CPU | Notes |
|---------|--------|-----|-------|
| Backend | 1GB | 0.5 cores | FastAPI application |
| Frontend | 1GB | 0.5 cores | Next.js development |
| Ollama | 2GB | 1.0 cores | LLM processing |
| Meilisearch | 512MB | 0.5 cores | Search engine |
| ArangoDB | 512MB | 0.5 cores | Knowledge graph |
| PostgreSQL | 512MB | 0.5 cores | Primary database |
| Qdrant | 512MB | 0.5 cores | Vector database |
| Redis | 256MB | 0.25 cores | Caching |

### Volume Optimization

Data is persisted in relative paths for better WSL2 performance:
- `./data/postgres` - PostgreSQL data
- `./data/redis` - Redis data
- `./data/meilisearch` - Meilisearch data
- `./data/arangodb` - ArangoDB data
- `./data/qdrant` - Qdrant data
- `./data/ollama` - Ollama models

## 🔒 Security Considerations

### Development Environment

1. **Default Passwords**: Change default passwords in `.env.docker`
2. **Secret Keys**: Generate unique secret keys for production
3. **Network Security**: Services are isolated in Docker network
4. **Volume Permissions**: Data volumes have appropriate permissions

### Production Deployment

1. **Environment Variables**: Use strong, unique secrets
2. **Network Security**: Configure proper firewall rules
3. **SSL/TLS**: Add reverse proxy with SSL termination
4. **Monitoring**: Enable comprehensive logging and monitoring

## 📝 Logs and Monitoring

### Viewing Logs

```powershell
# All services
.\docker-windows.bat logs

# Specific service
docker compose logs sarvanom_backend
docker compose logs frontend
docker compose logs ollama
```

### Log Locations

- **Application Logs**: `docker compose logs`
- **System Logs**: Windows Event Viewer
- **Docker Logs**: `%USERPROFILE%\AppData\Local\Docker\log.txt`

## 🔄 Updates and Maintenance

### Updating Services

```powershell
# Pull latest images
docker compose pull

# Rebuild services
.\docker-windows.bat build

# Restart services
.\docker-windows.bat restart
```

### Backup and Restore

```powershell
# Backup data
docker run --rm -v sarvanom_data:/data -v $(pwd):/backup alpine tar czf /backup/sarvanom-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore data
docker run --rm -v sarvanom_data:/data -v $(pwd):/backup alpine tar xzf /backup/sarvanom-backup-YYYYMMDD.tar.gz -C /data
```

## 🆘 Support

### Getting Help

1. **Check Health**: Run `.\docker-windows.bat health`
2. **View Logs**: Run `.\docker-windows.bat logs`
3. **Test Services**: Run `.\docker-windows.bat test`
4. **Check Status**: Run `.\docker-windows.bat status`

### Common Commands Reference

| Command | Description |
|---------|-------------|
| `.\docker-windows.bat up` | Start all services |
| `.\docker-windows.bat down` | Stop all services |
| `.\docker-windows.bat logs` | View service logs |
| `.\docker-windows.bat health` | Quick health check |
| `.\docker-windows.bat test` | Comprehensive health test |
| `.\docker-windows.bat status` | Show service status |
| `.\docker-windows.bat clean` | Remove all containers/data |
| `.\docker-windows.bat restart` | Restart all services |

## 🎯 Next Steps

After successful setup:

1. **Access the Application**: Open http://localhost:3000
2. **Test the API**: Visit http://localhost:8000/docs
3. **Monitor Health**: Run health checks regularly
4. **Configure LLM**: Download models in Ollama
5. **Add Data**: Import your knowledge base
6. **Customize**: Modify configuration as needed

---

**Happy coding with SarvanOM! 🚀** 