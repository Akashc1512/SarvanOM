"""
Query Classifier for SarvanOM
Categorizes and assesses query complexity for intelligent routing.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class QueryCategory(Enum):
    """Query categories for classification."""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    OPINION = "opinion"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"


class QueryComplexity(Enum):
    """Query complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class QueryAnalysis:
    """Result of query analysis."""
    category: QueryCategory
    complexity: QueryComplexity
    confidence: float
    keywords: List[str]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class QueryClassifier:
    """Classifies queries by category and complexity."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define patterns for different query categories
        self.category_patterns = {
            QueryCategory.FACTUAL: [
                r"what is",
                r"who is",
                r"when did",
                r"where is",
                r"how many",
                r"what are",
                r"define",
                r"explain",
                r"describe",
                r"tell me about"
            ],
            QueryCategory.ANALYTICAL: [
                r"analyze",
                r"examine",
                r"investigate",
                r"research",
                r"study",
                r"explore",
                r"evaluate",
                r"assess",
                r"review",
                r"consider"
            ],
            QueryCategory.CREATIVE: [
                r"create",
                r"generate",
                r"write",
                r"design",
                r"develop",
                r"imagine",
                r"brainstorm",
                r"come up with",
                r"suggest",
                r"propose"
            ],
            QueryCategory.COMPARATIVE: [
                r"compare",
                r"contrast",
                r"difference between",
                r"similar to",
                r"versus",
                r"vs",
                r"better than",
                r"worse than",
                r"advantages of",
                r"disadvantages of"
            ],
            QueryCategory.PROCEDURAL: [
                r"how to",
                r"steps to",
                r"process for",
                r"method for",
                r"procedure for",
                r"guide for",
                r"instructions for",
                r"tutorial",
                r"walkthrough",
                r"step by step"
            ],
            QueryCategory.OPINION: [
                r"what do you think",
                r"opinion on",
                r"view on",
                r"perspective on",
                r"thoughts on",
                r"belief about",
                r"feel about",
                r"think about",
                r"consider",
                r"judge"
            ],
            QueryCategory.CLARIFICATION: [
                r"clarify",
                r"explain further",
                r"elaborate on",
                r"expand on",
                r"provide more details",
                r"give examples",
                r"illustrate",
                r"demonstrate",
                r"show me",
                r"help me understand"
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            QueryComplexity.SIMPLE: [
                "what", "who", "when", "where", "how many", "define", "explain"
            ],
            QueryComplexity.MODERATE: [
                "analyze", "compare", "evaluate", "investigate", "research", "study"
            ],
            QueryComplexity.COMPLEX: [
                "synthesize", "critique", "examine", "explore", "assess", "review",
                "consider", "investigate", "research", "study", "analyze"
            ]
        }
    
    def classify_query(self, query: str) -> QueryAnalysis:
        """
        Classify a query by category and complexity.
        
        Args:
            query: The input query string
            
        Returns:
            QueryAnalysis with classification results
        """
        query_lower = query.lower().strip()
        
        # Determine category
        category, category_confidence = self._determine_category(query_lower)
        
        # Determine complexity
        complexity, complexity_confidence = self._determine_complexity(query_lower)
        
        # Extract keywords
        keywords = self._extract_keywords(query_lower)
        
        # Calculate overall confidence
        overall_confidence = (category_confidence + complexity_confidence) / 2
        
        return QueryAnalysis(
            category=category,
            complexity=complexity,
            confidence=overall_confidence,
            keywords=keywords,
            metadata={
                "category_confidence": category_confidence,
                "complexity_confidence": complexity_confidence,
                "query_length": len(query),
                "word_count": len(query.split())
            }
        )
    
    def _determine_category(self, query: str) -> Tuple[QueryCategory, float]:
        """Determine the category of a query."""
        scores = {}
        
        for category, patterns in self.category_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                scores[category] = score / len(patterns)
        
        if not scores:
            return QueryCategory.UNKNOWN, 0.0
        
        # Find the category with the highest score
        best_category = max(scores.items(), key=lambda x: x[1])
        return best_category[0], best_category[1]
    
    def _determine_complexity(self, query: str) -> Tuple[QueryComplexity, float]:
        """Determine the complexity of a query."""
        scores = {complexity: 0 for complexity in QueryComplexity}
        
        # Count complexity indicators
        for complexity, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator in query:
                    scores[complexity] += 1
        
        # Consider query length and structure
        word_count = len(query.split())
        if word_count > 20:
            scores[QueryComplexity.COMPLEX] += 2
        elif word_count > 10:
            scores[QueryComplexity.MODERATE] += 1
        
        # Check for complex sentence structures
        if any(char in query for char in [',', ';', ':', '?', '!']):
            scores[QueryComplexity.MODERATE] += 1
        
        # Find the complexity with the highest score
        best_complexity = max(scores.items(), key=lambda x: x[1])
        
        # Normalize confidence score
        max_possible_score = max(len(indicators) for indicators in self.complexity_indicators.values()) + 3
        confidence = min(best_complexity[1] / max_possible_score, 1.0)
        
        return best_complexity[0], confidence
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from the query."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Limit to top 10 keywords
    
    def get_agent_recommendations(self, analysis: QueryAnalysis) -> List[str]:
        """
        Get recommended agent types based on query analysis.
        
        Args:
            analysis: QueryAnalysis result
            
        Returns:
            List of recommended agent types
        """
        recommendations = []
        
        if analysis.category == QueryCategory.FACTUAL:
            recommendations.extend(['retrieval', 'factcheck'])
        elif analysis.category == QueryCategory.ANALYTICAL:
            recommendations.extend(['retrieval', 'synthesis', 'factcheck'])
        elif analysis.category == QueryCategory.CREATIVE:
            recommendations.extend(['synthesis'])
        elif analysis.category == QueryCategory.COMPARATIVE:
            recommendations.extend(['retrieval', 'synthesis'])
        elif analysis.category == QueryCategory.PROCEDURAL:
            recommendations.extend(['retrieval', 'synthesis'])
        elif analysis.category == QueryCategory.OPINION:
            recommendations.extend(['synthesis'])
        elif analysis.category == QueryCategory.CLARIFICATION:
            recommendations.extend(['retrieval', 'synthesis'])
        else:
            recommendations.extend(['retrieval', 'synthesis'])
        
        # Add complexity-based recommendations
        if analysis.complexity == QueryComplexity.COMPLEX:
            recommendations.append('factcheck')
        
        return list(set(recommendations))  # Remove duplicates
