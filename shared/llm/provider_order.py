import os
from typing import List

DEFAULT_ORDER = ["ollama_local", "remote_gpu", "huggingface", "openai", "anthropic"]

def get_provider_order() -> List[str]:
    """
    Returns provider preference order, env-driven.
    LLM_PROVIDER_ORDER env allows comma-separated override.
    e.g. 'ollama_local,remote_gpu,huggingface,openai,anthropic'
    
    Provider order prioritizes free GPU options:
    1. ollama_local - Local CPU quantized models (free)
    2. remote_gpu - Remote GPU via Colab/Kaggle/HF Space (free)
    3. huggingface - HuggingFace free tier API
    4. openai - Paid API (only if ENABLE_PAID_API=true)
    5. anthropic - Paid API (only if ENABLE_PAID_API=true)
    """
    raw = os.getenv("LLM_PROVIDER_ORDER", "")
    if raw.strip():
        order = [p.strip().lower() for p in raw.split(",") if p.strip()]
        # keep only known providers; preserve order
        known = [p for p in order if p in DEFAULT_ORDER]
        return known or DEFAULT_ORDER
    return DEFAULT_ORDER
