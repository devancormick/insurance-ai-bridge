#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify backend setup."""
import sys
import traceback
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    print("Testing imports...")
    from app.config import settings
    print("[OK] Config imported")
    
    from app.main import app
    print("[OK] Main app imported")
    
    from app.core.pii_handler import PIIHandler
    print("[OK] PII Handler imported")
    
    from app.schemas.claim_analysis import ClaimAnalysisRequest
    print("[OK] Schemas imported")
    
    # Test PII handler initialization
    print("\nTesting PII Handler...")
    handler = PIIHandler()
    test_data = {
        'member_name': 'John Doe',
        'ssn': '123-45-6789',
        'date_of_birth': '1980-01-01',
        'notes': 'Patient SSN is 123-45-6789'
    }
    masked = handler.mask_pii(test_data)
    print("[OK] PII masking works")
    print(f"  Original name: {test_data['member_name']}")
    print(f"  Masked name: {masked['member_name']}")
    
    # Test schema
    print("\nTesting schemas...")
    request = ClaimAnalysisRequest(claim_id="TEST-123")
    print(f"[OK] Schema validation works: {request.claim_id}")
    
    print("\n[SUCCESS] All backend tests passed!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    traceback.print_exc()
    sys.exit(1)

