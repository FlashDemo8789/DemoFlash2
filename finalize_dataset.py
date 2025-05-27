#!/usr/bin/env python3
"""
Finalize the 100k hybrid dataset to match our exact 45-feature specification.
Adds missing columns, removes extras, and ensures data quality.
"""
import numpy as np
import pandas as pd
import json
from datetime import datetime

# Define our exact 45 features organized by CAMP pillars
CAPITAL_FEATURES = [
    "funding_stage",
    "total_capital_raised_usd",
    "cash_on_hand_usd", 
    "monthly_burn_usd",
    "runway_months",
    "annual_revenue_run_rate",
    "revenue_growth_rate_percent",
    "gross_margin_percent",
    "burn_multiple",
    "ltv_cac_ratio",
    "investor_tier_primary",
    "has_debt"
]

ADVANTAGE_FEATURES = [
    "patent_count",
    "network_effects_present",
    "has_data_moat",
    "regulatory_advantage_present",
    "tech_differentiation_score",
    "switching_cost_score",
    "brand_strength_score",
    "scalability_score",
    "product_stage",
    "product_retention_30d",
    "product_retention_90d"
]

MARKET_FEATURES = [
    "sector",
    "tam_size_usd",
    "sam_size_usd",
    "som_size_usd",
    "market_growth_rate_percent",
    "customer_count",
    "customer_concentration_percent",
    "user_growth_rate_percent",
    "net_dollar_retention_percent",
    "competition_intensity",
    "competitors_named_count",
    "dau_mau_ratio"
]

PEOPLE_FEATURES = [
    "founders_count",
    "team_size_full_time",
    "years_experience_avg",
    "domain_expertise_years_avg",
    "prior_startup_experience_count",
    "prior_successful_exits_count",
    "board_advisor_experience_score",
    "advisors_count",
    "team_diversity_percent",
    "key_person_dependency"
]

# Combine all features
ALL_FEATURES = CAPITAL_FEATURES + ADVANTAGE_FEATURES + MARKET_FEATURES + PEOPLE_FEATURES
print(f"Total features defined: {len(ALL_FEATURES)}")

def add_missing_columns(df):
    """Add any missing columns that are in our 45-feature spec."""
    print("\nAdding missing columns...")
    
    # Add CAC if missing (needed for LTV/CAC ratio)
    if 'cac_usd' not in df.columns:
        # Calculate CAC from LTV/CAC ratio and customer metrics
        df['cac_usd'] = np.where(
            (df['customer_count'] > 0) & (df['ltv_cac_ratio'] > 0),
            df['annual_revenue_run_rate'] / (df['customer_count'] * df['ltv_cac_ratio']),
            1000  # Default CAC for companies without customers
        )
        print("  Added: cac_usd")
    
    # Add LTV if missing
    if 'ltv_usd' not in df.columns:
        df['ltv_usd'] = df['cac_usd'] * df['ltv_cac_ratio']
        print("  Added: ltv_usd")
    
    # Add NPS score if missing
    if 'nps_score' not in df.columns:
        # Generate NPS based on product retention and success
        base_nps = np.where(df['success'], 
                           np.random.normal(40, 20),  # Successful companies: mean 40
                           np.random.normal(0, 25))    # Failed companies: mean 0
        
        # Adjust by product retention
        retention_factor = (df['product_retention_30d'] + df['product_retention_90d']) / 2
        df['nps_score'] = np.clip(base_nps * retention_factor, -100, 100).astype(int)
        print("  Added: nps_score")
    
    return df

def validate_data_quality(df):
    """Validate data consistency and quality."""
    print("\nValidating data quality...")
    issues = []
    
    # Check for missing values in required columns
    for col in ALL_FEATURES:
        if col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                issues.append(f"  {col}: {missing} missing values")
    
    # Validate logical relationships
    # 1. Runway should match cash/burn
    calculated_runway = df['cash_on_hand_usd'] / df['monthly_burn_usd'].replace(0, 1)
    runway_diff = abs(df['runway_months'] - calculated_runway)
    if (runway_diff > 1).sum() > 0:
        issues.append(f"  Runway calculation mismatch: {(runway_diff > 1).sum()} rows")
    
    # 2. Burn multiple should match burn/revenue
    df['burn_multiple_calc'] = np.where(
        df['annual_revenue_run_rate'] > 0,
        (df['monthly_burn_usd'] * 12) / df['annual_revenue_run_rate'],
        100
    )
    
    # 3. Success rate should vary by stage
    stage_success = df.groupby('funding_stage')['success'].mean()
    print("\n  Success rates by stage:")
    for stage, rate in stage_success.items():
        print(f"    {stage}: {rate:.2%}")
    
    if issues:
        print("\n  Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("  ✓ No major issues found")
    
    return len(issues) == 0

def create_finalized_dataset(input_path, output_path):
    """Create the finalized dataset with exactly 45 features + success label."""
    print(f"Loading dataset from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    
    # Add missing columns
    df = add_missing_columns(df)
    
    # Select only our 45 features + success label + ID columns
    id_columns = ['startup_id', 'startup_name', 'founding_year']
    final_columns = id_columns + ALL_FEATURES + ['success']
    
    # Check which columns are missing
    missing_cols = [col for col in final_columns if col not in df.columns]
    if missing_cols:
        print(f"\nWarning: Missing columns that cannot be generated: {missing_cols}")
        # Remove missing columns from final list
        final_columns = [col for col in final_columns if col in df.columns]
    
    # Select final columns
    df_final = df[final_columns].copy()
    
    # Validate data quality
    is_valid = validate_data_quality(df_final)
    
    # Save the finalized dataset
    df_final.to_csv(output_path, index=False)
    print(f"\nFinalized dataset saved to: {output_path}")
    print(f"Shape: {df_final.shape}")
    
    # Generate summary statistics
    summary = {
        "total_rows": len(df_final),
        "total_features": len(ALL_FEATURES),
        "success_rate": float(df_final['success'].mean()),
        "features_by_pillar": {
            "capital": len(CAPITAL_FEATURES),
            "advantage": len(ADVANTAGE_FEATURES),
            "market": len(MARKET_FEATURES),
            "people": len(PEOPLE_FEATURES)
        },
        "stage_distribution": df_final['funding_stage'].value_counts().to_dict(),
        "sector_distribution": df_final['sector'].value_counts().head(10).to_dict(),
        "data_quality_valid": is_valid,
        "timestamp": datetime.now().isoformat()
    }
    
    # Save summary
    summary_path = output_path.replace('.csv', '_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to: {summary_path}")
    
    return df_final

def main():
    """Run the dataset finalization process."""
    input_path = "/Users/sf/Desktop/FLASH/data/hybrid_100k_companies.csv"
    output_path = "/Users/sf/Desktop/FLASH/data/final_100k_dataset_45features.csv"
    
    # Create finalized dataset
    df_final = create_finalized_dataset(input_path, output_path)
    
    # Create a sample for quick inspection
    sample_path = "/Users/sf/Desktop/FLASH/data/final_sample_1000.csv"
    df_final.sample(1000, random_state=42).to_csv(sample_path, index=False)
    print(f"\nSample saved to: {sample_path}")
    
    # Print feature list for documentation
    print("\n" + "="*50)
    print("FINAL 45 FEATURES BY PILLAR:")
    print("="*50)
    
    print(f"\nCAPITAL ({len(CAPITAL_FEATURES)} features):")
    for i, feat in enumerate(CAPITAL_FEATURES, 1):
        print(f"  {i}. {feat}")
    
    print(f"\nADVANTAGE ({len(ADVANTAGE_FEATURES)} features):")
    for i, feat in enumerate(ADVANTAGE_FEATURES, 1):
        print(f"  {i}. {feat}")
    
    print(f"\nMARKET ({len(MARKET_FEATURES)} features):")
    for i, feat in enumerate(MARKET_FEATURES, 1):
        print(f"  {i}. {feat}")
    
    print(f"\nPEOPLE ({len(PEOPLE_FEATURES)} features):")
    for i, feat in enumerate(PEOPLE_FEATURES, 1):
        print(f"  {i}. {feat}")
    
    print("\n✓ Dataset finalization complete!")

if __name__ == "__main__":
    main()