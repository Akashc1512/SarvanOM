#!/usr/bin/env python3
"""
Monitoring setup script for Universal Knowledge Hub.
"""

import asyncio
import os
import sys
import httpx
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
METRICS_ENDPOINT = f"{API_BASE_URL}/metrics"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
INTEGRATIONS_ENDPOINT = f"{API_BASE_URL}/integrations"


async def check_api_health() -> bool:
    """Check if the API is running and healthy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(HEALTH_ENDPOINT, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Health: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ API Health Check Failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


async def check_metrics_endpoint() -> bool:
    """Check if metrics endpoint is working."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(METRICS_ENDPOINT, timeout=5.0)
            if response.status_code == 200:
                content = response.text
                print("✅ Metrics endpoint is working")

                # Check for key metrics
                key_metrics = [
                    "ukp_requests_total",
                    "ukp_request_duration_seconds",
                    "ukp_errors_total",
                    "ukp_cache_hits_total",
                    "ukp_cache_misses_total",
                ]

                found_metrics = []
                for metric in key_metrics:
                    if metric in content:
                        found_metrics.append(metric)

                print(f"📊 Found {len(found_metrics)}/{len(key_metrics)} key metrics:")
                for metric in found_metrics:
                    print(f"   - {metric}")

                return True
            else:
                print(f"❌ Metrics endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot access metrics endpoint: {e}")
        return False


async def check_integrations() -> bool:
    """Check integration status."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(INTEGRATIONS_ENDPOINT, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                integrations = data.get("integrations", {})
                summary = data.get("summary", {})

                print(f"🔗 Integration Status:")
                print(f"   Total: {summary.get('total', 0)}")
                print(f"   Healthy: {summary.get('healthy', 0)}")
                print(f"   Unhealthy: {summary.get('unhealthy', 0)}")

                for name, status in integrations.items():
                    status_icon = "✅" if status.get("status") == "healthy" else "❌"
                    print(f"   {status_icon} {name}: {status.get('status', 'unknown')}")

                return summary.get("healthy", 0) > 0
            else:
                print(f"❌ Integrations endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot access integrations endpoint: {e}")
        return False


async def generate_test_metrics() -> bool:
    """Generate some test metrics by making API calls."""
    print("\n🧪 Generating test metrics...")

    test_endpoints = [
        ("GET", "/health"),
        ("GET", "/metrics"),
        ("GET", "/integrations"),
    ]

    async with httpx.AsyncClient() as client:
        for method, endpoint in test_endpoints:
            try:
                url = f"{API_BASE_URL}{endpoint}"
                if method == "GET":
                    response = await client.get(url, timeout=5.0)
                else:
                    response = await client.post(url, timeout=5.0)
                print(f"   {method} {endpoint} -> {response.status_code}")
            except Exception as e:
                print(f"   {method} {endpoint} -> ERROR: {e}")

    return True


def check_prometheus_config() -> bool:
    """Check if Prometheus configuration is valid."""
    try:
        import yaml

        with open("monitoring/prometheus-config.yaml", "r") as f:
            config = yaml.safe_load(f)

        print("✅ Prometheus configuration is valid")

        # Check for UKP backend job
        scrape_configs = config.get("scrape_configs", [])
        ukp_jobs = [job for job in scrape_configs if "ukp" in job.get("job_name", "")]

        if ukp_jobs:
            print(f"📊 Found {len(ukp_jobs)} UKP monitoring jobs:")
            for job in ukp_jobs:
                print(f"   - {job['job_name']}: {job['static_configs'][0]['targets']}")
        else:
            print("⚠️ No UKP monitoring jobs found in Prometheus config")

        return True
    except Exception as e:
        print(f"❌ Prometheus configuration error: {e}")
        return False


def setup_logging_config() -> bool:
    """Verify logging configuration."""
    print("\n📝 Checking logging configuration...")

    # Check if structured logging is configured
    try:
        import logging

        logger = logging.getLogger(__name__)

        # Test structured logging
        logger.info(
            "Test structured log message",
            extra={"test": True, "component": "monitoring_setup"},
        )

        print("✅ Logging configuration appears to be working")
        return True
    except Exception as e:
        print(f"❌ Logging configuration error: {e}")
        return False


async def main():
    """Main monitoring setup function."""
    print("🔧 Setting up monitoring for Universal Knowledge Hub")
    print("=" * 60)

    # Check API health
    print("\n1. Checking API health...")
    api_healthy = await check_api_health()

    if not api_healthy:
        print("❌ API is not running. Please start the backend first.")
        print("   Command: python -m uvicorn services.gateway.main:app --reload")
        return False

    # Check metrics endpoint
    print("\n2. Checking metrics endpoint...")
    metrics_working = await check_metrics_endpoint()

    # Check integrations
    print("\n3. Checking integrations...")
    integrations_working = await check_integrations()

    # Generate test metrics
    print("\n4. Generating test metrics...")
    await generate_test_metrics()

    # Setup logging
    print("\n5. Setting up logging configuration...")
    logging_configured = setup_logging_config()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Monitoring Setup Summary:")
    print(f"   API Health: {'✅' if api_healthy else '❌'}")
    print(f"   Metrics: {'✅' if metrics_working else '❌'}")
    print(f"   Integrations: {'✅' if integrations_working else '❌'}")
    print(f"   Logging: {'✅' if logging_configured else '❌'}")

    if all([api_healthy, metrics_working, integrations_working, logging_configured]):
        print("\n🎉 Monitoring setup complete!")
        print("\nNext steps:")
        print("1. Start Prometheus: prometheus --config.file=prometheus.yml")
        print("2. Start Grafana: grafana-server")
        print("3. Access Grafana: http://localhost:3000")
        print("4. Add Prometheus data source: http://localhost:9090")
        return True
    else:
        print("\n⚠️  Some monitoring components need attention.")
        return False


if __name__ == "__main__":
    asyncio.run(main())
