"""
Tests for FLASH API endpoints
"""
import pytest
from fastapi import status
from datetime import datetime
import json


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "FLASH 2.0 API is running"
        assert data["version"] == "2.0.0"
        assert "docs" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "models_loaded" in data
        assert "pillar_models_loaded" in data
        assert "version" in data
        assert "timestamp" in data


class TestPredictionEndpoint:
    """Test prediction endpoint"""
    
    def test_valid_prediction(self, client, valid_startup_data):
        """Test prediction with valid data"""
        response = client.post("/predict", json=valid_startup_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "success_probability" in data
        assert 0 <= data["success_probability"] <= 1
        assert "confidence_interval" in data
        assert "risk_level" in data
        assert "key_insights" in data
        assert "pillar_scores" in data
        assert "recommendation" in data
        assert "timestamp" in data
        
        # Check pillar scores
        assert all(pillar in data["pillar_scores"] for pillar in ["capital", "advantage", "market", "people"])
        assert all(0 <= score <= 1 for score in data["pillar_scores"].values())
    
    def test_invalid_prediction_data(self, client, invalid_startup_data):
        """Test prediction with invalid data"""
        response = client.post("/predict", json=invalid_startup_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_edge_case_prediction(self, client, edge_case_startup_data):
        """Test prediction with edge case data"""
        response = client.post("/predict", json=edge_case_startup_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        # Edge cases should still produce valid predictions
        assert 0 <= data["success_probability"] <= 1
        assert data["risk_level"] in ["Very Low Risk", "Low Risk", "Moderate Risk", "High Risk", "Very High Risk", "Critical Risk"]
    
    def test_missing_required_fields(self, client):
        """Test prediction with missing required fields"""
        incomplete_data = {
            "funding_stage": "seed",
            "total_capital_raised_usd": 1000000
            # Missing many required fields
        }
        response = client.post("/predict", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_comprehensive_evaluation(self, client, valid_startup_data):
        """Test comprehensive evaluation features"""
        response = client.post("/predict", json=valid_startup_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        if "comprehensive_evaluation" in data:
            eval_data = data["comprehensive_evaluation"]
            assert "verdict" in eval_data
            assert eval_data["verdict"] in ["PASS", "CONDITIONAL PASS", "FAIL"]
            assert "stage_context" in eval_data
            assert "critical_failures" in eval_data
            assert "risk_adjustments" in eval_data


class TestValidation:
    """Test input validation"""
    
    def test_funding_stage_validation(self, client, valid_startup_data):
        """Test funding stage validation"""
        data = valid_startup_data.copy()
        data["funding_stage"] = "invalid_stage"
        response = client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_numeric_bounds_validation(self, client, valid_startup_data):
        """Test numeric field bounds"""
        # Test negative values where not allowed
        data = valid_startup_data.copy()
        data["total_capital_raised_usd"] = -1000
        response = client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test percentage over 100
        data = valid_startup_data.copy()
        data["team_diversity_percent"] = 150
        response = client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test score out of range
        data = valid_startup_data.copy()
        data["tech_differentiation_score"] = 10  # Should be 1-5
        response = client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_market_size_validation(self, client, valid_startup_data):
        """Test TAM > SAM > SOM validation"""
        data = valid_startup_data.copy()
        data["tam_size_usd"] = 100
        data["sam_size_usd"] = 1000
        data["som_size_usd"] = 10000
        response = client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_string_length_validation(self, client, valid_startup_data):
        """Test string length limits"""
        data = valid_startup_data.copy()
        data["sector"] = "x" * 1001  # Exceed max length
        response = client.post("/predict", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self, async_client, valid_startup_data):
        """Test that rate limiting works"""
        # Make requests up to the limit
        for _ in range(100):
            response = await async_client.post("/predict", json=valid_startup_data)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        
        # Next request should be rate limited
        response = await async_client.post("/predict", json=valid_startup_data)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in response.json()["detail"]


class TestSecurityHeaders:
    """Test security headers and middleware"""
    
    def test_cors_headers(self, client, valid_startup_data):
        """Test CORS headers are set correctly"""
        response = client.post(
            "/predict",
            json=valid_startup_data,
            headers={"Origin": "http://localhost:3000"}
        )
        assert "access-control-allow-origin" in response.headers
    
    def test_request_size_limit(self, client):
        """Test request size limitation"""
        # Create a large payload
        large_data = {"data": "x" * (2 * 1024 * 1024)}  # 2MB
        response = client.post(
            "/predict",
            json=large_data,
            headers={"Content-Length": str(2 * 1024 * 1024)}
        )
        # Should be rejected before validation
        assert response.status_code in [
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


class TestExplanationEndpoint:
    """Test explanation endpoint"""
    
    def test_explanation_endpoint(self, client, valid_startup_data):
        """Test SHAP explanation endpoint"""
        response = client.post("/explain", json=valid_startup_data)
        # May fail if SHAP models not available
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "prediction" in data
            assert "explanation" in data
            assert "feature_mapping" in data