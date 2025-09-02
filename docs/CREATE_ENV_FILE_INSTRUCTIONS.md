# 🔑 CREATE YOUR .env FILE - STEP BY STEP

## 📍 **LOCATION**
Create this file in your **root directory**: `C:\Users\horiz\OneDrive\ドキュメント\sarvanom\.env`

## 📝 **EXACT CONTENT TO PUT IN .env FILE**

Copy and paste this content, then **replace the placeholder values** with your real API keys:

```env
# SarvanOM 2025 - Environment Configuration
# REPLACE PLACEHOLDER VALUES WITH YOUR REAL API KEYS

# =============================================================================
# LLM API KEYS (CRITICAL - REPLACE THESE!)
# =============================================================================
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# =============================================================================
# LLM SETTINGS
# =============================================================================
LLM_TIMEOUT_SECONDS=15
PRIORITIZE_FREE_MODELS=true
USE_DYNAMIC_SELECTION=true

# =============================================================================
# OLLAMA CONFIGURATION
# =============================================================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=deepseek-r1:8b
OLLAMA_TIMEOUT=15
OLLAMA_LLAMA3=llama3
OLLAMA_LLAMA3_7B=llama3:7b
OLLAMA_LLAMA3_13B=llama3:13b
OLLAMA_MISTRAL=mistral
OLLAMA_CODELLAMA=codellama

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=postgresql://postgres:sarvanom@localhost:5432/sarvanom_db
DATABASE_ENCRYPTION_KEY=your-encryption-key-here
ARANGODB_URL=http://localhost:8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=sarvanom
ARANGODB_DATABASE=sarvanom
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=sarvanom_vectors

# =============================================================================
# SEARCH SERVICES  
# =============================================================================
MEILI_HTTP_ADDR=127.0.0.1:7700
MEILI_MASTER_KEY=sarvanom_master_key_2025

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# =============================================================================
# FEATURE FLAGS
# =============================================================================
ENABLE_MEDIA=false
USE_VECTOR_DB=false
ENABLE_WEB_SEARCH=true
```

## 🎯 **MOST IMPORTANT REPLACEMENTS**

Replace these three lines with your **real API keys**:

1. **OpenAI**: `OPENAI_API_KEY=sk-proj-your-real-openai-key-here`
2. **Anthropic**: `ANTHROPIC_API_KEY=sk-ant-your-real-anthropic-key-here`  
3. **HuggingFace**: `HUGGINGFACE_API_KEY=hf_your-real-huggingface-token-here`

## 🚀 **EXPECTED RESULT**

Once you create the `.env` file with real API keys:

- ✅ **2-5 second AI responses** (instead of timeouts)
- ✅ **Latest GPT-4o and Claude-3.5 models**
- ✅ **Production-quality responses**

## 📋 **QUICK VERIFICATION**

After creating the file, run this to verify:
```bash
.\venv\Scripts\python.exe check_env_status.py
```

You should see "✅ WORKING API KEYS FOUND" instead of placeholders.
