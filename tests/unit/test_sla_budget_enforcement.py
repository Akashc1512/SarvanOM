"""
Test SLA Budget Enforcement
Tests the budget enforcement system with real-time assertions
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from shared.core.sla_budget_enforcer import (
    SLABudgetEnforcer, 
    ComplexityTier, 
    LaneType, 
    BudgetResult,
    budget_enforcer
)

class TestSLABudgetEnforcement:
    """Test SLA budget enforcement functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.enforcer = SLABudgetEnforcer()
        self.request_id = "test_request_001"
    
    def test_budget_config_loading(self):
        """Test that budget configurations are loaded correctly"""
        # Test simple tier configuration
        simple_config = self.enforcer.get_budget_config(ComplexityTier.SIMPLE)
        assert simple_config.response_time_limit == 5.0
        assert simple_config.ttfb_limit == 0.8
        
        # Test technical tier configuration
        technical_config = self.enforcer.get_budget_config(ComplexityTier.TECHNICAL)
        assert technical_config.response_time_limit == 7.0
        assert technical_config.ttfb_limit == 1.2
        
        # Test research tier configuration
        research_config = self.enforcer.get_budget_config(ComplexityTier.RESEARCH)
        assert research_config.response_time_limit == 10.0
        assert research_config.ttfb_limit == 1.5
        
        # Test multimedia tier configuration
        multimedia_config = self.enforcer.get_budget_config(ComplexityTier.MULTIMEDIA)
        assert multimedia_config.response_time_limit == 10.0
        assert multimedia_config.ttfb_limit == 2.0
    
    def test_effective_timeout_calculation(self):
        """Test effective timeout calculation using min(lane_budget, global_remaining)"""
        # Test with sufficient global budget
        result = self.enforcer.calculate_effective_timeout(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            global_remaining=4.0
        )
        assert result.effective_timeout == 3.0  # min(3.0, 4.0)
        assert result.remaining_budget == 1.0
        assert result.is_within_budget == True
        
        # Test with limited global budget
        result = self.enforcer.calculate_effective_timeout(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            global_remaining=2.0
        )
        assert result.effective_timeout == 2.0  # min(3.0, 2.0)
        assert result.remaining_budget == 0.0
        assert result.is_within_budget == True
        
        # Test with no global budget
        result = self.enforcer.calculate_effective_timeout(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            global_remaining=0.0
        )
        assert result.effective_timeout == 0.0
        assert result.remaining_budget == 0.0
        assert result.is_within_budget == False
    
    def test_lane_budget_allocation(self):
        """Test lane budget allocation for different complexity tiers"""
        # Test simple tier lane budgets
        simple_config = self.enforcer.get_budget_config(ComplexityTier.SIMPLE)
        assert simple_config.lane_budgets["llm"] == 3.0
        assert simple_config.lane_budgets["web"] == 1.5
        assert simple_config.lane_budgets["vector"] == 0.6
        assert simple_config.lane_budgets["kg"] == 1.0
        assert simple_config.lane_budgets["keyword"] == 0.3
        assert simple_config.lane_budgets["youtube"] == 2.0
        assert simple_config.lane_budgets["fusion"] == 0.5
        assert simple_config.lane_budgets["orchestrator"] == 0.1
        
        # Test technical tier lane budgets
        technical_config = self.enforcer.get_budget_config(ComplexityTier.TECHNICAL)
        assert technical_config.lane_budgets["llm"] == 4.0
        assert technical_config.lane_budgets["web"] == 1.8
        assert technical_config.lane_budgets["vector"] == 0.7
        assert technical_config.lane_budgets["kg"] == 1.2
        assert technical_config.lane_budgets["keyword"] == 0.35
        assert technical_config.lane_budgets["youtube"] == 2.5
        assert technical_config.lane_budgets["fusion"] == 0.7
        assert technical_config.lane_budgets["orchestrator"] == 0.15
    
    def test_budget_tracking(self):
        """Test budget tracking for requests"""
        # Start budget tracking
        self.enforcer.start_budget_tracking(self.request_id, ComplexityTier.SIMPLE)
        
        # Update budget usage
        self.enforcer.update_budget_usage(self.request_id, LaneType.LLM, 2.0)
        self.enforcer.update_budget_usage(self.request_id, LaneType.WEB, 1.0)
        
        # Check remaining budget
        remaining = self.enforcer.get_remaining_budget(self.request_id)
        assert remaining == 2.0  # 5.0 - 2.0 - 1.0
        
        # End budget tracking
        summary = self.enforcer.end_budget_tracking(self.request_id)
        assert summary["total_budget"] == 5.0
        assert summary["used_budget"] == 3.0
        assert summary["remaining_budget"] == 2.0
        assert summary["budget_utilization"] == 0.6
        assert summary["within_budget"] == True
    
    def test_budget_assertions(self):
        """Test budget compliance assertions"""
        # Set strict mode for assertion tests
        config = self.enforcer.get_budget_config(ComplexityTier.SIMPLE)
        config.strict_mode = True
        
        # Test successful assertion
        assert self.enforcer.assert_budget_compliance(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            actual_time=2.5,
            ttfb_time=0.6
        ) == True
        
        # Test lane budget exceeded
        with pytest.raises(AssertionError):
            self.enforcer.assert_budget_compliance(
                ComplexityTier.SIMPLE, 
                LaneType.LLM, 
                actual_time=4.0,  # Exceeds 3.0 budget
                ttfb_time=0.6
            )
        
        # Test TTFB budget exceeded
        with pytest.raises(AssertionError):
            self.enforcer.assert_budget_compliance(
                ComplexityTier.SIMPLE, 
                LaneType.LLM, 
                actual_time=2.5,
                ttfb_time=1.0  # Exceeds 0.8 TTFB budget
            )
    
    def test_budget_assertions_tolerance(self):
        """Test budget assertions with tolerance"""
        # Test with tolerance (non-strict mode)
        config = self.enforcer.get_budget_config(ComplexityTier.SIMPLE)
        config.strict_mode = False
        config.tolerance = 0.1
        
        # Should pass with 10% tolerance
        assert self.enforcer.assert_budget_compliance(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            actual_time=3.05,  # 3.0 + 0.05 (within 10% tolerance)
            ttfb_time=0.6
        ) == True
        
        # Should fail with excessive tolerance
        assert self.enforcer.assert_budget_compliance(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            actual_time=4.0,  # 3.0 + 1.0 (exceeds 10% tolerance)
            ttfb_time=0.6
        ) == False
    
    @pytest.mark.asyncio
    async def test_budget_context_manager(self):
        """Test budget context manager"""
        async with self.enforcer.budget_context(
            self.request_id, 
            ComplexityTier.SIMPLE, 
            LaneType.LLM
        ) as budget_result:
            assert isinstance(budget_result, BudgetResult)
            assert budget_result.effective_timeout > 0
            assert budget_result.is_within_budget == True
            
            # Simulate some work
            await asyncio.sleep(0.1)
        
        # Check that budget was tracked
        summary = self.enforcer.end_budget_tracking(self.request_id)
        assert summary["used_budget"] > 0
    
    def test_environment_overrides(self):
        """Test environment variable overrides"""
        with patch.dict('os.environ', {
            'SARVANOM_SLA_SIMPLE_RESPONSE_TIME': '4.0',
            'SARVANOM_SLA_SIMPLE_TTFB': '0.6'
        }):
            # Create new enforcer to load env overrides
            enforcer = SLABudgetEnforcer()
            config = enforcer.get_budget_config(ComplexityTier.SIMPLE)
            
            assert config.response_time_limit == 4.0
            assert config.ttfb_limit == 0.6
    
    def test_budget_summary(self):
        """Test budget summary generation"""
        # Start multiple requests
        self.enforcer.start_budget_tracking("req1", ComplexityTier.SIMPLE)
        self.enforcer.start_budget_tracking("req2", ComplexityTier.TECHNICAL)
        
        # Update usage
        self.enforcer.update_budget_usage("req1", LaneType.LLM, 2.0)
        self.enforcer.update_budget_usage("req2", LaneType.LLM, 3.0)
        
        # Get summary
        summary = self.enforcer.get_budget_summary()
        assert summary["active_requests"] == 2
        assert summary["total_budget_usage"] == 5.0
        assert len(summary["requests"]) == 2
        
        # Clean up
        self.enforcer.end_budget_tracking("req1")
        self.enforcer.end_budget_tracking("req2")
    
    def test_warning_thresholds(self):
        """Test warning and critical thresholds"""
        # Test warning threshold (80% of budget)
        result = self.enforcer.calculate_effective_timeout(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            global_remaining=1.5  # 30% of 5.0 budget, remaining = 1.5 - 1.5 = 0.0
        )
        assert result.warning_threshold == True
        assert result.critical_threshold == True  # 0.0 < 0.25 (5% of 5.0)
        
        # Test warning threshold without critical
        result = self.enforcer.calculate_effective_timeout(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            global_remaining=4.0  # 80% of 5.0 budget, remaining = 4.0 - 3.0 = 1.0
        )
        assert result.warning_threshold == False  # 1.0 > 1.0 (20% of 5.0)
        assert result.critical_threshold == False  # 1.0 > 0.25 (5% of 5.0)
        
        # Test critical threshold (5% of budget)
        result = self.enforcer.calculate_effective_timeout(
            ComplexityTier.SIMPLE, 
            LaneType.LLM, 
            global_remaining=0.2  # 4% of 5.0 budget
        )
        assert result.warning_threshold == True
        assert result.critical_threshold == True
    
    def test_budget_exceeded_handling(self):
        """Test handling when budget is exceeded"""
        # Start tracking
        self.enforcer.start_budget_tracking(self.request_id, ComplexityTier.SIMPLE)
        
        # Exceed budget
        self.enforcer.update_budget_usage(self.request_id, LaneType.LLM, 6.0)  # Exceeds 5.0 limit
        
        # Check remaining budget
        remaining = self.enforcer.get_remaining_budget(self.request_id)
        assert remaining == 0.0  # Should not go negative
        
        # End tracking
        summary = self.enforcer.end_budget_tracking(self.request_id)
        assert summary["within_budget"] == False
        assert summary["budget_utilization"] > 1.0

class TestBudgetEnforcementIntegration:
    """Integration tests for budget enforcement"""
    
    @pytest.mark.asyncio
    async def test_real_request_budget_tracking(self):
        """Test budget tracking for a real request scenario"""
        enforcer = SLABudgetEnforcer()
        request_id = "integration_test_001"
        
        # Start tracking
        enforcer.start_budget_tracking(request_id, ComplexityTier.RESEARCH)
        
        # Simulate request processing with multiple lanes
        lanes = [
            (LaneType.ORCHESTRATOR, 0.1),
            (LaneType.WEB, 1.5),
            (LaneType.VECTOR, 0.6),
            (LaneType.LLM, 3.0),
            (LaneType.FUSION, 0.8)
        ]
        
        total_time = 0
        for lane, time_spent in lanes:
            enforcer.update_budget_usage(request_id, lane, time_spent)
            total_time += time_spent
        
        # Check final budget
        summary = enforcer.end_budget_tracking(request_id)
        assert summary["used_budget"] == total_time
        assert summary["within_budget"] == True
        assert summary["budget_utilization"] < 1.0
    
    def test_budget_enforcement_under_load(self):
        """Test budget enforcement under concurrent load"""
        enforcer = SLABudgetEnforcer()
        request_ids = [f"load_test_{i:03d}" for i in range(10)]
        
        # Start multiple requests
        for req_id in request_ids:
            enforcer.start_budget_tracking(req_id, ComplexityTier.SIMPLE)
        
        # Update budgets concurrently
        for req_id in request_ids:
            enforcer.update_budget_usage(req_id, LaneType.LLM, 2.0)
        
        # Check all requests
        summary = enforcer.get_budget_summary()
        assert summary["active_requests"] == 10
        assert summary["total_budget_usage"] == 20.0
        
        # Clean up
        for req_id in request_ids:
            enforcer.end_budget_tracking(req_id)

if __name__ == "__main__":
    pytest.main([__file__])
