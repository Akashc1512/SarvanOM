#!/usr/bin/env python3
"""
Check Ollama Models
"""

import requests
import json

def check_ollama_models():
    """Check what Ollama models are available."""
    print("🔍 Checking Ollama Models")
    print("=" * 40)
    
    try:
        # Get available models
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models.get('models', []))} models:")
            
            for model in models.get('models', []):
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                modified_at = model.get('modified_at', 'Unknown')
                
                # Convert size to human readable
                if size > 1024**3:
                    size_str = f"{size / (1024**3):.1f} GB"
                elif size > 1024**2:
                    size_str = f"{size / (1024**2):.1f} MB"
                else:
                    size_str = f"{size / 1024:.1f} KB"
                
                print(f"   📦 {name}")
                print(f"      Size: {size_str}")
                print(f"      Modified: {modified_at}")
                print()
            
            # Recommend the best model for guardrails
            if models.get('models'):
                best_model = models['models'][0]['name']  # First available model
                print(f"💡 RECOMMENDATION:")
                print(f"   Use '{best_model}' for OLLAMA_MODEL in .env")
                print(f"   OLLAMA_BASE_URL=http://localhost:11434")
                
        else:
            print(f"❌ Failed to get models: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking models: {e}")

if __name__ == "__main__":
    check_ollama_models()
