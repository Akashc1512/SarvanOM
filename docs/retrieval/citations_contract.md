# Citations Contract - SarvanOM v2

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE CONTRACT**  
**Purpose**: Define citation alignment and disagreement flagging specifications

---

## 🎯 **Citations Overview**

The Citations Contract defines how sources are aligned with generated responses, how citations are formatted, and how disagreements between sources are detected and flagged. This ensures transparency and verifiability of all information provided.

### **Core Principles**
1. **Transparency**: Every major claim must be backed by a source
2. **Accuracy**: Citations must accurately reflect the source content
3. **Completeness**: All relevant sources must be included
4. **Disagreement Detection**: Conflicting information must be flagged
5. **Verifiability**: Users must be able to verify all claims

---

## 📝 **Citation Alignment**

### **Alignment Strategy**
| Strategy | Description | Use Case | Accuracy |
|----------|-------------|----------|----------|
| **Sentence-to-Passage** | Map each sentence to source passages | General responses | High |
| **Claim-to-Source** | Map specific claims to sources | Factual responses | Very High |
| **Topic-to-Source** | Map topics to relevant sources | Research responses | Medium |
| **Quote-to-Source** | Map direct quotes to sources | Quoted responses | Very High |

### **Alignment Implementation**
```python
# Example citation alignment implementation
class CitationAligner:
    def __init__(self):
        self.similarity_threshold = 0.7
        self.max_citations_per_sentence = 3
        self.min_confidence = 0.6
    
    def align_citations(self, response_text: str, source_documents: list) -> dict:
        """Align citations with response text"""
        # Split response into sentences
        sentences = self.split_into_sentences(response_text)
        
        # Align each sentence with sources
        aligned_sentences = []
        for sentence in sentences:
            alignment = self.align_sentence(sentence, source_documents)
            aligned_sentences.append(alignment)
        
        # Generate bibliography
        bibliography = self.generate_bibliography(source_documents)
        
        # Detect disagreements
        disagreements = self.detect_disagreements(aligned_sentences)
        
        return {
            "aligned_sentences": aligned_sentences,
            "bibliography": bibliography,
            "disagreements": disagreements,
            "citation_count": len(bibliography),
            "alignment_confidence": self.calculate_overall_confidence(aligned_sentences)
        }
    
    def align_sentence(self, sentence: str, source_documents: list) -> dict:
        """Align a single sentence with sources"""
        # Find matching passages
        matching_passages = self.find_matching_passages(sentence, source_documents)
        
        # Calculate confidence
        confidence = self.calculate_alignment_confidence(sentence, matching_passages)
        
        # Create citation markers
        citations = self.create_citation_markers(matching_passages)
        
        return {
            "sentence": sentence,
            "citations": citations,
            "confidence": confidence,
            "has_citations": len(citations) > 0
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
                        "similarity": similarity,
                        "passage_start": self.find_passage_start(content, passage),
                        "passage_end": self.find_passage_end(content, passage)
                    })
        
        # Sort by similarity and return top matches
        matching_passages.sort(key=lambda x: x["similarity"], reverse=True)
        return matching_passages[:self.max_citations_per_sentence]
    
    def calculate_similarity(self, sentence: str, passage: str) -> float:
        """Calculate semantic similarity between sentence and passage"""
        # Use sentence transformers for semantic similarity
        sentence_embedding = self.sentence_transformer.encode(sentence)
        passage_embedding = self.sentence_transformer.encode(passage)
        
        # Calculate cosine similarity
        similarity = cosine_similarity([sentence_embedding], [passage_embedding])[0][0]
        
        return float(similarity)
    
    def create_citation_markers(self, matching_passages: list) -> list:
        """Create citation markers for passages"""
        citations = []
        
        for i, passage in enumerate(matching_passages, 1):
            citations.append({
                "marker": f"[{i}]",
                "document_id": passage["document"]["id"],
                "passage": passage["passage"],
                "similarity": passage["similarity"],
                "passage_start": passage["passage_start"],
                "passage_end": passage["passage_end"],
                "url": passage["document"]["url"],
                "title": passage["document"]["title"]
            })
        
        return citations
```

---

## 📚 **Bibliography Generation**

### **Bibliography Schema**
```json
{
  "id": 1,
  "title": "Document Title",
  "url": "https://example.com/document",
  "domain": "example.com",
  "author": "Author Name",
  "published_at": "2025-01-01T00:00:00Z",
  "excerpt": "Relevant excerpt from the document",
  "relevance_score": 0.85,
  "authority_score": 0.9,
  "accessibility": "public",
  "language": "en",
  "word_count": 1500,
  "citations_count": 3
}
```

### **Bibliography Implementation**
```python
# Example bibliography implementation
class BibliographyGenerator:
    def __init__(self):
        self.authority_scores = self.load_authority_scores()
        self.language_detector = self.load_language_detector()
    
    def generate_bibliography(self, source_documents: list) -> list:
        """Generate comprehensive bibliography"""
        bibliography = []
        
        for i, doc in enumerate(source_documents, 1):
            bibliography_entry = {
                "id": i,
                "title": doc.get("title", "Untitled"),
                "url": doc.get("url", ""),
                "domain": doc.get("domain", ""),
                "author": doc.get("author", "Unknown"),
                "published_at": doc.get("published_at", ""),
                "excerpt": self.generate_excerpt(doc),
                "relevance_score": doc.get("relevance_score", 0.5),
                "authority_score": self.calculate_authority_score(doc),
                "accessibility": self.determine_accessibility(doc),
                "language": self.detect_language(doc),
                "word_count": self.count_words(doc.get("content", "")),
                "citations_count": self.count_citations(doc)
            }
            bibliography.append(bibliography_entry)
        
        # Sort by relevance and authority
        bibliography.sort(key=lambda x: (x["relevance_score"] + x["authority_score"]) / 2, reverse=True)
        
        return bibliography
    
    def generate_excerpt(self, doc: dict) -> str:
        """Generate relevant excerpt from document"""
        content = doc.get("content", "")
        
        # Find most relevant passage
        relevant_passage = self.find_most_relevant_passage(content)
        
        # Truncate to reasonable length
        if len(relevant_passage) > 200:
            relevant_passage = relevant_passage[:200] + "..."
        
        return relevant_passage
    
    def calculate_authority_score(self, doc: dict) -> float:
        """Calculate authority score for document"""
        domain = doc.get("domain", "")
        
        # Check predefined authority scores
        if domain in self.authority_scores:
            return self.authority_scores[domain]
        
        # Calculate based on domain characteristics
        if domain.endswith(".edu"):
            return 0.8
        elif domain.endswith(".gov"):
            return 0.9
        elif domain.endswith(".org"):
            return 0.7
        else:
            return 0.5
    
    def determine_accessibility(self, doc: dict) -> str:
        """Determine document accessibility"""
        url = doc.get("url", "")
        
        if "paywall" in url.lower() or "subscription" in url.lower():
            return "paywall"
        elif "login" in url.lower() or "auth" in url.lower():
            return "login_required"
        else:
            return "public"
    
    def detect_language(self, doc: dict) -> str:
        """Detect document language"""
        content = doc.get("content", "")
        if not content:
            return "en"
        
        try:
            language = self.language_detector.detect(content)
            return language
        except:
            return "en"
    
    def count_words(self, content: str) -> int:
        """Count words in content"""
        if not content:
            return 0
        
        words = content.split()
        return len(words)
    
    def count_citations(self, doc: dict) -> int:
        """Count citations in document"""
        content = doc.get("content", "")
        if not content:
            return 0
        
        # Count citation patterns
        citation_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\(\d+\)',  # (1), (2), etc.
            r'^\d+\.',   # 1., 2., etc.
        ]
        
        total_citations = 0
        for pattern in citation_patterns:
            matches = re.findall(pattern, content)
            total_citations += len(matches)
        
        return total_citations
```

---

## ⚠️ **Disagreement Detection**

### **Disagreement Types**
| Type | Description | Severity | Action |
|------|-------------|----------|--------|
| **Factual Disagreement** | Contradictory facts | High | Flag and explain |
| **Temporal Disagreement** | Different timeframes | Medium | Note temporal context |
| **Methodological Disagreement** | Different approaches | Low | Present both views |
| **Interpretation Disagreement** | Different interpretations | Medium | Present both views |

### **Disagreement Detection Implementation**
```python
# Example disagreement detection implementation
class DisagreementDetector:
    def __init__(self):
        self.factual_keywords = [
            "is", "are", "was", "were", "will be", "has been", "have been",
            "always", "never", "all", "none", "every", "no", "some"
        ]
        self.temporal_keywords = [
            "in", "on", "at", "during", "before", "after", "since", "until",
            "recently", "previously", "currently", "historically"
        ]
        self.contradiction_indicators = [
            "however", "but", "although", "despite", "in contrast", "on the other hand",
            "contradicts", "disagrees", "conflicts", "opposes"
        ]
    
    def detect_disagreements(self, aligned_sentences: list) -> list:
        """Detect disagreements between sources"""
        disagreements = []
        
        # Group sentences by topic
        topic_groups = self.group_sentences_by_topic(aligned_sentences)
        
        for topic, sentences in topic_groups.items():
            if len(sentences) > 1:
                # Check for disagreements within topic
                topic_disagreements = self.find_topic_disagreements(topic, sentences)
                disagreements.extend(topic_disagreements)
        
        # Check for cross-topic disagreements
        cross_topic_disagreements = self.find_cross_topic_disagreements(aligned_sentences)
        disagreements.extend(cross_topic_disagreements)
        
        return disagreements
    
    def group_sentences_by_topic(self, aligned_sentences: list) -> dict:
        """Group sentences by topic"""
        topic_groups = {}
        
        for sentence_data in aligned_sentences:
            sentence = sentence_data["sentence"]
            topic = self.extract_topic(sentence)
            
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(sentence_data)
        
        return topic_groups
    
    def extract_topic(self, sentence: str) -> str:
        """Extract topic from sentence"""
        # Use NLP to extract main topic
        doc = self.nlp(sentence)
        
        # Get main noun phrases
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        
        if noun_phrases:
            return noun_phrases[0]
        else:
            # Fallback to first few words
            words = sentence.split()[:3]
            return " ".join(words)
    
    def find_topic_disagreements(self, topic: str, sentences: list) -> list:
        """Find disagreements within a topic"""
        disagreements = []
        
        # Check for factual disagreements
        factual_disagreements = self.find_factual_disagreements(sentences)
        disagreements.extend(factual_disagreements)
        
        # Check for temporal disagreements
        temporal_disagreements = self.find_temporal_disagreements(sentences)
        disagreements.extend(temporal_disagreements)
        
        # Check for methodological disagreements
        methodological_disagreements = self.find_methodological_disagreements(sentences)
        disagreements.extend(methodological_disagreements)
        
        return disagreements
    
    def find_factual_disagreements(self, sentences: list) -> list:
        """Find factual disagreements"""
        disagreements = []
        
        for i, sentence1 in enumerate(sentences):
            for j, sentence2 in enumerate(sentences[i+1:], i+1):
                if self.is_factual_disagreement(sentence1["sentence"], sentence2["sentence"]):
                    disagreements.append({
                        "type": "factual_disagreement",
                        "severity": "high",
                        "topic": self.extract_topic(sentence1["sentence"]),
                        "conflicting_sentences": [
                            {
                                "sentence": sentence1["sentence"],
                                "citations": sentence1["citations"],
                                "confidence": sentence1["confidence"]
                            },
                            {
                                "sentence": sentence2["sentence"],
                                "citations": sentence2["citations"],
                                "confidence": sentence2["confidence"]
                            }
                        ],
                        "explanation": self.generate_disagreement_explanation(sentence1, sentence2)
                    })
        
        return disagreements
    
    def is_factual_disagreement(self, sentence1: str, sentence2: str) -> bool:
        """Check if two sentences contain factual disagreement"""
        # Extract facts from sentences
        facts1 = self.extract_facts(sentence1)
        facts2 = self.extract_facts(sentence2)
        
        # Check for contradictory facts
        for fact1 in facts1:
            for fact2 in facts2:
                if self.are_contradictory(fact1, fact2):
                    return True
        
        return False
    
    def extract_facts(self, sentence: str) -> list:
        """Extract facts from sentence"""
        facts = []
        
        # Use NLP to extract facts
        doc = self.nlp(sentence)
        
        # Extract subject-verb-object relationships
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                subject = self.get_subject(token)
                obj = self.get_object(token)
                
                if subject and obj:
                    facts.append({
                        "subject": subject,
                        "verb": token.text,
                        "object": obj,
                        "sentence": sentence
                    })
        
        return facts
    
    def are_contradictory(self, fact1: dict, fact2: dict) -> bool:
        """Check if two facts are contradictory"""
        # Check for contradictory verbs
        contradictory_verbs = [
            ("is", "is not"), ("are", "are not"), ("was", "was not"),
            ("has", "has not"), ("have", "have not"), ("will", "will not"),
            ("always", "never"), ("all", "none"), ("every", "no")
        ]
        
        for pos, neg in contradictory_verbs:
            if (fact1["verb"].lower() == pos and fact2["verb"].lower() == neg) or \
               (fact1["verb"].lower() == neg and fact2["verb"].lower() == pos):
                return True
        
        return False
    
    def generate_disagreement_explanation(self, sentence1: dict, sentence2: dict) -> str:
        """Generate explanation for disagreement"""
        return f"The sources provide conflicting information: '{sentence1['sentence']}' vs '{sentence2['sentence']}'. This may be due to different timeframes, methodologies, or interpretations."
```

---

## 📊 **Citation Quality Metrics**

### **Quality Metrics**
| Metric | Description | Target | Measurement |
|--------|-------------|--------|-------------|
| **Citation Coverage** | % of sentences with citations | > 80% | Sentence analysis |
| **Citation Accuracy** | % of accurate citations | > 90% | Human evaluation |
| **Source Diversity** | Number of unique domains | > 3 | Domain counting |
| **Authority Score** | Average source authority | > 0.7 | Authority calculation |
| **Disagreement Rate** | % of responses with disagreements | < 20% | Disagreement detection |

### **Quality Monitoring**
```python
# Example citation quality monitoring
class CitationQualityMonitor:
    def __init__(self):
        self.metrics = {
            "citation_coverage": 0.0,
            "citation_accuracy": 0.0,
            "source_diversity": 0.0,
            "authority_score": 0.0,
            "disagreement_rate": 0.0
        }
    
    def evaluate_citation_quality(self, citation_data: dict) -> dict:
        """Evaluate citation quality"""
        # Calculate citation coverage
        coverage = self.calculate_coverage(citation_data["aligned_sentences"])
        
        # Calculate source diversity
        diversity = self.calculate_diversity(citation_data["bibliography"])
        
        # Calculate authority score
        authority = self.calculate_authority(citation_data["bibliography"])
        
        # Calculate disagreement rate
        disagreement_rate = len(citation_data["disagreements"]) / max(len(citation_data["aligned_sentences"]), 1)
        
        return {
            "citation_coverage": coverage,
            "source_diversity": diversity,
            "authority_score": authority,
            "disagreement_rate": disagreement_rate,
            "overall_quality": (coverage + diversity + authority + (1 - disagreement_rate)) / 4
        }
    
    def calculate_coverage(self, aligned_sentences: list) -> float:
        """Calculate citation coverage"""
        if not aligned_sentences:
            return 0.0
        
        sentences_with_citations = sum(1 for s in aligned_sentences if s["has_citations"])
        return sentences_with_citations / len(aligned_sentences)
    
    def calculate_diversity(self, bibliography: list) -> float:
        """Calculate source diversity"""
        if not bibliography:
            return 0.0
        
        unique_domains = set(entry["domain"] for entry in bibliography)
        return len(unique_domains) / len(bibliography)
    
    def calculate_authority(self, bibliography: list) -> float:
        """Calculate average authority score"""
        if not bibliography:
            return 0.0
        
        total_authority = sum(entry["authority_score"] for entry in bibliography)
        return total_authority / len(bibliography)
```

---

## 📚 **References**

- Retrieval & Index Fabric: `06_retrieval_and_index_fabric.md`
- Fusion Policy: `docs/retrieval/fusion_policy.md`
- Data Platform: `07_data_platform_qdrant_arango_meili.md`
- System Context: `docs/architecture/system_context.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This citations contract ensures transparent, accurate, and verifiable information in SarvanOM v2 responses.*
