# 🚀 **SarvanOM Implementation Tasks - Complete Task List**

Based on analysis of SarvanOM documentation, here's the comprehensive implementation tasks list:

## 📋 **OVERVIEW**

**Project**: SarvanOM - Universal Knowledge Platform
**Goal**: "Google but for humans" - an always-on, zero-budget-first AI research assistant
**Status**: Phase A Complete (100%), Phase B1 In Progress (25%)

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

## 🔄 **PHASE B: Provider Order, LLM Policy, Zero-Budget Routing**

### **B1: Centralize Provider Order + Free-First Fallback**
**Priority**: 🔴 HIGH  
**Estimated Time**: 4-6 hours  
**Status**: 🚧 IN PROGRESS (25% complete)
**Owner**: TBD

#### **TODOs:**
- [x] Create `shared/llm/provider_order.py` with default order: ["ollama", "huggingface", "openai", "anthropic"]
- [ ] Remove duplicate provider ordering from `services/gateway/real_llm_integration.py`
- [ ] Update all call sites to import from single source of truth
- [ ] Implement fallback chain: if paid keys missing → proceed with local/free
- [ ] Update `.env.example` with sane defaults
- [ ] Add tests:
  - [ ] No keys → still answers
  - [ ] Some keys → best available
  - [ ] All keys → policy-based choice

**DoD**: Single provider-order source; fallback chain verified by tests; .env.example updated

---

### **B2: Best-LLM-per-Role Policy (Free + Paid)**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Implement capability-based registry with roles: {FAST, QUALITY, LONG, REASONING, TOOL}
- [ ] Map roles to providers/models via ENV (e.g., LLM_FAST=openai:gpt-4o-mini)
- [ ] Add fallback logic: if paid unavailable → HF Inference or local Ollama
- [ ] Implement latency/quality heuristics + health checks for dynamic selection
- [ ] Add metrics: provider pick rate, error rate, avg latency per role
- [ ] Make it data-driven (configurable without code changes)

**DoD**: Config-driven mapping; tests proving dynamic selection; metrics exported

---

### **B3: Always-On Multi-Lane Orchestration**
**Priority**: 🔴 HIGH  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Implement parallel lane execution for every query:
  - [ ] Web/Retrieval lane (free sources first)
  - [ ] Vector lane (Qdrant/Chroma)
  - [ ] Knowledge Graph lane (ArangoDB)
  - [ ] LLM synthesis lane (B2 policy)
- [ ] Add non-blocking orchestration with strict budgets
- [ ] Implement graceful degradation: if lane exceeds budget → return partial answer with uncertainty flags
- [ ] Add per-lane timeboxes enforcement

**DoD**: End-to-end tests confirm answers stream even if vector/KG are slow or down; logs show per-lane timeboxes enforced

---

## 🔍 **PHASE C: Zero-Budget Retrieval Aggregator + Citations/Fact-Check**

### **C1: Expand Free Sources & Unify /search**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Extend free-tier retrieval to aggregate:
  - [ ] Wikipedia, StackExchange, MDN, Python docs
  - [ ] GitHub, OpenAlex, arXiv, YouTube (if key)
  - [ ] One privacy-friendly web meta-search
- [ ] Add polite rate-limiting and domain+title similarity dedupe
- [ ] Create single `/search` endpoint merging results with {provider, url, snippet, timestamp, relevance}
- [ ] Implement result scoring and ranking

**DoD**: /search returns merged, deduped, scored list; rate-limit honored; tests cover each provider

---

### **C2: Sentence-Level Citation Alignment + Bibliography**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Implement claim→source alignment using cosine similarity on n-grams + SSD
- [ ] Add streaming citation markers: [1][2]... during response
- [ ] Render numbered bibliography with links at end
- [ ] Flag low-confidence claims with "uncertain" badge
- [ ] Add citation confidence scoring

**DoD**: UI shows inline markers; sidebar "Sources" with ranks; unit tests for alignment & uncertainty thresholds

---

## 🗄️ **PHASE D: Vector DB + Knowledge Graph (Make Them Work for Every Query)**

### **D1: Unify Vector Backends + Hot Path Performance**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Standardize VectorStore interface with adapters for Qdrant + Chroma
- [ ] Prefer Qdrant for prod, allow Chroma for dev/ephemeral
- [ ] Implement singleton client with connection pooling
- [ ] Preload collections at startup
- [ ] Add warmup job on boot (cheap queries) to avoid first-hit penalties
- [ ] Enforce P95 budgets: embed ≤ 300ms, search ≤ 300ms, fuse ≤ 300ms after warm

**DoD**: Repeat queries ≤ 1s total vector lane; health endpoint reports connections, collections, counts

---

### **D2: Meilisearch Hybrid Fusion**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 4-6 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Ensure keyword + semantic fusion: combine Meilisearch BM25 scores with vector scores
- [ ] Implement reciprocal rank fusion (RRF)
- [ ] Add toggles per query type: code/docs/QA
- [ ] Optimize fusion weights based on query type

**DoD**: Hybrid results measurably better on test corpus; regression tests added

---

### **D3: ArangoDB KG Pathfinding on Every Query**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] For each query, run shallow KG traversal (top-k entities/relations) under 1.5s cap
- [ ] Fuse KG results with retrieval/vector outputs
- [ ] Expose `/status/kg` with node/edge counts and last compaction time
- [ ] Implement KG query optimization

**DoD**: KG lane contributes context to synthesis; tests verify timeboxed traversal and fusion

---

### **D4: Data Ingestion & Status Visibility**
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

### **E1: SSE Streaming with Heartbeats + Trace IDs**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Emit `event: content_chunk` with `data: lines`
- [ ] Send `event: heartbeat` every 10s
- [ ] Propagate `X-Trace-ID` end-to-end (frontend→gateway→providers)
- [ ] Add `STREAM_MAX_SECONDS=60`
- [ ] Implement streaming error handling

**DoD**: Front-end renders tokens live; heartbeats visible in DevTools; traces correlate across logs

---

### **E2: Metrics + Logs (Prometheus/Grafana)**
**Priority**: 🟡 MEDIUM  
**Estimated Time**: 8-10 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Export counters/histograms: HTTP, lane durations, provider picks, cache hits, vector/KG timings
- [ ] Use structured JSON logs with trace IDs
- [ ] Provide basic Grafana dashboard JSON
- [ ] Add SLO monitoring

**DoD**: /metrics exposes series; dash loads; SLO panels show P95 latency and error budgets

---

### **E3: Security Hardening**
**Priority**: 🔴 HIGH  
**Estimated Time**: 6-8 hours
**Status**: 📋 TODO
**Owner**: TBD

#### **TODOs:**
- [ ] Enforce input sanitization, host allow-list, rate-limit (60 RPM/IP)
- [ ] Add security headers (CSP, HSTS, X-Frame-Options)
- [ ] Implement circuit breakers around all external calls with exponential backoff
- [ ] Add security testing suite

**DoD**: Security tests pass; headers visible; breakers trip in chaos tests without killing the request

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
**Completed**: 1 phase (A)
**In Progress**: 1 phase (B1)
**Remaining**: 21 phases

**Estimated Total Time**: 120-160 hours
**Estimated Completion**: 6-8 weeks with dedicated development

**Current Focus**: Phase B1 - Centralize Provider Order + Free-First Fallback
**Next Up**: Phase B2 - Best-LLM-per-Role Policy

---

## 🔄 **UPDATE HISTORY**


- **Date**: Current : 02 AUGUST 2025 21:04 IST
- **Action**: Created comprehensive implementation tasks list
- **Phase A**: Completed repository hygiene and baseline
- **Phase B1**: Started centralized provider order system (25% complete)
- **Status**: Ready for continued Phase B1 implementation
