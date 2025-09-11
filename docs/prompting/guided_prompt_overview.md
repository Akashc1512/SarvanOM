# Guided Prompt Confirmation - Overview

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE FEATURE**  
**Purpose**: Purpose & principles for Guided Prompt Confirmation feature (default ON, one-tap Bypass for power users, low friction)

---

## 🎯 **Purpose & Principles**

### **Core Purpose**
The Guided Prompt Confirmation feature helps users clarify their intent before execution, reducing wasted queries and teaching prompt engineering passively. It provides intelligent prompt refinement suggestions while maintaining low friction for power users.

### **Design Principles**
1. **Default ON**: All users get confirmation by default for better query quality
2. **One-tap Bypass**: Power users can skip refinement with a single action
3. **Low Friction**: Minimal interruption to user workflow
4. **Educational**: Teaches better prompt engineering through examples
5. **Privacy-First**: No raw draft storage by default
6. **Accessibility-First**: Keyboard navigation and screen reader support

---

## 🔄 **Supported Modes**

### **1. Refine Mode**
- **Purpose**: Improve clarity and specificity of user queries
- **Trigger**: Ambiguous or vague queries
- **Example**: "show me apple" → "Do you mean Apple Inc. (company) stock performance, or the fruit Apple nutritional info?"

### **2. Disambiguate Mode**
- **Purpose**: Resolve ambiguous terms or concepts
- **Trigger**: Queries with multiple possible interpretations
- **Example**: "python tutorial" → "Do you want a Python programming tutorial or information about Python snakes?"

### **3. Decompose Mode (Multi-step)**
- **Purpose**: Break complex queries into manageable steps
- **Trigger**: Multi-part or complex research queries
- **Example**: "analyze climate change" → "Would you like to: 1) Focus on causes, 2) Focus on effects, 3) Focus on solutions, or 4) Get a comprehensive overview?"

### **4. Constrain Mode**
- **Purpose**: Add time, sources, cost, or depth constraints
- **Trigger**: Open-ended queries that could be expensive or time-consuming
- **Example**: "research AI" → "Add constraints: Time range (recent/5 years/all), Sources (academic/news/both), Depth (simple/technical/research)"

### **5. Sanitize Mode**
- **Purpose**: Remove PII and harmful content, apply safety filters
- **Trigger**: Queries containing personal information or potentially harmful content
- **Example**: "my email is john@example.com, tell me about hacking" → "I'll help you learn about cybersecurity. [PII removed]"

---

## 🌍 **Language Detection & Localization Strategy**

### **Language Detection**
- **Input Analysis**: Detect user's primary language from query
- **UI Language**: Confirm UI in user's detected language
- **Source Preservation**: Preserve source language in final prompt unless user opts to translate

### **Localization Approach**
```python
# Example language detection and localization
class LanguageHandler:
    def detect_language(self, query: str) -> str:
        """Detect primary language of user query"""
        # Use language detection library
        detected_lang = detect_language(query)
        return detected_lang
    
    def localize_ui(self, detected_lang: str) -> dict:
        """Get UI text in detected language"""
        return {
            "confirm_button": self.get_text("confirm", detected_lang),
            "edit_button": self.get_text("edit", detected_lang),
            "skip_button": self.get_text("skip", detected_lang),
            "suggestions_title": self.get_text("suggestions_title", detected_lang)
        }
    
    def preserve_source_language(self, original_query: str, refined_query: str) -> str:
        """Preserve source language unless user opts to translate"""
        if self.user_prefers_translation():
            return self.translate_query(refined_query, target_lang="en")
        return refined_query
```

### **Supported Languages**
| Language | Code | UI Support | Query Processing | Notes |
|----------|------|------------|------------------|-------|
| **English** | en | ✅ Full | ✅ Native | Primary language |
| **Spanish** | es | ✅ Full | ✅ Native | Full support |
| **French** | fr | ✅ Full | ✅ Native | Full support |
| **German** | de | ✅ Full | ✅ Native | Full support |
| **Chinese (Simplified)** | zh-CN | ✅ Full | ✅ Native | Full support |
| **Japanese** | ja | ✅ Full | ✅ Native | Full support |
| **Portuguese** | pt | ✅ Full | ✅ Native | Full support |
| **Russian** | ru | ✅ Full | ✅ Native | Full support |

---

## 🎛️ **User Experience Modes**

### **Default Mode (ON)**
- **Target**: All users, especially new users
- **Behavior**: Show refinement suggestions for ambiguous queries
- **Benefits**: Better query quality, learning opportunity
- **Friction**: Low - one-tap to confirm or skip

### **Expert Mode (OFF)**
- **Target**: Power users who prefer direct execution
- **Behavior**: Bypass refinement, run queries directly
- **Benefits**: Faster workflow, no interruptions
- **Friction**: None - direct execution

### **Adaptive Mode**
- **Target**: Users who consistently override suggestions
- **Behavior**: System learns user preferences and auto-switches
- **Benefits**: Personalized experience, reduced friction over time
- **Friction**: Gradual reduction based on user behavior

---

## 🔧 **Technical Implementation**

### **Architecture Overview**
```
User Query → Language Detection → Intent Analysis → Refinement Generation → UI Display → User Choice → Final Query
```

### **Key Components**
1. **Language Detector**: Identifies user's primary language
2. **Intent Analyzer**: Determines query complexity and ambiguity
3. **Refinement Generator**: Creates improvement suggestions
4. **UI Renderer**: Displays suggestions in user's language
5. **Choice Handler**: Processes user confirmation/edit/skip

### **Performance Requirements**
- **Latency**: ≤ 500ms for refinement generation
- **Accuracy**: ≥ 80% relevant suggestions
- **Availability**: 99.9% uptime
- **Scalability**: Support 1000+ concurrent users

---

## 📊 **Success Metrics**

### **Primary KPIs**
| Metric | Target | Measurement | Notes |
|--------|--------|-------------|-------|
| **Refinement Shown Rate** | 60-80% | % of queries showing refinement | Depends on query quality |
| **Acceptance Rate** | ≥ 45% | % of suggestions accepted | Quality indicator |
| **Edit Rate** | 20-30% | % of suggestions edited | User engagement |
| **Skip Rate** | ≤ 35% | % of suggestions skipped | Friction indicator |
| **Time to Refinement** | ≤ 500ms | Median time to show suggestions | Performance |

### **Secondary KPIs**
| Metric | Target | Measurement | Notes |
|--------|--------|-------------|-------|
| **User Satisfaction** | ≥ 4.0/5.0 | User feedback score | Quality indicator |
| **Query Success Rate** | ≥ 90% | % of refined queries succeeding | Effectiveness |
| **Learning Rate** | ≥ 20% | % of users improving over time | Educational value |
| **Complaint Rate** | ≤ 5% | % of users complaining | User experience |

---

## 🔒 **Privacy & Security**

### **Privacy Principles**
1. **No Raw Storage**: Don't store raw user drafts by default
2. **Consent-Based**: Only store with explicit user consent
3. **Data Minimization**: Store only necessary data for improvement
4. **User Control**: Users can delete their data at any time

### **Security Measures**
1. **PII Redaction**: Automatically remove personal information
2. **Content Filtering**: Block harmful or inappropriate content
3. **Encryption**: Encrypt all stored data
4. **Access Control**: Limit access to authorized personnel only

### **Data Handling**
```python
# Example privacy-safe data handling
class PrivacyHandler:
    def process_query(self, raw_query: str) -> dict:
        """Process query with privacy protection"""
        # Redact PII
        sanitized_query = self.redact_pii(raw_query)
        
        # Check for harmful content
        if self.contains_harmful_content(sanitized_query):
            return {"error": "Content blocked for safety"}
        
        # Process without storing raw data
        return self.analyze_intent(sanitized_query)
    
    def redact_pii(self, query: str) -> str:
        """Remove personal information"""
        # Remove emails, phones, addresses, etc.
        patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
            r'\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b'  # Credit card
        ]
        
        for pattern in patterns:
            query = re.sub(pattern, '[REDACTED]', query)
        
        return query
```

---

## 📚 **References**

- UX Flow: `docs/prompting/guided_prompt_ux_flow.md`
- Policy: `docs/prompting/guided_prompt_policy.md`
- Toggle Contract: `docs/prompting/guided_prompt_toggle_contract.md`
- LLM Policy: `docs/prompting/guided_prompt_llm_policy.md`
- Metrics: `docs/prompting/guided_prompt_metrics.md`
- Experiments: `docs/prompting/guided_prompt_experiments.md`
- Test Cases: `docs/prompting/guided_prompt_test_cases.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This overview provides the foundation for the Guided Prompt Confirmation feature in SarvanOM v2.*
