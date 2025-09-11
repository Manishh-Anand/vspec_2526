#!/usr/bin/env python3
"""
Simple test to check server imports and basic functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing server imports...")
    
    # Test finance server imports
    print("1. Testing finance server imports...")
    from servers.finance_http_server import app as finance_app
    print("   ✓ Finance server imports successful")
    
    # Test productivity server imports
    print("2. Testing productivity server imports...")
    from servers.productivity_http_server import app as productivity_app
    print("   ✓ Productivity server imports successful")
    
    # Test basic FastAPI functionality
    print("3. Testing FastAPI functionality...")
    import uvicorn
    print("   ✓ Uvicorn import successful")
    
    print("\n[SUCCESS] All server imports working correctly!")
    print("The servers should be able to start properly.")
    
except Exception as e:
    print(f"\n[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
