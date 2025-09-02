#!/usr/bin/env python3
"""
CI Integration Script for SarvanOM Guardrails

This script is designed to be called from CI/CD pipelines:
- GitHub Actions
- GitLab CI
- Jenkins
- Azure DevOps
- Any other CI system

It runs all guardrails tests and provides appropriate exit codes for CI integration.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.append('.')

async def run_ci_guardrails() -> int:
    """Run guardrails tests for CI integration."""
    try:
        # Import and run the comprehensive guardrails runner
        from tests.run_guardrails import GuardrailsTestRunner
        
        print("🚀 CI Guardrails Integration")
        print("=" * 40)
        print(f"CI Environment: {os.getenv('CI', 'false')}")
        print(f"CI Provider: {os.getenv('GITHUB_ACTIONS', 'unknown') or os.getenv('GITLAB_CI', 'unknown') or 'unknown'}")
        print()
        
        # Initialize runner
        runner = GuardrailsTestRunner()
        
        # Run all guardrails
        success = await runner.run_all_guardrails()
        
        # Return appropriate exit code
        if success:
            print("\n✅ CI Guardrails: BUILD CAN PROCEED")
            return 0
        else:
            print("\n❌ CI Guardrails: BUILD SHOULD FAIL")
            return 1
            
    except Exception as e:
        print(f"\n💥 CI Guardrails failed with error: {e}")
        print("   Build should fail due to guardrails system error")
        return 1

def generate_ci_summary() -> Dict[str, Any]:
    """Generate a summary for CI systems."""
    try:
        # Try to load the latest comprehensive report
        code_garden_dir = Path("code_garden")
        latest_report = code_garden_dir / "guardrails_comprehensive_report_latest.json"
        
        if latest_report.exists():
            with open(latest_report, 'r') as f:
                report = json.load(f)
            
            return {
                'success': report.get('overall_success', False),
                'timestamp': report.get('timestamp', 'unknown'),
                'summary': report.get('summary', {}),
                'build_should_fail': report.get('summary', {}).get('build_should_fail', True)
            }
        else:
            return {
                'success': False,
                'timestamp': 'unknown',
                'summary': {},
                'build_should_fail': True,
                'error': 'No guardrails report found'
            }
            
    except Exception as e:
        return {
            'success': False,
            'timestamp': 'unknown',
            'summary': {},
            'build_should_fail': True,
            'error': f'Failed to load report: {e}'
        }

def main():
    """Main function for CI integration."""
    # Check if we're in a CI environment
    ci_env = os.getenv('CI', 'false').lower() == 'true'
    
    if ci_env:
        print("🔧 CI Environment Detected")
        print("   Running guardrails tests...")
        
        # Run guardrails tests
        exit_code = asyncio.run(run_ci_guardrails())
        
        # Generate CI summary
        summary = generate_ci_summary()
        
        # Print CI-friendly output
        print(f"\n📊 CI SUMMARY")
        print(f"Overall Success: {summary['success']}")
        print(f"Build Should Fail: {summary['build_should_fail']}")
        print(f"Timestamp: {summary['timestamp']}")
        
        if 'error' in summary:
            print(f"Error: {summary['error']}")
        
        # Exit with appropriate code
        sys.exit(exit_code)
    else:
        print("🔧 Local Environment Detected")
        print("   Running guardrails tests locally...")
        
        # Run guardrails tests locally
        exit_code = asyncio.run(run_ci_guardrails())
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
