"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "status" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "metrics" in data


def test_health_metrics():
    """Test health metrics in response."""
    response = client.get("/health")
    data = response.json()
    
    assert "metrics" in data
    metrics = data["metrics"]
    assert "uptime_seconds" in metrics
    assert "requests_total" in metrics
    assert isinstance(metrics["uptime_seconds"], int)


def test_claims_analyze_endpoint():
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
    
    if data["data"]:
        analysis = data["data"]
        assert "claim_id" in analysis
        assert "status" in analysis
        assert "confidence_score" in analysis


def test_auth_login_endpoint_invalid_credentials():
    """Test auth login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "invalid",
            "password": "invalid"
        }
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_auth_login_endpoint_valid_credentials():
    """Test auth login with valid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_auth_me_endpoint_requires_auth():
    """Test that /auth/me requires authentication."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401


def test_auth_me_endpoint_with_token():
    """Test /auth/me with valid token."""
    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Use token to access /me
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "email" in data


def test_rate_limiting_headers():
    """Test that rate limiting headers are present."""
    response = client.get("/")
    
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


def test_process_time_header():
    """Test that process time header is present."""
    response = client.get("/")
    
    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0

