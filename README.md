# Universal Knowledge Hub

> **MAANG-Level AI-Powered Knowledge Platform**
> 
> A production-ready, enterprise-grade platform for intelligent knowledge search, synthesis, and verification with comprehensive AI integration.

[![CI/CD](https://github.com/your-org/universal-knowledge-hub/workflows/Enterprise%20CI/badge.svg)](https://github.com/your-org/universal-knowledge-hub/actions)
[![Code Coverage](https://codecov.io/gh/your-org/universal-knowledge-hub/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/universal-knowledge-hub)
[![Security](https://img.shields.io/badge/security-audited-brightgreen.svg)](SECURITY.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🚀 Quick Start (5 minutes)

### Prerequisites
- **Node.js** >= 18.0.0
- **Python** >= 3.13.5
- **Git**

### One-Command Setup
```bash
# Clone and setup in one command
git clone https://github.com/your-org/universal-knowledge-hub.git && \
cd universal-knowledge-hub && \
.\dev.bat setup && \
.\dev.bat dev
```

### Manual Setup
```bash
# 1. Clone repository
git clone https://github.com/your-org/universal-knowledge-hub.git
cd universal-knowledge-hub

# 2. Install dependencies
.\dev.bat install

# 3. Configure environment
.\dev.bat setup

# 4. Start development servers
.\dev.bat dev
```

**🎉 You're ready!** 
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🏗️ Architecture Overview

```
universal-knowledge-hub/
├── services/                    # Microservices Architecture
│   ├── api-gateway/            # 🚪 Main entry point & orchestration
│   ├── auth-service/           # 🔐 Authentication & authorization
│   ├── search-service/         # 🔍 Knowledge retrieval & vector search
│   ├── synthesis-service/      # 🤖 AI synthesis & recommendations
│   ├── factcheck-service/      # ✅ Fact verification & validation
│   └── analytics-service/      # 📊 Metrics & monitoring
├── shared/                     # 📚 Shared libraries & utilities
│   ├── core/                   # Core functionality
│   ├── models/                 # Data models
│   ├── config/                 # Configuration management
│   └── middleware/             # Shared middleware
├── frontend/                   # ⚛️ Next.js application
├── infrastructure/             # 🏗️ Infrastructure as Code
├── tests/                      # 🧪 Comprehensive test suite
└── scripts/                    # 🔧 Build & deployment scripts
```

## 🛠️ Development Commands

### Essential Commands
```bash
# Development
.\dev.bat dev                   # Start all services
.\dev.bat dev:frontend         # Frontend only
.\dev.bat dev:backend          # Backend only

# Testing
.\dev.bat test                 # All tests
.\dev.bat test:unit           # Unit tests
.\dev.bat test:integration    # Integration tests
.\dev.bat test:e2e            # End-to-end tests

# Code Quality
.\dev.bat lint                 # Linting
.\dev.bat format              # Code formatting
```

### Service-Specific Development
```bash
# Start individual services
.\dev.bat start:api-gateway
.\dev.bat start:auth-service
.\dev.bat start:search-service
.\dev.bat start:synthesis-service
.\dev.bat start:factcheck-service
.\dev.bat start:analytics-service
```

## 🧪 Testing Strategy

### Test Coverage
- **Unit Tests**: 90%+ coverage required
- **Integration Tests**: Service communication
- **E2E Tests**: Full user workflows
- **Performance Tests**: Load testing & benchmarks

### Running Tests
```bash
# All tests with coverage
.\dev.bat test

# Specific test types
.\dev.bat test:unit
.\dev.bat test:integration
.\dev.bat test:e2e
.\dev.bat test:performance

# With coverage report
pytest --cov=services --cov=shared --cov-report=html
```

## 📊 Monitoring & Observability

### Health Checks
```bash
# Check all service health
.\dev.bat monitor:health

# View application logs
.\dev.bat monitor:logs
```

### Metrics & Dashboards
- **Service Metrics**: `/metrics` endpoints
- **Health Checks**: `/health` endpoints
- **Real-time Monitoring**: Grafana dashboards

## 🔧 Configuration

### Environment Variables
Copy `.env.template` to `.env` and configure:

```bash
# Core Configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/knowledge_hub

# Redis
REDIS_URL=redis://localhost:6379

# Meilisearch
MEILISEARCH_URL=http://localhost:7700

# AI Services
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Security
JWT_SECRET_KEY=your_jwt_secret
SECRET_KEY=your_secret_key
```

## 🚀 Deployment

### Production Deployment
```bash
# Build for production
.\dev.bat build

# Deploy to production
.\scripts\enterprise-deploy.sh deploy
```

### Infrastructure
- **Kubernetes**: `infrastructure/kubernetes/`
- **Terraform**: `infrastructure/terraform/`
- **Monitoring**: `infrastructure/monitoring/`

## 📚 Documentation

### Quick Links
- **API Documentation**: http://localhost:8000/docs
- **Architecture**: [docs/architecture/](docs/architecture/)
- **Migration Guide**: [MIGRATION.md](MIGRATION.md)
- **Setup Instructions**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Security**: [SECURITY.md](SECURITY.md)

### Developer Guides
- [Getting Started](docs/getting-started.md)
- [Architecture Deep Dive](docs/architecture/README.md)
- [API Reference](docs/api/README.md)
- [Testing Guide](docs/testing/README.md)
- [Deployment Guide](docs/deployment/README.md)

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Make changes and test**
   ```bash
   .\dev.bat test
   .\dev.bat lint
   ```
4. **Commit with conventional commits**
   ```bash
   git commit -m "feat: add new feature"
   ```
5. **Push and create a pull request**

### Code Standards
- **Python**: Black, flake8, mypy
- **TypeScript**: ESLint, Prettier
- **Testing**: pytest with 90%+ coverage
- **Documentation**: Comprehensive docstrings

## 🔒 Security

### Security Features
- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control
- **Input Validation**: Pydantic models with strict validation
- **Rate Limiting**: Per-user and per-endpoint limits
- **Security Headers**: CORS, CSP, HSTS
- **Audit Logging**: Comprehensive security event logging

### Security Audit
```bash
# Run security audit
.\dev.bat security:audit
```

## 📈 Performance

### Optimization Features
- **Caching**: Redis-based caching with TTL
- **Connection Pooling**: Database and HTTP connection pooling
- **Async Processing**: Non-blocking I/O operations
- **Load Balancing**: Service-level load balancing
- **Monitoring**: Real-time performance metrics

### Performance Testing
```bash
# Run performance tests
.\dev.bat test:performance
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Service won't start
```bash
# Check service health
.\dev.bat monitor:health

# View logs
.\dev.bat monitor:logs
```

#### 2. Import errors
```bash
# Check import paths
python -c "import services.api_gateway.main"
```

#### 3. Environment issues
```bash
# Verify environment
.\dev.bat setup
```

#### 4. PowerShell execution policy
```powershell
# If you get execution policy errors
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Getting Help
- **Documentation**: Check [docs/](docs/) directory
- **Issues**: Create [GitHub issue](https://github.com/your-org/universal-knowledge-hub/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/your-org/universal-knowledge-hub/discussions)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with FastAPI, Next.js, and modern Python
- Follows MAANG-level engineering practices
- Comprehensive testing and monitoring
- Production-ready microservices architecture
