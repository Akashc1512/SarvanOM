# SarvanOM — Our Solution (Full Document)

## 1) Overview

SarvanOM is a **Universal Knowledge Platform** that unifies **retrieval**, **reasoning**, and **re‑use**. It delivers **fast, cited answers** that **grow into durable knowledge**, enabling teams to move from “ask again” to “build upon.” The system is **evidence‑first**, **graph‑native**, **multi‑model**, and **zero‑budget‑first**—with enterprise‑grade observability and governance.

---

## 2) Architectural Principles

1. **Evidence‑First by Design**
   - Sentence‑source alignment; inline citation markers; bibliography with link health.
   - Bias and uncertainty surfaced alongside answers.
   - Real‑time citation insertion during streaming.

2. **Graph‑Native Knowledge**
   - Every session, upload, and answer becomes nodes/edges (concepts, sources, claims, decisions).
   - Query expansion and disambiguation powered by graph context.

3. **Multi‑Model, Free‑First Routing**
   - Provider order defaults: **Ollama → Hugging Face → OpenAI → Anthropic**.
   - Dynamic selection per task (classification, rewriting, synthesis, extraction).
   - Budgets and circuit breakers; graceful degradation to stubs in dev.

4. **Zero‑Budget‑First Retrieval**
   - Aggregates free sources (Wikipedia, StackExchange, MDN, GitHub, arXiv, OpenAlex, YouTube).
   - Rate‑limited; deduplicated; scored by credibility, novelty, and diversity.

5. **Resilience & Observability**
   - Strict timeouts per lane (vector/keyword/graph/web).
   - Prometheus metrics; structured logs with trace IDs; request replay.
   - Canary fallbacks and provider health scoring.

---

## 3) System Components

### 3.1 Retrieval Layer
- **Keyword/Hybrid Search:** Meilisearch for fast term recall and incremental indexing.
- **Vector Search:** Qdrant for semantic matching; compact embeddings with caching.
- **Knowledge Graph:** ArangoDB for entities/relations; GraphRAG for contextual expansion.
- **Upload Pipeline:** Chunk → embed → store; per‑workspace collections; PII filters.

### 3.2 Reasoning Layer
- **LLM Orchestrator:** Task classification; provider selection; prompt assembly.
- **Agent Patterns:** Retrieval agent, citation agent, reviewer agent, synthesis agent.
- **Citations Engine:** Aligns claims to sources using cosine similarity and fuzzy matching.
- **Fact‑Check Pass:** Cross‑verifies key claims and injects uncertainty markers when needed.

### 3.3 Application Layer
- **API Gateway:** FastAPI; SSE streaming; heartbeats; structured errors; auth hooks.
- **Frontend (Next.js):** Cosmic theme; streaming tokens; source cards; export to Markdown/Notion.
- **Collaboration:** Commenting, review requests, and decision records tied to sources.
- **Audit & Ops:** Metrics dashboards; error budgets; rate limiting; security headers.

---

## 4) Key Flows

### 4.1 “Research to Answer”
1. User asks a question → request gets a **trace ID**.
2. Retrieval runs **parallel lanes** (web/keyword/vector/graph) with strict budgets.
3. LLM synthesizes with **evidence alignment**; inserts citations during streaming.
4. Answer + sources display with **uncertainty badges** and **disagreement notes**.
5. Session is **captured to graph** for reuse and extension.

### 4.2 “Document to Knowledge”
1. User uploads PDFs/MD/TXT → chunked, embedded, and indexed.
2. Entities and claims extracted; **nodes/edges** created in graph.
3. Knowledge becomes available for future queries with provenance intact.

### 4.3 “Decision with Rationale”
1. Team adds commentary, counter‑evidence, and review requests.
2. Decisions are recorded with linked sources and model routes.
3. Export to Markdown/Notion/Slack with citation bundle; replayable later.

---

## 5) Performance & Reliability Targets

- **TFTT:** < 1s target with streaming.
- **Vector lane:** < 2.0s p95 (cached embeddings, async Qdrant, small models).
- **KG lane:** < 1.5s p95 (pre‑compiled traversals, bounded neighborhoods).
- **E2E:** < 3.0s p95 for typical queries.
- **Availability:** 99.9% for gateway; graceful degradation when a lane fails.

---

## 6) Security & Compliance

- Input sanitization; CSP/HSTS; rate limiting; trusted hosts.
- PII detection/redaction in upload and log pipelines.
- Per‑workspace isolation; SSO/SCIM on enterprise tier.
- Audit logs for retrieval sources, model routes, and changes to knowledge nodes.

---

## 7) Economic Model (Zero‑Budget‑First)

- **Local/Free by Default:** Ollama + HF inference; free web APIs.
- **Selective Escalation:** Paid LLM calls for high‑stakes answers; budget caps.
- **Caching Everywhere:** Embeddings, retrieval, prompt fragments, model responses.
- **Cost Control:** Per‑provider rate limiting; backpressure; adaptive concurrency.

---

## 8) Adoption Playbook

1. **Day 0:** Run locally via Docker Compose; use free routing with SSE streaming.
2. **Day 1–7:** Upload team documents; observe reuse; create first decisions with rationale.
3. **Week 2:** Integrate Slack/Jira/GitHub; enable review workflows; measure reuse ratio.
4. **Month 1:** Add SSO; expand knowledge graph; introduce enterprise policies.

---

## 9) Why We Win

- **Trust, not just speed:** Evidence‑first answers that stand up to scrutiny.
- **Knowledge that compounds:** Every interaction strengthens the graph.
- **Pragmatic orchestration:** Best model for the job, cost aware, transparent.
- **Developer‑grade ergonomics:** Clean APIs, batteries included, composable services.
- **Enterprise credibility:** Observability, security, governance from day one.

---

## 10) Roadmap Highlights

- Multimodal uploads (audio/image/video) → unified evidence layer.
- Reviewer‑in‑the‑loop workflows with role‑based controls.
- Richer GraphRAG (community detection, influence, conflict clusters).
- Private data connectors (Drive, Confluence, SharePoint) with policy control.
- Offline‑first mobile capture → later graph merge.

---

## 11) Summary

SarvanOM converts **scattered information** into **reliable, collaborative, continuously improving knowledge**. By unifying retrieval, reasoning, and reuse—grounded in **citations** and **graph context**—it delivers a step‑change in productivity and decision quality. The platform honors a **zero‑budget‑first** ethos while maintaining **MAANG‑grade** resilience, observability, and security. This is how the work of knowing becomes the work of building.