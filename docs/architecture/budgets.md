# Lane Budgets & Global Deadlines - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE ARCHITECTURE**  
**Purpose**: Define lane budgets and global deadlines per intent (5s/7s/10s + orchestrator reserve)

---

## 🎯 **Budget Philosophy**

SarvanOM v2 implements strict time budgets to ensure consistent performance across all query types. The system uses a multi-lane orchestration approach where each lane has a specific budget, and the orchestrator reserves time for coordination and result fusion.

### **Core Principles**
1. **Predictable Performance**: Every query type has a guaranteed maximum response time
2. **Graceful Degradation**: Lanes that exceed their budget return partial results
3. **Orchestrator Reserve**: Always reserve time for coordination and fusion
4. **SLO Compliance**: All budgets designed to meet SLO requirements

---

## ⏱️ **Global Deadlines by Query Mode**

### **Query Mode Classification**
| Mode | Description | Global Deadline | TTFT Target | Success Rate Target |
|------|-------------|-----------------|-------------|-------------------|
| **Simple** | Basic questions, definitions | 5 seconds | ≤ 1.5s | ≥ 95% |
| **Technical** | Code, technical explanations | 7 seconds | ≤ 1.5s | ≥ 90% |
| **Research** | Complex analysis, multiple sources | 10 seconds | ≤ 1.5s | ≥ 85% |
| **Multimedia** | Images, documents, multimodal | 10 seconds | ≤ 1.5s | ≥ 80% |

### **Deadline Allocation Strategy**
```
Global Deadline = Orchestrator Reserve + Lane Budgets + Fusion Time

Example (Simple Query - 5s total):
├─ Orchestrator Reserve: 500ms
├─ Lane Budgets: 4000ms
│  ├─ Web Retrieval: 1000ms
│  ├─ Vector Search: 1000ms
│  ├─ Knowledge Graph: 1000ms
│  └─ LLM Synthesis: 1000ms
└─ Fusion Time: 500ms
```

---

## 🛤️ **Lane Budgets**

### **Lane Budget Matrix**
| Lane | Simple (5s) | Technical (7s) | Research (10s) | Multimedia (10s) |
|------|-------------|----------------|----------------|------------------|
| **Guided Prompt Pre-flight** | 500ms | 500ms | 500ms | 500ms |
| **Web Retrieval** | 1000ms | 1500ms | 2000ms | 2000ms |
| **Vector Search** | 1000ms | 1500ms | 2000ms | 2000ms |
| **Knowledge Graph** | 1000ms | 1500ms | 2000ms | 2000ms |
| **Keyword Search** | 500ms | 750ms | 1000ms | 1000ms |
| **LLM Synthesis** | 1000ms | 1500ms | 2000ms | 2000ms |
| **Fact Check** | 500ms | 750ms | 1000ms | 1000ms |
| **News Feeds** | 300ms | 500ms | 800ms | 800ms |
| **Markets Feeds** | 300ms | 500ms | 800ms | 800ms |

### **Lane Budget Rationale**

#### **Guided Prompt Pre-flight Lane**
- **Purpose**: Analyze user intent and refine prompts before main execution
- **Budget**: 500ms (consistent across all query types)
- **Timeout Strategy**: Auto-skip refinement if budget exceeded
- **Fallback**: Run original query without refinement
- **Bypass Rules**: Skip if any lane has <25% of global budget remaining

#### **Web Retrieval Lane**
- **Purpose**: Fetch real-time information from web sources
- **Budget**: 1-2s depending on complexity
- **Timeout Strategy**: Return cached results if available
- **Fallback**: Use knowledge base if web fails

#### **Vector Search Lane**
- **Purpose**: Semantic similarity search in vector database
- **Budget**: 1-2s depending on complexity
- **Timeout Strategy**: Return top-k results with lower confidence
- **Fallback**: Use keyword search if vector search fails

#### **Knowledge Graph Lane**
- **Purpose**: Entity relationship queries and graph traversal
- **Budget**: 1-2s depending on complexity
- **Timeout Strategy**: Return partial graph results
- **Fallback**: Use vector search if graph query fails

#### **Keyword Search Lane**
- **Purpose**: Exact keyword matching and full-text search
- **Budget**: 0.5-1s depending on complexity
- **Timeout Strategy**: Return top results with basic ranking
- **Fallback**: Use vector search if keyword search fails

#### **LLM Synthesis Lane**
- **Purpose**: Generate final response using selected LLM
- **Budget**: 1-2s depending on complexity
- **Timeout Strategy**: Return partial response with continuation token
- **Fallback**: Use faster model if primary model fails

#### **Fact Check Lane**
- **Purpose**: Verify claims and detect disagreements
- **Budget**: 0.5-1s depending on complexity
- **Timeout Strategy**: Return basic verification without deep analysis
- **Fallback**: Skip fact-checking if timeout occurs

#### **News Feeds Lane**
- **Purpose**: Fetch current news and events
- **Budget**: 0.3-0.8s depending on complexity
- **Timeout Strategy**: Return cached news if available
- **Fallback**: Use web search if news feeds fail

#### **Markets Feeds Lane**
- **Purpose**: Fetch financial and market data
- **Budget**: 0.3-0.8s depending on complexity
- **Timeout Strategy**: Return cached market data if available
- **Fallback**: Use web search if markets feeds fail

---

## 🎯 **Guided Prompt Pre-flight Budget**

### **Pre-flight Budget Details**
| Metric | Target | Alert Threshold | Action |
|--------|--------|-----------------|--------|
| **Median Latency** | ≤ 500ms | > 600ms | Investigate performance |
| **P95 Latency** | ≤ 800ms | > 1000ms | Auto-skip refinement |
| **Success Rate** | ≥ 95% | < 90% | Review model selection |
| **Acceptance Rate** | ≥ 45% | < 30% | Tune refinement prompts |

### **Bypass Conditions**
1. **Budget Exceeded**: If pre-flight takes > 800ms (p95), auto-skip refinement
2. **System Pressure**: If any lane has <25% of global budget remaining, skip refinement
3. **Model Unavailable**: If refinement model is down, skip refinement
4. **User Override**: If user has "Always bypass" setting enabled

### **Pre-flight Budget Allocation**
```
Guided Prompt Pre-flight (500ms total):
├─ Intent Analysis: 200ms
├─ Prompt Refinement: 200ms
├─ Constraint Application: 50ms
└─ Response Generation: 50ms
```

### **Budget Monitoring**
```python
# Example pre-flight budget monitoring
class GuidedPromptBudgetMonitor:
    def check_budget_availability(self, global_budget_remaining):
        # Check if any lane has <25% budget remaining
        for lane in self.active_lanes:
            if lane.budget_remaining < (lane.total_budget * 0.25):
                return False  # Skip refinement
        return True
    
    def should_skip_refinement(self, elapsed_ms, global_budget_remaining):
        if elapsed_ms > 800:  # P95 threshold
            return True
        if not self.check_budget_availability(global_budget_remaining):
            return True
        return False
```

---

## 🎛️ **Orchestrator Reserve**

### **Reserve Time Allocation**
| Phase | Simple (5s) | Technical (7s) | Research (10s) | Multimedia (10s) |
|-------|-------------|----------------|----------------|------------------|
| **Query Classification** | 50ms | 50ms | 50ms | 50ms |
| **Lane Coordination** | 100ms | 150ms | 200ms | 200ms |
| **Result Fusion** | 200ms | 300ms | 400ms | 400ms |
| **Response Formatting** | 100ms | 150ms | 200ms | 200ms |
| **Error Handling** | 50ms | 50ms | 50ms | 50ms |
| **Total Reserve** | 500ms | 700ms | 900ms | 900ms |

### **Reserve Time Breakdown**

#### **Query Classification (50ms)**
- **Purpose**: Determine query mode and complexity
- **Operations**: NLP analysis, intent detection, mode selection
- **Timeout Strategy**: Default to "simple" mode if classification fails

#### **Lane Coordination (100-200ms)**
- **Purpose**: Start parallel lane execution
- **Operations**: Lane initialization, dependency resolution, parallel execution
- **Timeout Strategy**: Start lanes with reduced budgets if coordination takes too long

#### **Result Fusion (200-400ms)**
- **Purpose**: Combine results from multiple lanes
- **Operations**: Deduplication, ranking, citation alignment, confidence scoring
- **Timeout Strategy**: Use simple fusion if complex fusion takes too long

#### **Response Formatting (100-200ms)**
- **Purpose**: Format final response for client
- **Operations**: JSON serialization, streaming setup, metadata addition
- **Timeout Strategy**: Use basic formatting if advanced formatting fails

#### **Error Handling (50ms)**
- **Purpose**: Handle errors and timeouts gracefully
- **Operations**: Error aggregation, fallback selection, partial result handling
- **Timeout Strategy**: Return error response if error handling fails

---

## ⚡ **Timeout & Degradation Strategies**

### **Lane Timeout Handling**
```python
# Example timeout handling strategy
class LaneTimeoutHandler:
    def handle_timeout(self, lane_name, budget_ms, elapsed_ms):
        if elapsed_ms >= budget_ms:
            return {
                "status": "timeout",
                "partial_results": self.get_partial_results(lane_name),
                "timeout_reason": f"Exceeded budget of {budget_ms}ms",
                "elapsed_ms": elapsed_ms
            }
        return None
```

### **Degradation Levels**
| Level | Description | Action | Impact |
|-------|-------------|--------|--------|
| **Level 1** | Lane timeout | Return partial results | Reduced quality |
| **Level 2** | Multiple lane timeouts | Use fallback lanes | Lower confidence |
| **Level 3** | Critical lane failure | Return cached results | Stale information |
| **Level 4** | System overload | Return error with retry | Service unavailable |

### **Fallback Chain**
```
Primary Lane → Secondary Lane → Cached Results → Error Response

Example (Vector Search):
Qdrant → Meilisearch → Redis Cache → Error
```

---

## 📊 **Budget Monitoring & Metrics**

### **Key Metrics**
| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| **Lane Success Rate** | % of lanes completing within budget | ≥ 95% | < 90% |
| **Average Lane Time** | Mean time per lane | < 80% of budget | > 90% of budget |
| **Timeout Rate** | % of lanes timing out | < 5% | > 10% |
| **Fusion Time** | Time spent on result fusion | < 50% of reserve | > 70% of reserve |
| **SLO Compliance** | % of queries meeting SLO | ≥ 95% | < 90% |

### **Budget Utilization Tracking**
```python
# Example budget tracking
class BudgetTracker:
    def track_lane_performance(self, lane_name, budget_ms, actual_ms):
        utilization = (actual_ms / budget_ms) * 100
        
        metrics = {
            "lane_name": lane_name,
            "budget_ms": budget_ms,
            "actual_ms": actual_ms,
            "utilization_percent": utilization,
            "within_budget": actual_ms <= budget_ms,
            "timestamp": time.time()
        }
        
        self.record_metrics(metrics)
        return metrics
```

---

## 🔧 **Budget Configuration**

### **Environment Variables**
| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `LANE_BUDGET_SIMPLE_MS` | 5000 | Simple query total budget | 5000 |
| `LANE_BUDGET_TECHNICAL_MS` | 7000 | Technical query total budget | 7000 |
| `LANE_BUDGET_RESEARCH_MS` | 10000 | Research query total budget | 10000 |
| `LANE_BUDGET_MULTIMEDIA_MS` | 10000 | Multimedia query total budget | 10000 |
| `ORCHESTRATOR_RESERVE_MS` | 500 | Orchestrator reserve time | 500 |
| `SLA_TTFT_MAX_MS` | 1500 | Maximum time to first token | 1500 |

### **Dynamic Budget Adjustment**
```python
# Example dynamic budget adjustment
class DynamicBudgetManager:
    def adjust_budgets(self, system_load, historical_performance):
        if system_load > 0.8:  # High load
            return self.reduce_budgets_by_percent(10)
        elif system_load < 0.3:  # Low load
            return self.increase_budgets_by_percent(5)
        else:
            return self.get_default_budgets()
```

---

## 🎯 **Budget Validation & Testing**

### **Budget Validation Tests**
| Test Type | Description | Success Criteria |
|-----------|-------------|------------------|
| **Unit Tests** | Individual lane budget compliance | All lanes complete within budget |
| **Integration Tests** | End-to-end budget compliance | Total time within global deadline |
| **Load Tests** | Budget compliance under load | SLO compliance maintained |
| **Stress Tests** | Budget behavior under stress | Graceful degradation |

### **Budget Testing Framework**
```python
# Example budget testing
class BudgetTestSuite:
    def test_simple_query_budget(self):
        start_time = time.time()
        result = self.process_query("What is AI?", mode="simple")
        elapsed = (time.time() - start_time) * 1000
        
        assert elapsed <= 5000, f"Simple query took {elapsed}ms, exceeds 5000ms budget"
        assert result["status"] == "success"
    
    def test_lane_timeout_handling(self):
        # Simulate lane timeout
        result = self.process_query_with_timeout("Complex query", timeout_ms=1000)
        
        assert result["status"] == "partial"
        assert "timeout" in result["lane_metrics"]
```

---

## 📈 **Budget Optimization**

### **Optimization Strategies**
1. **Lane Parallelization**: Run independent lanes in parallel
2. **Caching**: Cache frequent results to reduce lane execution time
3. **Model Selection**: Use faster models for simple queries
4. **Result Streaming**: Stream results as they become available
5. **Predictive Scaling**: Scale resources based on predicted load

### **Performance Tuning**
| Optimization | Impact | Implementation |
|--------------|--------|----------------|
| **Connection Pooling** | 20-30% faster | Reuse database connections |
| **Result Caching** | 50-70% faster | Cache frequent query results |
| **Model Caching** | 10-20% faster | Cache model responses |
| **Parallel Execution** | 40-60% faster | Run lanes concurrently |
| **Streaming Responses** | 30-50% faster | Stream results to client |

---

## 📚 **References**

- System Context: `docs/architecture/system_context.md`
- Service Catalog: `docs/architecture/service_catalog.md`
- Retrieval & Index Fabric: `06_retrieval_and_index_fabric.md`
- Observability: `09_observability_and_budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This budget specification ensures predictable performance and SLO compliance across all query types in SarvanOM v2.*
