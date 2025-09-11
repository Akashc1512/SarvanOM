# Guided Prompt Policy

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE POLICY**  
**Purpose**: When to trigger, auto LMM trigger, safety & redaction, privacy, and latency budget

---

## 🎯 **Trigger Conditions**

### **When to Trigger Refinement**
The Guided Prompt Confirmation feature triggers on all free-text queries **except**:

1. **Repeat Follow-ups**: Queries in the same thread with high intent confidence (>0.8)
2. **Power User Bypass**: Queries from users with "Always bypass" setting enabled
3. **System Queries**: Internal system queries and health checks
4. **Error Recovery**: Queries that are part of error recovery flows

### **Trigger Logic**
```python
# Example trigger logic
class RefinementTrigger:
    def should_trigger_refinement(self, query: str, context: dict) -> bool:
        """Determine if refinement should be triggered"""
        
        # Check user preferences
        if context.get("user_bypass_enabled", False):
            return False
        
        # Check thread context
        if self.is_repeat_followup(query, context):
            return False
        
        # Check query characteristics
        if self.is_system_query(query):
            return False
        
        # Check intent confidence
        intent_confidence = self.analyze_intent_confidence(query)
        if intent_confidence > 0.8:
            return False
        
        # Check query complexity
        complexity = self.analyze_complexity(query)
        if complexity in ["simple", "very_simple"]:
            return False
        
        # Default to trigger
        return True
    
    def is_repeat_followup(self, query: str, context: dict) -> bool:
        """Check if this is a repeat follow-up in the same thread"""
        thread_id = context.get("thread_id")
        if not thread_id:
            return False
        
        # Check if user has been refining in this thread
        recent_refinements = self.get_recent_refinements(thread_id)
        if len(recent_refinements) > 2:
            return True
        
        # Check if query is very similar to recent queries
        similarity = self.calculate_similarity(query, recent_refinements)
        return similarity > 0.9
```

### **Intent Confidence Thresholds**
| Confidence Level | Action | Reasoning |
|------------------|--------|-----------|
| **0.9+** | Skip refinement | Very clear intent |
| **0.7-0.9** | Optional refinement | Some ambiguity |
| **0.5-0.7** | Trigger refinement | Moderate ambiguity |
| **<0.5** | Always trigger | High ambiguity |

---

## 🤖 **Auto LMM Trigger**

### **Multimodal Detection**
The system automatically triggers LMM (Large Multimodal Model) refinement when:

1. **Image Detection**: Query contains image references or attachments
2. **Screenshot Detection**: Query mentions screenshots or screen captures
3. **Video Links**: Query contains YouTube or video platform links
4. **File Attachments**: User attaches files (images, documents, etc.)
5. **Multimodal Keywords**: Query contains visual analysis keywords

### **LMM Trigger Logic**
```python
# Example LMM trigger logic
class LMMTrigger:
    def should_use_lmm(self, query: str, attachments: list) -> bool:
        """Determine if LMM should be used for refinement"""
        
        # Check for file attachments
        if attachments:
            for attachment in attachments:
                if self.is_visual_file(attachment):
                    return True
        
        # Check for image references
        if self.contains_image_references(query):
            return True
        
        # Check for video links
        if self.contains_video_links(query):
            return True
        
        # Check for multimodal keywords
        if self.contains_multimodal_keywords(query):
            return True
        
        return False
    
    def is_visual_file(self, attachment: dict) -> bool:
        """Check if attachment is a visual file"""
        visual_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        file_extension = attachment.get('extension', '').lower()
        return file_extension in visual_extensions
    
    def contains_image_references(self, query: str) -> bool:
        """Check if query references images"""
        image_keywords = [
            'image', 'picture', 'photo', 'screenshot', 'diagram', 'chart',
            'graph', 'visual', 'see this', 'look at', 'show me'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in image_keywords)
    
    def contains_video_links(self, query: str) -> bool:
        """Check if query contains video links"""
        video_domains = ['youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com']
        return any(domain in query.lower() for domain in video_domains)
```

---

## 🛡️ **Safety & Redaction**

### **PII Redaction**
The system automatically removes or blurs the following personal information:

1. **Email Addresses**: `john@example.com` → `[EMAIL_REDACTED]`
2. **Phone Numbers**: `+1-555-123-4567` → `[PHONE_REDACTED]`
3. **Physical Addresses**: `123 Main St, City, State` → `[ADDRESS_REDACTED]`
4. **Credit Card Numbers**: `1234-5678-9012-3456` → `[CARD_REDACTED]`
5. **SSN/SIN**: `123-45-6789` → `[SSN_REDACTED]`
6. **Passwords**: `password123` → `[PASSWORD_REDACTED]`

### **Redaction Implementation**
```python
# Example PII redaction implementation
import re
from typing import Dict, List

class PIIRedactor:
    def __init__(self):
        self.redaction_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
        }
    
    def redact_pii(self, text: str) -> Dict[str, str]:
        """Redact PII from text and return redacted version with metadata"""
        redacted_text = text
        redaction_log = []
        
        for pii_type, pattern in self.redaction_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                original = match.group()
                replacement = f'[{pii_type.upper()}_REDACTED]'
                redacted_text = redacted_text.replace(original, replacement)
                redaction_log.append({
                    'type': pii_type,
                    'original': original,
                    'replacement': replacement,
                    'position': match.span()
                })
        
        return {
            'redacted_text': redacted_text,
            'redaction_log': redaction_log,
            'has_pii': len(redaction_log) > 0
        }
```

### **Profanity Softening**
The system softens profanity and inappropriate language:

1. **Direct Profanity**: `damn` → `darn`
2. **Strong Language**: `f***` → `fudge`
3. **Inappropriate Content**: Block or redirect to appropriate alternatives
4. **Hate Speech**: Block entirely with educational message

### **Content Safety Filters**
```python
# Example content safety implementation
class ContentSafetyFilter:
    def __init__(self):
        self.profanity_map = {
            'damn': 'darn',
            'hell': 'heck',
            'crap': 'stuff',
            'sucks': 'is not good'
        }
        
        self.blocked_patterns = [
            r'\b(hate|kill|murder|suicide)\b',
            r'\b(drug|alcohol|weapon)\b',
            r'\b(sex|porn|adult)\b'
        ]
    
    def filter_content(self, text: str) -> Dict[str, str]:
        """Filter content for safety and appropriateness"""
        filtered_text = text.lower()
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, filtered_text, re.IGNORECASE):
                return {
                    'filtered_text': '[CONTENT_BLOCKED]',
                    'action': 'block',
                    'reason': 'Inappropriate content detected'
                }
        
        # Soften profanity
        for profanity, replacement in self.profanity_map.items():
            filtered_text = re.sub(
                rf'\b{profanity}\b',
                replacement,
                filtered_text,
                flags=re.IGNORECASE
            )
        
        return {
            'filtered_text': filtered_text,
            'action': 'allow',
            'reason': 'Content is appropriate'
        }
```

---

## 🔒 **Privacy Policy**

### **Data Storage Rules**
1. **No Raw Draft Storage**: Raw user drafts are not stored by default
2. **Consent-Based Storage**: Only store with explicit user consent
3. **Minimal Data**: Store only necessary data for improvement
4. **User Control**: Users can delete their data at any time

### **Privacy Implementation**
```python
# Example privacy implementation
class PrivacyManager:
    def __init__(self):
        self.storage_policy = {
            'raw_drafts': False,  # Never store raw drafts
            'refined_queries': True,  # Store with consent
            'user_preferences': True,  # Store user settings
            'analytics': True,  # Store anonymized analytics
            'consent_required': True  # Require explicit consent
        }
    
    def process_query(self, raw_query: str, user_consent: bool) -> Dict:
        """Process query according to privacy policy"""
        # Always redact PII regardless of consent
        redacted_query = self.redact_pii(raw_query)
        
        # Process for refinement
        refinement_result = self.generate_refinement(redacted_query)
        
        # Store data based on consent
        if user_consent and self.storage_policy['refined_queries']:
            self.store_refined_query(redacted_query, refinement_result)
        
        # Always store anonymized analytics
        if self.storage_policy['analytics']:
            self.store_analytics(redacted_query, refinement_result)
        
        return refinement_result
    
    def store_refined_query(self, query: str, result: dict):
        """Store refined query with user consent"""
        # Store only necessary data
        storage_data = {
            'query_hash': self.hash_query(query),
            'refinement_type': result['type'],
            'acceptance_rate': result['acceptance_rate'],
            'timestamp': time.time(),
            'user_id': self.get_anonymized_user_id()
        }
        
        # Store in secure database
        self.secure_storage.store(storage_data)
    
    def get_user_data(self, user_id: str) -> Dict:
        """Get user's stored data"""
        return self.secure_storage.get_user_data(user_id)
    
    def delete_user_data(self, user_id: str) -> bool:
        """Delete user's stored data"""
        return self.secure_storage.delete_user_data(user_id)
```

### **Consent Management**
```python
# Example consent management
class ConsentManager:
    def __init__(self):
        self.consent_types = {
            'data_storage': 'Store refined queries for improvement',
            'analytics': 'Use data for analytics and improvement',
            'personalization': 'Use data for personalization',
            'research': 'Use data for research purposes'
        }
    
    def get_consent_status(self, user_id: str) -> Dict:
        """Get user's consent status"""
        return self.consent_storage.get_consent(user_id)
    
    def update_consent(self, user_id: str, consent_data: Dict) -> bool:
        """Update user's consent preferences"""
        return self.consent_storage.update_consent(user_id, consent_data)
    
    def require_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has given consent for specific type"""
        consent_status = self.get_consent_status(user_id)
        return consent_status.get(consent_type, False)
```

---

## ⏱️ **Latency Budget**

### **Budget Allocation**
```
Guided Prompt Pre-flight (500ms total):
├─ Intent Analysis: 200ms
├─ Prompt Refinement: 200ms
├─ Constraint Application: 50ms
└─ Response Generation: 50ms
```

### **Budget Enforcement**
```python
# Example latency budget enforcement
import asyncio
import time
from typing import Optional, Dict, Any

class LatencyBudgetManager:
    def __init__(self, total_budget_ms: int = 500):
        self.total_budget_ms = total_budget_ms
        self.start_time = None
        self.phase_budgets = {
            'intent_analysis': 200,
            'prompt_refinement': 200,
            'constraint_application': 50,
            'response_generation': 50
        }
    
    async def execute_with_budget(self, phase: str, coro) -> Optional[Any]:
        """Execute phase within budget constraints"""
        if self.start_time is None:
            self.start_time = time.time()
        
        phase_budget = self.phase_budgets.get(phase, 100)
        elapsed_ms = (time.time() - self.start_time) * 1000
        
        if elapsed_ms >= self.total_budget_ms:
            return None  # Skip refinement
        
        remaining_budget = self.total_budget_ms - elapsed_ms
        phase_timeout = min(phase_budget, remaining_budget) / 1000
        
        try:
            return await asyncio.wait_for(coro, timeout=phase_timeout)
        except asyncio.TimeoutError:
            return None  # Phase timeout
    
    def should_skip_refinement(self) -> bool:
        """Check if refinement should be skipped due to budget constraints"""
        if self.start_time is None:
            return False
        
        elapsed_ms = (time.time() - self.start_time) * 1000
        return elapsed_ms >= self.total_budget_ms
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget in milliseconds"""
        if self.start_time is None:
            return self.total_budget_ms
        
        elapsed_ms = (time.time() - self.start_time) * 1000
        return max(0, self.total_budget_ms - elapsed_ms)
```

### **Budget Monitoring**
```python
# Example budget monitoring
class BudgetMonitor:
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'budget_exceeded': 0,
            'refinement_skipped': 0,
            'average_latency': 0.0,
            'p95_latency': 0.0
        }
    
    def record_request(self, latency_ms: float, budget_exceeded: bool):
        """Record request metrics"""
        self.metrics['total_requests'] += 1
        
        if budget_exceeded:
            self.metrics['budget_exceeded'] += 1
            self.metrics['refinement_skipped'] += 1
        
        # Update average latency
        total_requests = self.metrics['total_requests']
        current_avg = self.metrics['average_latency']
        self.metrics['average_latency'] = (
            (current_avg * (total_requests - 1) + latency_ms) / total_requests
        )
    
    def get_budget_health(self) -> Dict:
        """Get budget health metrics"""
        total_requests = self.metrics['total_requests']
        if total_requests == 0:
            return {'status': 'no_data'}
        
        budget_exceeded_rate = self.metrics['budget_exceeded'] / total_requests
        
        if budget_exceeded_rate > 0.1:  # 10% threshold
            return {'status': 'unhealthy', 'rate': budget_exceeded_rate}
        elif budget_exceeded_rate > 0.05:  # 5% threshold
            return {'status': 'warning', 'rate': budget_exceeded_rate}
        else:
            return {'status': 'healthy', 'rate': budget_exceeded_rate}
```

---

## 📚 **References**

- Overview: `docs/prompting/guided_prompt_overview.md`
- UX Flow: `docs/prompting/guided_prompt_ux_flow.md`
- Toggle Contract: `docs/prompting/guided_prompt_toggle_contract.md`
- LLM Policy: `docs/prompting/guided_prompt_llm_policy.md`
- Metrics: `docs/prompting/guided_prompt_metrics.md`
- Experiments: `docs/prompting/guided_prompt_experiments.md`
- Test Cases: `docs/prompting/guided_prompt_test_cases.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This policy ensures safe, private, and performant Guided Prompt Confirmation across all user interactions.*
