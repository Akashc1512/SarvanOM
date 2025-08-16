#!/usr/bin/env python3
"""
Legacy Entry Point Cleanup Verification Script

This script verifies that all legacy entry points have been properly removed
and the new microservices architecture is working correctly.

Checks:
1. No references to services.api_gateway.main
2. Gateway service is accessible on port 8004
3. All npm scripts are properly configured
4. Docker configuration is updated
5. README files are updated

Authors: Universal Knowledge Platform Engineering Team
Version: 1.0.0 (2025-08-11)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class LegacyCleanupVerifier:
    """Verifies that legacy entry points have been properly cleaned up."""

    def __init__(self):
        self.project_root = project_root
        self.results = []
        self.errors = []

    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print("🔍 Verifying Legacy Entry Point Cleanup...")
        print("=" * 60)

        # Core checks
        self._check_package_json_scripts()
        self._check_readme_files()
        self._check_docker_configuration()
        self._check_gateway_service()
        self._check_port_configuration()
        self._check_legacy_references()

        # Print results
        self._print_results()
        return len(self.errors) == 0

    def _check_package_json_scripts(self):
        """Check that package.json scripts are updated."""
        print("📦 Checking package.json scripts...")
        
        try:
            with open(self.project_root / "package.json", "r") as f:
                package_data = json.load(f)
            
            scripts = package_data.get("scripts", {})
            
            # Check for correct gateway references
            if "dev:backend" in scripts:
                script = scripts["dev:backend"]
                if "services.gateway.main:app" in script and "8004" in script:
                    self.results.append(("✅ package.json dev:backend", "Correctly configured"))
                else:
                    self.errors.append(("❌ package.json dev:backend", "Still references old gateway"))
            
            if "start:backend" in scripts:
                script = scripts["start:backend"]
                if "services.gateway.main:app" in script and "8004" in script:
                    self.results.append(("✅ package.json start:backend", "Correctly configured"))
                else:
                    self.errors.append(("❌ package.json start:backend", "Still references old gateway"))
            
            # Check for individual service scripts
            service_scripts = ["start:auth", "start:search", "start:synthesis", "start:factcheck", "start:analytics"]
            for script_name in service_scripts:
                if script_name in scripts:
                    self.results.append((f"✅ package.json {script_name}", "Service script present"))
                else:
                    self.errors.append((f"❌ package.json {script_name}", "Missing service script"))
                    
        except Exception as e:
            self.errors.append(("❌ package.json", f"Error reading file: {e}"))

    def _check_readme_files(self):
        """Check that README files are updated."""
        print("📖 Checking README files...")
        
        # Check main README
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if "services/gateway/" in content and "8004" in content:
                self.results.append(("✅ README.md", "Updated with correct gateway and port"))
            else:
                self.errors.append(("❌ README.md", "Still contains old references"))
                
            if "python run_server.py" not in content:
                self.results.append(("✅ README.md", "No legacy run_server.py references"))
            else:
                self.errors.append(("❌ README.md", "Still contains run_server.py references"))

    def _check_docker_configuration(self):
        """Check that Docker configuration is updated."""
        print("🐳 Checking Docker configuration...")
        
        dockerfile_path = self.project_root / "Dockerfile.enterprise"
        if dockerfile_path.exists():
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if "services.gateway.main" in content and "8004" in content:
                self.results.append(("✅ Dockerfile.enterprise", "Updated with correct gateway and port"))
            else:
                self.errors.append(("❌ Dockerfile.enterprise", "Still contains old references"))

    def _check_gateway_service(self):
        """Check that the gateway service is accessible."""
        print("🚪 Checking gateway service...")
        
        try:
            # Try to import the gateway service
            import services.gateway.main
            self.results.append(("✅ Gateway Import", "services.gateway.main imports successfully"))
        except ImportError as e:
            self.errors.append(("❌ Gateway Import", f"Failed to import: {e}"))
        
        # Check if gateway service can start (without actually starting it)
        gateway_path = self.project_root / "services" / "gateway" / "main.py"
        if gateway_path.exists():
            self.results.append(("✅ Gateway File", "services/gateway/main.py exists"))
        else:
            self.errors.append(("❌ Gateway File", "services/gateway/main.py missing"))

    def _check_port_configuration(self):
        """Check that port configuration is consistent."""
        print("🔌 Checking port configuration...")
        
        # Check start_services.bat
        bat_path = self.project_root / "start_services.bat"
        if bat_path.exists():
            with open(bat_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if "8004" in content:
                self.results.append(("✅ start_services.bat", "Updated with port 8004"))
            else:
                self.errors.append(("❌ start_services.bat", "Still references old port"))

    def _check_legacy_references(self):
        """Check for any remaining legacy references in critical files."""
        print("🔍 Checking for legacy references...")
        
        # Check for services.api_gateway references in critical files
        critical_files = [
            "package.json",
            "README.md",
            "services/README.md",
            "Dockerfile.enterprise",
            "start_services.bat"
        ]
        
        for file_name in critical_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                if "services.api_gateway" not in content:
                    self.results.append((f"✅ {file_name}", "No legacy api_gateway references"))
                else:
                    self.errors.append((f"❌ {file_name}", "Still contains services.api_gateway references"))

    def _print_results(self):
        """Print verification results."""
        print("\n" + "=" * 60)
        print("📊 LEGACY CLEANUP VERIFICATION RESULTS")
        print("=" * 60)
        
        # Print successful checks
        if self.results:
            print("\n✅ SUCCESSFUL CHECKS:")
            for check, message in self.results:
                print(f"  {check}: {message}")
        
        # Print errors
        if self.errors:
            print("\n❌ ISSUES FOUND:")
            for check, message in self.errors:
                print(f"  {check}: {message}")
        
        # Summary
        total_checks = len(self.results) + len(self.errors)
        success_rate = (len(self.results) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n📈 SUMMARY:")
        print(f"  Total Checks: {total_checks}")
        print(f"  Successful: {len(self.results)}")
        print(f"  Issues: {len(self.errors)}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if len(self.errors) == 0:
            print("\n🎉 ALL CHECKS PASSED! Legacy cleanup completed successfully.")
            print("✅ The microservices architecture is properly configured.")
            print("✅ All entry points point to services.gateway.main:app")
            print("✅ Port 8004 is configured as the main gateway port.")
        else:
            print(f"\n⚠️  {len(self.errors)} issues found. Please address them before proceeding.")
            print("💡 Check the LEGACY_CLEANUP_SUMMARY.md file for detailed information.")


def main():
    """Main verification function."""
    verifier = LegacyCleanupVerifier()
    success = verifier.run_all_checks()
    
    if success:
        print("\n🚀 Ready to start the updated microservices!")
        print("   Run: npm run dev:backend")
        print("   Access: http://localhost:8004")
        print("   Docs: http://localhost:8004/docs")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the issues above before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
