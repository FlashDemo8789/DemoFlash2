#!/usr/bin/env python3
"""
Create a large-scale hybrid dataset using real company data from public sources
combined with intelligently generated metrics based on industry patterns.
"""
import numpy as np
import pandas as pd
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import requests
import time

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

class HybridDatasetGenerator:
    """Generate hybrid dataset with real companies and synthetic metrics."""
    
    def __init__(self):
        # Sector profiles based on real industry data
        self.sector_profiles = {
            "SaaS": {
                "gross_margin": (0.70, 0.90),
                "burn_multiple": (0.5, 2.0),
                "growth_rate": (0.20, 1.50),
                "ltv_cac": (2.0, 5.0),
                "market_growth": (0.15, 0.30)
            },
            "FinTech": {
                "gross_margin": (0.60, 0.85),
                "burn_multiple": (0.8, 2.5),
                "growth_rate": (0.25, 2.00),
                "ltv_cac": (1.5, 4.0),
                "market_growth": (0.20, 0.35)
            },
            "HealthTech": {
                "gross_margin": (0.50, 0.75),
                "burn_multiple": (1.0, 3.0),
                "growth_rate": (0.15, 1.00),
                "ltv_cac": (1.0, 3.0),
                "market_growth": (0.18, 0.28)
            },
            "E-commerce": {
                "gross_margin": (0.25, 0.50),
                "burn_multiple": (0.8, 2.0),
                "growth_rate": (0.30, 2.50),
                "ltv_cac": (1.0, 2.5),
                "market_growth": (0.10, 0.20)
            },
            "AI/ML": {
                "gross_margin": (0.65, 0.85),
                "burn_multiple": (1.0, 3.5),
                "growth_rate": (0.30, 3.00),
                "ltv_cac": (1.5, 4.5),
                "market_growth": (0.25, 0.40)
            },
            "BioTech": {
                "gross_margin": (0.40, 0.70),
                "burn_multiple": (2.0, 5.0),
                "growth_rate": (0.10, 0.80),
                "ltv_cac": (0.8, 2.0),
                "market_growth": (0.15, 0.25)
            },
            "EdTech": {
                "gross_margin": (0.50, 0.75),
                "burn_multiple": (0.8, 2.5),
                "growth_rate": (0.20, 1.50),
                "ltv_cac": (1.2, 3.0),
                "market_growth": (0.12, 0.22)
            },
            "Gaming": {
                "gross_margin": (0.60, 0.85),
                "burn_multiple": (0.5, 2.0),
                "growth_rate": (0.10, 4.00),
                "ltv_cac": (0.8, 3.0),
                "market_growth": (0.15, 0.25)
            },
            "Cybersecurity": {
                "gross_margin": (0.75, 0.90),
                "burn_multiple": (0.8, 2.5),
                "growth_rate": (0.25, 1.80),
                "ltv_cac": (2.0, 5.0),
                "market_growth": (0.20, 0.30)
            },
            "Other": {
                "gross_margin": (0.40, 0.70),
                "burn_multiple": (1.0, 3.0),
                "growth_rate": (0.15, 1.20),
                "ltv_cac": (1.0, 3.0),
                "market_growth": (0.10, 0.20)
            }
        }
        
        # Funding stage characteristics
        self.stage_profiles = {
            "Pre-seed": {
                "funding_range": (50000, 500000),
                "team_size": (1, 5),
                "revenue_probability": 0.1,
                "customer_range": (0, 100)
            },
            "Seed": {
                "funding_range": (250000, 2000000),
                "team_size": (3, 15),
                "revenue_probability": 0.3,
                "customer_range": (10, 1000)
            },
            "Series A": {
                "funding_range": (2000000, 15000000),
                "team_size": (10, 50),
                "revenue_probability": 0.8,
                "customer_range": (100, 10000)
            },
            "Series B": {
                "funding_range": (10000000, 50000000),
                "team_size": (30, 150),
                "revenue_probability": 0.95,
                "customer_range": (1000, 50000)
            },
            "Series C+": {
                "funding_range": (30000000, 200000000),
                "team_size": (75, 500),
                "revenue_probability": 1.0,
                "customer_range": (5000, 500000)
            }
        }
        
        # Real company data sources (simplified for demonstration)
        self.real_companies = self._load_real_companies()
    
    def _load_real_companies(self) -> List[Dict]:
        """Load real company data from various sources."""
        # This is a simplified version. In production, you would:
        # 1. Load from Crunchbase CSV exports
        # 2. Parse AngelList data
        # 3. Scrape public LinkedIn company pages
        # 4. Use SEC EDGAR API for public companies
        
        # For now, we'll create a realistic distribution of company types
        companies = []
        
        # Fortune 500 tech companies (public data)
        tech_giants = [
            {"name": "Microsoft", "sector": "SaaS", "founded": 1975, "stage": "Public"},
            {"name": "Apple", "sector": "Other", "founded": 1976, "stage": "Public"},
            {"name": "Amazon", "sector": "E-commerce", "founded": 1994, "stage": "Public"},
            {"name": "Google", "sector": "AI/ML", "founded": 1998, "stage": "Public"},
            {"name": "Meta", "sector": "Other", "founded": 2004, "stage": "Public"},
        ]
        
        # Well-known unicorns
        unicorns = [
            {"name": "Stripe", "sector": "FinTech", "founded": 2010, "stage": "Series C+"},
            {"name": "SpaceX", "sector": "Other", "founded": 2002, "stage": "Series C+"},
            {"name": "Databricks", "sector": "AI/ML", "founded": 2013, "stage": "Series C+"},
            {"name": "Canva", "sector": "SaaS", "founded": 2013, "stage": "Series C+"},
            {"name": "Discord", "sector": "Other", "founded": 2015, "stage": "Series C+"},
        ]
        
        # Generate variations and similar companies
        sectors = list(self.sector_profiles.keys())
        stages = ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"]
        
        # Common startup name patterns
        prefixes = ["Cloud", "Data", "Smart", "Next", "First", "Prime", "Core", "Edge", 
                   "Quantum", "Rapid", "Swift", "Bright", "Clear", "Pure", "True"]
        suffixes = ["Tech", "Labs", "Works", "Hub", "Base", "Flow", "Mind", "Soft",
                   "Solutions", "Systems", "Platform", "Network", "Digital", "AI"]
        domains = ["Health", "Fin", "Ed", "Bio", "Cyber", "Green", "Auto", "Space",
                  "Food", "Travel", "Real Estate", "Legal", "HR", "Marketing"]
        
        # Generate 100,000 companies with realistic distributions
        print("Generating company list...")
        
        # Add known companies
        companies.extend(tech_giants)
        companies.extend(unicorns)
        
        # Generate the rest
        for i in range(99990):
            # Create realistic company names
            if random.random() < 0.3:
                # Domain-specific name
                name = f"{random.choice(domains)}{random.choice(suffixes)}"
            elif random.random() < 0.6:
                # Prefix-suffix pattern
                name = f"{random.choice(prefixes)}{random.choice(suffixes)}"
            else:
                # Creative name
                name = f"{random.choice(prefixes)}{random.choice(domains)}"
            
            # Add unique identifier to avoid duplicates
            name = f"{name}_{i}"
            
            # Realistic stage distribution
            stage_weights = [0.15, 0.30, 0.30, 0.20, 0.05]  # Pre-seed to Series C+
            stage = np.random.choice(stages, p=stage_weights)
            
            # Sector distribution based on market reality
            sector_weights = [0.25, 0.15, 0.10, 0.10, 0.15, 0.05, 0.08, 0.05, 0.05, 0.02]
            sector = np.random.choice(sectors, p=sector_weights)
            
            # Founding year distribution (more recent = more likely)
            current_year = datetime.now().year
            if stage == "Pre-seed":
                founded = random.randint(current_year - 2, current_year)
            elif stage == "Seed":
                founded = random.randint(current_year - 4, current_year - 1)
            elif stage == "Series A":
                founded = random.randint(current_year - 7, current_year - 2)
            elif stage == "Series B":
                founded = random.randint(current_year - 10, current_year - 4)
            else:  # Series C+
                founded = random.randint(current_year - 20, current_year - 6)
            
            companies.append({
                "name": name,
                "sector": sector,
                "founded": founded,
                "stage": stage
            })
            
            if (i + 1) % 10000 == 0:
                print(f"  Generated {i + 11} companies...")
        
        return companies
    
    def generate_company_metrics(self, company: Dict) -> Dict:
        """Generate realistic metrics for a company based on its profile."""
        sector = company["sector"]
        stage = company["stage"]
        
        # Handle public companies differently
        if stage == "Public":
            return self._generate_public_company_metrics(company)
        
        sector_profile = self.sector_profiles[sector]
        stage_profile = self.stage_profiles[stage]
        
        # Determine company performance archetype
        performance = self._determine_performance_archetype(sector, stage)
        
        # Generate correlated metrics
        metrics = {
            "startup_id": f"id_{hash(company['name']) % 1000000}",
            "startup_name": company["name"],
            "sector": sector,
            "founding_year": company["founded"],
            "funding_stage": stage,
        }
        
        # Capital metrics
        total_funding = np.random.uniform(*stage_profile["funding_range"])
        burn_rate = self._calculate_burn_rate(total_funding, stage, performance)
        revenue = self._calculate_revenue(burn_rate, stage, performance, sector)
        
        cash_on_hand = int(total_funding * np.random.uniform(0.3, 0.7))
        runway_months = cash_on_hand / burn_rate if burn_rate > 0 else 24
        
        metrics.update({
            "total_capital_raised_usd": int(total_funding),
            "cash_on_hand_usd": cash_on_hand,
            "monthly_burn_usd": int(burn_rate),
            "annual_revenue_run_rate": int(revenue),
            "revenue_growth_rate_percent": self._calculate_growth_rate(performance, sector),
            "gross_margin_percent": np.random.uniform(*sector_profile["gross_margin"]) * 100,
            "burn_multiple": burn_rate * 12 / revenue if revenue > 0 else 100,
            "runway_months": runway_months,
            "ltv_cac_ratio": np.random.uniform(*sector_profile["ltv_cac"]) * performance,
            "investor_tier_primary": self._assign_investor_tier(stage, performance),
            "has_debt": random.random() < 0.3,
        })
        
        # Market metrics
        tam = self._calculate_tam(sector)
        customer_count = np.random.randint(*stage_profile["customer_range"])
        
        metrics.update({
            "tam_size_usd": int(tam),
            "sam_size_usd": int(tam * np.random.uniform(0.05, 0.20)),
            "som_size_usd": int(tam * np.random.uniform(0.001, 0.05)),
            "market_growth_rate_percent": np.random.uniform(*sector_profile["market_growth"]) * 100,
            "customer_count": customer_count,
            "customer_concentration_percent": self._calculate_concentration(customer_count),
            "user_growth_rate_percent": metrics["revenue_growth_rate_percent"] * np.random.uniform(0.8, 1.2),
            "net_dollar_retention_percent": 100 + (performance - 0.5) * 40,
            "competition_intensity": np.random.uniform(2, 5),
            "competitors_named_count": np.random.randint(5, 50),
            "dau_mau_ratio": np.random.uniform(0.1, 0.6) * performance,
        })
        
        # People metrics
        team_size = np.random.randint(*stage_profile["team_size"])
        
        metrics.update({
            "founders_count": np.random.choice([1, 2, 3, 4], p=[0.2, 0.5, 0.25, 0.05]),
            "team_size_full_time": team_size,
            "years_experience_avg": np.random.uniform(3, 15) * performance,
            "domain_expertise_years_avg": np.random.uniform(2, 12) * performance,
            "prior_startup_experience_count": np.random.randint(0, 5),
            "prior_successful_exits_count": np.random.choice([0, 1, 2], p=[0.7, 0.25, 0.05]),
            "board_advisor_experience_score": np.random.uniform(1, 5) * performance,
            "advisors_count": np.random.randint(0, 10),
            "team_diversity_percent": np.random.uniform(20, 80),
            "key_person_dependency": random.random() < 0.3,
        })
        
        # Advantage metrics
        is_tech_heavy = sector in ["AI/ML", "SaaS", "Cybersecurity", "BioTech"]
        
        metrics.update({
            "patent_count": np.random.choice([0, 1, 2, 5, 10], p=[0.5, 0.2, 0.15, 0.1, 0.05]) if is_tech_heavy else 0,
            "network_effects_present": random.random() < (0.3 if performance > 0.7 else 0.1),
            "has_data_moat": random.random() < (0.4 if is_tech_heavy else 0.2),
            "regulatory_advantage_present": random.random() < (0.3 if sector in ["FinTech", "HealthTech", "BioTech"] else 0.1),
            "tech_differentiation_score": np.random.uniform(1, 5) * performance,
            "switching_cost_score": np.random.uniform(1, 5) * (performance + 0.2),
            "brand_strength_score": np.random.uniform(1, 5) * performance,
            "scalability_score": np.random.uniform(0.3, 1.0) * performance,
            "product_stage": self._assign_product_stage(stage),
            "product_retention_30d": np.random.uniform(0.4, 0.9) * performance,
            "product_retention_90d": np.random.uniform(0.2, 0.7) * performance,
        })
        
        # Success label based on performance and randomness
        success_probability = self._calculate_success_probability(performance, stage, sector)
        metrics["success"] = random.random() < success_probability
        
        return metrics
    
    def _determine_performance_archetype(self, sector: str, stage: str) -> float:
        """Determine company performance on a 0-1 scale."""
        # Base performance by stage
        stage_base = {
            "Pre-seed": 0.5,
            "Seed": 0.55,
            "Series A": 0.65,
            "Series B": 0.75,
            "Series C+": 0.85
        }
        
        # Sector multipliers
        sector_mult = {
            "AI/ML": 1.1,
            "SaaS": 1.05,
            "FinTech": 1.0,
            "HealthTech": 0.95,
            "E-commerce": 0.9,
            "Other": 0.85
        }
        
        base = stage_base.get(stage, 0.5)
        mult = sector_mult.get(sector, 1.0)
        
        # Add randomness
        performance = base * mult * np.random.uniform(0.5, 1.5)
        return np.clip(performance, 0.1, 1.0)
    
    def _calculate_burn_rate(self, funding: float, stage: str, performance: float) -> float:
        """Calculate monthly burn rate based on funding and stage."""
        stage_burn_ratio = {
            "Pre-seed": 0.08,
            "Seed": 0.06,
            "Series A": 0.05,
            "Series B": 0.04,
            "Series C+": 0.03
        }
        
        base_ratio = stage_burn_ratio.get(stage, 0.05)
        # High performers burn more efficiently
        efficiency = 1.0 - (performance - 0.5) * 0.3
        
        return funding * base_ratio * efficiency
    
    def _calculate_revenue(self, burn: float, stage: str, performance: float, sector: str) -> float:
        """Calculate revenue based on burn rate and company profile."""
        if stage == "Pre-seed" and random.random() > 0.3:
            return 0
        
        # Revenue as multiple of burn
        base_multiple = {
            "Pre-seed": 0.1,
            "Seed": 0.3,
            "Series A": 0.8,
            "Series B": 1.5,
            "Series C+": 2.5
        }
        
        multiple = base_multiple.get(stage, 1.0) * performance
        
        # Some sectors have better unit economics
        if sector in ["SaaS", "FinTech"]:
            multiple *= 1.3
        
        return burn * multiple * 12  # Annualized
    
    def _calculate_growth_rate(self, performance: float, sector: str) -> float:
        """Calculate revenue growth rate."""
        base_growth = self.sector_profiles[sector]["growth_rate"]
        return np.random.uniform(*base_growth) * performance * 100
    
    def _calculate_tam(self, sector: str) -> float:
        """Calculate Total Addressable Market by sector."""
        tam_ranges = {
            "AI/ML": (1e10, 5e11),
            "FinTech": (5e10, 1e12),
            "HealthTech": (1e11, 5e12),
            "E-commerce": (5e11, 2e12),
            "SaaS": (1e10, 5e11),
            "Other": (1e9, 1e11)
        }
        
        tam_range = tam_ranges.get(sector, (1e9, 1e11))
        return np.random.uniform(*tam_range)
    
    def _calculate_concentration(self, customers: int) -> float:
        """Calculate customer concentration percentage."""
        if customers < 10:
            return np.random.uniform(50, 90)
        elif customers < 100:
            return np.random.uniform(20, 50)
        elif customers < 1000:
            return np.random.uniform(10, 30)
        else:
            return np.random.uniform(5, 20)
    
    def _assign_investor_tier(self, stage: str, performance: float) -> str:
        """Assign investor tier based on stage and performance."""
        if stage == "Pre-seed":
            return np.random.choice(["Angel", "Unknown"], p=[0.7, 0.3])
        elif stage == "Seed":
            if performance > 0.7:
                return np.random.choice(["Tier1", "Tier2", "Angel"], p=[0.3, 0.5, 0.2])
            else:
                return np.random.choice(["Tier2", "Angel", "Unknown"], p=[0.4, 0.4, 0.2])
        else:  # Series A+
            if performance > 0.8:
                return np.random.choice(["Tier1", "Tier2"], p=[0.7, 0.3])
            else:
                return np.random.choice(["Tier1", "Tier2", "Unknown"], p=[0.3, 0.5, 0.2])
    
    def _assign_product_stage(self, funding_stage: str) -> str:
        """Assign product stage based on funding stage."""
        if funding_stage == "Pre-seed":
            return np.random.choice(["Concept", "Beta"], p=[0.7, 0.3])
        elif funding_stage == "Seed":
            return np.random.choice(["Beta", "GA"], p=[0.6, 0.4])
        else:
            return "GA"
    
    def _calculate_success_probability(self, performance: float, stage: str, sector: str) -> float:
        """Calculate probability of success."""
        # Base success rates by stage (industry averages)
        base_rates = {
            "Pre-seed": 0.10,
            "Seed": 0.20,
            "Series A": 0.35,
            "Series B": 0.50,
            "Series C+": 0.70
        }
        
        base = base_rates.get(stage, 0.25)
        
        # Adjust by performance
        adjusted = base * (0.5 + performance)
        
        # Sector adjustments
        if sector in ["AI/ML", "SaaS", "FinTech"]:
            adjusted *= 1.2
        elif sector in ["BioTech", "HealthTech"]:
            adjusted *= 0.9
        
        return np.clip(adjusted, 0.05, 0.95)
    
    def _generate_public_company_metrics(self, company: Dict) -> Dict:
        """Generate metrics for public companies (ultimate success)."""
        sector = company["sector"]
        
        # Public companies are successful by definition
        metrics = {
            "startup_id": f"id_{hash(company['name']) % 1000000}",
            "startup_name": company["name"],
            "sector": sector,
            "founding_year": company["founded"],
            "funding_stage": "Series C+",  # Treat as late stage
            "total_capital_raised_usd": int(np.random.uniform(1e8, 1e10)),
            "cash_on_hand_usd": int(np.random.uniform(1e8, 1e10)),
            "monthly_burn_usd": 0,  # Profitable
            "annual_revenue_run_rate": int(np.random.uniform(1e8, 1e11)),
            "revenue_growth_rate_percent": np.random.uniform(10, 50),
            "gross_margin_percent": np.random.uniform(60, 90),
            "burn_multiple": 0,
            "runway_months": 999,  # Infinite
            "ltv_cac_ratio": np.random.uniform(3, 10),
            "investor_tier_primary": "Tier1",
            "has_debt": True,
            "tam_size_usd": int(np.random.uniform(1e11, 1e13)),
            "sam_size_usd": int(np.random.uniform(1e10, 1e12)),
            "som_size_usd": int(np.random.uniform(1e9, 1e11)),
            "market_growth_rate_percent": np.random.uniform(10, 30),
            "customer_count": int(np.random.uniform(1e5, 1e8)),
            "customer_concentration_percent": np.random.uniform(5, 15),
            "user_growth_rate_percent": np.random.uniform(10, 50),
            "net_dollar_retention_percent": np.random.uniform(110, 150),
            "competition_intensity": np.random.uniform(3, 5),
            "competitors_named_count": np.random.randint(10, 100),
            "dau_mau_ratio": np.random.uniform(0.3, 0.8),
            "founders_count": np.random.randint(1, 3),
            "team_size_full_time": int(np.random.uniform(1000, 100000)),
            "years_experience_avg": np.random.uniform(10, 20),
            "domain_expertise_years_avg": np.random.uniform(10, 20),
            "prior_startup_experience_count": np.random.randint(1, 5),
            "prior_successful_exits_count": np.random.randint(1, 3),
            "board_advisor_experience_score": np.random.uniform(4, 5),
            "advisors_count": np.random.randint(5, 20),
            "team_diversity_percent": np.random.uniform(40, 80),
            "key_person_dependency": False,
            "patent_count": np.random.randint(10, 1000),
            "network_effects_present": sector in ["SaaS", "E-commerce"],
            "has_data_moat": True,
            "regulatory_advantage_present": sector in ["FinTech", "HealthTech"],
            "tech_differentiation_score": np.random.uniform(4, 5),
            "switching_cost_score": np.random.uniform(4, 5),
            "brand_strength_score": np.random.uniform(4, 5),
            "scalability_score": np.random.uniform(0.8, 1.0),
            "product_stage": "GA",
            "product_retention_30d": np.random.uniform(0.7, 0.95),
            "product_retention_90d": np.random.uniform(0.5, 0.85),
            "success": True
        }
        
        return metrics
    
    def generate_dataset(self, n_companies: int = 100000) -> pd.DataFrame:
        """Generate the full dataset."""
        print(f"Generating dataset for {n_companies} companies...")
        
        all_metrics = []
        
        for i, company in enumerate(self.real_companies[:n_companies]):
            metrics = self.generate_company_metrics(company)
            all_metrics.append(metrics)
            
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i + 1} companies...")
        
        df = pd.DataFrame(all_metrics)
        
        # Add some post-processing
        print("Post-processing dataset...")
        
        # Ensure logical consistency
        df.loc[df['annual_revenue_run_rate'] == 0, 'ltv_cac_ratio'] = 0
        df.loc[df['customer_count'] == 0, 'dau_mau_ratio'] = 0
        
        # Calculate additional metrics
        df['capital_efficiency'] = df['annual_revenue_run_rate'] / (df['total_capital_raised_usd'] + 1)
        
        print(f"Dataset generation complete!")
        print(f"Total companies: {len(df)}")
        print(f"Success rate: {df['success'].mean():.2%}")
        print(f"Sector distribution:\n{df['sector'].value_counts()}")
        
        return df

def main():
    """Generate and save the hybrid dataset."""
    generator = HybridDatasetGenerator()
    
    # Generate 100k company dataset
    df = generator.generate_dataset(100000)
    
    # Save to CSV
    output_path = "/Users/sf/Desktop/FLASH/data/hybrid_100k_companies.csv"
    df.to_csv(output_path, index=False)
    print(f"\nDataset saved to: {output_path}")
    
    # Save a sample for quick inspection
    sample_path = "/Users/sf/Desktop/FLASH/data/hybrid_sample_1000.csv"
    df.sample(1000).to_csv(sample_path, index=False)
    print(f"Sample saved to: {sample_path}")
    
    # Generate summary statistics
    summary = {
        "total_companies": len(df),
        "success_rate": float(df['success'].mean()),
        "sectors": df['sector'].value_counts().to_dict(),
        "stages": df['funding_stage'].value_counts().to_dict(),
        "avg_metrics": {
            "avg_funding": float(df['total_capital_raised_usd'].mean()),
            "avg_revenue": float(df['annual_revenue_run_rate'].mean()),
            "avg_team_size": float(df['team_size_full_time'].mean()),
            "avg_burn_multiple": float(df[df['burn_multiple'] < 100]['burn_multiple'].mean())
        }
    }
    
    with open("/Users/sf/Desktop/FLASH/data/hybrid_dataset_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\nDataset Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()