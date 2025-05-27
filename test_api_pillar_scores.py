#!/usr/bin/env python3
"""Test script to check API pillar scores response"""

import requests
import json

# Test data
test_data = {
    "funding_stage": "Series A",
    "total_capital_raised_usd": 5000000,
    "cash_on_hand_usd": 3000000,
    "monthly_burn_usd": 150000,
    "annual_revenue_run_rate": 1200000,
    "revenue_growth_rate_percent": 150,
    "gross_margin_percent": 65,
    "ltv_cac_ratio": 3.5,
    "investor_tier_primary": "Tier 1",
    "has_debt": False,
    "patent_count": 2,
    "network_effects_present": True,
    "has_data_moat": True,
    "regulatory_advantage_present": False,
    "tech_differentiation_score": 4,
    "switching_cost_score": 3.5,
    "brand_strength_score": 3,
    "scalability_score": 0.8,
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
    "user_growth_rate_percent": 200,
    "net_dollar_retention_percent": 120,
    "competition_intensity": 3,
    "competitors_named_count": 5,
    "dau_mau_ratio": 0.6,
    "founders_count": 2,
    "team_size_full_time": 25,
    "years_experience_avg": 12,
    "domain_expertise_years_avg": 8,
    "prior_startup_experience_count": 2,
    "prior_successful_exits_count": 1,
    "board_advisor_experience_score": 4,
    "advisors_count": 5,
    "team_diversity_percent": 40,
    "key_person_dependency": False
}

# Make request
response = requests.post('http://localhost:8000/predict', json=test_data)
print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print("\nRaw Response Text:")
print(response.text)

if response.status_code == 200:
    result = response.json()
    print("\nParsed JSON:")
    print(json.dumps(result, indent=2))
    
    # Check pillar_scores specifically
    print("\nPillar Scores:")
    if 'pillar_scores' in result:
        print(json.dumps(result['pillar_scores'], indent=2))
    else:
        print("ERROR: pillar_scores not found in response!")
        print("Available keys:", list(result.keys()))