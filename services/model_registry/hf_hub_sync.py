"""
Hugging Face Hub Sync - SarvanOM v2

Free-tier friendly Hugging Face model discovery and synchronization.
Discovers open-source models from HF Hub for auto-upgrade workflow.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

import httpx
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
hf_hub_sync_total = Counter('sarvanom_hf_hub_sync_total', 'Total HF Hub sync operations', ['status'])
hf_models_discovered = Counter('sarvanom_hf_models_discovered_total', 'Total HF models discovered', ['license', 'pipeline_tag'])
hf_sync_duration = Histogram('sarvanom_hf_sync_duration_seconds', 'HF Hub sync duration', ['operation'])
hf_candidates_found = Gauge('sarvanom_hf_candidates_found', 'Number of HF model candidates found')

class ModelStatus(str, Enum):
    CANDIDATE = "candidate"
    EVALUATING = "evaluating"
    STABLE = "stable"
    DEPRECATED = "deprecated"

@dataclass
class HFModelCandidate:
    """Hugging Face model candidate for auto-upgrade"""
    model_id: str
    model_name: str
    pipeline_tag: str
    license: str
    library_name: str
    quantized: bool
    safetensors: bool
    downloads: int
    likes: int
    last_modified: str
    tags: List[str]
    status: str = ModelStatus.CANDIDATE
    discovered_at: float = None
    evaluation_score: float = 0.0
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = time.time()

class HFHubSync:
    """Hugging Face Hub synchronization for free-tier model discovery"""
    
    def __init__(self, registry=None):
        self.registry = registry
        self.hf_api_base = "https://huggingface.co/api"
        self.sync_interval = 7 * 24 * 3600  # Weekly sync
        self.last_sync = 0
        self.candidates_cache = {}
        
        # Free-tier friendly filters
        self.license_filters = ["openrail", "apache-2.0", "mit", "bsd-3-clause", "bsd-2-clause"]
        self.pipeline_tags = ["text-generation", "text-embeddings", "text2text-generation"]
        self.required_library = "transformers"
        self.min_downloads = 1000  # Minimum downloads for consideration
        self.min_likes = 10  # Minimum likes for consideration
    
    async def sync_hf_models(self) -> List[HFModelCandidate]:
        """Sync models from Hugging Face Hub"""
        logger.info("Starting HF Hub model synchronization")
        start_time = time.time()
        
        try:
            # Discover text generation models
            text_gen_models = await self._discover_models_by_pipeline("text-generation")
            
            # Discover text embedding models
            embedding_models = await self._discover_models_by_pipeline("text-embeddings")
            
            # Discover text2text generation models
            text2text_models = await self._discover_models_by_pipeline("text2text-generation")
            
            # Combine and filter candidates
            all_candidates = text_gen_models + embedding_models + text2text_models
            filtered_candidates = self._filter_candidates(all_candidates)
            
            # Update metrics
            hf_candidates_found.set(len(filtered_candidates))
            hf_models_discovered.labels(license="all", pipeline_tag="all").inc(len(filtered_candidates))
            
            # Cache candidates
            self.candidates_cache = {c.model_id: c for c in filtered_candidates}
            
            # Update registry if available
            if self.registry:
                await self._update_registry_candidates(filtered_candidates)
            
            # Update sync timestamp
            self.last_sync = time.time()
            
            # Record metrics
            sync_duration = time.time() - start_time
            hf_sync_duration.labels(operation="full_sync").observe(sync_duration)
            hf_hub_sync_total.labels(status="success").inc()
            
            logger.info(f"HF Hub sync completed: {len(filtered_candidates)} candidates found in {sync_duration:.2f}s")
            return filtered_candidates
            
        except Exception as e:
            logger.error(f"HF Hub sync failed: {e}")
            hf_hub_sync_total.labels(status="error").inc()
            raise
    
    async def _discover_models_by_pipeline(self, pipeline_tag: str) -> List[HFModelCandidate]:
        """Discover models by pipeline tag"""
        logger.info(f"Discovering models with pipeline tag: {pipeline_tag}")
        
        candidates = []
        page = 0
        per_page = 100
        max_pages = 10  # Limit to prevent excessive API calls
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while page < max_pages:
                try:
                    # Query HF Hub API
                    url = f"{self.hf_api_base}/models"
                    params = {
                        "pipeline_tag": pipeline_tag,
                        "library": self.required_library,
                        "limit": per_page,
                        "offset": page * per_page,
                        "sort": "downloads",
                        "direction": -1
                    }
                    
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    models = data.get("models", [])
                    
                    if not models:
                        break
                    
                    # Process models
                    for model_data in models:
                        candidate = self._parse_model_data(model_data, pipeline_tag)
                        if candidate:
                            candidates.append(candidate)
                    
                    page += 1
                    
                    # Rate limiting - be respectful to free tier
                    await asyncio.sleep(0.1)
                    
                except httpx.HTTPError as e:
                    logger.warning(f"HTTP error discovering {pipeline_tag} models (page {page}): {e}")
                    break
                except Exception as e:
                    logger.error(f"Error discovering {pipeline_tag} models (page {page}): {e}")
                    break
        
        logger.info(f"Discovered {len(candidates)} {pipeline_tag} model candidates")
        return candidates
    
    def _parse_model_data(self, model_data: dict, pipeline_tag: str) -> Optional[HFModelCandidate]:
        """Parse HF Hub model data into candidate"""
        try:
            # Extract basic info
            model_id = model_data.get("id", "")
            model_name = model_data.get("modelId", model_id)
            
            # Check license
            license_info = model_data.get("license", "")
            if not any(license in license_info.lower() for license in self.license_filters):
                return None
            
            # Check library
            library_name = model_data.get("library_name", "")
            if library_name != self.required_library:
                return None
            
            # Check downloads and likes
            downloads = model_data.get("downloads", 0)
            likes = model_data.get("likes", 0)
            
            if downloads < self.min_downloads or likes < self.min_likes:
                return None
            
            # Check for quantized and safetensors
            tags = model_data.get("tags", [])
            quantized = any("quantized" in tag.lower() for tag in tags)
            safetensors = any("safetensors" in tag.lower() for tag in tags)
            
            # Get last modified
            last_modified = model_data.get("lastModified", "")
            
            return HFModelCandidate(
                model_id=model_id,
                model_name=model_name,
                pipeline_tag=pipeline_tag,
                license=license_info,
                library_name=library_name,
                quantized=quantized,
                safetensors=safetensors,
                downloads=downloads,
                likes=likes,
                last_modified=last_modified,
                tags=tags
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse model data: {e}")
            return None
    
    def _filter_candidates(self, candidates: List[HFModelCandidate]) -> List[HFModelCandidate]:
        """Filter candidates based on quality criteria"""
        filtered = []
        
        for candidate in candidates:
            # Skip if already in registry
            if self.registry and self.registry.get_model(candidate.model_id):
                continue
            
            # Quality scoring
            score = self._calculate_candidate_score(candidate)
            candidate.evaluation_score = score
            
            # Only include high-quality candidates
            if score >= 0.7:  # 70% quality threshold
                filtered.append(candidate)
        
        # Sort by evaluation score
        filtered.sort(key=lambda x: x.evaluation_score, reverse=True)
        
        return filtered
    
    def _calculate_candidate_score(self, candidate: HFModelCandidate) -> float:
        """Calculate quality score for candidate"""
        score = 0.0
        
        # Downloads score (0-0.3)
        if candidate.downloads >= 100000:
            score += 0.3
        elif candidate.downloads >= 10000:
            score += 0.2
        elif candidate.downloads >= 1000:
            score += 0.1
        
        # Likes score (0-0.2)
        if candidate.likes >= 100:
            score += 0.2
        elif candidate.likes >= 50:
            score += 0.15
        elif candidate.likes >= 10:
            score += 0.1
        
        # Quantized bonus (0-0.2)
        if candidate.quantized:
            score += 0.2
        
        # Safetensors bonus (0-0.1)
        if candidate.safetensors:
            score += 0.1
        
        # License bonus (0-0.1)
        if candidate.license.lower() in ["apache-2.0", "mit"]:
            score += 0.1
        
        # Pipeline tag bonus (0-0.1)
        if candidate.pipeline_tag in ["text-generation", "text2text-generation"]:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _update_registry_candidates(self, candidates: List[HFModelCandidate]):
        """Update model registry with new candidates"""
        if not self.registry:
            return
        
        for candidate in candidates:
            # Create registry entry
            model_entry = {
                "model_id": candidate.model_id,
                "provider": "huggingface",
                "model_family": candidate.model_name.split("/")[-1],
                "version": "latest",
                "status": candidate.status,
                "capabilities": self._map_capabilities(candidate),
                "performance": {
                    "avg_ttft_ms": 0,  # To be determined during evaluation
                    "avg_completion_ms": 0,
                    "success_rate": 0.0,
                    "quality_score": candidate.evaluation_score
                },
                "costs": {
                    "input_tokens_per_1k": 0.0,  # Free tier
                    "output_tokens_per_1k": 0.0,  # Free tier
                    "currency": "USD"
                },
                "limits": {
                    "max_context_tokens": 4096,  # Default, to be determined
                    "max_output_tokens": 2048,   # Default, to be determined
                    "rate_limit_rpm": 1000,      # Free tier limit
                    "rate_limit_tpm": 10000      # Free tier limit
                },
                "health": {
                    "status": "unknown",
                    "last_check": datetime.utcnow().isoformat(),
                    "uptime_percentage": 0.0,
                    "error_rate": 0.0
                },
                "metadata": {
                    "release_date": candidate.last_modified,
                    "deprecation_date": None,
                    "recommended_for": ["free_tier", "open_source"],
                    "not_recommended_for": ["high_volume"],
                    "hf_hub_url": f"https://huggingface.co/{candidate.model_id}",
                    "pipeline_tag": candidate.pipeline_tag,
                    "license": candidate.license,
                    "downloads": candidate.downloads,
                    "likes": candidate.likes,
                    "quantized": candidate.quantized,
                    "safetensors": candidate.safetensors,
                    "discovered_at": candidate.discovered_at,
                    "evaluation_score": candidate.evaluation_score
                }
            }
            
            # Add to registry
            self.registry.add_model(model_entry)
            logger.info(f"Added HF candidate to registry: {candidate.model_id}")
    
    def _map_capabilities(self, candidate: HFModelCandidate) -> dict:
        """Map HF model capabilities to registry format"""
        capabilities = {
            "text_generation": candidate.pipeline_tag in ["text-generation", "text2text-generation"],
            "text_embeddings": candidate.pipeline_tag == "text-embeddings",
            "multimodal": False,  # HF free tier typically text-only
            "tool_use": False,    # Not common in free tier
            "long_context": False,  # Limited in free tier
            "streaming": True,    # Usually supported
            "function_calling": False,  # Not common in free tier
            "free_tier": True,    # Mark as free tier
            "open_source": True   # Mark as open source
        }
        
        return capabilities
    
    async def get_candidate_models(self, limit: int = 10) -> List[HFModelCandidate]:
        """Get top candidate models"""
        if not self.candidates_cache:
            await self.sync_hf_models()
        
        candidates = list(self.candidates_cache.values())
        candidates.sort(key=lambda x: x.evaluation_score, reverse=True)
        
        return candidates[:limit]
    
    async def promote_candidate(self, model_id: str) -> bool:
        """Promote candidate to stable status"""
        if model_id not in self.candidates_cache:
            logger.warning(f"Candidate {model_id} not found in cache")
            return False
        
        candidate = self.candidates_cache[model_id]
        candidate.status = ModelStatus.STABLE
        
        if self.registry:
            model = self.registry.get_model(model_id)
            if model:
                model["status"] = "stable"
                logger.info(f"Promoted HF candidate to stable: {model_id}")
                return True
        
        return False
    
    def should_sync(self) -> bool:
        """Check if sync should run"""
        return time.time() - self.last_sync > self.sync_interval
    
    async def run_scheduled_sync(self):
        """Run scheduled sync if needed"""
        if self.should_sync():
            await self.sync_hf_models()

# Example usage
async def main():
    """Example usage of HF Hub sync"""
    sync = HFHubSync()
    
    # Run sync
    candidates = await sync.sync_hf_models()
    
    print(f"Discovered {len(candidates)} HF model candidates:")
    for candidate in candidates[:5]:  # Show top 5
        print(f"  - {candidate.model_id} ({candidate.pipeline_tag}) - Score: {candidate.evaluation_score:.2f}")
    
    # Get top candidates
    top_candidates = await sync.get_candidate_models(limit=3)
    print(f"\nTop 3 candidates:")
    for candidate in top_candidates:
        print(f"  - {candidate.model_id}: {candidate.evaluation_score:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
