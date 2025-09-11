# Qdrant Collections Schema - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Define Qdrant collection schema and warmup plan (no code)

---

## 🎯 **Qdrant Collections Overview**

Qdrant serves as the primary vector database for SarvanOM v2, storing embeddings for semantic search and similarity matching. The collections are designed for high-performance retrieval with proper indexing and warmup strategies.

### **Core Principles**
1. **Semantic Search**: Vector similarity for meaning-based retrieval
2. **High Performance**: Optimized for sub-second response times
3. **Scalability**: Support for millions of documents
4. **Flexibility**: Support for multiple embedding models
5. **Reliability**: Robust indexing and backup strategies

---

## 📊 **Collection Schema**

### **Primary Collection: `sarvanom_documents`**
| Field | Type | Description | Indexed | Required |
|-------|------|-------------|---------|----------|
| **id** | String | Unique document identifier | Yes | Yes |
| **vector** | Float[1536] | Document embedding vector | Yes | Yes |
| **title** | String | Document title | Yes | Yes |
| **content** | String | Document content | No | Yes |
| **url** | String | Source URL | Yes | Yes |
| **domain** | String | Source domain | Yes | Yes |
| **author** | String | Document author | No | No |
| **published_at** | Timestamp | Publication date | Yes | Yes |
| **language** | String | Document language | Yes | Yes |
| **category** | String | Document category | Yes | No |
| **tags** | String[] | Document tags | Yes | No |
| **word_count** | Integer | Word count | Yes | Yes |
| **relevance_score** | Float | Relevance score | Yes | Yes |
| **authority_score** | Float | Authority score | Yes | Yes |
| **accessibility** | String | Access level | Yes | Yes |
| **created_at** | Timestamp | Creation timestamp | Yes | Yes |
| **updated_at** | Timestamp | Update timestamp | Yes | Yes |

### **Secondary Collection: `sarvanom_entities`**
| Field | Type | Description | Indexed | Required |
|-------|------|-------------|---------|----------|
| **id** | String | Unique entity identifier | Yes | Yes |
| **vector** | Float[1536] | Entity embedding vector | Yes | Yes |
| **name** | String | Entity name | Yes | Yes |
| **type** | String | Entity type (person, org, concept) | Yes | Yes |
| **description** | String | Entity description | No | Yes |
| **aliases** | String[] | Entity aliases | Yes | No |
| **properties** | JSON | Entity properties | No | No |
| **relationships** | JSON | Entity relationships | No | No |
| **source_documents** | String[] | Source document IDs | Yes | Yes |
| **confidence** | Float | Entity confidence score | Yes | Yes |
| **created_at** | Timestamp | Creation timestamp | Yes | Yes |
| **updated_at** | Timestamp | Update timestamp | Yes | Yes |

### **Tertiary Collection: `sarvanom_passages`**
| Field | Type | Description | Indexed | Required |
|-------|------|-------------|---------|----------|
| **id** | String | Unique passage identifier | Yes | Yes |
| **vector** | Float[1536] | Passage embedding vector | Yes | Yes |
| **document_id** | String | Parent document ID | Yes | Yes |
| **passage_text** | String | Passage content | No | Yes |
| **passage_start** | Integer | Start position in document | Yes | Yes |
| **passage_end** | Integer | End position in document | Yes | Yes |
| **passage_type** | String | Passage type (intro, body, conclusion) | Yes | No |
| **entities** | String[] | Mentioned entities | Yes | No |
| **keywords** | String[] | Key terms | Yes | No |
| **relevance_score** | Float | Passage relevance | Yes | Yes |
| **created_at** | Timestamp | Creation timestamp | Yes | Yes |

---

## 🔧 **Collection Configuration**

### **Vector Configuration**
| Parameter | Value | Description |
|-----------|-------|-------------|
| **Vector Size** | 1536 | OpenAI embedding dimension |
| **Distance Metric** | Cosine | Cosine similarity |
| **Quantization** | Scalar | 8-bit quantization |
| **On-Disk Storage** | True | Store vectors on disk |
| **HNSW Index** | True | Hierarchical Navigable Small World |

### **HNSW Index Configuration**
| Parameter | Value | Description |
|-----------|-------|-------------|
| **M** | 16 | Number of bi-directional links |
| **Ef Construction** | 200 | Size of dynamic candidate list |
| **Ef Search** | 100 | Size of dynamic candidate list for search |
| **Max Indexing Threads** | 4 | Number of indexing threads |

### **Payload Index Configuration**
| Field | Index Type | Description |
|-------|------------|-------------|
| **title** | Text | Full-text search on titles |
| **domain** | Keyword | Exact match on domains |
| **published_at** | Integer | Range queries on dates |
| **language** | Keyword | Exact match on languages |
| **category** | Keyword | Exact match on categories |
| **tags** | Keyword | Multi-value keyword search |
| **word_count** | Integer | Range queries on word count |
| **relevance_score** | Float | Range queries on relevance |
| **authority_score** | Float | Range queries on authority |

---

## 📈 **Collection Warmup Plan**

### **Warmup Strategy**
| Phase | Duration | Description | Target |
|-------|----------|-------------|--------|
| **Phase 1** | 1 hour | Load core documents | 10,000 documents |
| **Phase 2** | 4 hours | Load entity data | 50,000 entities |
| **Phase 3** | 8 hours | Load passage data | 100,000 passages |
| **Phase 4** | 2 hours | Optimize indices | All collections |
| **Phase 5** | 1 hour | Performance testing | Full system |

### **Warmup Implementation Plan**
```yaml
# Warmup configuration
warmup:
  collections:
    - name: "sarvanom_documents"
      priority: 1
      batch_size: 1000
      concurrency: 4
      target_count: 10000
      
    - name: "sarvanom_entities"
      priority: 2
      batch_size: 500
      concurrency: 2
      target_count: 50000
      
    - name: "sarvanom_passages"
      priority: 3
      batch_size: 2000
      concurrency: 6
      target_count: 100000
  
  performance_targets:
    search_latency: "< 50ms"
    indexing_throughput: "> 1000 docs/sec"
    memory_usage: "< 8GB"
    disk_usage: "< 100GB"
```

### **Warmup Data Sources**
| Source | Type | Count | Priority |
|--------|------|-------|----------|
| **Wikipedia** | Documents | 5,000 | High |
| **ArXiv Papers** | Documents | 2,000 | High |
| **News Articles** | Documents | 2,000 | Medium |
| **Technical Blogs** | Documents | 1,000 | Medium |
| **Entity Database** | Entities | 50,000 | High |
| **Passage Extracts** | Passages | 100,000 | Medium |

---

## 🔍 **Search Configuration**

### **Search Parameters**
| Parameter | Value | Description |
|-----------|-------|-------------|
| **Top K** | 100 | Maximum results per search |
| **Score Threshold** | 0.7 | Minimum similarity score |
| **Timeout** | 1000ms | Search timeout |
| **Consistency** | Strong | Read consistency level |

### **Filter Configuration**
| Filter Type | Description | Use Case |
|-------------|-------------|----------|
| **Domain Filter** | Filter by source domain | Source-specific search |
| **Date Range** | Filter by publication date | Time-based search |
| **Language Filter** | Filter by document language | Language-specific search |
| **Category Filter** | Filter by document category | Topic-specific search |
| **Authority Filter** | Filter by authority score | Quality-based search |
| **Accessibility Filter** | Filter by access level | Access-based search |

### **Search Optimization**
| Optimization | Description | Impact |
|--------------|-------------|--------|
| **Vector Quantization** | 8-bit quantization | 4x memory reduction |
| **Payload Indexing** | Indexed payload fields | 10x faster filtering |
| **Batch Processing** | Batch multiple searches | 3x throughput increase |
| **Connection Pooling** | Reuse connections | 2x latency reduction |

---

## 📊 **Performance Monitoring**

### **Key Metrics**
| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| **Search Latency** | Average search time | < 50ms | > 100ms |
| **Indexing Throughput** | Documents indexed per second | > 1000 | < 500 |
| **Memory Usage** | RAM usage | < 8GB | > 12GB |
| **Disk Usage** | Storage usage | < 100GB | > 150GB |
| **Query Success Rate** | % of successful queries | > 99% | < 95% |
| **Index Health** | Index integrity score | > 95% | < 90% |

### **Monitoring Implementation**
```yaml
# Monitoring configuration
monitoring:
  metrics:
    - name: "search_latency"
      type: "histogram"
      buckets: [10, 25, 50, 100, 250, 500, 1000]
      
    - name: "indexing_throughput"
      type: "counter"
      unit: "docs/sec"
      
    - name: "memory_usage"
      type: "gauge"
      unit: "bytes"
      
    - name: "disk_usage"
      type: "gauge"
      unit: "bytes"
      
    - name: "query_success_rate"
      type: "gauge"
      unit: "percent"
      
    - name: "index_health"
      type: "gauge"
      unit: "percent"
  
  alerts:
    - name: "high_search_latency"
      condition: "search_latency > 100ms"
      severity: "warning"
      
    - name: "low_indexing_throughput"
      condition: "indexing_throughput < 500 docs/sec"
      severity: "warning"
      
    - name: "high_memory_usage"
      condition: "memory_usage > 12GB"
      severity: "critical"
      
    - name: "low_query_success_rate"
      condition: "query_success_rate < 95%"
      severity: "critical"
```

---

## 🔄 **Backup & Recovery**

### **Backup Strategy**
| Backup Type | Frequency | Retention | Location |
|-------------|-----------|-----------|----------|
| **Full Backup** | Daily | 30 days | S3 |
| **Incremental** | Every 6 hours | 7 days | S3 |
| **Snapshot** | Weekly | 12 weeks | S3 |
| **Point-in-Time** | Continuous | 24 hours | Local |

### **Recovery Plan**
| Recovery Type | RTO | RPO | Description |
|---------------|-----|-----|-------------|
| **Full Recovery** | 2 hours | 24 hours | Complete system restore |
| **Partial Recovery** | 30 minutes | 6 hours | Collection-level restore |
| **Point-in-Time** | 15 minutes | 1 hour | Specific timestamp restore |
| **Disaster Recovery** | 4 hours | 24 hours | Cross-region restore |

---

## 🚀 **Scaling Strategy**

### **Horizontal Scaling**
| Scale Factor | Description | Implementation |
|--------------|-------------|----------------|
| **2x** | Double collection size | Add replica nodes |
| **5x** | 5x collection size | Shard collections |
| **10x** | 10x collection size | Multi-region deployment |
| **100x** | 100x collection size | Distributed architecture |

### **Vertical Scaling**
| Resource | Current | 2x | 5x | 10x |
|----------|---------|----|----|----|
| **CPU** | 8 cores | 16 cores | 32 cores | 64 cores |
| **RAM** | 32GB | 64GB | 128GB | 256GB |
| **Storage** | 500GB | 1TB | 2TB | 5TB |
| **Network** | 1Gbps | 10Gbps | 25Gbps | 100Gbps |

---

## 📚 **References**

- Retrieval & Index Fabric: `06_retrieval_and_index_fabric.md`
- Data Platform: `07_data_platform_qdrant_arango_meili.md`
- Fusion Policy: `docs/retrieval/fusion_policy.md`
- Citations Contract: `docs/retrieval/citations_contract.md`
- System Context: `docs/architecture/system_context.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This Qdrant collections schema provides the foundation for high-performance semantic search in SarvanOM v2.*
