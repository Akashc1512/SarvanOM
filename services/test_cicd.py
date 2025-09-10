#!/usr/bin/env python3
"""
Test script for CI/CD Gates & Quality Bars Service
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class CICDTester:
    """Test the CI/CD service implementation"""
    
    def __init__(self):
        self.service_url = "http://localhost:8008"
        self.http_client = httpx.AsyncClient()
    
    async def test_service_health(self) -> bool:
        """Test service health check"""
        print("Testing CI/CD Service Health...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "cicd"
            print("✓ Service health check passed")
            return True
            
        except Exception as e:
            print(f"✗ Service health check failed: {e}")
            return False
    
    async def test_quality_gates(self) -> bool:
        """Test quality gate functionality"""
        print("\nTesting Quality Gates...")
        
        test_cases = [
            {
                "name": "All gates check",
                "check_types": None
            },
            {
                "name": "Lint checks only",
                "check_types": ["lint"]
            },
            {
                "name": "Security checks only",
                "check_types": ["security"]
            },
            {
                "name": "Performance checks only",
                "check_types": ["performance"]
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['name']}")
                
                payload = {}
                if test_case["check_types"]:
                    payload["check_types"] = test_case["check_types"]
                
                response = await self.http_client.post(
                    f"{self.service_url}/gates/check",
                    json=payload
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "gates" in result
                assert "should_block_merge" in result
                assert "blocking_issues" in result
                
                gates = result["gates"]
                print(f"    ✓ {len(gates)} gates evaluated")
                print(f"    ✓ Merge blocked: {result['should_block_merge']}")
                
                if result["blocking_issues"]:
                    print(f"    ⚠️  Blocking issues: {len(result['blocking_issues'])}")
                
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} quality gate tests passed")
        return success_count == len(test_cases)
    
    async def test_deployment_management(self) -> bool:
        """Test deployment management functionality"""
        print("\nTesting Deployment Management...")
        
        test_version = f"test-{int(time.time())}"
        
        try:
            # Test start canary deployment
            print("  Test 1: Start canary deployment")
            response = await self.http_client.post(
                f"{self.service_url}/deployment/start-canary",
                json={
                    "environment": "staging",
                    "version": test_version
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "deployment" in result
            
            deployment = result["deployment"]
            assert deployment["environment"] == "staging"
            assert deployment["version"] == test_version
            assert deployment["status"] == "canary"
            assert deployment["canary_percentage"] == 5.0
            
            print("    ✓ Canary deployment started")
            
            # Test update canary percentage
            print("  Test 2: Update canary percentage")
            response = await self.http_client.post(
                f"{self.service_url}/deployment/update-canary",
                json={
                    "environment": "staging",
                    "version": test_version,
                    "percentage": 25.0
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert result["percentage"] == 25.0
            
            print("    ✓ Canary percentage updated")
            
            # Test get deployment status
            print("  Test 3: Get deployment status")
            response = await self.http_client.get(
                f"{self.service_url}/deployment/status/staging/{test_version}"
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "deployment" in result
            
            deployment = result["deployment"]
            assert deployment["canary_percentage"] == 25.0
            
            print("    ✓ Deployment status retrieved")
            
            # Test promote deployment
            print("  Test 4: Promote deployment")
            response = await self.http_client.post(
                f"{self.service_url}/deployment/promote",
                json={
                    "environment": "staging",
                    "version": test_version
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert result["action"] == "promoted"
            
            print("    ✓ Deployment promoted")
            
            # Test rollback deployment
            print("  Test 5: Rollback deployment")
            response = await self.http_client.post(
                f"{self.service_url}/deployment/rollback",
                json={
                    "environment": "staging",
                    "version": test_version,
                    "reason": "Test rollback"
                }
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert result["action"] == "rollback"
            assert result["reason"] == "Test rollback"
            
            print("    ✓ Deployment rolled back")
            
            print("✓ All deployment management tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Deployment management test failed: {e}")
            return False
    
    async def test_gate_thresholds(self) -> bool:
        """Test gate threshold management"""
        print("\nTesting Gate Thresholds...")
        
        try:
            # Test get thresholds
            print("  Test 1: Get gate thresholds")
            response = await self.http_client.get(f"{self.service_url}/gates/thresholds")
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "thresholds" in result
            
            thresholds = result["thresholds"]
            required_thresholds = [
                "ttfr_refine_p95", "accept_rate", "error_rate",
                "response_time_p95", "test_coverage", "lighthouse_score", "bundle_size"
            ]
            
            for threshold in required_thresholds:
                assert threshold in thresholds
                assert isinstance(thresholds[threshold], (int, float))
            
            print("    ✓ Gate thresholds retrieved")
            
            # Test update thresholds
            print("  Test 2: Update gate thresholds")
            new_thresholds = {
                "ttfr_refine_p95": 750.0,
                "accept_rate": 35.0
            }
            
            response = await self.http_client.post(
                f"{self.service_url}/gates/thresholds",
                json=new_thresholds
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "thresholds" in result
            
            updated_thresholds = result["thresholds"]
            assert updated_thresholds["ttfr_refine_p95"] == 750.0
            assert updated_thresholds["accept_rate"] == 35.0
            
            print("    ✓ Gate thresholds updated")
            
            print("✓ Gate threshold tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Gate threshold test failed: {e}")
            return False
    
    async def test_merge_blocking_logic(self) -> bool:
        """Test merge blocking logic"""
        print("\nTesting Merge Blocking Logic...")
        
        try:
            # Test with failing gates
            print("  Test 1: Check merge blocking with failing gates")
            
            # This would typically involve mocking failing checks
            # For now, we'll test the API structure
            response = await self.http_client.post(
                f"{self.service_url}/gates/check",
                json={"check_types": ["lint"]}
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "should_block_merge" in result
            assert "blocking_issues" in result
            
            # should_block_merge should be a boolean
            assert isinstance(result["should_block_merge"], bool)
            
            # blocking_issues should be a list
            assert isinstance(result["blocking_issues"], list)
            
            print("    ✓ Merge blocking logic validated")
            
            print("✓ Merge blocking logic tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Merge blocking logic test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\nTesting Error Handling...")
        
        try:
            # Test invalid deployment request
            print("  Test 1: Invalid deployment request")
            response = await self.http_client.post(
                f"{self.service_url}/deployment/start-canary",
                json={
                    "environment": "invalid",
                    "version": "test"
                }
            )
            
            # Should return 422 for validation error
            assert response.status_code == 422
            print("    ✓ Invalid deployment request handled correctly")
            
            # Test invalid gate check request
            print("  Test 2: Invalid gate check request")
            response = await self.http_client.post(
                f"{self.service_url}/gates/check",
                json={"check_types": ["invalid_check_type"]}
            )
            
            # Should return 422 for validation error
            assert response.status_code == 422
            print("    ✓ Invalid gate check request handled correctly")
            
            # Test non-existent deployment status
            print("  Test 3: Non-existent deployment status")
            response = await self.http_client.get(
                f"{self.service_url}/deployment/status/staging/nonexistent"
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "not_found"
            print("    ✓ Non-existent deployment handled correctly")
            
            print("✓ Error handling tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
    
    async def test_performance_checks(self) -> bool:
        """Test performance check functionality"""
        print("\nTesting Performance Checks...")
        
        try:
            # Test performance gate check
            print("  Test 1: Performance gate check")
            response = await self.http_client.post(
                f"{self.service_url}/gates/check",
                json={"check_types": ["performance"]}
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "gates" in result
            
            # Find performance gate
            performance_gate = None
            for gate in result["gates"]:
                if gate["check_type"] == "performance":
                    performance_gate = gate
                    break
            
            assert performance_gate is not None
            assert "current_value" in performance_gate
            assert "threshold" in performance_gate
            assert "status" in performance_gate
            
            print(f"    ✓ Performance gate evaluated: {performance_gate['status']}")
            print(f"    ✓ Current value: {performance_gate['current_value']}")
            print(f"    ✓ Threshold: {performance_gate['threshold']}")
            
            print("✓ Performance check tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Performance check test failed: {e}")
            return False
    
    async def test_accessibility_checks(self) -> bool:
        """Test accessibility check functionality"""
        print("\nTesting Accessibility Checks...")
        
        try:
            # Test accessibility gate check
            print("  Test 1: Accessibility gate check")
            response = await self.http_client.post(
                f"{self.service_url}/gates/check",
                json={"check_types": ["accessibility"]}
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "gates" in result
            
            # Find accessibility gate
            accessibility_gate = None
            for gate in result["gates"]:
                if gate["check_type"] == "accessibility":
                    accessibility_gate = gate
                    break
            
            assert accessibility_gate is not None
            assert "status" in accessibility_gate
            assert "message" in accessibility_gate
            
            print(f"    ✓ Accessibility gate evaluated: {accessibility_gate['status']}")
            print(f"    ✓ Message: {accessibility_gate['message']}")
            
            print("✓ Accessibility check tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Accessibility check test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("Starting CI/CD Gates & Quality Bars Service Tests...")
        print("=" * 60)
        
        tests = [
            self.test_service_health,
            self.test_quality_gates,
            self.test_deployment_management,
            self.test_gate_thresholds,
            self.test_merge_blocking_logic,
            self.test_performance_checks,
            self.test_accessibility_checks,
            self.test_error_handling
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                print(f"✗ Test {test.__name__} failed with exception: {e}")
                results.append(False)
        
        print("\n" + "=" * 60)
        print("Test Results Summary:")
        print(f"Service Health: {'✓ PASS' if results[0] else '✗ FAIL'}")
        print(f"Quality Gates: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"Deployment Management: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"Gate Thresholds: {'✓ PASS' if results[3] else '✗ FAIL'}")
        print(f"Merge Blocking Logic: {'✓ PASS' if results[4] else '✗ FAIL'}")
        print(f"Performance Checks: {'✓ PASS' if results[5] else '✗ FAIL'}")
        print(f"Accessibility Checks: {'✓ PASS' if results[6] else '✗ FAIL'}")
        print(f"Error Handling: {'✓ PASS' if results[7] else '✗ FAIL'}")
        
        all_passed = all(results)
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = CICDTester()
    
    # Wait for service to be ready
    print("Waiting for CI/CD service to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
