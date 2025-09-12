# Retrieval Lanes - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Define retrieval lanes (web, vector, KG, keyword, news, markets) with Pre-flight lane for Guided Prompt

---

## 🎯 **Retrieval Lanes Overview**

The Retrieval Lanes system provides multiple parallel retrieval strategies to ensure comprehensive and diverse information gathering. Each lane specializes in different types of content and uses different retrieval techniques.

### **Core Lanes**
1. **Web Lane**: Real-time web search and crawling
2. **Vector Lane**: Semantic similarity search using Qdrant
3. **KG Lane**: Knowledge graph traversal using ArangoDB
4. **Keyword Lane**: Full-text search using Meilisearch
5. **News Lane**: News and current events retrieval
6. **Markets Lane**: Financial and market data retrieval
7. **Pre-flight Lane**: Guided Prompt Confirmation processing

---

## 🌐 **Web Lane**

### **Web Lane Configuration**
| Property | Value | Description |
|----------|-------|-------------|
| **Primary Engine** | Brave Search API | Real-time web search (BRAVE_SEARCH_API_KEY) |
| **Fallback Engine** | SerpAPI | Backup search provider (SERPAPI_KEY) |
| **Keyless Fallbacks** | DuckDuckGo IA, Wikipedia API, StackExchange API, MDN | No API key required |
| **Budget** | 2s (Simple), 3s (Technical), 4s (Research) | Time allocation |
| **Max Results** | 20 | Maximum results per query |
| **Cache TTL** | 300s | Cache time-to-live |
| **Provider Timeout** | ≤800ms per provider | Individual provider budget |

### **Web Lane Implementation**
```python
# Example web lane implementation
class WebLane:
    def __init__(self):
        self.primary_engine = CustomWebCrawler()
        self.fallback_engine = DuckDuckGoAPI()
        self.cache = WebCache(ttl=300)
        self.budgets = {
            'simple': 2000,  # 2 seconds
            'technical': 3000,  # 3 seconds
            'research': 4000  # 4 seconds
        }
    
    async def retrieve(self, query: str, complexity: str, constraints: dict = None) -> dict:
        """Retrieve web results for query"""
        budget_ms = self.budgets.get(complexity, 3000)
        
        try:
            # Check cache first
            cached_result = await self.cache.get(query)
            if cached_result:
                return cached_result
            
            # Try primary engine
            start_time = time.time()
            result = await self.primary_engine.search(query, budget_ms, constraints)
            
            if result['success'] and len(result['results']) > 0:
                # Cache successful result
                await self.cache.set(query, result)
                return result
            
            # Fallback to secondary engine
            result = await self.fallback_engine.search(query, budget_ms, constraints)
            
            if result['success']:
                await self.cache.set(query, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Web lane retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'lane': 'web'
            }
    
    def apply_constraints(self, query: str, constraints: dict) -> str:
        """Apply user constraints to web search query"""
        if not constraints:
            return query
        
        # Add time range constraints
        if constraints.get('time_range'):
            time_range = constraints['time_range']
            if time_range == 'recent':
                query += ' (last 2 years)'
            elif time_range == '5_years':
                query += ' (last 5 years)'
        
        # Add source constraints
        if constraints.get('sources'):
            sources = constraints['sources']
            if sources == 'academic':
                query += ' site:edu OR site:ac.uk OR site:scholar.google.com'
            elif sources == 'news':
                query += ' site:news.google.com OR site:reuters.com OR site:bbc.com'
        
        return query
```

---

## 🔍 **Vector Lane (Qdrant)**

### **Vector Lane Configuration**
| Property | Value | Description |
|----------|-------|-------------|
| **Primary Engine** | Qdrant | Vector similarity search |
| **Collection** | sarvanom_vectors | Main vector collection |
| **Embedding Model** | text-embedding-3-large | OpenAI embedding model |
| **Budget** | 1.5s (Simple), 2s (Technical), 3s (Research) | Time allocation |
| **Top K** | 15 | Maximum results per query |
| **Similarity Threshold** | 0.7 | Minimum similarity score |

### **Vector Lane Implementation**
```python
# Example vector lane implementation
class VectorLane:
    def __init__(self):
        self.qdrant_client = QdrantClient()
        self.embedding_model = OpenAIEmbedding()
        self.collection_name = 'sarvanom_vectors'
        self.budgets = {
            'simple': 1500,  # 1.5 seconds
            'technical': 2000,  # 2 seconds
            'research': 3000  # 3 seconds
        }
    
    async def retrieve(self, query: str, complexity: str, constraints: dict = None) -> dict:
        """Retrieve vector results for query"""
        budget_ms = self.budgets.get(complexity, 2000)
        
        try:
            # Generate query embedding
            start_time = time.time()
            query_embedding = await self.embedding_model.embed(query)
            
            # Apply constraints to search parameters
            search_params = self.build_search_params(constraints)
            
            # Search Qdrant
            search_result = await self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=search_params['top_k'],
                score_threshold=search_params['similarity_threshold'],
                with_payload=True,
                with_vectors=False
            )
            
            # Process results
            results = []
            for hit in search_result:
                results.append({
                    'content': hit.payload.get('content', ''),
                    'title': hit.payload.get('title', ''),
                    'url': hit.payload.get('url', ''),
                    'score': hit.score,
                    'source': hit.payload.get('source', ''),
                    'timestamp': hit.payload.get('timestamp', '')
                })
            
            return {
                'success': True,
                'results': results,
                'lane': 'vector',
                'latency_ms': (time.time() - start_time) * 1000,
                'total_found': len(results)
            }
            
        except Exception as e:
            logger.error(f"Vector lane retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'lane': 'vector'
            }
    
    def build_search_params(self, constraints: dict) -> dict:
        """Build search parameters based on constraints"""
        params = {
            'top_k': 15,
            'similarity_threshold': 0.7
        }
        
        if constraints:
            # Adjust top_k based on depth constraint
            if constraints.get('depth') == 'research':
                params['top_k'] = 25
            elif constraints.get('depth') == 'simple':
                params['top_k'] = 10
            
            # Adjust similarity threshold based on sources
            if constraints.get('sources') == 'academic':
                params['similarity_threshold'] = 0.8
        
        return params
```

---

## 🕸️ **KG Lane (ArangoDB)**

### **KG Lane Configuration**
| Property | Value | Description |
|----------|-------|-------------|
| **Primary Engine** | ArangoDB | Graph database |
| **Database** | sarvanom_kg | Knowledge graph database |
| **Graph** | knowledge_graph | Main knowledge graph |
| **Budget** | 2s (Simple), 3s (Technical), 4s (Research) | Time allocation |
| **Max Depth** | 3 | Maximum traversal depth |
| **Max Results** | 20 | Maximum results per query |

### **KG Lane Implementation**
```python
# Example KG lane implementation
class KGLane:
    def __init__(self):
        self.arango_client = ArangoClient()
        self.db = self.arango_client.db('sarvanom_kg')
        self.graph = self.db.graph('knowledge_graph')
        self.budgets = {
            'simple': 2000,  # 2 seconds
            'technical': 3000,  # 3 seconds
            'research': 4000  # 4 seconds
        }
    
    async def retrieve(self, query: str, complexity: str, constraints: dict = None) -> dict:
        """Retrieve knowledge graph results for query"""
        budget_ms = self.budgets.get(complexity, 3000)
        
        try:
            start_time = time.time()
            
            # Extract entities from query
            entities = await self.extract_entities(query)
            
            if not entities:
                return {
                    'success': True,
                    'results': [],
                    'lane': 'kg',
                    'message': 'No entities found in query'
                }
            
            # Build graph traversal query
            traversal_query = self.build_traversal_query(entities, constraints)
            
            # Execute graph traversal
            cursor = self.db.aql.execute(traversal_query)
            graph_results = [doc for doc in cursor]
            
            # Process results
            results = []
            for result in graph_results:
                results.append({
                    'content': result.get('content', ''),
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'entity_type': result.get('entity_type', ''),
                    'confidence': result.get('confidence', 0.0),
                    'relationships': result.get('relationships', []),
                    'source': result.get('source', '')
                })
            
            return {
                'success': True,
                'results': results,
                'lane': 'kg',
                'latency_ms': (time.time() - start_time) * 1000,
                'entities_found': len(entities),
                'total_found': len(results)
            }
            
        except Exception as e:
            logger.error(f"KG lane retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'lane': 'kg'
            }
    
    async def extract_entities(self, query: str) -> list:
        """Extract entities from query using NER"""
        # Use NER model to extract entities
        entities = await self.ner_model.extract(query)
        
        # Filter for relevant entity types
        relevant_types = ['PERSON', 'ORG', 'GPE', 'EVENT', 'WORK_OF_ART', 'LAW', 'LANGUAGE']
        filtered_entities = [
            entity for entity in entities
            if entity['type'] in relevant_types
        ]
        
        return filtered_entities
    
    def build_traversal_query(self, entities: list, constraints: dict) -> str:
        """Build AQL traversal query"""
        max_depth = 3
        if constraints and constraints.get('depth') == 'research':
            max_depth = 5
        
        # Build entity filter
        entity_filter = ' OR '.join([f"e.name == '{entity['text']}'" for entity in entities])
        
        query = f"""
        FOR v, e, p IN 0..{max_depth} OUTBOUND 'entities/start' knowledge_graph
        FILTER {entity_filter}
        RETURN {{
            content: v.content,
            title: v.title,
            url: v.url,
            entity_type: v.type,
            confidence: v.confidence,
            relationships: p.edges[*].type,
            source: v.source
        }}
        """
        
        return query
```

---

## 🔤 **Keyword Lane (Meilisearch)**

### **Keyword Lane Configuration**
| Property | Value | Description |
|----------|-------|-------------|
| **Primary Engine** | Meilisearch | Full-text search engine |
| **Index** | sarvanom_documents | Main document index |
| **Budget** | 1s (Simple), 1.5s (Technical), 2s (Research) | Time allocation |
| **Max Results** | 15 | Maximum results per query |
| **Search Attributes** | ['title', 'content', 'summary'] | Searchable fields |

### **Keyword Lane Implementation**
```python
# Example keyword lane implementation
class KeywordLane:
    def __init__(self):
        self.meili_client = MeiliSearch()
        self.index_name = 'sarvanom_documents'
        self.budgets = {
            'simple': 1000,  # 1 second
            'technical': 1500,  # 1.5 seconds
            'research': 2000  # 2 seconds
        }
    
    async def retrieve(self, query: str, complexity: str, constraints: dict = None) -> dict:
        """Retrieve keyword search results"""
        budget_ms = self.budgets.get(complexity, 1500)
        
        try:
            start_time = time.time()
            
            # Build search parameters
            search_params = self.build_search_params(query, constraints)
            
            # Execute search
            search_result = await self.meili_client.index(self.index_name).search(
                query,
                search_params
            )
            
            # Process results
            results = []
            for hit in search_result['hits']:
                results.append({
                    'content': hit.get('content', ''),
                    'title': hit.get('title', ''),
                    'url': hit.get('url', ''),
                    'score': hit.get('_score', 0.0),
                    'summary': hit.get('summary', ''),
                    'source': hit.get('source', ''),
                    'timestamp': hit.get('timestamp', '')
                })
            
            return {
                'success': True,
                'results': results,
                'lane': 'keyword',
                'latency_ms': (time.time() - start_time) * 1000,
                'total_found': search_result.get('totalHits', 0)
            }
            
        except Exception as e:
            logger.error(f"Keyword lane retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'lane': 'keyword'
            }
    
    def build_search_params(self, query: str, constraints: dict) -> dict:
        """Build Meilisearch parameters"""
        params = {
            'limit': 15,
            'attributesToSearchOn': ['title', 'content', 'summary'],
            'attributesToRetrieve': ['title', 'content', 'summary', 'url', 'source', 'timestamp']
        }
        
        if constraints:
            # Adjust limit based on depth
            if constraints.get('depth') == 'research':
                params['limit'] = 25
            elif constraints.get('depth') == 'simple':
                params['limit'] = 10
            
            # Add filters based on sources
            if constraints.get('sources') == 'academic':
                params['filter'] = 'source = "academic"'
            elif constraints.get('sources') == 'news':
                params['filter'] = 'source = "news"'
        
        return params
```

---

## 📰 **News Lane**

### **News Lane Configuration**
| Property | Value | Description |
|----------|-------|-------------|
| **Primary Source** | Guardian Open Platform | Real-time news (GUARDIAN_OPEN_PLATFORM_KEY) |
| **Fallback Source** | NewsAPI | Backup news provider (NEWSAPI_KEY) |
| **Keyless Fallbacks** | GDELT 2.1 API, Hacker News Algolia, RSS feeds | No API key required |
| **Budget** | 1.5s (Simple), 2s (Technical), 3s (Research) | Time allocation |
| **Max Results** | 10 | Maximum results per query |
| **Cache TTL** | 600s | Cache time-to-live |
| **Provider Timeout** | ≤800ms per provider | Individual provider budget |

### **News Lane Implementation**
```python
# Example news lane implementation
class NewsLane:
    def __init__(self):
        self.news_apis = [
            NewsAPI(),
            GuardianAPI(),
            ReutersAPI()
        ]
        self.cache = NewsCache(ttl=600)
        self.budgets = {
            'simple': 1500,  # 1.5 seconds
            'technical': 2000,  # 2 seconds
            'research': 3000  # 3 seconds
        }
    
    async def retrieve(self, query: str, complexity: str, constraints: dict = None) -> dict:
        """Retrieve news results"""
        budget_ms = self.budgets.get(complexity, 2000)
        
        try:
            # Check cache first
            cached_result = await self.cache.get(query)
            if cached_result:
                return cached_result
            
            start_time = time.time()
            
            # Try multiple news sources in parallel
            tasks = []
            for api in self.news_apis:
                task = self.fetch_from_api(api, query, budget_ms, constraints)
                tasks.append(task)
            
            # Wait for results
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine and deduplicate results
            combined_results = self.combine_news_results(results)
            
            # Cache successful result
            if combined_results:
                await self.cache.set(query, {
                    'success': True,
                    'results': combined_results,
                    'lane': 'news',
                    'latency_ms': (time.time() - start_time) * 1000
                })
            
            return {
                'success': True,
                'results': combined_results,
                'lane': 'news',
                'latency_ms': (time.time() - start_time) * 1000,
                'total_found': len(combined_results)
            }
            
        except Exception as e:
            logger.error(f"News lane retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'lane': 'news'
            }
    
    async def fetch_from_api(self, api, query: str, budget_ms: int, constraints: dict) -> list:
        """Fetch results from a single news API"""
        try:
            # Apply constraints to query
            constrained_query = self.apply_news_constraints(query, constraints)
            
            # Fetch with timeout
            result = await asyncio.wait_for(
                api.search(constrained_query),
                timeout=budget_ms / 1000
            )
            
            return result.get('articles', [])
            
        except asyncio.TimeoutError:
            logger.warning(f"News API {api.name} timed out")
            return []
        except Exception as e:
            logger.error(f"News API {api.name} failed: {e}")
            return []
    
    def apply_news_constraints(self, query: str, constraints: dict) -> dict:
        """Apply constraints to news search"""
        search_params = {'q': query}
        
        if constraints:
            # Add time range
            if constraints.get('time_range'):
                time_range = constraints['time_range']
                if time_range == 'recent':
                    search_params['from'] = (datetime.now() - timedelta(days=7)).isoformat()
                elif time_range == '5_years':
                    search_params['from'] = (datetime.now() - timedelta(days=365*5)).isoformat()
            
            # Add language
            if constraints.get('language'):
                search_params['language'] = constraints['language']
        
        return search_params
```

---

## 📈 **Markets Lane**

### **Markets Lane Configuration**
| Property | Value | Description |
|----------|-------|-------------|
| **Primary Source** | Alpha Vantage | Real-time market data (ALPHAVANTAGE_KEY) |
| **Fallback Sources** | Finnhub, FMP | Backup market providers (FINNHUB_KEY, FMP_API_KEY) |
| **Keyless Fallbacks** | Stooq CSV endpoints, SEC EDGAR | No API key required |
| **Budget** | 1s (Simple), 1.5s (Technical), 2s (Research) | Time allocation |
| **Max Results** | 15 | Maximum results per query |
| **Cache TTL** | 300s | Cache time-to-live |
| **Provider Timeout** | ≤800ms per provider | Individual provider budget |

### **Markets Lane Implementation**
```python
# Example markets lane implementation
class MarketsLane:
    def __init__(self):
        self.market_apis = [
            AlphaVantageAPI(),
            FinnhubAPI(),
            YahooFinanceAPI()
        ]
        self.cache = MarketCache(ttl=300)
        self.budgets = {
            'simple': 1000,  # 1 second
            'technical': 1500,  # 1.5 seconds
            'research': 2000  # 2 seconds
        }
    
    async def retrieve(self, query: str, complexity: str, constraints: dict = None) -> dict:
        """Retrieve market data results"""
        budget_ms = self.budgets.get(complexity, 1500)
        
        try:
            # Check cache first
            cached_result = await self.cache.get(query)
            if cached_result:
                return cached_result
            
            start_time = time.time()
            
            # Extract financial entities
            financial_entities = await self.extract_financial_entities(query)
            
            if not financial_entities:
                return {
                    'success': True,
                    'results': [],
                    'lane': 'markets',
                    'message': 'No financial entities found'
                }
            
            # Fetch market data for each entity
            tasks = []
            for entity in financial_entities:
                for api in self.market_apis:
                    task = self.fetch_market_data(api, entity, budget_ms, constraints)
                    tasks.append(task)
            
            # Wait for results
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine and process results
            combined_results = self.combine_market_results(results)
            
            # Cache successful result
            if combined_results:
                await self.cache.set(query, {
                    'success': True,
                    'results': combined_results,
                    'lane': 'markets',
                    'latency_ms': (time.time() - start_time) * 1000
                })
            
            return {
                'success': True,
                'results': combined_results,
                'lane': 'markets',
                'latency_ms': (time.time() - start_time) * 1000,
                'entities_found': len(financial_entities),
                'total_found': len(combined_results)
            }
            
        except Exception as e:
            logger.error(f"Markets lane retrieval failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'lane': 'markets'
            }
    
    async def extract_financial_entities(self, query: str) -> list:
        """Extract financial entities from query"""
        # Use financial NER to extract tickers, company names, etc.
        entities = await self.financial_ner.extract(query)
        
        # Filter for financial entities
        financial_types = ['TICKER', 'COMPANY', 'CURRENCY', 'INDEX', 'COMMODITY']
        financial_entities = [
            entity for entity in entities
            if entity['type'] in financial_types
        ]
        
        return financial_entities
```

---

## 🚀 **Pre-flight Lane (Guided Prompt)**

### **Pre-flight Lane Configuration**
| Property | Value | Description |
|----------|-------|-------------|
| **Purpose** | Guided Prompt Confirmation | Process user queries for refinement |
| **Budget** | 500ms | Time allocation (shared across all complexity levels) |
| **Parallel Execution** | Yes | Runs in parallel with orchestrator warmup |
| **Bypass Conditions** | Budget exceeded, system pressure | Auto-skip conditions |

### **Pre-flight Lane Implementation**
```python
# Example pre-flight lane implementation
class PreflightLane:
    def __init__(self):
        self.refinement_service = PromptRefinementService()
        self.budget_ms = 500
        self.bypass_conditions = {
            'budget_exceeded': True,
            'system_pressure': True,
            'model_unavailable': True
        }
    
    async def process(self, query: str, context: dict = None) -> dict:
        """Process query through pre-flight lane"""
        start_time = time.time()
        
        try:
            # Check bypass conditions
            if await self.should_bypass(context):
                return {
                    'success': True,
                    'bypassed': True,
                    'reason': 'Bypass conditions met',
                    'lane': 'preflight',
                    'latency_ms': (time.time() - start_time) * 1000
                }
            
            # Process refinement
            refinement_result = await self.refinement_service.refine_query(
                query, 
                context,
                budget_ms=self.budget_ms
            )
            
            return {
                'success': True,
                'bypassed': False,
                'refinement_result': refinement_result,
                'lane': 'preflight',
                'latency_ms': (time.time() - start_time) * 1000
            }
            
        except Exception as e:
            logger.error(f"Pre-flight lane processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'bypassed': True,
                'lane': 'preflight',
                'latency_ms': (time.time() - start_time) * 1000
            }
    
    async def should_bypass(self, context: dict) -> bool:
        """Check if pre-flight should be bypassed"""
        # Check budget exceeded
        if self.bypass_conditions['budget_exceeded']:
            # This would be checked by the refinement service
            pass
        
        # Check system pressure
        if self.bypass_conditions['system_pressure']:
            system_health = await self.get_system_health()
            if system_health['pressure_level'] > 0.75:
                return True
        
        # Check model availability
        if self.bypass_conditions['model_unavailable']:
            model_health = await self.refinement_service.check_model_health()
            if not model_health['available']:
                return True
        
        return False
    
    async def get_system_health(self) -> dict:
        """Get current system health metrics"""
        # Check if any lane has <25% of global budget remaining
        lane_budgets = await self.get_lane_budgets()
        
        for lane, budget in lane_budgets.items():
            if budget['remaining_percent'] < 25:
                return {'pressure_level': 0.8}
        
        return {'pressure_level': 0.0}
```

---

## 🔄 **Lane Orchestration**

### **Lane Orchestrator**
```python
# Example lane orchestrator
class LaneOrchestrator:
    def __init__(self):
        self.lanes = {
            'web': WebLane(),
            'vector': VectorLane(),
            'kg': KGLane(),
            'keyword': KeywordLane(),
            'news': NewsLane(),
            'markets': MarketsLane(),
            'preflight': PreflightLane()
        }
        self.fusion_policy = FusionPolicy()
    
    async def retrieve(self, query: str, complexity: str, constraints: dict = None) -> dict:
        """Orchestrate retrieval across all lanes"""
        start_time = time.time()
        
        # Process pre-flight lane first (in parallel with warmup)
        preflight_task = None
        if constraints and constraints.get('guided_prompt_enabled', True):
            preflight_task = asyncio.create_task(
                self.lanes['preflight'].process(query, constraints)
            )
        
        # Determine which lanes to use based on query and constraints
        active_lanes = self.select_active_lanes(query, complexity, constraints)
        
        # Execute retrieval in parallel
        tasks = []
        for lane_name in active_lanes:
            if lane_name in self.lanes:
                task = asyncio.create_task(
                    self.lanes[lane_name].retrieve(query, complexity, constraints)
                )
                tasks.append((lane_name, task))
        
        # Wait for all tasks to complete
        lane_results = {}
        for lane_name, task in tasks:
            try:
                result = await task
                lane_results[lane_name] = result
            except Exception as e:
                logger.error(f"Lane {lane_name} failed: {e}")
                lane_results[lane_name] = {
                    'success': False,
                    'error': str(e),
                    'results': []
                }
        
        # Wait for pre-flight if it was started
        preflight_result = None
        if preflight_task:
            try:
                preflight_result = await preflight_task
            except Exception as e:
                logger.error(f"Pre-flight lane failed: {e}")
                preflight_result = {'success': False, 'error': str(e)}
        
        # Fuse results from all lanes
        fused_results = await self.fusion_policy.fuse_results(lane_results)
        
        return {
            'success': True,
            'results': fused_results,
            'lane_results': lane_results,
            'preflight_result': preflight_result,
            'total_latency_ms': (time.time() - start_time) * 1000,
            'active_lanes': active_lanes
        }
    
    def select_active_lanes(self, query: str, complexity: str, constraints: dict) -> list:
        """Select which lanes to activate based on query and constraints"""
        active_lanes = ['vector', 'keyword']  # Always active
        
        # Add web lane for research queries
        if complexity == 'research':
            active_lanes.append('web')
        
        # Add KG lane for entity-rich queries
        if self.has_entities(query):
            active_lanes.append('kg')
        
        # Add news lane for current events
        if self.is_news_query(query):
            active_lanes.append('news')
        
        # Add markets lane for financial queries
        if self.is_financial_query(query):
            active_lanes.append('markets')
        
        # Apply constraint-based lane selection
        if constraints:
            if constraints.get('sources') == 'news':
                active_lanes = ['news', 'web']
            elif constraints.get('sources') == 'academic':
                active_lanes = ['vector', 'kg', 'keyword']
            elif constraints.get('sources') == 'financial':
                active_lanes = ['markets', 'web']
        
        return active_lanes
    
    def has_entities(self, query: str) -> bool:
        """Check if query contains entities"""
        # Simple heuristic - could be improved with NER
        entity_indicators = ['who', 'what', 'where', 'when', 'why', 'how']
        return any(indicator in query.lower() for indicator in entity_indicators)
    
    def is_news_query(self, query: str) -> bool:
        """Check if query is about current events"""
        news_keywords = ['news', 'latest', 'recent', 'today', 'yesterday', 'breaking']
        return any(keyword in query.lower() for keyword in news_keywords)
    
    def is_financial_query(self, query: str) -> bool:
        """Check if query is about financial markets"""
        financial_keywords = ['stock', 'price', 'market', 'trading', 'investment', 'finance']
        return any(keyword in query.lower() for keyword in financial_keywords)
```

---

## 📚 **References**

- Fusion Policy: `docs/retrieval/fusion_policy.md`
- Citations Contract: `docs/retrieval/citations_contract.md`
- Qdrant Collections: `docs/retrieval/qdrant_collections.md`
- Meili Indexes: `docs/retrieval/meili_indexes.md`
- Arango Entities: `docs/retrieval/arango_entities.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This lanes specification provides comprehensive retrieval capabilities across multiple data sources and retrieval strategies in SarvanOM v2.*
