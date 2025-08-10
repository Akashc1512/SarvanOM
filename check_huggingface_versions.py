#!/usr/bin/env python3
"""
Check and verify latest HuggingFace package versions
Ensures we're using the latest stable versions as of 2025
"""

import subprocess
import sys
import pkg_resources
from typing import Dict, List, Tuple

def get_installed_version(package_name: str) -> str:
    """Get installed version of a package"""
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return "Not installed"

def get_latest_version(package_name: str) -> str:
    """Get latest version from PyPI"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "index", "versions", package_name
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Parse the output to get the latest version
            lines = result.stdout.split('\n')
            for line in lines:
                if 'LATEST:' in line:
                    return line.split('LATEST:')[1].strip()
        return "Unknown"
    except Exception:
        return "Error checking"

def check_huggingface_packages() -> Dict[str, Dict[str, str]]:
    """Check all HuggingFace related packages"""
    
    packages = {
        "transformers": {"required": ">=4.60.0", "description": "Core transformers library"},
        "torch": {"required": ">=2.6.0", "description": "PyTorch deep learning framework"},
        "torchvision": {"required": ">=0.21.0", "description": "PyTorch computer vision"},
        "torchaudio": {"required": ">=0.21.0", "description": "PyTorch audio processing"},
        "sentence-transformers": {"required": ">=3.3.0", "description": "Sentence embeddings"},
        "huggingface-hub": {"required": ">=0.28.0", "description": "HuggingFace Hub client"},
        "datasets": {"required": ">=2.20.0", "description": "Datasets library"},
        "tokenizers": {"required": ">=0.21.0", "description": "Fast tokenizers"},
        "accelerate": {"required": ">=0.34.0", "description": "Accelerated training"},
        "optimum": {"required": ">=1.22.0", "description": "Optimization library"},
        "diffusers": {"required": ">=0.37.0", "description": "Diffusion models"},
        "peft": {"required": ">=0.14.0", "description": "Parameter efficient fine-tuning"},
        "bitsandbytes": {"required": ">=0.45.0", "description": "Quantization library"},
        "safetensors": {"required": ">=0.4.6", "description": "Safe tensor serialization"},
        "tqdm": {"required": ">=4.68.0", "description": "Progress bars"},
        "regex": {"required": ">=2025.1.0", "description": "Regular expressions"},
        "gradio-client": {"required": ">=1.0.0", "description": "Gradio client"},
        "huggingface-cli": {"required": ">=0.3.0", "description": "HuggingFace CLI"},
        "python-dotenv": {"required": ">=1.1.1", "description": "Environment variable loading"}
    }
    
    results = {}
    
    print("🔍 CHECKING HUGGINGFACE PACKAGE VERSIONS")
    print("=" * 60)
    
    for package, info in packages.items():
        installed = get_installed_version(package)
        latest = get_latest_version(package)
        
        results[package] = {
            "installed": installed,
            "latest": latest,
            "required": info["required"],
            "description": info["description"]
        }
        
        status = "✅" if installed != "Not installed" else "❌"
        print(f"{status} {package:<20} | Installed: {installed:<12} | Latest: {latest:<12} | {info['description']}")
    
    return results

def check_environment_variables() -> Dict[str, bool]:
    """Check if HuggingFace environment variables are set"""
    
    import os
    from dotenv import load_dotenv
    
    # Load .env file
    load_dotenv()
    
    env_vars = {
        "HUGGINGFACE_READ_TOKEN": "Read token for downloading models",
        "HUGGINGFACE_WRITE_TOKEN": "Write token for uploading models", 
        "HUGGINGFACE_API_TOKEN": "API token for HuggingFace API access",
        "HF_CACHE_DIR": "Cache directory for models",
        "HF_DEVICE": "Device to use (cpu/cuda/auto)",
        "HF_MAX_MODELS": "Maximum models to keep in memory"
    }
    
    results = {}
    
    print("\n🔑 CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        status = "✅" if value else "❌"
        display_value = value[:20] + "..." if value and len(value) > 20 else value or "Not set"
        print(f"{status} {var:<25} | {display_value:<25} | {description}")
        results[var] = bool(value)
    
    return results

def check_huggingface_imports() -> Dict[str, bool]:
    """Check if HuggingFace packages can be imported"""
    
    imports_to_test = {
        "transformers": "from transformers import AutoTokenizer, AutoModel",
        "torch": "import torch",
        "sentence_transformers": "from sentence_transformers import SentenceTransformer",
        "huggingface_hub": "from huggingface_hub import InferenceClient, HfApi",
        "datasets": "from datasets import load_dataset",
        "accelerate": "import accelerate",
        "diffusers": "import diffusers",
        "peft": "import peft",
        "python-dotenv": "from dotenv import load_dotenv"
    }
    
    results = {}
    
    print("\n🧪 TESTING HUGGINGFACE IMPORTS")
    print("=" * 60)
    
    for package, import_statement in imports_to_test.items():
        try:
            exec(import_statement)
            status = "✅"
            results[package] = True
        except ImportError as e:
            status = "❌"
            results[package] = False
            import_statement = f"{import_statement} - {str(e)}"
        except Exception as e:
            status = "⚠️"
            results[package] = False
            import_statement = f"{import_statement} - {str(e)}"
        
        print(f"{status} {package:<20} | {import_statement}")
    
    return results

def generate_upgrade_commands(package_results: Dict[str, Dict[str, str]]) -> List[str]:
    """Generate pip upgrade commands for outdated packages"""
    
    commands = []
    
    print("\n📦 UPGRADE COMMANDS (if needed)")
    print("=" * 60)
    
    for package, info in package_results.items():
        if info["installed"] != "Not installed" and info["latest"] != "Unknown" and info["latest"] != "Error checking":
            # Simple version comparison (this could be more sophisticated)
            if info["installed"] != info["latest"]:
                cmd = f"pip install --upgrade {package}"
                commands.append(cmd)
                print(f"🔄 {cmd}")
    
    if not commands:
        print("✅ All packages are up to date!")
    
    return commands

def main():
    """Main function to run all checks"""
    
    print("🚀 HUGGINGFACE TECH STACK VALIDATION")
    print("=" * 60)
    print("Checking packages, environment variables, and imports...")
    
    # Check package versions
    package_results = check_huggingface_packages()
    
    # Check environment variables
    env_results = check_environment_variables()
    
    # Check imports
    import_results = check_huggingface_imports()
    
    # Generate upgrade commands
    upgrade_commands = generate_upgrade_commands(package_results)
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    total_packages = len(package_results)
    installed_packages = sum(1 for info in package_results.values() if info["installed"] != "Not installed")
    working_imports = sum(1 for working in import_results.values() if working)
    env_vars_set = sum(1 for set_var in env_results.values() if set_var)
    
    print(f"📦 Packages: {installed_packages}/{total_packages} installed")
    print(f"🧪 Imports: {working_imports}/{len(import_results)} working")
    print(f"🔑 Environment: {env_vars_set}/{len(env_results)} variables set")
    
    if installed_packages == total_packages and working_imports == len(import_results):
        print("\n🎉 All HuggingFace packages are properly installed and working!")
    else:
        print("\n⚠️ Some packages need attention. Check the details above.")
    
    if env_vars_set < len(env_results):
        print("\n💡 Tip: Set missing environment variables in your .env file")
        print("   See HUGGINGFACE_SETUP_GUIDE.md for details")

if __name__ == "__main__":
    main()
