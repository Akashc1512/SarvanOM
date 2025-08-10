#!/usr/bin/env python3
"""
Comprehensive Dependency Version Checker and Updater
Checks all dependencies in requirements.txt against latest PyPI versions
and generates updated requirements.txt with latest stable versions.
"""

import subprocess
import sys
import re
from typing import Dict, List, Tuple, Optional
import json
import requests
from packaging import version

def get_installed_version(package_name: str) -> Optional[str]:
    """Get installed version of a package."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
    except subprocess.CalledProcessError:
        pass
    return None

def get_latest_version(package_name: str) -> Optional[str]:
    """Get latest version from PyPI."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception:
        pass
    return None

def parse_requirements_line(line: str) -> Tuple[str, str, str]:
    """Parse a requirements.txt line and return (package_name, version_spec, comment)."""
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None, line
    
    # Extract package name and version spec
    parts = line.split('#', 1)
    requirement = parts[0].strip()
    comment = f" # {parts[1].strip()}" if len(parts) > 1 else ""
    
    # Parse package name and version
    if '>=' in requirement:
        package_name, version_spec = requirement.split('>=', 1)
        version_spec = f">={version_spec.strip()}"
    elif '==' in requirement:
        package_name, version_spec = requirement.split('==', 1)
        version_spec = f"=={version_spec.strip()}"
    elif '~=' in requirement:
        package_name, version_spec = requirement.split('~=', 1)
        version_spec = f"~={version_spec.strip()}"
    else:
        package_name = requirement.strip()
        version_spec = ""
    
    return package_name.strip(), version_spec, comment

def check_package_versions(packages: List[str]) -> Dict[str, Dict[str, str]]:
    """Check versions for a list of packages."""
    results = {}
    
    print(f"Checking {len(packages)} packages...")
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] Checking {package}...")
        
        installed = get_installed_version(package)
        latest = get_latest_version(package)
        
        results[package] = {
            'installed': installed,
            'latest': latest,
            'needs_update': False
        }
        
        if installed and latest:
            try:
                installed_ver = version.parse(installed)
                latest_ver = version.parse(latest)
                results[package]['needs_update'] = latest_ver > installed_ver
            except version.InvalidVersion:
                pass
    
    return results

def generate_upgrade_commands(packages_to_update: List[str]) -> List[str]:
    """Generate pip upgrade commands for packages that need updating."""
    commands = []
    
    if packages_to_update:
        # Group packages for batch upgrade
        batch_size = 10
        for i in range(0, len(packages_to_update), batch_size):
            batch = packages_to_update[i:i + batch_size]
            commands.append(f"pip install --upgrade {' '.join(batch)}")
    
    return commands

def update_requirements_file(requirements_path: str, version_results: Dict[str, Dict[str, str]]) -> str:
    """Update requirements.txt with latest versions."""
    updated_lines = []
    
    with open(requirements_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        package_name, version_spec, comment = parse_requirements_line(line)
        
        if package_name and package_name in version_results:
            result = version_results[package_name]
            latest = result.get('latest')
            
            if latest and result.get('needs_update', False):
                # Update to latest version
                if '>=' in version_spec:
                    new_spec = f">={latest}"
                elif '==' in version_spec:
                    new_spec = f"=={latest}"
                elif '~=' in version_spec:
                    new_spec = f"~={latest}"
                else:
                    new_spec = f">={latest}"
                
                updated_line = f"{package_name}{new_spec}{comment}\n"
                updated_lines.append(updated_line)
                print(f"  Updated {package_name}: {version_spec} -> {new_spec}")
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Write updated requirements
    backup_path = requirements_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    with open(requirements_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return backup_path

def main():
    """Main function to check and update all dependencies."""
    print("🔍 Comprehensive Dependency Version Checker")
    print("=" * 50)
    
    # Read current requirements.txt
    requirements_path = "requirements.txt"
    
    with open(requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract package names
    packages = []
    for line in content.split('\n'):
        package_name, _, _ = parse_requirements_line(line)
        if package_name:
            packages.append(package_name)
    
    print(f"Found {len(packages)} packages in requirements.txt")
    
    # Check versions
    version_results = check_package_versions(packages)
    
    # Analyze results
    packages_to_update = []
    outdated_packages = []
    up_to_date_packages = []
    not_found_packages = []
    
    print("\n📊 Version Analysis Results:")
    print("=" * 50)
    
    for package, result in version_results.items():
        installed = result.get('installed')
        latest = result.get('latest')
        needs_update = result.get('needs_update', False)
        
        if not latest:
            not_found_packages.append(package)
            print(f"❌ {package}: Not found on PyPI")
        elif not installed:
            print(f"⚠️  {package}: Not installed (latest: {latest})")
        elif needs_update:
            outdated_packages.append(package)
            packages_to_update.append(package)
            print(f"🔄 {package}: {installed} -> {latest} (UPDATE NEEDED)")
        else:
            up_to_date_packages.append(package)
            print(f"✅ {package}: {installed} (up to date)")
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"  ✅ Up to date: {len(up_to_date_packages)}")
    print(f"  🔄 Needs update: {len(outdated_packages)}")
    print(f"  ❌ Not found: {len(not_found_packages)}")
    print(f"  ⚠️  Not installed: {len([p for p in packages if not version_results.get(p, {}).get('installed')])}")
    
    # Generate upgrade commands
    if packages_to_update:
        print(f"\n🚀 Upgrade Commands:")
        print("=" * 50)
        commands = generate_upgrade_commands(packages_to_update)
        for cmd in commands:
            print(f"$ {cmd}")
        
        # Update requirements.txt
        print(f"\n📝 Updating requirements.txt...")
        backup_path = update_requirements_file(requirements_path, version_results)
        print(f"  Backup saved to: {backup_path}")
        print(f"  Updated: {requirements_path}")
        
        # Save detailed report
        report_path = "dependency_version_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(version_results, f, indent=2)
        print(f"  Detailed report: {report_path}")
        
        print(f"\n🎯 Next Steps:")
        print(f"  1. Review the updated requirements.txt")
        print(f"  2. Run: pip install -r requirements.txt")
        print(f"  3. Test your application")
        print(f"  4. If issues occur, restore from: {backup_path}")
    else:
        print(f"\n🎉 All packages are up to date!")
    
    # Special focus on key tech stack categories
    print(f"\n🔧 Key Tech Stack Categories:")
    print("=" * 50)
    
    categories = {
        "LLM & AI": ["openai", "anthropic", "ollama", "transformers", "torch", "sentence-transformers"],
        "Vector DB": ["qdrant-client", "chromadb", "faiss-cpu"],
        "Embeddings": ["sentence-transformers", "huggingface-hub", "datasets"],
        "Framework": ["fastapi", "uvicorn", "starlette", "pydantic"],
        "Database": ["sqlalchemy", "asyncpg", "aiosqlite", "redis", "aioredis"],
        "Monitoring": ["prometheus_client", "opentelemetry-api", "opentelemetry-sdk"],
        "Testing": ["pytest", "pytest-asyncio", "pytest-cov"],
        "Security": ["bcrypt", "cryptography", "PyJWT", "passlib"]
    }
    
    for category, category_packages in categories.items():
        category_outdated = [p for p in category_packages if p in packages_to_update]
        if category_outdated:
            print(f"  {category}: {len(category_outdated)} packages need update")
            for pkg in category_outdated:
                result = version_results[pkg]
                print(f"    - {pkg}: {result['installed']} -> {result['latest']}")
        else:
            print(f"  {category}: ✅ All up to date")

if __name__ == "__main__":
    main()
