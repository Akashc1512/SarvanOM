# Guided Prompt LLM Policy

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE POLICY**  
**Purpose**: Model class for refinement, prompt style guide, and cost guardrails

---

## 🤖 **Model Class for Refinement**

### **Model Selection Strategy**
The Guided Prompt Confirmation feature uses a tiered model selection approach:

1. **FAST & CHEAP**: Primary model for refinement (≤500ms budget)
2. **QUALITY**: Fallback model if FAST is unavailable
3. **LMM**: Specialized model for image-rich inputs

### **Model Classes**
| Class | Purpose | Latency Target | Cost Target | Use Case |
|-------|---------|----------------|-------------|----------|
| **FAST & CHEAP** | Primary refinement | ≤ 200ms | $0.001/query | Text-only queries |
| **QUALITY** | Fallback refinement | ≤ 400ms | $0.005/query | Complex text queries |
| **LMM** | Multimodal refinement | ≤ 500ms | $0.010/query | Image/video queries |

### **Model Selection Logic**
```python
# Example model selection logic
class RefinementModelSelector:
    def __init__(self):
        self.model_classes = {
            'FAST_CHEAP': {
                'models': ['gpt-3.5-turbo', 'claude-3-haiku', 'llama-3-8b'],
                'latency_target': 200,
                'cost_target': 0.001,
                'priority': 1
            },
            'QUALITY': {
                'models': ['gpt-4o-mini', 'claude-3-sonnet', 'llama-3-70b'],
                'latency_target': 400,
                'cost_target': 0.005,
                'priority': 2
            },
            'LMM': {
                'models': ['gpt-4o', 'claude-3-opus', 'llama-3-vision'],
                'latency_target': 500,
                'cost_target': 0.010,
                'priority': 3
            }
        }
    
    def select_model(self, query: str, attachments: list, budget_ms: int) -> str:
        """Select appropriate model for refinement"""
        # Check for multimodal content
        if self.has_multimodal_content(query, attachments):
            return self.select_lmm_model(budget_ms)
        
        # Check budget constraints
        if budget_ms >= 400:
            return self.select_quality_model(budget_ms)
        else:
            return self.select_fast_cheap_model(budget_ms)
    
    def select_fast_cheap_model(self, budget_ms: int) -> str:
        """Select fast and cheap model"""
        available_models = self.get_available_models('FAST_CHEAP')
        for model in available_models:
            if self.check_model_health(model) and self.check_budget(model, budget_ms):
                return model
        
        # Fallback to quality model if no fast models available
        return self.select_quality_model(budget_ms)
    
    def select_quality_model(self, budget_ms: int) -> str:
        """Select quality model"""
        available_models = self.get_available_models('QUALITY')
        for model in available_models:
            if self.check_model_health(model) and self.check_budget(model, budget_ms):
                return model
        
        # Fallback to fast model if no quality models available
        return self.select_fast_cheap_model(budget_ms)
    
    def select_lmm_model(self, budget_ms: int) -> str:
        """Select LMM model for multimodal content"""
        available_models = self.get_available_models('LMM')
        for model in available_models:
            if self.check_model_health(model) and self.check_budget(model, budget_ms):
                return model
        
        # Fallback to quality model if no LMM models available
        return self.select_quality_model(budget_ms)
```

---

## 📝 **Prompt Style Guide**

### **Refinement Prompt Principles**
1. **Neutral Tone**: No over-specifying or bias
2. **Terse Style**: Concise and direct
3. **Clear Options**: Present clear alternatives
4. **User-Centric**: Focus on user intent
5. **Educational**: Help users learn better prompting

### **Prompt Templates**
```python
# Example prompt templates
class RefinementPromptTemplates:
    def __init__(self):
        self.templates = {
            'disambiguate': """
            The user query "{query}" is ambiguous. Provide 2-3 specific alternatives that clarify the intent.
            
            Format as:
            1. [Specific option 1]
            2. [Specific option 2] 
            3. [Specific option 3]
            
            Keep options concise and neutral.
            """,
            
            'refine': """
            The user query "{query}" could be more specific. Suggest 2-3 improved versions that are clearer and more actionable.
            
            Format as:
            1. [Improved version 1]
            2. [Improved version 2]
            3. [Improved version 3]
            
            Focus on clarity and specificity.
            """,
            
            'decompose': """
            The user query "{query}" is complex and could be broken down. Suggest 2-3 focused sub-questions or approaches.
            
            Format as:
            1. [Focused approach 1]
            2. [Focused approach 2]
            3. [Focused approach 3]
            
            Make each option manageable and specific.
            """,
            
            'constrain': """
            The user query "{query}" is open-ended and could be expensive. Suggest 2-3 constrained versions with specific parameters.
            
            Format as:
            1. [Constrained version 1 with parameters]
            2. [Constrained version 2 with parameters]
            3. [Constrained version 3 with parameters]
            
            Include time, scope, or source constraints.
            """,
            
            'sanitize': """
            The user query "{query}" contains sensitive information. Provide a sanitized version that removes PII while preserving intent.
            
            Format as:
            1. [Sanitized version 1]
            2. [Sanitized version 2]
            3. [Sanitized version 3]
            
            Remove personal information but keep the core question.
            """
        }
    
    def get_template(self, refinement_type: str) -> str:
        """Get prompt template for refinement type"""
        return self.templates.get(refinement_type, self.templates['refine'])
    
    def format_prompt(self, refinement_type: str, query: str) -> str:
        """Format prompt with query"""
        template = self.get_template(refinement_type)
        return template.format(query=query)
```

### **Prompt Quality Guidelines**
```python
# Example prompt quality guidelines
class PromptQualityGuidelines:
    def __init__(self):
        self.guidelines = {
            'length': {
                'min_words': 5,
                'max_words': 20,
                'description': 'Keep suggestions concise'
            },
            'tone': {
                'style': 'neutral',
                'avoid': ['hype', 'marketing', 'over-specifying'],
                'description': 'Use neutral, helpful tone'
            },
            'clarity': {
                'specificity': 'high',
                'ambiguity': 'low',
                'description': 'Make suggestions clear and specific'
            },
            'relevance': {
                'context_aware': True,
                'user_intent': True,
                'description': 'Stay relevant to user intent'
            }
        }
    
    def validate_suggestion(self, suggestion: str) -> Dict:
        """Validate suggestion quality"""
        validation_result = {
            'valid': True,
            'issues': [],
            'score': 0.0
        }
        
        # Check length
        word_count = len(suggestion.split())
        if word_count < self.guidelines['length']['min_words']:
            validation_result['issues'].append('Too short')
        elif word_count > self.guidelines['length']['max_words']:
            validation_result['issues'].append('Too long')
        
        # Check tone
        if self.contains_hype_language(suggestion):
            validation_result['issues'].append('Contains hype language')
        
        # Check clarity
        if self.is_ambiguous(suggestion):
            validation_result['issues'].append('Still ambiguous')
        
        # Calculate score
        validation_result['score'] = self.calculate_quality_score(suggestion)
        validation_result['valid'] = len(validation_result['issues']) == 0
        
        return validation_result
    
    def contains_hype_language(self, text: str) -> bool:
        """Check for hype language"""
        hype_words = ['amazing', 'incredible', 'revolutionary', 'game-changing', 'mind-blowing']
        return any(word in text.lower() for word in hype_words)
    
    def is_ambiguous(self, text: str) -> bool:
        """Check if text is still ambiguous"""
        ambiguous_indicators = ['something', 'anything', 'whatever', 'some', 'any']
        return any(indicator in text.lower() for indicator in ambiguous_indicators)
    
    def calculate_quality_score(self, text: str) -> float:
        """Calculate quality score (0-1)"""
        score = 1.0
        
        # Deduct for issues
        if self.contains_hype_language(text):
            score -= 0.2
        
        if self.is_ambiguous(text):
            score -= 0.3
        
        # Check word count
        word_count = len(text.split())
        if word_count < 5 or word_count > 20:
            score -= 0.1
        
        return max(0.0, score)
```

---

## 💰 **Cost Guardrails**

### **Per-Refinement Token Cap**
| Model Class | Max Tokens | Cost Limit | Budget Impact |
|-------------|------------|------------|---------------|
| **FAST & CHEAP** | 100 tokens | $0.001 | 0.1% of daily budget |
| **QUALITY** | 200 tokens | $0.005 | 0.5% of daily budget |
| **LMM** | 300 tokens | $0.010 | 1.0% of daily budget |

### **Cost Monitoring**
```python
# Example cost monitoring implementation
class CostGuardrails:
    def __init__(self):
        self.daily_budget = 100.0  # $100 daily budget
        self.model_costs = {
            'gpt-3.5-turbo': 0.001,
            'gpt-4o-mini': 0.005,
            'gpt-4o': 0.010,
            'claude-3-haiku': 0.001,
            'claude-3-sonnet': 0.005,
            'claude-3-opus': 0.010
        }
        self.daily_usage = 0.0
        self.refinement_usage = 0.0
    
    def check_cost_limit(self, model: str, estimated_tokens: int) -> bool:
        """Check if request is within cost limits"""
        model_cost = self.model_costs.get(model, 0.010)
        estimated_cost = model_cost * (estimated_tokens / 1000)
        
        # Check daily budget
        if self.daily_usage + estimated_cost > self.daily_budget:
            return False
        
        # Check refinement budget (10% of daily budget)
        refinement_budget = self.daily_budget * 0.1
        if self.refinement_usage + estimated_cost > refinement_budget:
            return False
        
        return True
    
    def record_usage(self, model: str, actual_tokens: int):
        """Record actual usage"""
        model_cost = self.model_costs.get(model, 0.010)
        actual_cost = model_cost * (actual_tokens / 1000)
        
        self.daily_usage += actual_cost
        self.refinement_usage += actual_cost
    
    def get_remaining_budget(self) -> Dict:
        """Get remaining budget information"""
        return {
            'daily_remaining': self.daily_budget - self.daily_usage,
            'refinement_remaining': (self.daily_budget * 0.1) - self.refinement_usage,
            'daily_usage_percent': (self.daily_usage / self.daily_budget) * 100,
            'refinement_usage_percent': (self.refinement_usage / (self.daily_budget * 0.1)) * 100
        }
```

### **Budget Abort Rules**
```python
# Example budget abort rules
class BudgetAbortRules:
    def __init__(self):
        self.abort_thresholds = {
            'daily_budget': 0.95,  # Abort at 95% of daily budget
            'refinement_budget': 0.90,  # Abort at 90% of refinement budget
            'hourly_budget': 0.80,  # Abort at 80% of hourly budget
            'per_request_budget': 0.10  # Abort if single request > 10% of daily budget
        }
    
    def should_abort_refinement(self, estimated_cost: float) -> bool:
        """Check if refinement should be aborted due to budget constraints"""
        # Check daily budget
        if self.daily_usage >= self.daily_budget * self.abort_thresholds['daily_budget']:
            return True
        
        # Check refinement budget
        refinement_budget = self.daily_budget * 0.1
        if self.refinement_usage >= refinement_budget * self.abort_thresholds['refinement_budget']:
            return True
        
        # Check per-request budget
        if estimated_cost >= self.daily_budget * self.abort_thresholds['per_request_budget']:
            return True
        
        return False
    
    def get_abort_reason(self, estimated_cost: float) -> str:
        """Get reason for aborting refinement"""
        if self.daily_usage >= self.daily_budget * self.abort_thresholds['daily_budget']:
            return "Daily budget exceeded"
        
        refinement_budget = self.daily_budget * 0.1
        if self.refinement_usage >= refinement_budget * self.abort_thresholds['refinement_budget']:
            return "Refinement budget exceeded"
        
        if estimated_cost >= self.daily_budget * self.abort_thresholds['per_request_budget']:
            return "Per-request budget exceeded"
        
        return "Unknown reason"
```

---

## 🔄 **Provider Rotation Rules**

### **Provider Selection Strategy**
1. **Health Check**: Only use healthy providers
2. **Load Balancing**: Distribute requests across providers
3. **Failover**: Switch to backup providers on failure
4. **Cost Optimization**: Prefer cheaper providers when possible

### **Provider Rotation Implementation**
```python
# Example provider rotation implementation
class ProviderRotation:
    def __init__(self):
        self.providers = {
            'openai': {
                'models': ['gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-4o'],
                'health': True,
                'cost_multiplier': 1.0,
                'priority': 1
            },
            'anthropic': {
                'models': ['claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus'],
                'health': True,
                'cost_multiplier': 1.1,
                'priority': 2
            },
            'huggingface': {
                'models': ['llama-3-8b', 'llama-3-70b', 'llama-3-vision'],
                'health': True,
                'cost_multiplier': 0.5,
                'priority': 3
            }
        }
        self.usage_stats = {
            'openai': {'requests': 0, 'errors': 0, 'cost': 0.0},
            'anthropic': {'requests': 0, 'errors': 0, 'cost': 0.0},
            'huggingface': {'requests': 0, 'errors': 0, 'cost': 0.0}
        }
    
    def select_provider(self, model_class: str, budget_ms: int) -> str:
        """Select best provider for given model class and budget"""
        available_providers = self.get_available_providers(model_class)
        
        # Sort by priority and health
        sorted_providers = sorted(
            available_providers,
            key=lambda p: (self.providers[p]['priority'], self.providers[p]['cost_multiplier'])
        )
        
        for provider in sorted_providers:
            if self.check_provider_health(provider) and self.check_provider_budget(provider, budget_ms):
                return provider
        
        # Fallback to any available provider
        for provider in available_providers:
            if self.check_provider_health(provider):
                return provider
        
        raise Exception("No available providers")
    
    def get_available_providers(self, model_class: str) -> list:
        """Get providers that support the given model class"""
        available = []
        for provider, config in self.providers.items():
            if model_class in config['models']:
                available.append(provider)
        return available
    
    def check_provider_health(self, provider: str) -> bool:
        """Check if provider is healthy"""
        return self.providers[provider]['health']
    
    def check_provider_budget(self, provider: str, budget_ms: int) -> bool:
        """Check if provider can meet budget constraints"""
        # Check if provider has been used too much recently
        recent_usage = self.get_recent_usage(provider)
        if recent_usage > 100:  # Max 100 requests per hour
            return False
        
        return True
    
    def record_provider_usage(self, provider: str, success: bool, cost: float):
        """Record provider usage statistics"""
        if success:
            self.usage_stats[provider]['requests'] += 1
            self.usage_stats[provider]['cost'] += cost
        else:
            self.usage_stats[provider]['errors'] += 1
        
        # Update provider health based on error rate
        total_requests = self.usage_stats[provider]['requests'] + self.usage_stats[provider]['errors']
        if total_requests > 0:
            error_rate = self.usage_stats[provider]['errors'] / total_requests
            if error_rate > 0.1:  # 10% error rate threshold
                self.providers[provider]['health'] = False
```

---

## 📊 **Model Performance Monitoring**

### **Performance Metrics**
| Metric | Target | Alert Threshold | Action |
|--------|--------|-----------------|--------|
| **Latency** | ≤ 500ms | > 800ms | Switch to faster model |
| **Success Rate** | ≥ 95% | < 90% | Investigate model issues |
| **Cost per Query** | ≤ $0.005 | > $0.010 | Switch to cheaper model |
| **Quality Score** | ≥ 0.8 | < 0.7 | Tune prompts |

### **Performance Monitoring Implementation**
```python
# Example performance monitoring
class ModelPerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'latency': [],
            'success_rate': [],
            'cost_per_query': [],
            'quality_score': []
        }
        self.alerts = []
    
    def record_metric(self, metric_type: str, value: float, model: str):
        """Record performance metric"""
        self.metrics[metric_type].append({
            'value': value,
            'model': model,
            'timestamp': time.time()
        })
        
        # Check for alerts
        self.check_alerts(metric_type, value, model)
    
    def check_alerts(self, metric_type: str, value: float, model: str):
        """Check for performance alerts"""
        thresholds = {
            'latency': {'target': 500, 'alert': 800},
            'success_rate': {'target': 0.95, 'alert': 0.90},
            'cost_per_query': {'target': 0.005, 'alert': 0.010},
            'quality_score': {'target': 0.8, 'alert': 0.7}
        }
        
        threshold = thresholds.get(metric_type)
        if threshold and value > threshold['alert']:
            alert = {
                'type': metric_type,
                'value': value,
                'model': model,
                'threshold': threshold['alert'],
                'timestamp': time.time()
            }
            self.alerts.append(alert)
            self.send_alert(alert)
    
    def get_model_performance(self, model: str) -> Dict:
        """Get performance summary for a model"""
        model_metrics = {}
        for metric_type, values in self.metrics.items():
            model_values = [v for v in values if v['model'] == model]
            if model_values:
                model_metrics[metric_type] = {
                    'average': sum(v['value'] for v in model_values) / len(model_values),
                    'count': len(model_values),
                    'latest': model_values[-1]['value']
                }
        
        return model_metrics
    
    def send_alert(self, alert: Dict):
        """Send performance alert"""
        # Implementation for sending alerts (email, Slack, etc.)
        logger.warning(f"Performance alert: {alert}")
```

---

## 📚 **References**

- Overview: `docs/prompting/guided_prompt_overview.md`
- UX Flow: `docs/prompting/guided_prompt_ux_flow.md`
- Policy: `docs/prompting/guided_prompt_policy.md`
- Toggle Contract: `docs/prompting/guided_prompt_toggle_contract.md`
- Metrics: `docs/prompting/guided_prompt_metrics.md`
- Experiments: `docs/prompting/guided_prompt_experiments.md`
- Test Cases: `docs/prompting/guided_prompt_test_cases.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This LLM policy ensures cost-effective, high-quality, and performant Guided Prompt Confirmation across all model classes.*
