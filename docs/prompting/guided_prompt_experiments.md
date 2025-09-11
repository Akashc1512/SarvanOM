# Guided Prompt Experiments

**Date**: September 9, 2025  
**Status**: ✅ **ACTIVE EXPERIMENTS**  
**Purpose**: A/B & holdback design, success criteria, sample size heuristics, and rollout steps

---

## 🧪 **A/B & Holdback Design**

### **Experiment Overview**
The Guided Prompt Confirmation feature uses A/B testing and holdback experiments to measure impact and optimize performance.

### **Experiment Types**
| Experiment Type | Description | Duration | Sample Size | Purpose |
|----------------|-------------|----------|-------------|---------|
| **A/B Test** | Compare refinement vs no refinement | 2 weeks | 10,000 users | Measure overall impact |
| **Holdback** | 10% control sees no refinement | 4 weeks | 50,000 users | Measure long-term impact |
| **Feature Toggle** | Compare different refinement modes | 1 week | 5,000 users | Optimize refinement approach |
| **Model Comparison** | Compare different LLM models | 1 week | 3,000 users | Optimize model selection |

### **A/B Test Design**
```python
# Example A/B test design
class ABTestDesign:
    def __init__(self):
        self.experiments = {
            'guided_prompt_ab': {
                'name': 'Guided Prompt A/B Test',
                'description': 'Compare refinement vs no refinement',
                'variants': {
                    'control': {
                        'name': 'No Refinement',
                        'description': 'Users see no refinement suggestions',
                        'traffic_percentage': 50
                    },
                    'treatment': {
                        'name': 'With Refinement',
                        'description': 'Users see refinement suggestions',
                        'traffic_percentage': 50
                    }
                },
                'duration_days': 14,
                'success_metrics': [
                    'query_success_rate',
                    'user_satisfaction',
                    'query_quality_score',
                    'time_to_success'
                ],
                'guardrail_metrics': [
                    'query_latency',
                    'user_retention',
                    'complaint_rate'
                ]
            }
        }
    
    def assign_user_to_variant(self, user_id: str, experiment_name: str) -> str:
        """Assign user to experiment variant"""
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return 'control'
        
        # Use consistent hashing for user assignment
        hash_value = hash(f"{user_id}_{experiment_name}") % 100
        
        cumulative_percentage = 0
        for variant_name, variant_config in experiment['variants'].items():
            cumulative_percentage += variant_config['traffic_percentage']
            if hash_value < cumulative_percentage:
                return variant_name
        
        return 'control'  # Fallback
    
    def is_user_in_experiment(self, user_id: str, experiment_name: str) -> bool:
        """Check if user is in experiment"""
        variant = self.assign_user_to_variant(user_id, experiment_name)
        return variant != 'control'
    
    def get_user_variant(self, user_id: str, experiment_name: str) -> str:
        """Get user's experiment variant"""
        return self.assign_user_to_variant(user_id, experiment_name)
```

### **Holdback Design**
```python
# Example holdback design
class HoldbackDesign:
    def __init__(self):
        self.holdback_config = {
            'name': 'Guided Prompt Holdback',
            'description': '10% control sees no refinement',
            'control_percentage': 10,
            'treatment_percentage': 90,
            'duration_weeks': 4,
            'success_metrics': [
                'long_term_user_satisfaction',
                'user_retention_rate',
                'query_quality_improvement',
                'learning_rate'
            ],
            'guardrail_metrics': [
                'system_performance',
                'cost_per_user',
                'support_ticket_rate'
            ]
        }
    
    def assign_holdback_group(self, user_id: str) -> str:
        """Assign user to holdback group"""
        hash_value = hash(f"{user_id}_holdback") % 100
        
        if hash_value < self.holdback_config['control_percentage']:
            return 'control'
        else:
            return 'treatment'
    
    def is_control_user(self, user_id: str) -> bool:
        """Check if user is in control group"""
        return self.assign_holdback_group(user_id) == 'control'
    
    def get_holdback_status(self, user_id: str) -> Dict:
        """Get user's holdback status"""
        group = self.assign_holdback_group(user_id)
        return {
            'group': group,
            'is_control': group == 'control',
            'experiment_name': self.holdback_config['name'],
            'start_date': self.get_experiment_start_date(),
            'end_date': self.get_experiment_end_date()
        }
```

---

## 🎯 **Success Criteria**

### **Primary Success Metrics**
| Metric | Description | Target | Measurement Method | Statistical Significance |
|--------|-------------|--------|-------------------|------------------------|
| **Query Success Rate** | % of queries that succeed | +5% improvement | A/B test comparison | p < 0.05 |
| **User Satisfaction** | User satisfaction score | +0.5 point improvement | Survey responses | p < 0.05 |
| **Query Quality Score** | Quality of query results | +10% improvement | Automated quality scoring | p < 0.05 |
| **Time to Success** | Time to get successful result | -20% reduction | Time measurement | p < 0.05 |

### **Secondary Success Metrics**
| Metric | Description | Target | Measurement Method | Statistical Significance |
|--------|-------------|--------|-------------------|------------------------|
| **User Retention** | % of users returning | +3% improvement | User behavior tracking | p < 0.05 |
| **Learning Rate** | % of users improving over time | +15% improvement | Quality trend analysis | p < 0.05 |
| **Query Complexity** | Average query complexity | +20% increase | Complexity scoring | p < 0.05 |
| **Feature Adoption** | % of users keeping feature enabled | ≥ 70% | Feature toggle tracking | p < 0.05 |

### **Success Criteria Implementation**
```python
# Example success criteria implementation
class SuccessCriteria:
    def __init__(self):
        self.criteria = {
            'primary': {
                'query_success_rate': {
                    'target_improvement': 0.05,  # 5% improvement
                    'statistical_significance': 0.05,
                    'minimum_sample_size': 1000
                },
                'user_satisfaction': {
                    'target_improvement': 0.5,  # 0.5 point improvement
                    'statistical_significance': 0.05,
                    'minimum_sample_size': 500
                },
                'query_quality_score': {
                    'target_improvement': 0.10,  # 10% improvement
                    'statistical_significance': 0.05,
                    'minimum_sample_size': 1000
                },
                'time_to_success': {
                    'target_improvement': -0.20,  # 20% reduction
                    'statistical_significance': 0.05,
                    'minimum_sample_size': 1000
                }
            },
            'secondary': {
                'user_retention': {
                    'target_improvement': 0.03,  # 3% improvement
                    'statistical_significance': 0.05,
                    'minimum_sample_size': 2000
                },
                'learning_rate': {
                    'target_improvement': 0.15,  # 15% improvement
                    'statistical_significance': 0.05,
                    'minimum_sample_size': 1000
                }
            }
        }
    
    def evaluate_success(self, experiment_results: Dict) -> Dict:
        """Evaluate experiment success against criteria"""
        success_evaluation = {
            'overall_success': False,
            'primary_metrics': {},
            'secondary_metrics': {},
            'recommendation': 'continue_experiment'
        }
        
        # Evaluate primary metrics
        for metric_name, criteria in self.criteria['primary'].items():
            if metric_name in experiment_results:
                result = self.evaluate_metric(
                    experiment_results[metric_name],
                    criteria
                )
                success_evaluation['primary_metrics'][metric_name] = result
        
        # Evaluate secondary metrics
        for metric_name, criteria in self.criteria['secondary'].items():
            if metric_name in experiment_results:
                result = self.evaluate_metric(
                    experiment_results[metric_name],
                    criteria
                )
                success_evaluation['secondary_metrics'][metric_name] = result
        
        # Determine overall success
        primary_success = all(
            result['success'] for result in success_evaluation['primary_metrics'].values()
        )
        secondary_success = all(
            result['success'] for result in success_evaluation['secondary_metrics'].values()
        )
        
        success_evaluation['overall_success'] = primary_success and secondary_success
        
        # Generate recommendation
        if success_evaluation['overall_success']:
            success_evaluation['recommendation'] = 'promote_to_production'
        elif primary_success:
            success_evaluation['recommendation'] = 'continue_experiment'
        else:
            success_evaluation['recommendation'] = 'stop_experiment'
        
        return success_evaluation
    
    def evaluate_metric(self, metric_result: Dict, criteria: Dict) -> Dict:
        """Evaluate individual metric against criteria"""
        improvement = metric_result.get('improvement', 0)
        p_value = metric_result.get('p_value', 1.0)
        sample_size = metric_result.get('sample_size', 0)
        
        success = (
            improvement >= criteria['target_improvement'] and
            p_value < criteria['statistical_significance'] and
            sample_size >= criteria['minimum_sample_size']
        )
        
        return {
            'success': success,
            'improvement': improvement,
            'target': criteria['target_improvement'],
            'p_value': p_value,
            'sample_size': sample_size,
            'meets_target': improvement >= criteria['target_improvement'],
            'statistically_significant': p_value < criteria['statistical_significance'],
            'sufficient_sample': sample_size >= criteria['minimum_sample_size']
        }
```

---

## 📊 **Sample Size Heuristics**

### **Sample Size Calculation**
| Metric Type | Base Sample Size | Multiplier | Total Sample Size | Duration |
|-------------|------------------|------------|-------------------|----------|
| **Primary Metrics** | 1,000 users | 1.0 | 1,000 users | 2 weeks |
| **Secondary Metrics** | 2,000 users | 1.0 | 2,000 users | 4 weeks |
| **Long-term Impact** | 5,000 users | 1.0 | 5,000 users | 8 weeks |
| **Model Comparison** | 500 users | 1.0 | 500 users | 1 week |

### **Sample Size Calculator**
```python
# Example sample size calculator
import math
from typing import Dict, Tuple

class SampleSizeCalculator:
    def __init__(self):
        self.default_params = {
            'alpha': 0.05,  # Type I error rate
            'beta': 0.20,   # Type II error rate (80% power)
            'effect_size': 0.2,  # Cohen's d
            'baseline_rate': 0.5  # Baseline success rate
        }
    
    def calculate_sample_size(
        self,
        metric_type: str,
        effect_size: float = None,
        alpha: float = None,
        beta: float = None
    ) -> Dict:
        """Calculate required sample size for experiment"""
        
        # Use defaults if not provided
        effect_size = effect_size or self.default_params['effect_size']
        alpha = alpha or self.default_params['alpha']
        beta = beta or self.default_params['beta']
        
        # Calculate sample size based on metric type
        if metric_type == 'proportion':
            sample_size = self.calculate_proportion_sample_size(
                effect_size, alpha, beta
            )
        elif metric_type == 'continuous':
            sample_size = self.calculate_continuous_sample_size(
                effect_size, alpha, beta
            )
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")
        
        # Add safety margin (20%)
        sample_size_with_margin = int(sample_size * 1.2)
        
        return {
            'metric_type': metric_type,
            'effect_size': effect_size,
            'alpha': alpha,
            'beta': beta,
            'sample_size': sample_size,
            'sample_size_with_margin': sample_size_with_margin,
            'total_sample_size': sample_size_with_margin * 2,  # A/B test
            'duration_weeks': self.estimate_duration(sample_size_with_margin)
        }
    
    def calculate_proportion_sample_size(
        self,
        effect_size: float,
        alpha: float,
        beta: float
    ) -> int:
        """Calculate sample size for proportion metrics"""
        # Z-scores for alpha and beta
        z_alpha = self.get_z_score(1 - alpha/2)
        z_beta = self.get_z_score(1 - beta)
        
        # Sample size calculation for proportions
        p1 = self.default_params['baseline_rate']
        p2 = p1 + effect_size
        
        # Pooled proportion
        p_pooled = (p1 + p2) / 2
        
        # Sample size formula
        numerator = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
                    z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
        denominator = (p2 - p1)**2
        
        sample_size = numerator / denominator
        return int(math.ceil(sample_size))
    
    def calculate_continuous_sample_size(
        self,
        effect_size: float,
        alpha: float,
        beta: float
    ) -> int:
        """Calculate sample size for continuous metrics"""
        # Z-scores for alpha and beta
        z_alpha = self.get_z_score(1 - alpha/2)
        z_beta = self.get_z_score(1 - beta)
        
        # Sample size formula for continuous metrics
        sample_size = 2 * ((z_alpha + z_beta) / effect_size)**2
        return int(math.ceil(sample_size))
    
    def get_z_score(self, probability: float) -> float:
        """Get Z-score for given probability"""
        # Simplified Z-score calculation
        # In practice, use scipy.stats.norm.ppf
        z_scores = {
            0.95: 1.96,
            0.90: 1.64,
            0.80: 1.28,
            0.70: 1.04
        }
        return z_scores.get(probability, 1.96)
    
    def estimate_duration(self, sample_size: int) -> int:
        """Estimate experiment duration in weeks"""
        # Assume 1000 users per week
        weeks = math.ceil(sample_size / 1000)
        return max(1, weeks)  # Minimum 1 week
```

---

## 🚀 **Gradual Rollout & Rollback Steps**

### **Rollout Strategy**
| Phase | Traffic % | Duration | Success Criteria | Rollback Trigger |
|-------|-----------|----------|------------------|------------------|
| **Phase 1** | 1% | 1 week | No critical issues | Any critical issue |
| **Phase 2** | 5% | 1 week | Success rate ≥ 95% | Success rate < 90% |
| **Phase 3** | 25% | 2 weeks | All metrics green | Any metric red |
| **Phase 4** | 50% | 2 weeks | User satisfaction ≥ 4.0 | Satisfaction < 3.5 |
| **Phase 5** | 100% | Ongoing | All success criteria met | Any success criteria failed |

### **Rollout Implementation**
```python
# Example rollout implementation
class GradualRollout:
    def __init__(self):
        self.rollout_phases = {
            'phase_1': {
                'traffic_percentage': 1,
                'duration_days': 7,
                'success_criteria': {
                    'critical_issues': 0,
                    'success_rate': 0.95,
                    'user_satisfaction': 3.5
                },
                'rollback_triggers': ['critical_issues > 0']
            },
            'phase_2': {
                'traffic_percentage': 5,
                'duration_days': 7,
                'success_criteria': {
                    'success_rate': 0.95,
                    'user_satisfaction': 3.5,
                    'query_quality': 0.8
                },
                'rollback_triggers': ['success_rate < 0.90']
            },
            'phase_3': {
                'traffic_percentage': 25,
                'duration_days': 14,
                'success_criteria': {
                    'all_metrics_green': True,
                    'user_satisfaction': 4.0,
                    'retention_rate': 0.70
                },
                'rollback_triggers': ['any_metric_red']
            },
            'phase_4': {
                'traffic_percentage': 50,
                'duration_days': 14,
                'success_criteria': {
                    'user_satisfaction': 4.0,
                    'query_success_rate': 0.90,
                    'learning_rate': 0.15
                },
                'rollback_triggers': ['user_satisfaction < 3.5']
            },
            'phase_5': {
                'traffic_percentage': 100,
                'duration_days': 0,  # Ongoing
                'success_criteria': {
                    'all_success_criteria_met': True
                },
                'rollback_triggers': ['any_success_criteria_failed']
            }
        }
        
        self.current_phase = 'phase_1'
        self.phase_start_time = time.time()
    
    def get_traffic_percentage(self) -> int:
        """Get current traffic percentage"""
        phase_config = self.rollout_phases[self.current_phase]
        return phase_config['traffic_percentage']
    
    def should_user_get_feature(self, user_id: str) -> bool:
        """Check if user should get the feature"""
        traffic_percentage = self.get_traffic_percentage()
        
        # Use consistent hashing for user assignment
        hash_value = hash(f"{user_id}_rollout") % 100
        
        return hash_value < traffic_percentage
    
    def check_phase_completion(self) -> bool:
        """Check if current phase is complete"""
        phase_config = self.rollout_phases[self.current_phase]
        duration_days = phase_config['duration_days']
        
        if duration_days == 0:  # Ongoing phase
            return False
        
        elapsed_days = (time.time() - self.phase_start_time) / (24 * 3600)
        return elapsed_days >= duration_days
    
    def evaluate_phase_success(self, metrics: Dict) -> bool:
        """Evaluate if current phase meets success criteria"""
        phase_config = self.rollout_phases[self.current_phase]
        success_criteria = phase_config['success_criteria']
        
        for criterion, target in success_criteria.items():
            if criterion == 'all_metrics_green':
                if not self.all_metrics_green(metrics):
                    return False
            elif criterion == 'all_success_criteria_met':
                if not self.all_success_criteria_met(metrics):
                    return False
            else:
                if metrics.get(criterion, 0) < target:
                    return False
        
        return True
    
    def check_rollback_triggers(self, metrics: Dict) -> bool:
        """Check if rollback should be triggered"""
        phase_config = self.rollout_phases[self.current_phase]
        rollback_triggers = phase_config['rollback_triggers']
        
        for trigger in rollback_triggers:
            if self.evaluate_rollback_trigger(trigger, metrics):
                return True
        
        return False
    
    def evaluate_rollback_trigger(self, trigger: str, metrics: Dict) -> bool:
        """Evaluate individual rollback trigger"""
        if trigger == 'critical_issues > 0':
            return metrics.get('critical_issues', 0) > 0
        elif trigger == 'success_rate < 0.90':
            return metrics.get('success_rate', 1.0) < 0.90
        elif trigger == 'any_metric_red':
            return self.any_metric_red(metrics)
        elif trigger == 'user_satisfaction < 3.5':
            return metrics.get('user_satisfaction', 5.0) < 3.5
        elif trigger == 'any_success_criteria_failed':
            return not self.all_success_criteria_met(metrics)
        
        return False
    
    def advance_phase(self):
        """Advance to next rollout phase"""
        phase_order = ['phase_1', 'phase_2', 'phase_3', 'phase_4', 'phase_5']
        current_index = phase_order.index(self.current_phase)
        
        if current_index < len(phase_order) - 1:
            self.current_phase = phase_order[current_index + 1]
            self.phase_start_time = time.time()
    
    def rollback_phase(self):
        """Rollback to previous phase"""
        phase_order = ['phase_1', 'phase_2', 'phase_3', 'phase_4', 'phase_5']
        current_index = phase_order.index(self.current_phase)
        
        if current_index > 0:
            self.current_phase = phase_order[current_index - 1]
            self.phase_start_time = time.time()
    
    def all_metrics_green(self, metrics: Dict) -> bool:
        """Check if all metrics are green"""
        # Implementation depends on metric definitions
        return True  # Placeholder
    
    def any_metric_red(self, metrics: Dict) -> bool:
        """Check if any metric is red"""
        # Implementation depends on metric definitions
        return False  # Placeholder
    
    def all_success_criteria_met(self, metrics: Dict) -> bool:
        """Check if all success criteria are met"""
        # Implementation depends on success criteria definitions
        return True  # Placeholder
```

---

## 📚 **References**

- Overview: `docs/prompting/guided_prompt_overview.md`
- UX Flow: `docs/prompting/guided_prompt_ux_flow.md`
- Policy: `docs/prompting/guided_prompt_policy.md`
- Toggle Contract: `docs/prompting/guided_prompt_toggle_contract.md`
- LLM Policy: `docs/prompting/guided_prompt_llm_policy.md`
- Metrics: `docs/prompting/guided_prompt_metrics.md`
- Test Cases: `docs/prompting/guided_prompt_test_cases.md`
- Implementation Tracker: `SARVANOM_V2_IMPLEMENTATION_TRACKER.md`

---

*This experiments specification ensures rigorous testing and safe rollout of the Guided Prompt Confirmation feature.*
