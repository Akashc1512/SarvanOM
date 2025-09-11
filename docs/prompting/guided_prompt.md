# Guided Prompt Confirmation Specification

**Version**: 1.0  
**Last Updated**: September 9, 2025  
**Owner**: Product Team  

## Overview

The Guided Prompt Confirmation feature is a user experience enhancement that helps users clarify their intent before query execution. It uses lightweight LLM analysis to refine ambiguous queries and provides users with confirmation options, significantly improving query quality and user satisfaction.

## Core Workflow

### 1. User Input Processing
```
User Input: "show me apple"
    ↓
Intent Analyzer: Lightweight LLM parsing
    ↓
Refined Prompt Generation: System proposes refined query
    ↓
User Confirmation: Confirm/Edit/Disable options
    ↓
Query Execution: Process refined or original query
```

### 2. Intent Analysis Process
```python
# Intent analysis configuration
intent_analysis_config = {
    "model": "ollama:llama3:3b",  # Fastest available free model
    "timeout": 500,  # 500ms budget
    "max_tokens": 150,  # Concise analysis
    "temperature": 0.3,  # Consistent analysis
    "analysis_prompt": """
    Analyze this user query and identify potential ambiguities or improvements.
    
    Query: "{user_query}"
    
    Provide:
    1. Identified ambiguity (if any)
    2. Refined query suggestion
    3. Confidence score (0-1)
    4. Reasoning for refinement
    
    Format as JSON:
    {
        "has_ambiguity": boolean,
        "refined_query": "string",
        "confidence": float,
        "reasoning": "string",
        "suggested_lane": "simple|technical|research|multimodal"
    }
    """
}
```

### 3. User Confirmation Interface
```typescript
// GuidedPromptModal component interface
interface GuidedPromptModalProps {
  originalQuery: string;
  refinedQuery: string;
  confidence: number;
  reasoning: string;
  suggestedLane: QueryLane;
  onConfirm: (query: string) => void;
  onEdit: (query: string) => void;
  onDisable: () => void;
  onSkip: () => void;
}

// User confirmation options
enum ConfirmationAction {
  CONFIRM = "confirm",      // Use refined query
  EDIT = "edit",           // Edit refined query
  DISABLE = "disable",     // Disable feature for user
  SKIP = "skip"           // Skip this time only
}
```

## Feature Modes

### 1. Default Mode (ON)
- **Target**: All new users and users who haven't disabled the feature
- **Behavior**: Show confirmation modal for all queries
- **Benefits**: Improved query quality, user education
- **Metrics**: Track acceptance rate and user satisfaction

### 2. Expert Mode (OFF)
- **Target**: Power users who have disabled the feature
- **Behavior**: Bypass confirmation, direct query execution
- **Benefits**: Faster workflow for experienced users
- **Metrics**: Track usage patterns and performance

### 3. Adaptive Mode (Future Enhancement)
- **Target**: Users who consistently override suggestions
- **Behavior**: Auto-switch to expert mode with notification
- **Benefits**: Personalized experience based on user behavior
- **Metrics**: Track adaptation patterns and user feedback

## Integration Points

### 1. Frontend Integration
```typescript
// Query input component with guided prompt
const QueryInput: React.FC = () => {
  const [query, setQuery] = useState("");
  const [showGuidedPrompt, setShowGuidedPrompt] = useState(false);
  const [guidedPromptData, setGuidedPromptData] = useState(null);
  const [guidedPromptEnabled, setGuidedPromptEnabled] = useState(true);

  const handleSubmit = async (userQuery: string) => {
    if (guidedPromptEnabled) {
      // Analyze query for refinement
      const analysis = await analyzeQuery(userQuery);
      
      if (analysis.has_ambiguity && analysis.confidence > 0.7) {
        setGuidedPromptData(analysis);
        setShowGuidedPrompt(true);
        return;
      }
    }
    
    // Execute query directly
    executeQuery(userQuery);
  };

  return (
    <div className="query-input-container">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSubmit(query)}
        placeholder="Ask me anything..."
      />
      
      {showGuidedPrompt && (
        <GuidedPromptModal
          originalQuery={query}
          refinedQuery={guidedPromptData.refined_query}
          confidence={guidedPromptData.confidence}
          reasoning={guidedPromptData.reasoning}
          suggestedLane={guidedPromptData.suggested_lane}
          onConfirm={(refinedQuery) => {
            setShowGuidedPrompt(false);
            executeQuery(refinedQuery);
          }}
          onEdit={(editedQuery) => {
            setShowGuidedPrompt(false);
            executeQuery(editedQuery);
          }}
          onDisable={() => {
            setGuidedPromptEnabled(false);
            setShowGuidedPrompt(false);
            executeQuery(query);
          }}
          onSkip={() => {
            setShowGuidedPrompt(false);
            executeQuery(query);
          }}
        />
      )}
    </div>
  );
};
```

### 2. Backend Integration
```python
# Prompt Refinement Service
class PromptRefinementService:
    def __init__(self):
        self.llm_client = self._get_fastest_llm()
        self.timeout = 500  # 500ms budget
        self.cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour cache
    
    async def analyze_query(self, user_query: str) -> dict:
        """Analyze user query for potential refinement"""
        # Check cache first
        cache_key = hashlib.md5(user_query.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Run analysis with timeout
            analysis = await asyncio.wait_for(
                self._run_analysis(user_query),
                timeout=self.timeout / 1000
            )
            
            # Cache result
            self.cache[cache_key] = analysis
            return analysis
            
        except asyncio.TimeoutError:
            # Fallback to direct execution
            return {
                "has_ambiguity": False,
                "refined_query": user_query,
                "confidence": 0.0,
                "reasoning": "Analysis timeout",
                "suggested_lane": "simple"
            }
    
    async def _run_analysis(self, user_query: str) -> dict:
        """Run LLM analysis of user query"""
        prompt = self._build_analysis_prompt(user_query)
        
        response = await self.llm_client.generate(
            prompt=prompt,
            max_tokens=150,
            temperature=0.3
        )
        
        return self._parse_analysis_response(response)
    
    def _get_fastest_llm(self):
        """Get the fastest available LLM for analysis"""
        # Priority order: Ollama local > HuggingFace small > OpenAI GPT-3.5
        if self._is_ollama_available():
            return OllamaClient(model="llama3:3b")
        elif self._is_huggingface_available():
            return HuggingFaceClient(model="microsoft/DialoGPT-small")
        else:
            return OpenAIClient(model="gpt-3.5-turbo")
```

### 3. Settings Integration
```typescript
// Settings page toggle
const SettingsPage: React.FC = () => {
  const [guidedPromptEnabled, setGuidedPromptEnabled] = useState(true);
  
  const handleToggleGuidedPrompt = async (enabled: boolean) => {
    setGuidedPromptEnabled(enabled);
    
    // Save to user preferences
    await updateUserPreferences({
      guided_prompt_enabled: enabled
    });
    
    // Track setting change
    analytics.track('guided_prompt_toggle', {
      enabled: enabled,
      user_id: getCurrentUserId()
    });
  };

  return (
    <div className="settings-page">
      <h2>Query Preferences</h2>
      
      <div className="setting-item">
        <label>
          <input
            type="checkbox"
            checked={guidedPromptEnabled}
            onChange={(e) => handleToggleGuidedPrompt(e.target.checked)}
          />
          Enable Guided Prompt Confirmation
        </label>
        <p className="setting-description">
          Get suggestions to refine your queries for better results. 
          This helps clarify ambiguous questions and improves answer quality.
        </p>
      </div>
    </div>
  );
};
```

## Time Budgets and Performance

### 1. Analysis Time Budget
```yaml
# Time budget configuration
time_budgets:
  analysis_timeout: 500ms  # Maximum time for query analysis
  cache_lookup: 10ms       # Cache lookup time
  llm_inference: 400ms     # LLM inference time
  response_parsing: 50ms   # Response parsing time
  fallback_time: 40ms      # Fallback processing time

# Performance targets
performance_targets:
  p95_analysis_time: 400ms
  p99_analysis_time: 500ms
  cache_hit_rate: 0.3      # 30% cache hit rate
  analysis_accuracy: 0.85  # 85% accurate analysis
```

### 2. Parallel Processing
```python
# Parallel processing with orchestrator warmup
async def process_query_with_guidance(user_query: str):
    """Process query with guided prompt in parallel with orchestrator warmup"""
    
    # Start both processes in parallel
    analysis_task = asyncio.create_task(
        prompt_refinement_service.analyze_query(user_query)
    )
    
    warmup_task = asyncio.create_task(
        orchestrator_service.warmup()
    )
    
    # Wait for analysis (with timeout)
    try:
        analysis_result = await asyncio.wait_for(analysis_task, timeout=0.5)
        
        if analysis_result["has_ambiguity"] and analysis_result["confidence"] > 0.7:
            return {
                "action": "show_guidance",
                "analysis": analysis_result
            }
        else:
            # Wait for warmup to complete
            await warmup_task
            return {
                "action": "execute_direct",
                "query": user_query
            }
            
    except asyncio.TimeoutError:
        # Analysis timeout, execute directly
        await warmup_task
        return {
            "action": "execute_direct",
            "query": user_query
        }
```

## Observability and Metrics

### 1. Key Metrics
```yaml
# Guided prompt metrics
metrics:
  usage_metrics:
    - name: "guided_prompt_queries_total"
      description: "Total number of queries analyzed for guidance"
      type: "counter"
    
    - name: "guided_prompt_suggestions_shown"
      description: "Number of guidance suggestions shown to users"
      type: "counter"
    
    - name: "guided_prompt_acceptance_rate"
      description: "Percentage of suggestions accepted by users"
      type: "gauge"
    
    - name: "guided_prompt_override_rate"
      description: "Percentage of suggestions overridden by users"
      type: "gauge"
  
  performance_metrics:
    - name: "guided_prompt_analysis_duration"
      description: "Time taken for query analysis"
      type: "histogram"
      buckets: [0.1, 0.2, 0.3, 0.4, 0.5]
    
    - name: "guided_prompt_cache_hit_rate"
      description: "Cache hit rate for query analysis"
      type: "gauge"
    
    - name: "guided_prompt_analysis_accuracy"
      description: "Accuracy of query analysis"
      type: "gauge"
  
  user_behavior_metrics:
    - name: "guided_prompt_user_satisfaction"
      description: "User satisfaction with guided prompts"
      type: "gauge"
    
    - name: "guided_prompt_feature_adoption"
      description: "Percentage of users who keep the feature enabled"
      type: "gauge"
    
    - name: "guided_prompt_query_quality_improvement"
      description: "Improvement in query quality metrics"
      type: "gauge"
```

### 2. A/B Testing Framework
```python
# A/B testing configuration
ab_testing_config = {
    "experiment_name": "guided_prompt_effectiveness",
    "variants": {
        "control": {
            "guided_prompt_enabled": False,
            "description": "No guided prompt confirmation"
        },
        "treatment": {
            "guided_prompt_enabled": True,
            "description": "Guided prompt confirmation enabled"
        }
    },
    "metrics": [
        "user_satisfaction",
        "query_quality_score",
        "click_through_rate",
        "session_duration",
        "return_user_rate"
    ],
    "success_criteria": {
        "user_satisfaction": 0.05,  # 5% improvement
        "query_quality_score": 0.10,  # 10% improvement
        "click_through_rate": 0.03   # 3% improvement
    }
}
```

## Future Enhancements (v2.1+)

### 1. Multi-Option Clarifications
```typescript
// Enhanced guided prompt with multiple options
interface MultiOptionGuidedPrompt {
  originalQuery: string;
  options: Array<{
    id: string;
    refinedQuery: string;
    confidence: number;
    reasoning: string;
    suggestedLane: QueryLane;
  }>;
  onSelect: (optionId: string) => void;
  onEdit: (query: string) => void;
  onDisable: () => void;
}
```

### 2. Domain-Aware Refinement
```python
# Domain-aware refinement configuration
domain_refinement_config = {
    "finance": {
        "triggers": ["stock", "price", "market", "trading", "portfolio"],
        "refinement_prompt": "Refine this financial query with specific stock symbols, timeframes, and data requirements.",
        "structured_output": True
    },
    "research": {
        "triggers": ["research", "study", "analysis", "investigate", "explore"],
        "refinement_prompt": "Expand this research query with specific sources, methodologies, and scope requirements.",
        "rag_expansion": True
    },
    "technical": {
        "triggers": ["code", "programming", "algorithm", "system", "architecture"],
        "refinement_prompt": "Refine this technical query with specific technologies, frameworks, and implementation details.",
        "code_examples": True
    }
}
```

### 3. Auto-Teach Mode
```typescript
// Auto-teach mode component
const AutoTeachTooltip: React.FC = {
  show: boolean;
  originalQuery: string;
  refinedQuery: string;
  onDismiss: () => void;
} = ({ show, originalQuery, refinedQuery, onDismiss }) => {
  if (!show) return null;

  return (
    <div className="auto-teach-tooltip">
      <h4>💡 Pro Tip</h4>
      <p>
        Instead of "{originalQuery}", try being more specific: "{refinedQuery}"
      </p>
      <p>
        This helps the AI provide more accurate and relevant answers.
      </p>
      <button onClick={onDismiss}>Got it!</button>
    </div>
  );
};
```

## Implementation Checklist

### 1. Backend Implementation
- [ ] Create Prompt Refinement Service
- [ ] Implement lightweight LLM integration
- [ ] Add caching layer for analysis results
- [ ] Implement parallel processing with orchestrator
- [ ] Add comprehensive error handling and fallbacks
- [ ] Integrate with existing observability framework

### 2. Frontend Implementation
- [ ] Create GuidedPromptModal component
- [ ] Implement query input integration
- [ ] Add settings page toggle
- [ ] Implement responsive design for mobile/desktop
- [ ] Add accessibility features (ARIA labels, keyboard navigation)
- [ ] Integrate with existing Cosmic Pro design system

### 3. Testing and Validation
- [ ] Unit tests for analysis logic
- [ ] Integration tests for modal workflow
- [ ] Performance tests for time budgets
- [ ] A/B testing framework setup
- [ ] User acceptance testing
- [ ] Accessibility testing

### 4. Observability and Monitoring
- [ ] Add metrics collection
- [ ] Implement dashboards for guided prompt usage
- [ ] Set up alerting for performance issues
- [ ] Create user behavior analytics
- [ ] Implement A/B testing metrics

---

## Appendix

### A. Component Specifications
- `GuidedPromptModal.tsx` - Main confirmation modal component
- `QueryInput.tsx` - Enhanced query input with guidance integration
- `SettingsPage.tsx` - Settings page with toggle control
- `AutoTeachTooltip.tsx` - Educational tooltip component

### B. Service Specifications
- `PromptRefinementService.py` - Backend analysis service
- `GuidedPromptMetrics.py` - Metrics collection service
- `ABTestingService.py` - A/B testing framework

### C. Configuration Files
- `guided_prompt_config.yaml` - Feature configuration
- `ab_testing_config.yaml` - A/B testing configuration
- `metrics_config.yaml` - Metrics collection configuration
