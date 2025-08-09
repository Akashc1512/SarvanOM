"""
Windows Compatibility Module

This module provides Windows-specific compatibility fixes and utilities
for the Universal Knowledge Platform.
"""

import os
import sys
import platform
from typing import Optional

# Windows-specific imports
if platform.system() == "Windows":
    try:
        import asyncio
        import nest_asyncio

        # Apply nest_asyncio for Windows compatibility
        nest_asyncio.apply()
    except ImportError:
        # nest_asyncio not available, continue without it
        pass


def setup_windows_compatibility():
    """Setup Windows-specific compatibility fixes."""
    if platform.system() == "Windows":
        # Set environment variables for Windows
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")

        # Fix for Windows path issues
        if hasattr(os, "add_dll_directory"):
            try:
                # Add current directory to DLL search path
                os.add_dll_directory(os.getcwd())
            except Exception:
                pass


def get_windows_event_loop_policy():
    """Get appropriate event loop policy for Windows."""
    if platform.system() == "Windows":
        try:
            import asyncio

            return asyncio.WindowsProactorEventLoopPolicy()
        except Exception:
            return None
    return None


def setup_windows_event_loop():
    """Setup Windows-specific event loop configuration."""
    if platform.system() == "Windows":
        try:
            import asyncio

            policy = get_windows_event_loop_policy()
            if policy:
                asyncio.set_event_loop_policy(policy)
        except Exception:
            pass


# Auto-setup when module is imported
setup_windows_compatibility()
setup_windows_event_loop()
