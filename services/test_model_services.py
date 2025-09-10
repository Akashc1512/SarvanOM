#!/usr/bin/env python3
"""
Test script for Model Registry, Router, and Auto-Upgrade services
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class ModelServicesTester:
    """Test the model services implementation"""
    
    def __init__(self):
        self.registry_url = "http://localhost:8000"
        self.router_url = "http://localhost:8001"
        self.auto_upgrade_url = "http://localhost:8002"
        self.http_client = httpx.AsyncClient()
    
    async def test_registry_service(self) -> bool:
        """Test model registry service"""
        print("Testing Model Registry Service...")
        
        try:
            # Test health check
            response = await self.http_client.get(f"{self.registry_url}/health")
            assert response.status_code == 200
            print("✓ Registry health check passed")
            
            # Test get all models
            response = await self.http_client.get(f"{self.registry_url}/models")
            assert response.status_code == 200
            models = response.json()
            assert len(models) > 0
            print(f"✓ Found {len(models)} models in registry")
            
            # Test get specific model
            model_id = models[0]["model_id"]
            response = await self.http_client.get(f"{self.registry_url}/models/{model_id}")
            assert response.status_code == 200
            print(f"✓ Retrieved model {model_id}")
            
            # Test get stable models
            response = await self.http_client.get(f"{self.registry_url}/models/stable")
            assert response.status_code == 200
            stable_models = response.json()
            print(f"✓ Found {len(stable_models)} stable models")
            
            # Test get refiner models
            response = await self.http_client.get(f"{self.registry_url}/models/refiners")
            assert response.status_code == 200
            refiner_models = response.json()
            print(f"✓ Found {len(refiner_models)} refiner models")
            
            # Test get models by capability
            response = await self.http_client.get(f"{self.registry_url}/models/capability/multimodal")
            assert response.status_code == 200
            multimodal_models = response.json()
            print(f"✓ Found {len(multimodal_models)} multimodal models")
            
            # Test get models by provider
            response = await self.http_client.get(f"{self.registry_url}/models/provider/openai")
            assert response.status_code == 200
            openai_models = response.json()
            print(f"✓ Found {len(openai_models)} OpenAI models")
            
            # Test get providers
            response = await self.http_client.get(f"{self.registry_url}/providers")
            assert response.status_code == 200
            providers = response.json()
            print(f"✓ Found {len(providers)} providers")
            
            # Test record model usage
            response = await self.http_client.post(
                f"{self.registry_url}/models/{model_id}/usage",
                params={
                    "query_type": "simple",
                    "response_time": 1.5,
                    "cost_usd": 0.01
                }
            )
            assert response.status_code == 200
            print("✓ Recorded model usage")
            
            return True
            
        except Exception as e:
            print(f"✗ Registry service test failed: {e}")
            return False
    
    async def test_router_service(self) -> bool:
        """Test model router service"""
        print("\nTesting Model Router Service...")
        
        try:
            # Test health check
            response = await self.http_client.get(f"{self.router_url}/health")
            assert response.status_code == 200
            print("✓ Router health check passed")
            
            # Test query classification
            response = await self.http_client.get(
                f"{self.router_url}/classify",
                params={"query": "What is the capital of France?"}
            )
            assert response.status_code == 200
            classification = response.json()
            assert "query_type" in classification
            assert "complexity" in classification
            assert "budget_seconds" in classification
            print(f"✓ Query classified as {classification['query_type']} with {classification['complexity']} complexity")
            
            # Test simple query routing
            response = await self.http_client.post(
                f"{self.router_url}/route",
                json={
                    "query": "What is the capital of France?",
                    "context": {}
                }
            )
            assert response.status_code == 200
            routing = response.json()
            assert "model_id" in routing
            assert "provider" in routing
            assert "confidence" in routing
            print(f"✓ Simple query routed to {routing['model_id']} with {routing['confidence']} confidence")
            
            # Test technical query routing
            response = await self.http_client.post(
                f"{self.router_url}/route",
                json={
                    "query": "Write a Python function to calculate factorial",
                    "context": {}
                }
            )
            assert response.status_code == 200
            routing = response.json()
            print(f"✓ Technical query routed to {routing['model_id']}")
            
            # Test multimodal query routing
            response = await self.http_client.post(
                f"{self.router_url}/route",
                json={
                    "query": "Analyze this image",
                    "context": {"has_images": True}
                }
            )
            assert response.status_code == 200
            routing = response.json()
            print(f"✓ Multimodal query routed to {routing['model_id']}")
            
            # Test refinement query routing
            response = await self.http_client.post(
                f"{self.router_url}/route/refinement",
                json={
                    "query": "show me apple",
                    "refinement_type": "fast"
                }
            )
            assert response.status_code == 200
            routing = response.json()
            print(f"✓ Refinement query routed to {routing['model_id']}")
            
            return True
            
        except Exception as e:
            print(f"✗ Router service test failed: {e}")
            return False
    
    async def test_auto_upgrade_service(self) -> bool:
        """Test auto-upgrade service"""
        print("\nTesting Auto-Upgrade Service...")
        
        try:
            # Test health check
            response = await self.http_client.get(f"{self.auto_upgrade_url}/health")
            assert response.status_code == 200
            print("✓ Auto-upgrade health check passed")
            
            # Test get candidates
            response = await self.http_client.get(f"{self.auto_upgrade_url}/candidates")
            assert response.status_code == 200
            candidates = response.json()
            print(f"✓ Found {len(candidates)} model candidates")
            
            # Test get evaluations
            response = await self.http_client.get(f"{self.auto_upgrade_url}/evaluations")
            assert response.status_code == 200
            evaluations = response.json()
            print(f"✓ Found {len(evaluations)} evaluation results")
            
            # Test trigger discovery
            response = await self.http_client.post(f"{self.auto_upgrade_url}/discover")
            assert response.status_code == 200
            discovery_result = response.json()
            print(f"✓ Discovery triggered, found {discovery_result['discovered']} models")
            
            # Test start service
            response = await self.http_client.post(f"{self.auto_upgrade_url}/start")
            assert response.status_code == 200
            print("✓ Auto-upgrade service started")
            
            # Test stop service
            response = await self.http_client.post(f"{self.auto_upgrade_url}/stop")
            assert response.status_code == 200
            print("✓ Auto-upgrade service stopped")
            
            return True
            
        except Exception as e:
            print(f"✗ Auto-upgrade service test failed: {e}")
            return False
    
    async def test_integration(self) -> bool:
        """Test integration between services"""
        print("\nTesting Service Integration...")
        
        try:
            # Test that router can get models from registry
            response = await self.http_client.post(
                f"{self.router_url}/route",
                json={
                    "query": "Test integration query",
                    "context": {}
                }
            )
            assert response.status_code == 200
            routing = response.json()
            
            # Verify the model exists in registry
            response = await self.http_client.get(
                f"{self.registry_url}/models/{routing['model_id']}"
            )
            assert response.status_code == 200
            print("✓ Router-registry integration working")
            
            # Test that auto-upgrade can access registry
            response = await self.http_client.post(f"{self.auto_upgrade_url}/discover")
            assert response.status_code == 200
            print("✓ Auto-upgrade-registry integration working")
            
            return True
            
        except Exception as e:
            print(f"✗ Integration test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("Starting Model Services Tests...")
        print("=" * 50)
        
        tests = [
            self.test_registry_service,
            self.test_router_service,
            self.test_auto_upgrade_service,
            self.test_integration
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
        print(f"Registry Service: {'✓ PASS' if results[0] else '✗ FAIL'}")
        print(f"Router Service: {'✓ PASS' if results[1] else '✗ FAIL'}")
        print(f"Auto-Upgrade Service: {'✓ PASS' if results[2] else '✗ FAIL'}")
        print(f"Integration: {'✓ PASS' if results[3] else '✗ FAIL'}")
        
        all_passed = all(results)
        print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        
        return all_passed

async def main():
    """Main test function"""
    tester = ModelServicesTester()
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    success = await tester.run_all_tests()
    
    # Cleanup
    await tester.http_client.aclose()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
