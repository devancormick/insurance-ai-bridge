#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test API endpoints."""
import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data
    print("[OK] Root endpoint works")

def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("[OK] Health endpoint works")

def test_claims_analyze():
    """Test claim analysis endpoint."""
    response = client.post(
        "/api/v1/claims/TEST-123/analyze",
        json={
            "claim_id": "TEST-123",
            "include_member_history": True,
            "include_policy_docs": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "processing_time_ms" in data
    print("[OK] Claim analysis endpoint works")
    print(f"    Processing time: {data['processing_time_ms']}ms")

if __name__ == "__main__":
    print("Testing API endpoints...\n")
    try:
        test_root()
        test_health()
        test_claims_analyze()
        print("\n[SUCCESS] All API tests passed!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

