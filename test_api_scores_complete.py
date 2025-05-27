#!/usr/bin/env python3
"""Test API with complete data to verify CAMP scores"""

import requests
import json

# Complete startup data matching API requirements
test_data = {
    # Capital metrics
    "funding_stage": "series_a",
    "total_capital_raised_usd": 5000000,
    "cash_on_hand_usd": 3000000,
    "monthly_burn_usd": 150000,
    "runway_months": 20,
    "annual_revenue_run_rate": 2400000,
    "revenue_growth_rate_percent": 15,
    "gross_margin_percent": 65,
    "burn_multiple": 0.75,
    "ltv_cac_ratio": 5.0,
    "investor_tier_primary": "tier_1",
    "has_debt": False,
    
    # Advantage metrics
    "patent_count": 2,
    "network_effects_present": True,
    "has_data_moat": True,
    "regulatory_advantage_present": False,
    "tech_differentiation_score": 4,
    "switching_cost_score": 4,
    "brand_strength_score": 3,
    "scalability_score": 0.8,
    "product_stage": "growth",
    "product_retention_30d": 0.85,
    "product_retention_90d": 0.75,
    
    # Market metrics
    "sector": "fintech",
    "tam_size_usd": 50000000000,
    "sam_size_usd": 10000000000,
    "som_size_usd": 500000000,
    "market_growth_rate_percent": 25,
    "customer_count": 5000,
    "customer_concentration_percent": 15,
    "user_growth_rate_percent": 20,
    "net_dollar_retention_percent": 115,
    "competition_intensity": 3,
    "competitors_named_count": 15,
    "dau_mau_ratio": 0.4,
    
    # People metrics
    "founders_count": 2,
    "team_size_full_time": 25,
    "years_experience_avg": 8,
    "domain_expertise_years_avg": 6,
    "prior_startup_experience_count": 3,
    "prior_successful_exits_count": 1,
    "board_advisor_experience_score": 4,
    "advisors_count": 4,
    "team_diversity_percent": 40,
    "key_person_dependency": False
}

# Test prediction endpoint
print("Testing /predict endpoint with complete data...")
response = requests.post("http://localhost:8000/predict", json=test_data)

if response.status_code == 200:
    result = response.json()
    print("\n✅ API Response:")
    print(f"Success Probability: {result['success_probability']:.2%}")
    print(f"Risk Level: {result['risk_level']}")
    
    print("\n📊 CAMP Pillar Scores (from actual models):")
    for pillar, score in result['pillar_scores'].items():
        print(f"  {pillar.capitalize()}: {score:.2%}")
    
    print("\n🔍 Key Insights:")
    for i, insight in enumerate(result['key_insights'][:5]):
        print(f"  {i+1}. {insight}")
        
    print("\n💡 Recommendation:")
    print(f"  {result['recommendation']}")
    
    print("\n📈 Confidence Interval:")
    print(f"  [{result['confidence_interval']['lower']:.2%}, {result['confidence_interval']['upper']:.2%}]")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text[:500])

# Test explain endpoint
print("\n\nTesting /explain endpoint...")
explain_response = requests.post("http://localhost:8000/explain", json=test_data)
if explain_response.status_code == 200:
    explain_data = explain_response.json()
    print("✅ Explanation generated successfully")
    if 'explanation' in explain_data and 'insights' in explain_data['explanation']:
        insights = explain_data['explanation']['insights']
        if insights.get('strengths'):
            print(f"  Strengths: {len(insights['strengths'])} identified")
        if insights.get('weaknesses'): 
            print(f"  Weaknesses: {len(insights['weaknesses'])} identified")
else:
    print(f"❌ Explain error: {explain_response.status_code}")