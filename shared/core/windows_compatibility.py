"""
Windows Compatibility Module for SarvanOM

This module provides Windows-specific compatibility fixes and utilities.
"""

import os
import sys
import asyncio
from typing import Any, Optional

def setup_windows_compatibility():
    """Setup Windows-specific compatibility fixes."""
    if sys.platform == "win32":
        # Fix for Windows event loop policy
        if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Fix for Windows console encoding
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
            except Exception:
                pass
        
        # Set environment variables for better Windows compatibility
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        os.environ.setdefault('PYTHONLEGACYWINDOWSSTDIO', '1')

def get_windows_specific_config() -> dict:
    """Get Windows-specific configuration."""
    if sys.platform != "win32":
        return {}
    
    return {
        "event_loop_policy": "WindowsProactorEventLoopPolicy",
        "console_encoding": "utf-8",
        "path_separator": "\\",
        "temp_dir": os.environ.get('TEMP', 'C:\\Windows\\Temp')
    }

# Auto-setup on import
setup_windows_compatibility()
