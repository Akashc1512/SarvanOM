#!/usr/bin/env python3
"""
Debug environment variables and API connectivity
"""

import os
from dotenv import load_dotenv

# Try to load .env file
try:
    load_dotenv()
    print("✅ .env file loaded successfully")
except Exception as e:
    print(f"⚠️ .env file loading failed: {e}")

print("\n🔍 ENVIRONMENT VARIABLE CHECK:")
print("=" * 40)

# Check critical environment variables
env_vars = [
    ("HUGGINGFACE_API_KEY", "HuggingFace API Key"),
    ("OPENAI_API_KEY", "OpenAI API Key"),
    ("ANTHROPIC_API_KEY", "Anthropic API Key"),
    ("OLLAMA_BASE_URL", "Ollama URL"),
    ("PRIORITIZE_FREE_MODELS", "Free Models Priority"),
    ("USE_DYNAMIC_SELECTION", "Dynamic Selection"),
    ("LLM_TIMEOUT_SECONDS", "LLM Timeout")
]

for var_name, description in env_vars:
    value = os.getenv(var_name)
    if value:
        if "key" in var_name.lower() or "secret" in var_name.lower():
            masked_value = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {description}: {masked_value}")
        else:
            print(f"✅ {description}: {value}")
    else:
        print(f"❌ {description}: NOT SET")

print(f"\n🧪 QUICK API TEST:")
print("=" * 40)

# Test HuggingFace API if key is available
hf_key = os.getenv("HUGGINGFACE_API_KEY")
if hf_key and hf_key != "your_huggingface_api_key_here":
    try:
        import requests
        response = requests.get(
            "https://api-inference.huggingface.co/models/gpt2",
            headers={"Authorization": f"Bearer {hf_key}"},
            timeout=10
        )
        print(f"✅ HuggingFace API: Status {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ HuggingFace API Test Failed: {e}")
else:
    print("⚠️ HuggingFace API: No valid key found")

# Test Ollama if URL is available  
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
try:
    import requests
    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
    print(f"✅ Ollama API: Status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        models = [model.get("name", "unknown") for model in data.get("models", [])]
        print(f"   Available models: {models[:3]}...")
except Exception as e:
    print(f"❌ Ollama API Test Failed: {e}")

print(f"\n💡 RECOMMENDATIONS:")
print("=" * 40)

if not hf_key or hf_key == "your_huggingface_api_key_here":
    print("🔑 Get HuggingFace API key from: https://huggingface.co/settings/tokens")
    print("   - Create a free account")
    print("   - Generate a read token")
    print("   - Add it to your .env file")

print("🔄 For immediate testing without API keys:")
print("   - The system will use intelligent fallback responses")
print("   - Real AI responses require valid API keys")
print("   - Mock responses have been removed per your request")

if __name__ == "__main__":
    pass
