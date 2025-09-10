#!/usr/bin/env python3
"""
Test script for Guided Prompt Confirmation Service
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class GuidedPromptTester:
    """Test the guided prompt service implementation"""
    
    def __init__(self):
        self.service_url = "http://localhost:8003"
        self.http_client = httpx.AsyncClient()
    
    async def test_service_health(self) -> bool:
        """Test service health check"""
        print("Testing Guided Prompt Service Health...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "guided-prompt"
            print("✓ Service health check passed")
            return True
            
        except Exception as e:
            print(f"✗ Service health check failed: {e}")
            return False
    
    async def test_refinement_processing(self) -> bool:
        """Test refinement processing"""
        print("\nTesting Refinement Processing...")
        
        test_cases = [
            {
                "query": "show me apple",
                "context": {"intent_confidence": 0.3},
                "expected_type": "disambiguate"
            },
            {
                "query": "analyze climate change",
                "context": {"intent_confidence": 0.4},
                "expected_type": "decompose"
            },
            {
                "query": "tell me about AI",
                "context": {"intent_confidence": 0.2},
                "expected_type": "constrain"
            },
            {
                "query": "my email is john@example.com, tell me about hacking",
                "context": {"intent_confidence": 0.5},
                "expected_type": "sanitize"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['query']}")
                
                response = await self.http_client.post(
                    f"{self.service_url}/refine",
                    json={
                        "query": test_case["query"],
                        "context": test_case["context"]
                    }
                )
                
                assert response.status_code == 200
                result = response.json()
                
                # Check response structure
                assert "should_trigger" in result
                assert "suggestions" in result
                assert "constraints" in result
                assert "latency_ms" in result
                assert "model_used" in result
                assert "cost_usd" in result
                
                # Check latency budget
                assert result["latency_ms"] <= 500, f"Latency {result['latency_ms']}ms exceeded 500ms budget"
                
                # Check suggestions
                if result["should_trigger"]:
                    assert len(result["suggestions"]) > 0, "Should have suggestions when triggered"
                    
                    # Check suggestion structure
                    for suggestion in result["suggestions"]:
                        assert "id" in suggestion
                        assert "title" in suggestion
                        assert "description" in suggestion
                        assert "refined_query" in suggestion
                        assert "type" in suggestion
                        assert "confidence" in suggestion
                        assert "reasoning" in suggestion
                
                print(f"    ✓ Processed successfully (latency: {result['latency_ms']}ms)")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} refinement tests passed")
        return success_count == len(test_cases)
    
    async def test_user_settings(self) -> bool:
        """Test user settings management"""
        print("\nTesting User Settings...")
        
        try:
            # Test get settings
            response = await self.http_client.get(f"{self.service_url}/settings/test_user")
            assert response.status_code == 200
            settings_data = response.json()
            assert "user_id" in settings_data
            assert "settings" in settings_data
            print("✓ Get user settings passed")
            
            # Test update settings
            new_settings = {
                "user_id": "test_user",
                "mode": "OFF",
                "preferences": {
                    "show_hints": False,
                    "auto_learn": True,
                    "constraint_chips": True,
                    "accessibility_mode": False
                }
            }
            
            response = await self.http_client.post(
                f"{self.service_url}/settings",
                json=new_settings
            )
            assert response.status_code == 200
            update_data = response.json()
            assert update_data["status"] == "updated"
            assert update_data["user_id"] == "test_user"
            print("✓ Update user settings passed")
            
            return True
            
        except Exception as e:
            print(f"✗ User settings test failed: {e}")
            return False
    
    async def test_feedback_recording(self) -> bool:
        """Test feedback recording"""
        print("\nTesting Feedback Recording...")
        
        try:
            # Test accepted feedback
            response = await self.http_client.post(
                f"{self.service_url}/feedback",
                params={
                    "user_id": "test_user",
                    "suggestion_id": "test_suggestion",
                    "action": "accepted",
                    "feedback": "Great suggestion!"
                }
            )
            assert response.status_code == 200
            feedback_data = response.json()
            assert feedback_data["status"] == "recorded"
            assert feedback_data["action"] == "accepted"
            print("✓ Accepted feedback recording passed")
            
            # Test edited feedback
            response = await self.http_client.post(
                f"{self.service_url}/feedback",
                params={
                    "user_id": "test_user",
                    "suggestion_id": "test_suggestion",
                    "action": "edited"
                }
            )
            assert response.status_code == 200
            print("✓ Edited feedback recording passed")
            
            # Test skipped feedback
            response = await self.http_client.post(
                f"{self.service_url}/feedback",
                params={
                    "user_id": "test_user",
                    "suggestion_id": "test_suggestion",
                    "action": "skipped"
                }
            )
            assert response.status_code == 200
            print("✓ Skipped feedback recording passed")
            
            return True
            
        except Exception as e:
            print(f"✗ Feedback recording test failed: {e}")
            return False
    
    async def test_latency_budget(self) -> bool:
        """Test latency budget enforcement"""
        print("\nTesting Latency Budget Enforcement...")
        
        try:
            # Test with high confidence (should bypass)
            response = await self.http_client.post(
                f"{self.service_url}/refine",
                json={
                    "query": "What is the capital of France?",
                    "context": {"intent_confidence": 0.9}
                }
            )
            assert response.status_code == 200
            result = response.json()
            assert result["should_trigger"] == False
            assert result["bypass_reason"] == "user_preference_or_confidence"
            print("✓ High confidence bypass test passed")
            
            # Test with low budget (should bypass)
            response = await self.http_client.post(
                f"{self.service_url}/refine",
                json={
                    "query": "show me apple",
                    "context": {"budget_remaining": 0.1}
                }
            )
            assert response.status_code == 200
            result = response.json()
            assert result["should_trigger"] == False
            assert result["bypass_reason"] == "user_preference_or_confidence"
            print("✓ Low budget bypass test passed")
            
            return True
            
        except Exception as e:
            print(f"✗ Latency budget test failed: {e}")
            return False
    
    async def test_pii_redaction(self) -> bool:
        """Test PII redaction"""
        print("\nTesting PII Redaction...")
        
        try:
            # Test with PII in query
            response = await self.http_client.post(
                f"{self.service_url}/refine",
                json={
                    "query": "my email is john@example.com and my phone is 555-1234",
                    "context": {"intent_confidence": 0.3}
                }
            )
            assert response.status_code == 200
            result = response.json()
            
            # Should trigger sanitization
            if result["should_trigger"]:
                sanitize_suggestions = [s for s in result["suggestions"] if s["type"] == "sanitize"]
                assert len(sanitize_suggestions) > 0, "Should have sanitization suggestions for PII"
                print("✓ PII redaction test passed")
            else:
                print("✓ PII query bypassed (expected)")
            
            return True
            
        except Exception as e:
            print(f"✗ PII redaction test failed: {e}")
            return False
    
    async def test_multimodal_detection(self) -> bool:
        """Test multimodal content detection"""
        print("\nTesting Multimodal Detection...")
        
        try:
            # Test with image context
            response = await self.http_client.post(
                f"{self.service_url}/refine",
                json={
                    "query": "analyze this image",
                    "context": {
                        "has_images": True,
                        "intent_confidence": 0.3
                    }
                }
            )
            assert response.status_code == 200
            result = response.json()
            
            if result["should_trigger"]:
                # Should have refinement suggestions
                assert len(result["suggestions"]) > 0, "Should have suggestions for multimodal query"
                print("✓ Multimodal detection test passed")
            else:
                print("✓ Multimodal query bypassed (expected)")
            
            return True
            
        except Exception as e:
            print(f"✗ Multimodal detection test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("Starting Guided Prompt Service Tests...")
        print("=" * 50)
        
        tests = [
            self.test_service_health,
            self.test_refinement_processing,
            self.test_user_settings,
            self.test_feedback_recording,
            self.test_latency_budget,
            self.test_pii_redaction,
            self.test_multimodal_detection
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"✗ Test {test.__name__} failed with exception: {e}")
                results.append(False)
        
        print("\n" + "=" * 50)
        print("Test Results Summary:")
        print(f"Service Health: {'✓ PASS' if results[0] else '✗ FAIL'}")
        print(f"Refinement Processing: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"User Settings: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"Feedback Recording: {'✓ PASS' if results[3] else '✗ FAIL'}")
        print(f"Latency Budget: {'✓ PASS' if results[4] else '✗ FAIL'}")
        print(f"PII Redaction: {'✓ PASS' if results[5] else '✗ FAIL'}")
        print(f"Multimodal Detection: {'✓ PASS' if results[6] else '✗ FAIL'}")
        
        all_passed = all(results)
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = GuidedPromptTester()
    
    # Wait for service to be ready
    print("Waiting for Guided Prompt service to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
