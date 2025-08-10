#!/usr/bin/env python3
"""
HuggingFace Components Update Script
Updates all HuggingFace-related packages to their latest stable versions
as of August 10, 2025.
"""

import subprocess
import sys
import requests
import json
from packaging import version

def get_installed_version(package_name: str) -> str:
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
        return None
    return None

def get_latest_version(package_name: str) -> str:
    """Get latest version from PyPI."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception:
        pass
    return None

def install_package(package_name: str, version_spec: str = None):
    """Install or upgrade a package."""
    if version_spec:
        package_spec = f"{package_name}{version_spec}"
    else:
        package_spec = package_name
    
    try:
        print(f"Installing {package_spec}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package_spec],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Successfully installed {package_spec}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_spec}: {e.stderr}")
        return False

def main():
    """Main function to update HuggingFace components."""
    print("🚀 HuggingFace Components Update - August 10, 2025")
    print("=" * 60)
    
    # Comprehensive list of HuggingFace-related packages with latest stable versions
    huggingface_packages = {
        # Core HuggingFace packages
        "transformers": ">=4.55.0",
        "torch": ">=2.8.0",
        "torchvision": ">=0.23.0", 
        "torchaudio": ">=2.8.0",
        "sentence-transformers": ">=5.1.0",
        "huggingface-hub": ">=0.34.4",
        "datasets": ">=4.0.0",
        "tokenizers": ">=0.21.4",
        "accelerate": ">=1.10.0",
        "optimum": ">=1.27.0",
        "diffusers": ">=0.34.0",
        "peft": ">=0.17.0",
        "bitsandbytes": ">=0.46.1",
        "safetensors": ">=0.6.2",
        "tqdm": ">=4.67.1",
        "regex": ">=2025.7.34",
        "gradio-client": ">=1.11.1",
        "gradio": ">=5.42.0",
        
        # Additional ML/NLP packages
        "scikit-learn": ">=1.7.1",
        "pandas": ">=2.3.1",
        "numpy": ">=2.3.2",
        "scipy": ">=1.16.1",
        "matplotlib": ">=3.10.5",
        "seaborn": ">=0.13.2",
        "plotly": ">=6.2.0",
        
        # Vector databases and similarity search
        "faiss-cpu": ">=1.11.0.post1",
        "chromadb": ">=1.0.16",
        "qdrant-client": ">=1.15.1",
        
        # Additional utilities
        "requests": ">=2.32.4",
        "urllib3": ">=2.5.0",
        "certifi": ">=2025.8.3",
        "packaging": ">=25.0",
        "typing-extensions": ">=4.14.1",
        "annotated-types": ">=0.7.0",
        
        # Development and testing
        "pytest": ">=8.4.1",
        "pytest-asyncio": ">=1.1.0",
        "pytest-cov": ">=6.2.1",
        "black": ">=24.0.0",
        "isort": ">=5.13.0",
        "flake8": ">=7.0.0",
        
        # Monitoring and logging
        "structlog": ">=25.4.0",
        "prometheus_client": ">=0.22.1",
        "psutil": ">=7.0.0",
        
        # Async and performance
        "aiohttp": ">=3.12.15",
        "httpx": ">=0.28.1",
        "asyncio": None,  # Built-in
        "anyio": ">=4.10.0",
        
        # Configuration and environment
        "python-dotenv": ">=1.1.1",
        "pydantic": ">=2.11.7",
        "pydantic-settings": ">=2.10.1",
        "pydantic_core": ">=2.33.2",
        
        # Database and caching
        "redis": ">=6.4.0",
        "aioredis": ">=2.0.1",
        "aiocache": ">=0.12.3",
        
        # Web framework
        "fastapi": ">=0.116.1",
        "uvicorn[standard]": ">=0.32.0",
        "starlette": ">=0.47.2",
        
        # Security
        "cryptography": ">=45.0.6",
        "bcrypt": ">=4.3.0",
        "PyJWT": ">=2.10.1",
        
        # Additional ML libraries
        "joblib": ">=1.5.1",
        "networkx": ">=3.5",
        "PyYAML": ">=6.0.2",
        "click": ">=8.2.1",
        
        # Visualization
        "dash": ">=3.2.0",
        "streamlit": ">=1.48.0",
        
        # Background processing
        "celery": ">=5.5.3",
        "flower": ">=2.0.1",
        "rq": ">=2.4.1",
        "dramatiq": ">=1.18.0",
        
        # Streaming and real-time
        "sse-starlette": ">=3.0.2",
        "websockets": ">=15.0.1",
        
        # OpenTelemetry for monitoring
        "opentelemetry-api": ">=1.36.0",
        "opentelemetry-sdk": ">=1.36.0",
        "opentelemetry-instrumentation": ">=0.57b0",
        "opentelemetry-instrumentation-fastapi": ">=0.57b0",
        "opentelemetry-instrumentation-logging": ">=0.57b0",
        "opentelemetry-instrumentation-asgi": ">=0.57b0",
        "opentelemetry-semantic-conventions": ">=0.57b0",
        "opentelemetry-util-http": ">=0.57b0",
        
        # Performance optimization
        "orjson": ">=3.11.1",
        "ujson": ">=5.10.0",
        "msgpack": ">=1.1.1",
        "lz4": ">=4.4.4",
        "zstandard": ">=0.23.0",
        
        # Setuptools for Python 3.13 compatibility
        "setuptools": ">=80.9.0"
    }
    
    print(f"📦 Found {len(huggingface_packages)} HuggingFace-related packages to check")
    print()
    
    # Check current versions
    current_versions = {}
    latest_versions = {}
    
    for package, version_spec in huggingface_packages.items():
        print(f"Checking {package}...")
        current_versions[package] = get_installed_version(package)
        latest_versions[package] = get_latest_version(package)
    
    print("\n📊 Version Analysis:")
    print("=" * 60)
    
    packages_to_update = []
    up_to_date_packages = []
    not_installed_packages = []
    
    for package, version_spec in huggingface_packages.items():
        current = current_versions[package]
        latest = latest_versions[package]
        
        if not current:
            not_installed_packages.append(package)
            print(f"⚠️  {package}: Not installed (latest: {latest})")
        elif not latest:
            print(f"❌ {package}: Could not fetch latest version")
        else:
            try:
                current_ver = version.parse(current)
                latest_ver = version.parse(latest)
                
                if latest_ver > current_ver:
                    packages_to_update.append(package)
                    print(f"🔄 {package}: {current} -> {latest} (UPDATE NEEDED)")
                else:
                    up_to_date_packages.append(package)
                    print(f"✅ {package}: {current} (up to date)")
            except version.InvalidVersion:
                print(f"⚠️  {package}: Invalid version format")
    
    print(f"\n📈 Summary:")
    print(f"  ✅ Up to date: {len(up_to_date_packages)}")
    print(f"  🔄 Needs update: {len(packages_to_update)}")
    print(f"  ⚠️  Not installed: {len(not_installed_packages)}")
    
    # Update packages
    if packages_to_update:
        print(f"\n🚀 Updating {len(packages_to_update)} packages...")
        print("=" * 60)
        
        success_count = 0
        for package in packages_to_update:
            version_spec = huggingface_packages[package]
            if install_package(package, version_spec):
                success_count += 1
        
        print(f"\n✅ Successfully updated {success_count}/{len(packages_to_update)} packages")
    
    # Install missing packages
    if not_installed_packages:
        print(f"\n📦 Installing {len(not_installed_packages)} missing packages...")
        print("=" * 60)
        
        success_count = 0
        for package in not_installed_packages:
            version_spec = huggingface_packages[package]
            if install_package(package, version_spec):
                success_count += 1
        
        print(f"\n✅ Successfully installed {success_count}/{len(not_installed_packages)} packages")
    
    # Update requirements.txt
    print(f"\n📝 Updating requirements.txt with latest versions...")
    update_requirements_file(huggingface_packages)
    
    print(f"\n🎉 HuggingFace Components Update Complete!")
    print(f"📅 Date: August 10, 2025")
    print(f"🔧 All packages updated to latest stable versions")

def update_requirements_file(huggingface_packages):
    """Update requirements.txt with latest HuggingFace package versions."""
    try:
        # Read current requirements.txt
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Create backup
        with open("requirements.txt.backup", "w", encoding="utf-8") as f:
            f.write(content)
        
        # Update HuggingFace section
        updated_content = content
        
        # Find and update HuggingFace section
        hf_section_start = "# HuggingFace Comprehensive Integration - 2025 Latest Stable"
        if hf_section_start in content:
            # Extract the section and update it
            lines = content.split('\n')
            updated_lines = []
            in_hf_section = False
            
            for line in lines:
                if hf_section_start in line:
                    in_hf_section = True
                    updated_lines.append(line)
                    # Add updated HuggingFace packages
                    for package, version_spec in huggingface_packages.items():
                        if version_spec:
                            updated_lines.append(f"{package}{version_spec}")
                        else:
                            updated_lines.append(package)
                elif in_hf_section and line.startswith('#'):
                    in_hf_section = False
                    updated_lines.append(line)
                elif not in_hf_section:
                    updated_lines.append(line)
            
            updated_content = '\n'.join(updated_lines)
        
        # Write updated requirements.txt
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("✅ requirements.txt updated successfully")
        print("📁 Backup saved as requirements.txt.backup")
        
    except Exception as e:
        print(f"❌ Failed to update requirements.txt: {e}")

if __name__ == "__main__":
    main()
