"""
Tests for input validation and data processing
"""
import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_server import StartupMetrics


class TestStartupMetricsValidation:
    """Test StartupMetrics model validation"""
    
    def test_valid_metrics_creation(self, valid_startup_data):
        """Test creating metrics with valid data"""
        metrics = StartupMetrics(**valid_startup_data)
        assert metrics.funding_stage == "seed"
        assert metrics.total_capital_raised_usd == 2000000
        assert metrics.runway_months == 15
    
    def test_runway_calculation(self):
        """Test automatic runway calculation"""
        data = {
            "funding_stage": "seed",
            "total_capital_raised_usd": 1000000,
            "cash_on_hand_usd": 500000,
            "monthly_burn_usd": 50000,
            # runway_months not provided, should be calculated
            "annual_revenue_run_rate": 100000,
            "gross_margin_percent": 80,
            "investor_tier_primary": "tier_2",
            "has_debt": False,
            "network_effects_present": True,
            "has_data_moat": False,
            "regulatory_advantage_present": False,
            "tech_differentiation_score": 3.0,
            "switching_cost_score": 3.0,
            "brand_strength_score": 3.0,
            "scalability_score": 0.5,
            "product_stage": "mvp",
            "product_retention_30d": 0.5,
            "product_retention_90d": 0.3,
            "sector": "SaaS",
            "tam_size_usd": 1000000000,
            "sam_size_usd": 100000000,
            "som_size_usd": 10000000,
            "market_growth_rate_percent": 20,
            "customer_count": 10,
            "customer_concentration_percent": 30,
            "user_growth_rate_percent": 15,
            "net_dollar_retention_percent": 105,
            "competition_intensity": 3.0,
            "competitors_named_count": 5,
            "dau_mau_ratio": 0.3,
            "founders_count": 2,
            "team_size_full_time": 5,
            "years_experience_avg": 5,
            "domain_expertise_years_avg": 3,
            "prior_startup_experience_count": 1,
            "prior_successful_exits_count": 0,
            "board_advisor_experience_score": 3.0,
            "advisors_count": 2,
            "team_diversity_percent": 20,
            "key_person_dependency": True
        }
        
        metrics = StartupMetrics(**data)
        assert metrics.runway_months == 10  # 500k / 50k = 10 months
    
    def test_burn_multiple_calculation(self):
        """Test automatic burn multiple calculation"""
        data = {
            "funding_stage": "series_a",
            "total_capital_raised_usd": 5000000,
            "cash_on_hand_usd": 3000000,
            "monthly_burn_usd": 200000,
            "annual_revenue_run_rate": 1000000,
            # burn_multiple not provided, should be calculated
            "gross_margin_percent": 70,
            "investor_tier_primary": "tier_1",
            "has_debt": False,
            "network_effects_present": True,
            "has_data_moat": True,
            "regulatory_advantage_present": False,
            "tech_differentiation_score": 4.0,
            "switching_cost_score": 4.0,
            "brand_strength_score": 3.5,
            "scalability_score": 0.8,
            "product_stage": "growth",
            "product_retention_30d": 0.7,
            "product_retention_90d": 0.6,
            "sector": "Enterprise SaaS",
            "tam_size_usd": 10000000000,
            "sam_size_usd": 1000000000,
            "som_size_usd": 100000000,
            "market_growth_rate_percent": 30,
            "customer_count": 100,
            "customer_concentration_percent": 15,
            "user_growth_rate_percent": 50,
            "net_dollar_retention_percent": 120,
            "competition_intensity": 2.5,
            "competitors_named_count": 8,
            "dau_mau_ratio": 0.5,
            "founders_count": 2,
            "team_size_full_time": 25,
            "years_experience_avg": 12,
            "domain_expertise_years_avg": 8,
            "prior_startup_experience_count": 3,
            "prior_successful_exits_count": 1,
            "board_advisor_experience_score": 4.5,
            "advisors_count": 6,
            "team_diversity_percent": 35,
            "key_person_dependency": False
        }
        
        metrics = StartupMetrics(**data)
        # Annual burn = 200k * 12 = 2.4M
        # Net burn = 2.4M - 1M = 1.4M
        # New ARR (20% growth) = 1M * 0.2 = 200k
        # Burn multiple = 1.4M / 200k = 7.0
        assert metrics.burn_multiple == 7.0
    
    def test_funding_stage_validation(self):
        """Test funding stage enum validation"""
        with pytest.raises(ValidationError) as exc_info:
            StartupMetrics(
                funding_stage="unknown_stage",
                total_capital_raised_usd=1000000,
                # ... other required fields would go here
            )
        assert "funding_stage" in str(exc_info.value)
    
    def test_negative_value_validation(self):
        """Test that negative values are rejected where inappropriate"""
        with pytest.raises(ValidationError) as exc_info:
            StartupMetrics(
                funding_stage="seed",
                total_capital_raised_usd=-1000000,  # Negative funding
                # ... other required fields
            )
        assert "total_capital_raised_usd" in str(exc_info.value)
    
    def test_percentage_bounds(self):
        """Test percentage fields are bounded correctly"""
        with pytest.raises(ValidationError) as exc_info:
            StartupMetrics(
                funding_stage="seed",
                total_capital_raised_usd=1000000,
                gross_margin_percent=150,  # Over 100%
                # ... other required fields
            )
        assert "gross_margin_percent" in str(exc_info.value)
    
    def test_score_bounds(self):
        """Test score fields (1-5) are bounded correctly"""
        with pytest.raises(ValidationError) as exc_info:
            StartupMetrics(
                funding_stage="seed",
                total_capital_raised_usd=1000000,
                tech_differentiation_score=10,  # Should be 1-5
                # ... other required fields
            )
        assert "tech_differentiation_score" in str(exc_info.value)
    
    def test_market_size_validation(self, valid_startup_data):
        """Test TAM >= SAM >= SOM validation"""
        data = valid_startup_data.copy()
        
        # Test TAM < SAM (invalid)
        data["tam_size_usd"] = 100
        data["sam_size_usd"] = 1000
        data["som_size_usd"] = 50
        
        with pytest.raises(ValidationError) as exc_info:
            StartupMetrics(**data)
        assert "TAM must be greater than or equal to SAM" in str(exc_info.value)
        
        # Test SAM < SOM (invalid)
        data["tam_size_usd"] = 10000
        data["sam_size_usd"] = 100
        data["som_size_usd"] = 1000
        
        with pytest.raises(ValidationError) as exc_info:
            StartupMetrics(**data)
        assert "SAM must be greater than or equal to SOM" in str(exc_info.value)
    
    def test_edge_cases(self):
        """Test edge case handling"""
        # Test zero burn rate
        data = {
            "funding_stage": "seed",
            "total_capital_raised_usd": 1000000,
            "cash_on_hand_usd": 1000000,
            "monthly_burn_usd": 0,  # No burn
            "annual_revenue_run_rate": 500000,
            "gross_margin_percent": 90,
            "investor_tier_primary": "tier_1",
            "has_debt": False,
            "network_effects_present": True,
            "has_data_moat": True,
            "regulatory_advantage_present": False,
            "tech_differentiation_score": 5.0,
            "switching_cost_score": 5.0,
            "brand_strength_score": 4.0,
            "scalability_score": 0.9,
            "product_stage": "growth",
            "product_retention_30d": 0.8,
            "product_retention_90d": 0.7,
            "sector": "SaaS",
            "tam_size_usd": 5000000000,
            "sam_size_usd": 500000000,
            "som_size_usd": 50000000,
            "market_growth_rate_percent": 40,
            "customer_count": 200,
            "customer_concentration_percent": 10,
            "user_growth_rate_percent": 100,
            "net_dollar_retention_percent": 130,
            "competition_intensity": 2.0,
            "competitors_named_count": 5,
            "dau_mau_ratio": 0.6,
            "founders_count": 3,
            "team_size_full_time": 30,
            "years_experience_avg": 15,
            "domain_expertise_years_avg": 10,
            "prior_startup_experience_count": 5,
            "prior_successful_exits_count": 2,
            "board_advisor_experience_score": 5.0,
            "advisors_count": 8,
            "team_diversity_percent": 50,
            "key_person_dependency": False
        }
        
        metrics = StartupMetrics(**data)
        assert metrics.runway_months == 120  # Max runway when no burn
        assert metrics.burn_multiple == 0  # No burn multiple when profitable