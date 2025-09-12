# Retrieval & Index Fabric - Fusion Policy

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Define lanes, RRF fusion policy, and deduplication specification

---

## 🎯 **Retrieval Fabric Overview**

The Retrieval & Index Fabric implements a multi-lane retrieval system that runs in parallel and fuses results using Reciprocal Rank Fusion (RRF) with domain diversity and recency boosts. The system ensures comprehensive coverage while maintaining strict SLO budgets.

### **Core Principles**
1. **Parallel Execution**: All lanes run simultaneously within budget constraints
2. **Result Fusion**: RRF with domain diversity and recency boosts
3. **Deduplication**: Remove duplicates by domain + title + hash similarity
4. **Citation Alignment**: Sentence-to-passage alignment with inline markers
5. **Budget Compliance**: Strict adherence to lane budgets and timeouts
6. **Provider Penalties**: Rate-limit or failure penalties for provider demotion
7. **Keyless Boosts**: High-credibility keyless sources (Wikipedia, MDN) get ranking boosts

---

## 🛤️ **Retrieval Lanes**

### **Lane Configuration**
| Lane | Technology | Purpose | Budget (5s/7s/10s) | Fallback |
|------|------------|---------|-------------------|----------|
| **Web Retrieval** | Web APIs | Real-time information | 1000ms/1500ms/2000ms | Cached results |
| **Vector Search** | Qdrant | Semantic similarity | 1000ms/1500ms/2000ms | Keyword search |
| **Knowledge Graph** | ArangoDB | Entity relationships | 1000ms/1500ms/2000ms | Vector search |
| **Keyword Search** | Meilisearch | Exact keyword matching | 500ms/750ms/1000ms | Vector search |
| **News Feeds** | News APIs | Current events | 300ms/500ms/800ms | Web search |
| **Markets Feeds** | Market APIs | Financial data | 300ms/500ms/800ms | Web search |
| **Pre-flight Lane** | Guided Prompt | Query refinement | 500ms (all modes) | Skip refinement |

### **Lane Execution Strategy**
```python
# Example lane execution strategy
class LaneExecutor:
    def __init__(self):
        self.lanes = {
            "web_retrieval": WebRetrievalLane(),
            "vector_search": VectorSearchLane(),
            "knowledge_graph": KnowledgeGraphLane(),
            "keyword_search": KeywordSearchLane(),
            "news_feeds": NewsFeedsLane(),
            "markets_feeds": MarketsFeedsLane(),
            "preflight": PreflightLane()
        }
    
    async def execute_lanes(self, query: str, mode: str, budget_ms: int) -> dict:
        """Execute all lanes in parallel within budget"""
        lane_budgets = self.calculate_lane_budgets(mode, budget_ms)
        
        # Create tasks for all lanes
        tasks = []
        for lane_name, lane in self.lanes.items():
            lane_budget = lane_budgets[lane_name]
            task = asyncio.create_task(
                self.execute_lane_with_timeout(lane, query, lane_budget)
            )
            tasks.append((lane_name, task))
        
        # Wait for all tasks to complete or timeout
        results = {}
        for lane_name, task in tasks:
            try:
                result = await task
                results[lane_name] = result
            except asyncio.TimeoutError:
                results[lane_name] = {
                    "status": "timeout",
                    "error": f"Lane {lane_name} exceeded budget",
                    "partial_results": []
                }
            except Exception as e:
                results[lane_name] = {
                    "status": "error",
                    "error": str(e),
                    "partial_results": []
                }
        
        return results
    
    def calculate_lane_budgets(self, mode: str, total_budget_ms: int) -> dict:
        """Calculate individual lane budgets based on mode"""
        budget_allocations = {
            "simple": {
                "web_retrieval": 1000,
                "vector_search": 1000,
                "knowledge_graph": 1000,
                "keyword_search": 500,
                "news_feeds": 300,
                "markets_feeds": 300
            },
            "technical": {
                "web_retrieval": 1500,
                "vector_search": 1500,
                "knowledge_graph": 1500,
                "keyword_search": 750,
                "news_feeds": 500,
                "markets_feeds": 500
            },
            "research": {
                "web_retrieval": 2000,
                "vector_search": 2000,
                "knowledge_graph": 2000,
                "keyword_search": 1000,
                "news_feeds": 800,
                "markets_feeds": 800
            },
            "multimedia": {
                "web_retrieval": 2000,
                "vector_search": 2000,
                "knowledge_graph": 2000,
                "keyword_search": 1000,
                "news_feeds": 800,
                "markets_feeds": 800
            }
        }
        
        return budget_allocations.get(mode, budget_allocations["simple"])
```

---

## 🎯 **Constraint Binding**

### **User Constraint Integration**
The retrieval system integrates user-selected constraints from the Guided Prompt Confirmation step into the retrieval request schema:

```python
# Example constraint binding implementation
class ConstraintBinder:
    def __init__(self):
        self.constraint_mappings = {
            'time_range': self.apply_time_constraints,
            'sources': self.apply_source_constraints,
            'cost': self.apply_cost_constraints,
            'depth': self.apply_depth_constraints,
            'citations_required': self.apply_citation_constraints
        }
    
    def bind_constraints(self, query: str, constraints: dict) -> dict:
        """Bind user constraints to retrieval request"""
        if not constraints:
            return {'original_query': query, 'constraints': {}}
        
        bound_request = {
            'original_query': query,
            'constraints': constraints,
            'modified_queries': {},
            'lane_parameters': {}
        }
        
        # Apply each constraint type
        for constraint_type, constraint_value in constraints.items():
            if constraint_type in self.constraint_mappings:
                constraint_result = self.constraint_mappings[constraint_type](
                    query, constraint_value
                )
                bound_request['modified_queries'][constraint_type] = constraint_result['query']
                bound_request['lane_parameters'][constraint_type] = constraint_result['parameters']
        
        return bound_request
    
    def apply_time_constraints(self, query: str, time_range: str) -> dict:
        """Apply time range constraints to query"""
        time_modifiers = {
            'recent': ' (last 2 years)',
            '5_years': ' (last 5 years)',
            'all_time': ''
        }
        
        modified_query = query + time_modifiers.get(time_range, '')
        
        return {
            'query': modified_query,
            'parameters': {
                'time_filter': time_range,
                'date_from': self.get_date_from(time_range),
                'date_to': datetime.now().isoformat()
            }
        }
    
    def apply_source_constraints(self, query: str, sources: str) -> dict:
        """Apply source constraints to query"""
        source_modifiers = {
            'academic': ' site:edu OR site:ac.uk OR site:scholar.google.com',
            'news': ' site:news.google.com OR site:reuters.com OR site:bbc.com',
            'both': ''
        }
        
        modified_query = query + source_modifiers.get(sources, '')
        
        return {
            'query': modified_query,
            'parameters': {
                'source_filter': sources,
                'preferred_domains': self.get_preferred_domains(sources)
            }
        }
    
    def apply_cost_constraints(self, query: str, cost_ceiling: str) -> dict:
        """Apply cost constraints to retrieval"""
        cost_limits = {
            'low': {'max_tokens': 1000, 'max_results': 10},
            'medium': {'max_tokens': 2000, 'max_results': 20},
            'high': {'max_tokens': 5000, 'max_results': 50}
        }
        
        return {
            'query': query,
            'parameters': {
                'cost_ceiling': cost_ceiling,
                'token_limits': cost_limits.get(cost_ceiling, cost_limits['medium']),
                'budget_multiplier': self.get_budget_multiplier(cost_ceiling)
            }
        }
    
    def apply_depth_constraints(self, query: str, depth: str) -> dict:
        """Apply depth constraints to retrieval"""
        depth_parameters = {
            'simple': {'max_results': 10, 'search_depth': 1, 'complexity': 'simple'},
            'technical': {'max_results': 20, 'search_depth': 2, 'complexity': 'technical'},
            'research': {'max_results': 50, 'search_depth': 3, 'complexity': 'research'}
        }
        
        return {
            'query': query,
            'parameters': {
                'depth': depth,
                'search_parameters': depth_parameters.get(depth, depth_parameters['technical']),
                'complexity': depth_parameters.get(depth, depth_parameters['technical'])['complexity']
            }
        }
    
    def apply_citation_constraints(self, query: str, citations_required: bool) -> dict:
        """Apply citation requirements to retrieval"""
        if citations_required:
            modified_query = query + ' with citations and sources'
        else:
            modified_query = query
        
        return {
            'query': modified_query,
            'parameters': {
                'citations_required': citations_required,
                'citation_format': 'inline' if citations_required else 'none',
                'source_verification': citations_required
            }
        }
    
    def get_date_from(self, time_range: str) -> str:
        """Get start date for time range"""
        now = datetime.now()
        if time_range == 'recent':
            return (now - timedelta(days=365*2)).isoformat()
        elif time_range == '5_years':
            return (now - timedelta(days=365*5)).isoformat()
        else:
            return (now - timedelta(days=365*10)).isoformat()  # 10 years default
    
    def get_preferred_domains(self, sources: str) -> list:
        """Get preferred domains for source constraint"""
        domain_mappings = {
            'academic': ['edu', 'ac.uk', 'scholar.google.com', 'arxiv.org', 'pubmed.ncbi.nlm.nih.gov'],
            'news': ['news.google.com', 'reuters.com', 'bbc.com', 'cnn.com', 'nytimes.com'],
            'both': []
        }
        return domain_mappings.get(sources, [])
    
    def get_budget_multiplier(self, cost_ceiling: str) -> float:
        """Get budget multiplier for cost constraint"""
        multipliers = {
            'low': 0.5,
            'medium': 1.0,
            'high': 2.0
        }
        return multipliers.get(cost_ceiling, 1.0)
```

### **Pre-flight Lane Integration**
The Pre-flight lane runs in parallel with orchestrator warmup and must not block main execution beyond the pre-flight budget:

```python
# Example pre-flight lane integration
class PreflightLaneIntegration:
    def __init__(self):
        self.preflight_budget_ms = 500
        self.bypass_conditions = {
            'budget_exceeded': True,
            'system_pressure': True,
            'model_unavailable': True
        }
    
    async def process_preflight(self, query: str, constraints: dict) -> dict:
        """Process query through pre-flight lane"""
        start_time = time.time()
        
        # Check if pre-flight should be bypassed
        if await self.should_bypass_preflight():
            return {
                'bypassed': True,
                'reason': 'Bypass conditions met',
                'latency_ms': (time.time() - start_time) * 1000
            }
        
        # Process refinement within budget
        try:
            refinement_result = await asyncio.wait_for(
                self.refinement_service.refine_query(query, constraints),
                timeout=self.preflight_budget_ms / 1000
            )
            
            return {
                'bypassed': False,
                'refinement_result': refinement_result,
                'latency_ms': (time.time() - start_time) * 1000
            }
            
        except asyncio.TimeoutError:
            return {
                'bypassed': True,
                'reason': 'Pre-flight budget exceeded',
                'latency_ms': (time.time() - start_time) * 1000
            }
    
    async def should_bypass_preflight(self) -> bool:
        """Check if pre-flight should be bypassed"""
        # Check system pressure
        system_health = await self.get_system_health()
        if system_health['pressure_level'] > 0.75:
            return True
        
        # Check if any lane has <25% of global budget remaining
        lane_budgets = await self.get_lane_budgets()
        for lane, budget in lane_budgets.items():
            if budget['remaining_percent'] < 25:
                return True
        
        return False
```

---

## 🔄 **Reciprocal Rank Fusion (RRF)**

### **RRF Algorithm**
RRF combines results from multiple retrieval systems by assigning scores based on reciprocal ranks:

```
RRF_score = Σ(1 / (k + rank_i))
```

Where:
- `k` = constant (typically 60)
- `rank_i` = rank of document in lane i

### **RRF Implementation**
```python
# Example RRF implementation
class ReciprocalRankFusion:
    def __init__(self, k: int = 60):
        self.k = k
        self.domain_boost = 0.1
        self.recency_boost = 0.05
    
    def fuse_results(self, lane_results: dict) -> list:
        """Fuse results from multiple lanes using RRF"""
        # Collect all documents with their ranks
        document_scores = {}
        
        for lane_name, results in lane_results.items():
            if results["status"] == "success" and results["documents"]:
                for rank, doc in enumerate(results["documents"], 1):
                    doc_id = doc["id"]
                    
                    # Calculate RRF score
                    rrf_score = 1 / (self.k + rank)
                    
                    # Apply domain diversity boost
                    domain_boost = self.calculate_domain_boost(doc, document_scores)
                    
                    # Apply recency boost
                    recency_boost = self.calculate_recency_boost(doc)
                    
                    # Total score
                    total_score = rrf_score + domain_boost + recency_boost
                    
                    if doc_id in document_scores:
                        document_scores[doc_id]["score"] += total_score
                        document_scores[doc_id]["lanes"].append(lane_name)
                    else:
                        document_scores[doc_id] = {
                            "document": doc,
                            "score": total_score,
                            "lanes": [lane_name]
                        }
        
        # Sort by score and return top results
        sorted_docs = sorted(
            document_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        return [doc["document"] for doc in sorted_docs]
    
    def calculate_domain_boost(self, doc: dict, existing_docs: dict) -> float:
        """Calculate domain diversity boost"""
        domain = doc.get("domain", "")
        
        # Count existing documents from same domain
        domain_count = sum(
            1 for existing_doc in existing_docs.values()
            if existing_doc["document"].get("domain") == domain
        )
        
        # Boost decreases with domain frequency
        if domain_count == 0:
            return self.domain_boost
        else:
            return self.domain_boost / (domain_count + 1)
    
    def calculate_recency_boost(self, doc: dict) -> float:
        """Calculate recency boost"""
        published_at = doc.get("published_at")
        if not published_at:
            return 0.0
        
        # Calculate age in days
        age_days = (time.time() - published_at) / (24 * 3600)
        
        # Boost decreases with age
        if age_days <= 1:
            return self.recency_boost
        elif age_days <= 7:
            return self.recency_boost * 0.5
        elif age_days <= 30:
            return self.recency_boost * 0.2
        else:
            return 0.0
```

---

## 🔍 **Deduplication Strategy**

### **Deduplication Criteria**
| Criterion | Weight | Description | Threshold |
|-----------|--------|-------------|-----------|
| **Domain + Title** | 70% | Same domain and similar title | 0.8 similarity |
| **Content Hash** | 20% | Identical content hash | Exact match |
| **URL Similarity** | 10% | Similar URL structure | 0.9 similarity |

### **Deduplication Implementation**
```python
# Example deduplication implementation
class Deduplicator:
    def __init__(self):
        self.title_similarity_threshold = 0.8
        self.url_similarity_threshold = 0.9
        self.content_hash_threshold = 1.0
    
    def deduplicate(self, documents: list) -> list:
        """Remove duplicate documents"""
        unique_docs = []
        seen_hashes = set()
        seen_domain_titles = set()
        
        for doc in documents:
            # Check content hash
            content_hash = self.calculate_content_hash(doc)
            if content_hash in seen_hashes:
                continue
            
            # Check domain + title similarity
            domain_title_key = self.create_domain_title_key(doc)
            if self.is_similar_to_existing(domain_title_key, seen_domain_titles):
                continue
            
            # Document is unique
            unique_docs.append(doc)
            seen_hashes.add(content_hash)
            seen_domain_titles.add(domain_title_key)
        
        return unique_docs
    
    def calculate_content_hash(self, doc: dict) -> str:
        """Calculate content hash for deduplication"""
        content = doc.get("content", "")
        return hashlib.md5(content.encode()).hexdigest()
    
    def create_domain_title_key(self, doc: dict) -> tuple:
        """Create domain + title key for similarity checking"""
        domain = doc.get("domain", "")
        title = doc.get("title", "")
        return (domain, title.lower().strip())
    
    def is_similar_to_existing(self, domain_title_key: tuple, existing_keys: set) -> bool:
        """Check if domain + title is similar to existing"""
        domain, title = domain_title_key
        
        for existing_domain, existing_title in existing_keys:
            if domain == existing_domain:
                # Calculate title similarity
                similarity = self.calculate_title_similarity(title, existing_title)
                if similarity >= self.title_similarity_threshold:
                    return True
        
        return False
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity using Jaccard similarity"""
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union
```

---

## 📊 **Result Ranking & Scoring**

### **Ranking Factors**
| Factor | Weight | Description | Calculation |
|--------|--------|-------------|-------------|
| **RRF Score** | 50% | Reciprocal rank fusion score | 1/(k+rank) |
| **Domain Diversity** | 20% | Domain diversity boost | 0.1/(domain_count+1) |
| **Recency** | 15% | Document recency boost | Age-based decay |
| **Source Authority** | 10% | Source authority score | Predefined authority scores |
| **Content Quality** | 5% | Content quality score | Readability + completeness |

### **Ranking Implementation**
```python
# Example ranking implementation
class ResultRanker:
    def __init__(self):
        self.ranking_weights = {
            "rrf_score": 0.5,
            "domain_diversity": 0.2,
            "recency": 0.15,
            "source_authority": 0.1,
            "content_quality": 0.05
        }
        self.authority_scores = self.load_authority_scores()
    
    def rank_results(self, documents: list, lane_results: dict) -> list:
        """Rank documents based on multiple factors"""
        ranked_docs = []
        
        for doc in documents:
            # Calculate individual scores
            rrf_score = self.calculate_rrf_score(doc, lane_results)
            domain_diversity_score = self.calculate_domain_diversity_score(doc, documents)
            recency_score = self.calculate_recency_score(doc)
            authority_score = self.calculate_authority_score(doc)
            quality_score = self.calculate_quality_score(doc)
            
            # Calculate weighted total score
            total_score = (
                rrf_score * self.ranking_weights["rrf_score"] +
                domain_diversity_score * self.ranking_weights["domain_diversity"] +
                recency_score * self.ranking_weights["recency"] +
                authority_score * self.ranking_weights["source_authority"] +
                quality_score * self.ranking_weights["content_quality"]
            )
            
            ranked_docs.append({
                "document": doc,
                "total_score": total_score,
                "component_scores": {
                    "rrf_score": rrf_score,
                    "domain_diversity": domain_diversity_score,
                    "recency": recency_score,
                    "authority": authority_score,
                    "quality": quality_score
                }
            })
        
        # Sort by total score
        ranked_docs.sort(key=lambda x: x["total_score"], reverse=True)
        
        return [doc["document"] for doc in ranked_docs]
    
    def calculate_rrf_score(self, doc: dict, lane_results: dict) -> float:
        """Calculate RRF score for document"""
        total_score = 0.0
        k = 60
        
        for lane_name, results in lane_results.items():
            if results["status"] == "success" and results["documents"]:
                for rank, lane_doc in enumerate(results["documents"], 1):
                    if lane_doc["id"] == doc["id"]:
                        total_score += 1 / (k + rank)
                        break
        
        return total_score
    
    def calculate_domain_diversity_score(self, doc: dict, all_docs: list) -> float:
        """Calculate domain diversity score"""
        domain = doc.get("domain", "")
        domain_count = sum(1 for d in all_docs if d.get("domain") == domain)
        
        if domain_count == 1:
            return 1.0
        else:
            return 1.0 / domain_count
    
    def calculate_recency_score(self, doc: dict) -> float:
        """Calculate recency score"""
        published_at = doc.get("published_at")
        if not published_at:
            return 0.5  # Default score for unknown dates
        
        age_days = (time.time() - published_at) / (24 * 3600)
        
        if age_days <= 1:
            return 1.0
        elif age_days <= 7:
            return 0.8
        elif age_days <= 30:
            return 0.6
        elif age_days <= 365:
            return 0.4
        else:
            return 0.2
    
    def calculate_authority_score(self, doc: dict) -> float:
        """Calculate source authority score"""
        domain = doc.get("domain", "")
        return self.authority_scores.get(domain, 0.5)
    
    def calculate_quality_score(self, doc: dict) -> float:
        """Calculate content quality score"""
        content = doc.get("content", "")
        
        # Calculate readability score
        readability_score = self.calculate_readability(content)
        
        # Calculate completeness score
        completeness_score = self.calculate_completeness(content)
        
        return (readability_score + completeness_score) / 2
    
    def load_authority_scores(self) -> dict:
        """Load predefined authority scores for domains"""
        return {
            "wikipedia.org": 0.9,
            "arxiv.org": 0.9,
            "pubmed.ncbi.nlm.nih.gov": 0.9,
            "github.com": 0.8,
            "stackoverflow.com": 0.8,
            "medium.com": 0.6,
            "blogspot.com": 0.5,
            "wordpress.com": 0.5
        }
```

---

## 📝 **Citation Alignment**

### **Citation Strategy**
1. **Sentence-to-Passage Mapping**: Map each sentence to source passages
2. **Inline Markers**: Add [1], [2] markers to sentences
3. **Bibliography Generation**: Create comprehensive bibliography
4. **Disagreement Detection**: Flag conflicting information

### **Citation Implementation**
```python
# Example citation implementation
class CitationAligner:
    def __init__(self):
        self.similarity_threshold = 0.7
        self.max_citations_per_sentence = 3
    
    def align_citations(self, response_text: str, source_documents: list) -> dict:
        """Align citations with response text"""
        sentences = self.split_into_sentences(response_text)
        aligned_citations = []
        
        for sentence in sentences:
            # Find best matching passages
            matching_passages = self.find_matching_passages(sentence, source_documents)
            
            if matching_passages:
                # Create citation markers
                citation_markers = self.create_citation_markers(matching_passages)
                aligned_citations.append({
                    "sentence": sentence,
                    "citations": citation_markers,
                    "confidence": max(p["similarity"] for p in matching_passages)
                })
            else:
                aligned_citations.append({
                    "sentence": sentence,
                    "citations": [],
                    "confidence": 0.0
                })
        
        # Generate bibliography
        bibliography = self.generate_bibliography(source_documents)
        
        # Detect disagreements
        disagreements = self.detect_disagreements(aligned_citations)
        
        return {
            "aligned_citations": aligned_citations,
            "bibliography": bibliography,
            "disagreements": disagreements,
            "total_citations": len(bibliography)
        }
    
    def find_matching_passages(self, sentence: str, source_documents: list) -> list:
        """Find passages that match the sentence"""
        matching_passages = []
        
        for doc in source_documents:
            content = doc.get("content", "")
            passages = self.split_into_passages(content)
            
            for passage in passages:
                similarity = self.calculate_similarity(sentence, passage)
                if similarity >= self.similarity_threshold:
                    matching_passages.append({
                        "document": doc,
                        "passage": passage,
                        "similarity": similarity
                    })
        
        # Sort by similarity and return top matches
        matching_passages.sort(key=lambda x: x["similarity"], reverse=True)
        return matching_passages[:self.max_citations_per_sentence]
    
    def create_citation_markers(self, matching_passages: list) -> list:
        """Create citation markers for passages"""
        citations = []
        
        for i, passage in enumerate(matching_passages, 1):
            citations.append({
                "marker": f"[{i}]",
                "document": passage["document"],
                "passage": passage["passage"],
                "similarity": passage["similarity"]
            })
        
        return citations
    
    def generate_bibliography(self, source_documents: list) -> list:
        """Generate bibliography from source documents"""
        bibliography = []
        
        for i, doc in enumerate(source_documents, 1):
            bibliography.append({
                "id": i,
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "domain": doc.get("domain", ""),
                "published_at": doc.get("published_at", ""),
                "author": doc.get("author", ""),
                "excerpt": doc.get("excerpt", "")
            })
        
        return bibliography
    
    def detect_disagreements(self, aligned_citations: list) -> list:
        """Detect disagreements between sources"""
        disagreements = []
        
        # Group sentences by topic
        topic_groups = self.group_sentences_by_topic(aligned_citations)
        
        for topic, sentences in topic_groups.items():
            if len(sentences) > 1:
                # Check for conflicting information
                conflicts = self.find_conflicts(sentences)
                if conflicts:
                    disagreements.append({
                        "topic": topic,
                        "conflicts": conflicts,
                        "severity": self.calculate_conflict_severity(conflicts)
                    })
        
        return disagreements
```

---

## 📊 **Performance Monitoring**

### **Retrieval Metrics**
| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| **Lane Success Rate** | % of lanes completing successfully | > 95% | < 90% |
| **Fusion Quality** | Quality of fused results | > 0.8 | < 0.7 |
| **Deduplication Rate** | % of duplicates removed | > 20% | < 10% |
| **Citation Accuracy** | % of accurate citations | > 90% | < 80% |
| **Response Time** | Total retrieval time | < 2s | > 3s |

### **Monitoring Implementation**
```python
# Example monitoring implementation
class RetrievalMonitor:
    def __init__(self):
        self.metrics = {
            "lane_success_rate": 0.0,
            "fusion_quality": 0.0,
            "deduplication_rate": 0.0,
            "citation_accuracy": 0.0,
            "response_time": 0.0
        }
    
    def record_retrieval_metrics(self, lane_results: dict, fused_results: list, response_time: float):
        """Record retrieval performance metrics"""
        # Calculate lane success rate
        successful_lanes = sum(1 for result in lane_results.values() if result["status"] == "success")
        total_lanes = len(lane_results)
        self.metrics["lane_success_rate"] = successful_lanes / total_lanes
        
        # Calculate fusion quality
        self.metrics["fusion_quality"] = self.calculate_fusion_quality(fused_results)
        
        # Calculate deduplication rate
        self.metrics["deduplication_rate"] = self.calculate_deduplication_rate(lane_results, fused_results)
        
        # Record response time
        self.metrics["response_time"] = response_time
    
    def calculate_fusion_quality(self, fused_results: list) -> float:
        """Calculate quality of fused results"""
        if not fused_results:
            return 0.0
        
        # Calculate average relevance score
        total_score = sum(doc.get("relevance_score", 0.5) for doc in fused_results)
        return total_score / len(fused_results)
    
    def calculate_deduplication_rate(self, lane_results: dict, fused_results: list) -> float:
        """Calculate deduplication rate"""
        total_documents = sum(
            len(result.get("documents", []))
            for result in lane_results.values()
            if result["status"] == "success"
        )
        
        if total_documents == 0:
            return 0.0
        
        unique_documents = len(fused_results)
        duplicates_removed = total_documents - unique_documents
        
        return duplicates_removed / total_documents
```

---

## 📚 **References**

- Retrieval & Index Fabric: `06_retrieval_and_index_fabric.md`
- Data Platform: `07_data_platform_qdrant_arango_meili.md`
- System Context: `docs/architecture/system_context.md`
- Budgets: `docs/architecture/budgets.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This fusion policy ensures comprehensive and high-quality retrieval results while maintaining strict performance budgets in SarvanOM v2.*
