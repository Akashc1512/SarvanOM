# SarvanOM Universal Knowledge Platform

> **MAANG-Level AI-Powered Knowledge Platform**
> 
> A production-ready, enterprise-grade platform for intelligent knowledge search, synthesis, and verification with comprehensive AI integration.

[![CI/CD](https://github.com/your-org/universal-knowledge-hub/workflows/Enterprise%20CI/badge.svg)](https://github.com/your-org/universal-knowledge-hub/actions)
[![Code Coverage](https://codecov.io/gh/your-org/universal-knowledge-hub/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/universal-knowledge-hub)
[![Security](https://img.shields.io/badge/security-audited-brightgreen.svg)](SECURITY.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Development](https://img.shields.io/badge/development-make%20doctor-blue.svg)](README.md#development-environment-check)
[![Environment Check](https://img.shields.io/badge/env%20check-python%20scripts%2Fdev_check.py-green.svg)](README.md#development-environment-check)

## 🎯 Project Overview

SarvanOM is a Universal Knowledge Platform designed for founders with zero coding background who are completely dependent on AI agents for all code. This project follows the most robust, industry-standard, and defensively programmed architecture.

### 🏗️ Architecture & Design Priorities

**Microservices Architecture:**
- **API Gateway** - Main entry point & orchestration
- **Search Service** - Query intelligence & vector search
- **Synthesis Service** - Multi-model LLM orchestration
- **Fact-check Service** - Expert validation & verification
- **Auth Service** - Authentication & authorization
- **Analytics Service** - Metrics & monitoring

**Feature MUST-HAVES:**
- Query intent detection
- Complexity scoring
- Domain routing
- Vector + KG + keyword search (hybrid RAG)
- Multi-agent orchestration
- Expert LLM validation

### 🔒 Security & Compliance

- All credentials and API keys in `.env`, never in code
- Every push/update to clean GitHub repo
- No credentials or secrets in code or history
- Robust, modular, and secure architecture
- Defensive programming principles

## 🚀 Quick Start (5 minutes)

### Prerequisites
- **Node.js** >= 18.0.0
- **Python** >= 3.13.5
- **Git**

### One-Command Setup
```bash
# Clone and setup in one command
git clone https://github.com/Akashc1512/SarvanOM.git && \
cd SarvanOM && \
python scripts/setup_sarvanom.py && \
npm run dev:backend
```

### Manual Setup
```bash
# 1. Clone repository
git clone https://github.com/Akashc1512/SarvanOM.git
cd SarvanOM

# 2. Install dependencies
.venv/bin/pip install -r requirements.txt

# 3. Configure environment
cp env.docker.template .env
# Edit .env with your actual credentials

# 4. Run setup validation
python scripts/setup_sarvanom.py

# 5. Start development servers
npm run dev:backend
```

**🎉 You're ready!** 
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8004 (services/gateway/)
- API Docs: http://localhost:8004/docs

## 🏗️ Architecture Overview

```
sarvanom/
├── services/                    # Microservices Architecture
│   ├── gateway/                # 🚪 Main entry point & orchestration
│   ├── auth/                   # 🔐 Authentication & authorization
│   ├── search/                 # 🔍 Knowledge retrieval & vector search
│   ├── synthesis/              # 🤖 AI synthesis & recommendations
│   ├── fact_check/             # ✅ Fact verification & validation
│   └── analytics/              # 📊 Metrics & monitoring
├── shared/                     # 📚 Shared libraries & utilities
│   ├── core/                   # Core functionality
│   │   ├── agent_pattern.py    # Agent strategy patterns
│   │   ├── logging_config.py   # Structured logging
│   │   └── api/config.py       # Configuration management
│   ├── models/                 # Data models
│   └── middleware/             # Shared middleware
├── frontend/                   # ⚛️ Next.js application
├── infrastructure/             # 🏗️ Infrastructure as Code
├── tests/                      # 🧪 Comprehensive test suite
└── scripts/                    # 🔧 Build & deployment scripts
```

## 🔧 Development Commands

## 🔍 Development Environment Check

### Quick Check Commands
```bash
# Check your development environment setup
make doctor                    # Linux/macOS (requires make)
python scripts/dev_check.py    # Cross-platform Python (recommended)
.\scripts\dev_check.ps1        # Windows PowerShell
.\scripts\dev_check.bat        # Windows Batch file

# This will verify:
# - Python ≥3.11
# - Node ≥18
# - Docker present
# - Required environment variables in .env, .env.docker, frontend/.env.local
# - Project structure
# - Free mode configuration (recommended defaults)
```

### Essential Commands
```bash
# Development
npm run dev                      # Start all services
python scripts/setup_sarvanom.py # Validate setup

# Testing
python -m pytest tests/         # All tests
python -m pytest tests/unit/    # Unit tests
python -m pytest tests/integration/ # Integration tests

# Code Quality
python scripts/verify_env_config.py # Validate environment
python scripts/check_hardcoded_values.py # Security audit
```

### Service-Specific Development
```bash
# Start individual services
npm run start:gateway
npm run start:auth
npm run start:search
```

## 🔒 Security Configuration

### Environment Variables
All sensitive configuration is managed through environment variables:

```bash
# Copy template and configure
cp env.docker.template .env

# Required variables for basic setup
ENVIRONMENT=development
SERVICE_NAME=sarvanom-api
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Database configuration
DATABASE_URL=postgresql://username:password@localhost:5432/sarvanom_db
REDIS_URL=redis://localhost:6379/0

# Zero Budget LLM Configuration
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
HUGGINGFACE_WRITE_TOKEN=your-huggingface-write-token
USE_DYNAMIC_SELECTION=true
PRIORITIZE_FREE_MODELS=true
```

### Security Best Practices
- ✅ Never commit `.env` files to version control
- ✅ Use strong, unique secrets for production
- ✅ Rotate secrets regularly
- ✅ Enable all security features in production
- ✅ Monitor for security vulnerabilities

## 🤖 Agent Architecture

### Agent Pattern Requirements
- All agents return only Python dictionaries (no custom classes, no None, no bool)
- All logging uses the `extra={}` pattern (never custom keyword args)
- Vector backend checker always runs at startup and validates all DBs
- All vector DB credentials and config loaded from `.env`, never hardcoded

### Agent Types
- **Synthesis Agent** - Creates comprehensive answers from verified facts
- **Fact-check Agent** - Validates claims against knowledge base
- **Retrieval Agent** - Hybrid search across vector, KG, and keyword
- **Knowledge Graph Agent** - Manages relationships and connections

## 📊 Monitoring & Analytics

### Health Checks
```bash
# Basic health check
curl http://localhost:8004/health

# Comprehensive diagnostics
curl http://localhost:8004/system/diagnostics

# Metrics (Prometheus format)
curl http://localhost:8004/metrics
```

### Logging
- Structured JSON logging with `extra={}` pattern
- Automatic secret masking
- Performance metrics tracking
- Audit trail for compliance

## 🧪 Testing

### Test Categories
- **Unit Tests** - Individual component testing
- **Integration Tests** - Service interaction testing
- **End-to-End Tests** - Complete user journey testing
- **Security Tests** - Vulnerability and penetration testing

### Running Tests
```bash
# All tests
python -m pytest

# Specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/

# With coverage
python -m pytest --cov=services --cov=shared
```

## 🚀 Deployment

### Production Checklist
- [ ] All environment variables configured
- [ ] Security audit completed
- [ ] Performance testing passed
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] SSL certificates installed
- [ ] Rate limiting configured
- [ ] Error handling tested

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/

# Check deployment status
kubectl get pods -n sarvanom
```

## 📚 Documentation

### Architecture Documentation
- [C4 Model](documentation/architecture/c4-model.md)
- [API Documentation](http://localhost:8004/docs)
- [Security Guide](SECURITY.md)
- [Deployment Guide](documentation/ENTERPRISE_DEPLOYMENT_GUIDE.md)

### Development Guides
- [Zero Budget LLM Guide](ZERO_BUDGET_LLM_GUIDE.md)
- [Agent Pattern Guide](QUERY_CLASSIFIER_GUIDE.md)
- [Knowledge Graph Guide](KNOWLEDGE_GRAPH_AGENT_GUIDE.md)

## 🔍 Troubleshooting

### Common Issues

**Environment Configuration**
```bash
# Validate environment setup
python scripts/verify_env_config.py

# Check for hardcoded secrets
python scripts/check_hardcoded_values.py
```

**Database Connectivity**
```bash
# Test database connection
python scripts/test_database_connectivity.py

# Verify vector database
python verify_meilisearch_setup.py
```

**Agent Issues**
```bash
# Test agent patterns
python test_agent_patterns.py

# Validate agent returns
python test_agent_returns.py
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes following defensive programming principles
4. Add comprehensive tests
5. Update documentation
6. Submit pull request

### Code Standards
- All code must follow defensive programming principles
- All agents must return dictionaries
- All logging must use `extra={}` pattern
- No hardcoded secrets or credentials
- Comprehensive error handling required

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- Check the [documentation](documentation/)
- Review [troubleshooting guide](#troubleshooting)
- Open an [issue](https://github.com/Akashc1512/SarvanOM/issues)

### Security Issues
- Report security vulnerabilities to security@yourdomain.com
- Do not disclose security issues publicly

---

**Built with ❤️ for founders who believe in AI-powered knowledge platforms**
