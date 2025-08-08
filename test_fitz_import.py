#!/usr/bin/env python3
"""
Test script to check fitz import
"""

import sys
import traceback

def test_fitz_import():
    """Test if fitz can be imported."""
    try:
        print("Testing fitz import...")
        import fitz
        print("✅ fitz imported successfully")
        print(f"fitz version: {fitz.version}")
        print(f"fitz file: {fitz.__file__}")
        return True
    except Exception as e:
        print(f"❌ fitz import failed: {e}")
        traceback.print_exc()
        return False

def test_pymupdf_import():
    """Test if PyMuPDF can be imported."""
    try:
        print("Testing PyMuPDF import...")
        import PyMuPDF
        print("✅ PyMuPDF imported successfully")
        print(f"PyMuPDF file: {PyMuPDF.__file__}")
        return True
    except Exception as e:
        print(f"❌ PyMuPDF import failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("=== Fitz Import Test ===")
    
    # Test 1: fitz import
    if not test_fitz_import():
        print("❌ fitz import test failed")
        sys.exit(1)
    
    # Test 2: PyMuPDF import
    if not test_pymupdf_import():
        print("❌ PyMuPDF import test failed")
        sys.exit(1)
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    main() 