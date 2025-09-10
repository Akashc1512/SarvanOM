#!/usr/bin/env python3
"""
Test script for Security & Privacy Enforcement Service
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class SecurityTester:
    """Test the security service implementation"""
    
    def __init__(self):
        self.service_url = "http://localhost:8007"
        self.http_client = httpx.AsyncClient()
    
    async def test_service_health(self) -> bool:
        """Test service health check"""
        print("Testing Security Service Health...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "security"
            print("✓ Service health check passed")
            return True
            
        except Exception as e:
            print(f"✗ Service health check failed: {e}")
            return False
    
    async def test_data_classification(self) -> bool:
        """Test data classification functionality"""
        print("\nTesting Data Classification...")
        
        test_cases = [
            {
                "name": "Public data",
                "data": {
                    "timestamp": "2025-09-09T12:00:00Z",
                    "version": "2.0.0",
                    "query": "What is the weather today?"
                }
            },
            {
                "name": "Internal data",
                "data": {
                    "query": "What is the weather today?",
                    "response": "The weather is sunny",
                    "user_id": "user123"
                }
            },
            {
                "name": "Confidential data",
                "data": {
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0...",
                    "session_id": "sess_abc123"
                }
            },
            {
                "name": "Restricted data with PII",
                "data": {
                    "email": "user@example.com",
                    "phone": "555-123-4567",
                    "name": "John Doe",
                    "ssn": "123-45-6789"
                }
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['name']}")
                
                response = await self.http_client.post(
                    f"{self.service_url}/classify-data",
                    json={"data": test_case["data"]}
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "classification" in result
                
                classification = result["classification"]
                assert "overall_classification" in classification
                assert "field_classifications" in classification
                assert "pii_detected" in classification
                assert "recommendations" in classification
                
                print(f"    ✓ Data classified as {classification['overall_classification']}")
                if classification["pii_detected"]:
                    print(f"    ✓ {len(classification['pii_detected'])} PII items detected")
                
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} data classification tests passed")
        return success_count == len(test_cases)
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        print("\nTesting Rate Limiting...")
        
        test_cases = [
            {
                "identifier": "test_user_1",
                "tier": "anonymous",
                "expected_limit": 10
            },
            {
                "identifier": "test_user_2",
                "tier": "authenticated",
                "expected_limit": 60
            },
            {
                "identifier": "test_user_3",
                "tier": "premium",
                "expected_limit": 120
            },
            {
                "identifier": "test_user_4",
                "tier": "enterprise",
                "expected_limit": 300
            },
            {
                "identifier": "test_user_5",
                "tier": "api",
                "expected_limit": 1000
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['tier']} tier")
                
                response = await self.http_client.post(
                    f"{self.service_url}/check-rate-limit",
                    json={
                        "identifier": test_case["identifier"],
                        "tier": test_case["tier"]
                    }
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "rate_limit" in result
                
                rate_limit = result["rate_limit"]
                assert "allowed" in rate_limit
                assert "limit" in rate_limit
                assert "remaining" in rate_limit
                assert "tier" in rate_limit
                
                assert rate_limit["tier"] == test_case["tier"]
                assert rate_limit["limit"] == test_case["expected_limit"]
                assert rate_limit["allowed"] == True
                
                print(f"    ✓ Rate limit check passed for {test_case['tier']} tier")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} rate limiting tests passed")
        return success_count == len(test_cases)
    
    async def test_user_agent_analysis(self) -> bool:
        """Test user agent analysis functionality"""
        print("\nTesting User Agent Analysis...")
        
        test_cases = [
            {
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "expected_type": "browser",
                "expected_action": "allow"
            },
            {
                "user_agent": "Googlebot/2.1 (+http://www.google.com/bot.html)",
                "expected_type": "bot",
                "expected_action": "rate_limit"
            },
            {
                "user_agent": "curl/7.68.0",
                "expected_type": "bot",
                "expected_action": "rate_limit"
            },
            {
                "user_agent": "",
                "expected_type": "empty",
                "expected_action": "block"
            },
            {
                "user_agent": "Mozilla",
                "expected_type": "suspicious",
                "expected_action": "block"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['user_agent'][:50]}...")
                
                response = await self.http_client.post(
                    f"{self.service_url}/analyze-user-agent",
                    json={"user_agent": test_case["user_agent"]}
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "analysis" in result
                
                analysis = result["analysis"]
                assert "type" in analysis
                assert "action" in analysis
                assert "risk_score" in analysis
                assert "reason" in analysis
                
                assert analysis["type"] == test_case["expected_type"]
                assert analysis["action"] == test_case["expected_action"]
                
                print(f"    ✓ User agent analyzed as {analysis['type']} with action {analysis['action']}")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} user agent analysis tests passed")
        return success_count == len(test_cases)
    
    async def test_consent_management(self) -> bool:
        """Test consent management functionality"""
        print("\nTesting Consent Management...")
        
        test_user_id = "test_consent_user"
        consent_types = [
            "raw_draft_storage",
            "refined_prompt_storage",
            "analytics_tracking",
            "personalization",
            "marketing"
        ]
        
        success_count = 0
        
        try:
            # Test setting consent
            for consent_type in consent_types:
                response = await self.http_client.post(
                    f"{self.service_url}/consent/set",
                    json={
                        "user_id": test_user_id,
                        "consent_type": consent_type,
                        "granted": True
                    }
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert result["granted"] == True
            
            print("    ✓ Consent setting tests passed")
            success_count += 1
            
            # Test checking consent
            for consent_type in consent_types:
                response = await self.http_client.post(
                    f"{self.service_url}/consent/check",
                    params={
                        "user_id": test_user_id,
                        "consent_type": consent_type
                    }
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert result["granted"] == True
            
            print("    ✓ Consent checking tests passed")
            success_count += 1
            
            # Test getting all consents
            response = await self.http_client.get(f"{self.service_url}/consent/all/{test_user_id}")
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "consents" in result
            
            consents = result["consents"]
            for consent_type in consent_types:
                assert consent_type in consents
                assert consents[consent_type] == True
            
            print("    ✓ Get all consents test passed")
            success_count += 1
            
        except Exception as e:
            print(f"    ✗ Consent management test failed: {e}")
        
        print(f"✓ {success_count}/3 consent management tests passed")
        return success_count == 3
    
    async def test_security_headers(self) -> bool:
        """Test security headers functionality"""
        print("\nTesting Security Headers...")
        
        try:
            response = await self.http_client.get(f"{self.service_url}/security-headers")
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "headers" in result
            
            headers = result["headers"]
            required_headers = [
                "csp", "hsts", "x_frame_options", "x_content_type_options",
                "referrer_policy", "permissions_policy"
            ]
            
            for header in required_headers:
                assert header in headers
                assert headers[header] is not None
                assert len(headers[header]) > 0
            
            print("    ✓ All required security headers present")
            print("    ✓ CSP header configured")
            print("    ✓ HSTS header configured")
            print("    ✓ Permissions-Policy configured for LMM flows")
            
            return True
            
        except Exception as e:
            print(f"✗ Security headers test failed: {e}")
            return False
    
    async def test_rate_limit_info(self) -> bool:
        """Test rate limit information functionality"""
        print("\nTesting Rate Limit Information...")
        
        test_cases = [
            {"identifier": "test_info_1", "tier": "anonymous"},
            {"identifier": "test_info_2", "tier": "authenticated"},
            {"identifier": "test_info_3", "tier": "premium"}
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['tier']} tier")
                
                response = await self.http_client.get(
                    f"{self.service_url}/rate-limit-info/{test_case['identifier']}",
                    params={"tier": test_case["tier"]}
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                assert "rate_limit_info" in result
                
                info = result["rate_limit_info"]
                required_fields = [
                    "tier", "minute_limit", "minute_used", "minute_remaining",
                    "hour_limit", "hour_used", "hour_remaining", "reset_time"
                ]
                
                for field in required_fields:
                    assert field in info
                
                assert info["tier"] == test_case["tier"]
                assert info["minute_limit"] > 0
                assert info["hour_limit"] > 0
                
                print(f"    ✓ Rate limit info retrieved for {test_case['tier']} tier")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} rate limit info tests passed")
        return success_count == len(test_cases)
    
    async def test_pii_detection(self) -> bool:
        """Test PII detection functionality"""
        print("\nTesting PII Detection...")
        
        test_cases = [
            {
                "name": "Email detection",
                "data": {"message": "Contact me at john.doe@example.com for more info"},
                "expected_pii": ["email"]
            },
            {
                "name": "Phone detection",
                "data": {"contact": "Call me at 555-123-4567"},
                "expected_pii": ["phone"]
            },
            {
                "name": "SSN detection",
                "data": {"ssn": "123-45-6789"},
                "expected_pii": ["ssn"]
            },
            {
                "name": "Credit card detection",
                "data": {"card": "4111 1111 1111 1111"},
                "expected_pii": ["credit_card"]
            },
            {
                "name": "Multiple PII",
                "data": {
                    "email": "user@example.com",
                    "phone": "555-123-4567",
                    "ssn": "123-45-6789"
                },
                "expected_pii": ["email", "phone", "ssn"]
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                print(f"  Test case {i+1}: {test_case['name']}")
                
                response = await self.http_client.post(
                    f"{self.service_url}/classify-data",
                    json={"data": test_case["data"]}
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["status"] == "success"
                
                classification = result["classification"]
                pii_detected = classification["pii_detected"]
                
                detected_types = [pii["pii_type"] for pii in pii_detected]
                
                for expected_pii in test_case["expected_pii"]:
                    assert expected_pii in detected_types, f"Expected {expected_pii} not detected"
                
                print(f"    ✓ {len(pii_detected)} PII items detected: {detected_types}")
                success_count += 1
                
            except Exception as e:
                print(f"    ✗ Test case {i+1} failed: {e}")
        
        print(f"✓ {success_count}/{len(test_cases)} PII detection tests passed")
        return success_count == len(test_cases)
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\nTesting Error Handling...")
        
        try:
            # Test invalid data classification
            response = await self.http_client.post(
                f"{self.service_url}/classify-data",
                json={"invalid": "data"}
            )
            assert response.status_code == 200  # Should still work with empty data
            print("    ✓ Invalid data classification handled correctly")
            
            # Test invalid rate limit request
            response = await self.http_client.post(
                f"{self.service_url}/check-rate-limit",
                json={"identifier": "test", "tier": "invalid_tier"}
            )
            assert response.status_code == 500  # Should return error for invalid tier
            print("    ✓ Invalid rate limit request handled correctly")
            
            # Test invalid user agent analysis
            response = await self.http_client.post(
                f"{self.service_url}/analyze-user-agent",
                json={"invalid": "data"}
            )
            assert response.status_code == 422  # Should return validation error
            print("    ✓ Invalid user agent analysis handled correctly")
            
            print("✓ Error handling tests passed")
            return True
            
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("Starting Security & Privacy Enforcement Service Tests...")
        print("=" * 60)
        
        tests = [
            self.test_service_health,
            self.test_data_classification,
            self.test_rate_limiting,
            self.test_user_agent_analysis,
            self.test_consent_management,
            self.test_security_headers,
            self.test_rate_limit_info,
            self.test_pii_detection,
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
        print(f"Data Classification: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"Rate Limiting: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"User Agent Analysis: {'✓ PASS' if results[3] else '✗ FAIL'}")
        print(f"Consent Management: {'✓ PASS' if results[4] else '✗ FAIL'}")
        print(f"Security Headers: {'✓ PASS' if results[5] else '✗ FAIL'}")
        print(f"Rate Limit Info: {'✓ PASS' if results[6] else '✗ FAIL'}")
        print(f"PII Detection: {'✓ PASS' if results[7] else '✗ FAIL'}")
        print(f"Error Handling: {'✓ PASS' if results[8] else '✗ FAIL'}")
        
        all_passed = all(results)
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = SecurityTester()
    
    # Wait for service to be ready
    print("Waiting for Security service to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
