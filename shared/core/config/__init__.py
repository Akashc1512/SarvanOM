"""
Configuration Management Module - SarvanOM

This module provides centralized configuration management for all services.
"""

from .central_config import get_central_config, CentralConfig

__all__ = [
    "get_central_config",
    "CentralConfig",
]
