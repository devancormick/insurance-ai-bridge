"""
Security Testing Suite
SAST, DAST, and penetration testing
"""

import pytest
import requests
from typing import Dict, Any


class TestSecurity:
    """Security test suite"""
    
    BASE_URL = "https://api.insurance-ai-bridge.com"
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Attempt SQL injection in search query
        malicious_inputs = [
            "'; DROP TABLE claims; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users--",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        for malicious_input in malicious_inputs:
            response = requests.get(
                f"{self.BASE_URL}/api/v1/claims/search",
                params={"q": malicious_input}
            )
            # Should return 400 or sanitized response, not execute SQL
            assert response.status_code in [400, 200]
            assert "DROP TABLE" not in response.text
            assert "xp_cmdshell" not in response.text
    
    def test_xss_prevention(self):
        """Test Cross-Site Scripting (XSS) prevention"""
        malicious_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>"
        ]
        
        for malicious_input in malicious_inputs:
            response = requests.post(
                f"{self.BASE_URL}/api/v1/claims",
                json={"description": malicious_input}
            )
            # Should sanitize or reject XSS attempts
            assert "<script>" not in response.text
            assert "javascript:" not in response.text.lower()
    
    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            "/api/v1/claims",
            "/api/v1/members",
            "/api/v1/admin/users"
        ]
        
        for endpoint in protected_endpoints:
            response = requests.get(f"{self.BASE_URL}{endpoint}")
            assert response.status_code == 401  # Unauthorized
    
    def test_authorization_checks(self):
        """Test role-based authorization"""
        # Test regular user cannot access admin endpoints
        user_token = self._get_user_token()
        response = requests.get(
            f"{self.BASE_URL}/api/v1/admin/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403  # Forbidden
    
    def test_rate_limiting(self):
        """Test rate limiting on API endpoints"""
        token = self._get_user_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send rapid requests
        response_count = 0
        rate_limited = False
        
        for _ in range(200):  # Exceed rate limit
            response = requests.get(
                f"{self.BASE_URL}/api/v1/claims",
                headers=headers
            )
            response_count += 1
            
            if response.status_code == 429:  # Too Many Requests
                rate_limited = True
                break
        
        assert rate_limited, "Rate limiting not working"
        assert response_count < 200  # Should be rate limited before 200 requests
    
    def test_https_only(self):
        """Test that HTTP is redirected to HTTPS"""
        http_url = self.BASE_URL.replace("https://", "http://")
        response = requests.get(http_url, allow_redirects=False)
        assert response.status_code in [301, 302, 308]  # Redirect
        assert "https://" in response.headers.get("Location", "")
    
    def test_sensitive_data_masking(self):
        """Test that sensitive data is masked in logs and responses"""
        token = self._get_user_token()
        response = requests.get(
            f"{self.BASE_URL}/api/v1/members/member-123",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = response.json()
        # SSN, credit card numbers should be masked
        if "ssn" in data:
            assert "***-**-****" in data["ssn"] or data["ssn"] == ""
        
        if "credit_card" in data:
            assert "****" in data["credit_card"] or data["credit_card"] == ""
    
    def test_input_validation(self):
        """Test input validation on all endpoints"""
        # Test invalid email
        response = requests.post(
            f"{self.BASE_URL}/api/v1/users",
            json={"email": "invalid-email", "username": "test"}
        )
        assert response.status_code == 400  # Bad Request
        
        # Test negative amounts
        response = requests.post(
            f"{self.BASE_URL}/api/v1/claims",
            json={"amount": -100}
        )
        assert response.status_code == 400  # Bad Request
    
    def test_cors_headers(self):
        """Test CORS headers are properly configured"""
        response = requests.options(
            f"{self.BASE_URL}/api/v1/claims",
            headers={
                "Origin": "https://app.insurance-ai-bridge.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # Check CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
    
    def _get_user_token(self) -> str:
        """Get authentication token for testing"""
        response = requests.post(
            f"{self.BASE_URL}/api/v1/auth/login",
            json={"username": "test_user", "password": "test_password"}
        )
        return response.json().get("access_token")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

