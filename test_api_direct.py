#!/usr/bin/env python3
"""Direct API test to check for errors"""

import requests
import json

# Test data
test_data = {
    "funding_stage": "series_a",
    "total_capital_raised_usd": 15000000,
    "cash_on_hand_usd": 8000000,
    "monthly_burn_usd": 400000,
    "annual_revenue_run_rate": 3000000,
    "revenue_growth_rate_percent": 150,
    "gross_margin_percent": 75,
    "ltv_cac_ratio": 3.5,
    "investor_tier_primary": "tier_1",
    "has_debt": False,
    "patent_count": 3,
    "network_effects_present": True,
    "has_data_moat": True,
    "regulatory_advantage_present": False,
    "tech_differentiation_score": 4.2,
    "switching_cost_score": 3.8,
    "brand_strength_score": 3.5,
    "scalability_score": 4.5,
    "product_stage": "growth",
    "product_retention_30d": 0.85,
    "product_retention_90d": 0.75,
    "sector": "SaaS",
    "tam_size_usd": 50000000000,
    "sam_size_usd": 5000000000,
    "som_size_usd": 500000000,
    "market_growth_rate_percent": 25,
    "customer_count": 150,
    "customer_concentration_percent": 15,
    "user_growth_rate_percent": 20,
    "net_dollar_retention_percent": 125,
    "competition_intensity": 3,
    "competitors_named_count": 5,
    "dau_mau_ratio": 0.4,
    "founders_count": 3,
    "team_size_full_time": 45,
    "years_experience_avg": 12,
    "domain_expertise_years_avg": 8,
    "prior_startup_experience_count": 2,
    "prior_successful_exits_count": 1,
    "board_advisor_experience_score": 4,
    "advisors_count": 6,
    "team_diversity_percent": 40,
    "key_person_dependency": False
}

print("Testing FLASH API...")
print("-" * 50)

# Test health endpoint
try:
    response = requests.get("http://localhost:8000/health")
    print("Health Check:", response.json())
except Exception as e:
    print(f"Health Check Error: {e}")

print("-" * 50)

# Test prediction endpoint
try:
    response = requests.post(
        "http://localhost:8000/predict",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("Prediction Success!")
        print(f"Success Probability: {result.get('success_probability', 'N/A')}")
        print(f"Verdict: {result.get('verdict', 'N/A')}")
        print(f"Strength: {result.get('strength', 'N/A')}")
        print(f"Pillar Scores: {result.get('pillar_scores', {})}")
    else:
        print(f"Prediction Error: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Prediction Error: {e}")

print("-" * 50)