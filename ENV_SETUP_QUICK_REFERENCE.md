# .env Setup Quick Reference

## 🚀 Essential Zero Budget LLM Variables

Add these to your `.env` file for the zero-budget LLM integration:

### **Ollama Configuration (Local - FREE)**
```bash
# Enable Ollama provider
OLLAMA_ENABLED=true

# Default model
OLLAMA_MODEL=llama3.2:3b

# Server URL
OLLAMA_BASE_URL=http://localhost:11434
```

### **Hugging Face Configuration (API - FREE)**
```bash
# Get tokens from: https://huggingface.co/settings/tokens
HUGGINGFACE_WRITE_TOKEN=your_write_token_here
HUGGINGFACE_READ_TOKEN=your_read_token_here
HUGGINGFACE_API_KEY=your_legacy_api_key_here

# Default model
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium
```

### **Model Selection Configuration**
```bash
# Enable dynamic model selection
USE_DYNAMIC_SELECTION=true

# Prioritize free models
PRIORITIZE_FREE_MODELS=true
```

## 🔧 Optional Fallback Providers

If you want paid providers as fallbacks:

```bash
# OpenAI (Paid - Fallback)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_LLM_MODEL=gpt-4o-mini

# Anthropic (Paid - Fallback)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ANTHROPIC_MODEL=claude-3-haiku-20240307

# Azure (Paid - Fallback)
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here

# Google (Paid - Fallback)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-pro
```

## 📊 System Configuration

```bash
# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_TOKENS_PER_MINUTE=10000

# Agent configuration
AGENT_TIMEOUT_SECONDS=30
AGENT_MAX_RETRIES=3
```

## 🎯 Priority Order

The system will use providers in this order:

1. **Ollama** (if `OLLAMA_ENABLED=true` and models available)
2. **Hugging Face** (if tokens available)
3. **Paid providers** (as fallbacks)

## 🔍 Token Types Explained

### Hugging Face Tokens:
- **Write Token**: Full access (recommended)
- **Read Token**: Read-only access
- **Legacy API Key**: Backward compatibility

### How to get tokens:
1. Go to https://huggingface.co/settings/tokens
2. Create new token
3. Choose appropriate permissions
4. Copy token to `.env` file

## ✅ Quick Setup Checklist

- [ ] `OLLAMA_ENABLED=true`
- [ ] `OLLAMA_MODEL=llama3.2:3b`
- [ ] `HUGGINGFACE_WRITE_TOKEN=your_token` (optional)
- [ ] `HUGGINGFACE_READ_TOKEN=your_token` (optional)
- [ ] `USE_DYNAMIC_SELECTION=true`
- [ ] `PRIORITIZE_FREE_MODELS=true`

## 🧪 Test Your Setup

```bash
# Test the integration
python quick_start_zero_budget.py

# Check provider health
python scripts/manage_zero_budget_llm.py --test

# Monitor usage
python scripts/manage_zero_budget_llm.py --dashboard
```

## 💡 Tips

1. **Start with Ollama only** - It's completely free and local
2. **Add Hugging Face later** - For additional free API access
3. **Keep paid providers as fallbacks** - For reliability
4. **Use the monitoring dashboard** - To track usage and savings

## 🚨 Important Notes

- **Never commit `.env` files** with real tokens to version control
- **Use strong, unique tokens** for each service
- **Rotate tokens regularly** for security
- **Monitor usage** to stay within free tiers 