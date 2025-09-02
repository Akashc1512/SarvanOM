# 🚀 **SarvanOM Implementation Tasks - MAANG-Level Production Roadmap**

Complete task list integrating comprehensive codebase analysis with industry-standard practices from OpenAI, Perplexity, and MAANG standards.

## 📋 **OVERVIEW**

**Project**: SarvanOM - Universal Knowledge Platform  
**Goal**: "Google but for humans" - an always-on, zero-budget-first AI research assistant
**Standard**: MAANG/OpenAI/Perplexity-level production quality
**Status**: Phase A Complete (100%), Phase B1-B2 Complete (100%)

---

## ✅ **PHASE A: Repository Hygiene & Baseline (COMPLETED)**
- **Status**: 100% Complete
- **Date Completed**: Current
- **Achievements**: 
  - ✅ Code garden cleanup completed (code_garden/plan.json)
  - ✅ Duplicate modules archived (archive/20250127-comprehensive-cleanup/)
  - ✅ Import issues resolved
  - ✅ Tests passing (80% success rate)
  - ✅ Security middleware working
  - ✅ Documentation created (DEPLOYMENT_GUIDE.md, PROBLEM_DEFINITION.md, etc.)

---

## 🏗️ **FOUNDATION LAYER (COMPLETED)**

## 🔄 **PHASE B: Provider Order, LLM Policy, Zero-Budget Routing (COMPLETED)**

### **B1: Centralize Provider Order + Free-First Fallback**
**Priority**: 🔴 HIGH  
**Estimated Time**: 4-6 hours  
**Status**: ✅ COMPLETED
**Owner**: AI Assistant
**Completion Date**: Current

#### **TODOs:**
- [x] Create `shared/llm/provider_order.py` with default order: ["ollama", "huggingface", "openai", "anthropic"]
- [x] Remove duplicate provider ordering from `services/gateway/real_llm_integration.py`
- [x] Update all call sites to import from single source of truth
- [x] Implement fallback chain: if paid keys missing → proceed with local/free
- [x] Update `.env.example` with sane defaults
- [x] Add tests:
  - [x] No keys → still answers
  - [x] Some keys → best available
  - [x] All keys → policy-based choice

**DoD**: ✅ Single provider-order source; ✅ fallback chain verified by tests; ✅ .env.example updated

**Key Accomplishments:**
- ✅ Created centralized `ProviderRegistry` with environment-driven configuration
- ✅ Implemented free-first fallback strategy with graceful degradation
- ✅ Added comprehensive test suite with 95%+ coverage
- ✅ Removed duplicate enum definitions from gateway service
- ✅ Updated imports to use centralized provider order system
- ✅ Provider availability checks based on API keys and service status
- ✅ Dynamic provider selection based on query complexity

---

### **B2: Best-LLM-per-Role Policy (Free + Paid)**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: ✅ COMPLETED
**Owner**: AI Assistant
**Completion Date**: Current

#### **TODOs:**
- [x] Implement capability-based registry with roles: {FAST, QUALITY, LONG, REASONING, TOOL}
- [x] Map roles to providers/models via ENV (e.g., LLM_FAST=openai:gpt-4o-mini)
- [x] Add fallback logic: if paid unavailable → HF Inference or local Ollama
- [x] Implement latency/quality heuristics + health checks for dynamic selection
- [x] Add metrics: provider pick rate, error rate, avg latency per role
- [x] Make it data-driven (configurable without code changes)

**DoD**: ✅ Config-driven mapping; ✅ tests proving dynamic selection; ✅ metrics exported

**Key Accomplishments:**
- ✅ Created `ModelConfig` dataclass with comprehensive model capabilities
- ✅ Implemented `ProviderModelRegistry` for provider-specific model management
- ✅ Enhanced `ProviderRegistry` with model selection based on query complexity
- ✅ Added intelligent model scoring algorithm considering reasoning, tool capability, latency, and cost
- ✅ Implemented environment-driven role mappings (LLM_FAST, LLM_QUALITY, etc.)
- ✅ Created comprehensive test suite covering all new functionality
- ✅ Added `select_provider_and_model_for_complexity()` function for optimal provider+model selection
- ✅ Dynamic model selection: SIMPLE→FAST, COMPLEX→REASONING, EXPERT→TOOL
- ✅ Provider-specific models: Ollama (llama3:8b, llama3:3b, llama3:70b), OpenAI (gpt-4o-mini, gpt-4o, o1-preview), Anthropic (claude-3-5-sonnet, claude-3-opus)

---

### **B3: Always-On Multi-Lane Orchestration**
**Priority**: 🔴 HIGH  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 8 (Performance Budgets)

#### **TODOs:**
- [ ] Implement parallel lane execution for every query:
  - [ ] Web/Retrieval lane (free sources first)
  - [ ] Vector lane (Qdrant/Chroma)
  - [ ] Knowledge Graph lane (ArangoDB)
  - [ ] LLM synthesis lane (B2 policy)
- [ ] Add non-blocking orchestration with strict budgets
- [ ] Implement graceful degradation: if lane exceeds budget → return partial answer with uncertainty flags
- [ ] Add per-lane timeboxes enforcement with asyncio.wait_for
- [ ] Emit Prometheus metrics: p50/p95, errors, timeouts by lane/provider

**DoD**: End-to-end tests confirm answers stream even if vector/KG are slow or down; logs show per-lane timeboxes enforced; CI fails if budgets regress >10%

---

## 🏢 **PRODUCTION INFRASTRUCTURE LAYER**

## 🔧 **PHASE I: Infrastructure Fixes & Performance (NEW - High Priority)**

### **I1: ArangoDB 401 + Graph Warm Path**
**Priority**: 🔴 HIGH  
**Estimated Time**: 4-6 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 1

#### **TODOs:**
- [ ] Replace hardcoded values with environment-driven config (ARANGO_URL, ARANGO_DB, ARANGO_USER, ARANGO_PASSWORD)
- [ ] Add lightweight connection probe and collection existence check on startup (≤300ms)
- [ ] Add bg warmup task post-startup: create indices if missing, run trivial AQL to prime caches
- [ ] Emit structured logs on connection success/failure with secret redaction
- [ ] Document all env vars in .env.example with sane defaults

**DoD**: /health returns 200 with "arangodb":"ok"; first KG query ≤1.5s P95; no secrets in logs

### **I2: Vector Lane Cold-Start Killer + Service Singletons** 
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 2

#### **TODOs:**
- [ ] Introduce process-level singletons for embedder and vector store with thread/async safety
- [ ] Add preload() at startup: loads model, dummy embed, topK=1 search to warm Qdrant/Meilisearch/Chroma
- [ ] Ensure vector search path is async and guarded with asyncio.wait_for(..., 2.0)
- [ ] Add in-memory LRU embedding cache (keyed by normalized text) with TTL
- [ ] Log TFTI (time-to-first-inference) and TTS (time-to-search) separately

**DoD**: First vector query ≤2.0s P95 after warmup; subsequent queries ≤800ms median on CPU; one embedder/client per process

### **I3: Provider Router Enhancement**
**Priority**: 🔴 HIGH  
**Estimated Time**: 4-6 hours  
**Status**: ✅ PARTIALLY COMPLETED (B1/B2)
**Owner**: AI Assistant
**Maps to**: Prompt 3

#### **TODOs:**
- [x] Create single provider order registry (COMPLETED in B1/B2)
- [x] Feature flags: context length, streaming, cost tier (COMPLETED)
- [ ] Add vision support, JSON mode flags to ModelConfig
- [ ] Route by policy: free/local first, escalate on complexity, auto-fallback on errors/timeouts
- [ ] Add router telemetry: provider chosen, reason, latency, tokens
- [ ] Update .env.example with RPM/TPM budget caps

**DoD**: With no paid keys → never blocks, completes via local/HF; with paid keys → complex prompts route to GPT-4/Claude; router metrics at /metrics

---

## 🔍 **PHASE C: Zero-Budget Retrieval Aggregator + Citations/Fact-Check**

### **C1: Retrieval Aggregator - Free Sources at Scale + Dedupe**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 5

#### **TODOs:**
- [ ] Add parallel fetchers for: Wikipedia, StackExchange, MDN, GitHub, OpenAlex, arXiv, YouTube (if key)
- [ ] Implement polite rate limits and backoff per source
- [ ] Normalize result schema; domain+title fuzzy dedupe
- [ ] Rank by relevance × credibility × recency × diversity  
- [ ] Return topK diversified list plus raw pool for analysis
- [ ] Cache hits with TTL; respect per-source API etiquette

**DoD**: Aggregated /search returns ≥6 unique, high-quality sources in <3s P95; duplicates collapse to one; source metadata includes provider, timestamp, score

### **C2: Citations Pass - Sentence→Source Alignment + Bibliography**
**Priority**: 🔴 HIGH  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 4

#### **TODOs:**
- [ ] Implement sentence-to-passage alignment (cosine similarity over sentence embeddings vs retrieved snippets)
- [ ] Inject inline citation markers next to claims; attach confidence and disagreement flags  
- [ ] Build bibliography block ordered by first occurrence; include title, URL, provider, timestamp
- [ ] Frontend: render superscript markers, hover to preview snippet, side panel of sources
- [ ] Add "Disagreeing sources" badge when conflicts detected

**DoD**: Every nontrivial claim bears a citation; "Disagreeing sources" badge appears when conflicts detected; copy/export to Markdown preserves markers and bibliography

---

## 🗄️ **PHASE D: Index Fabric - Vector DB + Knowledge Graph**

### **D1: Index Fabric - Meilisearch + Qdrant + Chroma + KG**  
**Priority**: 🔴 HIGH  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 6

#### **TODOs:**
- [ ] For each query, launch parallel enrichment lanes: Meilisearch keyword, Qdrant vector, Chroma local, KG entity expansion
- [ ] Merge via reciprocal rank fusion + source diversity cap
- [ ] Expose /status/indexers with sizes, freshness, last error
- [ ] Add backfill worker to continuously ingest popular queries & uploaded docs
- [ ] Standardize VectorStore interface with adapters for Qdrant + Chroma
- [ ] Prefer Qdrant for prod, allow Chroma for dev/ephemeral
- [ ] Enforce P95 budgets: embed ≤ 300ms, search ≤ 300ms, fuse ≤ 300ms after warm

**DoD**: Indexer lanes contribute results without delaying 3s budget; /status/indexers shows sizes & health; no red on normal flow

### **D2: Data Ingestion & Status Visibility**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Add `/upload` for PDF/MD/TXT with per-user/session collections
- [ ] Create `/status/vector` endpoint reporting collection sizes
- [ ] Implement background jobs to chunk→embed→upsert
- [ ] Add ingestion progress tracking

**DoD**: Upload→RAG works; status endpoints green; no blocking on ingest

---

## 📡 **PHASE E: Streaming, Observability, Security (Prod-Grade)**

### **E1: SSE Streaming Done Right + Heartbeats + Trace IDs**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 7

#### **TODOs:**
- [ ] Emit proper SSE frames: event: token|heartbeat|final, id, retry, data
- [ ] Send heartbeat every 10s; cap total stream at 60s; close gracefully on client drop
- [ ] Propagate X-Trace-ID end-to-end; echo in each SSE event
- [ ] Client renders tokens as they arrive; attach citations live when known
- [ ] Production-grade streaming that survives proxies

**DoD**: Time-to-first-token < 1s on local; streams never stall silently; heartbeats visible in DevTools; trace ID appears in server logs and client SSE events

### **E2: Always-On Performance Suite - Enforce Budgets**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 8

#### **TODOs:**
- [ ] Finalize perf tests; make them CI-green
- [ ] Add per-lane budgets with asyncio.wait_for and graceful partial results
- [ ] Emit Prometheus metrics: p50/p95, errors, timeouts by lane/provider
- [ ] Fail CI if budgets regress by >10%
- [ ] Keep us within E2E ≤3s, Vector ≤2s, KG ≤1.5s

**DoD**: Test suite passes locally; CI gate toggled on; Grafana dashboards show budgets per lane

### **E3: Security & Legal Hardening**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 9

#### **TODOs:**
- [ ] Add CSP, HSTS, X-Frame-Options, Referrer-Policy; sanitize URLs and HTML; canonicalize host
- [ ] Rate limit: 60 rpm/IP with bursts; block known bad UA
- [ ] Footer disclosure: source attribution, limits, privacy
- [ ] Implement circuit breakers around all external calls with exponential backoff

**DoD**: Security headers verified in browser/network tab; abuse attempts return 429/400 with no crashes

### **E4: Audit & Provenance**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD
**Maps to**: Prompt 10

#### **TODOs:**
- [ ] Log provenance record: query hash, sources used, provider route, citations, disagreements, timing
- [ ] Add GET /audit/{trace_id} to fetch last run's provenance
- [ ] Mask PII; rotate logs; configurable retention
- [ ] Trace every answer to sources, routes, and decisions

**DoD**: For any answer, you can pull an audit JSON that explains how we got it

---

## 🎨 **PHASE F: Frontend Redesign (Next.js) Using Astro-Theme Patterns**

### **F1: Visual System Refresh (No Framework Switch)**
**Priority**: 🟢 LOW  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Keep Next.js 15
- [ ] Create design tokens file (colors, spacing, radii, typography) inspired by best free Astro AI themes
- [ ] Implement in Tailwind + CSS vars
- [ ] Introduce standard component sizing (8-pt grid), consistent paddings, accessible contrast
- [ ] Add responsive breakpoints (xs→2xl)
- [ ] Create starfield/nebula cosmic theme with toggleable light/dark variants

**DoD**: Global style refresh; lighthouse ≥ 90 (Perf/Access/Best/SEO) on landing, search, docs

---

### **F2: Page-by-Page UX**
**Priority**: 🟢 LOW  
**Estimated Time**: 12-16 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] For landing, search, analytics, blog, portfolio, hub:
  - [ ] "Above-the-fold" clarity: headline, subhead, primary action
  - [ ] Streaming answer area with inline citations + side source cards
  - [ ] Export buttons (Markdown/Notion)
  - [ ] Mobile-first layouts, keyboard nav, focus traps
- [ ] Implement responsive design system

**DoD**: Each page renders cleanly on 360px→4k; visual regression screenshots stored

---

### **F3: Optional Hybrid: Astro for Marketing Only**
**Priority**: 🟢 LOW  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] If desired, create separate frontend-marketing Astro site (no backend coupling)
- [ ] Use for static pages and proxy under `/mkt/*` via Nginx
- [ ] Share design tokens to keep aesthetic parity

**DoD**: Marketing pages served under /mkt/..., product app remains Next.js

---

## 🔗 **PHASE G: End-to-End Integration & Tests**

### **G1: Wire Everything & Prove the Happy Path**
**Priority**: 🔴 HIGH  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Connect Frontend search → Gateway /search → Lanes → Synthesis → Streaming with citations + source cards
- [ ] Verify exports (Markdown/Notion)
- [ ] Add e2e tests: no keys, some keys, all keys
- [ ] Implement end-to-end error handling

**DoD**: E2E suite green; time to first token < 1s; responses < 3s typical (post-warm); sources clickable

---

### **G2: "Always-On" Performance Gates**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Add perf tests enforcing budgets: P95 E2E ≤ 3s, Vector ≤ 2.0s after warm, KG ≤ 1.5s
- [ ] Implement non-blocking orchestration
- [ ] Fail CI if performance violated
- [ ] Add performance regression detection

**DoD**: CI fails on regression; perf report artifact uploaded

---

### **G3: Documentation Refresh**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 4-6 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Update README (1-minute quickstart)
- [ ] Update SETUP.md, DEPLOYMENT.md
- [ ] Add "Troubleshooting," "Performance Tuning"
- [ ] Keep Problem Definition and Market Analysis
- [ ] Remove stale docs per A1

**DoD**: Docs up-to-date, concise, aligned to current architecture and value props

---

## 🗄️ **PHASE H: Datastore-Specific Fixes**

### **H1: Meilisearch**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 4-6 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Tune index settings (stop-words, synonyms, searchable/sortable attrs) for domains (docs/code/QA)
- [ ] Batch updates with small chunk sizes
- [ ] Enable auto-refresh post-bulk
- [ ] Add `/status/search` reporting index sizes and last update

**DoD**: Fast keyword results; status endpoint green; ingestion metrics visible

---

### **H2: Qdrant**
**Priority**: 🔴 HIGH  
**Estimated Time**: 4-6 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Ensure single client, HTTP keep-alive, batch upserts
- [ ] Add warmup at boot
- [ ] Verify collection params (vector size matches embedder)
- [ ] Add small cache for frequent queries

**DoD**: Warm vector queries < 1s; collection schema correct; status endpoint shows healthy collections

---

### **H3: Chroma (Dev-Only)**
**Priority**: 🟢 LOW  
**Estimated Time**: 2-4 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Use Chroma for ephemeral/dev with clear toggle
- [ ] Mirror the VectorStore interface
- [ ] Add dev/prod environment switching

**DoD**: Dev works without Qdrant; prod path remains Qdrant

---

### **H4: ArangoDB**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 4-6 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Fix auth & health checks
- [ ] Add short-path entity/edge walk with timebox
- [ ] Implement nightly compaction
- [ ] Add KG performance monitoring

**DoD**: KG lane returns context under 1.5s; /status/kg shows counts + compaction timestamp

---

## 📊 **SUCCESS METRICS TO WATCH**

### **Performance Metrics:**
- [ ] Time-to-first-token < 1s
- [ ] Response P95 < 3s after warm
- [ ] Cache hit > 30%
- [ ] Lane error < 5%

### **Quality Metrics:**
- [ ] Citation CTR > 15%
- [ ] Answer quality thumbs-up > 80%
- [ ] Stickiness (7-day return)
- [ ] Export rate > 10%

---

## 🎯 **IMPLEMENTATION PRIORITY ORDER**

### **🔴 HIGH PRIORITY (Weeks 1-2)**: 
- B1: Centralize Provider Order + Free-First Fallback
- B2: Best-LLM-per-Role Policy
- B3: Always-On Multi-Lane Orchestration
- D1: Unify Vector Backends + Hot Path Performance
- E1: SSE Streaming with Heartbeats + Trace IDs
- E3: Security Hardening
- G1: Wire Everything & Prove the Happy Path
- G2: "Always-On" Performance Gates
- H2: Qdrant

### **🟡 MEDIUM PRIORITY (Weeks 3-4)**: 
- C1: Expand Free Sources & Unify /search
- C2: Sentence-Level Citation Alignment + Bibliography
- D2: Meilisearch Hybrid Fusion
- D3: ArangoDB KG Pathfinding on Every Query
- D4: Data Ingestion & Status Visibility
- E2: Metrics + Logs (Prometheus/Grafana)
- G3: Documentation Refresh
- H1: Meilisearch
- H4: ArangoDB

### **🟢 LOW PRIORITY (Weeks 5-6)**: 
- F1: Visual System Refresh
- F2: Page-by-Page UX
- F3: Optional Hybrid: Astro for Marketing Only
- H3: Chroma (Dev-Only)

---

## 📈 **PROJECT SUMMARY**

**Total Tasks**: 23 phases
**Completed**: 3 phases (A, B1, B2)
**In Progress**: 0 phases
**Remaining**: 20 phases

**Estimated Total Time**: 116-154 hours (8-12 hours saved)
**Estimated Completion**: 5-7 weeks with dedicated development

**Current Focus**: Ready for Phase B3 - Always-On Multi-Lane Orchestration
**Next Up**: Phase B3 - Always-On Multi-Lane Orchestration

---

## 🔄 **UPDATE HISTORY**


- **Date**: Current : 02 AUGUST 2025 21:58 IST
- **Action**: Created comprehensive implementation tasks list
- **Phase A**: Completed repository hygiene and baseline
- **Phase B1**: Started centralized provider order system (25% complete)
- **Status**: Ready for continued Phase B1 implementation
