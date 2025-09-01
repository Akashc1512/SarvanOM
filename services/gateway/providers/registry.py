from typing import Dict, Type
from shared.llm.provider_order import get_provider_order

_REGISTRY: Dict[str, object] = {}

def register(name: str, provider: object) -> None:
    _REGISTRY[name.lower()] = provider

def get_registry() -> Dict[str, object]:
    return dict(_REGISTRY)

def get_ordered_providers() -> Dict[str, object]:
    order = get_provider_order()
    reg = get_registry()
    # return subset in order
    return {k: reg[k] for k in order if k in reg}


