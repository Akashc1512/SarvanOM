# Service Catalog - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE ARCHITECTURE**  
**Purpose**: Comprehensive catalog of all services, ports, dependencies, and SLAs

---

## 🏗️ **Service Architecture Overview**

SarvanOM v2 follows a microservices architecture with clear service boundaries, well-defined APIs, and independent deployment capabilities. Each service has specific responsibilities and SLAs.

---

## 📋 **Core Services**

### **1. API Gateway Service**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 8004 | Main API gateway port |
| **Technology** | FastAPI (Python 3.11+) | Async-first web framework |
| **Dependencies** | All backend services | Routes requests to appropriate services |
| **SLA** | 99.9% availability, <100ms latency | High availability gateway |
| **Scaling** | Horizontal (stateless) | Multiple instances behind load balancer |
| **Health Check** | `/health` | Basic health endpoint |
| **Metrics** | Request rate, latency, error rate | Prometheus metrics |

**Responsibilities:**
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- Request/response logging
- CORS handling
- API versioning

### **2. Authentication Service**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 8001 | Authentication service port |
| **Technology** | FastAPI (Python 3.11+) | JWT-based authentication |
| **Dependencies** | PostgreSQL, Redis | User data and session storage |
| **SLA** | 99.9% availability, <50ms latency | Critical for all operations |
| **Scaling** | Horizontal (stateless) | JWT tokens enable stateless scaling |
| **Health Check** | `/health` | Service health monitoring |
| **Metrics** | Auth success rate, token validation time | Security and performance metrics |

**Responsibilities:**
- User authentication (login/logout)
- JWT token generation and validation
- User session management
- Password reset and account recovery
- Role-based access control
- Audit logging for security events

### **3. Search Service**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 8002 | Search service port |
| **Technology** | FastAPI (Python 3.11+) | Search orchestration |
| **Dependencies** | Meilisearch, Qdrant, ArangoDB | Multi-lane search capabilities |
| **SLA** | 99.9% availability, <200ms latency | Fast search responses |
| **Scaling** | Horizontal (stateless) | Search operations are stateless |
| **Health Check** | `/health` | Service health monitoring |
| **Metrics** | Search latency, result quality, cache hit rate | Search performance metrics |

**Responsibilities:**
- Multi-lane search orchestration
- Result fusion and ranking
- Search result caching
- Query optimization
- Search analytics
- Real-time search updates

### **4. Synthesis Service**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 8003 | Synthesis service port |
| **Technology** | FastAPI (Python 3.11+) | LLM orchestration |
| **Dependencies** | LLM providers, Redis | Model selection and caching |
| **SLA** | 99.9% availability, <500ms latency | LLM response generation |
| **Scaling** | Horizontal (stateless) | LLM calls are stateless |
| **Health Check** | `/health` | Service health monitoring |
| **Metrics** | LLM response time, token usage, model performance | LLM operation metrics |

**Responsibilities:**
- LLM provider management
- Model selection and routing
- Response generation and streaming
- Cost optimization
- Model performance monitoring
- Auto-upgrade policy implementation

### **5. Fact-Check Service**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 8005 | Fact-check service port |
| **Technology** | FastAPI (Python 3.11+) | Fact verification |
| **Dependencies** | External fact-check APIs, Redis | Verification and caching |
| **SLA** | 99.9% availability, <300ms latency | Fact verification |
| **Scaling** | Horizontal (stateless) | Verification operations are stateless |
| **Health Check** | `/health` | Service health monitoring |
| **Metrics** | Verification accuracy, response time, source quality | Fact-check quality metrics |

**Responsibilities:**
- Fact verification and validation
- Source credibility assessment
- Disagreement detection
- Citation quality scoring
- Fact-check result caching
- Verification analytics

### **6. Analytics Service**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 8006 | Analytics service port |
| **Technology** | FastAPI (Python 3.11+) | Analytics and reporting |
| **Dependencies** | PostgreSQL, Redis | Data storage and caching |
| **SLA** | 99.9% availability, <100ms latency | Analytics data access |
| **Scaling** | Horizontal (stateless) | Analytics queries are stateless |
| **Health Check** | `/health` | Service health monitoring |
| **Metrics** | Query performance, data freshness, report generation time | Analytics performance metrics |

**Responsibilities:**
- Usage analytics and reporting
- Performance metrics collection
- User behavior analysis
- System health monitoring
- Business intelligence
- Custom dashboard generation

---

## 🎨 **Frontend Services**

### **7. Next.js Frontend**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 3001 | Frontend development port |
| **Technology** | Next.js 14, React, TypeScript | Modern frontend framework |
| **Dependencies** | All backend services | API integration |
| **SLA** | 99.9% availability, <2s load time | User interface |
| **Scaling** | Horizontal (CDN) | Static assets via CDN |
| **Health Check** | `/api/health` | Frontend health monitoring |
| **Metrics** | Page load time, user interactions, error rate | Frontend performance metrics |

**Responsibilities:**
- User interface and experience
- API integration and data fetching
- Real-time updates via SSE
- Client-side routing
- Form handling and validation
- Accessibility compliance

---

## 🗄️ **Data Services**

### **8. PostgreSQL Database**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 5432 | PostgreSQL port |
| **Technology** | PostgreSQL 15+ | Primary relational database |
| **Dependencies** | None | Primary data store |
| **SLA** | 99.9% availability, <10ms query time | Critical data persistence |
| **Scaling** | Vertical + Read replicas | Master-slave replication |
| **Health Check** | Connection test | Database health monitoring |
| **Metrics** | Query performance, connection pool, replication lag | Database performance metrics |

**Responsibilities:**
- User data storage
- Application state persistence
- Transaction management
- Data consistency
- Backup and recovery
- Query optimization

### **9. Redis Cache**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 6379 | Redis port |
| **Technology** | Redis 7+ | In-memory cache |
| **Dependencies** | None | Caching layer |
| **SLA** | 99.9% availability, <1ms access time | High-speed caching |
| **Scaling** | Cluster mode | Redis cluster for scaling |
| **Health Check** | PING command | Cache health monitoring |
| **Metrics** | Hit rate, memory usage, eviction rate | Cache performance metrics |

**Responsibilities:**
- Session storage
- Query result caching
- Rate limiting counters
- Temporary data storage
- Pub/Sub messaging
- Performance optimization

### **10. Qdrant Vector Database**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 6333 | Qdrant port |
| **Technology** | Qdrant 1.7+ | Vector similarity search |
| **Dependencies** | None | Vector operations |
| **SLA** | 99.9% availability, <50ms search time | Vector search performance |
| **Scaling** | Cluster mode | Qdrant cluster for scaling |
| **Health Check** | `/health` | Vector DB health monitoring |
| **Metrics** | Search latency, index size, memory usage | Vector search metrics |

**Responsibilities:**
- Vector similarity search
- Embedding storage
- Semantic search
- Vector indexing
- Similarity calculations
- Vector data management

### **11. Meilisearch Engine**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 7700 | Meilisearch port |
| **Technology** | Meilisearch 1.5+ | Full-text search engine |
| **Dependencies** | None | Keyword search |
| **SLA** | 99.9% availability, <20ms search time | Fast text search |
| **Scaling** | Single instance | Meilisearch scaling |
| **Health Check** | `/health` | Search engine health |
| **Metrics** | Search latency, index size, query volume | Search performance metrics |

**Responsibilities:**
- Full-text search
- Keyword matching
- Search result ranking
- Index management
- Search analytics
- Query optimization

### **12. ArangoDB Knowledge Graph**
| Property | Value | Description |
|----------|-------|-------------|
| **Port** | 8529 | ArangoDB port |
| **Technology** | ArangoDB 3.11+ | Graph database |
| **Dependencies** | None | Graph operations |
| **SLA** | 99.9% availability, <100ms query time | Graph query performance |
| **Scaling** | Cluster mode | ArangoDB cluster |
| **Health Check** | `/_api/version` | Graph DB health monitoring |
| **Metrics** | Query performance, graph size, traversal time | Graph operation metrics |

**Responsibilities:**
- Knowledge graph storage
- Entity relationship management
- Graph traversal queries
- Knowledge extraction
- Graph analytics
- Relationship inference

---

## 🔄 **Service Dependencies**

### **Dependency Graph**
```
API Gateway (8004)
├── Authentication Service (8001)
├── Search Service (8002)
├── Synthesis Service (8003)
├── Fact-Check Service (8005)
└── Analytics Service (8006)

Authentication Service (8001)
├── PostgreSQL (5432)
└── Redis (6379)

Search Service (8002)
├── Meilisearch (7700)
├── Qdrant (6333)
├── ArangoDB (8529)
└── Redis (6379)

Synthesis Service (8003)
├── LLM Providers (External)
└── Redis (6379)

Fact-Check Service (8005)
├── External Fact-Check APIs
└── Redis (6379)

Analytics Service (8006)
├── PostgreSQL (5432)
└── Redis (6379)

Next.js Frontend (3001)
└── API Gateway (8004)
```

---

## 📊 **Service SLAs Summary**

| Service | Availability | Latency | Throughput | Notes |
|---------|-------------|---------|------------|-------|
| **API Gateway** | 99.9% | <100ms | 1000 RPS | Critical path |
| **Authentication** | 99.9% | <50ms | 500 RPS | Security critical |
| **Search** | 99.9% | <200ms | 200 RPS | Multi-lane search |
| **Synthesis** | 99.9% | <500ms | 100 RPS | LLM dependent |
| **Fact-Check** | 99.9% | <300ms | 150 RPS | External API dependent |
| **Analytics** | 99.9% | <100ms | 300 RPS | Read-heavy workload |
| **PostgreSQL** | 99.9% | <10ms | 1000 QPS | Primary database |
| **Redis** | 99.9% | <1ms | 10000 OPS | High-speed cache |
| **Qdrant** | 99.9% | <50ms | 500 QPS | Vector operations |
| **Meilisearch** | 99.9% | <20ms | 1000 QPS | Text search |
| **ArangoDB** | 99.9% | <100ms | 200 QPS | Graph operations |

---

## 🎯 **Service Health Monitoring**

### **Health Check Endpoints**
| Service | Health Endpoint | Response Format | Check Frequency |
|---------|----------------|-----------------|-----------------|
| **API Gateway** | `/health` | JSON | 30s |
| **Authentication** | `/health` | JSON | 30s |
| **Search** | `/health` | JSON | 30s |
| **Synthesis** | `/health` | JSON | 30s |
| **Fact-Check** | `/health` | JSON | 30s |
| **Analytics** | `/health` | JSON | 30s |
| **PostgreSQL** | Connection test | Boolean | 30s |
| **Redis** | PING | PONG | 30s |
| **Qdrant** | `/health` | JSON | 30s |
| **Meilisearch** | `/health` | JSON | 30s |
| **ArangoDB** | `/_api/version` | JSON | 30s |

### **Health Check Response Format**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-09T10:00:00Z",
  "uptime_seconds": 3600,
  "version": "1.0.0",
  "dependencies": {
    "database": "healthy",
    "cache": "healthy",
    "external_apis": "healthy"
  },
  "metrics": {
    "response_time_ms": 50,
    "memory_usage_mb": 256,
    "cpu_usage_percent": 15
  }
}
```

---

## 📚 **References**

- System Context: `docs/architecture/system_context.md`
- Architecture Overview: `04_architecture_overview.md`
- Data Platform: `07_data_platform_qdrant_arango_meili.md`
- Observability: `09_observability_and_budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This service catalog provides the complete reference for all services in SarvanOM v2.*
