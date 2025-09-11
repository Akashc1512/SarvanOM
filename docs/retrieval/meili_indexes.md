# Meilisearch Indexes - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Define Meilisearch indexes for full-text search and keyword matching

---

## 🎯 **Meilisearch Overview**

Meilisearch serves as the full-text search engine for SarvanOM v2, providing fast keyword matching, typo tolerance, and faceted search capabilities. It complements Qdrant's semantic search with exact keyword matching.

### **Core Principles**
1. **Fast Keyword Search**: Sub-20ms response times for keyword queries
2. **Typo Tolerance**: Handle misspellings and typos gracefully
3. **Faceted Search**: Filter results by multiple criteria
4. **Relevance Ranking**: Intelligent ranking based on multiple factors
5. **Real-time Updates**: Immediate index updates for new content

---

## 📊 **Index Schema**

### **Primary Index: `sarvanom_documents`**
| Field | Type | Description | Searchable | Filterable | Sortable |
|-------|------|-------------|------------|------------|----------|
| **id** | String | Unique document identifier | No | Yes | No |
| **title** | String | Document title | Yes | Yes | Yes |
| **content** | String | Document content | Yes | No | No |
| **excerpt** | String | Document excerpt | Yes | No | No |
| **url** | String | Source URL | No | Yes | No |
| **domain** | String | Source domain | No | Yes | Yes |
| **author** | String | Document author | Yes | Yes | Yes |
| **published_at** | Timestamp | Publication date | No | Yes | Yes |
| **language** | String | Document language | No | Yes | Yes |
| **category** | String | Document category | Yes | Yes | Yes |
| **tags** | String[] | Document tags | Yes | Yes | No |
| **keywords** | String[] | Extracted keywords | Yes | Yes | No |
| **word_count** | Integer | Word count | No | Yes | Yes |
| **relevance_score** | Float | Relevance score | No | Yes | Yes |
| **authority_score** | Float | Authority score | No | Yes | Yes |
| **accessibility** | String | Access level | No | Yes | Yes |
| **created_at** | Timestamp | Creation timestamp | No | Yes | Yes |
| **updated_at** | Timestamp | Update timestamp | No | Yes | Yes |

### **Secondary Index: `sarvanom_entities`**
| Field | Type | Description | Searchable | Filterable | Sortable |
|-------|------|-------------|------------|------------|----------|
| **id** | String | Unique entity identifier | No | Yes | No |
| **name** | String | Entity name | Yes | Yes | Yes |
| **type** | String | Entity type | No | Yes | Yes |
| **description** | String | Entity description | Yes | No | No |
| **aliases** | String[] | Entity aliases | Yes | Yes | No |
| **properties** | JSON | Entity properties | No | Yes | No |
| **source_documents** | String[] | Source document IDs | No | Yes | No |
| **confidence** | Float | Entity confidence | No | Yes | Yes |
| **created_at** | Timestamp | Creation timestamp | No | Yes | Yes |

### **Tertiary Index: `sarvanom_passages`**
| Field | Type | Description | Searchable | Filterable | Sortable |
|-------|------|-------------|------------|------------|----------|
| **id** | String | Unique passage identifier | No | Yes | No |
| **document_id** | String | Parent document ID | No | Yes | No |
| **passage_text** | String | Passage content | Yes | No | No |
| **passage_type** | String | Passage type | No | Yes | Yes |
| **entities** | String[] | Mentioned entities | Yes | Yes | No |
| **keywords** | String[] | Key terms | Yes | Yes | No |
| **relevance_score** | Float | Passage relevance | No | Yes | Yes |
| **created_at** | Timestamp | Creation timestamp | No | Yes | Yes |

---

## 🔧 **Index Configuration**

### **Search Configuration**
| Parameter | Value | Description |
|-----------|-------|-------------|
| **Typo Tolerance** | Enabled | Handle typos and misspellings |
| **Max Typos** | 2 | Maximum typos per word |
| **Min Word Size** | 2 | Minimum word size for indexing |
| **Stop Words** | Custom | Custom stop words list |
| **Synonyms** | Custom | Custom synonyms dictionary |
| **Ranking Rules** | Custom | Custom ranking algorithm |

### **Ranking Rules**
| Rule | Weight | Description |
|------|--------|-------------|
| **Words** | 1 | Exact word matches |
| **Typo** | 2 | Typo-corrected matches |
| **Proximity** | 3 | Word proximity |
| **Attribute** | 4 | Field-specific ranking |
| **Sort** | 5 | Custom sorting |
| **Exactness** | 6 | Exact phrase matches |

### **Typo Tolerance Configuration**
| Parameter | Value | Description |
|-----------|-------|-------------|
| **Enabled** | True | Enable typo tolerance |
| **Min Word Size** | 2 | Minimum word size |
| **Min Word Size for Typos** | 4 | Minimum size for typo correction |
| **Max Typos** | 2 | Maximum typos per word |
| **Max Typos for One Typo** | 1 | Maximum typos for one-typo words |
| **Max Typos for Two Typos** | 2 | Maximum typos for two-typo words |

---

## 🔍 **Search Configuration**

### **Search Parameters**
| Parameter | Value | Description |
|-----------|-------|-------------|
| **Query** | String | Search query |
| **Limit** | 100 | Maximum results |
| **Offset** | 0 | Result offset |
| **Attributes to Retrieve** | All | Fields to return |
| **Attributes to Crop** | content, excerpt | Fields to crop |
| **Crop Length** | 200 | Crop length in characters |
| **Attributes to Highlight** | title, content | Fields to highlight |
| **Highlight Pre Tag** | <mark> | Highlight opening tag |
| **Highlight Post Tag** | </mark> | Highlight closing tag |
| **Show Matches Position** | True | Show match positions |
| **Show Ranking Score** | True | Show ranking scores |

### **Filter Configuration**
| Filter Type | Description | Example |
|-------------|-------------|---------|
| **Equality** | Exact match | `domain = "wikipedia.org"` |
| **Inequality** | Range match | `published_at > 2024-01-01` |
| **Array Contains** | Array membership | `tags IN ["AI", "ML"]` |
| **Array Not Contains** | Array exclusion | `tags NOT IN ["spam"]` |
| **Null Check** | Null/not null | `author IS NOT NULL` |
| **String Contains** | Substring match | `title CONTAINS "artificial"` |

### **Sort Configuration**
| Sort Field | Direction | Description |
|------------|-----------|-------------|
| **relevance_score** | Desc | Sort by relevance |
| **published_at** | Desc | Sort by publication date |
| **authority_score** | Desc | Sort by authority |
| **word_count** | Asc | Sort by word count |
| **created_at** | Desc | Sort by creation date |

---

## 📈 **Performance Optimization**

### **Indexing Optimization**
| Optimization | Description | Impact |
|--------------|-------------|--------|
| **Batch Indexing** | Index documents in batches | 5x faster indexing |
| **Async Indexing** | Asynchronous index updates | 3x better throughput |
| **Compression** | Compress stored data | 2x storage reduction |
| **Memory Mapping** | Use memory-mapped files | 1.5x faster access |

### **Search Optimization**
| Optimization | Description | Impact |
|--------------|-------------|--------|
| **Query Caching** | Cache frequent queries | 10x faster repeated searches |
| **Result Caching** | Cache search results | 5x faster result retrieval |
| **Connection Pooling** | Reuse connections | 2x latency reduction |
| **Parallel Search** | Parallel query execution | 3x throughput increase |

### **Memory Optimization**
| Optimization | Description | Impact |
|--------------|-------------|--------|
| **Memory Mapping** | Map files to memory | 2x faster access |
| **Compression** | Compress in-memory data | 3x memory reduction |
| **Garbage Collection** | Optimize GC settings | 1.5x better performance |
| **Cache Management** | Smart cache eviction | 2x better hit rate |

---

## 📊 **Monitoring & Metrics**

### **Key Metrics**
| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| **Search Latency** | Average search time | < 20ms | > 50ms |
| **Indexing Throughput** | Documents indexed per second | > 2000 | < 1000 |
| **Memory Usage** | RAM usage | < 4GB | > 6GB |
| **Disk Usage** | Storage usage | < 50GB | > 75GB |
| **Query Success Rate** | % of successful queries | > 99% | < 95% |
| **Index Health** | Index integrity score | > 95% | < 90% |

### **Performance Monitoring**
```yaml
# Monitoring configuration
monitoring:
  metrics:
    - name: "search_latency"
      type: "histogram"
      buckets: [5, 10, 20, 50, 100, 250, 500]
      
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
      condition: "search_latency > 50ms"
      severity: "warning"
      
    - name: "low_indexing_throughput"
      condition: "indexing_throughput < 1000 docs/sec"
      severity: "warning"
      
    - name: "high_memory_usage"
      condition: "memory_usage > 6GB"
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
| **Incremental** | Every 4 hours | 7 days | S3 |
| **Snapshot** | Weekly | 12 weeks | S3 |
| **Point-in-Time** | Continuous | 12 hours | Local |

### **Recovery Plan**
| Recovery Type | RTO | RPO | Description |
|---------------|-----|-----|-------------|
| **Full Recovery** | 1 hour | 12 hours | Complete system restore |
| **Partial Recovery** | 15 minutes | 4 hours | Index-level restore |
| **Point-in-Time** | 10 minutes | 1 hour | Specific timestamp restore |
| **Disaster Recovery** | 2 hours | 12 hours | Cross-region restore |

---

## 🚀 **Scaling Strategy**

### **Horizontal Scaling**
| Scale Factor | Description | Implementation |
|--------------|-------------|----------------|
| **2x** | Double index size | Add replica nodes |
| **5x** | 5x index size | Shard indexes |
| **10x** | 10x index size | Multi-region deployment |
| **100x** | 100x index size | Distributed architecture |

### **Vertical Scaling**
| Resource | Current | 2x | 5x | 10x |
|----------|---------|----|----|----|
| **CPU** | 4 cores | 8 cores | 16 cores | 32 cores |
| **RAM** | 16GB | 32GB | 64GB | 128GB |
| **Storage** | 200GB | 500GB | 1TB | 2TB |
| **Network** | 1Gbps | 10Gbps | 25Gbps | 100Gbps |

---

## 📚 **References**

- Retrieval & Index Fabric: `06_retrieval_and_index_fabric.md`
- Data Platform: `07_data_platform_qdrant_arango_meili.md`
- Qdrant Collections: `docs/retrieval/qdrant_collections.md`
- Fusion Policy: `docs/retrieval/fusion_policy.md`
- Citations Contract: `docs/retrieval/citations_contract.md`
- System Context: `docs/architecture/system_context.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This Meilisearch indexes specification provides the foundation for fast full-text search in SarvanOM v2.*
