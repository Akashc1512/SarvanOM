from __future__ import annotations

import time
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from shared.core.config import get_central_config
from shared.core.logging import get_logger
from shared.core.cache import get_cache_manager
from shared.embeddings.local_embedder import embed_texts
from shared.vectorstores.vector_store_service import (
    ChromaVectorStore,
    QdrantVectorStore,
    InMemoryVectorStore,
    VectorDocument,
)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from shared.contracts.query import (
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    RetrievalIndexRequest,
    RetrievalIndexResponse,
)

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

config = get_central_config()

app = FastAPI(
    title=f"{config.service_name}-retrieval",
    version=config.app_version,
    description="Retrieval microservice with real vector search",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=bool(config.cors_credentials),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict:
    return {
        "service": "retrieval",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }

_service_start = time.time()
REQUEST_COUNTER = Counter("retrieval_requests_total", "Total retrieval requests")
REQUEST_LATENCY = Histogram("retrieval_request_latency_seconds", "Retrieval request latency")

def _init_vector_store():
    cfg = get_central_config()
    provider = getattr(cfg, "vector_db_provider", "chroma").lower()
    if provider == "qdrant":
        return QdrantVectorStore(
            url=str(cfg.qdrant_url),
            api_key=(cfg.qdrant_api_key.get_secret_value() if cfg.qdrant_api_key else None),
            collection=str(cfg.qdrant_collection),
            vector_size=int(getattr(cfg, "embedding_dimension", 384)),
        )
    elif provider == "inmemory" or provider == "memory":
        return InMemoryVectorStore()
    # default to chroma (local/in-process)
    return ChromaVectorStore(collection_name="knowledge")

VECTOR_STORE = _init_vector_store()

@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root() -> dict:
    return {
        "service": "retrieval",
        "version": config.app_version,
        "status": "ok",
    }

@app.post("/search", response_model=RetrievalSearchResponse)
async def search(payload: RetrievalSearchRequest) -> RetrievalSearchResponse:
    REQUEST_COUNTER.inc()
    
    with REQUEST_LATENCY.time():
        try:
            # Get cache
            cache = get_cache_manager()
            
            # Create cache key
            cache_key = f"search:{hash(payload.query)}:{payload.max_results}"
            
            # Check cache first
            cached_result = await cache.get(cache_key)
            if cached_result:
                logger.info("Cache hit for search", query=payload.query[:100])
                return RetrievalSearchResponse(**cached_result)
            
            # Generate embeddings for query
            query_embedding = embed_texts([payload.query])
            
            # Perform vector search
            search_results = await VECTOR_STORE.search(
                query_embedding=query_embedding[0],
                top_k=payload.max_results
            )
            
            # Format results
            sources = []
            relevance_scores = []
            
            for result in search_results:
                if isinstance(result, tuple):
                    doc, score = result
                    sources.append({
                        "id": doc.id,
                        "content": doc.text,
                        "metadata": doc.metadata,
                        "score": score
                    })
                    relevance_scores.append(score)
                else:
                    # Handle dict format
                    sources.append(result)
                    relevance_scores.append(result.get("score", 0.0))
            
            # Create response
            response = RetrievalSearchResponse(
                sources=sources,
                method="vector_search",
                total_results=len(sources),
                relevance_scores=relevance_scores,
                limit=payload.max_results
            )
            
            # Cache result for 1 hour
            await cache.set(cache_key, response.dict())
            
            logger.info("Search completed", 
                       query=payload.query[:100], 
                       results_count=len(sources))
            
            return response
            
        except Exception as e:
            logger.error("Search failed", error=str(e), query=payload.query[:100])
            # Fallback to empty results
            return RetrievalSearchResponse(
                sources=[],
                method="stub_search_fallback",
                total_results=0,
                relevance_scores=[],
                limit=payload.max_results
            )

@app.post("/index", response_model=RetrievalIndexResponse)
async def index(payload: RetrievalIndexRequest) -> RetrievalIndexResponse:
    try:
        # Validate input
        payload.validate_lengths()
        
        # Generate embeddings
        embeddings = embed_texts(payload.texts)
        
        # Create vector documents
        documents = []
        for i, (doc_id, text, embedding) in enumerate(zip(payload.ids, payload.texts, embeddings)):
            metadata = payload.metadatas[i] if i < len(payload.metadatas) else {}
            documents.append(VectorDocument(
                id=doc_id,
                text=text,
                embedding=embedding,
                metadata=metadata
            ))
        
        # Index documents
        upserted_count = await VECTOR_STORE.upsert(documents)
        
        logger.info("Indexing completed", 
                   documents_count=len(documents),
                   upserted_count=upserted_count)
        
        return RetrievalIndexResponse(upserted=upserted_count)
        
    except Exception as e:
        logger.error("Indexing failed", error=str(e))
        return RetrievalIndexResponse(upserted=0)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.retrieval.main:app", host="0.0.0.0", port=8001, reload=True)
