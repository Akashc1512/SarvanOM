# System Context - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE ARCHITECTURE**  
**Purpose**: High-level system context and external dependencies

---

## 🎯 **System Overview**

SarvanOM v2 is a universal knowledge assistant that provides fast, grounded responses with citations and disagreement detection. The system automatically selects the best latest stable model for each query (including multimodal) while meeting strict 5-10s end-to-end SLOs.

### **Core Mission**
- **Speed**: TTFT ≤ 1.5s, end-to-end ≤ 5s (Simple), 7s (Technical), 10s (Research/Multimedia)
- **Accuracy**: ≥1 inline citation per major answer claim, disagreements flagged
- **Intelligence**: Automatic model selection with provider fallback and cost-awareness
- **Observability**: Per-lane budgets, timeouts → partials, traceable via dashboards
- **Consistency**: Canonical names and environment keys used end-to-end

---

## 🏗️ **System Architecture**

### **High-Level Components**
```
┌─────────────────────────────────────────────────────────────┐
│                    SarvanOM v2 System                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js)     │  Backend (FastAPI)              │
│  - Cosmic Pro Design    │  - Multi-lane Orchestrator      │
│  - SSE Streaming        │  - Model Router                 │
│  - A11y First          │  - Auto-upgrade Policy          │
└─────────────────────────────────────────────────────────────┘
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                              │
│  Qdrant (Vector)  │  Meilisearch (Keyword)  │  ArangoDB (KG) │
└─────────────────────────────────────────────────────────────┘
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                External Dependencies                       │
│  LLM Providers  │  News Feeds  │  Markets  │  Web Sources  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 **External Dependencies**

### **LLM Providers**
| Provider | Purpose | Status | Cost Model |
|----------|---------|--------|------------|
| **OpenAI** | Primary text generation | ✅ **ACTIVE** | Pay-per-token |
| **Anthropic** | Claude models | ✅ **ACTIVE** | Pay-per-token |
| **HuggingFace** | Open-source models | ✅ **ACTIVE** | Free tier + paid |
| **Ollama** | Local models | ✅ **ACTIVE** | Free (self-hosted) |

### **Data Sources**
| Source | Purpose | Status | Rate Limits |
|--------|---------|--------|-------------|
| **Web Search** | Real-time information | ✅ **ACTIVE** | Provider-dependent |
| **News APIs** | Current events | ✅ **ACTIVE** | Free tier limits |
| **Markets APIs** | Financial data | ✅ **ACTIVE** | Free tier limits |
| **Knowledge Bases** | Structured data | ✅ **ACTIVE** | Internal |

### **Infrastructure**
| Component | Purpose | Status | SLA |
|-----------|---------|--------|-----|
| **PostgreSQL** | Primary database | ✅ **ACTIVE** | 99.9% |
| **Redis** | Caching layer | ✅ **ACTIVE** | 99.9% |
| **Qdrant** | Vector database | ✅ **ACTIVE** | 99.9% |
| **Meilisearch** | Full-text search | ✅ **ACTIVE** | 99.9% |
| **ArangoDB** | Knowledge graph | ✅ **ACTIVE** | 99.9% |

---

## 🔄 **Data Flow**

### **Query Processing Flow**
```
User Query → Frontend → API Gateway → Multi-lane Orchestrator
                                              │
                                              ├─ Web Retrieval Lane
                                              ├─ Vector Search Lane (Qdrant)
                                              ├─ Knowledge Graph Lane (ArangoDB)
                                              ├─ Keyword Search Lane (Meilisearch)
                                              └─ LLM Synthesis Lane
                                              │
                                              ↓
Response ← Frontend ← API Gateway ← Result Fusion ← Citations
```

### **Model Selection Flow**
```
Query Classification → Model Registry → Provider Selection → Fallback Chain
        │                    │                │
        ├─ Simple           ├─ Text Models   ├─ Primary Provider
        ├─ Technical        ├─ LMM Models    ├─ Secondary Provider
        ├─ Research         ├─ Tool Models   └─ Local Fallback
        └─ Multimedia       └─ Long Context
```

---

## 📊 **Performance Requirements**

### **SLOs (Service Level Objectives)**
| Query Type | End-to-End | TTFT | Success Rate | Availability |
|------------|------------|------|--------------|--------------|
| **Simple** | ≤ 5s | ≤ 1.5s | ≥ 95% | 99.9% |
| **Technical** | ≤ 7s | ≤ 1.5s | ≥ 90% | 99.9% |
| **Research** | ≤ 10s | ≤ 1.5s | ≥ 85% | 99.9% |
| **Multimedia** | ≤ 10s | ≤ 1.5s | ≥ 80% | 99.9% |

### **Capacity Requirements**
| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| **Concurrent Users** | 1000+ | 100+ | Scalable architecture |
| **Queries per Second** | 100+ | 10+ | Auto-scaling enabled |
| **Data Volume** | 1TB+ | 100GB+ | Distributed storage |
| **Response Size** | 10MB max | 1MB avg | Streaming for large responses |

---

## 🔒 **Security & Compliance**

### **Security Requirements**
- **Authentication**: JWT-based with service secrets
- **Authorization**: Role-based access control
- **Data Protection**: PII redaction and encryption at rest
- **Network Security**: HTTPS only, CORS configuration
- **Rate Limiting**: Per-IP and per-user limits

### **Compliance Requirements**
- **Data Privacy**: GDPR-compliant data handling
- **Audit Logging**: All actions logged with trace IDs
- **Data Retention**: Configurable retention policies
- **Source Attribution**: All citations properly attributed

---

## 🌍 **Deployment Architecture**

### **Environment Strategy**
| Environment | Purpose | Data | Scaling |
|-------------|---------|------|---------|
| **Development** | Local development | Mock data | Single instance |
| **Staging** | Pre-production testing | Production-like | Limited scaling |
| **Production** | Live service | Real data | Auto-scaling |

### **Infrastructure Components**
- **Load Balancer**: Distributes traffic across instances
- **API Gateway**: Routes requests to appropriate services
- **Database Cluster**: PostgreSQL with read replicas
- **Cache Layer**: Redis cluster for high availability
- **Vector Database**: Qdrant cluster for vector operations
- **Search Engine**: Meilisearch cluster for full-text search
- **Knowledge Graph**: ArangoDB cluster for graph operations

---

## 📈 **Scalability Considerations**

### **Horizontal Scaling**
- **Stateless Services**: All services designed for horizontal scaling
- **Database Sharding**: Partition data by user/tenant
- **Cache Distribution**: Redis cluster for distributed caching
- **Load Balancing**: Multiple instances behind load balancer

### **Vertical Scaling**
- **Resource Monitoring**: CPU, memory, disk usage tracking
- **Auto-scaling**: Automatic instance scaling based on metrics
- **Performance Tuning**: Database and cache optimization
- **Resource Limits**: Configurable resource limits per service

---

## 🔍 **Monitoring & Observability**

### **Metrics Collection**
- **Application Metrics**: Response times, error rates, throughput
- **Infrastructure Metrics**: CPU, memory, disk, network usage
- **Business Metrics**: Query success rates, user satisfaction
- **Custom Metrics**: Model performance, citation quality

### **Logging Strategy**
- **Structured Logging**: JSON format with consistent fields
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Trace IDs**: End-to-end request tracing
- **Log Aggregation**: Centralized log collection and analysis

### **Alerting**
- **SLO Violations**: Alert when SLOs are not met
- **Error Rates**: Alert on high error rates
- **Resource Usage**: Alert on high resource utilization
- **Security Events**: Alert on suspicious activities

---

## 🎯 **Success Criteria**

### **Technical Success**
- ✅ All SLOs met consistently
- ✅ 99.9% availability
- ✅ Sub-second TTFT for all query types
- ✅ Automatic model selection working
- ✅ Citation generation accurate

### **Business Success**
- ✅ User satisfaction > 90%
- ✅ Query success rate > 95%
- ✅ Cost per query optimized
- ✅ Response quality high
- ✅ System reliability proven

---

## 📚 **References**

- Architecture Overview: `04_architecture_overview.md`
- Model Orchestration: `05_model_orchestration.md`
- Retrieval & Index Fabric: `06_retrieval_and_index_fabric.md`
- Data Platform: `07_data_platform_qdrant_arango_meili.md`
- Observability: `09_observability_and_budgets.md`
- Security: `10_security_and_privacy.md`

---

*This system context document provides the foundation for all architectural decisions in SarvanOM v2.*
