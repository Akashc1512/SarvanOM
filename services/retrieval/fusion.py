"""
Reciprocal Rank Fusion - SarvanOM v2 Retrieval Service

RRF fusion with domain diversity and recency boosts.
Deduplication by domain + title + hash similarity.
Citation alignment and disagreement detection.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FusedResult:
    results: List[Dict[str, Any]]
    fusion_metadata: Dict[str, Any]
    citations: List[Dict[str, Any]]
    disagreements: List[Dict[str, Any]]
    total_results: int
    unique_domains: int
    fusion_time_ms: float

class ReciprocalRankFusion:
    """Reciprocal Rank Fusion for combining results from multiple lanes"""
    
    def __init__(self):
        self.k = 60  # RRF parameter
        self.diversity_boost = 0.1
        self.recency_boost = 0.05
    
    def fuse_results(self, lane_results: List[Any]) -> FusedResult:
        """Fuse results from multiple lanes using RRF"""
        start_time = time.time()
        
        # Collect all results with lane information
        all_results = []
        for lane_result in lane_results:
            if lane_result.status == "success":
                for i, result in enumerate(lane_result.results):
                    result['lane'] = lane_result.lane
                    result['lane_rank'] = i + 1
                    result['rrf_score'] = 1.0 / (self.k + i + 1)
                    all_results.append(result)
        
        # Group by domain for diversity
        domain_groups = {}
        for result in all_results:
            domain = result.get('domain', 'unknown')
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append(result)
        
        # Apply diversity boost
        for domain, results in domain_groups.items():
            diversity_boost = self.diversity_boost / len(results)
            for result in results:
                result['rrf_score'] += diversity_boost
        
        # Apply recency boost
        current_time = datetime.now()
        for result in all_results:
            try:
                published_at = datetime.fromisoformat(result.get('published_at', current_time.isoformat()))
                days_old = (current_time - published_at).days
                recency_boost = max(0, self.recency_boost * (1 - days_old / 365))
                result['rrf_score'] += recency_boost
            except:
                pass  # Skip recency boost if date parsing fails
        
        # Sort by RRF score
        all_results.sort(key=lambda x: x['rrf_score'], reverse=True)
        
        # Deduplicate by domain + title similarity
        deduplicated_results = self._deduplicate_results(all_results)
        
        # Generate citations
        citations = self._generate_citations(deduplicated_results)
        
        # Detect disagreements
        disagreements = self._detect_disagreements(deduplicated_results)
        
        fusion_time_ms = (time.time() - start_time) * 1000
        
        return FusedResult(
            results=deduplicated_results,
            fusion_metadata={
                'total_lanes': len(lane_results),
                'successful_lanes': len([r for r in lane_results if r.status == "success"]),
                'rrf_k': self.k,
                'diversity_boost': self.diversity_boost,
                'recency_boost': self.recency_boost
            },
            citations=citations,
            disagreements=disagreements,
            total_results=len(deduplicated_results),
            unique_domains=len(domain_groups),
            fusion_time_ms=fusion_time_ms
        )
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on domain + title similarity"""
        deduplicated = []
        seen_combinations = set()
        
        for result in results:
            domain = result.get('domain', 'unknown')
            title = result.get('title', '')
            combination = f"{domain}:{title.lower()}"
            
            if combination not in seen_combinations:
                seen_combinations.add(combination)
                deduplicated.append(result)
        
        return deduplicated
    
    def _generate_citations(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate citations for results"""
        citations = []
        for i, result in enumerate(results):
            citations.append({
                'id': f"citation_{i+1}",
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'domain': result.get('domain', ''),
                'published_at': result.get('published_at', ''),
                'author': result.get('author', ''),
                'relevance_score': result.get('relevance_score', 0.0),
                'authority_score': result.get('authority_score', 0.0)
            })
        return citations
    
    def _detect_disagreements(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect disagreements between sources"""
        disagreements = []
        
        # Simple disagreement detection based on conflicting information
        # In real implementation, this would use more sophisticated NLP
        for i, result1 in enumerate(results):
            for j, result2 in enumerate(results[i+1:], i+1):
                if result1.get('domain') != result2.get('domain'):
                    # Check for potential conflicts (simplified)
                    if self._has_potential_conflict(result1, result2):
                        disagreements.append({
                            'source1': result1.get('domain', ''),
                            'source2': result2.get('domain', ''),
                            'conflict_type': 'potential_disagreement',
                            'confidence': 0.5  # Simplified confidence
                        })
        
        return disagreements
    
    def _has_potential_conflict(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> bool:
        """Check if two results have potential conflicts"""
        # Simplified conflict detection
        # In real implementation, this would use semantic analysis
        return False  # Placeholder
