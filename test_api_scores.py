#!/usr/bin/env python3
"""Test API to verify CAMP scores are working"""

import requests
import json

# Sample startup data
test_data = {
    "funding_stage": "series_a",
    "total_capital_raised_usd": 5000000,
    "cash_on_hand_usd": 3000000,
    "monthly_burn_usd": 150000,
    "runway_months": 20,
    "annual_revenue_run_rate": 2400000,
    "revenue_growth_rate_percent": 15,
    "gross_margin_percent": 65,
    "burn_multiple": 0.75,
    "capital_efficiency": 0.48,
    "burn_risk": 0.3,
    "product_stage": "growth",
    "tech_stack_size": 12,
    "patent_count": 2,
    "proprietary_tech": 1,
    "moat_strength": 65,
    "pmf_score": 70,
    "nps": 45,
    "cac_usd": 500,
    "ltv_usd": 2500,
    "ltv_cac_ratio": 5.0,
    "time_to_market_months": 6,
    "competitive_advantage_score": 7,
    "market_size_usd": 50000000000,
    "market_growth_rate": 25,
    "market_share_potential": 0.02,
    "market_capture_percent": 0.5,
    "saturation_risk": 0.3,
    "sector": "fintech",
    "is_emerging_market": 0,
    "regulatory_complexity_score": 4,
    "competitor_intensity": 0.6,
    "team_size": 25,
    "founder_yoe": 12,
    "previous_exits": 1,
    "technical_staff_percent": 60,
    "advisor_count": 4,
    "board_size": 5,
    "team_quality": 35,
    "investor_tier_primary": "tier_1",
    "founder_domain_expertise": 1,
    "technical_cofounder": 1,
    "employee_growth_mom": 5,
    "diversity_score": 7
}

# Test prediction endpoint
print("Testing /predict endpoint...")
response = requests.post("http://localhost:8000/predict", json=test_data)

if response.status_code == 200:
    result = response.json()
    print("\n✅ API Response:")
    print(f"Success Probability: {result['success_probability']:.2%}")
    print(f"Risk Level: {result['risk_level']}")
    
    print("\n📊 CAMP Pillar Scores:")
    for pillar, score in result['pillar_scores'].items():
        print(f"  {pillar.capitalize()}: {score:.2%}")
    
    print("\n🔍 Key Insights:")
    for insight in result['key_insights'][:3]:
        print(f"  - {insight}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)

# Test health endpoint
print("\n\nTesting /health endpoint...")
health_response = requests.get("http://localhost:8000/health")
if health_response.status_code == 200:
    health = health_response.json()
    print(f"✅ Models loaded: {health['models_loaded']}")
    print(f"✅ Pillar models loaded: {health.get('pillar_models_loaded', 'N/A')}")