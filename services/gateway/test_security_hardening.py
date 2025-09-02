#!/usr/bin/env python3
"""
Security Hardening Test Suite

Tests for enhanced security features:
- Rate limiting (60 RPM/IP with burst handling)
- HTML/markdown sanitization
- Security headers
- Input/output validation
- Injection attempt detection
- Security footer integration
"""

import asyncio
import json
import time
import httpx
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from services.gateway.main import app
from services.gateway.middleware.security_hardening import (
    SecurityHardeningMiddleware,
    SecurityHardeningConfig,
    ContentSanitizer,
    EnhancedRateLimiter
)

class SecurityTestClient:
    """Test client for security hardening features."""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = []
    
    async def test_rate_limiting(self) -> Dict[str, Any]:
        """Test 60 RPM rate limiting with burst handling."""
        print("🧪 Testing rate limiting...")
        
        results = {
            "test_name": "Rate Limiting",
            "success": False,
            "details": {}
        }
        
        try:
            # Test normal requests (should pass)
            normal_requests = []
            for i in range(5):
                response = self.client.get("/health")
                normal_requests.append(response.status_code)
            
            results["details"]["normal_requests"] = normal_requests
            results["details"]["normal_requests_passed"] = all(code == 200 for code in normal_requests)
            
            # Test burst requests (should be limited)
            burst_requests = []
            for i in range(15):  # Exceed burst limit of 10
                response = self.client.get("/health")
                burst_requests.append(response.status_code)
                time.sleep(0.1)  # Small delay
            
            results["details"]["burst_requests"] = burst_requests
            results["details"]["burst_limited"] = any(code == 429 for code in burst_requests)
            
            # Test rate limit over time
            rate_limit_requests = []
            for i in range(65):  # Exceed 60 RPM limit
                response = self.client.get("/health")
                rate_limit_requests.append(response.status_code)
                time.sleep(1)  # 1 second between requests
            
            results["details"]["rate_limit_requests"] = rate_limit_requests
            results["details"]["rate_limited"] = any(code == 429 for code in rate_limit_requests)
            
            # Overall success if rate limiting is working
            results["success"] = (
                results["details"]["normal_requests_passed"] and
                results["details"]["burst_limited"] and
                results["details"]["rate_limited"]
            )
            
            print(f"   ✅ Rate limiting test: {'PASS' if results['success'] else 'FAIL'}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Rate limiting test failed: {e}")
        
        return results
    
    async def test_content_sanitization(self) -> Dict[str, Any]:
        """Test HTML and markdown content sanitization."""
        print("🧪 Testing content sanitization...")
        
        results = {
            "test_name": "Content Sanitization",
            "success": False,
            "details": {}
        }
        
        try:
            # Test HTML sanitization
            config = SecurityHardeningConfig()
            sanitizer = ContentSanitizer(config.sanitization)
            
            # Test XSS attempts
            xss_attempts = [
                "<script>alert('xss')</script>",
                "<iframe src='javascript:alert(1)'></iframe>",
                "<img src='x' onerror='alert(1)'>",
                "<object data='javascript:alert(1)'></object>",
                "<embed src='javascript:alert(1)'>"
            ]
            
            sanitized_html = []
            for xss in xss_attempts:
                sanitized = sanitizer.sanitize_html(xss)
                sanitized_html.append({
                    "original": xss,
                    "sanitized": sanitized,
                    "safe": "<script>" not in sanitized and "<iframe>" not in sanitized
                })
            
            results["details"]["html_sanitization"] = sanitized_html
            results["details"]["html_safe"] = all(item["safe"] for item in sanitized_html)
            
            # Test markdown sanitization
            markdown_attempts = [
                "# Header\n<script>alert('xss')</script>",
                "**Bold** <iframe src='javascript:alert(1)'></iframe>",
                "```code``` <img src='x' onerror='alert(1)'>"
            ]
            
            sanitized_markdown = []
            for md in markdown_attempts:
                sanitized = sanitizer.sanitize_markdown(md)
                sanitized_markdown.append({
                    "original": md,
                    "sanitized": sanitized,
                    "safe": "<script>" not in sanitized and "<iframe>" not in sanitized
                })
            
            results["details"]["markdown_sanitization"] = sanitized_markdown
            results["details"]["markdown_safe"] = all(item["safe"] for item in sanitized_markdown)
            
            # Test text sanitization
            text_attempts = [
                "SELECT * FROM users WHERE id = 1 OR 1=1",
                "cat /etc/passwd",
                "rm -rf /",
                "javascript:alert(1)"
            ]
            
            sanitized_text = []
            for text in text_attempts:
                sanitized = sanitizer.sanitize_text(text)
                sanitized_text.append({
                    "original": text,
                    "sanitized": sanitized,
                    "safe": sanitized != text  # Should be HTML escaped
                })
            
            results["details"]["text_sanitization"] = sanitized_text
            results["details"]["text_safe"] = all(item["safe"] for item in sanitized_text)
            
            # Overall success if all sanitization is working
            results["success"] = (
                results["details"]["html_safe"] and
                results["details"]["markdown_safe"] and
                results["details"]["text_safe"]
            )
            
            print(f"   ✅ Content sanitization test: {'PASS' if results['success'] else 'FAIL'}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Content sanitization test failed: {e}")
        
        return results
    
    async def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers are properly set."""
        print("🧪 Testing security headers...")
        
        results = {
            "test_name": "Security Headers",
            "success": False,
            "details": {}
        }
        
        try:
            response = self.client.get("/health")
            headers = dict(response.headers)
            
            # Check required security headers
            required_headers = {
                "Content-Security-Policy": "CSP header",
                "Strict-Transport-Security": "HSTS header",
                "X-Frame-Options": "Clickjacking protection",
                "X-Content-Type-Options": "MIME type sniffing protection",
                "X-XSS-Protection": "XSS protection",
                "Referrer-Policy": "Referrer policy",
                "Permissions-Policy": "Permissions policy"
            }
            
            header_results = {}
            for header, description in required_headers.items():
                present = header in headers
                header_results[header] = {
                    "present": present,
                    "description": description,
                    "value": headers.get(header, "Not set")
                }
            
            results["details"]["headers"] = header_results
            results["details"]["all_headers_present"] = all(
                result["present"] for result in header_results.values()
            )
            
            # Check CSP policy content
            csp_policy = headers.get("Content-Security-Policy", "")
            csp_checks = {
                "has_default_src": "default-src" in csp_policy,
                "has_script_src": "script-src" in csp_policy,
                "has_frame_ancestors": "frame-ancestors" in csp_policy,
                "has_object_src": "object-src" in csp_policy
            }
            
            results["details"]["csp_checks"] = csp_checks
            results["details"]["csp_valid"] = all(csp_checks.values())
            
            # Overall success if all headers are present and CSP is valid
            results["success"] = (
                results["details"]["all_headers_present"] and
                results["details"]["csp_valid"]
            )
            
            print(f"   ✅ Security headers test: {'PASS' if results['success'] else 'FAIL'}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Security headers test failed: {e}")
        
        return results
    
    async def test_injection_detection(self) -> Dict[str, Any]:
        """Test injection attempt detection and logging."""
        print("🧪 Testing injection detection...")
        
        results = {
            "test_name": "Injection Detection",
            "success": False,
            "details": {}
        }
        
        try:
            # Test SQL injection attempts
            sql_injections = [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "admin'--",
                "1' UNION SELECT * FROM users--"
            ]
            
            sql_results = []
            for injection in sql_injections:
                response = self.client.post("/search", json={"query": injection})
                sql_results.append({
                    "injection": injection,
                    "status_code": response.status_code,
                    "blocked": response.status_code in [400, 403, 429]
                })
            
            results["details"]["sql_injections"] = sql_results
            results["details"]["sql_blocked"] = all(result["blocked"] for result in sql_results)
            
            # Test XSS attempts
            xss_attempts = [
                "<script>alert('xss')</script>",
                "javascript:alert(1)",
                "<img src='x' onerror='alert(1)'>",
                "<iframe src='javascript:alert(1)'></iframe>"
            ]
            
            xss_results = []
            for xss in xss_attempts:
                response = self.client.post("/search", json={"query": xss})
                xss_results.append({
                    "xss": xss,
                    "status_code": response.status_code,
                    "blocked": response.status_code in [400, 403, 429]
                })
            
            results["details"]["xss_attempts"] = xss_results
            results["details"]["xss_blocked"] = all(result["blocked"] for result in xss_results)
            
            # Test command injection attempts
            cmd_injections = [
                "test; cat /etc/passwd",
                "test | whoami",
                "test && rm -rf /",
                "test `id`"
            ]
            
            cmd_results = []
            for cmd in cmd_injections:
                response = self.client.post("/search", json={"query": cmd})
                cmd_results.append({
                    "command": cmd,
                    "status_code": response.status_code,
                    "blocked": response.status_code in [400, 403, 429]
                })
            
            results["details"]["command_injections"] = cmd_results
            results["details"]["cmd_blocked"] = all(result["blocked"] for result in cmd_results)
            
            # Overall success if all injection attempts are blocked
            results["success"] = (
                results["details"]["sql_blocked"] and
                results["details"]["xss_blocked"] and
                results["details"]["cmd_blocked"]
            )
            
            print(f"   ✅ Injection detection test: {'PASS' if results['success'] else 'FAIL'}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Injection detection test failed: {e}")
        
        return results
    
    async def test_request_limits(self) -> Dict[str, Any]:
        """Test request size and length limits."""
        print("🧪 Testing request limits...")
        
        results = {
            "test_name": "Request Limits",
            "success": False,
            "details": {}
        }
        
        try:
            # Test query length limit
            long_query = "a" * 1001  # Exceed 1000 character limit
            response = self.client.post("/search", json={"query": long_query})
            
            results["details"]["long_query"] = {
                "length": len(long_query),
                "status_code": response.status_code,
                "blocked": response.status_code == 400
            }
            
            # Test request size limit (simulate large request)
            large_data = {"query": "test", "data": "x" * (11 * 1024 * 1024)}  # 11MB
            response = self.client.post("/search", json=large_data)
            
            results["details"]["large_request"] = {
                "size_mb": 11,
                "status_code": response.status_code,
                "blocked": response.status_code == 413
            }
            
            # Test URL length limit
            long_url = "/search?" + "a" * 2000  # Exceed 2048 character limit
            response = self.client.get(long_url)
            
            results["details"]["long_url"] = {
                "length": len(long_url),
                "status_code": response.status_code,
                "blocked": response.status_code == 414
            }
            
            # Overall success if all limits are enforced
            results["success"] = (
                results["details"]["long_query"]["blocked"] and
                results["details"]["large_request"]["blocked"] and
                results["details"]["long_url"]["blocked"]
            )
            
            print(f"   ✅ Request limits test: {'PASS' if results['success'] else 'FAIL'}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Request limits test failed: {e}")
        
        return results
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all security tests."""
        print("🚀 SECURITY HARDENING TEST SUITE")
        print("=" * 60)
        
        tests = [
            self.test_rate_limiting,
            self.test_content_sanitization,
            self.test_security_headers,
            self.test_injection_detection,
            self.test_request_limits
        ]
        
        results = []
        for test in tests:
            try:
                result = await test()
                results.append(result)
            except Exception as e:
                results.append({
                    "test_name": test.__name__,
                    "success": False,
                    "error": str(e)
                })
        
        return results

async def main():
    """Run security hardening tests."""
    test_client = SecurityTestClient()
    results = await test_client.run_all_tests()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for result in results:
        success = result.get("success", False)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {result['test_name']}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SECURITY HARDENING TESTS PASSED!")
        print("✅ Security implementation verified")
    else:
        print("⚠️  Some tests failed - check implementation")
    
    # Save detailed results
    with open("security_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Detailed results saved to: security_test_results.json")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
