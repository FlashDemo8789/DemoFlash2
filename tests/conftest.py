"""
Test configuration and fixtures for FLASH API tests
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_server import app
from config import settings

# Override settings for testing
settings.ENVIRONMENT = "testing"
settings.RATE_LIMIT_REQUESTS = 1000
settings.RATE_LIMIT_WINDOW = 1


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def valid_startup_data():
    """Valid startup data for testing."""
    return {
        "funding_stage": "seed",
        "total_capital_raised_usd": 2000000,
        "cash_on_hand_usd": 1500000,
        "monthly_burn_usd": 100000,
        "runway_months": 15,
        "annual_revenue_run_rate": 500000,
        "revenue_growth_rate_percent": 20,
        "gross_margin_percent": 70,
        "burn_multiple": 2.5,
        "ltv_cac_ratio": 3.0,
        "investor_tier_primary": "tier_2",
        "has_debt": False,
        "patent_count": 2,
        "network_effects_present": True,
        "has_data_moat": False,
        "regulatory_advantage_present": False,
        "tech_differentiation_score": 4.0,
        "switching_cost_score": 3.5,
        "brand_strength_score": 3.0,
        "scalability_score": 0.7,
        "product_stage": "beta",
        "product_retention_30d": 0.6,
        "product_retention_90d": 0.45,
        "sector": "SaaS",
        "tam_size_usd": 10000000000,
        "sam_size_usd": 1000000000,
        "som_size_usd": 100000000,
        "market_growth_rate_percent": 25,
        "customer_count": 50,
        "customer_concentration_percent": 20,
        "user_growth_rate_percent": 30,
        "net_dollar_retention_percent": 110,
        "competition_intensity": 3.5,
        "competitors_named_count": 10,
        "dau_mau_ratio": 0.4,
        "founders_count": 2,
        "team_size_full_time": 15,
        "years_experience_avg": 10,
        "domain_expertise_years_avg": 7,
        "prior_startup_experience_count": 2,
        "prior_successful_exits_count": 1,
        "board_advisor_experience_score": 4.0,
        "advisors_count": 5,
        "team_diversity_percent": 40,
        "key_person_dependency": False
    }


@pytest.fixture
def invalid_startup_data():
    """Invalid startup data for testing validation."""
    return {
        "funding_stage": "invalid_stage",
        "total_capital_raised_usd": -1000,
        "cash_on_hand_usd": "not_a_number",
        "monthly_burn_usd": -50000,
        "tam_size_usd": 100,
        "sam_size_usd": 1000,
        "som_size_usd": 10000,  # SOM > SAM > TAM (invalid)
        "founders_count": 0,
        "team_diversity_percent": 150  # >100%
    }


@pytest.fixture
def edge_case_startup_data():
    """Edge case startup data for testing."""
    return {
        "funding_stage": "pre_seed",
        "total_capital_raised_usd": 0,
        "cash_on_hand_usd": 0,
        "monthly_burn_usd": 0,
        "runway_months": None,
        "annual_revenue_run_rate": 0,
        "revenue_growth_rate_percent": -50,
        "gross_margin_percent": -20,
        "burn_multiple": None,
        "ltv_cac_ratio": 0,
        "investor_tier_primary": "none",
        "has_debt": True,
        "patent_count": 0,
        "network_effects_present": False,
        "has_data_moat": False,
        "regulatory_advantage_present": False,
        "tech_differentiation_score": 1.0,
        "switching_cost_score": 1.0,
        "brand_strength_score": 1.0,
        "scalability_score": 0,
        "product_stage": "concept",
        "product_retention_30d": 0,
        "product_retention_90d": 0,
        "sector": "Unknown",
        "tam_size_usd": 1000000,
        "sam_size_usd": 500000,
        "som_size_usd": 100000,
        "market_growth_rate_percent": -10,
        "customer_count": 0,
        "customer_concentration_percent": 100,
        "user_growth_rate_percent": -20,
        "net_dollar_retention_percent": 50,
        "competition_intensity": 5.0,
        "competitors_named_count": 100,
        "dau_mau_ratio": 0,
        "founders_count": 1,
        "team_size_full_time": 1,
        "years_experience_avg": 0,
        "domain_expertise_years_avg": 0,
        "prior_startup_experience_count": 0,
        "prior_successful_exits_count": 0,
        "board_advisor_experience_score": 1.0,
        "advisors_count": 0,
        "team_diversity_percent": 0,
        "key_person_dependency": True
    }