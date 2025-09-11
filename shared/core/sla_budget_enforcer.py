"""
SLA Budget Enforcer for SarvanOM
Enforces performance budgets and timeouts across all system components
"""

import os
import time
import yaml
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ComplexityTier(Enum):
    SIMPLE = "simple"
    TECHNICAL = "technical"
    RESEARCH = "research"
    MULTIMEDIA = "multimedia"

class LaneType(Enum):
    LLM = "llm"
    WEB = "web"
    VECTOR = "vector"
    KG = "kg"
    KEYWORD = "keyword"
    YOUTUBE = "youtube"
    FUSION = "fusion"
    ORCHESTRATOR = "orchestrator"

@dataclass
class BudgetConfig:
    """Configuration for budget enforcement"""
    response_time_limit: float
    ttfb_limit: float
    lane_budgets: Dict[str, float]
    orchestrator_reserve: float = 0.2
    tolerance: float = 0.1
    strict_mode: bool = False

@dataclass
class BudgetResult:
    """Result of budget calculation"""
    effective_timeout: float
    remaining_budget: float
    lane_budget: float
    global_remaining: float
    is_within_budget: bool
    warning_threshold: bool = False
    critical_threshold: bool = False

class SLABudgetEnforcer:
    """Enforces SLA budgets and timeouts across all system components"""
    
    def __init__(self, config_file: str = "sla_budget_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.budget_configs = self._initialize_budget_configs()
        self.active_budgets: Dict[str, BudgetConfig] = {}
        self.budget_usage: Dict[str, float] = {}
        
        # Load environment overrides
        self._load_env_overrides()
        
        logger.info("SLA Budget Enforcer initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'global_sla': {
                'response_time_limits': {
                    'simple': 5.0,
                    'technical': 7.0,
                    'research': 10.0,
                    'multimedia': 10.0
                },
                'ttfb_limits': {
                    'simple': 0.8,
                    'technical': 1.2,
                    'research': 1.5,
                    'multimedia': 2.0
                }
            },
            'lane_budgets': {
                'llm': {'budget_allocation': {'simple': 3.0, 'technical': 4.0, 'research': 4.5, 'multimedia': 4.0}},
                'web': {'budget_allocation': {'simple': 1.5, 'technical': 1.8, 'research': 2.0, 'multimedia': 2.0}},
                'vector': {'budget_allocation': {'simple': 0.6, 'technical': 0.7, 'research': 0.8, 'multimedia': 0.8}},
                'kg': {'budget_allocation': {'simple': 1.0, 'technical': 1.2, 'research': 1.5, 'multimedia': 1.5}},
                'keyword': {'budget_allocation': {'simple': 0.3, 'technical': 0.35, 'research': 0.4, 'multimedia': 0.4}},
                'youtube': {'budget_allocation': {'simple': 2.0, 'technical': 2.5, 'research': 3.0, 'multimedia': 3.0}},
                'fusion': {'budget_allocation': {'simple': 0.5, 'technical': 0.7, 'research': 1.0, 'multimedia': 1.0}},
                'orchestrator': {'budget_allocation': {'simple': 0.1, 'technical': 0.15, 'research': 0.2, 'multimedia': 0.2}}
            }
        }

    def _initialize_budget_configs(self) -> Dict[str, Dict[str, BudgetConfig]]:
        """Initialize budget configurations for all complexity tiers"""
        configs = {}
        
        for tier in ComplexityTier:
            tier_name = tier.value
            configs[tier_name] = {}
            
            # Get global limits
            response_time_limit = self.config['global_sla']['response_time_limits'][tier_name]
            ttfb_limit = self.config['global_sla']['ttfb_limits'][tier_name]
            
            # Get lane budgets
            lane_budgets = {}
            for lane_name, lane_config in self.config['lane_budgets'].items():
                lane_budgets[lane_name] = lane_config['budget_allocation'][tier_name]
            
            # Create budget config
            budget_config = BudgetConfig(
                response_time_limit=response_time_limit,
                ttfb_limit=ttfb_limit,
                lane_budgets=lane_budgets
            )
            
            configs[tier_name] = budget_config
        
        return configs

    def _load_env_overrides(self):
        """Load environment variable overrides"""
        if not self.config.get('global_sla', {}).get('env_overrides', {}).get('enabled', False):
            return
        
        prefix = self.config['global_sla']['env_overrides']['prefix']
        
        # Override response time limits
        for tier in ComplexityTier:
            tier_name = tier.value
            env_var = f"{prefix}{tier_name.upper()}_RESPONSE_TIME"
            if env_var in os.environ:
                try:
                    value = float(os.environ[env_var])
                    self.budget_configs[tier_name].response_time_limit = value
                    logger.info(f"Override: {tier_name} response time = {value}s")
                except ValueError:
                    logger.warning(f"Invalid value for {env_var}: {os.environ[env_var]}")
        
        # Override TTFB limits
        for tier in ComplexityTier:
            tier_name = tier.value
            env_var = f"{prefix}{tier_name.upper()}_TTFB"
            if env_var in os.environ:
                try:
                    value = float(os.environ[env_var])
                    self.budget_configs[tier_name].ttfb_limit = value
                    logger.info(f"Override: {tier_name} TTFB = {value}s")
                except ValueError:
                    logger.warning(f"Invalid value for {env_var}: {os.environ[env_var]}")

    def get_budget_config(self, complexity_tier: ComplexityTier) -> BudgetConfig:
        """Get budget configuration for a complexity tier"""
        return self.budget_configs[complexity_tier.value]

    def calculate_effective_timeout(self, 
                                  complexity_tier: ComplexityTier,
                                  lane_type: LaneType,
                                  global_remaining: float) -> BudgetResult:
        """Calculate effective timeout for a lane"""
        budget_config = self.get_budget_config(complexity_tier)
        lane_name = lane_type.value
        
        # Get lane budget
        lane_budget = budget_config.lane_budgets.get(lane_name, 0.0)
        
        # Calculate effective timeout using min(lane_budget, global_remaining)
        effective_timeout = min(lane_budget, global_remaining)
        
        # Calculate remaining budget
        remaining_budget = global_remaining - effective_timeout
        
        # Check thresholds
        warning_threshold = remaining_budget < (budget_config.response_time_limit * 0.2)
        critical_threshold = remaining_budget < (budget_config.response_time_limit * 0.05)
        
        # Check if within budget - must have sufficient global budget
        is_within_budget = effective_timeout <= lane_budget and global_remaining > 0
        
        return BudgetResult(
            effective_timeout=effective_timeout,
            remaining_budget=remaining_budget,
            lane_budget=lane_budget,
            global_remaining=global_remaining,
            is_within_budget=is_within_budget,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )

    def start_budget_tracking(self, request_id: str, complexity_tier: ComplexityTier):
        """Start tracking budget for a request"""
        budget_config = self.get_budget_config(complexity_tier)
        self.active_budgets[request_id] = budget_config
        self.budget_usage[request_id] = 0.0
        
        logger.debug(f"Started budget tracking for {request_id} with {complexity_tier.value} tier")

    def update_budget_usage(self, request_id: str, lane_type: LaneType, usage_time: float):
        """Update budget usage for a lane"""
        if request_id not in self.active_budgets:
            logger.warning(f"No active budget for request {request_id}")
            return
        
        self.budget_usage[request_id] += usage_time
        
        # Check if budget exceeded
        budget_config = self.active_budgets[request_id]
        if self.budget_usage[request_id] > budget_config.response_time_limit:
            logger.warning(f"Budget exceeded for {request_id}: {self.budget_usage[request_id]:.2f}s > {budget_config.response_time_limit}s")

    def get_remaining_budget(self, request_id: str) -> float:
        """Get remaining budget for a request"""
        if request_id not in self.active_budgets:
            return 0.0
        
        budget_config = self.active_budgets[request_id]
        used_budget = self.budget_usage.get(request_id, 0.0)
        return max(0.0, budget_config.response_time_limit - used_budget)

    def end_budget_tracking(self, request_id: str) -> Dict[str, Any]:
        """End budget tracking and return summary"""
        if request_id not in self.active_budgets:
            return {}
        
        budget_config = self.active_budgets[request_id]
        used_budget = self.budget_usage.get(request_id, 0.0)
        
        summary = {
            'request_id': request_id,
            'total_budget': budget_config.response_time_limit,
            'used_budget': used_budget,
            'remaining_budget': budget_config.response_time_limit - used_budget,
            'budget_utilization': used_budget / budget_config.response_time_limit,
            'within_budget': used_budget <= budget_config.response_time_limit,
            'ttfb_limit': budget_config.ttfb_limit
        }
        
        # Clean up
        del self.active_budgets[request_id]
        del self.budget_usage[request_id]
        
        return summary

    def assert_budget_compliance(self, 
                               complexity_tier: ComplexityTier,
                               lane_type: LaneType,
                               actual_time: float,
                               ttfb_time: float = None) -> bool:
        """Assert budget compliance for a lane"""
        budget_config = self.get_budget_config(complexity_tier)
        lane_name = lane_type.value
        
        # Check lane budget
        lane_budget = budget_config.lane_budgets.get(lane_name, 0.0)
        tolerance = budget_config.tolerance if not budget_config.strict_mode else 0.0
        
        # Assert lane budget compliance
        if actual_time > (lane_budget + tolerance):
            error_msg = f"Lane budget exceeded: {lane_name} took {actual_time:.2f}s, budget: {lane_budget:.2f}s"
            logger.warning(error_msg)
            if budget_config.strict_mode:
                raise AssertionError(error_msg)
            return False
        
        # Assert TTFB compliance if provided
        if ttfb_time is not None:
            if ttfb_time > (budget_config.ttfb_limit + tolerance):
                error_msg = f"TTFB budget exceeded: {ttfb_time:.2f}s, budget: {budget_config.ttfb_limit:.2f}s"
                logger.warning(error_msg)
                if budget_config.strict_mode:
                    raise AssertionError(error_msg)
                return False
        
        return True

    @asynccontextmanager
    async def budget_context(self, 
                           request_id: str,
                           complexity_tier: ComplexityTier,
                           lane_type: LaneType):
        """Context manager for budget tracking"""
        start_time = time.time()
        ttfb_time = None
        
        try:
            # Start budget tracking
            self.start_budget_tracking(request_id, complexity_tier)
            
            # Calculate effective timeout
            global_remaining = self.get_remaining_budget(request_id)
            budget_result = self.calculate_effective_timeout(complexity_tier, lane_type, global_remaining)
            
            # Log budget allocation
            logger.debug(f"Budget allocated: {lane_type.value} = {budget_result.effective_timeout:.2f}s")
            
            yield budget_result
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout exceeded for {lane_type.value} in request {request_id}")
            raise
        except Exception as e:
            logger.error(f"Error in budget context for {lane_type.value}: {e}")
            raise
        finally:
            # Update budget usage
            end_time = time.time()
            usage_time = end_time - start_time
            self.update_budget_usage(request_id, lane_type, usage_time)
            
            # Assert budget compliance
            try:
                self.assert_budget_compliance(complexity_tier, lane_type, usage_time, ttfb_time)
            except AssertionError as e:
                logger.error(f"Budget assertion failed: {e}")
                raise

    def get_budget_summary(self) -> Dict[str, Any]:
        """Get summary of all active budgets"""
        summary = {
            'active_requests': len(self.active_budgets),
            'total_budget_usage': sum(self.budget_usage.values()),
            'requests': []
        }
        
        for request_id, budget_config in self.active_budgets.items():
            used_budget = self.budget_usage.get(request_id, 0.0)
            summary['requests'].append({
                'request_id': request_id,
                'total_budget': budget_config.response_time_limit,
                'used_budget': used_budget,
                'remaining_budget': budget_config.response_time_limit - used_budget,
                'utilization_percent': (used_budget / budget_config.response_time_limit) * 100
            })
        
        return summary

# Global instance
budget_enforcer = SLABudgetEnforcer()

# Convenience functions
def get_effective_timeout(complexity_tier: ComplexityTier, lane_type: LaneType, global_remaining: float) -> BudgetResult:
    """Get effective timeout for a lane"""
    return budget_enforcer.calculate_effective_timeout(complexity_tier, lane_type, global_remaining)

def assert_budget_compliance(complexity_tier: ComplexityTier, lane_type: LaneType, actual_time: float, ttfb_time: float = None) -> bool:
    """Assert budget compliance for a lane"""
    return budget_enforcer.assert_budget_compliance(complexity_tier, lane_type, actual_time, ttfb_time)

async def budget_context(request_id: str, complexity_tier: ComplexityTier, lane_type: LaneType):
    """Budget context manager"""
    return budget_enforcer.budget_context(request_id, complexity_tier, lane_type)
