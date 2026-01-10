"""
Load Testing with Locust
Simulates 10K+ concurrent users for performance testing
"""

from locust import HttpUser, task, between
import random
import json


class InsuranceAIBridgeUser(HttpUser):
    """Simulates a user interacting with the Insurance AI Bridge API"""
    
    wait_time = between(1, 3)  # Wait between 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        # Authenticate user
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": f"user_{random.randint(1, 1000)}",
                "password": "test_password"
            }
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def view_claims(self):
        """View claims list - High frequency task"""
        self.client.get("/api/v1/claims", name="View Claims")
    
    @task(2)
    def view_claim_details(self):
        """View specific claim details - Medium frequency task"""
        claim_id = f"claim-{random.randint(1, 10000)}"
        self.client.get(f"/api/v1/claims/{claim_id}", name="View Claim Details")
    
    @task(1)
    def search_claims(self):
        """Search claims - Lower frequency task"""
        query_params = {
            "q": random.choice(["medical", "dental", "vision", "pharmacy"]),
            "limit": random.choice([10, 20, 50]),
            "offset": random.randint(0, 100)
        }
        self.client.get("/api/v1/claims/search", params=query_params, name="Search Claims")
    
    @task(1)
    def create_claim(self):
        """Create new claim - Lower frequency task"""
        claim_data = {
            "member_id": f"member-{random.randint(1, 1000)}",
            "claim_type": random.choice(["medical", "dental", "vision"]),
            "amount": round(random.uniform(100, 10000), 2),
            "provider": f"Provider-{random.randint(1, 100)}",
            "claim_date": "2024-01-15",
            "description": "Test claim for load testing"
        }
        self.client.post("/api/v1/claims", json=claim_data, name="Create Claim")
    
    @task(1)
    def analyze_claim(self):
        """Analyze claim with AI - Lower frequency task"""
        claim_id = f"claim-{random.randint(1, 10000)}"
        self.client.post(
            f"/api/v1/claims/{claim_id}/analyze",
            json={"llm_provider": "openai"},
            name="Analyze Claim"
        )
    
    @task(1)
    def view_analytics(self):
        """View analytics dashboard - Lower frequency task"""
        self.client.get("/api/v1/analytics", params={"range": "30d"}, name="View Analytics")


class HighLoadScenario(HttpUser):
    """High load scenario with rapid requests"""
    
    wait_time = between(0.1, 0.5)  # Very short wait times
    
    @task
    def rapid_requests(self):
        """Rapid fire requests to test system under high load"""
        endpoints = [
            "/api/v1/health",
            "/api/v1/claims",
            "/api/v1/members",
            "/api/v1/policies"
        ]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint, name="Rapid Requests")


# Run with:
# locust -f locustfile.py --host=https://api.insurance-ai-bridge.com --users 10000 --spawn-rate 100

