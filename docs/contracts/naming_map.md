# Cross-Repository Naming Map

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Single source of truth for canonical parameter names across API, UI, logs, metrics, and config

---

## 🎯 **Canonical Parameter Names**

### **Core Parameters**
| Canonical Name | Forbidden Synonyms | Usage | Example |
|----------------|-------------------|-------|---------|
| `top_k` | `limit`, `k`, `topk`, `count` | Vector search results | `top_k: 10` |
| `temperature` | `temp`, `t` | LLM randomness | `temperature: 0.7` |
| `max_tokens` | `max_tok`, `tokens`, `length` | Response length | `max_tokens: 1000` |
| `seed` | `random_seed`, `rng_seed` | Reproducibility | `seed: 42` |
| `system_prompt` | `sys_prompt`, `instruction` | System context | `system_prompt: "You are..."` |
| `user_prompt` | `user_input`, `query`, `prompt` | User input | `user_prompt: "What is..."` |

### **Provider & Model Parameters**
| Canonical Name | Forbidden Synonyms | Usage | Example |
|----------------|-------------------|-------|---------|
| `provider` | `llm_provider`, `model_provider` | Provider selection | `provider: "openai"` |
| `model_id` | `model`, `model_name` | Full model identifier | `model_id: "gpt-4o"` |
| `model_family` | `family`, `base_model` | Model family | `model_family: "gpt-4o"` |

### **Query Mode Parameters**
| Canonical Name | Forbidden Synonyms | Usage | Example |
|----------------|-------------------|-------|---------|
| `mode` | `query_mode`, `type` | Query complexity | `mode: "simple"` |
| `deadline_ms` | `deadline`, `timeout`, `max_time` | Global request deadline | `deadline_ms: 5000` |
| `lane_budget_ms` | `budget`, `lane_timeout`, `timeout_ms` | Per-lane budget | `lane_budget_ms: 2000` |

### **Performance Metrics**
| Canonical Name | Forbidden Synonyms | Usage | Example |
|----------------|-------------------|-------|---------|
| `ttft_ms` | `first_byte`, `ttfb`, `first_token` | Time to first token | `ttft_ms: 150` |
| `finalize_ms` | `completion_time`, `total_time` | Time to completion | `finalize_ms: 2500` |
| `answered_under_slo` | `slo_met`, `within_slo` | SLO compliance | `answered_under_slo: true` |

### **Response Quality Metrics**
| Canonical Name | Forbidden Synonyms | Usage | Example |
|----------------|-------------------|-------|---------|
| `citations_count` | `citation_count`, `num_citations` | Number of citations | `citations_count: 3` |
| `disagreement_detected` | `has_disagreement`, `conflict` | Disagreement flag | `disagreement_detected: false` |

---

## 📋 **Response Fields (Minimum Set)**

### **Core Response Fields**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `answer_stream` | SSE Stream | Streaming response | `data: {"token": "Hello"}` |
| `citations` | Array | Citation objects | `[{"id": 1, "source": "...", "url": "..."}]` |
| `lane_metrics` | Object | Per-lane timing data | `{"vector": {"time_ms": 200}}` |
| `trace_id` | String | End-to-end trace ID | `trace_id: "abc123"` |

### **Citation Object Schema**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | Integer | Citation ID | `id: 1` |
| `source` | String | Source name | `source: "Wikipedia"` |
| `url` | String | Source URL | `url: "https://..."` |
| `passage` | String | Quoted text | `passage: "The sky is blue..."` |
| `published_at` | ISO Date | Publication date | `published_at: "2025-01-01T00:00:00Z"` |

---

## 🚫 **Provider Key Synonyms → Forbidden**

### **Environment Variable Forbidden Synonyms**
| Forbidden | Canonical | Context | Action |
|-----------|-----------|---------|--------|
| `FINNHUB_API_KEY` | `FINNHUB_KEY` | Finnhub provider | Never use API_KEY suffix |
| `ALPHAVANTAGE_API_KEY` | `ALPHAVANTAGE_KEY` | Alpha Vantage provider | Never use API_KEY suffix |
| `GUARDIAN_API_KEY` | `GUARDIAN_OPEN_PLATFORM_KEY` | Guardian provider | Use full canonical name |
| `NEWS_API_KEY` | `NEWSAPI_KEY` | NewsAPI provider | Use NEWSAPI_KEY format |
| `FMP_KEY` | `FMP_API_KEY` | Financial Modeling Prep | Use FMP_API_KEY format |
| `YOUTUBE_DATA_API_KEY` | `YOUTUBE_API_KEY` | YouTube provider | Use YOUTUBE_API_KEY format |
| `BRAVE_API_KEY` | `BRAVE_SEARCH_API_KEY` | Brave Search provider | Use full canonical name |
| `SERP_API_KEY` | `SERPAPI_KEY` | SerpAPI provider | Use SERPAPI_KEY format |
| `QDRANT_KEY` | `QDRANT_API_KEY` | Qdrant provider | Use QDRANT_API_KEY format |
| `MEILI_KEY` | `MEILI_MASTER_KEY` | Meilisearch provider | Use MEILI_MASTER_KEY format |
| `ARANGO_USER` | `ARANGO_USERNAME` | ArangoDB provider | Use ARANGO_USERNAME format |
| `ARANGO_PASS` | `ARANGO_PASSWORD` | ArangoDB provider | Use ARANGO_PASSWORD format |
| `ARANGO_DB` | `ARANGO_DATABASE` | ArangoDB provider | Use ARANGO_DATABASE format |

---

## 🚫 **Forbidden Synonyms (Replace Everywhere)**

### **High Priority Replacements**
| Forbidden | Canonical | Context | Action |
|-----------|-----------|---------|--------|
| `limit` | `top_k` | Vector search | Replace immediately |
| `k` | `top_k` | Vector search | Replace immediately |
| `count` | `top_k` | Vector search | Replace immediately |
| `deadline` | `deadline_ms` | Timeouts | Replace immediately |
| `timeout` | `deadline_ms` | Timeouts | Replace immediately |
| `budget` | `lane_budget_ms` | Lane budgets | Replace immediately |
| `first_byte` | `ttft_ms` | Performance | Replace immediately |

### **Medium Priority Replacements**
| Forbidden | Canonical | Context | Action |
|-----------|-----------|---------|--------|
| `temp` | `temperature` | LLM params | Replace in next phase |
| `t` | `temperature` | LLM params | Replace in next phase |
| `max_tok` | `max_tokens` | LLM params | Replace in next phase |
| `tokens` | `max_tokens` | LLM params | Replace in next phase |
| `model` | `model_id` | Model selection | Replace in next phase |
| `model_name` | `model_id` | Model selection | Replace in next phase |

### **Low Priority Replacements**
| Forbidden | Canonical | Context | Action |
|-----------|-----------|---------|--------|
| `sys_prompt` | `system_prompt` | Prompts | Replace in cleanup phase |
| `user_input` | `user_prompt` | Prompts | Replace in cleanup phase |
| `query` | `user_prompt` | Prompts | Replace in cleanup phase |
| `prompt` | `user_prompt` | Prompts | Replace in cleanup phase |

---

## 🔄 **Versioning Policy**

### **Additive Only**
- New parameters can be added
- Existing parameters cannot be removed
- Deprecations require 2-cycle grace period with alias

### **Deprecation Process**
1. **Announcement**: Add deprecation notice to parameter
2. **Alias Creation**: Create alias for deprecated parameter
3. **Grace Period**: 2 release cycles with warnings
4. **Removal**: Remove deprecated parameter after grace period

### **Alias Examples**
```yaml
# During deprecation period
limit: 10  # Deprecated, use top_k
top_k: 10  # Canonical

# After grace period
top_k: 10  # Only canonical name accepted
```

---

## 📊 **Implementation Checklist**

### **Phase 1: High Priority**
- [ ] Replace all `limit` → `top_k`
- [ ] Replace all `deadline` → `deadline_ms`
- [ ] Replace all `timeout` → `deadline_ms`
- [ ] Replace all `budget` → `lane_budget_ms`
- [ ] Replace all `first_byte` → `ttft_ms`

### **Phase 2: Medium Priority**
- [ ] Replace all `temp` → `temperature`
- [ ] Replace all `max_tok` → `max_tokens`
- [ ] Replace all `model` → `model_id`

### **Phase 3: Low Priority**
- [ ] Replace all `sys_prompt` → `system_prompt`
- [ ] Replace all `user_input` → `user_prompt`
- [ ] Replace all `query` → `user_prompt`

---

## 🎯 **Validation Rules**

### **API Validation**
- All API endpoints must use canonical names
- Request/response schemas must use canonical names
- OpenAPI specs must use canonical names

### **UI Validation**
- All form fields must use canonical names
- All URL parameters must use canonical names
- All component props must use canonical names

### **Logging Validation**
- All log messages must use canonical names
- All metrics must use canonical names
- All trace data must use canonical names

---

## 📚 **References**

- SarvanOM v2 Documentation: `02_naming_conventions.md`
- Environment Contract: `03_env_contract.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This naming map is the single source of truth and must be followed across all code, documentation, and configuration.*
